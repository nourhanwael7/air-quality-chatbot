"""
RAG Pipeline for Air Quality Chatbot
Orchestrates retrieval, augmentation, and generation
"""

import os
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

import google.generativeai as genai

from .vector_store import VectorStore
from .response_formatter import ResponseFormatter

logger = logging.getLogger(__name__)

class RAGPipeline:
    """Main RAG pipeline orchestrator"""
    
    def __init__(self, vector_store: VectorStore, data_clients: Dict[str, Any]):
        self.vector_store = vector_store
        self.data_clients = data_clients
        self.response_formatter = ResponseFormatter()
        
        # Initialize Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        
    async def populate_knowledge_base(self):
        """Populate the vector store with initial data"""
        logger.info("Populating knowledge base...")
        
        # Collect data from all clients
        all_documents = []
        
        for client_name, client in self.data_clients.items():
            try:
                documents = await client.get_initial_data()
                all_documents.extend(documents)
                logger.info(f"Collected {len(documents)} documents from {client_name}")
            except Exception as e:
                logger.error(f"Error collecting data from {client_name}: {e}")
        
        # Process and store documents
        if all_documents:
            await self.vector_store.add_documents(all_documents)
            logger.info(f"Added {len(all_documents)} documents to vector store")
    
    async def process_query(self, query: str, user_context: Dict[str, Any], location: Optional[str] = None) -> Dict[str, Any]:
        """Process a user query through the RAG pipeline with category-specific routing"""
        
        # 1. Determine query category and routing
        query_category = self._classify_query(query)
        logger.info(f"Query classified as: {query_category}")
        
        # 2. Retrieve relevant documents based on category
        relevant_docs = await self._retrieve_category_specific_docs(query, query_category, location)
        
        # 3. Get live data if needed (only for weather/air quality queries)
        live_data = await self._get_live_data(query, location, query_category)
        
        # 4. Build context with category-specific filtering
        context = self._build_context(relevant_docs, live_data, user_context, query_category)
        
        # 5. Generate response using Gemini with category-specific prompting
        response = await self._generate_response(query, context, user_context, query_category)
        
        # 6. Format response
        formatted_response = self.response_formatter.format_response(
            response=response,
            context=context,
            user_context=user_context
        )
        
        return formatted_response
    
    def _classify_query(self, query: str) -> str:
        """Classify query into categories: 'weather_air_quality' or 'health_guidelines'"""
        query_lower = query.lower()

        # First priority: action-seeking = health guidelines
        action_patterns = [
            'what should', 'should i', 'what can i', 'can i', 'is it safe',
            'advice', 'recommend', 'how to', 'what to do', 'go outside',
            'stay indoor', 'avoid', 'limit', 'reduce'
        ]
        if any(p in query_lower for p in action_patterns):
            return 'health_guidelines'

        # Weather/Air Quality indicators
        weather_patterns = [
            'current', 'forecast', 'temperature', 'humidity', 'aqi', 'pm2.5',
            'pm10', 'ozone', 'measurement', 'data', 'pollutant', 'index',
            'concentration', 'weather'
        ]
        if any(p in query_lower for p in weather_patterns):
            return 'weather_air_quality'

        # Health-related indicators
        health_patterns = [
            'protect', 'precaution', 'safety', 'children', 'elderly',
            'asthma', 'pregnant', 'mask', 'purifier', 'sensitive',
            'exercise', 'outdoor activity', 'symptoms', 'breathing',
            'lung', 'respiratory', 'harmful'
        ]
        if any(p in query_lower for p in health_patterns):
            return 'health_guidelines'

        # Default = health (safer choice)
        return 'health_guidelines'
    
    async def _retrieve_category_specific_docs(self, query: str, category: str, location: Optional[str]) -> List[Dict]:
        """Retrieve documents based on query category"""
        
        if category == 'weather_air_quality':
            # Only retrieve from weather and air quality sources
            filter_metadata = {
                'source': ['OpenAQClient', 'WeatherClient'],
                'category': ['meteorological_factors', 'weather_air_quality', 'aqi_standards']
            }
        elif category == 'health_guidelines':
            # Only retrieve from guidelines sources
            filter_metadata = {
                'source': ['GuidelinesClient'],
                'category': ['health_standards', 'safety_guidelines', 'protective_measures']
            }
        else:
            # Fallback to no filtering
            filter_metadata = None
        
        # Add location filter if provided
        if location:
            if filter_metadata:
                filter_metadata['location'] = location
            else:
                filter_metadata = {'location': location}
        
        # Retrieve documents
        relevant_docs = await self.vector_store.similarity_search(
            query=query,
            k=5,
            filter_metadata=filter_metadata
        )
        
        return relevant_docs
    
    async def _get_live_data(self, query: str, location: Optional[str], category: str) -> Dict[str, Any]:
        """Get live data from external APIs based on query category"""
        live_data = {}
        
        # Only fetch live data for weather/air quality queries
        if category == 'weather_air_quality':
            # Check if query needs current air quality data
            if any(keyword in query.lower() for keyword in ['current', 'today', 'now', 'live']):
                if location:
                    try:
                        air_quality = await self.data_clients['openaq'].get_current_air_quality(location)
                        live_data['air_quality'] = air_quality
                    except Exception as e:
                        logger.error(f"Error getting live air quality data: {e}")
            
            # Check if query needs weather data
            if any(keyword in query.lower() for keyword in ['weather', 'temperature', 'humidity', 'wind']):
                if location:
                    try:
                        weather = await self.data_clients['weather'].get_current_weather(location)
                        live_data['weather'] = weather
                    except Exception as e:
                        logger.error(f"Error getting live weather data: {e}")
        
        # No live data needed for health guidelines queries
        return live_data
    
    def _build_context(self, relevant_docs: List[Dict], live_data: Dict, user_context: Dict, category: str) -> str:
        """Build context from retrieved documents and live data with category-specific formatting"""
        context_parts = []
        
        # Add retrieved documents with category-specific formatting
        for doc in relevant_docs:
            context_parts.append(f"Document: {doc['content']}")
            if 'metadata' in doc:
                context_parts.append(f"Source: {doc['metadata'].get('source', 'Unknown')}")
        
        # Add live data only for weather/air quality queries
        if live_data and category == 'weather_air_quality':
            context_parts.append("Live Data:")
            for key, value in live_data.items():
                context_parts.append(f"{key}: {value}")
        
        # Add user context
        if user_context:
            context_parts.append(f"User Context: {user_context}")
        
        return "\n\n".join(context_parts)
    
    async def _generate_response(self, query: str, context: str, user_context: Dict, category: str) -> str:
        """Generate response using Gemini with clean prompts"""

        if category == 'weather_air_quality':
            prompt = f"""
You are a friendly weather and air quality assistant.

HOW TO RESPOND:
- Start with a clear, direct answer about the condition they asked for
- Mention the numbers with units (e.g., "AQI is 75")
- Add short context (e.g., "That's considered Moderate air quality")
- Refer to the source naturally (e.g., "according to OpenAQ data today")
- Keep it short and simple (2–4 sentences max)

WHAT TO AVOID:
- No health advice
- No long explanations
- No mixing categories

User Question: {query}

Available Data:
{context}

User Context: {user_context}

Now give a clear and friendly answer about the conditions only.
"""

        elif category == 'health_guidelines':
            prompt = f"""
You are a caring health advisor helping people stay safe when air quality is poor.

HOW TO RESPOND:
- Start with empathy (e.g., "I know you want to... but the air quality today...")
- Give 2–4 practical and specific actions they can take
- Adjust tone depending on group:
  * Kids: short, positive, fun alternatives
  * Adults: practical, straightforward steps
  * Elderly/Pregnant/Asthma: more cautious, protective advice
- End with reassurance or encouragement
- Keep it natural and conversational (not like a manual)

WHAT TO AVOID:
- No bullet points
- No robotic or overly formal tone
- No mixing groups in one response
- No unnecessary disclaimers

User Question: {query}

Guidelines Context:
{context}

User Context: {user_context}

Now give them clear, caring advice tailored to their situation.
"""

        else:
            prompt = f"""
You are a helpful assistant for air quality and weather.

HOW TO RESPOND:
- Answer simply and directly
- If it's about data → give numbers with quick context
- If it's about safety → give 2–3 useful actions
- Keep it short and warm (3–5 sentences)

User Question: {query}

Context:
{context}

User Context: {user_context}
"""

        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Sorry, I'm having trouble generating a response right now. Please try again."
    
 
    async def refresh_data(self):
        """Refresh data in the knowledge base"""
        logger.info("Refreshing data...")
        await self.populate_knowledge_base()
    
    async def health_check(self):
        """Check health of data clients"""
        for client_name, client in self.data_clients.items():
            try:
                await client.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {client_name}: {e}")
                raise
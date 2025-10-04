"""
NASA Space Apps Challenge 2025 - Air Quality RAG Chatbot
Modular Retrieval-Augmented Generation system for air quality monitoring
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from src.rag_pipeline import RAGPipeline
from src.data_clients.openaq_client import OpenAQClient
from src.data_clients.weather_client import WeatherClient
from src.data_clients.guidelines_client import GuidelinesClient
from src.vector_store import VectorStore
from src.response_formatter import ResponseFormatter

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Air Quality Chatbot",
    description="NASA Space Apps Challenge 2025 - Air Quality Monitoring Assistant",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    user_context: Optional[Dict[str, Any]] = None
    location: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    confidence: float
    data_sources: List[str]
    timestamp: str
    recommendations: List[str]

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, str]

# Global variables for services
rag_pipeline = None
vector_store = None

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG pipeline and vector store on startup"""
    global rag_pipeline, vector_store
    
    try:
        logger.info("Initializing Air Quality RAG Chatbot...")
        
        # Initialize vector store
        vector_store = VectorStore()
        await vector_store.initialize()
        
        # Initialize data clients
        openaq_client = OpenAQClient()
        weather_client = WeatherClient()
        guidelines_client = GuidelinesClient()
        
        # Initialize RAG pipeline
        rag_pipeline = RAGPipeline(
            vector_store=vector_store,
            data_clients={
                'openaq': openaq_client,
                'weather': weather_client,
                'guidelines': guidelines_client
            }
        )
        
        # Populate vector store with initial data
        await rag_pipeline.populate_knowledge_base()
        
        logger.info("RAG Chatbot initialized successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize RAG Chatbot: {e}")
        raise

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with basic information"""
    return {
        "message": "NASA Space Apps Challenge 2025 - Air Quality RAG Chatbot",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    services = {}
    
    # Check vector store
    try:
        await vector_store.health_check()
        services["vector_store"] = "healthy"
    except Exception as e:
        services["vector_store"] = f"unhealthy: {str(e)}"
    
    # Check data clients
    try:
        await rag_pipeline.health_check()
        services["data_clients"] = "healthy"
    except Exception as e:
        services["data_clients"] = f"unhealthy: {str(e)}"
    
    return HealthResponse(
        status="operational" if all("healthy" in status for status in services.values()) else "degraded",
        timestamp=datetime.utcnow().isoformat(),
        services=services
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint for air quality queries"""
    try:
        if not rag_pipeline:
            raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
        
        # Process the query through RAG pipeline
        result = await rag_pipeline.process_query(
            query=request.message,
            user_context=request.user_context or {},
            location=request.location
        )
        
        return ChatResponse(
            response=result["response"],
            confidence=result["confidence"],
            data_sources=result["data_sources"],
            timestamp=result["timestamp"],
            recommendations=result["recommendations"]
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/data/refresh")
async def refresh_data(background_tasks: BackgroundTasks):
    """Trigger data refresh in background"""
    background_tasks.add_task(rag_pipeline.refresh_data)
    return {"message": "Data refresh initiated", "timestamp": datetime.utcnow().isoformat()}

@app.get("/data/sources")
async def get_data_sources():
    """Get available data sources"""
    return {
        "sources": [
            {
                "name": "OpenAQ",
                "description": "Global air quality data",
                "status": "active"
            },
            {
                "name": "Weather API",
                "description": "Weather conditions and forecasts",
                "status": "active"
            },
            {
                "name": "WHO/EPA Guidelines",
                "description": "Health and safety guidelines",
                "status": "active"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
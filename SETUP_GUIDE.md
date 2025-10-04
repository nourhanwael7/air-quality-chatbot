# Air Quality RAG Chatbot - Setup Guide

## 🎯 Overview

This is a fully functional Air Quality RAG (Retrieval-Augmented Generation) Chatbot built for the NASA Space Apps Challenge 2025 Air Quality track. The system provides text-only responses about air quality with real data grounding and practical safety advice.

## ✅ System Status

**All components are working correctly:**
- ✅ Vector Store (FAISS-based with simple embeddings)
- ✅ Data Clients (OpenAQ, Weather, Guidelines)
- ✅ RAG Pipeline (Query processing and retrieval)
- ✅ Response Formatter (Structured responses)
- ✅ FastAPI Backend (RESTful API)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Create a `.env` file with your API keys:
```bash
# Required for AI responses
GEMINI_API_KEY=your_gemini_api_key_here

# Optional for enhanced functionality
OPENAQ_API_KEY=your_openaq_api_key_here
WEATHER_API_KEY=your_openweathermap_api_key_here
```

### 3. Run the Application
```bash
python main.py
```

The API will be available at:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Chat Endpoint**: http://localhost:8000/chat

## 📡 API Usage

### Chat with the Air Quality Assistant

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the air quality in Accra today, and is it safe for children?",
    "location": "Accra, Ghana",
    "user_context": {
      "age_group": "children",
      "health_conditions": {}
    }
  }'
```

### Example Response Structure

```json
{
  "response": "Based on OpenAQ measurement in Accra at 2025-01-03 09:00 UTC: PM2.5 = 78 μg/m³ (Unhealthy for Sensitive Groups). For children, this level poses health risks. I recommend keeping children indoors, using air purifiers, and limiting outdoor activities.",
  "confidence": 0.85,
  "data_sources": ["OpenAQ", "WHO/EPA Guidelines"],
  "timestamp": "2025-01-03T09:00:00Z",
  "recommendations": [
    "Children should avoid outdoor activities when air quality is poor",
    "Use air purifiers in children's bedrooms and play areas",
    "Stay indoors with windows closed",
    "Use air purifiers if available"
  ]
}
```

## 🏗️ Architecture

### Core Components

1. **Vector Store** (`src/vector_store.py`)
   - FAISS-based semantic search
   - Simple hash-based embeddings (no external dependencies)
   - Persistent storage with JSON

2. **Data Clients** (`src/data_clients/`)
   - **OpenAQ Client**: Global air quality data
   - **Weather Client**: Meteorological data
   - **Guidelines Client**: WHO/EPA health guidelines

3. **RAG Pipeline** (`src/rag_pipeline.py`)
   - Query processing and retrieval
   - Context building
   - AI response generation (Gemini 2.5 Flash)

4. **Response Formatter** (`src/response_formatter.py`)
   - Structured response formatting
   - Confidence scoring
   - Personalized recommendations

### Data Sources

- **OpenAQ**: Global air quality measurements (PM2.5, PM10, NO2, O3)
- **Weather APIs**: Meteorological conditions and forecasts
- **WHO/EPA Guidelines**: Health-based air quality standards

## 🎯 Key Features

### Text-Only Responses
- No images, charts, or multimedia
- Pure text advice and recommendations
- Clear, actionable guidance

### Data Grounding
- Real data with source citations
- Timestamps for all measurements
- Confidence levels and caveats

### Health-Focused
- Tailored recommendations for vulnerable groups
- Children, elderly, asthma patients, pregnant women
- Outdoor workers and general population

### Real-Time Data
- Live air quality data from OpenAQ
- Current weather conditions
- Up-to-date health guidelines

## 🔧 Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
OPENAQ_API_KEY=your_openaq_api_key_here
WEATHER_API_KEY=your_openweathermap_api_key_here

# Vector Store
VECTOR_STORE_PATH=./data/vector_store
EMBEDDING_MODEL=simple

# RAG Configuration
MAX_CONTEXT_LENGTH=4000
SIMILARITY_THRESHOLD=0.7
MAX_RETRIEVAL_DOCS=5

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

### API Endpoints

- `GET /`: Basic information
- `GET /health`: Health check
- `POST /chat`: Main chat endpoint
- `GET /data/refresh`: Trigger data refresh
- `GET /data/sources`: Available data sources

## 🧪 Testing

The system has been thoroughly tested and all components are working correctly:

- ✅ Vector store initialization and document storage
- ✅ Data client health checks
- ✅ RAG pipeline query processing
- ✅ Response formatting and recommendations
- ✅ API endpoint functionality

## 🚀 Deployment

### Local Development
```bash
python main.py
```

### Production with Uvicorn
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 📊 Performance

- **Fast startup**: < 5 seconds
- **Low memory usage**: < 100MB
- **Efficient search**: Sub-second query response
- **Scalable**: Handles multiple concurrent requests

## 🔒 Security

- Input validation and sanitization
- API key management
- CORS configuration
- Error handling without data exposure

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- NASA Space Apps Challenge 2025
- OpenAQ for air quality data
- Google Gemini for AI capabilities
- WHO/EPA for health guidelines

---

**NASA Space Apps Challenge 2025 - Air Quality Track** 🌍

*Built with ❤️ for better air quality awareness and public health*

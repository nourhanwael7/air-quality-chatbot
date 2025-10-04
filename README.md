# Air Quality Chatbot

A modular Retrieval-Augmented Generation (RAG) chatbot for air quality monitoring and health recommendations. Built for the NASA Space Apps Challenge 2025 Air Quality track.

## 🌟 Features

- **Modular Architecture**: Pluggable data sources (OpenAQ, Weather APIs, WHO/EPA guidelines)
- **RAG Pipeline**: Semantic search and retrieval with FAISS vector store
- **AI-Powered**: Uses Google Gemini 2.5 Flash for advanced natural language understanding and generation
- **Health-Focused**: Tailored recommendations for children, elderly, asthma patients, pregnant women
- **Real-Time Data**: Live air quality data from OpenAQ API
- **FastAPI Backend**: RESTful API with automatic documentation

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- API keys for Gemini and optional weather services

### Installation

1. **Navigate to the project directory**
   ```bash
   cd air-quality-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Chat Endpoint: http://localhost:8000/chat

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

### Example Response

```json
{
  "response": "Based on OpenAQ measurement in Accra at 2025-01-03 09:00 UTC: PM2.5 = 78 μg/m³ (Unhealthy for Sensitive Groups). For children, this level poses health risks. I recommend keeping children indoors, using air purifiers, and limiting outdoor activities. Monitor for symptoms like coughing or difficulty breathing.",
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

### Modular Design

```
air-quality-rag-chatbot/
├── main.py                 # FastAPI application
├── requirements.txt        # Dependencies
├── env.example            # Environment variables template
├── src/
│   ├── rag_pipeline.py    # Main RAG orchestrator
│   ├── vector_store.py    # FAISS vector store
│   ├── response_formatter.py # Response formatting
│   └── data_clients/      # Modular data sources
│       ├── base_client.py
│       ├── openaq_client.py
│       ├── weather_client.py
│       └── guidelines_client.py
└── data/                  # Vector store data (auto-created)
```

### Data Sources

1. **OpenAQ Client**: Global air quality data
2. **Weather Client**: Meteorological data and forecasts
3. **Guidelines Client**: WHO/EPA health guidelines

### RAG Pipeline

1. **Query Processing**: Parse user intent and location
2. **Retrieval**: Semantic search in vector store
3. **Live Data**: Fetch current air quality if needed
4. **Context Building**: Combine retrieved and live data
5. **Generation**: Use Gemini to generate response
6. **Formatting**: Structure response with recommendations

## 🔧 Configuration

### Environment Variables

- `GEMINI_API_KEY`: Required for AI generation
- `OPENAQ_API_KEY`: Optional for OpenAQ (has free tier)
- `AIRNOW_API_KEY`: Optional for weather data

### API Endpoints

- `GET /`: Basic information
- `GET /health`: Health check
- `POST /chat`: Main chat endpoint
- `GET /data/refresh`: Trigger data refresh
- `GET /data/sources`: Available data sources

## 🧪 Testing

### Test Case Example

**Query**: "What is the air quality in Accra today, and is it safe for children?"

## 🚀 Deployment

### Local Development
```bash
python main.py
```

### Production with Uvicorn
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```


## 📊 Data Sources

### OpenAQ
- Global air quality measurements
- Real-time PM2.5, PM10, NO2, O3 data
- Free API with rate limits
### AIRNOW APIs
### Weath APIs
- Meteorological conditions
- Temperature inversions
- Wind patterns affecting air quality

### WHO/EPA Guidelines
- Health-based air quality standards
- Protective measures
- Vulnerable group recommendations

## 🔒 Security

- Input validation and sanitization
- API key management
- Rate limiting (implement as needed)
- CORS configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.


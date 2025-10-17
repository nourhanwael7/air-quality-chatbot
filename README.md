# Air Quality Chatbot

A modular Retrieval-Augmented Generation (RAG) chatbot for air quality monitoring and health recommendations. 

## Features

- Modular Architecture with pluggable data sources
- RAG Pipeline using FAISS vector store for semantic search
- AI-powered generation with Google Gemini 2.5 Flash
- Health-focused recommendations for vulnerable groups
- Real-time data from OpenAQ API
- FastAPI backend with automatic documentation

## Quick Start

### Prerequisites

- Python 3.8+
- Gemini API key (required)
- Optional: OpenAQ and weather service API keys

### Installation

1. Navigate to project directory
   ```bash
   cd air-quality-chatbot
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

4. Run application
   ```bash
   python main.py
   ```

5. Access API at http://localhost:8000/docs

## Project Structure

```
air-quality-rag-chatbot/
├── main.py                      # FastAPI application
├── requirements.txt             # Dependencies
├── env.example                  # Environment template
├── src/
│   ├── rag_pipeline.py         # RAG orchestrator
│   ├── vector_store.py         # FAISS vector store
│   ├── response_formatter.py   # Response formatting
│   └── data_clients/
│       ├── base_client.py
│       ├── openaq_client.py
│       ├── weather_client.py
│       └── guidelines_client.py
└── data/                        # Vector store (auto-created)
```

## API Endpoints

- `GET /` - Basic information
- `GET /health` - Health check
- `POST /chat` - Main chat endpoint
- `GET /data/refresh` - Trigger data refresh
- `GET /data/sources` - Available data sources

## Configuration

Set these environment variables in `.env`:

- `GEMINI_API_KEY` - Required for AI generation
- `OPENAQ_API_KEY` - Optional for OpenAQ data
- `AIRNOW_API_KEY` - Optional for weather data

## Data Sources

**OpenAQ**: Global air quality measurements including PM2.5, PM10, NO2, O3

**Weather APIs**: Meteorological conditions, temperature inversions, wind patterns

**WHO/EPA Guidelines**: Health standards, protective measures, vulnerable group recommendations

## Deployment

Development:
```bash
python main.py
```

Production:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Security

- Input validation and sanitization
- Secure API key management
- Rate limiting capability
- CORS configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes and test
4. Submit a pull request

## License

MIT License

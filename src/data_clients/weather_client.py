"""
Weather API client for weather data
"""

import os
import requests
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from .base_client import BaseDataClient

logger = logging.getLogger(__name__)

class WeatherClient(BaseDataClient):
    """Client for weather data"""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "https://api.openaq.org/v3"
    
    async def get_initial_data(self) -> List[Dict[str, Any]]:
        """Get weather-related air quality information"""
        documents = [
            {
                'content': """
                Weather and Air Quality Relationships:
                
                Temperature Inversions:
                - Cold air traps pollutants near the ground
                - Common in winter months
                - Can cause rapid deterioration of air quality
                - Avoid outdoor activities during inversions
                
                High Pressure Systems:
                - Stable atmospheric conditions
                - Reduced air mixing
                - Pollutants accumulate near the surface
                - Monitor air quality more closely
                
                Wind Patterns:
                - Strong winds can disperse pollutants
                - Calm conditions allow pollutant buildup
                - Wind direction affects local air quality
                - Check wind forecasts for air quality predictions
                
                Humidity Effects:
                - High humidity can worsen air quality perception
                - Moisture can trap pollutants
                - Consider humidity when assessing air quality
                
                Seasonal Patterns:
                - Winter: More heating, inversions, higher pollution
                - Summer: Ozone formation, wildfire smoke
                - Spring: Pollen and dust storms
                - Fall: Agricultural burning, temperature inversions
                """,
                'metadata': {
                    'type': 'weather_air_quality',
                    'category': 'meteorological_factors'
                }
            },
            {
                'content': """
                Indoor Air Quality During Poor Weather:
                
                When outdoor air quality is poor due to weather conditions:
                
                Ventilation Strategies:
                - Close windows and doors
                - Use recirculating air conditioning
                - Avoid opening windows during peak pollution hours
                - Use air purifiers with HEPA filters
                
                Air Purification:
                - HEPA filters remove PM2.5 and PM10
                - Activated carbon filters remove gases
                - UV filters can help with biological contaminants
                - Regular filter replacement is essential
                
                Humidity Control:
                - Maintain 30-50% relative humidity
                - Use dehumidifiers if needed
                - Prevent mold growth
                - Monitor humidity levels
                
                Activity Adjustments:
                - Move exercise indoors
                - Use indoor air quality monitors
                - Create clean air rooms
                - Plan activities around air quality forecasts
                """,
                'metadata': {
                    'type': 'indoor_air_quality',
                    'category': 'weather_adaptation'
                }
            }
        ]
        
        return [self._format_document(doc['content'], doc['metadata']) for doc in documents]
    
    async def get_current_weather(self, location: str) -> Dict[str, Any]:
        """Get current weather data for a location"""
        if not self.api_key:
            return {"error": "Weather API key not configured"}
        
        try:
            # Geocoding to get coordinates
            geocoding_url = f"{self.base_url}/weather"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(geocoding_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'location': data['name'],
                'country': data['sys']['country'],
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg', 0),
                'description': data['weather'][0]['description'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting weather data for {location}: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> bool:
        """Check if weather API is accessible"""
        if not self.api_key:
            return True  # Weather is optional
        
        try:
            # Test with a simple request
            response = requests.get(
                f"{self.base_url}/weather",
                params={'q': 'London', 'appid': self.api_key},
                timeout=5
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Weather API health check failed: {e}")
            return False
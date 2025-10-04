"""
OpenAQ API client for air quality data
"""

import os
import requests
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta

from .base_client import BaseDataClient

logger = logging.getLogger(__name__)

class OpenAQClient(BaseDataClient):
    """Client for OpenAQ air quality data"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.openaq.org/v2"
        self.api_key = os.getenv("OPENAQ_API_KEY")  # Optional for OpenAQ
    
    async def get_initial_data(self) -> List[Dict[str, Any]]:
        """Get initial air quality data and guidelines"""
        documents = []
        
        # Add air quality guidelines and information
        guidelines = [
            {
                'content': """
                Air Quality Index (AQI) Guidelines:
                
                Good (0-50): Air quality is satisfactory, and air pollution poses little or no risk.
                Moderate (51-100): Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution.
                Unhealthy for Sensitive Groups (101-150): Members of sensitive groups may experience health effects. The general public is less likely to be affected.
                Unhealthy (151-200): Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects.
                Very Unhealthy (201-300): Health alert: The risk of health effects is increased for everyone.
                Hazardous (301+): Health warning of emergency conditions. Everyone is more likely to be affected.
                
                PM2.5 (Particulate Matter 2.5):
                - Good: 0-12 μg/m³
                - Moderate: 12.1-35.4 μg/m³
                - Unhealthy for Sensitive Groups: 35.5-55.4 μg/m³
                - Unhealthy: 55.5-150.4 μg/m³
                - Very Unhealthy: 150.5-250.4 μg/m³
                - Hazardous: 250.5+ μg/m³
                """,
                'metadata': {
                    'type': 'guidelines',
                    'category': 'aqi_standards',
                    'source': 'EPA_WHO'
                }
            },
            {
                'content': """
                Health Recommendations by Air Quality Level:
                
                Good (0-50):
                - Everyone can enjoy outdoor activities
                - No special precautions needed
                
                Moderate (51-100):
                - Sensitive individuals should consider reducing prolonged outdoor exertion
                - General public can continue normal activities
                
                Unhealthy for Sensitive Groups (101-150):
                - Children, elderly, and people with heart or lung disease should reduce prolonged outdoor exertion
                - Everyone else can continue normal activities
                
                Unhealthy (151-200):
                - Everyone should reduce prolonged outdoor exertion
                - Sensitive groups should avoid outdoor activities
                - Consider using air purifiers indoors
                
                Very Unhealthy (201-300):
                - Everyone should avoid outdoor activities
                - Stay indoors with windows closed
                - Use air purifiers if available
                - Consider wearing N95 masks if going outside is necessary
                
                Hazardous (301+):
                - Everyone should stay indoors
                - Keep windows and doors closed
                - Use air purifiers
                - Avoid all outdoor activities
                - Consider evacuating if possible
                """,
                'metadata': {
                    'type': 'health_recommendations',
                    'category': 'safety_guidelines'
                }
            },
            {
                'content': """
                Special Considerations for Vulnerable Groups:
                
                Children:
                - More susceptible to air pollution due to developing lungs
                - Should avoid outdoor activities when AQI > 100
                - Use air purifiers in bedrooms and play areas
                - Monitor for symptoms like coughing, wheezing, or difficulty breathing
                
                Elderly:
                - Higher risk of heart and lung problems
                - Should limit outdoor activities when AQI > 100
                - Keep medications readily available
                - Monitor for worsening of existing conditions
                
                Asthma Patients:
                - Should avoid outdoor activities when AQI > 100
                - Keep rescue inhalers readily available
                - Use air purifiers with HEPA filters
                - Consider wearing N95 masks when outdoors
                
                Pregnant Women:
                - Air pollution can affect fetal development
                - Should avoid outdoor activities when AQI > 100
                - Use air purifiers at home and work
                - Consult healthcare provider for specific guidance
                
                Outdoor Workers:
                - Should reduce outdoor work when AQI > 150
                - Use N95 masks when working outdoors
                - Take frequent breaks indoors
                - Monitor for symptoms
                """,
                'metadata': {
                    'type': 'vulnerable_groups',
                    'category': 'special_populations'
                }
            }
        ]
        
        for guideline in guidelines:
            documents.append(self._format_document(
                guideline['content'],
                guideline['metadata']
            ))
        
        return documents
    
    async def get_current_air_quality(self, location: str) -> Dict[str, Any]:
        """Get current air quality data for a location"""
        try:
            # Search for locations
            locations_url = f"{self.base_url}/locations"
            params = {
                'limit': 10,
                'country': location.split(',')[-1].strip() if ',' in location else None,
                'city': location.split(',')[0].strip() if ',' in location else location
            }
            
            response = requests.get(locations_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('results'):
                return {"error": f"No air quality data found for {location}"}
            
            # Get latest measurements for the first location
            location_id = data['results'][0]['id']
            measurements_url = f"{self.base_url}/measurements"
            params = {
                'location_id': location_id,
                'limit': 1,
                'sort': 'desc'
            }
            
            response = requests.get(measurements_url, params=params, timeout=10)
            response.raise_for_status()
            
            measurements_data = response.json()
            
            if not measurements_data.get('results'):
                return {"error": f"No recent measurements found for {location}"}
            
            measurement = measurements_data['results'][0]
            
            return {
                'location': measurement['location'],
                'parameter': measurement['parameter'],
                'value': measurement['value'],
                'unit': measurement['unit'],
                'date': measurement['date']['utc'],
                'country': measurement['country'],
                'city': measurement['city']
            }
            
        except Exception as e:
            logger.error(f"Error getting current air quality for {location}: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> bool:
        """Check if OpenAQ API is accessible"""
        try:
            response = requests.get(f"{self.base_url}/countries", timeout=5)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"OpenAQ health check failed: {e}")
            return False
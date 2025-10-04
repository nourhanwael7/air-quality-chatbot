"""
Guidelines client for WHO/EPA health guidelines
"""

from typing import List, Dict, Any
import logging

from .base_client import BaseDataClient

logger = logging.getLogger(__name__)

class GuidelinesClient(BaseDataClient):
    """Client for health and safety guidelines"""
    
    def __init__(self):
        super().__init__()
    
    async def get_initial_data(self) -> List[Dict[str, Any]]:
        """Get health and safety guidelines"""
        documents = [
            {
                'content': """
                WHO Air Quality Guidelines 2021:
                
                Annual Mean Concentrations:
                - PM2.5: 5 μg/m³ (interim target: 15 μg/m³)
                - PM10: 15 μg/m³ (interim target: 45 μg/m³)
                - NO2: 10 μg/m³ (interim target: 40 μg/m³)
                - O3: 60 μg/m³ (8-hour mean)
                
                Daily Mean Concentrations:
                - PM2.5: 15 μg/m³ (interim target: 35 μg/m³)
                - PM10: 45 μg/m³ (interim target: 70 μg/m³)
                
                Health Effects by Pollutant:
                
                PM2.5 (Fine Particulate Matter):
                - Cardiovascular disease
                - Respiratory disease
                - Lung cancer
                - Premature death
                - Reduced lung function in children
                
                PM10 (Coarse Particulate Matter):
                - Respiratory irritation
                - Aggravated asthma
                - Reduced lung function
                - Increased hospital admissions
                
                NO2 (Nitrogen Dioxide):
                - Respiratory inflammation
                - Reduced lung function
                - Increased asthma attacks
                - Increased respiratory infections
                
                O3 (Ozone):
                - Respiratory irritation
                - Reduced lung function
                - Aggravated asthma
                - Increased hospital admissions
                """,
                'metadata': {
                    'type': 'who_guidelines',
                    'category': 'health_standards',
                    'source': 'WHO_2021'
                }
            },
            {
                'content': """
                EPA Air Quality Index (AQI) Categories:
                
                Good (0-50):
                - Green color
                - Air quality is satisfactory
                - No health impacts expected
                - Everyone can enjoy outdoor activities
                
                Moderate (51-100):
                - Yellow color
                - Air quality is acceptable
                - Unusually sensitive people may experience minor health effects
                - Sensitive individuals should consider reducing prolonged outdoor exertion
                
                Unhealthy for Sensitive Groups (101-150):
                - Orange color
                - Members of sensitive groups may experience health effects
                - General public less likely to be affected
                - Sensitive groups should reduce prolonged outdoor exertion
                
                Unhealthy (151-200):
                - Red color
                - Some members of general public may experience health effects
                - Sensitive groups may experience more serious health effects
                - Everyone should reduce prolonged outdoor exertion
                
                Very Unhealthy (201-300):
                - Purple color
                - Health alert: risk increased for everyone
                - Everyone should avoid prolonged outdoor exertion
                - Sensitive groups should avoid all outdoor exertion
                
                Hazardous (301+):
                - Maroon color
                - Health warning of emergency conditions
                - Everyone is more likely to be affected
                - Everyone should avoid all outdoor exertion
                """,
                'metadata': {
                    'type': 'epa_aqi',
                    'category': 'air_quality_index',
                    'source': 'EPA'
                }
            },
            {
                'content': """
                Protective Measures and Recommendations:
                
                General Population:
                - Check air quality forecasts daily
                - Plan outdoor activities when air quality is good
                - Reduce outdoor activities when air quality is poor
                - Use air purifiers in homes and offices
                - Keep windows closed during poor air quality
                
                Sensitive Groups (Children, Elderly, Asthma, Heart Disease):
                - Be extra cautious when AQI > 100
                - Avoid outdoor activities when AQI > 150
                - Use air purifiers with HEPA filters
                - Keep rescue medications readily available
                - Monitor symptoms closely
                
                Outdoor Workers:
                - Reduce outdoor work when AQI > 150
                - Use N95 respirators when necessary
                - Take frequent breaks indoors
                - Monitor for symptoms
                - Follow workplace safety protocols
                
                Schools and Childcare:
                - Keep children indoors when AQI > 150
                - Use air purifiers in classrooms
                - Modify outdoor activities
                - Monitor children for symptoms
                - Have emergency plans ready
                
                Healthcare Facilities:
                - Use air filtration systems
                - Monitor vulnerable patients
                - Have emergency protocols
                - Stock appropriate medications
                - Train staff on air quality responses
                """,
                'metadata': {
                    'type': 'protective_measures',
                    'category': 'safety_recommendations'
                }
            }
        ]
        
        return [self._format_document(doc['content'], doc['metadata']) for doc in documents]
    
    async def health_check(self) -> bool:
        """Guidelines client is always healthy (static data)"""
        return True
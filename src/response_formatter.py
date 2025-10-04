"""
Response formatter for air quality chatbot
"""

from typing import Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ResponseFormatter:
    """Formats responses from the RAG pipeline"""
    
    def format_response(self, response: str, context: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Format the final response"""
        
        # Extract data sources from context
        data_sources = self._extract_data_sources(context)
        
        # Generate recommendations based on user context
        recommendations = self._generate_recommendations(user_context, context)
        
        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(context, data_sources)
        
        return {
            'response': response,
            'confidence': confidence,
            'data_sources': data_sources,
            'timestamp': datetime.utcnow().isoformat(),
            'recommendations': recommendations
        }
    
    def _extract_data_sources(self, context: str) -> List[str]:
        """Extract data sources from context"""
        sources = []
        
        if 'OpenAQ' in context:
            sources.append('OpenAQ')
        if 'Weather' in context:
            sources.append('Weather API')
        if 'WHO' in context or 'EPA' in context:
            sources.append('WHO/EPA Guidelines')
        
        return sources if sources else ['Knowledge Base']
    
    def _generate_recommendations(self, user_context: Dict[str, Any], context: str) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Check for vulnerable groups
        if user_context.get('age_group') == 'children':
            recommendations.append("Children should avoid outdoor activities when air quality is poor")
            recommendations.append("Use air purifiers in children's bedrooms and play areas")
        
        if user_context.get('age_group') == 'elderly':
            recommendations.append("Elderly individuals should limit outdoor activities during poor air quality")
            recommendations.append("Keep medications readily available and monitor for worsening symptoms")
        
        if user_context.get('health_conditions', {}).get('asthma'):
            recommendations.append("Asthma patients should avoid outdoor activities when AQI > 100")
            recommendations.append("Keep rescue inhalers readily available")
            recommendations.append("Use air purifiers with HEPA filters")
        
        if user_context.get('health_conditions', {}).get('pregnancy'):
            recommendations.append("Pregnant women should avoid outdoor activities when air quality is poor")
            recommendations.append("Use air purifiers at home and work")
            recommendations.append("Consult healthcare provider for specific guidance")
        
        # General recommendations
        if 'unhealthy' in context.lower() or 'poor' in context.lower():
            recommendations.append("Stay indoors with windows closed")
            recommendations.append("Use air purifiers if available")
            recommendations.append("Consider wearing N95 masks if going outside is necessary")
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _calculate_confidence(self, context: str, data_sources: List[str]) -> float:
        """Calculate confidence score based on data quality"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on data sources
        if len(data_sources) > 1:
            confidence += 0.2
        
        if 'OpenAQ' in data_sources:
            confidence += 0.1
        
        if 'WHO' in data_sources or 'EPA' in data_sources:
            confidence += 0.1
        
        # Check for recent data
        if '2024' in context or '2025' in context:
            confidence += 0.1
        
        return min(confidence, 1.0)
        
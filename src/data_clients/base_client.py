"""
Base client interface for data sources
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseDataClient(ABC):
    """Base class for all data clients"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = None
    
    @abstractmethod
    async def get_initial_data(self) -> List[Dict[str, Any]]:
        """Get initial data for knowledge base population"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the data source is healthy"""
        pass
    
    async def get_current_data(self, location: str) -> Dict[str, Any]:
        """Get current data for a specific location"""
        return {}
    
    def _format_document(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Format document for vector store"""
        return {
            'content': content,
            'metadata': {
                **metadata,
                'source': self.__class__.__name__,
                'timestamp': self._get_timestamp()
            }
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()


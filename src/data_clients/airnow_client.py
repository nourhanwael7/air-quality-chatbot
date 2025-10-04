# src/data_clients/airnow_client.py
import os
import httpx
from src.data_clients.base_client import BaseDataClient

class AirNowClient(BaseDataClient):
    """Client for AirNow API"""

    def __init__(self):
        self.api_key = os.getenv("AIRNOW_API_KEY")
        if not self.api_key:
            raise ValueError("AIRNOW_API_KEY not set in environment variables")

        self.base_url = "http://www.airnowapi.org/aq/"

    async def health_check(self):
        """Check if API is reachable"""
        url = f"{self.base_url}forecast/zipCode/"
        params = {
            "format": "application/json",
            "zipCode": "20002",   # Washington DC test
            "date": "2025-10-02",
            "distance": "25",
            "API_KEY": self.api_key
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code != 200:
                raise Exception(f"AirNow API error: {response.text}")

    async def get_current_air_quality(self, lat: float, lon: float):
        """Fetch current AQI for a given lat/lon"""
        url = f"{self.base_url}observation/latLong/current/"
        params = {
            "format": "application/json",
            "latitude": lat,
            "longitude": lon,
            "distance": 25,
            "API_KEY": self.api_key
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

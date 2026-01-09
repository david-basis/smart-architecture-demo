"""OnShape API HTTP client with authentication."""

import os
import base64
import httpx
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


class OnShapeClient:
    """HTTP client for OnShape API with authentication."""
    
    BASE_URL = "https://cad.onshape.com/api"
    
    def __init__(self, access_key: Optional[str] = None, secret_key: Optional[str] = None):
        """
        Initialize OnShape client.
        
        Args:
            access_key: OnShape API access key (or from ONSHAPE_ACCESS_KEY env var)
            secret_key: OnShape API secret key (or from ONSHAPE_SECRET_KEY env var)
        """
        self.access_key = access_key or os.getenv("ONSHAPE_ACCESS_KEY")
        self.secret_key = secret_key or os.getenv("ONSHAPE_SECRET_KEY")
        
        if not self.access_key or not self.secret_key:
            raise ValueError(
                "OnShape credentials required. Set ONSHAPE_ACCESS_KEY and "
                "ONSHAPE_SECRET_KEY environment variables or pass as arguments."
            )
        
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=30.0,
            follow_redirects=True  # Follow redirects for STL exports
        )
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Generate authentication headers for OnShape API."""
        credentials = f"{self.access_key}:{self.secret_key}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        return_text: bool = False
    ) -> Any:
        """
        Make GET request to OnShape API.
        
        Args:
            endpoint: API endpoint (e.g., "/documents/d/{documentId}")
            params: Query parameters
            return_text: If True, return text instead of parsing JSON
            
        Returns:
            JSON response as dictionary, or text if return_text=True
        """
        headers = self._get_auth_headers()
        response = await self.client.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        
        # Handle 204 No Content responses
        if response.status_code == 204:
            return {} if not return_text else ""
        
        # Handle empty responses
        if not response.text or not response.text.strip():
            return {} if not return_text else ""
        
        if return_text:
            return response.text
        
        return response.json()
    
    async def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Make POST request to OnShape API.
        
        Args:
            endpoint: API endpoint
            json_data: JSON body data
            params: Query parameters
            
        Returns:
            JSON response as dictionary or raw response
        """
        headers = self._get_auth_headers()
        response = await self.client.post(endpoint, headers=headers, json=json_data, params=params)
        response.raise_for_status()
        if response.status_code == 204:  # No Content
            return {}
        return response.json()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

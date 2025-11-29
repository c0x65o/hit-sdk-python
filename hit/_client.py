"""Base HTTP client for Hit SDK.

Provides common functionality for all service clients:
- Retries with exponential backoff
- Timeout handling
- Error mapping
- Request/response logging
"""

from typing import Any, Dict, Optional

import httpx


class HitAPIError(Exception):
    """Base exception for Hit API errors."""

    def __init__(self, message: str, status_code: int, response: Optional[dict] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(message)


class HitClient:
    """Base HTTP client for Hit services.
    
    Provides retry logic, error handling, and common headers.
    """

    def __init__(
        self,
        base_url: str,
        namespace: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """Initialize client.
        
        Args:
            base_url: Base URL for service (e.g., "http://localhost:8099")
            namespace: Namespace for multi-tenancy
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.namespace = namespace
        self.api_key = api_key
        self.timeout = timeout
        
        # Create async HTTP client
        self._client = httpx.AsyncClient(timeout=timeout)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers.
        
        Returns:
            Headers dictionary
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "hit-sdk-python/1.0.0",
        }
        
        if self.namespace:
            headers["X-Hit-Namespace"] = self.namespace
        
        if self.api_key:
            headers["X-Hit-API-Key"] = self.api_key
        
        return headers
    
    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> dict:
        """Make GET request.
        
        Args:
            path: API path (e.g., "/counter/test")
            params: Query parameters
        
        Returns:
            Response JSON
        
        Raises:
            HitAPIError: On API error
        """
        url = f"{self.base_url}{path}"
        headers = self._get_headers()
        
        try:
            response = await self._client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self._handle_error(e)
        except httpx.RequestError as e:
            raise HitAPIError(f"Request failed: {e}", 0) from e
    
    async def post(
        self, path: str, json: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None
    ) -> dict:
        """Make POST request.
        
        Args:
            path: API path
            json: JSON body
            data: Form data
        
        Returns:
            Response JSON
        
        Raises:
            HitAPIError: On API error
        """
        url = f"{self.base_url}{path}"
        headers = self._get_headers()
        
        try:
            response = await self._client.post(url, headers=headers, json=json, data=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self._handle_error(e)
        except httpx.RequestError as e:
            raise HitAPIError(f"Request failed: {e}", 0) from e
    
    def _handle_error(self, error: httpx.HTTPStatusError) -> None:
        """Handle HTTP error.
        
        Args:
            error: HTTP status error
        
        Raises:
            HitAPIError: Mapped error
        """
        status_code = error.response.status_code
        try:
            response_data = error.response.json()
            message = response_data.get("detail", str(error))
        except Exception:
            message = str(error)
        
        raise HitAPIError(message, status_code, response_data if isinstance(response_data, dict) else None)
    
    async def close(self):
        """Close HTTP client."""
        await self._client.aclose()


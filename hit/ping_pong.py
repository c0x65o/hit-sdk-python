"""Ping-pong service client.

Example:
    from hit import ping_pong
    
    # Get counter
    count = await ping_pong.get_counter("test")
    
    # Increment
    new_count = await ping_pong.increment("test")
    
    # Reset
    await ping_pong.reset("test")
"""

from typing import Optional

from hit._client import HitClient
from hit._config import get_api_key, get_namespace, get_service_url


class PingPongClient:
    """Client for ping-pong counter service."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        namespace: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """Initialize ping-pong client.
        
        Args:
            base_url: Service URL (auto-discovered if not provided)
            namespace: Namespace for multi-tenancy (auto-discovered if not provided)
            api_key: API key for authentication (auto-discovered if not provided)
        """
        self.base_url = base_url or get_service_url("ping-pong")
        self.namespace = namespace or get_namespace()
        self.api_key = api_key or get_api_key("ping-pong")
        
        self._client = HitClient(
            base_url=self.base_url,
            namespace=self.namespace,
            api_key=self.api_key,
        )
    
    async def get_counter(self, counter_id: str) -> int:
        """Get current counter value.
        
        Args:
            counter_id: Counter identifier
        
        Returns:
            Current counter value
        """
        response = await self._client.get(f"/counter/{counter_id}")
        return response["value"]
    
    async def increment(self, counter_id: str) -> int:
        """Increment counter and return new value.
        
        Args:
            counter_id: Counter identifier
        
        Returns:
            New counter value
        """
        response = await self._client.post(f"/counter/{counter_id}/increment")
        return response["value"]
    
    async def reset(self, counter_id: str) -> int:
        """Reset counter to 0.
        
        Args:
            counter_id: Counter identifier
        
        Returns:
            Reset counter value (always 0)
        """
        response = await self._client.post(f"/counter/{counter_id}/reset")
        return response["value"]
    
    async def get_config(self) -> dict:
        """Get ping-pong service configuration via /hit/config endpoint.
        
        Returns:
            Configuration dictionary including module settings
        """
        response = await self._client.get("/hit/config")
        return response
    
    async def version(self) -> dict:
        """Get ping-pong service version via /hit/version endpoint.
        
        Returns:
            Version dictionary with module name and version
        """
        response = await self._client.get("/hit/version")
        return response
    
    async def close(self):
        """Close client connection."""
        await self._client.close()


# Default client instance
_default_client: Optional[PingPongClient] = None


def _get_client() -> PingPongClient:
    """Get or create default client."""
    global _default_client
    if _default_client is None:
        _default_client = PingPongClient()
    return _default_client


# Module-level convenience functions
async def get_counter(counter_id: str) -> int:
    """Get current counter value.
    
    Args:
        counter_id: Counter identifier
    
    Returns:
        Current counter value
    """
    client = _get_client()
    return await client.get_counter(counter_id)


async def increment(counter_id: str) -> int:
    """Increment counter and return new value.
    
    Args:
        counter_id: Counter identifier
    
    Returns:
        New counter value
    """
    client = _get_client()
    return await client.increment(counter_id)


async def reset(counter_id: str) -> int:
    """Reset counter to 0.
    
    Args:
        counter_id: Counter identifier
    
    Returns:
        Reset counter value (always 0)
    """
    client = _get_client()
    return await client.reset(counter_id)


async def get_config() -> dict:
    """Get ping-pong service configuration via /hit/config endpoint.
    
    Returns:
        Configuration dictionary including module settings
    """
    client = _get_client()
    return await client.get_config()


async def version() -> dict:
    """Get ping-pong service version via /hit/version endpoint.
    
    Returns:
        Version dictionary with module name and version
    """
    client = _get_client()
    return await client.version()


# Export default client instance for convenience
ping_pong = _get_client()


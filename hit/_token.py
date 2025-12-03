"""Token management for Hit SDK authentication.

Handles fetching and caching service/project tokens from CAC for SDK requests.

Token Resolution Order:
1. HIT_SERVICE_TOKEN (new per-service tokens with module/database ACL)
2. HIT_PROJECT_TOKEN (legacy project-wide tokens, for backward compatibility)
3. Explicit token passed in constructor
"""

from __future__ import annotations

import os
import time
from typing import Optional

import httpx


class TokenManager:
    """Manages service/project tokens for SDK authentication.

    Prefers HIT_SERVICE_TOKEN (per-service with ACL) over HIT_PROJECT_TOKEN (legacy).
    Fetches tokens from CAC and caches them until expiration.
    """

    def __init__(
        self,
        cac_url: Optional[str] = None,
        project_slug: Optional[str] = None,
        namespace: Optional[str] = None,
        project_token: Optional[str] = None,
        service_token: Optional[str] = None,
    ):
        """Initialize token manager.

        Args:
            cac_url: CAC base URL (defaults to HIT_CAC_URL env var)
            project_slug: Project slug (defaults to HIT_PROJECT_SLUG env var)
            namespace: Namespace (defaults to HIT_NAMESPACE env var or "shared")
            project_token: Legacy project token (defaults to HIT_PROJECT_TOKEN env var)
            service_token: Per-service token with ACL (defaults to HIT_SERVICE_TOKEN env var)
        """
        self.cac_url = (cac_url or os.getenv("HIT_CAC_URL", "")).rstrip("/")
        self.project_slug = project_slug or os.getenv("HIT_PROJECT_SLUG", "")
        self.namespace = namespace or os.getenv("HIT_NAMESPACE", "shared")
        
        # Prefer service token over project token (service token has ACL)
        self._service_token = service_token or os.getenv("HIT_SERVICE_TOKEN")
        self._project_token = project_token or os.getenv("HIT_PROJECT_TOKEN")
        
        self._cached_token: Optional[str] = None
        self._token_expires_at: Optional[float] = None
        self._http_client = httpx.AsyncClient(timeout=10.0)

    async def get_token(self) -> Optional[str]:
        """Get a valid service or project token.

        Token resolution order:
        1. Explicitly provided service token (HIT_SERVICE_TOKEN)
        2. Explicitly provided project token (HIT_PROJECT_TOKEN)
        3. Cached token from previous fetch
        4. Fetch from CAC (if configured)

        Returns:
            Token string, or None if not available
        """
        # Prefer service token (new per-service with ACL)
        if self._service_token:
            return self._service_token
        
        # Fall back to project token (legacy)
        if self._project_token:
            return self._project_token

        # Check cached token
        if self._cached_token and self._token_expires_at:
            if time.time() < self._token_expires_at - 60:  # Refresh 1 min before expiry
                return self._cached_token

        # Fetch from CAC if configured
        if self.cac_url and self.project_slug:
            try:
                token = await self._fetch_token_from_cac()
                if token:
                    self._cached_token = token
                    # Assume 24 hour expiry (CAC default) - we'll refresh before then
                    self._token_expires_at = time.time() + (24 * 3600) - 3600
                    return token
            except Exception:
                # If CAC fetch fails, return None (SDK can work without token in local dev)
                pass

        return None

    async def _fetch_token_from_cac(self) -> Optional[str]:
        """Fetch project token from CAC.

        Returns:
            Token string or None if fetch fails
        """
        if not self.cac_url or not self.project_slug:
            return None

        # For now, we need CAC auth - in production this would use service account
        # For local dev, tokens should be set via env vars
        # TODO: Add service account auth for automated token fetching
        return None

    async def close(self):
        """Close HTTP client."""
        await self._http_client.aclose()


# Global token manager instance
_token_manager: Optional[TokenManager] = None


def get_token_manager() -> TokenManager:
    """Get or create global token manager instance."""
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager()
    return _token_manager


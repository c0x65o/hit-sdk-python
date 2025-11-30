"""Token management for Hit SDK authentication.

Handles fetching and caching project tokens from CAC for SDK requests.
"""

from __future__ import annotations

import os
import time
from typing import Optional

import httpx


class TokenManager:
    """Manages project tokens for SDK authentication.

    Fetches tokens from CAC and caches them until expiration.
    """

    def __init__(
        self,
        cac_url: Optional[str] = None,
        project_slug: Optional[str] = None,
        namespace: Optional[str] = None,
        project_token: Optional[str] = None,
    ):
        """Initialize token manager.

        Args:
            cac_url: CAC base URL (defaults to HIT_CAC_URL env var)
            project_slug: Project slug (defaults to HIT_PROJECT_SLUG env var)
            namespace: Namespace (defaults to HIT_NAMESPACE env var or "shared")
            project_token: Pre-configured project token (defaults to HIT_PROJECT_TOKEN env var)
        """
        self.cac_url = (cac_url or os.getenv("HIT_CAC_URL", "")).rstrip("/")
        self.project_slug = project_slug or os.getenv("HIT_PROJECT_SLUG", "")
        self.namespace = namespace or os.getenv("HIT_NAMESPACE", "shared")
        self._project_token = project_token or os.getenv("HIT_PROJECT_TOKEN")
        self._cached_token: Optional[str] = None
        self._token_expires_at: Optional[float] = None
        self._http_client = httpx.AsyncClient(timeout=10.0)

    async def get_token(self) -> Optional[str]:
        """Get a valid project token.

        Returns:
            Project token string, or None if not available
        """
        # If explicitly provided, use it
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


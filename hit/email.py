"""Email module client."""

from __future__ import annotations

from typing import Any, Dict, Optional

from ._client import HitClient
from ._config import get_api_key, get_namespace, get_service_url


class EmailClient:
    """Client for the Hit Email module."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        namespace: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        self.client = HitClient(
            base_url=base_url or get_service_url("email"),
            namespace=namespace or get_namespace(),
            api_key=api_key or get_api_key("email"),
            timeout=15.0,
        )

    async def send(
        self,
        to: str | list[str],
        subject: str,
        text: Optional[str] = None,
        html: Optional[str] = None,
        template_id: Optional[str] = None,
        template_variables: Optional[Dict[str, Any]] = None,
        from_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send an email."""

        payload = {
            "to": to,
            "subject": subject,
            "text": text,
            "html": html,
            "template_id": template_id,
            "template_variables": template_variables,
            "from_email": from_email,
        }
        return await self.client.post("/send", json=payload)

    async def config(self) -> Dict[str, Any]:
        """Fetch module configuration."""

        return await self.client.get("/config")

    async def features(self) -> Dict[str, Any]:
        """Get feature flags."""

        return await self.client.get("/features")


def _get_client() -> EmailClient:
    """Create a new client with current environment settings.
    
    Note: We create a fresh client each time to pick up any environment
    variable changes. This ensures service discovery works correctly
    in Kubernetes where env vars may be injected after module import.
    """
    return EmailClient()


async def send_email(
    to: str | list[str],
    subject: str,
    text: Optional[str] = None,
    html: Optional[str] = None,
    template_id: Optional[str] = None,
    template_variables: Optional[Dict[str, Any]] = None,
    from_email: Optional[str] = None,
) -> Dict[str, Any]:
    """Convenience function mirroring EmailClient.send."""
    return await _get_client().send(
        to=to,
        subject=subject,
        text=text,
        html=html,
        template_id=template_id,
        template_variables=template_variables,
        from_email=from_email,
    )


async def send(
    to: str | list[str],
    subject: str,
    text: Optional[str] = None,
    html: Optional[str] = None,
    template_id: Optional[str] = None,
    template_variables: Optional[Dict[str, Any]] = None,
    from_email: Optional[str] = None,
) -> Dict[str, Any]:
    """Send an email."""
    return await _get_client().send(
        to=to,
        subject=subject,
        text=text,
        html=html,
        template_id=template_id,
        template_variables=template_variables,
        from_email=from_email,
    )


async def config() -> Dict[str, Any]:
    """Fetch module configuration."""
    return await _get_client().config()


async def features() -> Dict[str, Any]:
    """Get feature flags."""
    return await _get_client().features()


class _LazyEmailClient:
    """Lazy proxy that creates EmailClient on first attribute access.
    
    This ensures service discovery happens at request time, not import time.
    """
    
    def __getattr__(self, name: str):
        return getattr(_get_client(), name)


# Export lazy client for backwards compatibility with `from hit.email import email`
email = _LazyEmailClient()

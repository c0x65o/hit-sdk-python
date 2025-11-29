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


_default_email_client: EmailClient | None = None


def get_default_client() -> EmailClient:
    global _default_email_client
    if not _default_email_client:
        _default_email_client = EmailClient()
    return _default_email_client


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

    client = get_default_client()
    return await client.send(
        to=to,
        subject=subject,
        text=text,
        html=html,
        template_id=template_id,
        template_variables=template_variables,
        from_email=from_email,
    )


email = get_default_client()

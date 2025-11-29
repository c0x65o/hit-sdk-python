"""Auth module client."""

from __future__ import annotations

from typing import Any, Dict, Optional

from ._client import HitClient
from ._config import get_api_key, get_namespace, get_service_url


class AuthClient:
    """Client wrapper for the Hit Auth module."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        namespace: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        self.client = HitClient(
            base_url=base_url or get_service_url("auth"),
            namespace=namespace or get_namespace(),
            api_key=api_key or get_api_key("auth"),
            timeout=15.0,
        )

    async def register(self, email: str, password: str) -> Dict[str, Any]:
        payload = {"email": email, "password": password}
        return await self.client.post("/register", json=payload)

    async def login(
        self,
        email: str,
        password: Optional[str] = None,
        two_factor_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "email": email,
            "password": password,
            "two_factor_code": two_factor_code,
        }
        return await self.client.post("/login", json=payload)

    async def verify_email(self, email: str, code: str) -> Dict[str, Any]:
        payload = {"email": email, "code": code}
        return await self.client.post("/verify-email", json=payload)

    async def enable_two_factor(self, email: str) -> Dict[str, Any]:
        return await self.client.post("/enable-2fa", json={"email": email})

    async def verify_two_factor(self, email: str, code: str) -> Dict[str, Any]:
        return await self.client.post(
            "/verify-2fa", json={"email": email, "code": code}
        )

    async def oauth_url(self, provider: str) -> Dict[str, Any]:
        return await self.client.post("/oauth/url", json={"provider": provider})

    async def oauth_callback(self, provider: str, oauth_code: str) -> Dict[str, Any]:
        payload = {"provider": provider, "oauth_code": oauth_code}
        return await self.client.post("/oauth/callback", json=payload)

    async def features(self) -> Dict[str, Any]:
        return await self.client.get("/config")


_default_auth_client: AuthClient | None = None


def get_default_client() -> AuthClient:
    global _default_auth_client
    if not _default_auth_client:
        _default_auth_client = AuthClient()
    return _default_auth_client


async def register(email: str, password: str) -> Dict[str, Any]:
    return await get_default_client().register(email, password)


async def login(
    email: str,
    password: Optional[str] = None,
    two_factor_code: Optional[str] = None,
) -> Dict[str, Any]:
    return await get_default_client().login(email, password, two_factor_code)


async def verify_email(email: str, code: str) -> Dict[str, Any]:
    return await get_default_client().verify_email(email, code)


auth = get_default_client()

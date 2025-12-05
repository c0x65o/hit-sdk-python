"""Auth module client.

Provides authentication for HIT applications:
- Password login with email verification
- OAuth providers (Google, Azure AD, GitHub)
- Two-factor authentication (TOTP, email)
- Session management with refresh tokens
- Token validation for other modules

Example:
    from hit.auth import auth
    
    # Register and login
    result = await auth.register("user@example.com", "Password123")
    token = result["token"]
    refresh_token = result["refresh_token"]
    
    # Refresh token when access token expires
    new_tokens = await auth.refresh(refresh_token)
    
    # Validate tokens (for other modules)
    validation = await auth.validate(token)
    if validation["valid"]:
        user_email = validation["claims"]["email"]
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from ._client import HitClient
from ._config import get_api_key, get_namespace, get_service_url


class AuthTokens:
    """Container for access and refresh tokens."""
    
    def __init__(self, token: str, refresh_token: Optional[str] = None, expires_in: int = 3600):
        self.token = token
        self.refresh_token = refresh_token
        self.expires_in = expires_in
    
    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> "AuthTokens":
        """Create from API response."""
        return cls(
            token=response["token"],
            refresh_token=response.get("refresh_token"),
            expires_in=response.get("expires_in", 3600),
        )


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
        """Register a new user.
        
        Args:
            email: User's email address
            password: Password (min 8 chars, uppercase, lowercase, digit)
            
        Returns:
            Dict with token, refresh_token, email_verified, expires_in
        """
        payload = {"email": email, "password": password}
        return await self.client.post("/register", json=payload)

    async def login(
        self,
        email: str,
        password: Optional[str] = None,
        two_factor_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Login with email and password.
        
        Args:
            email: User's email address
            password: User's password
            two_factor_code: 2FA code if required
            
        Returns:
            Dict with token, refresh_token, email_verified, two_factor_required, expires_in
            
        Raises:
            HitAPIError: 401 for invalid credentials, 403 for 2FA required
        """
        payload = {
            "email": email,
            "password": password,
            "two_factor_code": two_factor_code,
        }
        return await self.client.post("/login", json=payload)

    async def refresh(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using a refresh token.
        
        Args:
            refresh_token: Valid refresh token from login/register
            
        Returns:
            Dict with new token, refresh_token (rotated), expires_in
        """
        payload = {"refresh_token": refresh_token}
        return await self.client.post("/refresh", json=payload)

    async def logout(self, refresh_token: Optional[str] = None) -> Dict[str, Any]:
        """Logout and revoke refresh token.
        
        Args:
            refresh_token: Token to revoke (optional)
            
        Returns:
            Dict with status
        """
        payload = {"refresh_token": refresh_token}
        return await self.client.post("/logout", json=payload)

    async def logout_all(self, access_token: str) -> Dict[str, Any]:
        """Logout from all sessions.
        
        Args:
            access_token: Valid access token to identify user
            
        Returns:
            Dict with status and sessions_revoked count
        """
        # Need to pass token in header for this endpoint
        original_headers = self.client._client.headers.copy()
        self.client._client.headers["Authorization"] = f"Bearer {access_token}"
        try:
            return await self.client.post("/logout-all", json={})
        finally:
            self.client._client.headers = original_headers

    async def validate(self, token: str) -> Dict[str, Any]:
        """Validate a user token.
        
        Use this to validate tokens from users in other services.
        
        Args:
            token: Access token to validate
            
        Returns:
            Dict with valid (bool), claims (if valid), error (if invalid)
        """
        payload = {"token": token}
        return await self.client.post("/validate", json=payload)

    async def get_me(self, access_token: str) -> Dict[str, Any]:
        """Get current user's profile.
        
        Args:
            access_token: Valid access token
            
        Returns:
            User profile dict
        """
        original_headers = self.client._client.headers.copy()
        self.client._client.headers["Authorization"] = f"Bearer {access_token}"
        try:
            return await self.client.get("/me")
        finally:
            self.client._client.headers = original_headers

    async def verify_email(self, email: str, code: str) -> Dict[str, Any]:
        """Verify email with code.
        
        Args:
            email: User's email
            code: 6-digit verification code
            
        Returns:
            Dict with status
        """
        payload = {"email": email, "code": code}
        return await self.client.post("/verify-email", json=payload)

    async def enable_two_factor(self, email: str) -> Dict[str, Any]:
        """Enable two-factor authentication.
        
        Args:
            email: User's email
            
        Returns:
            Dict with status and setup info
        """
        return await self.client.post("/enable-2fa", json={"email": email})

    async def verify_two_factor(self, email: str, code: str) -> Dict[str, Any]:
        """Verify and complete 2FA setup.
        
        Args:
            email: User's email
            code: TOTP or email code
            
        Returns:
            Dict with status
        """
        return await self.client.post(
            "/verify-2fa", json={"email": email, "code": code}
        )

    async def oauth_url(self, provider: str) -> Dict[str, Any]:
        """Get OAuth redirect URL for a provider.
        
        Args:
            provider: OAuth provider (google, azure_ad, github)
            
        Returns:
            Dict with provider, url, additional_params
        """
        return await self.client.post("/oauth/url", json={"provider": provider})

    async def oauth_callback(self, provider: str, oauth_code: str) -> Dict[str, Any]:
        """Handle OAuth callback.
        
        Args:
            provider: OAuth provider
            oauth_code: Code from OAuth redirect
            
        Returns:
            Dict with token, refresh_token, email_verified, expires_in
        """
        payload = {"provider": provider, "oauth_code": oauth_code}
        return await self.client.post("/oauth/callback", json=payload)

    async def config(self) -> Dict[str, Any]:
        """Get module configuration."""
        return await self.client.get("/config")

    async def features(self) -> Dict[str, Any]:
        """Get feature flags."""
        return await self.client.get("/features")


def _get_client() -> AuthClient:
    """Create a new client with current environment settings.
    
    Note: We create a fresh client each time to pick up any environment
    variable changes. This ensures service discovery works correctly
    in Kubernetes where env vars may be injected after module import.
    """
    return AuthClient()


# Module-level convenience functions
async def register(email: str, password: str) -> Dict[str, Any]:
    """Register a new user."""
    return await _get_client().register(email, password)


async def login(
    email: str,
    password: Optional[str] = None,
    two_factor_code: Optional[str] = None,
) -> Dict[str, Any]:
    """Login with email and password."""
    return await _get_client().login(email, password, two_factor_code)


async def refresh(refresh_token: str) -> Dict[str, Any]:
    """Refresh access token using a refresh token."""
    return await _get_client().refresh(refresh_token)


async def logout(refresh_token: Optional[str] = None) -> Dict[str, Any]:
    """Logout and revoke refresh token."""
    return await _get_client().logout(refresh_token)


async def logout_all(access_token: str) -> Dict[str, Any]:
    """Logout from all sessions."""
    return await _get_client().logout_all(access_token)


async def validate(token: str) -> Dict[str, Any]:
    """Validate a user token."""
    return await _get_client().validate(token)


async def get_me(access_token: str) -> Dict[str, Any]:
    """Get current user's profile."""
    return await _get_client().get_me(access_token)


async def verify_email(email: str, code: str) -> Dict[str, Any]:
    """Verify email with code."""
    return await _get_client().verify_email(email, code)


async def enable_two_factor(email: str) -> Dict[str, Any]:
    """Enable two-factor authentication."""
    return await _get_client().enable_two_factor(email)


async def verify_two_factor(email: str, code: str) -> Dict[str, Any]:
    """Verify and complete 2FA setup."""
    return await _get_client().verify_two_factor(email, code)


async def oauth_url(provider: str) -> Dict[str, Any]:
    """Get OAuth redirect URL for a provider."""
    return await _get_client().oauth_url(provider)


async def oauth_callback(provider: str, oauth_code: str) -> Dict[str, Any]:
    """Handle OAuth callback."""
    return await _get_client().oauth_callback(provider, oauth_code)


async def config() -> Dict[str, Any]:
    """Get module configuration."""
    return await _get_client().config()


async def features() -> Dict[str, Any]:
    """Get feature flags."""
    return await _get_client().features()


class _LazyAuthClient:
    """Lazy proxy that creates AuthClient on first attribute access.
    
    This ensures service discovery happens at request time, not import time.
    """
    
    def __getattr__(self, name: str):
        return getattr(_get_client(), name)


auth = _LazyAuthClient()

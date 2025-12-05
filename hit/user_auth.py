"""User authentication helpers for FastAPI applications.

Provides dependencies for protecting API endpoints with user authentication.
Uses the auth module to validate user tokens.

Example:
    from fastapi import FastAPI, Depends
    from hit.user_auth import require_user, get_current_user
    
    app = FastAPI()
    
    @app.get("/protected")
    async def protected_endpoint(user = Depends(require_user())):
        # user contains decoded JWT claims
        return {"email": user["email"]}
    
    @app.get("/admin-only")
    async def admin_endpoint(user = Depends(require_user(roles=["admin"]))):
        return {"admin": True}
    
    @app.get("/optional-auth")
    async def optional_auth(user = Depends(get_current_user)):
        # user is None if no token provided
        if user:
            return {"logged_in": True, "email": user["email"]}
        return {"logged_in": False}
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .auth import validate

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> Optional[Dict[str, Any]]:
    """Get current user from token (optional).
    
    Returns user claims if valid token is provided, None otherwise.
    Does not raise exceptions for missing/invalid tokens.
    
    Returns:
        User claims dict or None
    """
    if not credentials:
        return None
    
    try:
        result = await validate(credentials.credentials)
        if result.get("valid"):
            return result.get("claims")
        return None
    except Exception:
        return None


def require_user(
    roles: Optional[List[str]] = None,
    verified_email: bool = False,
) -> Any:
    """Create a dependency that requires user authentication.
    
    Args:
        roles: Optional list of required roles (user must have at least one)
        verified_email: If True, require user's email to be verified
        
    Returns:
        FastAPI dependency that returns user claims
        
    Raises:
        HTTPException: 401 if not authenticated, 403 if insufficient permissions
        
    Example:
        @app.get("/admin")
        async def admin(user = Depends(require_user(roles=["admin"]))):
            return {"admin": True}
    """
    async def dependency(
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    ) -> Dict[str, Any]:
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            result = await validate(credentials.credentials)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {e}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not result.get("valid"):
            error = result.get("error", "Invalid token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error,
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        claims = result.get("claims", {})
        
        # Check email verification if required
        if verified_email and not claims.get("email_verified"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email verification required",
            )
        
        # Check roles if required
        if roles:
            user_roles = claims.get("roles", [])
            if not any(role in user_roles for role in roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )
        
        return claims
    
    return dependency


class UserContext:
    """User context for the current request.
    
    Provides typed access to user claims from the JWT token.
    """
    
    def __init__(self, claims: Dict[str, Any]):
        self._claims = claims
    
    @property
    def email(self) -> str:
        """User's email address."""
        return self._claims.get("email", "")
    
    @property
    def email_verified(self) -> bool:
        """Whether user's email is verified."""
        return self._claims.get("email_verified", False)
    
    @property
    def roles(self) -> List[str]:
        """User's roles."""
        return self._claims.get("roles", [])
    
    @property
    def project(self) -> Optional[str]:
        """Project slug from token."""
        return self._claims.get("prj")
    
    @property
    def claims(self) -> Dict[str, Any]:
        """Raw claims dictionary."""
        return self._claims
    
    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        return role in self.roles
    
    def has_any_role(self, roles: List[str]) -> bool:
        """Check if user has any of the specified roles."""
        return any(role in self.roles for role in roles)


def require_user_context(
    roles: Optional[List[str]] = None,
    verified_email: bool = False,
) -> Any:
    """Like require_user but returns a UserContext object.
    
    Args:
        roles: Optional list of required roles
        verified_email: If True, require verified email
        
    Returns:
        FastAPI dependency that returns UserContext
        
    Example:
        @app.get("/profile")
        async def profile(user: UserContext = Depends(require_user_context())):
            return {"email": user.email, "roles": user.roles}
    """
    user_dep = require_user(roles=roles, verified_email=verified_email)
    
    async def dependency(
        claims: Dict[str, Any] = Depends(user_dep),
    ) -> UserContext:
        return UserContext(claims)
    
    return dependency


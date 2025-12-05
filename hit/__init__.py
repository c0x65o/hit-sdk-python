"""Hit SDK for Python.

Strongly-typed client for Hit platform microservices.

Example:
    from hit import ping_pong, auth
    
    # Counter service
    count = await ping_pong.get_counter("test")
    new_count = await ping_pong.increment("test")
    
    # Authentication
    result = await auth.login("user@example.com", "password")
    token = result["token"]
    
    # Protected endpoints (FastAPI)
    from hit.user_auth import require_user
    
    @app.get("/protected")
    async def protected(user = Depends(require_user())):
        return {"email": user["email"]}
"""

# Import client instances from their modules
from hit import ping_pong
from hit.auth import auth
from hit.email import email

# User auth helpers for FastAPI
from hit.user_auth import require_user, get_current_user, UserContext, require_user_context

__version__ = "1.0.1"

__all__ = [
    "ping_pong",
    "email", 
    "auth",
    "require_user",
    "get_current_user",
    "UserContext",
    "require_user_context",
]

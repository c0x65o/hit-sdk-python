"""Hit SDK for Python.

Strongly-typed client for Hit platform microservices.

Example:
    from hit import ping_pong

    count = await ping_pong.get_counter("test")
    new_count = await ping_pong.increment("test")
"""

# Import client instances from their modules
from hit import ping_pong
from hit.auth import auth
from hit.email import email

__version__ = "1.0.0"

__all__ = ["ping_pong", "email", "auth"]

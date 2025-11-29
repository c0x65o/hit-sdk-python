"""Hit SDK for Python.

Strongly-typed client for Hit platform microservices.

Example:
    from hit import ping_pong

    count = await ping_pong.get_counter("test")
    new_count = await ping_pong.increment("test")
"""

from hit import auth, email, ping_pong

__version__ = "1.0.0"

__all__ = ["ping_pong", "email", "auth"]

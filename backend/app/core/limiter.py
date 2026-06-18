"""
Shared rate limiter instance for the application.

Used by routers that need rate limiting (e.g., auth/login).
Must be wired to the FastAPI app via `app.state.limiter = limiter` in main.py.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

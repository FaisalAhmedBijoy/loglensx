"""Integration modules for web frameworks."""

from .fastapi_integration import setup_fastapi_loglensx
from .flask_integration import setup_flask_loglensx

__all__ = ["setup_fastapi_loglensx", "setup_flask_loglensx"]
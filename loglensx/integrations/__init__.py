"""Integration modules for web frameworks."""

from .fastapi_integration import setup_fastapi_loglens
from .flask_integration import setup_flask_loglens

__all__ = ["setup_fastapi_loglens", "setup_flask_loglens"]

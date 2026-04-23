"""
LogLens - Interactive Log Viewer for Python Web Applications

A comprehensive log visualization and analysis tool for FastAPI and Flask applications.
"""

__version__ = "1.0.0"
__author__ = "LogLens Contributors"
__description__ = "Interactive log viewer with charts and visualizations for FastAPI and Flask"

from .core.parser import LogParser
from .core.analyzer import LogAnalyzer
from .integrations.fastapi_integration import setup_fastapi_loglens
from .integrations.flask_integration import setup_flask_loglens

__all__ = [
    "LogParser",
    "LogAnalyzer",
    "setup_fastapi_loglens",
    "setup_flask_loglens",
]

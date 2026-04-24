"""
loglensx - Interactive Log Viewer for Python Web Applications

A comprehensive log visualization and analysis tool for FastAPI and Flask applications.
"""

__version__ = "1.0.1"
__author__ = "loglensx Contributors"
__description__ = "Interactive log viewer with charts and visualizations for FastAPI and Flask"

from .core.parser import LogParser
from .core.analyzer import LogAnalyzer


def _missing_optional_dependency(framework: str, extra: str):
    """Create a helpful placeholder for an unavailable optional integration."""

    def _setup(*args, **kwargs):
        raise ImportError(
            f"{framework} support requires optional dependencies. "
            f"Install them with: pip install 'loglensx[{extra}]'"
        )

    _setup.__name__ = f"setup_{extra}_loglensx"
    return _setup


try:
    from .integrations.fastapi_integration import setup_fastapi_loglensx
except ModuleNotFoundError as exc:
    if exc.name != "fastapi":
        raise
    setup_fastapi_loglensx = _missing_optional_dependency("FastAPI", "fastapi")

try:
    from .integrations.flask_integration import setup_flask_loglensx
except ModuleNotFoundError as exc:
    if exc.name != "flask":
        raise
    setup_flask_loglensx = _missing_optional_dependency("Flask", "flask")

__all__ = [
    "LogParser",
    "LogAnalyzer",
    "setup_fastapi_loglensx",
    "setup_flask_loglensx",
]

"""Integration modules for web frameworks."""

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
    from .fastapi_integration import setup_fastapi_loglensx
except ModuleNotFoundError as exc:
    if exc.name != "fastapi":
        raise
    setup_fastapi_loglensx = _missing_optional_dependency("FastAPI", "fastapi")

try:
    from .flask_integration import setup_flask_loglensx
except ModuleNotFoundError as exc:
    if exc.name != "flask":
        raise
    setup_flask_loglensx = _missing_optional_dependency("Flask", "flask")

__all__ = ["setup_fastapi_loglensx", "setup_flask_loglensx"]

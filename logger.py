import os
import logging
import inspect
from datetime import datetime
from typing import List, Dict, Any

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


def formated_api_exception_response(
    logger,
    e: Exception,
    error_code: str,
    request: Request = None,
    app_env: str = "DEVELOPMENT"
):
    """
    Format and log API exceptions with detailed context information.
    
    Args:
        logger: Logger instance
        e: Exception object
        error_code: Error code identifier
        request: FastAPI Request object (optional)
        app_env: Application environment (default: "DEVELOPMENT")
    
    Raises:
        HTTPException: Always raises with formatted error response
    """
    # Safely extract traceback information
    tb = e.__traceback__ if e.__traceback__ is not None else None
    if tb is None:
        file_path = "Unknown"
        line = 0
    else:
        try:
            file_path = os.path.relpath(tb.tb_frame.f_code.co_filename, start=os.getcwd())
            line = tb.tb_lineno
        except (OSError, ValueError):
            file_path = "Unknown"
            line = 0
    
    server = app_env.upper()  # e.g., "DEV", "PRODUCTION"
    error_type = type(e).__name__
    error_msg = str(e)

    # Get calling function and module path safely
    frame = inspect.currentframe()
    function_name = frame.f_back.f_code.co_name if frame and frame.f_back else "unknown"

    # Get request path if available (safe dict access)
    route_path = request.scope.get('path', 'N/A') if request else 'N/A'

    context = {
        "route": route_path,
        "function": function_name,
        "file": file_path,
        "line": line,
        "code": error_code
    }

    exception = {
        "exception": f"{error_type}: {error_msg}"
    }

    log_message = (
        f"{server}.ERROR: "
        f"{error_msg} "
        f"{context} {exception}"
    )

    logger.error(log_message)

    raise HTTPException(
        status_code=500,
        detail={
            "status": "error",
            "message": (
                f"Internal server error in `{function_name}()` "
                f"[{error_code}] — {error_type}: {error_msg}"
            ),
            "status_code": 500
        }
    )


def configure_logging(logger_name: str = "fastapi_app") -> logging.Logger:
    """
    Configure structured logging for FastAPI applications.
    
    Args:
        logger_name: Name of the logger (default: "fastapi_app")
    
    Returns:
        logging.Logger: Configured logger instance
    """
    try:
        logger = logging.getLogger(logger_name)

        # Avoid duplicate handlers during reload
        if logger.handlers:
            return logger

        # Ensure log directory exists
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        # Generate file name with current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        log_filename = f"log_file_{current_date}.log"
        log_file_path = os.path.join(log_dir, log_filename)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

        # File handler with daily log file
        file_handler = logging.FileHandler(log_file_path, mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        logger.setLevel(logging.DEBUG)

        return logger
    except Exception as e:
        logging.error(f"Failed to configure logging: {e}", exc_info=True)
        return logging.getLogger(logger_name)

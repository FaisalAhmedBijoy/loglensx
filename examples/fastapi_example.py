"""
FastAPI example showing LogLens integration.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from loglensx import setup_fastapi_loglens

# Configure logging
import os
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f"log_file_{datetime.now().strftime('%Y-%m-%d')}.log")
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="LogLens FastAPI Example")

# Setup LogLens
setup_fastapi_loglens(app, log_dir="logs", prefix="/loglens")


@app.get("/")
def read_root():
    """Root endpoint."""
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to LogLens FastAPI Example", "logs_url": "/loglens/"}


@app.get("/api/items/{item_id}")
def get_item(item_id: int):
    """Get an item by ID."""
    logger.info(f"Getting item with ID: {item_id}")
    
    if item_id < 1:
        logger.warning(f"Invalid item ID requested: {item_id}")
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid item ID"}
        )
    
    logger.debug(f"Item {item_id} found in database")
    return {"item_id": item_id, "name": f"Item {item_id}"}


@app.post("/api/items")
def create_item(name: str):
    """Create a new item."""
    logger.info(f"Creating new item: {name}")
    
    if not name.strip():
        logger.error("Attempt to create item with empty name")
        return JSONResponse(
            status_code=400,
            content={"error": "Item name cannot be empty"}
        )
    
    logger.debug(f"Item created successfully: {name}")
    return {"id": 1, "name": name, "status": "created"}


@app.get("/api/error-test")
def test_error():
    """Endpoint to test error logging."""
    logger.error("This is a test error message")
    logger.warning("This is a test warning message")
    return {"message": "Check /loglens/ to see the logged error and warning"}


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("LogLens FastAPI Example")
    print("="*60)
    print("Main app:  http://localhost:8000/")
    print("LogLens:   http://localhost:8000/loglens/")
    print("API Docs:  http://localhost:8000/docs")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

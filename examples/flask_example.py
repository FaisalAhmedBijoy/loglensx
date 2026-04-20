"""
Flask example showing LogLens integration.
"""

from flask import Flask, jsonify
import logging
from datetime import datetime
from loglens import setup_flask_loglens
import os

# Create Flask app
app = Flask(__name__)

# Configure logging
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

# Setup LogLens
setup_flask_loglens(app, log_dir="logs", prefix="/loglens")


@app.route("/")
def home():
    """Home route."""
    logger.info("Home page accessed")
    return jsonify({
        "message": "Welcome to LogLens Flask Example",
        "logs_url": "/loglens/"
    })


@app.route("/api/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    """Get an item by ID."""
    logger.info(f"Getting item with ID: {item_id}")
    
    if item_id < 1:
        logger.warning(f"Invalid item ID requested: {item_id}")
        return jsonify({"error": "Invalid item ID"}), 400
    
    logger.debug(f"Item {item_id} found in database")
    return jsonify({"item_id": item_id, "name": f"Item {item_id}"})


@app.route("/api/items", methods=["POST"])
def create_item():
    """Create a new item."""
    from flask import request
    
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    
    logger.info(f"Creating new item: {name}")
    
    if not name:
        logger.error("Attempt to create item with empty name")
        return jsonify({"error": "Item name cannot be empty"}), 400
    
    logger.debug(f"Item created successfully: {name}")
    return jsonify({"id": 1, "name": name, "status": "created"})


@app.route("/api/error-test")
def test_error():
    """Endpoint to test error logging."""
    logger.error("This is a test error message")
    logger.warning("This is a test warning message")
    logger.info("This is a test info message")
    logger.debug("This is a test debug message")
    return jsonify({"message": "Check /loglens/ to see the logged messages"})


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    logger.warning(f"404 error: Resource not found")
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"500 error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    print("\n" + "="*60)
    print("LogLens Flask Example")
    print("="*60)
    print("Main app:  http://localhost:5000/")
    print("LogLens:   http://localhost:5000/loglens/")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)

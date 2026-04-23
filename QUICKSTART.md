# Quick Start Guide for LogLens

## Installation

### Basic Installation
```bash
pip install loglensx
```

### With FastAPI
```bash
pip install loglensx[fastapi]
```

### With Flask
```bash
pip install loglensx[flask]
```

### For Development
```bash
pip install loglensx[dev]
```

## 5-Minute Tutorial

### 1. FastAPI Setup (3 minutes)

```python
# main.py
from fastapi import FastAPI
from loglensx import setup_fastapi_loglens
import logging
from datetime import datetime
import os

app = FastAPI()

# Setup logging
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
setup_fastapi_loglens(app, log_dir="logs", prefix="/loglens")

@app.get("/")
def read_root():
    logger.info("Root endpoint called")
    return {"status": "ok"}

@app.get("/error-test")
def test():
    logger.error("This is a test error")
    return {"status": "error logged"}
```

Run:
```bash
pip install uvicorn
uvicorn main:app --reload
```

Visit:
- App: http://localhost:8000/
- LogLens: http://localhost:8000/loglens/

### 2. Flask Setup (3 minutes)

```python
# app.py
from flask import Flask, jsonify
from loglensx import setup_flask_loglens
import logging
from datetime import datetime
import os

app = Flask(__name__)

# Setup logging
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
    logger.info("Home page accessed")
    return jsonify({"status": "ok"})

@app.route("/error-test")
def test():
    logger.error("This is a test error")
    return jsonify({"status": "error logged"})
```

Run:
```bash
python app.py
```

Visit:
- App: http://localhost:5000/
- LogLens: http://localhost:5000/loglens/

### 3. Standalone Usage (2 minutes)

```python
from loglensx import LogParser, LogAnalyzer

# Parse logs
parser = LogParser(log_dir="logs")
analyzer = LogAnalyzer(parser)

# Get summary
summary = analyzer.get_log_summary()
print(f"Total logs: {summary['total_logs']}")
print(f"Errors: {summary['error_count']}")

# Get recent errors
errors = analyzer.get_recent_errors(limit=5)
for error in errors:
    print(f"Error: {error['message']}")
```

## Dashboard Features

### Main View
- **Statistics Cards** - Total logs, errors, warnings, etc.
- **Level Distribution** - Pie chart showing log level breakdown
- **Error Timeline** - Line chart of errors over time
- **Top Loggers** - Bar chart of most active loggers
- **Recent Errors** - Table of latest error entries

### Search Features
- Search by keyword
- Filter by log level (ERROR, WARNING, INFO, DEBUG)
- View all available log files

## API Endpoints

```bash
# Get dashboard
curl http://localhost:8000/loglens/

# Get logs (with filters)
curl http://localhost:8000/loglens/api/logs?level=ERROR&limit=10
curl http://localhost:8000/loglens/api/logs?search=database

# Get statistics
curl http://localhost:8000/loglens/api/stats

# Search logs
curl http://localhost:8000/loglens/api/search?q=error

# List log files
curl http://localhost:8000/loglens/api/files
```

## Log Format

LogLens expects logs in this format:

```
[2024-01-15 10:30:45] [ERROR] [app.module] Error message here
[2024-01-15 10:30:46] [WARNING] [app.module] Warning message here
[2024-01-15 10:30:47] [INFO] [app.module] Info message here
```

Your Python logging configuration:

```python
import logging

handler = logging.FileHandler('logs/log_file_{}.log'.format(
    datetime.now().strftime('%Y-%m-%d')
))
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
```

## Next Steps

1. **Explore Examples** - See `examples/` directory for complete working examples
2. **Read Documentation** - Check `README.md` for detailed documentation
3. **Run Tests** - `pytest tests/` to verify installation
4. **Customize** - Adjust log directory, URL prefix, and styling to your needs

## Troubleshooting

### Logs not appearing?
1. Check `logs/` directory exists
2. Verify logs are being written
3. Check file format matches expected pattern
4. Look at server console for parsing errors

### Dashboard won't load?
1. Verify app is running (FastAPI/Flask)
2. Check browser console for errors
3. Ensure prefix matches your configuration
4. Check firewall/network settings

### Getting help?
- Check README.md for detailed documentation
- Look at examples/ for working code
- Review PUBLISHING.md for deployment info
- Check test_loglens.py for API usage examples

## What's Next?

- Deploy your app with LogLens enabled
- Monitor your application logs in real-time
- Share insights with your team using the dashboard
- Integrate LogLens into your CI/CD pipeline

Happy logging! 🎉

# loglensx Quick Start

This guide gets `loglensx` running in a Flask app, a FastAPI app, or a standalone script. For full package documentation, see `README.md`.

## Install

Core package:

```bash
pip install loglensx
```

With Flask support:

```bash
pip install "loglensx[flask]"
```

With FastAPI support:

```bash
pip install "loglensx[fastapi]"
```

For local development from this repository:

```bash
pip install -e ".[dev,flask,fastapi]"
```

## Expected Log Format

The default parser works with standard Python logging output like this:

```text
[2024-01-15 10:30:45] [ERROR] [app.database] Connection timeout
[2024-01-15 10:30:46] [WARNING] [app.cache] Cache miss
[2024-01-15 10:30:47] [INFO] [app.api] GET /users - 200
```

Use this formatter in your app:

```python
import logging
import os
from datetime import datetime

os.makedirs("logs", exist_ok=True)
log_file = f"logs/log_file_{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)
```

## Flask in 3 Minutes

Create `app.py`:

```python
import logging
import os
from datetime import datetime

from flask import Flask, jsonify
from loglensx import setup_flask_loglensx

app = Flask(__name__)

os.makedirs("logs", exist_ok=True)
log_file = f"logs/log_file_{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

setup_flask_loglensx(app, log_dir="logs", prefix="/loglensx")


@app.route("/")
def home():
    logger.info("Home page accessed")
    return jsonify({"status": "ok", "dashboard": "/loglensx/"})


@app.route("/error-test")
def error_test():
    logger.error("Example error from Flask")
    return jsonify({"status": "error logged"})


if __name__ == "__main__":
    app.run(port=5000)
```

Run:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000/loglensx/
```

## FastAPI in 3 Minutes

Create `main.py`:

```python
import logging
import os
from datetime import datetime

from fastapi import FastAPI
from loglensx import setup_fastapi_loglensx

app = FastAPI()

os.makedirs("logs", exist_ok=True)
log_file = f"logs/log_file_{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

setup_fastapi_loglensx(app, log_dir="logs", prefix="/loglensx")


@app.get("/")
def home():
    logger.info("Root endpoint accessed")
    return {"status": "ok", "dashboard": "/loglensx/"}


@app.get("/error-test")
def error_test():
    logger.error("Example error from FastAPI")
    return {"status": "error logged"}
```

Run:

```bash
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000/loglensx/
```

## Standalone Usage

Use `LogParser` and `LogAnalyzer` without a web framework:

```python
from loglensx import LogAnalyzer, LogParser

parser = LogParser(log_dir="logs")
analyzer = LogAnalyzer(parser)

summary = analyzer.get_log_summary()
print("Total logs:", summary["total_logs"])
print("Errors:", summary["error_count"])

for entry in analyzer.get_recent_errors(limit=5):
    print(entry["timestamp"], entry["message"])
```

## Dashboard Features

The mounted dashboard includes:

- Summary metrics for total logs, errors, warnings, loggers, files, and stability
- Log level distribution chart
- Error frequency timeline
- Top loggers chart
- Recent errors table with expandable messages
- Log explorer with search, level, logger, and row-limit filters
- JSON APIs for logs, statistics, search, and file metadata

## Useful Endpoints

These examples assume the dashboard is mounted at `/loglensx`.

```bash
curl "http://127.0.0.1:5000/loglensx/api/logs?level=ERROR&limit=20"
curl "http://127.0.0.1:5000/loglensx/api/logs?search=database"
curl "http://127.0.0.1:5000/loglensx/api/stats"
curl "http://127.0.0.1:5000/loglensx/api/search?query=timeout"
curl "http://127.0.0.1:5000/loglensx/api/files"
```

## Visualization JSON Viewer

The standalone example can generate Plotly figure JSON files in `visualizations/`. To view them as charts, serve the repository root:

```bash
python -m http.server 8080
```

Then open:

```text
http://127.0.0.1:8080/visualizations/
```

## Run Included Examples

From the repository root:

```bash
python examples/flask_example.py
python examples/fastapi_example.py
python examples/standalone_example.py
```

## Troubleshooting

### Dashboard does not load

- Confirm the app server is running.
- Confirm the URL includes the configured prefix, for example `/loglensx/`.
- Install the correct framework extra: `loglensx[flask]` or `loglensx[fastapi]`.

### Logs do not appear

- Confirm the log directory exists.
- Confirm log files use the `.log` extension.
- Confirm your log format matches the default parser or configure a custom pattern.
- Generate a new log entry and refresh the dashboard.

### Tests fail because of coverage options

Install development dependencies:

```bash
pip install -e ".[dev,flask,fastapi]"
```

Or run without configured coverage options:

```bash
pytest -q -o addopts=""
```

# loglensx

[![PyPI version](https://badge.fury.io/py/loglensx.svg)](https://badge.fury.io/py/loglensx)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

`loglensx` is an interactive log viewer and analysis toolkit for Python applications. It parses standard application log files, summarizes errors and warnings, generates Plotly visualizations, and adds a professional dashboard to FastAPI or Flask apps with a single setup function.

It is designed for teams that want a lightweight operational view of local or server-side logs without deploying a full observability stack.

## Highlights

- Framework integrations for FastAPI and Flask
- Responsive dashboard with metric cards, Plotly charts, and searchable tables
- Log explorer with filters for search text, level, logger, and row limits
- JSON APIs for logs, statistics, search results, and log file metadata
- Standalone parser and analyzer APIs for scripts, notebooks, and CLI workflows
- Plotly figure JSON generation for custom dashboards or static viewers
- Support for common Python logging formats and custom regex parsing

## Installation

Install the core package:

```bash
pip install loglensx
```

Install with a web framework extra:

```bash
pip install "loglensx[flask]"
pip install "loglensx[fastapi]"
```

Install for local development:

```bash
pip install -e ".[dev,flask,fastapi]"
```

## Quick Start

### Flask

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


if __name__ == "__main__":
    app.run(port=5000)
```

Run the app and open:

```text
http://127.0.0.1:5000/loglensx/
```

### FastAPI

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
```

Run the app and open:

```bash
uvicorn main:app --reload
```

```text
http://127.0.0.1:8000/loglensx/
```

### Standalone Analysis

```python
from loglensx import LogAnalyzer, LogParser

parser = LogParser(log_dir="logs")
analyzer = LogAnalyzer(parser)

summary = analyzer.get_log_summary()
print(summary["total_logs"], "logs parsed")
print(summary["error_count"], "errors found")

for entry in analyzer.get_recent_errors(limit=5):
    print(entry["timestamp"], entry["message"])
```

## Dashboard

The integrated dashboard includes:

- Summary metrics for total logs, errors, warnings, loggers, files, and stability score
- Log level distribution chart
- Error frequency timeline
- Top loggers chart
- Recent errors table with expandable long messages
- Log explorer with server-side filters and client-side table search
- Responsive layout for desktop and mobile screens

Mount path is controlled by the `prefix` argument:

```python
setup_flask_loglensx(app, log_dir="logs", prefix="/internal/logs")
setup_fastapi_loglensx(app, log_dir="logs", prefix="/internal/logs")
```

## API Reference

When the dashboard is mounted at `/loglensx`, these routes are available:

| Route | Description |
| --- | --- |
| `GET /loglensx/` | Dashboard UI |
| `GET /loglensx/logs` | Log explorer UI |
| `GET /loglensx/api/logs` | Filtered log entries as JSON |
| `GET /loglensx/api/stats` | Summary statistics, level counts, top loggers, and error frequency |
| `GET /loglensx/api/search` | Search log entries |
| `GET /loglensx/api/files` | Log file metadata |

Common query parameters for `/api/logs` and `/logs`:

| Parameter | Example | Description |
| --- | --- | --- |
| `search` | `database` | Match text in log messages |
| `level` | `ERROR` | Filter by log level |
| `logger` | `app.api` | Match logger names |
| `limit` | `100` | Maximum rows to return |

Examples:

```bash
curl "http://127.0.0.1:5000/loglensx/api/logs?level=ERROR&limit=20"
curl "http://127.0.0.1:5000/loglensx/api/stats"
curl "http://127.0.0.1:5000/loglensx/api/search?query=timeout"
```

## Log Format

The default parser supports log lines like this:

```text
[2024-01-15 10:30:45] [ERROR] [app.database] Connection timeout
[2024-01-15 10:30:46] [WARNING] [app.cache] Cache miss
[2024-01-15 10:30:47] [INFO] [app.api] GET /users - 200
```

Recommended Python logging format:

```python
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()],
)
```

You can also provide a custom regex pattern:

```python
from loglensx import LogParser

pattern = r"(?P<timestamp>.*?)\\|(?P<level>\\w+)\\|(?P<logger>.*?)\\|(?P<message>.*)"
parser = LogParser(log_dir="logs", pattern=pattern)
```

The pattern should use named groups where possible:

- `timestamp`
- `level`
- `logger`
- `message`

## Visualization JSON

`ChartGenerator` returns Plotly figure JSON. You can save that JSON and render it in any page that loads Plotly.

```python
from pathlib import Path

from loglensx import LogAnalyzer, LogParser
from loglensx.visualizers import ChartGenerator

parser = LogParser(log_dir="logs")
analyzer = LogAnalyzer(parser)

Path("visualizations").mkdir(exist_ok=True)
Path("visualizations/level_distribution.json").write_text(
    ChartGenerator.plotly_level_distribution(analyzer.get_level_statistics())
)
Path("visualizations/error_timeline.json").write_text(
    ChartGenerator.plotly_error_timeline(analyzer.get_error_frequency())
)
Path("visualizations/top_loggers.json").write_text(
    ChartGenerator.plotly_top_loggers(analyzer.get_top_loggers(limit=10))
)
```

This repository includes a simple viewer at `visualizations/index.html`. Serve the project folder and open the viewer:

```bash
python -m http.server 8080
```

```text
http://127.0.0.1:8080/visualizations/
```

## Core API

### `LogParser`

```python
from loglensx import LogParser

parser = LogParser(log_dir="logs")

files = parser.get_log_files(limit=5)
entries = parser.parse_all_logs()
matches = parser.search_logs("timeout", limit=50)
by_level = parser.parse_logs_by_level()
```

### `LogAnalyzer`

```python
from loglensx import LogAnalyzer

analyzer = LogAnalyzer(parser)

summary = analyzer.get_log_summary()
level_stats = analyzer.get_level_statistics()
top_loggers = analyzer.get_top_loggers(limit=10)
error_frequency = analyzer.get_error_frequency(hours=24)
recent_errors = analyzer.get_recent_errors(limit=10)

filtered = analyzer.filter_logs(
    level="ERROR",
    logger="database",
    search_term="timeout",
    limit=100,
)
```

### `TableGenerator`

```python
from loglensx.visualizers import TableGenerator

html = TableGenerator.logs_to_html_table(recent_errors, title="Recent Errors")
```

## Examples

Complete examples are available in the `examples/` directory:

| File | Purpose |
| --- | --- |
| `examples/flask_example.py` | Flask app with dashboard routes |
| `examples/fastapi_example.py` | FastAPI app with dashboard routes |
| `examples/standalone_example.py` | Parser, analyzer, and visualization JSON workflow |

Run the Flask example:

```bash
python examples/flask_example.py
```

Run the FastAPI example:

```bash
python examples/fastapi_example.py
```

Run the standalone example:

```bash
python examples/standalone_example.py
```

## CLI

After installation, `loglensx` provides a small summary command that reads from the default `logs/` directory:

```bash
loglensx
```

It prints total logs, counts by level, unique loggers, log file count, and recent errors.

## Project Structure

```text
loglensx/
  core/
    parser.py
    analyzer.py
  integrations/
    fastapi_integration.py
    flask_integration.py
    _dashboard.py
  visualizers/
    charts.py
    tables.py
examples/
tests/
visualizations/
```

## Development

Create a local environment and install development dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,flask,fastapi]"
```

Run tests:

```bash
pytest
```

If `pytest-cov` is not installed in your environment, run tests without the configured coverage options:

```bash
pytest -q -o addopts=""
```

## Troubleshooting

### Dashboard page does not open

- Confirm the Flask or FastAPI server is running.
- Use the correct prefix, for example `/loglensx/`.
- Check that the framework extra is installed: `loglensx[flask]` or `loglensx[fastapi]`.

### Logs are not visible

- Confirm `log_dir` points to the directory where log files are written.
- Confirm files have a `.log` extension.
- Confirm your log format matches the default parser or pass a custom regex pattern.
- Generate a test log entry and refresh the dashboard.

### Visualization JSON opens as raw text

The JSON files are data, not standalone charts. Use `visualizations/index.html` through a local server:

```bash
python -m http.server 8080
```

Then open `http://127.0.0.1:8080/visualizations/`.

### Import fails when running examples directly

Run examples from the repository root:

```bash
python examples/flask_example.py
python examples/fastapi_example.py
```

For installed usage, install the package first:

```bash
pip install -e ".[flask,fastapi]"
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Support

Open issues and feature requests on the project issue tracker:

https://github.com/faisalahmedbijoy/loglensx/issues

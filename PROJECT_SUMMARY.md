# loglensx Project Summary

`loglensx` is a Python log analysis and visualization package. It can be used as a standalone parser/analyzer, as a Flask dashboard, or as a FastAPI dashboard.

The project focuses on a small and practical workflow:

1. Write normal Python logs to `.log` files.
2. Parse those logs with `LogParser`.
3. Analyze them with `LogAnalyzer`.
4. Display them through a web dashboard, JSON API, generated Plotly figures, or terminal summary.

## Current State

| Area | Status |
| --- | --- |
| Core parser and analyzer | Implemented |
| Flask integration | Implemented |
| FastAPI integration | Implemented |
| Shared dashboard renderer | Implemented |
| Plotly chart JSON generation | Implemented |
| HTML table generation | Implemented |
| Standalone examples | Implemented |
| Tests | Implemented |
| Packaging metadata | Implemented |
| Publication docs | Implemented |

## Architecture

```text
loglensx/
  __init__.py
  cli.py
  core/
    parser.py
    analyzer.py
  integrations/
    _dashboard.py
    fastapi_integration.py
    flask_integration.py
  visualizers/
    charts.py
    tables.py
examples/
tests/
visualizations/
```

### Core Layer

`LogParser` is responsible for file discovery and parsing. It reads `.log` files, extracts structured fields, and preserves source metadata.

`LogAnalyzer` is responsible for aggregations and query behavior. It produces summaries, counts, filtered rows, recent errors, top loggers, and error frequency data.

### Visualization Layer

`ChartGenerator` converts analyzer results into Plotly-compatible figure JSON. These figures can be embedded in the dashboard, saved to disk, or rendered in any Plotly page.

`TableGenerator` converts log entries into HTML tables with severity badges, source metadata, expandable messages, and table attributes used by the dashboard JavaScript.

### Integration Layer

The Flask and FastAPI integrations expose the same user-facing behavior:

- Dashboard page.
- Log explorer page.
- JSON logs endpoint.
- Statistics endpoint.
- Search endpoint.
- Log file metadata endpoint.

Both integrations use `loglensx/integrations/_dashboard.py` for shared HTML, CSS, JavaScript, and route-page rendering. This keeps the dashboard experience consistent across frameworks.

## Main Capabilities

### Parsing

- Reads `.log` files from a configurable directory.
- Supports the bracketed logging format used by the examples.
- Falls back gracefully for simple messages.
- Allows custom regex patterns.
- Tracks file name and line number for each entry.

### Analysis

- Total log counts.
- Error, warning, info, and debug counts.
- Unique logger counts.
- Log file counts.
- Recent errors and warnings.
- Top loggers.
- Error frequency by hour.
- Filtered log retrieval by level, logger, message search, and limit.

### Dashboard

- Responsive layout.
- Summary metric cards.
- Plotly charts for level distribution, error timeline, and top loggers.
- Log explorer with server-side filters.
- Client-side table search, sort, and level filtering.
- Expandable long messages.
- Source file and line number display.

### APIs

Default route prefix:

```text
/loglensx
```

Available routes:

```text
GET /loglensx/
GET /loglensx/logs
GET /loglensx/api/logs
GET /loglensx/api/stats
GET /loglensx/api/search
GET /loglensx/api/files
```

### Standalone Workflow

The standalone example demonstrates:

- Creating sample logs.
- Printing summaries in the terminal.
- Filtering logs.
- Searching logs.
- Writing Plotly JSON to `visualizations/`.
- Viewing generated JSON with `visualizations/index.html`.

## Package Metadata

| Field | Value |
| --- | --- |
| Name | `loglensx` |
| Python | `>=3.8` |
| License | MIT |
| Core dependencies | `plotly`, `python-dateutil` |
| Optional extras | `flask`, `fastapi`, `dev` |
| Console script | `loglensx` |

Before a release, verify that all version declarations match:

- `pyproject.toml`
- `setup.py`
- `loglensx/__init__.py`

## Example Usage

### Flask

```python
from flask import Flask
from loglensx import setup_flask_loglensx

app = Flask(__name__)
setup_flask_loglensx(app, log_dir="logs", prefix="/loglensx")
```

### FastAPI

```python
from fastapi import FastAPI
from loglensx import setup_fastapi_loglensx

app = FastAPI()
setup_fastapi_loglensx(app, log_dir="logs", prefix="/loglensx")
```

### Standalone

```python
from loglensx import LogAnalyzer, LogParser

parser = LogParser(log_dir="logs")
analyzer = LogAnalyzer(parser)

print(analyzer.get_log_summary())
```

## Quality Checks

Recommended checks before publishing:

```bash
python -m compileall loglensx examples tests
pytest
twine check dist/*
```

If `pytest-cov` is not installed:

```bash
pytest -q -o addopts=""
```

## Release Workflow

1. Update version values.
2. Update `CHANGELOG.md`.
3. Run tests and syntax checks.
4. Clean old builds.
5. Build with `python -m build`.
6. Validate with `twine check dist/*`.
7. Upload to TestPyPI or PyPI.
8. Tag the release in Git.

See `PUBLISHING.md` and `PUBLICATION_CHECKLIST.md` for the detailed release process.

## Maintenance Notes

- Keep Flask and FastAPI dashboard behavior aligned through the shared renderer.
- Keep examples runnable directly from the repository root.
- Keep generated visualization docs aligned with `visualizations/index.html`.
- Avoid documenting a release as ready until version metadata is synchronized.
- Keep `CHANGELOG.md` updated before publishing.

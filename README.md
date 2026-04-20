# LogLens - Interactive Log Viewer

[![PyPI version](https://badge.fury.io/py/loglens.svg)](https://badge.fury.io/py/loglens)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful, interactive log viewer and analyzer for Python web applications. LogLens provides beautiful dashboards with real-time charts, tables, and analytics for your application logs.

## Features

✨ **Interactive Dashboards**
- Real-time log visualization with charts and graphs
- Log level distribution (pie charts)
- Error frequency timeline
- Top loggers analysis

📊 **Rich Analytics**
- Log statistics and summary
- Error and warning frequency tracking
- Logger distribution analysis
- Full-text search across logs

🚀 **Framework Integration**
- **FastAPI** - Add LogLens with a single function call
- **Flask** - Seamless Flask integration
- Works with any Python logging setup

🎨 **Beautiful UI**
- Responsive design with Plotly charts
- Dark/Light theme support
- Mobile-friendly interface
- Real-time updates

## Installation

Install LogLens from PyPI:

```bash
pip install loglens
```

### With Framework Support

**FastAPI:**
```bash
pip install loglens[fastapi]
```

**Flask:**
```bash
pip install loglens[flask]
```

**Development:**
```bash
pip install loglens[dev]
```

## Quick Start

### FastAPI Integration

```python
from fastapi import FastAPI
from loglens import setup_fastapi_loglens

app = FastAPI()

# Setup LogLens at your preferred URL prefix
setup_fastapi_loglens(app, log_dir="logs", prefix="/loglens")

# Now access the dashboard at http://localhost:8000/loglens/
```

### Flask Integration

```python
from flask import Flask
from loglens import setup_flask_loglens

app = Flask(__name__)

# Setup LogLens
setup_flask_loglens(app, log_dir="logs", prefix="/loglens")

# Access the dashboard at http://localhost:5000/loglens/
```

### Standalone Usage

```python
from loglens import LogParser, LogAnalyzer

# Parse logs
parser = LogParser(log_dir="logs")
analyzer = LogAnalyzer(parser)

# Get statistics
summary = analyzer.get_log_summary()
print(f"Total logs: {summary['total_logs']}")
print(f"Errors: {summary['error_count']}")

# Get recent errors
recent_errors = analyzer.get_recent_errors(limit=5)
for error in recent_errors:
    print(f"{error['timestamp']} - {error['message']}")

# Search logs
results = parser.search_logs("database", limit=50)
print(f"Found {len(results)} matching logs")
```

## Log Format Support

LogLens automatically detects and parses common log formats:

```
[2024-01-15 10:30:45] [ERROR] [my_app.database] Connection timeout
[2024-01-15 10:30:46] [WARNING] [my_app.cache] Cache miss for key: user_123
[2024-01-15 10:30:47] [INFO] [my_app.api] GET /users/123 - 200
```

Custom format? LogLens accepts regex patterns for custom parsing.

## API Endpoints

When integrated with FastAPI or Flask, LogLens exposes these API endpoints:

### Dashboard
- `GET /loglens/` - Main dashboard

### API Endpoints
- `GET /loglens/api/logs?search=term&level=ERROR&limit=100` - Get filtered logs
- `GET /loglens/api/stats` - Get statistics and summary
- `GET /loglens/api/search?q=query` - Search logs
- `GET /loglens/api/files` - List available log files

## Configuration

### Log Directory Structure

LogLens expects logs in the following format:

```
logs/
  ├── log_file_2024-01-15.log
  ├── log_file_2024-01-14.log
  └── log_file_2024-01-13.log
```

This works perfectly with the standard Python logging configuration:

```python
import logging

handler = logging.FileHandler('logs/log_file_{}.log'.format(
    datetime.now().strftime('%Y-%m-%d')
))
```

### Custom Logger Configuration

```python
from loglens import LogParser

# Use custom log directory
parser = LogParser(log_dir="/var/log/myapp")

# Use custom regex pattern
custom_pattern = r'(?P<timestamp>.*?)\|(?P<level>\w+)\|(?P<message>.*)'
parser = LogParser(log_dir="logs", pattern=custom_pattern)
```

## Advanced Usage

### Filter Logs

```python
from loglens import LogAnalyzer

analyzer = LogAnalyzer(parser)

# Filter by level
errors = analyzer.filter_logs(level="ERROR", limit=50)

# Filter by logger
db_logs = analyzer.filter_logs(logger="database", limit=50)

# Search term
api_logs = analyzer.filter_logs(search_term="API", limit=50)
```

### Get Statistics

```python
# Log level distribution
level_stats = analyzer.get_level_statistics()
# Output: {'ERROR': 5, 'WARNING': 12, 'INFO': 234, 'DEBUG': 1000}

# Top loggers
top_loggers = analyzer.get_top_loggers(limit=10)
# Output: [('database', 450), ('api', 320), ('cache', 180), ...]

# Error frequency
error_freq = analyzer.get_error_frequency(hours=24)
# Output: {'2024-01-15 10:00': 3, '2024-01-15 11:00': 1, ...}
```

### Generate Visualizations

```python
from loglens.visualizers import ChartGenerator, TableGenerator

# Generate charts (returns JSON for Plotly)
level_chart = ChartGenerator.plotly_level_distribution(level_stats)
error_timeline = ChartGenerator.plotly_error_timeline(error_freq)
top_loggers_chart = ChartGenerator.plotly_top_loggers(top_loggers)

# Generate HTML tables
html_table = TableGenerator.logs_to_html_table(errors, title="Recent Errors")
```

## Performance Considerations

- **Large Log Files**: LogLens efficiently handles large log files
- **Real-time Parsing**: Use `limit` parameter to control parsing scope
- **Caching**: Implement caching for frequently accessed data in production

## Troubleshooting

### Logs Not Appearing

1. Check log directory exists: `logs/`
2. Verify log file naming: `log_file_YYYY-MM-DD.log`
3. Check file permissions
4. View server logs for parsing errors

### Dashboard Not Loading

1. Ensure FastAPI/Flask app is running
2. Check URL prefix configuration
3. Verify browser console for errors
4. Check server logs for issues

### Memory Issues with Large Logs

Use the `limit` parameter to control how many files are parsed:

```python
parser.get_log_files(limit=7)  # Only parse last 7 days
analyzer.get_log_summary()  # Uses limited logs
```

## Examples

See the [examples/](examples/) directory for complete working examples:

- `fastapi_example.py` - FastAPI integration with LogLens
- `flask_example.py` - Flask integration with LogLens
- `standalone_example.py` - Standalone usage without frameworks

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or suggestions, please open an issue on [GitHub](https://github.com/faisalahmedbijoy/loglens/issues).

---

Made with ❤️ for Python developers

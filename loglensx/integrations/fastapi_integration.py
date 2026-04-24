"""
FastAPI integration for loglensx viewer.
"""

from html import escape
from fastapi import FastAPI, APIRouter, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional

from ..core.parser import LogParser
from ..core.analyzer import LogAnalyzer
from ..visualizers.charts import ChartGenerator
from ..visualizers.tables import TableGenerator


BASE_STYLES = """
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Avenir Next', 'Segoe UI', sans-serif;
        color: #0f172a;
        background:
            radial-gradient(circle at top left, rgba(14, 165, 233, 0.16), transparent 30%),
            radial-gradient(circle at top right, rgba(251, 191, 36, 0.16), transparent 24%),
            linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
        min-height: 100vh;
    }
    .container { max-width: 1440px; margin: 0 auto; padding: 32px 20px 48px; }
    .header {
        padding: 28px;
        border-radius: 28px;
        color: white;
        background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 55%, #0ea5e9 100%);
        box-shadow: 0 24px 60px rgba(15, 23, 42, 0.28);
        margin-bottom: 22px;
    }
    .header h1 { font-size: 34px; margin-bottom: 6px; }
    .header p { max-width: 720px; opacity: 0.88; line-height: 1.55; }
    .nav { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 22px; }
    .nav a {
        text-decoration: none;
        padding: 11px 16px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.78);
        color: #0f172a;
        border: 1px solid rgba(148, 163, 184, 0.35);
        font-weight: 700;
    }
    .nav a:hover { background: #ffffff; }
    .panel {
        background: rgba(255, 255, 255, 0.82);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(226, 232, 240, 0.9);
        border-radius: 24px;
        padding: 22px;
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
    }
    .panel + .panel { margin-top: 22px; }
    .panel h2 { font-size: 20px; margin-bottom: 8px; }
    .panel p { color: #475569; }
    .filters {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 12px;
        align-items: end;
    }
    .filters label { display: block; font-size: 12px; font-weight: 700; color: #475569; margin-bottom: 6px; }
    .filters input, .filters select {
        width: 100%;
        padding: 12px 14px;
        border-radius: 14px;
        border: 1px solid #cbd5e1;
        background: #ffffff;
        color: #0f172a;
    }
    .filters button {
        padding: 12px 16px;
        border: none;
        border-radius: 14px;
        background: linear-gradient(135deg, #1d4ed8 0%, #0ea5e9 100%);
        color: white;
        font-weight: 700;
        cursor: pointer;
    }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; margin-bottom: 22px; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }
    .stat-card {
        background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 100%);
        color: white;
        padding: 18px;
        border-radius: 18px;
        text-align: center;
    }
    .stat-value { font-size: 24px; font-weight: 800; }
    .stat-label { font-size: 12px; margin-top: 5px; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.06em; }
    .card {
        background: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 24px;
        border: 1px solid rgba(226, 232, 240, 0.95);
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
    }
    .card h2 { font-size: 18px; margin-bottom: 15px; color: #0f172a; }
    .chart-container { height: 400px; }
    .hint { color: #64748b; font-size: 14px; margin-top: 12px; }
"""


def setup_fastapi_loglensx(app: FastAPI, log_dir: str = "logs", prefix: str = "/loglensx") -> None:
    """
    Setup loglensx routes in a FastAPI application.

    Args:
        app: FastAPI application instance
        log_dir: Directory containing log files
        prefix: URL prefix for loglensx routes
    """
    parser = LogParser(log_dir=log_dir)
    analyzer = LogAnalyzer(parser)
    router = APIRouter(prefix=prefix, tags=["loglensx"])

    # Dashboard HTML
    @router.get("/", response_class=HTMLResponse)
    def dashboard():
        """Main loglensx dashboard."""
        summary = analyzer.get_log_summary()
        level_stats = analyzer.get_level_statistics()
        top_loggers = analyzer.get_top_loggers(limit=5)
        recent_errors = analyzer.get_recent_errors(limit=5)

        level_chart = ChartGenerator.plotly_level_distribution(level_stats)
        error_timeline = ChartGenerator.plotly_error_timeline(analyzer.get_error_frequency())
        top_loggers_chart = ChartGenerator.plotly_top_loggers(top_loggers)

        errors_table = TableGenerator.logs_to_html_table(recent_errors, "Recent Errors", max_rows=5)
        stats_html = TableGenerator.statistics_to_html(summary)

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>loglensx - Log Viewer</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>{BASE_STYLES}</style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>loglensx Dashboard</h1>
                    <p>Interactive log monitoring with fast visual summaries and a proper browser for the raw entries behind them.</p>
                </div>

                <div class="nav">
                    <a href="{prefix}/">Dashboard</a>
                    <a href="{prefix}/logs?limit=100">View Logs</a>
                    <a href="{prefix}/api/stats">Statistics</a>
                </div>

                <form class="panel filters" action="{prefix}/logs" method="get">
                    <div>
                        <label for="search">Search</label>
                        <input id="search" name="search" placeholder="database, timeout, /api/users">
                    </div>
                    <div>
                        <label for="level">Level</label>
                        <select id="level" name="level">
                            <option value="">All levels</option>
                            <option value="ERROR">ERROR</option>
                            <option value="WARNING">WARNING</option>
                            <option value="INFO">INFO</option>
                            <option value="DEBUG">DEBUG</option>
                        </select>
                    </div>
                    <div>
                        <label for="limit">Rows</label>
                        <input id="limit" name="limit" type="number" min="10" max="500" value="100">
                    </div>
                    <button type="submit">Open Log Explorer</button>
                </form>

                {stats_html}

                <div class="grid">
                <div class="card">
                    <h2>Log Level Distribution</h2>
                    <div class="chart-container" id="levelChart"></div>
                </div>
                <div class="card">
                    <h2>Error Timeline</h2>
                    <div class="chart-container" id="errorChart"></div>
                </div>
                </div>

                <div class="card">
                    <h2>Top Loggers</h2>
                    <div class="chart-container" id="loggersChart"></div>
                    <p class="hint">Use the log explorer to filter by logger name and inspect the exact messages behind these counts.</p>
                </div>

                {errors_table}
            </div>

            <script>
                const levelChart = {level_chart};
                const errorChart = {error_timeline};
                const loggersChart = {top_loggers_chart};

                Plotly.newPlot('levelChart', levelChart.data, levelChart.layout, {{responsive: true}});
                Plotly.newPlot('errorChart', errorChart.data, errorChart.layout, {{responsive: true}});
                Plotly.newPlot('loggersChart', loggersChart.data, loggersChart.layout, {{responsive: true}});
            </script>
        </body>
        </html>
        """
        return html

    @router.get("/logs", response_class=HTMLResponse)
    def logs_page(
        search: Optional[str] = Query(None),
        level: Optional[str] = Query(None),
        logger: Optional[str] = Query(None),
        limit: int = Query(100, ge=1, le=1000)
    ):
        """Browsable log explorer page."""
        logs = analyzer.filter_logs(level=level, logger=logger, search_term=search, limit=limit)
        logs_table = TableGenerator.logs_to_html_table(logs, title="Log Explorer")

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>loglensx - Log Explorer</title>
            <style>{BASE_STYLES}</style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Log Explorer</h1>
                    <p>Filter noisy log streams down to the slice you actually need, then open long messages inline without leaving the page.</p>
                </div>

                <div class="nav">
                    <a href="{prefix}/">Dashboard</a>
                    <a href="{prefix}/logs?limit=100">View Logs</a>
                    <a href="{prefix}/api/logs?limit=100">JSON API</a>
                </div>

                <form class="panel filters" method="get" action="{prefix}/logs">
                    <div>
                        <label for="search">Search</label>
                        <input id="search" name="search" value="{escape(search or '')}" placeholder="error message or route">
                    </div>
                    <div>
                        <label for="level">Level</label>
                        <select id="level" name="level">
                            <option value="" {"selected" if not level else ""}>All levels</option>
                            <option value="ERROR" {"selected" if level == "ERROR" else ""}>ERROR</option>
                            <option value="WARNING" {"selected" if level == "WARNING" else ""}>WARNING</option>
                            <option value="INFO" {"selected" if level == "INFO" else ""}>INFO</option>
                            <option value="DEBUG" {"selected" if level == "DEBUG" else ""}>DEBUG</option>
                        </select>
                    </div>
                    <div>
                        <label for="logger">Logger</label>
                        <input id="logger" name="logger" value="{escape(logger or '')}" placeholder="app.api or worker">
                    </div>
                    <div>
                        <label for="limit">Rows</label>
                        <input id="limit" name="limit" type="number" min="10" max="1000" value="{limit}">
                    </div>
                    <button type="submit">Apply Filters</button>
                </form>

                <div class="panel">
                    <h2>Current Slice</h2>
                    <p>Showing up to {limit} entries from <code>{escape(log_dir)}</code> with the current search and level filters.</p>
                </div>

                {logs_table}
            </div>
        </body>
        </html>
        """
        return html

    # API endpoints
    @router.get("/api/logs", response_class=JSONResponse)
    def get_logs(
        search: Optional[str] = Query(None),
        level: Optional[str] = Query(None),
        logger: Optional[str] = Query(None),
        limit: int = Query(100, ge=1, le=1000)
    ):
        """Get logs with optional filters."""
        try:
            logs = analyzer.filter_logs(
                level=level,
                logger=logger,
                search_term=search,
                limit=limit
            )
            return {"status": "success", "count": len(logs), "logs": logs}
        except ValueError as e:
            return JSONResponse(status_code=400, content={"status": "error", "detail": str(e)})
        except Exception as e:
            return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})

    @router.get("/api/stats", response_class=JSONResponse)
    def get_stats():
        """Get log statistics."""
        try:
            summary = analyzer.get_log_summary()
            level_stats = analyzer.get_level_statistics()
            top_loggers = analyzer.get_top_loggers(limit=10)
            error_freq = analyzer.get_error_frequency()

            return {
                "status": "success",
                "summary": summary,
                "level_stats": level_stats,
                "top_loggers": top_loggers,
                "error_frequency": error_freq,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/api/search", response_class=JSONResponse)
    def search_logs(query: str = Query(..., min_length=1)):
        """Search logs by query."""
        try:
            results = parser.search_logs(query, limit=100)
            return {"status": "success", "count": len(results), "results": results}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/api/files", response_class=JSONResponse)
    def get_log_files():
        """Get available log files."""
        try:
            files = parser.get_log_files()
            file_info = [
                {
                    "name": f.name,
                    "size": f.stat().st_size,
                    "modified": f.stat().st_mtime,
                }
                for f in files
            ]
            return {"status": "success", "files": file_info}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    app.include_router(router)

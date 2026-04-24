"""
FastAPI integration for loglensx viewer with enhanced professional dashboard.
"""

from html import escape
from fastapi import FastAPI, APIRouter, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional

from ..core.parser import LogParser
from ..core.analyzer import LogAnalyzer
from ..visualizers.charts import ChartGenerator
from ..visualizers.tables import TableGenerator


ENHANCED_STYLES = """
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto Mono', sans-serif;
        color: #1a202c;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    .container { max-width: 1600px; margin: 0 auto; padding: 40px 24px; }
    .header {
        padding: 40px;
        border-radius: 20px;
        color: white;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.25);
        margin-bottom: 40px;
        position: relative;
        overflow: hidden;
    }
    .header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        animation: float 3s ease-in-out infinite;
    }
    @keyframes float { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(20px); } }
    .header h1 { font-size: 40px; font-weight: 700; margin-bottom: 10px; position: relative; z-index: 1; }
    .header p { font-size: 16px; opacity: 0.9; max-width: 600px; line-height: 1.6; position: relative; z-index: 1; }
    .nav { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 30px; }
    .nav a {
        text-decoration: none;
        padding: 12px 24px;
        border-radius: 10px;
        background: white;
        color: #667eea;
        border: 2px solid #667eea;
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .nav a:hover { background: #667eea; color: white; transform: translateY(-2px); }
    .panel {
        background: white;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 0, 0, 0.08);
        border-radius: 16px;
        padding: 28px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
        margin-bottom: 30px;
    }
    .filters {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        align-items: end;
    }
    .filters label { display: block; font-size: 13px; font-weight: 600; color: #4a5568; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }
    .filters input, .filters select {
        width: 100%;
        padding: 12px 14px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        background: white;
        color: #1a202c;
        font-size: 14px;
        transition: border-color 0.3s;
    }
    .filters input:focus, .filters select:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); }
    .filters button {
        padding: 12px 24px;
        border: none;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    .filters button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4); }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 24px; margin-bottom: 30px; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px; margin: 30px 0; }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 24px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
        transition: all 0.3s;
        position: relative;
        overflow: hidden;
    }
    .stat-card::before { content: ''; position: absolute; top: -50%; right: -20%; width: 150px; height: 150px; background: rgba(255, 255, 255, 0.1); border-radius: 50%; }
    .stat-card:hover { transform: translateY(-5px); box-shadow: 0 15px 40px rgba(102, 126, 234, 0.3); }
    .stat-value { font-size: 32px; font-weight: 800; position: relative; z-index: 1; }
    .stat-label { font-size: 12px; margin-top: 8px; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.8px; position: relative; z-index: 1; }
    .card {
        background: white;
        padding: 28px;
        border-radius: 16px;
        border: 1px solid rgba(0, 0, 0, 0.08);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
    }
    .card h2 { font-size: 20px; font-weight: 700; margin-bottom: 20px; color: #1a202c; display: flex; align-items: center; gap: 10px; }
    .card h2::before { content: ''; width: 4px; height: 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 2px; }
    .chart-container { min-height: 450px; width: 100%; }
    .hint { color: #718096; font-size: 14px; margin-top: 16px; padding: 12px; background: #f7fafc; border-left: 3px solid #667eea; border-radius: 4px; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    thead { background: #f7fafc; }
    th { padding: 14px 16px; text-align: left; font-weight: 600; color: #4a5568; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #e2e8f0; }
    td { padding: 14px 16px; border-bottom: 1px solid #e2e8f0; font-size: 14px; }
    tbody tr:hover { background: #f7fafc; }
    tbody tr:last-child td { border-bottom: none; }
    code { background: #f7fafc; padding: 2px 6px; border-radius: 4px; font-family: 'Monaco', monospace; color: #764ba2; }
"""


def setup_fastapi_loglensx(app: FastAPI, log_dir: str = "logs", prefix: str = "/loglensx") -> None:
    """
    Setup loglensx routes in a FastAPI application with enhanced dashboard.

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
        """Main loglensx dashboard with enhanced professional design."""
        summary = analyzer.get_log_summary()
        level_stats = analyzer.get_level_statistics()
        top_loggers = analyzer.get_top_loggers(limit=10)
        recent_errors = analyzer.get_recent_errors(limit=10)

        level_chart = ChartGenerator.plotly_level_distribution(level_stats)
        error_timeline = ChartGenerator.plotly_error_timeline(analyzer.get_error_frequency())
        top_loggers_chart = ChartGenerator.plotly_top_loggers(top_loggers)

        errors_table = TableGenerator.logs_to_html_table(recent_errors, "Recent Errors", max_rows=10)
        
        # Build stats HTML
        stats_html = '<div class="stats-grid">'
        for key, value in summary.items():
            key_display = key.replace('_', ' ').title()
            stats_html += f'<div class="stat-card"><div class="stat-value">{value}</div><div class="stat-label">{key_display}</div></div>'
        stats_html += '</div>'

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>loglensx - Professional Log Viewer Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>{ENHANCED_STYLES}</style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 loglensx Dashboard</h1>
                    <p>Advanced log monitoring and analysis platform with interactive visualizations and comprehensive insights</p>
                </div>

                <div class="nav">
                    <a href="{prefix}/">Dashboard</a>
                    <a href="{prefix}/logs?limit=100">View Logs</a>
                    <a href="{prefix}/api/stats">Statistics API</a>
                </div>

                <form class="panel filters" action="{prefix}/logs" method="get">
                    <div>
                        <label for="search">Search</label>
                        <input id="search" name="search" placeholder="error, timeout, database...">
                    </div>
                    <div>
                        <label for="level">Log Level</label>
                        <select id="level" name="level">
                            <option value="">All Levels</option>
                            <option value="ERROR">🔴 ERROR</option>
                            <option value="WARNING">🟡 WARNING</option>
                            <option value="INFO">🔵 INFO</option>
                            <option value="DEBUG">⚪ DEBUG</option>
                        </select>
                    </div>
                    <div>
                        <label for="limit">Results</label>
                        <input id="limit" name="limit" type="number" min="10" max="500" value="100">
                    </div>
                    <button type="submit">🔍 Search Logs</button>
                </form>

                {stats_html}

                <div class="grid">
                    <div class="card">
                        <h2>Log Level Distribution</h2>
                        <div class="chart-container" id="levelChart"></div>
                    </div>
                    <div class="card">
                        <h2>Error Frequency Timeline</h2>
                        <div class="chart-container" id="errorChart"></div>
                    </div>
                </div>

                <div class="card">
                    <h2>Top Loggers</h2>
                    <div class="chart-container" id="loggersChart"></div>
                    <p class="hint">📋 Shows the most active loggers. Click on bars to explore individual logger messages.</p>
                </div>

                {errors_table}
            </div>

            <script>
                const levelChart = {level_chart};
                const errorChart = {error_timeline};
                const loggersChart = {top_loggers_chart};

                const plotConfig = {{ responsive: true, displayModeBar: true, displaylogo: false }};
                
                Plotly.newPlot('levelChart', levelChart.data, levelChart.layout, plotConfig);
                Plotly.newPlot('errorChart', errorChart.data, errorChart.layout, plotConfig);
                Plotly.newPlot('loggersChart', loggersChart.data, loggersChart.layout, plotConfig);
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
        """Browsable log explorer page with advanced filtering."""
        logs = analyzer.filter_logs(level=level, logger=logger, search_term=search, limit=limit)
        logs_table = TableGenerator.logs_to_html_table(logs, title="Log Explorer", max_rows=limit)

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>loglensx - Log Explorer</title>
            <style>{ENHANCED_STYLES}</style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔍 Log Explorer</h1>
                    <p>Advanced filtering and inspection of log entries with powerful search capabilities</p>
                </div>

                <div class="nav">
                    <a href="{prefix}/">Dashboard</a>
                    <a href="{prefix}/logs?limit=100">View Logs</a>
                    <a href="{prefix}/api/logs?limit=100">JSON API</a>
                </div>

                <form class="panel filters" method="get" action="{prefix}/logs">
                    <div>
                        <label for="search">Search Query</label>
                        <input id="search" name="search" value="{escape(search or '')}" placeholder="error message or route pattern">
                    </div>
                    <div>
                        <label for="level">Log Level</label>
                        <select id="level" name="level">
                            <option value="" {"selected" if not level else ""}>All Levels</option>
                            <option value="ERROR" {"selected" if level == "ERROR" else ""}>🔴 ERROR</option>
                            <option value="WARNING" {"selected" if level == "WARNING" else ""}>🟡 WARNING</option>
                            <option value="INFO" {"selected" if level == "INFO" else ""}>🔵 INFO</option>
                            <option value="DEBUG" {"selected" if level == "DEBUG" else ""}>⚪ DEBUG</option>
                        </select>
                    </div>
                    <div>
                        <label for="logger">Logger Name</label>
                        <input id="logger" name="logger" value="{escape(logger or '')}" placeholder="app.api or worker">
                    </div>
                    <div>
                        <label for="limit">Rows Per Page</label>
                        <input id="limit" name="limit" type="number" min="10" max="1000" value="{limit}">
                    </div>
                    <button type="submit">🔍 Apply Filters</button>
                </form>

                <div class="panel">
                    <h2>Current Search Results</h2>
                    <p>Displaying <strong>{len(logs)}</strong> entries from <code>{escape(log_dir)}</code> with applied filters</p>
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
        """Get logs with optional filters in JSON format."""
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
        """Get comprehensive log statistics."""
        try:
            summary = analyzer.get_log_summary()
            level_stats = analyzer.get_level_statistics()
            top_loggers = analyzer.get_top_loggers(limit=15)
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
        """Search logs by query string."""
        try:
            results = parser.search_logs(query, limit=100)
            return {"status": "success", "count": len(results), "results": results}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/api/files", response_class=JSONResponse)
    def get_log_files():
        """Get available log files metadata."""
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

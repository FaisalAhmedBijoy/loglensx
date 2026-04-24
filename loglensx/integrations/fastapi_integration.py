"""
FastAPI integration for loglensx viewer.
"""

from fastapi import FastAPI, APIRouter, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional

from ..core.parser import LogParser
from ..core.analyzer import LogAnalyzer
from ..visualizers.charts import ChartGenerator
from ..visualizers.tables import TableGenerator


def setup_fastapi_loglensx(app: FastAPI, log_dir: str = "logs", prefix: str = "/loglens") -> None:
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
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
                .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; }}
                .header h1 {{ font-size: 32px; margin-bottom: 5px; }}
                .header p {{ opacity: 0.9; }}
                .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .card h2 {{ font-size: 18px; margin-bottom: 15px; color: #333; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px; }}
                .chart-container {{ height: 400px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #eee; }}
                th {{ background: #f8f9fa; font-weight: 600; }}
                tr:hover {{ background: #fafafa; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 20px; }}
                .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
                .stat-value {{ font-size: 24px; font-weight: bold; }}
                .stat-label {{ font-size: 12px; margin-top: 5px; opacity: 0.9; }}
                .search-box {{ margin-bottom: 20px; }}
                .search-box input, .search-box select {{ padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-right: 10px; }}
                .search-box button {{ padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; }}
                .search-box button:hover {{ background: #764ba2; }}
                .nav {{ margin-bottom: 20px; }}
                .nav a {{ display: inline-block; padding: 10px 15px; background: white; color: #667eea; text-decoration: none; border-radius: 4px; margin-right: 10px; border: 2px solid #667eea; }}
                .nav a:hover {{ background: #667eea; color: white; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 loglensx Dashboard</h1>
                    <p>Interactive Log Viewer & Analyzer</p>
                </div>

                <div class="nav">
                    <a href="{prefix}/">Dashboard</a>
                    <a href="{prefix}/api/logs?limit=100">View Logs</a>
                    <a href="{prefix}/api/search">Search</a>
                    <a href="{prefix}/api/stats">Statistics</a>
                </div>

                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="Search logs...">
                    <select id="levelFilter">
                        <option value="">All Levels</option>
                        <option value="ERROR">ERROR</option>
                        <option value="WARNING">WARNING</option>
                        <option value="INFO">INFO</option>
                        <option value="DEBUG">DEBUG</option>
                    </select>
                    <button onclick="searchLogs()">Search</button>
                </div>

                {stats_html}

                <div class="grid">
                    <div class="card">
                        <h2>📈 Log Level Distribution</h2>
                        <div class="chart-container" id="levelChart"></div>
                    </div>
                    <div class="card">
                        <h2>⏱️ Error Timeline</h2>
                        <div class="chart-container" id="errorChart"></div>
                    </div>
                </div>

                <div class="card">
                    <h2>🔝 Top Loggers</h2>
                    <div class="chart-container" id="loggersChart"></div>
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

                function searchLogs() {{
                    const query = document.getElementById('searchInput').value;
                    const level = document.getElementById('levelFilter').value;
                    const url = `{prefix}/api/logs?search=${{query}}&level=${{level}}`;
                    window.location.href = url;
                }}
            </script>
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

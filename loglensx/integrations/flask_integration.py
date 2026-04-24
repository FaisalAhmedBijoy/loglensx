"""
Flask integration for loglensx viewer.
"""

from flask import Flask, Blueprint, render_template_string, jsonify, request
from typing import Optional

from ..core.parser import LogParser
from ..core.analyzer import LogAnalyzer
from ..visualizers.charts import ChartGenerator
from ..visualizers.tables import TableGenerator


def setup_flask_loglensx(app: Flask, log_dir: str = "logs", prefix: str = "/loglens") -> None:
    """
    Setup loglensx routes in a Flask application.

    Args:
        app: Flask application instance
        log_dir: Directory containing log files
        prefix: URL prefix for loglensx routes
    """
    blueprint = Blueprint("loglensx", __name__, url_prefix=prefix)
    parser = LogParser(log_dir=log_dir)
    analyzer = LogAnalyzer(parser)

    # Dashboard HTML template
    dashboard_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>loglensx - Log Viewer</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
            .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; }
            .header h1 { font-size: 32px; margin-bottom: 5px; }
            .header p { opacity: 0.9; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .card h2 { font-size: 18px; margin-bottom: 15px; color: #333; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px; }
            .chart-container { height: 400px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #eee; }
            th { background: #f8f9fa; font-weight: 600; }
            tr:hover { background: #fafafa; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 20px; }
            .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }
            .stat-value { font-size: 24px; font-weight: bold; }
            .stat-label { font-size: 12px; margin-top: 5px; opacity: 0.9; }
            .search-box { margin-bottom: 20px; }
            .search-box input, .search-box select { padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-right: 10px; }
            .search-box button { padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; }
            .search-box button:hover { background: #764ba2; }
            .nav { margin-bottom: 20px; }
            .nav a { display: inline-block; padding: 10px 15px; background: white; color: #667eea; text-decoration: none; border-radius: 4px; margin-right: 10px; border: 2px solid #667eea; }
            .nav a:hover { background: #667eea; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 loglensx Dashboard</h1>
                <p>Interactive Log Viewer & Analyzer</p>
            </div>

            <div class="nav">
                <a href="{{ url_for('loglensx.dashboard') }}">Dashboard</a>
                <a href="{{ url_for('loglensx.get_logs') }}">View Logs</a>
                <a href="{{ url_for('loglensx.api_stats') }}">Statistics</a>
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

            <div class="stats-grid" id="statsGrid"></div>

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

            <div class="card" id="errorsTable"></div>
        </div>

        <script>
            fetch('{{ url_for("loglensx.api_stats") }}')
                .then(r => r.json())
                .then(data => {
                    const stats = data.summary;
                    let html = '';
                    for (const [key, value] of Object.entries(stats)) {
                        html += `
                            <div class="stat-card">
                                <div class="stat-value">${value}</div>
                                <div class="stat-label">${key}</div>
                            </div>
                        `;
                    }
                    document.getElementById('statsGrid').innerHTML = html;

                    // Plot charts
                    const levelStats = data.level_stats;
                    const topLoggers = data.top_loggers;

                    const levelChart = {
                        data: [{
                            labels: Object.keys(levelStats),
                            values: Object.values(levelStats),
                            type: 'pie'
                        }],
                        layout: { title: 'Log Level Distribution' }
                    };
                    Plotly.newPlot('levelChart', levelChart.data, levelChart.layout, {responsive: true});

                    const loggersChart = {
                        data: [{
                            x: topLoggers.map(l => l[1]),
                            y: topLoggers.map(l => l[0]),
                            type: 'bar',
                            orientation: 'h'
                        }],
                        layout: { title: 'Top Loggers', height: 400 }
                    };
                    Plotly.newPlot('loggersChart', loggersChart.data, loggersChart.layout, {responsive: true});
                });

            function searchLogs() {
                const query = document.getElementById('searchInput').value;
                const level = document.getElementById('levelFilter').value;
                window.location.search = `?search=${query}&level=${level}`;
            }
        </script>
    </body>
    </html>
    """

    @blueprint.route("/")
    def dashboard():
        """Main loglensx dashboard."""
        return render_template_string(dashboard_template)

    @blueprint.route("/api/logs")
    def get_logs():
        """Get logs with optional filters."""
        try:
            search = request.args.get("search")
            level = request.args.get("level")
            logger = request.args.get("logger")
            limit = request.args.get("limit", 100, type=int)

            logs = analyzer.filter_logs(
                level=level or None,
                logger=logger or None,
                search_term=search or None,
                limit=limit
            )
            return jsonify({"status": "success", "count": len(logs), "logs": logs})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @blueprint.route("/api/stats")
    def api_stats():
        """Get log statistics."""
        try:
            summary = analyzer.get_log_summary()
            level_stats = analyzer.get_level_statistics()
            top_loggers = analyzer.get_top_loggers(limit=10)
            error_freq = analyzer.get_error_frequency()

            return jsonify({
                "status": "success",
                "summary": summary,
                "level_stats": level_stats,
                "top_loggers": top_loggers,
                "error_frequency": error_freq,
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @blueprint.route("/api/search")
    def search():
        """Search logs by query."""
        try:
            query = request.args.get("q", "")
            if not query:
                return jsonify({"status": "error", "message": "Query parameter required"}), 400

            results = parser.search_logs(query, limit=100)
            return jsonify({"status": "success", "count": len(results), "results": results})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    app.register_blueprint(blueprint)

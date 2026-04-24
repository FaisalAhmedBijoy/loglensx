"""
Flask integration for loglensx viewer.
"""

from html import escape
from flask import Flask, Blueprint, render_template_string, jsonify, request
from ..visualizers.tables import TableGenerator
from ..core.parser import LogParser
from ..core.analyzer import LogAnalyzer


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


def setup_flask_loglensx(app: Flask, log_dir: str = "logs", prefix: str = "/loglensx") -> None:
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
        <style>{{ base_styles }}</style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>loglensx Dashboard</h1>
                <p>Interactive log monitoring with fast visual summaries and a proper browser for the raw entries behind them.</p>
            </div>

            <div class="nav">
                <a href="{{ url_for('loglensx.dashboard') }}">Dashboard</a>
                <a href="{{ url_for('loglensx.logs_page') }}">View Logs</a>
                <a href="{{ url_for('loglensx.api_stats') }}">Statistics</a>
            </div>

            <form class="panel filters" action="{{ url_for('loglensx.logs_page') }}" method="get">
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

            <div class="stats-grid" id="statsGrid"></div>

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
                    const errorFrequency = data.error_frequency;

                    const levelChart = {
                        data: [{
                            labels: Object.keys(levelStats),
                            values: Object.values(levelStats),
                            type: 'pie'
                        }],
                        layout: { title: 'Log Level Distribution' }
                    };
                    Plotly.newPlot('levelChart', levelChart.data, levelChart.layout, {responsive: true});

                    const errorChart = {
                        data: [{
                            x: Object.keys(errorFrequency),
                            y: Object.values(errorFrequency),
                            type: 'scatter',
                            mode: 'lines+markers',
                            line: { color: '#dc2626' }
                        }],
                        layout: { title: 'Error Frequency', height: 400 }
                    };
                    Plotly.newPlot('errorChart', errorChart.data, errorChart.layout, {responsive: true});

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
        </script>
    </body>
    </html>
    """

    logs_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>loglensx - Log Explorer</title>
        <style>{{ base_styles }}</style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Log Explorer</h1>
                <p>Filter noisy log streams down to the slice you actually need, then open long messages inline without leaving the page.</p>
            </div>

            <div class="nav">
                <a href="{{ url_for('loglensx.dashboard') }}">Dashboard</a>
                <a href="{{ url_for('loglensx.logs_page') }}">View Logs</a>
                <a href="{{ url_for('loglensx.get_logs', limit=limit) }}">JSON API</a>
            </div>

            <form class="panel filters" action="{{ url_for('loglensx.logs_page') }}" method="get">
                <div>
                    <label for="search">Search</label>
                    <input id="search" name="search" value="{{ search }}" placeholder="error message or route">
                </div>
                <div>
                    <label for="level">Level</label>
                    <select id="level" name="level">
                        <option value="" {% if not level %}selected{% endif %}>All levels</option>
                        <option value="ERROR" {% if level == 'ERROR' %}selected{% endif %}>ERROR</option>
                        <option value="WARNING" {% if level == 'WARNING' %}selected{% endif %}>WARNING</option>
                        <option value="INFO" {% if level == 'INFO' %}selected{% endif %}>INFO</option>
                        <option value="DEBUG" {% if level == 'DEBUG' %}selected{% endif %}>DEBUG</option>
                    </select>
                </div>
                <div>
                    <label for="logger">Logger</label>
                    <input id="logger" name="logger" value="{{ logger }}" placeholder="app.api or worker">
                </div>
                <div>
                    <label for="limit">Rows</label>
                    <input id="limit" name="limit" type="number" min="10" max="1000" value="{{ limit }}">
                </div>
                <button type="submit">Apply Filters</button>
            </form>

            <div class="panel">
                <h2>Current Slice</h2>
                <p>Showing up to {{ limit }} entries from <code>{{ log_dir }}</code> with the current search and level filters.</p>
            </div>

            {{ logs_table|safe }}
        </div>
    </body>
    </html>
    """

    @blueprint.route("/")
    def dashboard():
        """Main loglensx dashboard."""
        return render_template_string(dashboard_template, base_styles=BASE_STYLES)

    @blueprint.route("/logs")
    def logs_page():
        """Browsable log explorer page."""
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

        return render_template_string(
            logs_template,
            base_styles=BASE_STYLES,
            search=escape(search or ""),
            level=level or "",
            logger=escape(logger or ""),
            limit=limit,
            log_dir=escape(log_dir),
            logs_table=TableGenerator.logs_to_html_table(logs, title="Log Explorer"),
        )

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

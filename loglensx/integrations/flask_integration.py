"""
Flask integration for loglensx viewer with enhanced professional dashboard.
"""

from html import escape
from flask import Flask, Blueprint, render_template_string, jsonify, request
from typing import Optional

from ..core.parser import LogParser
from ..core.analyzer import LogAnalyzer
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


def setup_flask_loglensx(app: Flask, log_dir: str = "logs", prefix: str = "/loglensx") -> None:
    """
    Setup loglensx routes in a Flask application with enhanced dashboard.

    Args:
        app: Flask application instance
        log_dir: Directory containing log files
        prefix: URL prefix for loglensx routes
    """
    blueprint = Blueprint("loglensx", __name__, url_prefix=prefix)
    parser = LogParser(log_dir=log_dir)
    analyzer = LogAnalyzer(parser)

    # Dashboard template
    dashboard_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>loglensx - Professional Log Viewer Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>{{ enhanced_styles }}</style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 loglensx Dashboard</h1>
                <p>Advanced log monitoring and analysis platform with interactive visualizations and comprehensive insights</p>
            </div>

            <div class="nav">
                <a href="{{ url_for('loglensx.dashboard') }}">Dashboard</a>
                <a href="{{ url_for('loglensx.logs_page') }}">View Logs</a>
                <a href="{{ url_for('loglensx.api_stats') }}">Statistics API</a>
            </div>

            <form class="panel filters" action="{{ url_for('loglensx.logs_page') }}" method="get">
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

            <div class="stats-grid" id="statsGrid"></div>

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
        </div>

        <script>
            fetch('{{ url_for("loglensx.api_stats") }}')
                .then(r => r.json())
                .then(data => {
                    const stats = data.summary;
                    let html = '';
                    for (const [key, value] of Object.entries(stats)) {
                        const keyDisplay = key.replace(/_/g, ' ').toUpperCase().split(' ').join(' ');
                        html += `
                            <div class="stat-card">
                                <div class="stat-value">${value}</div>
                                <div class="stat-label">${keyDisplay}</div>
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
                            type: 'pie',
                            marker: { colors: ['#ef4444', '#f59e0b', '#3b82f6', '#6b7280'] }
                        }],
                        layout: { title: 'Log Level Distribution', height: 450 }
                    };
                    Plotly.newPlot('levelChart', levelChart.data, levelChart.layout, {responsive: true, displayModeBar: true, displaylogo: false});

                    const errorChart = {
                        data: [{
                            x: Object.keys(errorFrequency),
                            y: Object.values(errorFrequency),
                            type: 'scatter',
                            mode: 'lines+markers',
                            line: { color: '#ef4444', width: 3 },
                            marker: { size: 8 }
                        }],
                        layout: { title: 'Error Frequency Timeline', height: 450, xaxis: { title: 'Time' }, yaxis: { title: 'Count' } }
                    };
                    Plotly.newPlot('errorChart', errorChart.data, errorChart.layout, {responsive: true, displayModeBar: true, displaylogo: false});

                    const loggersChart = {
                        data: [{
                            x: topLoggers.map(l => l[1]),
                            y: topLoggers.map(l => l[0]),
                            type: 'bar',
                            orientation: 'h',
                            marker: { color: '#667eea' }
                        }],
                        layout: { title: 'Top Loggers by Message Count', height: 450, xaxis: { title: 'Message Count' } }
                    };
                    Plotly.newPlot('loggersChart', loggersChart.data, loggersChart.layout, {responsive: true, displayModeBar: true, displaylogo: false});
                });
        </script>
    </body>
    </html>
    """

    # Logs page template
    logs_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>loglensx - Log Explorer</title>
        <style>{{ enhanced_styles }}</style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔍 Log Explorer</h1>
                <p>Advanced filtering and inspection of log entries with powerful search capabilities</p>
            </div>

            <div class="nav">
                <a href="{{ url_for('loglensx.dashboard') }}">Dashboard</a>
                <a href="{{ url_for('loglensx.logs_page') }}">View Logs</a>
                <a href="{{ url_for('loglensx.get_logs') }}">JSON API</a>
            </div>

            <form class="panel filters" action="{{ url_for('loglensx.logs_page') }}" method="get">
                <div>
                    <label for="search">Search Query</label>
                    <input id="search" name="search" value="{{ search }}" placeholder="error message or route pattern">
                </div>
                <div>
                    <label for="level">Log Level</label>
                    <select id="level" name="level">
                        <option value="" {% if not level %}selected{% endif %}>All Levels</option>
                        <option value="ERROR" {% if level == 'ERROR' %}selected{% endif %}>🔴 ERROR</option>
                        <option value="WARNING" {% if level == 'WARNING' %}selected{% endif %}>🟡 WARNING</option>
                        <option value="INFO" {% if level == 'INFO' %}selected{% endif %}>🔵 INFO</option>
                        <option value="DEBUG" {% if level == 'DEBUG' %}selected{% endif %}>⚪ DEBUG</option>
                    </select>
                </div>
                <div>
                    <label for="logger">Logger Name</label>
                    <input id="logger" name="logger" value="{{ logger }}" placeholder="app.api or worker">
                </div>
                <div>
                    <label for="limit">Rows Per Page</label>
                    <input id="limit" name="limit" type="number" min="10" max="1000" value="{{ limit }}">
                </div>
                <button type="submit">🔍 Apply Filters</button>
            </form>

            <div class="panel">
                <h2>Current Search Results</h2>
                <p>Displaying <strong>{{ log_count }}</strong> entries from <code>{{ log_dir }}</code> with applied filters</p>
            </div>

            {{ logs_table|safe }}
        </div>
    </body>
    </html>
    """

    @blueprint.route("/")
    def dashboard():
        """Main dashboard with statistics and charts."""
        return render_template_string(dashboard_template, enhanced_styles=ENHANCED_STYLES)

    @blueprint.route("/logs")
    def logs_page():
        """Browsable log explorer page."""
        search = request.args.get("search")
        level = request.args.get("level")
        logger_name = request.args.get("logger")
        limit = request.args.get("limit", 100, type=int)

        logs = analyzer.filter_logs(
            level=level or None,
            logger=logger_name or None,
            search_term=search or None,
            limit=limit
        )

        logs_table = TableGenerator.logs_to_html_table(logs, title="Log Explorer", max_rows=limit)

        return render_template_string(
            logs_template,
            enhanced_styles=ENHANCED_STYLES,
            search=escape(search or ""),
            level=level or "",
            logger=escape(logger_name or ""),
            limit=limit,
            log_dir=escape(log_dir),
            log_count=len(logs),
            logs_table=logs_table,
        )

    @blueprint.route("/api/logs")
    def get_logs():
        """Get logs as JSON with optional filters."""
        try:
            search = request.args.get("search")
            level = request.args.get("level")
            logger_name = request.args.get("logger")
            limit = request.args.get("limit", 100, type=int)

            logs = analyzer.filter_logs(
                level=level or None,
                logger=logger_name or None,
                search_term=search or None,
                limit=limit
            )
            return jsonify({"status": "success", "count": len(logs), "logs": logs})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @blueprint.route("/api/stats")
    def api_stats():
        """Get comprehensive log statistics as JSON."""
        try:
            summary = analyzer.get_log_summary()
            level_stats = analyzer.get_level_statistics()
            top_loggers = analyzer.get_top_loggers(limit=15)
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

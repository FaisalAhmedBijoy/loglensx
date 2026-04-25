"""
Flask integration for the loglensx dashboard.
"""

from flask import Blueprint, Flask, Response, jsonify, request, url_for

from ..core.analyzer import LogAnalyzer
from ..core.exporter import LogExporter
from ..core.parser import LogParser
from ._dashboard import (
    DASHBOARD_STYLES as ENHANCED_STYLES,
    render_dashboard_page,
    render_logs_page,
)


__all__ = ["ENHANCED_STYLES", "setup_flask_loglensx"]


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

    def route_links():
        """Build request-aware links for the dashboard templates."""
        return {
            "dashboard": url_for("loglensx.dashboard"),
            "logs": url_for("loglensx.logs_page", limit=100),
            "logs_base": url_for("loglensx.logs_page"),
            "api_stats": url_for("loglensx.api_stats"),
            "api_logs": url_for("loglensx.get_logs", limit=100),
            "api_export": url_for("loglensx.api_export", format="csv", limit=1000),
            "api_files": url_for("loglensx.api_files"),
        }

    def request_limit(default: int = 100) -> int:
        """Read and clamp the requested row limit."""
        limit = request.args.get("limit", default, type=int) or default
        return max(1, min(limit, 1000))

    def request_filters():
        """Read shared log filters from query parameters."""
        return {
            "search": request.args.get("search"),
            "level": request.args.get("level"),
            "logger_name": request.args.get("logger"),
            "source_file": request.args.get("file"),
            "since": request.args.get("since"),
            "until": request.args.get("until"),
        }

    def filtered_logs(limit: int):
        """Apply request filters through the analyzer."""
        filters = request_filters()
        return analyzer.filter_logs(
            level=filters["level"] or None,
            logger=filters["logger_name"] or None,
            search_term=filters["search"] or None,
            source_file=filters["source_file"] or None,
            since=filters["since"] or None,
            until=filters["until"] or None,
            limit=limit,
        )

    @blueprint.route("/")
    def dashboard():
        """Main loglensx dashboard with interactive charts and tables."""
        summary = analyzer.get_log_summary()
        level_stats = analyzer.get_level_statistics()
        top_loggers = analyzer.get_top_loggers(limit=12)
        recent_errors = analyzer.get_recent_errors(limit=10)
        error_frequency = analyzer.get_error_frequency()

        return render_dashboard_page(
            links=route_links(),
            summary=summary,
            level_stats=level_stats,
            top_loggers=top_loggers,
            error_frequency=error_frequency,
            recent_errors=recent_errors,
            log_dir=log_dir,
        )

    @blueprint.route("/logs")
    def logs_page():
        """Browsable log explorer page."""
        filters = request_filters()
        limit = request_limit()
        logs = filtered_logs(limit)

        return render_logs_page(
            links=route_links(),
            logs=logs,
            log_dir=log_dir,
            search=filters["search"],
            level=filters["level"],
            logger=filters["logger_name"],
            source_file=filters["source_file"],
            since=filters["since"],
            until=filters["until"],
            limit=limit,
        )

    @blueprint.route("/api/logs")
    def get_logs():
        """Get logs as JSON with optional filters."""
        try:
            limit = request_limit()
            logs = filtered_logs(limit)
            return jsonify({"status": "success", "count": len(logs), "logs": logs})
        except Exception as exc:
            return jsonify({"status": "error", "message": str(exc)}), 500

    @blueprint.route("/api/stats")
    def api_stats():
        """Get comprehensive log statistics as JSON."""
        try:
            return jsonify(
                {
                    "status": "success",
                    "summary": analyzer.get_log_summary(),
                    "level_stats": analyzer.get_level_statistics(),
                    "top_loggers": analyzer.get_top_loggers(limit=15),
                    "error_frequency": analyzer.get_error_frequency(),
                    "error_patterns": analyzer.get_error_patterns(limit=10),
                }
            )
        except Exception as exc:
            return jsonify({"status": "error", "message": str(exc)}), 500

    @blueprint.route("/api/export")
    def api_export():
        """Export filtered logs as JSON, CSV, or NDJSON."""
        try:
            export_format = request.args.get("format", "csv")
            limit = request_limit(default=1000)
            logs = filtered_logs(limit)
            payload = LogExporter.export(logs, format=export_format)
            mimetype = {
                "json": "application/json",
                "csv": "text/csv",
                "ndjson": "application/x-ndjson",
            }[export_format.lower()]
            response = Response(payload, mimetype=mimetype)
            response.headers["Content-Disposition"] = (
                f"attachment; filename=loglensx-export.{export_format.lower()}"
            )
            return response
        except ValueError as exc:
            return jsonify({"status": "error", "message": str(exc)}), 400
        except Exception as exc:
            return jsonify({"status": "error", "message": str(exc)}), 500

    @blueprint.route("/api/search")
    def search():
        """Search logs by query."""
        try:
            query = request.args.get("query") or request.args.get("q", "")
            if not query:
                return jsonify({"status": "error", "message": "Query parameter required"}), 400

            results = parser.search_logs(query, limit=100)
            return jsonify({"status": "success", "count": len(results), "results": results})
        except Exception as exc:
            return jsonify({"status": "error", "message": str(exc)}), 500

    @blueprint.route("/api/files")
    def api_files():
        """Get available log files metadata."""
        try:
            return jsonify({"status": "success", "files": analyzer.get_file_statistics()})
        except Exception as exc:
            return jsonify({"status": "error", "message": str(exc)}), 500

    app.register_blueprint(blueprint)

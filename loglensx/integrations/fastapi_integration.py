"""
FastAPI integration for the loglensx dashboard.
"""

from typing import Optional

from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, Response

from ..core.analyzer import LogAnalyzer
from ..core.exporter import LogExporter
from ..core.parser import LogParser
from ._dashboard import (
    DASHBOARD_STYLES as ENHANCED_STYLES,
    default_links,
    render_dashboard_page,
    render_logs_page,
)


__all__ = ["ENHANCED_STYLES", "setup_fastapi_loglensx"]


def setup_fastapi_loglensx(
    app: FastAPI,
    log_dir: str = "logs",
    prefix: str = "/loglensx",
) -> None:
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
    links = default_links(prefix)

    @router.get("/", response_class=HTMLResponse)
    def dashboard():
        """Main loglensx dashboard with interactive charts and tables."""
        summary = analyzer.get_log_summary()
        level_stats = analyzer.get_level_statistics()
        top_loggers = analyzer.get_top_loggers(limit=12)
        recent_errors = analyzer.get_recent_errors(limit=10)
        error_frequency = analyzer.get_error_frequency()

        return render_dashboard_page(
            links=links,
            summary=summary,
            level_stats=level_stats,
            top_loggers=top_loggers,
            error_frequency=error_frequency,
            recent_errors=recent_errors,
            log_dir=log_dir,
        )

    @router.get("/logs", response_class=HTMLResponse)
    def logs_page(
        search: Optional[str] = Query(None),
        level: Optional[str] = Query(None),
        logger: Optional[str] = Query(None),
        source_file: Optional[str] = Query(None, alias="file"),
        since: Optional[str] = Query(None),
        until: Optional[str] = Query(None),
        limit: int = Query(100, ge=1, le=1000),
    ):
        """Browsable log explorer page with advanced filtering."""
        logs = analyzer.filter_logs(
            level=level,
            logger=logger,
            search_term=search,
            source_file=source_file,
            since=since,
            until=until,
            limit=limit,
        )

        return render_logs_page(
            links=links,
            logs=logs,
            log_dir=log_dir,
            search=search,
            level=level,
            logger=logger,
            source_file=source_file,
            since=since,
            until=until,
            limit=limit,
        )

    @router.get("/api/logs", response_class=JSONResponse)
    def get_logs(
        search: Optional[str] = Query(None),
        level: Optional[str] = Query(None),
        logger: Optional[str] = Query(None),
        source_file: Optional[str] = Query(None, alias="file"),
        since: Optional[str] = Query(None),
        until: Optional[str] = Query(None),
        limit: int = Query(100, ge=1, le=1000),
    ):
        """Get logs with optional filters in JSON format."""
        try:
            logs = analyzer.filter_logs(
                level=level,
                logger=logger,
                search_term=search,
                source_file=source_file,
                since=since,
                until=until,
                limit=limit,
            )
            return {"status": "success", "count": len(logs), "logs": logs}
        except ValueError as exc:
            return JSONResponse(status_code=400, content={"status": "error", "detail": str(exc)})
        except Exception as exc:
            return JSONResponse(status_code=500, content={"status": "error", "detail": str(exc)})

    @router.get("/api/stats", response_class=JSONResponse)
    def get_stats():
        """Get comprehensive log statistics."""
        try:
            return {
                "status": "success",
                "summary": analyzer.get_log_summary(),
                "level_stats": analyzer.get_level_statistics(),
                "top_loggers": analyzer.get_top_loggers(limit=15),
                "error_frequency": analyzer.get_error_frequency(),
                "error_patterns": analyzer.get_error_patterns(limit=10),
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/api/export")
    def export_logs(
        format: str = Query("csv", regex="^(json|csv|ndjson)$"),
        search: Optional[str] = Query(None),
        level: Optional[str] = Query(None),
        logger: Optional[str] = Query(None),
        source_file: Optional[str] = Query(None, alias="file"),
        since: Optional[str] = Query(None),
        until: Optional[str] = Query(None),
        limit: int = Query(1000, ge=1, le=1000),
    ):
        """Export filtered logs as JSON, CSV, or NDJSON."""
        try:
            logs = analyzer.filter_logs(
                level=level,
                logger=logger,
                search_term=search,
                source_file=source_file,
                since=since,
                until=until,
                limit=limit,
            )
            payload = LogExporter.export(logs, format=format)
            media_type = {
                "json": "application/json",
                "csv": "text/csv",
                "ndjson": "application/x-ndjson",
            }[format]
            return Response(
                content=payload,
                media_type=media_type,
                headers={"Content-Disposition": f"attachment; filename=loglensx-export.{format}"},
            )
        except ValueError as exc:
            return JSONResponse(status_code=400, content={"status": "error", "detail": str(exc)})
        except Exception as exc:
            return JSONResponse(status_code=500, content={"status": "error", "detail": str(exc)})

    @router.get("/api/search", response_class=JSONResponse)
    def search_logs(query: str = Query(..., min_length=1)):
        """Search logs by query string."""
        try:
            results = parser.search_logs(query, limit=100)
            return {"status": "success", "count": len(results), "results": results}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @router.get("/api/files", response_class=JSONResponse)
    def get_log_files():
        """Get available log files metadata."""
        try:
            return {"status": "success", "files": analyzer.get_file_statistics()}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    app.include_router(router)

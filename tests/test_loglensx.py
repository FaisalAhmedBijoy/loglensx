"""Test suite for loglensx."""

import json
import pytest
import os
import tempfile
from pathlib import Path
from datetime import datetime
from loglensx.cli import main as cli_main
from loglensx.core.parser import LogParser
from loglensx.core.analyzer import LogAnalyzer
from loglensx.core.exporter import LogExporter
from loglensx.integrations._dashboard import default_links, render_dashboard_page, render_logs_page
from loglensx.visualizers.tables import TableGenerator


@pytest.fixture
def temp_log_dir():
    """Create a temporary log directory with sample logs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample log file
        log_file = Path(tmpdir) / f"log_file_{datetime.now().strftime('%Y-%m-%d')}.log"
        log_file.write_text(
            "[2024-01-15 10:30:45] [ERROR] [app.database] Connection timeout\n"
            "[2024-01-15 10:30:46] [WARNING] [app.cache] Cache miss\n"
            "[2024-01-15 10:30:47] [INFO] [app.api] GET /users - 200\n"
            "[2024-01-15 10:30:48] [DEBUG] [app.service] Processing request\n"
        )
        yield tmpdir


class TestLogParser:
    """Test LogParser class."""

    def test_parser_initialization(self, temp_log_dir):
        """Test parser initialization."""
        parser = LogParser(log_dir=temp_log_dir)
        assert parser.log_dir == Path(temp_log_dir)

    def test_get_log_files(self, temp_log_dir):
        """Test getting log files."""
        parser = LogParser(log_dir=temp_log_dir)
        files = parser.get_log_files()
        assert len(files) > 0
        assert files[0].suffix == ".log"

    def test_parse_log_file(self, temp_log_dir):
        """Test parsing a log file."""
        parser = LogParser(log_dir=temp_log_dir)
        files = parser.get_log_files()
        entries = parser.parse_log_file(files[0])
        assert len(entries) == 4
        assert entries[0]["level"] == "ERROR"
        assert entries[1]["level"] == "WARNING"

    def test_parse_all_logs(self, temp_log_dir):
        """Test parsing all logs."""
        parser = LogParser(log_dir=temp_log_dir)
        all_entries = parser.parse_all_logs()
        assert len(all_entries) >= 4

    def test_parse_logs_by_level(self, temp_log_dir):
        """Test parsing logs grouped by level."""
        parser = LogParser(log_dir=temp_log_dir)
        logs_by_level = parser.parse_logs_by_level()
        assert "ERROR" in logs_by_level
        assert "WARNING" in logs_by_level
        assert "INFO" in logs_by_level

    def test_search_logs(self, temp_log_dir):
        """Test searching logs."""
        parser = LogParser(log_dir=temp_log_dir)
        results = parser.search_logs("Connection")
        assert len(results) > 0
        assert "Connection timeout" in results[0]["message"]

    def test_custom_pattern_is_used_before_builtin_patterns(self):
        """Custom regex patterns should parse non-default log formats."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "custom.log"
            log_file.write_text("2024-01-15T10:31:00|ERROR|billing.worker|Payment failed\n")

            pattern = r"(?P<timestamp>.*?)\|(?P<level>\w+)\|" r"(?P<logger>.*?)\|(?P<message>.*)"
            parser = LogParser(log_dir=tmpdir, pattern=pattern)
            entries = parser.parse_log_file(log_file)

            assert entries[0]["timestamp"] == "2024-01-15T10:31:00"
            assert entries[0]["level"] == "ERROR"
            assert entries[0]["logger"] == "billing.worker"
            assert entries[0]["format"] == "custom"

    def test_json_logs_and_multiline_tracebacks_are_parsed(self):
        """JSON log lines should keep extras and absorb traceback continuations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "json.log"
            log_file.write_text(
                '{"time":"2024-01-15T10:31:00","severity":"error",'
                '"name":"app.api","event":"Request failed","request_id":"abc123"}\n'
                "Traceback (most recent call last):\n"
                '  File "app.py", line 10, in handler\n'
                "ValueError: boom\n"
            )

            parser = LogParser(log_dir=tmpdir)
            entries = parser.parse_log_file(log_file)

            assert len(entries) == 1
            assert entries[0]["level"] == "ERROR"
            assert entries[0]["logger"] == "app.api"
            assert "Traceback" in entries[0]["message"]
            assert entries[0]["extra"]["request_id"] == "abc123"

    def test_unstructured_lines_do_not_merge_unless_they_look_like_continuations(self):
        """Plain unmatched lines should remain separate fallback entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "plain.log"
            log_file.write_text("server started\nrequest completed\n")

            entries = LogParser(log_dir=tmpdir).parse_log_file(log_file)

            assert len(entries) == 2
            assert entries[0]["message"] == "server started"
            assert entries[1]["message"] == "request completed"


class TestLogAnalyzer:
    """Test LogAnalyzer class."""

    def test_analyzer_initialization(self, temp_log_dir):
        """Test analyzer initialization."""
        parser = LogParser(log_dir=temp_log_dir)
        analyzer = LogAnalyzer(parser)
        assert analyzer.parser == parser

    def test_get_level_statistics(self, temp_log_dir):
        """Test getting level statistics."""
        parser = LogParser(log_dir=temp_log_dir)
        analyzer = LogAnalyzer(parser)
        stats = analyzer.get_level_statistics()
        assert "ERROR" in stats
        assert "WARNING" in stats
        assert stats["ERROR"] > 0

    def test_get_log_summary(self, temp_log_dir):
        """Test getting log summary."""
        parser = LogParser(log_dir=temp_log_dir)
        analyzer = LogAnalyzer(parser)
        summary = analyzer.get_log_summary()
        assert summary["total_logs"] > 0
        assert "error_count" in summary
        assert "warning_count" in summary

    def test_get_recent_errors(self, temp_log_dir):
        """Test getting recent errors."""
        parser = LogParser(log_dir=temp_log_dir)
        analyzer = LogAnalyzer(parser)
        errors = analyzer.get_recent_errors(limit=5)
        assert len(errors) > 0
        assert errors[0]["level"] == "ERROR"

    def test_filter_logs(self, temp_log_dir):
        """Test filtering logs."""
        parser = LogParser(log_dir=temp_log_dir)
        analyzer = LogAnalyzer(parser)

        # Filter by level
        errors = analyzer.filter_logs(level="ERROR")
        assert all(e["level"] == "ERROR" for e in errors)

        # Filter by search term
        results = analyzer.filter_logs(search_term="cache")
        assert len(results) > 0

    def test_filter_logs_by_time_window_and_file(self, temp_log_dir):
        """Analyzer filters should support time windows and source files."""
        parser = LogParser(log_dir=temp_log_dir)
        analyzer = LogAnalyzer(parser)
        file_name = Path(parser.get_log_files()[0]).name

        results = analyzer.filter_logs(
            since="2024-01-15 10:30:46",
            until="2024-01-15 10:30:47",
            source_file=file_name,
            limit=10,
        )

        assert {entry["level"] for entry in results} == {"WARNING", "INFO"}

    def test_get_error_patterns_groups_recurring_messages(self):
        """Repeated dynamic error messages should collapse into patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "errors.log"
            log_file.write_text(
                "[2024-01-15 10:30:45] [ERROR] [app.db] User 123 lookup failed\n"
                "[2024-01-15 10:30:46] [ERROR] [app.db] User 456 lookup failed\n"
            )

            analyzer = LogAnalyzer(LogParser(log_dir=tmpdir))
            patterns = analyzer.get_error_patterns()

            assert patterns[0]["count"] == 2
            assert "user {number} lookup failed" == patterns[0]["pattern"]


class TestLogExporter:
    """Test export serialization helpers."""

    def test_export_json_csv_and_ndjson(self):
        """Exporter should serialize stable fields and flattened extras."""
        entries = [
            {
                "timestamp": "2024-01-15 10:30:45",
                "level": "ERROR",
                "logger": "app.database",
                "message": "Connection timeout",
                "file": "app.log",
                "line_num": 42,
                "raw": "raw line",
                "extra": {"request_id": "abc123"},
            }
        ]

        json_payload = LogExporter.to_json(entries)
        csv_payload = LogExporter.to_csv(entries)
        ndjson_payload = LogExporter.to_ndjson(entries)

        assert json.loads(json_payload)[0]["message"] == "Connection timeout"
        assert "extra.request_id" in csv_payload
        assert json.loads(ndjson_payload)["logger"] == "app.database"


class TestTableGenerator:
    """Test HTML generation for log tables."""

    def test_logs_to_html_table_includes_source_and_badges(self):
        """Table should render level badges and file source information."""
        entries = [
            {
                "timestamp": "2024-01-15 10:30:45",
                "level": "ERROR",
                "logger": "app.database",
                "message": "Connection timeout while fetching user profile",
                "file": "app.log",
                "line_num": 42,
            }
        ]

        html = TableGenerator.logs_to_html_table(entries, title="Log Explorer")
        assert "Log Explorer" in html
        assert "ERROR" in html
        assert "app.log:42" in html
        assert "Visible Logs" in html

    def test_logs_to_html_table_uses_expandable_message_for_long_entries(self):
        """Long messages should be expandable instead of abruptly cut off."""
        entries = [
            {
                "timestamp": "2024-01-15 10:30:45",
                "level": "INFO",
                "logger": "app.api",
                "message": "A" * 220,
                "file": "api.log",
                "line_num": 7,
            }
        ]

        html = TableGenerator.logs_to_html_table(entries)
        assert "<details>" in html
        assert "api.log:7" in html


class TestDashboardRendering:
    """Test shared dashboard rendering used by Flask and FastAPI."""

    def test_dashboard_page_contains_interactive_charts_and_table(self, temp_log_dir):
        """Dashboard HTML should include Plotly targets and the enhanced table."""
        parser = LogParser(log_dir=temp_log_dir)
        analyzer = LogAnalyzer(parser)
        links = default_links("/loglensx")

        html = render_dashboard_page(
            links=links,
            summary=analyzer.get_log_summary(),
            level_stats=analyzer.get_level_statistics(),
            top_loggers=analyzer.get_top_loggers(),
            error_frequency=analyzer.get_error_frequency(),
            recent_errors=analyzer.get_recent_errors(),
            log_dir=temp_log_dir,
        )

        assert "Log Intelligence" in html
        assert "levelChart" in html
        assert "loggersChart" in html
        assert "window.LOGLENSX_DATA" in html
        assert "data-log-table" in html

    def test_logs_page_contains_sortable_table_controls(self, temp_log_dir):
        """Log explorer HTML should render sortable columns and client-side controls."""
        parser = LogParser(log_dir=temp_log_dir)
        analyzer = LogAnalyzer(parser)

        html = render_logs_page(
            links=default_links("/loglensx"),
            logs=analyzer.filter_logs(limit=10),
            log_dir=temp_log_dir,
            limit=10,
        )

        assert "Log Explorer" in html
        assert "data-table-search" in html
        assert 'data-sort="timestamp"' in html
        assert 'name="since"' in html
        assert 'name="file"' in html
        assert "Export CSV" in html
        assert "JSON Results" in html


class TestCLI:
    """Test command-line workflows."""

    def test_cli_logs_json_output(self, temp_log_dir, capsys):
        """The logs command should emit filtered JSON."""
        exit_code = cli_main(
            [
                "logs",
                "--log-dir",
                temp_log_dir,
                "--level",
                "ERROR",
                "--format",
                "json",
            ]
        )
        captured = capsys.readouterr()

        assert exit_code == 0
        payload = json.loads(captured.out)
        assert payload[0]["level"] == "ERROR"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

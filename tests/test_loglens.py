"""Test suite for LogLens."""

import pytest
import os
import tempfile
from pathlib import Path
from datetime import datetime
from loglens.core.parser import LogParser
from loglens.core.analyzer import LogAnalyzer


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

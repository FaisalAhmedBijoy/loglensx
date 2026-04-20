"""
Log analysis module for generating statistics and insights.
"""

from typing import List, Dict, Any, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from .parser import LogParser


class LogAnalyzer:
    """Analyze log entries and generate statistics."""

    def __init__(self, parser: LogParser):
        """
        Initialize the analyzer with a log parser.

        Args:
            parser: LogParser instance
        """
        self.parser = parser

    def get_level_statistics(self, limit: Optional[int] = None) -> Dict[str, int]:
        """Get count of logs by level."""
        logs_by_level = self.parser.parse_logs_by_level(limit=limit)
        return {level: len(entries) for level, entries in logs_by_level.items()}

    def get_top_loggers(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get top loggers by log count."""
        all_entries = self.parser.parse_all_logs()
        loggers = Counter(entry.get("logger", "unknown") for entry in all_entries)
        return loggers.most_common(limit)

    def get_error_frequency(self, hours: int = 24) -> Dict[str, int]:
        """Get error frequency over the last N hours."""
        all_entries = self.parser.parse_all_logs()
        errors = [e for e in all_entries if e.get("level") == "ERROR"]

        frequency = defaultdict(int)
        for entry in errors:
            try:
                ts_str = entry.get("timestamp", "")
                # Parse timestamp (format: YYYY-MM-DD HH:MM:SS)
                ts = datetime.strptime(ts_str.split('.')[0], "%Y-%m-%d %H:%M:%S")
                hour_key = ts.strftime("%Y-%m-%d %H:00")
                frequency[hour_key] += 1
            except Exception:
                pass

        return dict(sorted(frequency.items()))

    def get_logger_distribution(self) -> Dict[str, int]:
        """Get distribution of logs across loggers."""
        all_entries = self.parser.parse_all_logs()
        distribution = defaultdict(int)

        for entry in all_entries:
            logger = entry.get("logger", "unknown")
            distribution[logger] += 1

        return dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))

    def get_log_summary(self) -> Dict[str, Any]:
        """Get overall summary of logs."""
        all_entries = self.parser.parse_all_logs()
        logs_by_level = self.parser.parse_logs_by_level()

        return {
            "total_logs": len(all_entries),
            "by_level": {level: len(entries) for level, entries in logs_by_level.items()},
            "error_count": len(logs_by_level.get("ERROR", [])),
            "warning_count": len(logs_by_level.get("WARNING", [])),
            "info_count": len(logs_by_level.get("INFO", [])),
            "debug_count": len(logs_by_level.get("DEBUG", [])),
            "unique_loggers": len(set(e.get("logger") for e in all_entries)),
            "files": len(set(e.get("file") for e in all_entries)),
        }

    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent error entries."""
        all_entries = self.parser.parse_all_logs()
        errors = [e for e in all_entries if e.get("level") == "ERROR"]
        return errors[:limit]

    def get_recent_warnings(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent warning entries."""
        all_entries = self.parser.parse_all_logs()
        warnings = [e for e in all_entries if e.get("level") == "WARNING"]
        return warnings[:limit]

    def filter_logs(
        self,
        level: Optional[str] = None,
        logger: Optional[str] = None,
        search_term: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Filter logs by various criteria."""
        all_entries = self.parser.parse_all_logs(limit=limit * 5)

        if level:
            all_entries = [e for e in all_entries if e.get("level") == level.upper()]

        if logger:
            all_entries = [e for e in all_entries if logger.lower() in e.get("logger", "").lower()]

        if search_term:
            search_lower = search_term.lower()
            all_entries = [
                e for e in all_entries
                if search_lower in e.get("message", "").lower()
            ]

        return all_entries[:limit]

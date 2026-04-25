"""
Log analysis module for generating statistics and insights.
"""

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import re
from typing import Any, DefaultDict, Dict, Iterable, List, Optional, Tuple

from dateutil import parser as date_parser

from .parser import LogParser


class LogAnalyzer:
    """Analyze log entries and generate statistics."""

    ERROR_LEVELS = {"CRITICAL", "ERROR"}

    def __init__(self, parser: LogParser):
        """
        Initialize the analyzer with a log parser.

        Args:
            parser: LogParser instance
        """
        self.parser = parser

    def get_level_statistics(
        self,
        limit: Optional[int] = None,
        since: Optional[Any] = None,
        until: Optional[Any] = None,
        source_file: Optional[str] = None,
    ) -> Dict[str, int]:
        """Get count of logs by level."""
        entries = self._filter_entries(
            self.parser.parse_all_logs(limit=limit),
            since=since,
            until=until,
            source_file=source_file,
        )
        return dict(Counter(entry.get("level", "INFO") for entry in entries))

    def get_top_loggers(
        self,
        limit: int = 10,
        since: Optional[Any] = None,
        until: Optional[Any] = None,
        source_file: Optional[str] = None,
    ) -> List[Tuple[str, int]]:
        """Get top loggers by log count."""
        all_entries = self._filter_entries(
            self.parser.parse_all_logs(),
            since=since,
            until=until,
            source_file=source_file,
        )
        loggers = Counter(entry.get("logger") or "root" for entry in all_entries)
        return loggers.most_common(limit)

    def get_error_frequency(
        self,
        hours: int = 24,
        since: Optional[Any] = None,
        until: Optional[Any] = None,
    ) -> Dict[str, int]:
        """Get critical/error frequency by hour.

        When ``since`` is not provided, ``hours`` is anchored to the newest
        parsed error timestamp. This keeps historical log fixtures useful while
        still returning a rolling window for live logs.
        """
        all_entries = self.parser.parse_all_logs()
        errors = [e for e in all_entries if e.get("level") in self.ERROR_LEVELS]
        parsed_errors = [(entry, self._entry_datetime(entry)) for entry in errors]
        parsed_errors = [(entry, ts) for entry, ts in parsed_errors if ts]

        lower_bound = self._parse_datetime(since)
        upper_bound = self._parse_datetime(until)
        if lower_bound is None and hours and hours > 0 and parsed_errors:
            newest = max(ts for _, ts in parsed_errors if ts)
            lower_bound = newest - timedelta(hours=hours)

        frequency: DefaultDict[str, int] = defaultdict(int)
        for _, ts in parsed_errors:
            if lower_bound and ts < lower_bound:
                continue
            if upper_bound and ts > upper_bound:
                continue
            hour_key = ts.strftime("%Y-%m-%d %H:00")
            frequency[hour_key] += 1

        return dict(sorted(frequency.items()))

    def get_logger_distribution(
        self,
        since: Optional[Any] = None,
        until: Optional[Any] = None,
        source_file: Optional[str] = None,
    ) -> Dict[str, int]:
        """Get distribution of logs across loggers."""
        all_entries = self._filter_entries(
            self.parser.parse_all_logs(),
            since=since,
            until=until,
            source_file=source_file,
        )
        distribution: DefaultDict[str, int] = defaultdict(int)

        for entry in all_entries:
            logger = entry.get("logger") or "root"
            distribution[logger] += 1

        return dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))

    def get_log_summary(
        self,
        since: Optional[Any] = None,
        until: Optional[Any] = None,
        source_file: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get overall summary of logs."""
        all_entries = self._filter_entries(
            self.parser.parse_all_logs(),
            since=since,
            until=until,
            source_file=source_file,
        )
        by_level = Counter(entry.get("level", "INFO") for entry in all_entries)
        parsed_times = [self._entry_datetime(entry) for entry in all_entries]
        parsed_times = [ts for ts in parsed_times if ts]

        return {
            "total_logs": len(all_entries),
            "by_level": dict(by_level),
            "critical_count": by_level.get("CRITICAL", 0),
            "error_count": by_level.get("ERROR", 0),
            "warning_count": by_level.get("WARNING", 0),
            "info_count": by_level.get("INFO", 0),
            "debug_count": by_level.get("DEBUG", 0),
            "unique_loggers": len(set(e.get("logger") or "root" for e in all_entries)),
            "files": len(set(e.get("file") for e in all_entries)),
            "first_timestamp": min(parsed_times).isoformat(sep=" ") if parsed_times else "",
            "last_timestamp": max(parsed_times).isoformat(sep=" ") if parsed_times else "",
        }

    def get_recent_errors(
        self,
        limit: int = 10,
        since: Optional[Any] = None,
        until: Optional[Any] = None,
        source_file: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get recent error entries."""
        all_entries = self._filter_entries(
            self.parser.parse_all_logs(),
            levels=self.ERROR_LEVELS,
            since=since,
            until=until,
            source_file=source_file,
        )
        errors = self._sort_entries(all_entries)
        return errors[:limit]

    def get_recent_warnings(
        self,
        limit: int = 10,
        since: Optional[Any] = None,
        until: Optional[Any] = None,
        source_file: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get recent warning entries."""
        all_entries = self._filter_entries(
            self.parser.parse_all_logs(),
            levels=["WARNING"],
            since=since,
            until=until,
            source_file=source_file,
        )
        warnings = self._sort_entries(all_entries)
        return warnings[:limit]

    def filter_logs(
        self,
        level: Optional[str] = None,
        levels: Optional[Iterable[str]] = None,
        logger: Optional[str] = None,
        search_term: Optional[str] = None,
        source_file: Optional[str] = None,
        since: Optional[Any] = None,
        until: Optional[Any] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Filter logs by various criteria."""
        target_levels = list(levels or [])
        if level:
            target_levels.append(level)

        all_entries = self._filter_entries(
            self.parser.parse_all_logs(),
            levels=target_levels or None,
            logger=logger,
            search_term=search_term,
            source_file=source_file,
            since=since,
            until=until,
        )

        return all_entries[:limit]

    def get_file_statistics(self) -> List[Dict[str, Any]]:
        """Get file metadata enriched with parsed entry counts."""
        entries_by_file: DefaultDict[str, List[Dict[str, Any]]] = defaultdict(list)
        for entry in self.parser.parse_all_logs():
            entries_by_file[entry.get("file", "")].append(entry)

        file_stats: List[Dict[str, Any]] = []
        for file_path in self.parser.get_log_files():
            entries = entries_by_file.get(file_path.name, [])
            times = [self._entry_datetime(entry) for entry in entries]
            times = [ts for ts in times if ts]
            level_counts = Counter(entry.get("level", "INFO") for entry in entries)
            file_stats.append(
                {
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime,
                    "entries": len(entries),
                    "by_level": dict(level_counts),
                    "first_timestamp": min(times).isoformat(sep=" ") if times else "",
                    "last_timestamp": max(times).isoformat(sep=" ") if times else "",
                }
            )

        return file_stats

    def get_error_patterns(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Group recurring critical/error messages by a normalized message signature."""
        errors = [
            entry
            for entry in self.parser.parse_all_logs()
            if entry.get("level") in self.ERROR_LEVELS
        ]

        grouped: Dict[str, Dict[str, Any]] = {}
        for entry in errors:
            message = str(entry.get("message", ""))
            pattern = self._normalize_message_pattern(message)
            if pattern not in grouped:
                grouped[pattern] = {
                    "pattern": pattern,
                    "count": 0,
                    "example": message,
                    "level": entry.get("level", "ERROR"),
                    "last_seen": entry.get("timestamp", ""),
                }
            grouped[pattern]["count"] += 1

        return sorted(grouped.values(), key=lambda item: item["count"], reverse=True)[:limit]

    def _filter_entries(
        self,
        entries: Iterable[Dict[str, Any]],
        levels: Optional[Iterable[str]] = None,
        logger: Optional[str] = None,
        search_term: Optional[str] = None,
        source_file: Optional[str] = None,
        since: Optional[Any] = None,
        until: Optional[Any] = None,
    ) -> List[Dict[str, Any]]:
        """Apply shared entry filters used by summaries, APIs, and the CLI."""
        filtered = list(entries)

        if levels:
            normalized_levels = {self._normalize_level(level) for level in levels}
            filtered = [entry for entry in filtered if entry.get("level") in normalized_levels]

        if logger:
            logger_lower = logger.lower()
            filtered = [
                entry
                for entry in filtered
                if logger_lower in str(entry.get("logger", "") or "root").lower()
            ]

        if search_term:
            search_lower = search_term.lower()
            filtered = [
                entry
                for entry in filtered
                if search_lower
                in " ".join(
                    [
                        str(entry.get("message", "")),
                        str(entry.get("logger", "")),
                        str(entry.get("file", "")),
                        str(entry.get("raw", "")),
                    ]
                ).lower()
            ]

        if source_file:
            source_lower = source_file.lower()
            filtered = [
                entry for entry in filtered if source_lower in str(entry.get("file", "")).lower()
            ]

        lower_bound = self._parse_datetime(since)
        upper_bound = self._parse_datetime(until)
        if lower_bound or upper_bound:
            filtered = [
                entry
                for entry in filtered
                if self._within_time_bounds(entry, lower_bound, upper_bound)
            ]

        return self._sort_entries(filtered)

    def _within_time_bounds(
        self,
        entry: Dict[str, Any],
        lower_bound: Optional[datetime],
        upper_bound: Optional[datetime],
    ) -> bool:
        """Check whether an entry timestamp falls inside the requested window."""
        entry_time = self._entry_datetime(entry)
        if entry_time is None:
            return False
        if lower_bound and entry_time < lower_bound:
            return False
        if upper_bound and entry_time > upper_bound:
            return False
        return True

    def _sort_entries(self, entries: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort entries newest-first when timestamps are available."""
        return sorted(
            entries,
            key=lambda entry: (
                self._entry_datetime(entry) or datetime.min,
                str(entry.get("file", "")),
                self._safe_int(entry.get("line_num")),
            ),
            reverse=True,
        )

    def _entry_datetime(self, entry: Dict[str, Any]) -> Optional[datetime]:
        """Parse an entry timestamp into a comparable datetime."""
        return self._parse_datetime(entry.get("timestamp"))

    @staticmethod
    def _parse_datetime(value: Optional[Any]) -> Optional[datetime]:
        """Parse a flexible timestamp string into a naive UTC datetime."""
        if value in (None, ""):
            return None
        if isinstance(value, datetime):
            parsed = value
        else:
            text = str(value).strip()
            if not text:
                return None
            try:
                parsed = date_parser.parse(text)
            except (TypeError, ValueError, OverflowError):
                return None

        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed

    @staticmethod
    def _normalize_level(value: Any) -> str:
        """Normalize level aliases for filtering."""
        level = str(value or "INFO").upper()
        return LogParser.LEVEL_ALIASES.get(level, level)

    @staticmethod
    def _normalize_message_pattern(message: str) -> str:
        """Reduce dynamic values in a message so recurring failures group together."""
        normalized = message.strip().lower()
        normalized = re.sub(r"\b[0-9a-f]{8,}\b", "{hex}", normalized)
        normalized = re.sub(r"\b\d+(?:\.\d+)?\b", "{number}", normalized)
        normalized = re.sub(r"\s+", " ", normalized)
        return normalized[:240]

    @staticmethod
    def _safe_int(value: Any) -> int:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

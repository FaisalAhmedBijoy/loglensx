"""
Log file parser for extracting and parsing log entries.
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Tuple


class LogParser:
    """Parse and extract information from log files."""

    # Pattern to match common log formats
    LOG_PATTERNS = {
        "standard": r"\[(?P<timestamp>.*?)\]\s*\[(?P<level>\w+)\]\s*\[(?P<logger>.*?)\]\s*(?P<message>.*)",
        "simple": r"(?P<timestamp>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\s*-\s*(?P<level>\w+)\s*-\s*(?P<message>.*)",
        "error": r"(?P<level>CRITICAL|ERROR|WARNING|WARN|INFO|DEBUG|TRACE):\s*(?P<message>.*?)(?:\s+(?P<context>\{.*?\}))?(?:\s+(?P<exception>.*))?$",
    }

    LEVEL_ALIASES = {
        "WARN": "WARNING",
        "FATAL": "CRITICAL",
    }
    TRACEBACK_PREFIXES = (
        "Traceback ",
        "During handling of the above exception",
        "The above exception was the direct cause",
        "Caused by:",
    )
    EXCEPTION_SUMMARY_PATTERN = re.compile(r"^[A-Za-z_][\w.]*(Error|Exception|Warning|Interrupt)?:")
    TIMESTAMP_KEYS = ("timestamp", "time", "asctime", "datetime", "date", "ts")
    LEVEL_KEYS = ("level", "levelname", "severity", "status")
    LOGGER_KEYS = ("logger", "logger_name", "name", "module")
    MESSAGE_KEYS = ("message", "msg", "event", "text")

    def __init__(
        self,
        log_dir: str = "logs",
        pattern: Optional[str] = None,
        merge_multiline: bool = True,
    ):
        """
        Initialize the log parser.

        Args:
            log_dir: Directory containing log files
            pattern: Optional regex pattern for parsing logs
            merge_multiline: Append unmatched continuation lines to the previous entry.
        """
        self.log_dir = Path(log_dir)
        self.pattern = pattern or self.LOG_PATTERNS["standard"]
        self.custom_pattern = pattern
        self.merge_multiline = merge_multiline
        self._compiled_patterns = self._compile_patterns(pattern)

    def _compile_patterns(self, pattern: Optional[str]) -> List[Tuple[str, Pattern[str]]]:
        """Compile custom and built-in regex patterns in matching order."""
        compiled: List[Tuple[str, Pattern[str]]] = []
        if pattern:
            compiled.append(("custom", re.compile(pattern)))

        for pattern_name, pattern_value in self.LOG_PATTERNS.items():
            compiled.append((pattern_name, re.compile(pattern_value)))

        return compiled

    def get_log_files(self, limit: Optional[int] = None) -> List[Path]:
        """Get all log files in the log directory, sorted by date (newest first)."""
        if limit is not None and limit < 0:
            raise ValueError("limit must be a positive integer")

        if not self.log_dir.exists():
            return []

        log_files = sorted(
            self.log_dir.glob("*.log"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        return log_files[:limit] if limit else log_files

    def parse_log_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse a single log file and extract log entries."""
        logger = logging.getLogger(__name__)

        entries: List[Dict[str, Any]] = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                for line_num, line in enumerate(f, 1):
                    clean_line = line.rstrip("\n\r")
                    stripped = clean_line.strip()
                    if not stripped:
                        continue

                    entry = self._match_log_line(stripped, file_path.name, line_num)
                    if entry:
                        entries.append(entry)
                    elif (
                        self.merge_multiline
                        and entries
                        and self._is_continuation_line(clean_line, entries[-1])
                    ):
                        self._append_continuation(entries[-1], clean_line, line_num)
                    else:
                        entries.append(self._fallback_entry(stripped, file_path.name, line_num))
        except (IOError, OSError) as e:
            logger.error(f"Error parsing {file_path}: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Unexpected error parsing {file_path}: {e}", exc_info=True)

        return entries

    def _parse_log_line(self, line: str, filename: str, line_num: int) -> Optional[Dict[str, Any]]:
        """Parse a single log line using regex patterns."""
        return self._match_log_line(line, filename, line_num) or self._fallback_entry(
            line,
            filename,
            line_num,
        )

    def _match_log_line(self, line: str, filename: str, line_num: int) -> Optional[Dict[str, Any]]:
        """Return a parsed entry only when the line matches a known structured format."""
        json_entry = self._parse_json_line(line, filename, line_num)
        if json_entry:
            return json_entry

        for pattern_name, pattern in self._compiled_patterns:
            match = pattern.search(line)
            if match:
                groups = match.groupdict()
                return self._entry_from_groups(groups, line, filename, line_num, pattern_name)

        return None

    def _parse_json_line(self, line: str, filename: str, line_num: int) -> Optional[Dict[str, Any]]:
        """Parse common structured JSON log lines."""
        if not line.startswith("{"):
            return None

        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            return None

        if not isinstance(payload, dict):
            return None

        timestamp_key = self._first_present_key(payload, self.TIMESTAMP_KEYS)
        level_key = self._first_present_key(payload, self.LEVEL_KEYS)
        logger_key = self._first_present_key(payload, self.LOGGER_KEYS)
        message_key = self._first_present_key(payload, self.MESSAGE_KEYS)

        known_keys = {key for key in (timestamp_key, level_key, logger_key, message_key) if key}
        extra = {key: value for key, value in payload.items() if key not in known_keys}

        message = payload.get(message_key, payload) if message_key else payload
        return {
            "timestamp": self._stringify(payload.get(timestamp_key, "")) if timestamp_key else "",
            "level": self._normalize_level(payload.get(level_key, "INFO")) if level_key else "INFO",
            "logger": self._stringify(payload.get(logger_key, "")) if logger_key else "",
            "message": self._stringify(message),
            "file": filename,
            "line_num": line_num,
            "raw": line,
            "format": "json",
            "extra": extra,
        }

    def _entry_from_groups(
        self,
        groups: Dict[str, Any],
        line: str,
        filename: str,
        line_num: int,
        pattern_name: str,
    ) -> Dict[str, Any]:
        """Build a normalized entry from regex named groups."""
        timestamp = self._first_group(groups, self.TIMESTAMP_KEYS)
        level = self._first_group(groups, self.LEVEL_KEYS) or "INFO"
        logger = self._first_group(groups, self.LOGGER_KEYS)
        message = self._first_group(groups, self.MESSAGE_KEYS) or line
        known_keys = set(
            self.TIMESTAMP_KEYS + self.LEVEL_KEYS + self.LOGGER_KEYS + self.MESSAGE_KEYS
        )
        extra = {key: value for key, value in groups.items() if key not in known_keys and value}

        return {
            "timestamp": self._stringify(timestamp),
            "level": self._normalize_level(level),
            "logger": self._stringify(logger),
            "message": self._stringify(message),
            "file": filename,
            "line_num": line_num,
            "raw": line,
            "format": pattern_name,
            "extra": extra,
        }

    def _append_continuation(self, entry: Dict[str, Any], line: str, line_num: int) -> None:
        """Attach traceback or stack-frame continuation lines to the previous entry."""
        continuation = line.rstrip()
        if not continuation:
            return

        current_message = self._stringify(entry.get("message", ""))
        current_raw = self._stringify(entry.get("raw", ""))
        entry["message"] = f"{current_message}\n{continuation}" if current_message else continuation
        entry["raw"] = f"{current_raw}\n{continuation}" if current_raw else continuation
        entry.setdefault("continuation_lines", []).append(line_num)

    def _is_continuation_line(self, line: str, previous_entry: Dict[str, Any]) -> bool:
        """Detect traceback and stack-frame continuations without merging unrelated lines."""
        stripped = line.strip()
        if not stripped:
            return False
        if line[:1].isspace():
            return True
        if stripped.startswith(self.TRACEBACK_PREFIXES):
            return True
        if previous_entry.get("continuation_lines") and self.EXCEPTION_SUMMARY_PATTERN.match(
            stripped
        ):
            return True
        return False

    def _fallback_entry(self, line: str, filename: str, line_num: int) -> Dict[str, Any]:
        """Return the entire line as an INFO message when no parser matches."""
        return {
            "timestamp": "",
            "level": "INFO",
            "logger": "",
            "message": line,
            "file": filename,
            "line_num": line_num,
            "raw": line,
            "format": "fallback",
            "extra": {},
        }

    @staticmethod
    def _first_present_key(data: Dict[str, Any], keys: Tuple[str, ...]) -> Optional[str]:
        """Find the first present key from a list of common aliases."""
        for key in keys:
            if key in data:
                return key
        return None

    @staticmethod
    def _first_group(groups: Dict[str, Any], keys: Tuple[str, ...]) -> Any:
        """Find the first non-empty regex group from a list of aliases."""
        for key in keys:
            value = groups.get(key)
            if value not in (None, ""):
                return value
        return ""

    @classmethod
    def _normalize_level(cls, value: Any) -> str:
        """Normalize Python and common structured-logging level names."""
        level = cls._stringify(value).upper() or "INFO"
        return cls.LEVEL_ALIASES.get(level, level)

    @staticmethod
    def _stringify(value: Any) -> str:
        """Convert values to strings without losing structured JSON payloads."""
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        try:
            return json.dumps(value, sort_keys=True)
        except TypeError:
            return str(value)

    def parse_all_logs(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Parse all log files and return combined entries."""
        all_entries = []
        log_files = self.get_log_files(limit=limit)

        for log_file in log_files:
            entries = self.parse_log_file(log_file)
            all_entries.extend(entries)

        return all_entries

    def parse_logs_by_level(self, limit: Optional[int] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Parse logs and group by log level."""
        all_entries = self.parse_all_logs(limit=limit)
        grouped = {}

        for entry in all_entries:
            level = entry.get("level", "INFO")
            if level not in grouped:
                grouped[level] = []
            grouped[level].append(entry)

        return grouped

    def search_logs(self, query: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search for logs matching a query."""
        all_entries = self.parse_all_logs()
        query_lower = query.lower()
        results = [
            entry
            for entry in all_entries
            if query_lower in entry.get("message", "").lower()
            or query_lower in entry.get("logger", "").lower()
            or query_lower in entry.get("file", "").lower()
            or query_lower in entry.get("raw", "").lower()
        ]
        return results[:limit] if limit else results

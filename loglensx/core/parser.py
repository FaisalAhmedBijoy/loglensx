"""
Log file parser for extracting and parsing log entries.
"""

import re
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class LogParser:
    """Parse and extract information from log files."""

    # Pattern to match common log formats
    LOG_PATTERNS = {
        "standard": r"\[(?P<timestamp>.*?)\]\s*\[(?P<level>\w+)\]\s*\[(?P<logger>.*?)\]\s*(?P<message>.*)",
        "simple": r"(?P<timestamp>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\s*-\s*(?P<level>\w+)\s*-\s*(?P<message>.*)",
        "error": r"(?P<level>ERROR|WARNING|INFO|DEBUG):\s*(?P<message>.*?)(?:\s+(?P<context>\{.*?\}))?(?:\s+(?P<exception>.*))?$",
    }

    def __init__(self, log_dir: str = "logs", pattern: Optional[str] = None):
        """
        Initialize the log parser.

        Args:
            log_dir: Directory containing log files
            pattern: Optional regex pattern for parsing logs
        """
        self.log_dir = Path(log_dir)
        self.pattern = pattern or self.LOG_PATTERNS["standard"]

    def get_log_files(self, limit: Optional[int] = None) -> List[Path]:
        """Get all log files in the log directory, sorted by date (newest first)."""
        if limit is not None and limit < 0:
            raise ValueError("limit must be a positive integer")
        
        if not self.log_dir.exists():
            return []

        log_files = sorted(
            self.log_dir.glob("*.log"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        return log_files[:limit] if limit else log_files

    def parse_log_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse a single log file and extract log entries."""
        import logging
        logger = logging.getLogger(__name__)
        
        entries = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    entry = self._parse_log_line(line, file_path.name, line_num)
                    if entry:
                        entries.append(entry)
        except (IOError, OSError) as e:
            logger.error(f"Error parsing {file_path}: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Unexpected error parsing {file_path}: {e}", exc_info=True)

        return entries

    def _parse_log_line(self, line: str, filename: str, line_num: int) -> Optional[Dict[str, Any]]:
        """Parse a single log line using regex patterns."""
        for pattern_name, pattern in self.LOG_PATTERNS.items():
            try:
                match = re.search(pattern, line)
                if match:
                    groups = match.groupdict()
                    return {
                        "timestamp": groups.get("timestamp", ""),
                        "level": groups.get("level", "INFO").upper(),
                        "logger": groups.get("logger", ""),
                        "message": groups.get("message", line),
                        "file": filename,
                        "line_num": line_num,
                        "raw": line,
                    }
            except Exception:
                continue

        # Fallback: return the entire line as message
        return {
            "timestamp": "",
            "level": "INFO",
            "logger": "",
            "message": line,
            "file": filename,
            "line_num": line_num,
            "raw": line,
        }

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
        all_entries = self.parse_all_logs(limit=limit)
        query_lower = query.lower()
        results = [
            entry for entry in all_entries
            if query_lower in entry.get("message", "").lower()
            or query_lower in entry.get("logger", "").lower()
        ]
        return results

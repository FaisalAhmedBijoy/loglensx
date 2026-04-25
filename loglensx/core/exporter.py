"""
Export helpers for log entries.
"""

import csv
import json
from io import StringIO
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


class LogExporter:
    """Serialize parsed log entries to common interchange formats."""

    DEFAULT_FIELDS = ["timestamp", "level", "logger", "message", "file", "line_num", "raw"]
    SUPPORTED_FORMATS = {"json", "csv", "ndjson"}

    @classmethod
    def export(
        cls,
        entries: Iterable[Dict[str, Any]],
        format: str = "json",
        output_path: Optional[str] = None,
    ) -> str:
        """Serialize entries and optionally write the result to disk."""
        normalized_format = cls._normalize_format(format)
        entry_list = list(entries)

        if normalized_format == "json":
            payload = cls.to_json(entry_list)
        elif normalized_format == "csv":
            payload = cls.to_csv(entry_list)
        else:
            payload = cls.to_ndjson(entry_list)

        if output_path:
            Path(output_path).write_text(payload, encoding="utf-8")

        return payload

    @staticmethod
    def to_json(entries: Iterable[Dict[str, Any]], indent: int = 2) -> str:
        """Serialize entries to JSON."""
        return json.dumps(list(entries), indent=indent, default=str)

    @classmethod
    def to_csv(
        cls,
        entries: Iterable[Dict[str, Any]],
        fieldnames: Optional[List[str]] = None,
    ) -> str:
        """Serialize entries to CSV with a stable, useful field order."""
        entry_list = list(entries)
        fields = fieldnames or cls._fieldnames(entry_list)

        buffer = StringIO()
        writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for entry in entry_list:
            writer.writerow(cls._flatten_entry(entry))

        return buffer.getvalue()

    @staticmethod
    def to_ndjson(entries: Iterable[Dict[str, Any]]) -> str:
        """Serialize entries to newline-delimited JSON."""
        return "\n".join(json.dumps(entry, default=str) for entry in entries)

    @classmethod
    def _fieldnames(cls, entries: List[Dict[str, Any]]) -> List[str]:
        extra_fields = sorted(
            {
                key
                for entry in entries
                for key in cls._flatten_entry(entry).keys()
                if key not in cls.DEFAULT_FIELDS
            }
        )
        return cls.DEFAULT_FIELDS + extra_fields

    @staticmethod
    def _flatten_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten common structured-log extras for CSV export."""
        flattened = dict(entry)
        extra = flattened.pop("extra", None)
        if isinstance(extra, dict):
            for key, value in extra.items():
                flattened[f"extra.{key}"] = value

        for key, value in list(flattened.items()):
            if isinstance(value, (dict, list, tuple)):
                flattened[key] = json.dumps(value, default=str, sort_keys=True)

        return flattened

    @classmethod
    def _normalize_format(cls, format: str) -> str:
        normalized = (format or "json").lower()
        if normalized not in cls.SUPPORTED_FORMATS:
            supported = ", ".join(sorted(cls.SUPPORTED_FORMATS))
            raise ValueError(f"Unsupported export format '{format}'. Use one of: {supported}")
        return normalized

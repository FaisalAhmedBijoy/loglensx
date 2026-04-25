"""Command line interface for loglensx."""

import argparse
import json
import logging
import sys
from typing import Any, Dict, List, Optional

from .core.analyzer import LogAnalyzer
from .core.exporter import LogExporter
from .core.parser import LogParser


logging.basicConfig(level=logging.INFO, format="%(message)s")

COMMANDS = {"summary", "logs", "files", "patterns"}


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point. Returns exit code."""
    try:
        args = build_arg_parser().parse_args(_normalize_argv(argv))
        parser = LogParser(log_dir=args.log_dir)
        analyzer = LogAnalyzer(parser)

        if args.command == "summary":
            return _summary_command(analyzer, args)
        if args.command == "logs":
            return _logs_command(analyzer, args)
        if args.command == "files":
            return _files_command(analyzer, args)
        if args.command == "patterns":
            return _patterns_command(analyzer, args)

        raise ValueError(f"Unknown command: {args.command}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        logging.debug("Unexpected error in CLI", exc_info=True)
        return 1


def build_arg_parser() -> argparse.ArgumentParser:
    """Build the command parser while preserving the historical default summary."""
    arg_parser = argparse.ArgumentParser(
        prog="loglensx",
        description="Inspect, filter, and export Python application logs.",
    )
    subparsers = arg_parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--log-dir", default="logs", help="Directory containing .log files.")

    time_filters = argparse.ArgumentParser(add_help=False)
    time_filters.add_argument("--since", help="Start timestamp, for example 2024-01-15T10:30:00.")
    time_filters.add_argument("--until", help="End timestamp, for example 2024-01-15T11:00:00.")
    time_filters.add_argument("--file", dest="source_file", help="Filter by log file name.")

    summary = subparsers.add_parser(
        "summary",
        parents=[common, time_filters],
        help="Print a summary of parsed logs.",
    )
    summary.add_argument("--format", choices=["text", "json"], default="text")

    logs = subparsers.add_parser(
        "logs",
        parents=[common, time_filters],
        help="List or export filtered log entries.",
    )
    logs.add_argument("--level", help="Filter by a log level such as ERROR or WARNING.")
    logs.add_argument("--logger", help="Filter by logger name.")
    logs.add_argument("--search", help="Search messages, loggers, files, and raw text.")
    logs.add_argument("--limit", type=int, default=100, help="Maximum number of rows to return.")
    logs.add_argument("--format", choices=["text", "json", "csv", "ndjson"], default="text")
    logs.add_argument("--output", help="Write exported JSON, CSV, or NDJSON to this file.")

    files = subparsers.add_parser(
        "files",
        parents=[common],
        help="Show indexed log files and parsed entry counts.",
    )
    files.add_argument("--format", choices=["text", "json"], default="text")

    patterns = subparsers.add_parser(
        "patterns",
        parents=[common],
        help="Group recurring critical/error messages.",
    )
    patterns.add_argument("--limit", type=int, default=10)
    patterns.add_argument("--format", choices=["text", "json"], default="text")

    return arg_parser


def _normalize_argv(argv: Optional[List[str]]) -> List[str]:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] in {"-h", "--help"}:
        return args
    if not args or args[0] not in COMMANDS:
        return ["summary"] + args
    return args


def _summary_command(analyzer: LogAnalyzer, args: argparse.Namespace) -> int:
    summary = analyzer.get_log_summary(
        since=args.since,
        until=args.until,
        source_file=args.source_file,
    )
    if args.format == "json":
        print(json.dumps(summary, indent=2, default=str))
        return 0

    print("\n" + "=" * 60)
    print("                   loglensx Summary                    ")
    print("=" * 60)
    print(f"Total Logs:         {summary.get('total_logs', 0)}")
    print(f"Critical:           {summary.get('critical_count', 0)}")
    print(f"Errors:             {summary.get('error_count', 0)}")
    print(f"Warnings:           {summary.get('warning_count', 0)}")
    print(f"Info:               {summary.get('info_count', 0)}")
    print(f"Debug:              {summary.get('debug_count', 0)}")
    print(f"Unique Loggers:     {summary.get('unique_loggers', 0)}")
    print(f"Log Files:          {summary.get('files', 0)}")
    if summary.get("first_timestamp") or summary.get("last_timestamp"):
        print(f"First Timestamp:    {summary.get('first_timestamp') or 'N/A'}")
        print(f"Last Timestamp:     {summary.get('last_timestamp') or 'N/A'}")
    print("=" * 60 + "\n")

    recent_errors = analyzer.get_recent_errors(
        limit=5,
        since=args.since,
        until=args.until,
        source_file=args.source_file,
    )
    if recent_errors:
        print("Recent Critical/Error Entries:")
        for index, error in enumerate(recent_errors, 1):
            print(f"{index}. {_format_entry_line(error)}")
    print()
    return 0


def _logs_command(analyzer: LogAnalyzer, args: argparse.Namespace) -> int:
    if args.limit < 1:
        raise ValueError("limit must be a positive integer")

    logs = analyzer.filter_logs(
        level=args.level,
        logger=args.logger,
        search_term=args.search,
        source_file=args.source_file,
        since=args.since,
        until=args.until,
        limit=args.limit,
    )

    if args.format == "text":
        if not logs:
            print("No log entries matched the current filters.")
            return 0
        for entry in logs:
            print(_format_entry_line(entry))
        return 0

    payload = LogExporter.export(logs, format=args.format, output_path=args.output)
    if args.output:
        print(f"Wrote {len(logs)} log entries to {args.output}")
    else:
        print(payload)
    return 0


def _files_command(analyzer: LogAnalyzer, args: argparse.Namespace) -> int:
    files = analyzer.get_file_statistics()
    if args.format == "json":
        print(json.dumps(files, indent=2, default=str))
        return 0

    if not files:
        print(f"No .log files found in {analyzer.parser.log_dir}")
        return 0

    for item in files:
        modified = item.get("modified", "")
        print(
            "{name}  {entries} entries  {size} bytes  modified={modified}".format(
                name=item.get("name", ""),
                entries=item.get("entries", 0),
                size=item.get("size", 0),
                modified=modified,
            )
        )
    return 0


def _patterns_command(analyzer: LogAnalyzer, args: argparse.Namespace) -> int:
    if args.limit < 1:
        raise ValueError("limit must be a positive integer")

    patterns = analyzer.get_error_patterns(limit=args.limit)
    if args.format == "json":
        print(json.dumps(patterns, indent=2, default=str))
        return 0

    if not patterns:
        print("No critical/error patterns found.")
        return 0

    for index, item in enumerate(patterns, 1):
        print(
            f"{index}. x{item.get('count', 0)} [{item.get('level', 'ERROR')}] {item.get('pattern', '')}"
        )
        print(f"   example: {_shorten(item.get('example', ''))}")
    return 0


def _format_entry_line(entry: Dict[str, Any]) -> str:
    timestamp = entry.get("timestamp") or "no timestamp"
    level = entry.get("level") or "INFO"
    logger = entry.get("logger") or "root"
    source = entry.get("file") or "unknown"
    if entry.get("line_num"):
        source = f"{source}:{entry.get('line_num')}"
    message = _shorten(entry.get("message", ""))
    return f"[{timestamp}] [{level}] [{logger}] {message} ({source})"


def _shorten(value: Any, limit: int = 160) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


if __name__ == "__main__":
    sys.exit(main())

"""Quick start CLI for LogLens."""

import sys
import logging
from .core.parser import LogParser
from .core.analyzer import LogAnalyzer

# Setup logging for CLI
logging.basicConfig(level=logging.INFO, format='%(message)s')


def main() -> int:
    """Main CLI entry point. Returns exit code."""
    try:
        parser = LogParser()
        analyzer = LogAnalyzer(parser)

        # Get summary
        summary = analyzer.get_log_summary()

        print("\n" + "=" * 60)
        print("                   LogLens Summary                    ")
        print("=" * 60)
        print(f"Total Logs:         {summary.get('total_logs', 0)}")
        print(f"Errors:             {summary.get('error_count', 0)}")
        print(f"Warnings:           {summary.get('warning_count', 0)}")
        print(f"Info:               {summary.get('info_count', 0)}")
        print(f"Debug:              {summary.get('debug_count', 0)}")
        print(f"Unique Loggers:     {summary.get('unique_loggers', 0)}")
        print(f"Log Files:          {summary.get('files', 0)}")
        print("=" * 60 + "\n")

        # Show recent errors
        recent_errors = analyzer.get_recent_errors(limit=5)
        if recent_errors:
            print("Recent Errors:")
            for i, error in enumerate(recent_errors, 1):
                print(f"{i}. {error.get('message', 'N/A')[:80]}")
        print()
        return 0
    except FileNotFoundError:
        print("Error: logs directory not found. Please ensure logs are being generated.")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Unexpected error in CLI: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

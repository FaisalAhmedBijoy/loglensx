"""
Table generation for log data display.
"""

from collections import Counter
from html import escape
from typing import Any, Dict, List, Optional


class TableGenerator:
    """Generate HTML tables for log data."""

    LEVEL_CLASSES = {
        "CRITICAL": "llx-badge-critical",
        "ERROR": "llx-badge-error",
        "WARNING": "llx-badge-warning",
        "INFO": "llx-badge-info",
        "DEBUG": "llx-badge-debug",
        "TRACE": "llx-badge-debug",
    }

    @classmethod
    def _level_badge(cls, level: str) -> str:
        """Render a colored level badge."""
        badge_class = cls.LEVEL_CLASSES.get(level, "llx-badge-default")
        return f'<span class="llx-badge {badge_class}">{escape(level)}</span>'

    @staticmethod
    def _message_cell(message: str) -> str:
        """Render a message cell with graceful expansion for long entries."""
        message = str(message or "")
        safe_message = escape(message)
        preview = escape(message[:140])
        if len(message) <= 140:
            return f'<div class="llx-message-preview">{safe_message}</div>'

        return f"""
        <details>
            <summary class="llx-message-summary">{preview}...</summary>
            <div class="llx-message-full">{safe_message}</div>
        </details>
        """

    @classmethod
    def _summary_cards(cls, entries: List[Dict[str, Any]]) -> str:
        """Render summary cards for the current log slice."""
        level_counts = Counter(str(entry.get("level", "INFO")).upper() for entry in entries)
        ordered_levels = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]

        cards = [
            """
            <div class="llx-summary-tile">
                <div class="llx-summary-label">Visible Logs</div>
                <div class="llx-summary-value" data-table-count>{}</div>
            </div>
            """.format(
                len(entries)
            )
        ]

        for level in ordered_levels:
            cards.append(
                """
                <div class="llx-summary-tile">
                    <div class="llx-summary-label">{level}</div>
                    <div class="llx-summary-value">{count}</div>
                </div>
                """.format(
                    level=escape(level),
                    count=level_counts.get(level, 0),
                )
            )

        return '<div class="llx-table-summary">' + "".join(cards) + "</div>"

    @staticmethod
    def _sort_header(label: str, key: str) -> str:
        """Render a sortable table header button."""
        return (
            f'<button type="button" class="llx-sort-button" data-sort="{escape(key, quote=True)}">'
            f'{escape(label)} <span class="llx-sort-indicator" aria-hidden="true"></span>'
            "</button>"
        )

    @staticmethod
    def logs_to_html_table(
        entries: List[Dict[str, Any]], title: str = "Logs", max_rows: Optional[int] = None
    ) -> str:
        """Convert log entries to HTML table."""
        if max_rows:
            entries = entries[:max_rows]

        if not entries:
            return f"""
            <section class="llx-table-card">
                <div class="llx-table-header">
                    <div>
                        <p class="eyebrow">Table</p>
                        <h2>{escape(title)}</h2>
                    </div>
                </div>
                <div class="empty-state">
                    <div>
                        <strong>No log entries</strong>
                        <span>No rows matched the current filters.</span>
                    </div>
                </div>
            </section>
            """

        summary_html = TableGenerator._summary_cards(entries)
        html = f"""
        <section class="llx-table-card" data-log-table>
            <div class="llx-table-header">
                <div>
                    <p class="eyebrow">Table</p>
                    <h2>{escape(title)}</h2>
                </div>
                <div class="llx-table-tools">
                    <input type="search" data-table-search aria-label="Filter table rows" placeholder="Filter visible rows">
                    <select data-table-level aria-label="Filter by level">
                        <option value="">All levels</option>
                        <option value="CRITICAL">CRITICAL</option>
                        <option value="ERROR">ERROR</option>
                        <option value="WARNING">WARNING</option>
                        <option value="INFO">INFO</option>
                        <option value="DEBUG">DEBUG</option>
                    </select>
                    <button type="button" class="button button-secondary" data-table-clear>Reset</button>
                </div>
            </div>
            {summary_html}
            <div class="llx-table-scroll">
            <table class="llx-log-table">
                <thead>
                    <tr>
                        <th>{TableGenerator._sort_header("Timestamp", "timestamp")}</th>
                        <th>{TableGenerator._sort_header("Level", "level")}</th>
                        <th>{TableGenerator._sort_header("Logger", "logger")}</th>
                        <th>{TableGenerator._sort_header("Message", "message")}</th>
                        <th>{TableGenerator._sort_header("Source", "source")}</th>
                    </tr>
                </thead>
                <tbody>
        """

        for entry in entries:
            level = str(entry.get("level", "INFO")).upper()
            timestamp_raw = str(entry.get("timestamp", ""))
            logger_raw = str(entry.get("logger", ""))
            message_raw = str(entry.get("message", ""))
            file_raw = str(entry.get("file", ""))
            line_num_raw = str(entry.get("line_num", ""))

            timestamp = escape(timestamp_raw)
            logger = escape(logger_raw)
            message = TableGenerator._message_cell(entry.get("message", ""))
            file = escape(file_raw)
            line_num = escape(line_num_raw)
            source_raw = file_raw if not line_num_raw else f"{file_raw}:{line_num_raw}"
            source = escape(source_raw)
            row_search = " ".join(
                [timestamp_raw, level, logger_raw, message_raw, source_raw]
            ).lower()

            html += f"""
                    <tr
                        data-level="{escape(level, quote=True)}"
                        data-timestamp="{escape(timestamp_raw, quote=True)}"
                        data-logger="{escape(logger_raw or 'root', quote=True)}"
                        data-message="{escape(message_raw, quote=True)}"
                        data-source="{escape(source_raw, quote=True)}"
                        data-search="{escape(row_search, quote=True)}"
                    >
                        <td class="llx-cell-timestamp">{timestamp}</td>
                        <td>{TableGenerator._level_badge(level)}</td>
                        <td class="llx-cell-logger">{logger or '<span class="llx-empty-logger">root</span>'}</td>
                        <td class="llx-cell-message">{message}</td>
                        <td class="llx-cell-source">{source}</td>
                    </tr>
            """

        html += """
                </tbody>
            </table>
            </div>
        </section>
        """

        return html

    @staticmethod
    def dict_to_html_table(data: Dict[str, Any], title: str = "Data") -> str:
        """Convert a dictionary to HTML table."""
        html = f"""
        <section class="llx-table-card">
            <div class="llx-table-header">
                <div>
                    <p class="eyebrow">Table</p>
                    <h2>{escape(title)}</h2>
                </div>
            </div>
            <div class="llx-table-scroll">
            <table class="llx-log-table">
                <tbody>
        """

        for key, value in data.items():
            html += f"""
                    <tr>
                        <td class="llx-cell-logger">{escape(str(key))}</td>
                        <td class="llx-cell-message">{escape(str(value))}</td>
                    </tr>
            """

        html += """
                </tbody>
            </table>
            </div>
        </section>
        """

        return html

    @staticmethod
    def statistics_to_html(stats: Dict[str, Any]) -> str:
        """Convert statistics to HTML display."""
        html = '<section class="metrics-grid">'

        for key, value in stats.items():
            html += f"""
            <article class="metric-card">
                <div class="metric-label">{escape(str(key).replace('_', ' ').title())}</div>
                <div class="metric-value">{escape(str(value))}</div>
            </article>
            """

        html += "</section>"
        return html

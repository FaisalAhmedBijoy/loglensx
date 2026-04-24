"""
Table generation for log data display.
"""

from typing import List, Dict, Any, Optional
from html import escape
from collections import Counter


class TableGenerator:
    """Generate HTML tables for log data."""

    LEVEL_STYLES = {
        "ERROR": {"bg": "#fee2e2", "fg": "#991b1b"},
        "WARNING": {"bg": "#fef3c7", "fg": "#92400e"},
        "INFO": {"bg": "#dbeafe", "fg": "#1d4ed8"},
        "DEBUG": {"bg": "#e5e7eb", "fg": "#374151"},
    }

    @classmethod
    def _level_badge(cls, level: str) -> str:
        """Render a colored level badge."""
        styles = cls.LEVEL_STYLES.get(level, {"bg": "#ede9fe", "fg": "#5b21b6"})
        return (
            f"<span style=\"display:inline-flex;align-items:center;padding:4px 10px;"
            f"border-radius:999px;font-size:11px;font-weight:700;letter-spacing:0.04em;"
            f"background:{styles['bg']};color:{styles['fg']};\">{escape(level)}</span>"
        )

    @staticmethod
    def _message_cell(message: str) -> str:
        """Render a message cell with graceful expansion for long entries."""
        safe_message = escape(message)
        preview = safe_message[:140]
        if len(safe_message) <= 140:
            return f"<div style=\"white-space:pre-wrap;word-break:break-word;\">{safe_message}</div>"

        return f"""
        <details>
            <summary style="cursor:pointer;color:#0f172a;font-weight:600;">{preview}...</summary>
            <div style="margin-top:8px;white-space:pre-wrap;word-break:break-word;color:#334155;">{safe_message}</div>
        </details>
        """

    @classmethod
    def _summary_cards(cls, entries: List[Dict[str, Any]]) -> str:
        """Render summary cards for the current log slice."""
        level_counts = Counter(entry.get("level", "INFO").upper() for entry in entries)
        ordered_levels = ["ERROR", "WARNING", "INFO", "DEBUG"]

        cards = [
            """
            <div style="padding:16px 18px;border-radius:16px;background:#0f172a;color:#f8fafc;">
                <div style="font-size:12px;opacity:0.75;text-transform:uppercase;letter-spacing:0.08em;">Visible Logs</div>
                <div style="font-size:28px;font-weight:800;margin-top:6px;">{}</div>
            </div>
            """.format(len(entries))
        ]

        for level in ordered_levels:
            cards.append(
                """
                <div style="padding:16px 18px;border-radius:16px;background:#ffffff;border:1px solid #e2e8f0;">
                    <div>{badge}</div>
                    <div style="font-size:24px;font-weight:800;margin-top:10px;color:#0f172a;">{count}</div>
                </div>
                """.format(
                    badge=cls._level_badge(level),
                    count=level_counts.get(level, 0),
                )
            )

        return (
            "<div style=\"display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));"
            "gap:12px;margin-bottom:18px;\">"
            + "".join(cards)
            + "</div>"
        )

    @staticmethod
    def logs_to_html_table(
        entries: List[Dict[str, Any]],
        title: str = "Logs",
        max_rows: Optional[int] = None
    ) -> str:
        """Convert log entries to HTML table."""
        if max_rows:
            entries = entries[:max_rows]

        if not entries:
            return f"""
            <section style="background:#ffffff;border:1px solid #e2e8f0;border-radius:20px;padding:24px;">
                <h3 style="font-size:22px;color:#0f172a;margin-bottom:8px;">{escape(title)}</h3>
                <p style="color:#64748b;">No log entries matched the current filters.</p>
            </section>
            """

        summary_html = TableGenerator._summary_cards(entries)
        html = f"""
        <section style="background:#ffffff;border:1px solid #e2e8f0;border-radius:20px;padding:24px;box-shadow:0 20px 45px rgba(15,23,42,0.08);">
            <div style="display:flex;justify-content:space-between;align-items:flex-end;gap:12px;flex-wrap:wrap;margin-bottom:18px;">
                <div>
                    <h3 style="font-size:22px;color:#0f172a;margin:0;">{escape(title)}</h3>
                    <p style="margin:6px 0 0;color:#64748b;">Scan recent activity, inspect long messages, and trace each line back to its source file.</p>
                </div>
            </div>
            {summary_html}
            <div style="overflow-x:auto;border:1px solid #e2e8f0;border-radius:16px;">
            <table style="border-collapse:separate;border-spacing:0;width:100%;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;background:#ffffff;">
                <thead>
                    <tr style="background:#f8fafc;color:#334155;">
                        <th style="padding:14px 16px;text-align:left;border-bottom:1px solid #e2e8f0;">Timestamp</th>
                        <th style="padding:14px 16px;text-align:left;border-bottom:1px solid #e2e8f0;">Level</th>
                        <th style="padding:14px 16px;text-align:left;border-bottom:1px solid #e2e8f0;">Logger</th>
                        <th style="padding:14px 16px;text-align:left;border-bottom:1px solid #e2e8f0;">Message</th>
                        <th style="padding:14px 16px;text-align:left;border-bottom:1px solid #e2e8f0;">Source</th>
                    </tr>
                </thead>
                <tbody>
        """

        for entry in entries:
            level = entry.get("level", "INFO").upper()
            timestamp = escape(entry.get("timestamp", ""))
            logger = escape(entry.get("logger", ""))
            message = TableGenerator._message_cell(entry.get("message", ""))
            file = escape(entry.get("file", ""))
            line_num = escape(str(entry.get("line_num", "")))
            source = file if not line_num else f"{file}:{line_num}"

            html += f"""
                    <tr style="border-bottom:1px solid #e2e8f0;">
                        <td style="padding:16px;border-bottom:1px solid #e2e8f0;color:#475569;white-space:nowrap;">{timestamp}</td>
                        <td style="padding:16px;border-bottom:1px solid #e2e8f0;">{TableGenerator._level_badge(level)}</td>
                        <td style="padding:16px;border-bottom:1px solid #e2e8f0;color:#0f172a;">{logger or '<span style="color:#94a3b8;">root</span>'}</td>
                        <td style="padding:16px;border-bottom:1px solid #e2e8f0;color:#0f172a;min-width:320px;">{message}</td>
                        <td style="padding:16px;border-bottom:1px solid #e2e8f0;color:#475569;white-space:nowrap;">{source}</td>
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
        <div style="margin: 20px 0;">
            <h3>{title}</h3>
            <table style="border-collapse: collapse; font-family: sans-serif;">
                <tbody>
        """

        for key, value in data.items():
            html += f"""
                    <tr style="border-bottom: 1px solid #dee2e6;">
                        <td style="padding: 8px; font-weight: bold; background-color: #f8f9fa;">{key}</td>
                        <td style="padding: 8px;">{value}</td>
                    </tr>
            """

        html += """
                </tbody>
            </table>
        </div>
        """

        return html

    @staticmethod
    def statistics_to_html(stats: Dict[str, Any]) -> str:
        """Convert statistics to HTML display."""
        html = """
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
        """

        for key, value in stats.items():
            html += f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center;">
                <div style="font-size: 24px; font-weight: bold;">{value}</div>
                <div style="font-size: 12px; margin-top: 5px; opacity: 0.9;">{key}</div>
            </div>
            """

        html += "</div>"
        return html

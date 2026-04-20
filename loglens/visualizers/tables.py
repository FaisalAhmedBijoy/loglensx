"""
Table generation for log data display.
"""

from typing import List, Dict, Any, Optional
from html import escape


class TableGenerator:
    """Generate HTML tables for log data."""

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
            return f"<p>{title} - No entries found</p>"

        # Build HTML table
        html = f"""
        <div style="overflow-x: auto;">
            <h3>{title}</h3>
            <table style="border-collapse: collapse; width: 100%; font-family: monospace; font-size: 12px;">
                <thead>
                    <tr style="background-color: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                        <th style="padding: 8px; text-align: left; border: 1px solid #dee2e6;">Timestamp</th>
                        <th style="padding: 8px; text-align: left; border: 1px solid #dee2e6;">Level</th>
                        <th style="padding: 8px; text-align: left; border: 1px solid #dee2e6;">Logger</th>
                        <th style="padding: 8px; text-align: left; border: 1px solid #dee2e6;">Message</th>
                        <th style="padding: 8px; text-align: left; border: 1px solid #dee2e6;">File</th>
                    </tr>
                </thead>
                <tbody>
        """

        level_colors = {
            "ERROR": "#ffe6e6",
            "WARNING": "#fff3e0",
            "INFO": "#e3f2fd",
            "DEBUG": "#f5f5f5",
        }

        for entry in entries:
            level = entry.get("level", "INFO")
            bg_color = level_colors.get(level, "#ffffff")
            timestamp = escape(entry.get("timestamp", ""))
            logger = escape(entry.get("logger", ""))
            message = escape(entry.get("message", ""))[:100]  # Truncate long messages
            file = escape(entry.get("file", ""))

            html += f"""
                    <tr style="background-color: {bg_color}; border-bottom: 1px solid #dee2e6;">
                        <td style="padding: 8px; border: 1px solid #dee2e6;">{timestamp}</td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;"><strong>{level}</strong></td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">{logger}</td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">{message}</td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">{file}</td>
                    </tr>
            """

        html += """
                </tbody>
            </table>
        </div>
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

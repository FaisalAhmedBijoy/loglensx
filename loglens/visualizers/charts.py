"""
Chart generation for log visualizations using Plotly.
"""

from typing import Dict, List, Any
import json as json_module

# Chart constants
CHART_HEIGHT = 400
COLOR_ERROR = "#dc3545"
COLOR_WARNING = "#ffc107"
COLOR_INFO = "#17a2b8"
COLOR_DEBUG = "#6c757d"
COLOR_DEFAULT = "#007bff"
COLOR_TRANSPARENT_ERROR = "rgba(220, 53, 69, 0.1)"


class ChartGenerator:
    """Generate interactive charts for log data."""

    @staticmethod
    def level_distribution_chart(level_stats: Dict[str, int]) -> Dict[str, Any]:
        """Generate a pie chart for log level distribution."""
        levels = list(level_stats.keys())
        counts = list(level_stats.values())

        return {
            "type": "pie",
            "data": {
                "labels": levels,
                "datasets": [
                    {
                        "data": counts,
                        "backgroundColor": [
                            COLOR_ERROR,
                            COLOR_WARNING,
                            COLOR_INFO,
                            COLOR_DEBUG,
                        ][:len(levels)],
                    }
                ]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {"position": "bottom"}
                }
            }
        }

    @staticmethod
    def error_timeline_chart(error_frequency: Dict[str, int]) -> Dict[str, Any]:
        """Generate a line chart for error frequency over time."""
        timestamps = list(error_frequency.keys())
        counts = list(error_frequency.values())

        return {
            "type": "line",
            "data": {
                "labels": timestamps,
                "datasets": [
                    {
                        "label": "Errors",
                        "data": counts,
                        "borderColor": COLOR_ERROR,
                        "backgroundColor": COLOR_TRANSPARENT_ERROR,
                        "tension": 0.4,
                        "fill": True,
                    }
                ]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {"display": True}
                },
                "scales": {
                    "y": {"beginAtZero": True}
                }
            }
        }

    @staticmethod
    def top_loggers_chart(top_loggers: List[tuple]) -> Dict[str, Any]:
        """Generate a bar chart for top loggers."""
        loggers = [item[0] for item in top_loggers]
        counts = [item[1] for item in top_loggers]

        return {
            "type": "bar",
            "data": {
                "labels": loggers,
                "datasets": [
                    {
                        "label": "Log Count",
                        "data": counts,
                        "backgroundColor": "#007bff",
                    }
                ]
            },
            "options": {
                "responsive": True,
                "indexAxis": "y",
                "plugins": {
                    "legend": {"display": False}
                },
                "scales": {
                    "x": {"beginAtZero": True}
                }
            }
        }

    @staticmethod
    def plotly_level_distribution(level_stats: Dict[str, int]) -> str:
        """Generate Plotly JSON for level distribution."""
        levels = list(level_stats.keys())
        counts = list(level_stats.values())

        color_map = {
            "ERROR": COLOR_ERROR,
            "WARNING": COLOR_WARNING,
            "INFO": COLOR_INFO,
            "DEBUG": COLOR_DEBUG,
        }

        colors = [color_map.get(level, COLOR_DEFAULT) for level in levels]

        figure = {
            "data": [
                {
                    "labels": levels,
                    "values": counts,
                    "type": "pie",
                    "marker": {"colors": colors},
                }
            ],
            "layout": {
                "title": "Log Level Distribution",
                "height": CHART_HEIGHT,
            }
        }

        return json_module.dumps(figure)

    @staticmethod
    def plotly_error_timeline(error_frequency: Dict[str, int]) -> str:
        """Generate Plotly JSON for error timeline."""
        timestamps = list(error_frequency.keys())
        counts = list(error_frequency.values())

        figure = {
            "data": [
                {
                    "x": timestamps,
                    "y": counts,
                    "type": "scatter",
                    "mode": "lines+markers",
                    "line": {"color": COLOR_ERROR},
                    "name": "Errors",
                }
            ],
            "layout": {
                "title": "Error Frequency Over Time",
                "xaxis": {"title": "Time"},
                "yaxis": {"title": "Error Count"},
                "height": CHART_HEIGHT,
            }
        }

        return json_module.dumps(figure)

    @staticmethod
    def plotly_top_loggers(top_loggers: List[tuple]) -> str:
        """Generate Plotly JSON for top loggers."""
        loggers = [item[0] for item in top_loggers]
        counts = [item[1] for item in top_loggers]

        figure = {
            "data": [
                {
                    "x": counts,
                    "y": loggers,
                    "type": "bar",
                    "marker": {"color": COLOR_DEFAULT},
                    "orientation": "h",
                }
            ],
            "layout": {
                "title": "Top 10 Loggers by Log Count",
                "xaxis": {"title": "Log Count"},
                "height": CHART_HEIGHT,
            }
        }

        return json_module.dumps(figure)

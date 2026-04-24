"""
Chart generation for log visualizations using Plotly.
"""

import json as json_module
from typing import Any, Dict, List

# Chart constants
CHART_HEIGHT = 420
COLOR_ERROR = "#dc2626"
COLOR_WARNING = "#d97706"
COLOR_INFO = "#0284c7"
COLOR_DEBUG = "#475569"
COLOR_DEFAULT = "#2563eb"
COLOR_SUCCESS = "#059669"
COLOR_TRANSPARENT_ERROR = "rgba(220, 38, 38, 0.10)"
GRID_COLOR = "#e5edf7"
TEXT_COLOR = "#334155"

LEVEL_COLORS = {
    "ERROR": COLOR_ERROR,
    "WARNING": COLOR_WARNING,
    "INFO": COLOR_INFO,
    "DEBUG": COLOR_DEBUG,
}


class ChartGenerator:
    """Generate interactive charts for log data."""

    @staticmethod
    def _level_colors(levels: List[str]) -> List[str]:
        """Return colors for log levels in the supplied order."""
        return [LEVEL_COLORS.get(level, COLOR_DEFAULT) for level in levels]

    @staticmethod
    def _plotly_layout(title: str, height: int = CHART_HEIGHT) -> Dict[str, Any]:
        """Common Plotly layout for dashboard visualizations."""
        return {
            "title": {"text": title, "font": {"size": 16}},
            "height": height,
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "#ffffff",
            "font": {"family": "Inter, system-ui, sans-serif", "color": TEXT_COLOR},
            "margin": {"t": 56, "r": 28, "b": 56, "l": 64},
            "hoverlabel": {
                "bgcolor": "#111827",
                "bordercolor": "#111827",
                "font": {"color": "#ffffff"},
            },
            "legend": {"orientation": "h", "y": 1.08, "x": 1, "xanchor": "right"},
        }

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
                        "backgroundColor": ChartGenerator._level_colors(levels),
                        "borderColor": "#ffffff",
                        "borderWidth": 2,
                        "hoverOffset": 8,
                    }
                ]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "cutout": "62%",
                "plugins": {
                    "legend": {"position": "bottom"},
                    "tooltip": {"enabled": True},
                },
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
                        "pointRadius": 4,
                        "pointHoverRadius": 7,
                    }
                ]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {"display": True}
                },
                "scales": {
                    "x": {"grid": {"color": GRID_COLOR}},
                    "y": {"beginAtZero": True, "grid": {"color": GRID_COLOR}},
                },
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
                        "backgroundColor": COLOR_DEFAULT,
                        "borderRadius": 6,
                    }
                ]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "indexAxis": "y",
                "plugins": {
                    "legend": {"display": False}
                },
                "scales": {
                    "x": {"beginAtZero": True, "grid": {"color": GRID_COLOR}},
                    "y": {"grid": {"display": False}},
                },
            }
        }

    @staticmethod
    def plotly_level_distribution(level_stats: Dict[str, int]) -> str:
        """Generate Plotly JSON for level distribution."""
        levels = list(level_stats.keys())
        counts = list(level_stats.values())

        figure = {
            "data": [
                {
                    "labels": levels,
                    "values": counts,
                    "type": "pie",
                    "hole": 0.62,
                    "sort": False,
                    "marker": {
                        "colors": ChartGenerator._level_colors(levels),
                        "line": {"color": "#ffffff", "width": 3},
                    },
                    "textinfo": "label+percent",
                    "hovertemplate": "<b>%{label}</b><br>%{value} entries<br>%{percent}<extra></extra>",
                }
            ],
            "layout": {
                **ChartGenerator._plotly_layout("Log Level Distribution"),
                "margin": {"t": 46, "r": 16, "b": 20, "l": 16},
            },
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
                    "line": {
                        "color": COLOR_ERROR,
                        "width": 3,
                        "shape": "spline",
                        "smoothing": 1.1,
                    },
                    "marker": {
                        "size": 7,
                        "color": "#ffffff",
                        "line": {"color": COLOR_ERROR, "width": 2},
                    },
                    "fill": "tozeroy",
                    "fillcolor": COLOR_TRANSPARENT_ERROR,
                    "name": "Errors",
                    "hovertemplate": "<b>%{x}</b><br>%{y} errors<extra></extra>",
                }
            ],
            "layout": {
                **ChartGenerator._plotly_layout("Error Frequency Over Time"),
                "xaxis": {"title": "", "gridcolor": GRID_COLOR},
                "yaxis": {"title": "Error Count", "rangemode": "tozero", "gridcolor": GRID_COLOR},
            },
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
                    "marker": {
                        "color": counts,
                        "colorscale": [[0, "#bfdbfe"], [0.55, "#38bdf8"], [1, COLOR_DEFAULT]],
                        "line": {"color": "#ffffff", "width": 1},
                    },
                    "orientation": "h",
                    "hovertemplate": "<b>%{y}</b><br>%{x} entries<extra></extra>",
                }
            ],
            "layout": {
                **ChartGenerator._plotly_layout("Top Loggers by Log Count"),
                "xaxis": {"title": "Log Count", "rangemode": "tozero", "gridcolor": GRID_COLOR},
                "yaxis": {"title": "", "automargin": True},
                "showlegend": False,
            },
        }

        return json_module.dumps(figure)

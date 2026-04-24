"""
Shared HTML, CSS, and JavaScript for the FastAPI and Flask dashboards.
"""

import json
from html import escape
from string import Template
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple
from urllib.parse import urlencode

from ..visualizers.tables import TableGenerator


PLOTLY_CDN = "https://cdn.plot.ly/plotly-latest.min.js"

DASHBOARD_STYLES = """
:root {
    --llx-bg: #f4f6fb;
    --llx-surface: #ffffff;
    --llx-surface-muted: #f8fafc;
    --llx-border: #dbe3ef;
    --llx-border-strong: #c7d2e2;
    --llx-text: #152238;
    --llx-muted: #64748b;
    --llx-soft: #eef4ff;
    --llx-primary: #2563eb;
    --llx-primary-dark: #1d4ed8;
    --llx-danger: #dc2626;
    --llx-danger-soft: #fee2e2;
    --llx-warning: #d97706;
    --llx-warning-soft: #fef3c7;
    --llx-info: #0284c7;
    --llx-info-soft: #e0f2fe;
    --llx-debug: #475569;
    --llx-debug-soft: #e2e8f0;
    --llx-success: #059669;
    --llx-success-soft: #d1fae5;
    --llx-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
    margin: 0;
    min-height: 100vh;
    color: var(--llx-text);
    background:
        linear-gradient(180deg, rgba(255,255,255,0.88), rgba(244,246,251,0.94)),
        radial-gradient(circle at top left, rgba(37,99,235,0.14), transparent 34%),
        var(--llx-bg);
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    line-height: 1.5;
}

a { color: inherit; }
button, input, select { font: inherit; }
[hidden] { display: none !important; }

.skip-link {
    position: absolute;
    left: 16px;
    top: -80px;
    z-index: 100;
    padding: 10px 14px;
    border-radius: 8px;
    background: var(--llx-primary);
    color: #ffffff;
    text-decoration: none;
    transition: top 0.2s ease;
}
.skip-link:focus { top: 16px; }

.app-shell {
    display: grid;
    grid-template-columns: 260px minmax(0, 1fr);
    min-height: 100vh;
}

.sidebar {
    position: sticky;
    top: 0;
    height: 100vh;
    padding: 28px 18px;
    border-right: 1px solid var(--llx-border);
    background: rgba(255,255,255,0.84);
    backdrop-filter: blur(16px);
}

.brand {
    display: flex;
    gap: 12px;
    align-items: center;
    padding: 0 10px 28px;
}
.brand-mark {
    width: 42px;
    height: 42px;
    display: inline-grid;
    place-items: center;
    border-radius: 12px;
    color: #ffffff;
    background: linear-gradient(135deg, #2563eb, #14b8a6);
    box-shadow: 0 12px 28px rgba(37, 99, 235, 0.22);
    font-weight: 800;
}
.brand-title { margin: 0; font-size: 18px; font-weight: 800; letter-spacing: 0; }
.brand-subtitle { margin: 2px 0 0; color: var(--llx-muted); font-size: 12px; }

.nav {
    display: grid;
    gap: 8px;
}
.nav a {
    display: flex;
    align-items: center;
    gap: 10px;
    min-height: 42px;
    padding: 10px 12px;
    border-radius: 8px;
    color: #334155;
    text-decoration: none;
    font-weight: 650;
    transition: background 0.18s ease, color 0.18s ease, transform 0.18s ease;
}
.nav a:hover,
.nav a.is-active {
    background: var(--llx-soft);
    color: var(--llx-primary-dark);
}
.nav-icon {
    width: 9px;
    height: 9px;
    border-radius: 999px;
    background: currentColor;
    opacity: 0.85;
}

.sidebar-footer {
    position: absolute;
    left: 18px;
    right: 18px;
    bottom: 24px;
    padding: 14px;
    border: 1px solid var(--llx-border);
    border-radius: 10px;
    color: var(--llx-muted);
    background: var(--llx-surface-muted);
    font-size: 12px;
}
.sidebar-footer code {
    display: block;
    margin-top: 6px;
    color: var(--llx-text);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.main {
    width: 100%;
    min-width: 0;
    padding: 32px;
}
.topbar {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 24px;
    margin-bottom: 22px;
}
.eyebrow {
    margin: 0 0 6px;
    color: var(--llx-primary);
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
h1, h2, h3, p { margin-top: 0; }
h1 {
    margin-bottom: 8px;
    font-size: clamp(30px, 4vw, 44px);
    line-height: 1.05;
    letter-spacing: 0;
}
h2 { margin-bottom: 0; font-size: 18px; letter-spacing: 0; }
h3 { letter-spacing: 0; }
.topbar p:not(.eyebrow) {
    max-width: 720px;
    margin-bottom: 0;
    color: var(--llx-muted);
}

.actions,
.form-actions,
.card-actions {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
}
.button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    min-height: 42px;
    padding: 10px 16px;
    border: 1px solid transparent;
    border-radius: 8px;
    background: var(--llx-primary);
    color: #ffffff;
    font-weight: 750;
    text-decoration: none;
    cursor: pointer;
    transition: transform 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;
    white-space: nowrap;
}
.button:hover {
    background: var(--llx-primary-dark);
    box-shadow: 0 12px 24px rgba(37, 99, 235, 0.18);
    transform: translateY(-1px);
}
.button-secondary {
    border-color: var(--llx-border-strong);
    background: var(--llx-surface);
    color: var(--llx-text);
}
.button-secondary:hover {
    background: var(--llx-surface-muted);
    color: var(--llx-primary-dark);
    box-shadow: none;
}

.icon {
    width: 17px;
    height: 17px;
    flex: 0 0 auto;
}

.command-panel,
.dashboard-card,
.llx-table-card {
    border: 1px solid var(--llx-border);
    border-radius: 10px;
    background: rgba(255,255,255,0.92);
    box-shadow: var(--llx-shadow);
}

.command-panel {
    margin-bottom: 22px;
    padding: 18px;
}
.filters {
    display: grid;
    grid-template-columns: minmax(220px, 1.5fr) minmax(160px, 0.8fr) minmax(180px, 1fr) minmax(120px, 0.55fr) auto;
    gap: 14px;
    align-items: end;
}
.field label,
.llx-field-label {
    display: block;
    margin-bottom: 7px;
    color: #475569;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.field input,
.field select,
.llx-table-tools input,
.llx-table-tools select {
    width: 100%;
    min-height: 42px;
    border: 1px solid var(--llx-border-strong);
    border-radius: 8px;
    padding: 9px 11px;
    color: var(--llx-text);
    background: #ffffff;
    outline: none;
    transition: border-color 0.16s ease, box-shadow 0.16s ease;
}
.field input:focus,
.field select:focus,
.llx-table-tools input:focus,
.llx-table-tools select:focus {
    border-color: var(--llx-primary);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(6, minmax(140px, 1fr));
    gap: 14px;
    margin-bottom: 22px;
}
.metric-card {
    min-height: 128px;
    padding: 18px;
    border: 1px solid var(--llx-border);
    border-radius: 10px;
    background: var(--llx-surface);
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
}
.metric-card.metric-danger { border-top: 4px solid var(--llx-danger); }
.metric-card.metric-warning { border-top: 4px solid var(--llx-warning); }
.metric-card.metric-info { border-top: 4px solid var(--llx-info); }
.metric-card.metric-success { border-top: 4px solid var(--llx-success); }
.metric-label {
    margin-bottom: 12px;
    color: var(--llx-muted);
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.metric-value {
    color: var(--llx-text);
    font-size: 30px;
    font-weight: 850;
    line-height: 1;
    letter-spacing: 0;
}
.metric-note {
    margin-top: 10px;
    color: var(--llx-muted);
    font-size: 13px;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: minmax(320px, 0.9fr) minmax(440px, 1.4fr);
    gap: 18px;
    margin-bottom: 18px;
}
.dashboard-grid-wide {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: 18px;
    margin-bottom: 18px;
}
.dashboard-card {
    min-width: 0;
    padding: 18px;
}
.card-header,
.llx-table-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 14px;
}
.card-header p,
.llx-table-header p {
    margin: 5px 0 0;
    color: var(--llx-muted);
    font-size: 13px;
}
.chart-container {
    width: 100%;
    min-height: 380px;
}
.chart-container.is-large { min-height: 430px; }
.empty-state {
    min-height: 240px;
    display: grid;
    place-items: center;
    gap: 4px;
    text-align: center;
    color: var(--llx-muted);
    border: 1px dashed var(--llx-border-strong);
    border-radius: 10px;
    background: var(--llx-surface-muted);
}
.empty-state strong {
    display: block;
    color: var(--llx-text);
}

.llx-table-card {
    padding: 18px;
    margin: 18px 0;
}
.llx-table-tools {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: flex-end;
    gap: 10px;
}
.llx-table-tools input { width: min(320px, 100%); }
.llx-table-tools select { width: 140px; }
.llx-table-summary {
    display: grid;
    grid-template-columns: repeat(5, minmax(110px, 1fr));
    gap: 10px;
    margin-bottom: 14px;
}
.llx-summary-tile {
    padding: 12px;
    border: 1px solid var(--llx-border);
    border-radius: 8px;
    background: var(--llx-surface-muted);
}
.llx-summary-label {
    margin-bottom: 6px;
    color: var(--llx-muted);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.llx-summary-value {
    font-size: 22px;
    font-weight: 850;
    line-height: 1;
}
.llx-table-scroll {
    overflow-x: auto;
    border: 1px solid var(--llx-border);
    border-radius: 10px;
    background: #ffffff;
}
.llx-log-table {
    width: 100%;
    min-width: 980px;
    border-collapse: separate;
    border-spacing: 0;
    background: #ffffff;
}
.llx-log-table th,
.llx-log-table td {
    padding: 13px 14px;
    border-bottom: 1px solid var(--llx-border);
    text-align: left;
    vertical-align: top;
}
.llx-log-table thead th {
    position: sticky;
    top: 0;
    z-index: 1;
    background: #f8fafc;
    color: #334155;
    font-size: 12px;
    font-weight: 850;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.llx-log-table tbody tr {
    transition: background 0.14s ease;
}
.llx-log-table tbody tr:hover { background: #f8fafc; }
.llx-log-table tbody tr:last-child td { border-bottom: 0; }
.llx-sort-button {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 0;
    border: 0;
    color: inherit;
    background: transparent;
    font-weight: inherit;
    letter-spacing: inherit;
    text-transform: inherit;
    cursor: pointer;
}
.llx-sort-indicator {
    color: var(--llx-muted);
    font-size: 10px;
}
.llx-cell-timestamp,
.llx-cell-source {
    color: #475569;
    white-space: nowrap;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 12px;
}
.llx-cell-logger {
    color: #0f172a;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 12px;
}
.llx-cell-message {
    min-width: 360px;
    max-width: 760px;
    color: #172033;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 12px;
    word-break: break-word;
}
.llx-message-preview,
.llx-message-full {
    white-space: pre-wrap;
}
.llx-message-summary {
    cursor: pointer;
    color: #0f172a;
    font-weight: 700;
}
.llx-message-full {
    margin-top: 8px;
    color: #334155;
}
.llx-empty-logger { color: #94a3b8; }
.llx-badge {
    display: inline-flex;
    align-items: center;
    min-height: 24px;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 850;
    letter-spacing: 0.05em;
}
.llx-badge-error { background: var(--llx-danger-soft); color: #991b1b; }
.llx-badge-warning { background: var(--llx-warning-soft); color: #92400e; }
.llx-badge-info { background: var(--llx-info-soft); color: #075985; }
.llx-badge-debug { background: var(--llx-debug-soft); color: #334155; }
.llx-badge-default { background: #ede9fe; color: #5b21b6; }
.llx-log-table tr[data-level="ERROR"] { box-shadow: inset 3px 0 0 var(--llx-danger); }
.llx-log-table tr[data-level="WARNING"] { box-shadow: inset 3px 0 0 var(--llx-warning); }
.llx-log-table tr[data-level="INFO"] { box-shadow: inset 3px 0 0 var(--llx-info); }

code {
    padding: 2px 6px;
    border-radius: 6px;
    background: var(--llx-surface-muted);
    color: #334155;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}

@media (max-width: 1180px) {
    .app-shell { grid-template-columns: 1fr; }
    .sidebar {
        position: relative;
        height: auto;
        padding: 16px 20px;
        border-right: 0;
        border-bottom: 1px solid var(--llx-border);
    }
    .brand { padding-bottom: 14px; }
    .nav { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .sidebar-footer { display: none; }
    .metrics-grid { grid-template-columns: repeat(3, minmax(140px, 1fr)); }
    .filters { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .form-actions { grid-column: 1 / -1; }
}

@media (max-width: 780px) {
    .main { padding: 22px 16px; }
    .topbar { display: grid; }
    .actions { width: 100%; }
    .button { flex: 1 1 auto; }
    .nav { grid-template-columns: 1fr; }
    .dashboard-grid { grid-template-columns: 1fr; }
    .metrics-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .filters { grid-template-columns: 1fr; }
    .llx-table-header { display: grid; }
    .llx-table-tools { justify-content: stretch; }
    .llx-table-tools input,
    .llx-table-tools select,
    .llx-table-tools .button { width: 100%; }
    .llx-table-summary { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 520px) {
    h1 { font-size: 30px; }
    .metrics-grid { grid-template-columns: 1fr; }
    .metric-card { min-height: 108px; }
    .chart-container,
    .chart-container.is-large { min-height: 320px; }
}
"""

DASHBOARD_SCRIPT = """
(function () {
    const data = window.LOGLENSX_DATA || {};
    const palette = {
        ERROR: "#dc2626",
        WARNING: "#d97706",
        INFO: "#0284c7",
        DEBUG: "#475569",
        DEFAULT: "#7c3aed"
    };

    function formatNumber(value) {
        const number = Number(value || 0);
        return new Intl.NumberFormat().format(number);
    }

    function showEmpty(container, title) {
        if (!container) {
            return;
        }
        container.innerHTML = '<div class="empty-state"><div><strong>' + title + '</strong><span>No data available</span></div></div>';
    }

    function toLogUrl(params) {
        const links = data.links || {};
        const base = links.logsBase || links.logs || "/loglensx/logs";
        const url = new URL(base, window.location.href);
        Object.keys(params || {}).forEach(function (key) {
            const value = params[key];
            if (value !== undefined && value !== null && value !== "") {
                url.searchParams.set(key, value);
            }
        });
        if (!url.searchParams.has("limit")) {
            url.searchParams.set("limit", "100");
        }
        return url.pathname + url.search;
    }

    function activateNavigation() {
        const current = window.location.pathname.replace(/\\/$/, "");
        document.querySelectorAll(".nav a").forEach(function (link) {
            const target = new URL(link.href, window.location.href).pathname.replace(/\\/$/, "");
            if (target === current) {
                link.classList.add("is-active");
            }
        });
    }

    function animateMetrics() {
        document.querySelectorAll("[data-count]").forEach(function (node) {
            const target = Number(node.getAttribute("data-count") || 0);
            const suffix = node.getAttribute("data-suffix") || "";
            const duration = 700;
            const start = performance.now();

            function frame(now) {
                const progress = Math.min((now - start) / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3);
                const value = Math.round(target * eased);
                node.textContent = formatNumber(value) + suffix;
                if (progress < 1) {
                    requestAnimationFrame(frame);
                }
            }

            requestAnimationFrame(frame);
        });
    }

    function commonLayout(extra) {
        return Object.assign({
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: "#ffffff",
            margin: { t: 22, r: 18, b: 48, l: 58 },
            font: { family: "Inter, system-ui, sans-serif", color: "#334155" },
            hoverlabel: { bgcolor: "#111827", bordercolor: "#111827", font: { color: "#ffffff" } },
            legend: { orientation: "h", y: 1.12, x: 1, xanchor: "right" }
        }, extra || {});
    }

    function plotCharts() {
        if (!window.Plotly) {
            showEmpty(document.getElementById("levelChart"), "Charts unavailable");
            showEmpty(document.getElementById("errorChart"), "Charts unavailable");
            showEmpty(document.getElementById("loggersChart"), "Charts unavailable");
            return;
        }

        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ["lasso2d", "select2d"]
        };

        const levelEl = document.getElementById("levelChart");
        const levelEntries = Object.entries(data.levelStats || {}).filter(function (item) {
            return Number(item[1]) > 0;
        });
        if (levelEl && levelEntries.length) {
            Plotly.newPlot(levelEl, [{
                labels: levelEntries.map(function (item) { return item[0]; }),
                values: levelEntries.map(function (item) { return item[1]; }),
                type: "pie",
                hole: 0.62,
                sort: false,
                marker: {
                    colors: levelEntries.map(function (item) { return palette[item[0]] || palette.DEFAULT; }),
                    line: { color: "#ffffff", width: 3 }
                },
                textinfo: "label+percent",
                hovertemplate: "<b>%{label}</b><br>%{value} entries<br>%{percent}<extra></extra>"
            }], commonLayout({
                margin: { t: 12, r: 12, b: 20, l: 12 },
                showlegend: true
            }), config);
            levelEl.on("plotly_click", function (event) {
                const level = event.points && event.points[0] && event.points[0].label;
                if (level) {
                    window.location.href = toLogUrl({ level: level });
                }
            });
        } else {
            showEmpty(levelEl, "Level mix");
        }

        const errorEl = document.getElementById("errorChart");
        const errorEntries = Object.entries(data.errorFrequency || {});
        if (errorEl && errorEntries.length) {
            Plotly.newPlot(errorEl, [{
                x: errorEntries.map(function (item) { return item[0]; }),
                y: errorEntries.map(function (item) { return item[1]; }),
                type: "scatter",
                mode: "lines+markers",
                name: "Errors",
                fill: "tozeroy",
                fillcolor: "rgba(220,38,38,0.10)",
                line: { color: palette.ERROR, width: 3, shape: "spline", smoothing: 1.1 },
                marker: { size: 7, color: "#ffffff", line: { color: palette.ERROR, width: 2 } },
                hovertemplate: "<b>%{x}</b><br>%{y} errors<extra></extra>"
            }], commonLayout({
                xaxis: {
                    title: "",
                    gridcolor: "#e5edf7",
                    rangeselector: {
                        buttons: [
                            { count: 6, label: "6h", step: "hour", stepmode: "backward" },
                            { count: 24, label: "24h", step: "hour", stepmode: "backward" },
                            { step: "all", label: "All" }
                        ]
                    }
                },
                yaxis: { title: "Errors", rangemode: "tozero", gridcolor: "#e5edf7" }
            }), config);
        } else {
            showEmpty(errorEl, "Error timeline");
        }

        const loggerEl = document.getElementById("loggersChart");
        const topLoggers = (data.topLoggers || []).slice().reverse();
        if (loggerEl && topLoggers.length) {
            Plotly.newPlot(loggerEl, [{
                x: topLoggers.map(function (item) { return item[1]; }),
                y: topLoggers.map(function (item) { return item[0] || "root"; }),
                type: "bar",
                orientation: "h",
                marker: {
                    color: topLoggers.map(function (item) { return item[1]; }),
                    colorscale: [[0, "#bfdbfe"], [0.55, "#38bdf8"], [1, "#2563eb"]],
                    line: { color: "#ffffff", width: 1 }
                },
                hovertemplate: "<b>%{y}</b><br>%{x} entries<extra></extra>"
            }], commonLayout({
                margin: { t: 14, r: 22, b: 46, l: 130 },
                xaxis: { title: "Entries", rangemode: "tozero", gridcolor: "#e5edf7" },
                yaxis: { title: "", automargin: true },
                showlegend: false
            }), config);
            loggerEl.on("plotly_click", function (event) {
                const loggerName = event.points && event.points[0] && event.points[0].y;
                if (loggerName) {
                    window.location.href = toLogUrl({ logger: loggerName });
                }
            });
        } else {
            showEmpty(loggerEl, "Top loggers");
        }
    }

    function initTables() {
        document.querySelectorAll("[data-log-table]").forEach(function (wrapper) {
            const tbody = wrapper.querySelector("tbody");
            if (!tbody) {
                return;
            }

            const rows = Array.from(tbody.querySelectorAll("tr"));
            const search = wrapper.querySelector("[data-table-search]");
            const level = wrapper.querySelector("[data-table-level]");
            const count = wrapper.querySelector("[data-table-count]");
            const clear = wrapper.querySelector("[data-table-clear]");
            let activeSort = { key: "", direction: "asc" };

            function applyFilters() {
                const query = search ? search.value.trim().toLowerCase() : "";
                const selectedLevel = level ? level.value : "";
                let visible = 0;

                rows.forEach(function (row) {
                    const matchesText = !query || (row.dataset.search || "").includes(query);
                    const matchesLevel = !selectedLevel || row.dataset.level === selectedLevel;
                    const show = matchesText && matchesLevel;
                    row.hidden = !show;
                    if (show) {
                        visible += 1;
                    }
                });

                if (count) {
                    count.textContent = formatNumber(visible);
                }
            }

            function sortRows(key) {
                if (activeSort.key === key) {
                    activeSort.direction = activeSort.direction === "asc" ? "desc" : "asc";
                } else {
                    activeSort = { key: key, direction: "asc" };
                }

                const levelOrder = { ERROR: 1, WARNING: 2, INFO: 3, DEBUG: 4 };
                const sorted = rows.slice().sort(function (a, b) {
                    let left = a.dataset[key] || "";
                    let right = b.dataset[key] || "";

                    if (key === "level") {
                        left = levelOrder[left] || 99;
                        right = levelOrder[right] || 99;
                    } else {
                        left = left.toLowerCase();
                        right = right.toLowerCase();
                    }

                    if (left < right) {
                        return activeSort.direction === "asc" ? -1 : 1;
                    }
                    if (left > right) {
                        return activeSort.direction === "asc" ? 1 : -1;
                    }
                    return 0;
                });

                sorted.forEach(function (row) { tbody.appendChild(row); });
                wrapper.querySelectorAll("[data-sort] .llx-sort-indicator").forEach(function (node) {
                    node.textContent = "";
                });
                const indicator = wrapper.querySelector('[data-sort="' + key + '"] .llx-sort-indicator');
                if (indicator) {
                    indicator.textContent = activeSort.direction === "asc" ? "ASC" : "DESC";
                }
                applyFilters();
            }

            if (search) {
                search.addEventListener("input", applyFilters);
            }
            if (level) {
                level.addEventListener("change", applyFilters);
            }
            if (clear) {
                clear.addEventListener("click", function () {
                    if (search) {
                        search.value = "";
                    }
                    if (level) {
                        level.value = "";
                    }
                    applyFilters();
                });
            }
            wrapper.querySelectorAll("[data-sort]").forEach(function (button) {
                button.addEventListener("click", function () {
                    sortRows(button.getAttribute("data-sort"));
                });
            });

            applyFilters();
        });
    }

    activateNavigation();
    animateMetrics();
    plotCharts();
    initTables();
})();
"""


SVG_SEARCH = """
<svg class="icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path d="M11 19a8 8 0 1 1 5.292-14.002A8 8 0 0 1 11 19Z" stroke="currentColor" stroke-width="2"/>
    <path d="m21 21-4.35-4.35" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>
"""

SVG_REFRESH = """
<svg class="icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path d="M21 12a9 9 0 0 1-15.3 6.36" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <path d="M3 12A9 9 0 0 1 18.3 5.64" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <path d="M18 3v4h-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M6 21v-4h4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""


def default_links(prefix: str) -> Dict[str, str]:
    """Build stable dashboard links from a route prefix."""
    base = (prefix or "").rstrip("/")
    return {
        "dashboard": f"{base}/",
        "logs": f"{base}/logs?limit=100",
        "logs_base": f"{base}/logs",
        "api_stats": f"{base}/api/stats",
        "api_logs": f"{base}/api/logs?limit=100",
        "api_files": f"{base}/api/files",
    }


def _as_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _rate(count: int, total: int) -> str:
    if total <= 0:
        return "0.0%"
    return f"{(count / total) * 100:.1f}%"


def _safe_json(data: Mapping[str, Any]) -> str:
    """Serialize JSON safely inside a script tag."""
    return (
        json.dumps(data, default=str)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )


def _query_url(base: str, **params: Any) -> str:
    query = urlencode({key: value for key, value in params.items() if value not in (None, "")})
    return f"{base}?{query}" if query else base


def _selected(value: Optional[str], expected: str) -> str:
    return " selected" if (value or "").upper() == expected else ""


def _stat_cards(summary: Mapping[str, Any], level_stats: Mapping[str, int]) -> str:
    total = _as_int(summary.get("total_logs"))
    errors = _as_int(summary.get("error_count", level_stats.get("ERROR", 0)))
    warnings = _as_int(summary.get("warning_count", level_stats.get("WARNING", 0)))
    unique_loggers = _as_int(summary.get("unique_loggers"))
    files = _as_int(summary.get("files"))
    stability = max(0, min(100, round(100 - ((_as_int(errors) * 4 + _as_int(warnings) * 1.5) / total * 100)))) if total else 100

    cards = [
        ("Total Logs", total, f"{files} files indexed", "info", ""),
        ("Errors", errors, f"{_rate(errors, total)} of traffic", "danger", ""),
        ("Warnings", warnings, f"{_rate(warnings, total)} of traffic", "warning", ""),
        ("Loggers", unique_loggers, "Unique sources", "success", ""),
        ("Files", files, "Active log files", "info", ""),
        ("Stability", stability, "Composite score", "success", "%"),
    ]

    html = ['<section class="metrics-grid" aria-label="Log summary metrics">']
    for label, value, note, tone, suffix in cards:
        html.append(
            '<article class="metric-card metric-{tone}">'
            '<div class="metric-label">{label}</div>'
            '<div class="metric-value" data-count="{value}" data-suffix="{suffix}">{display}</div>'
            '<div class="metric-note">{note}</div>'
            '</article>'.format(
                tone=escape(tone),
                label=escape(label),
                value=escape(str(value)),
                suffix=escape(suffix),
                display=escape(f"{value}{suffix}"),
                note=escape(note),
            )
        )
    html.append("</section>")
    return "".join(html)


def _dashboard_data(
    links: Mapping[str, str],
    summary: Mapping[str, Any],
    level_stats: Mapping[str, int],
    top_loggers: Sequence[Tuple[str, int]],
    error_frequency: Mapping[str, int],
) -> Dict[str, Any]:
    return {
        "links": {
            "logs": links.get("logs", ""),
            "logsBase": links.get("logs_base", links.get("logs", "")),
            "apiStats": links.get("api_stats", ""),
        },
        "summary": dict(summary or {}),
        "levelStats": dict(level_stats or {}),
        "topLoggers": [list(item) for item in top_loggers or []],
        "errorFrequency": dict(error_frequency or {}),
    }


def render_dashboard_page(
    *,
    links: Mapping[str, str],
    summary: Mapping[str, Any],
    level_stats: Mapping[str, int],
    top_loggers: Sequence[Tuple[str, int]],
    error_frequency: Mapping[str, int],
    recent_errors: List[Dict[str, Any]],
    log_dir: str,
) -> str:
    """Render the shared dashboard page."""
    stats_html = _stat_cards(summary, level_stats)
    errors_table = TableGenerator.logs_to_html_table(
        recent_errors,
        title="Recent Errors",
        max_rows=10,
    )
    dashboard_data = _safe_json(
        _dashboard_data(links, summary, level_stats, top_loggers, error_frequency)
    )

    template = Template(
        """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>loglensx Dashboard</title>
    <script src="${plotly_cdn}"></script>
    <style>${styles}</style>
</head>
<body>
    <a class="skip-link" href="#main">Skip to content</a>
    <div class="app-shell">
        <aside class="sidebar">
            <div class="brand">
                <div class="brand-mark">LX</div>
                <div>
                    <p class="brand-title">loglensx</p>
                    <p class="brand-subtitle">Log analytics</p>
                </div>
            </div>
            <nav class="nav" aria-label="Dashboard navigation">
                <a href="${dashboard_url}"><span class="nav-icon" aria-hidden="true"></span>Dashboard</a>
                <a href="${logs_url}"><span class="nav-icon" aria-hidden="true"></span>Log Explorer</a>
                <a href="${api_stats_url}"><span class="nav-icon" aria-hidden="true"></span>Statistics API</a>
            </nav>
            <div class="sidebar-footer">
                Log directory
                <code>${log_dir}</code>
            </div>
        </aside>

        <main class="main" id="main">
            <header class="topbar">
                <div>
                    <p class="eyebrow">Operational Dashboard</p>
                    <h1>Log Intelligence</h1>
                    <p>Monitor severity, error timing, and noisy loggers from a single workspace.</p>
                </div>
                <div class="actions">
                    <a class="button button-secondary" href="${api_logs_url}">JSON Logs</a>
                    <a class="button" href="${logs_url}">Open Explorer</a>
                </div>
            </header>

            <form class="command-panel filters" action="${logs_base_url}" method="get">
                <div class="field">
                    <label for="dashboard-search">Search</label>
                    <input id="dashboard-search" name="search" type="search" placeholder="message text or route">
                </div>
                <div class="field">
                    <label for="dashboard-level">Level</label>
                    <select id="dashboard-level" name="level">
                        <option value="">All levels</option>
                        <option value="ERROR">ERROR</option>
                        <option value="WARNING">WARNING</option>
                        <option value="INFO">INFO</option>
                        <option value="DEBUG">DEBUG</option>
                    </select>
                </div>
                <div class="field">
                    <label for="dashboard-logger">Logger</label>
                    <input id="dashboard-logger" name="logger" placeholder="app.api or worker">
                </div>
                <div class="field">
                    <label for="dashboard-limit">Rows</label>
                    <input id="dashboard-limit" name="limit" type="number" min="10" max="1000" value="100">
                </div>
                <div class="form-actions">
                    <button class="button" type="submit">${search_icon}<span>Search</span></button>
                </div>
            </form>

            ${stats_html}

            <section class="dashboard-grid" aria-label="Severity and timeline charts">
                <article class="dashboard-card">
                    <div class="card-header">
                        <div>
                            <p class="eyebrow">Severity</p>
                            <h2>Level Mix</h2>
                        </div>
                    </div>
                    <div class="chart-container" id="levelChart"></div>
                </article>
                <article class="dashboard-card">
                    <div class="card-header">
                        <div>
                            <p class="eyebrow">Reliability</p>
                            <h2>Error Timeline</h2>
                        </div>
                        <div class="card-actions">
                            <a class="button button-secondary" href="${dashboard_url}">${refresh_icon}<span>Refresh</span></a>
                        </div>
                    </div>
                    <div class="chart-container" id="errorChart"></div>
                </article>
            </section>

            <section class="dashboard-grid-wide" aria-label="Logger activity chart">
                <article class="dashboard-card">
                    <div class="card-header">
                        <div>
                            <p class="eyebrow">Sources</p>
                            <h2>Top Loggers</h2>
                        </div>
                    </div>
                    <div class="chart-container is-large" id="loggersChart"></div>
                </article>
            </section>

            ${errors_table}
        </main>
    </div>
    <script>window.LOGLENSX_DATA = ${dashboard_data};</script>
    <script>${script}</script>
</body>
</html>"""
    )

    return template.substitute(
        plotly_cdn=PLOTLY_CDN,
        styles=DASHBOARD_STYLES,
        dashboard_url=escape(links.get("dashboard", "#"), quote=True),
        logs_url=escape(links.get("logs", "#"), quote=True),
        logs_base_url=escape(links.get("logs_base", links.get("logs", "#")), quote=True),
        api_stats_url=escape(links.get("api_stats", "#"), quote=True),
        api_logs_url=escape(links.get("api_logs", "#"), quote=True),
        log_dir=escape(log_dir),
        search_icon=SVG_SEARCH,
        refresh_icon=SVG_REFRESH,
        stats_html=stats_html,
        errors_table=errors_table,
        dashboard_data=dashboard_data,
        script=DASHBOARD_SCRIPT,
    )


def render_logs_page(
    *,
    links: Mapping[str, str],
    logs: List[Dict[str, Any]],
    log_dir: str,
    search: Optional[str] = None,
    level: Optional[str] = None,
    logger: Optional[str] = None,
    limit: int = 100,
) -> str:
    """Render the shared log explorer page."""
    logs_table = TableGenerator.logs_to_html_table(logs, title="Log Explorer", max_rows=limit)
    level_value = (level or "").upper()
    dashboard_data = _safe_json(
        {
            "links": {
                "logs": links.get("logs", ""),
                "logsBase": links.get("logs_base", links.get("logs", "")),
            },
            "levelStats": {},
            "topLoggers": [],
            "errorFrequency": {},
        }
    )

    template = Template(
        """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>loglensx Log Explorer</title>
    <style>${styles}</style>
</head>
<body>
    <a class="skip-link" href="#main">Skip to content</a>
    <div class="app-shell">
        <aside class="sidebar">
            <div class="brand">
                <div class="brand-mark">LX</div>
                <div>
                    <p class="brand-title">loglensx</p>
                    <p class="brand-subtitle">Log explorer</p>
                </div>
            </div>
            <nav class="nav" aria-label="Dashboard navigation">
                <a href="${dashboard_url}"><span class="nav-icon" aria-hidden="true"></span>Dashboard</a>
                <a href="${logs_url}"><span class="nav-icon" aria-hidden="true"></span>Log Explorer</a>
                <a href="${api_logs_url}"><span class="nav-icon" aria-hidden="true"></span>Logs API</a>
            </nav>
            <div class="sidebar-footer">
                Log directory
                <code>${log_dir}</code>
            </div>
        </aside>

        <main class="main" id="main">
            <header class="topbar">
                <div>
                    <p class="eyebrow">Search Workspace</p>
                    <h1>Log Explorer</h1>
                    <p>${result_count} entries from <code>${log_dir}</code></p>
                </div>
                <div class="actions">
                    <a class="button button-secondary" href="${api_logs_filtered_url}">JSON Results</a>
                    <a class="button" href="${dashboard_url}">Dashboard</a>
                </div>
            </header>

            <form class="command-panel filters" action="${logs_base_url}" method="get">
                <div class="field">
                    <label for="search">Search</label>
                    <input id="search" name="search" type="search" value="${search}" placeholder="message text or route">
                </div>
                <div class="field">
                    <label for="level">Level</label>
                    <select id="level" name="level">
                        <option value=""${selected_all}>All levels</option>
                        <option value="ERROR"${selected_error}>ERROR</option>
                        <option value="WARNING"${selected_warning}>WARNING</option>
                        <option value="INFO"${selected_info}>INFO</option>
                        <option value="DEBUG"${selected_debug}>DEBUG</option>
                    </select>
                </div>
                <div class="field">
                    <label for="logger">Logger</label>
                    <input id="logger" name="logger" value="${logger}" placeholder="app.api or worker">
                </div>
                <div class="field">
                    <label for="limit">Rows</label>
                    <input id="limit" name="limit" type="number" min="1" max="1000" value="${limit}">
                </div>
                <div class="form-actions">
                    <button class="button" type="submit">${search_icon}<span>Apply</span></button>
                </div>
            </form>

            ${logs_table}
        </main>
    </div>
    <script>window.LOGLENSX_DATA = ${dashboard_data};</script>
    <script>${script}</script>
</body>
</html>"""
    )

    api_logs_base = links.get("api_logs", links.get("logs_base", "#")).split("?", 1)[0]
    filtered_api_url = _query_url(
        api_logs_base,
        search=search,
        level=level,
        logger=logger,
        limit=limit,
    )

    return template.substitute(
        styles=DASHBOARD_STYLES,
        dashboard_url=escape(links.get("dashboard", "#"), quote=True),
        logs_url=escape(links.get("logs", "#"), quote=True),
        logs_base_url=escape(links.get("logs_base", links.get("logs", "#")), quote=True),
        api_logs_url=escape(links.get("api_logs", "#"), quote=True),
        api_logs_filtered_url=escape(filtered_api_url, quote=True),
        log_dir=escape(log_dir),
        result_count=escape(str(len(logs))),
        search=escape(search or "", quote=True),
        logger=escape(logger or "", quote=True),
        limit=escape(str(limit), quote=True),
        selected_all=" selected" if not level_value else "",
        selected_error=_selected(level_value, "ERROR"),
        selected_warning=_selected(level_value, "WARNING"),
        selected_info=_selected(level_value, "INFO"),
        selected_debug=_selected(level_value, "DEBUG"),
        search_icon=SVG_SEARCH,
        logs_table=logs_table,
        dashboard_data=dashboard_data,
        script=DASHBOARD_SCRIPT,
    )

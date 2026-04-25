# Changelog

All notable changes to `loglensx` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4] - 2026-04-25

### Added

- JSON-line log parsing with preserved structured extras.
- Multiline traceback folding so stack frames stay attached to the originating log entry.
- Time-window and source-file filters across analyzer APIs, web explorer pages, and `/api/logs`.
- `LogExporter` for JSON, CSV, and NDJSON serialization.
- `/api/export` endpoints for Flask and FastAPI integrations.
- Expanded CLI workflows for `summary`, `logs`, `files`, and recurring error `patterns`.
- Error pattern grouping and enriched per-file statistics.

### Changed

- Refreshed non-README project documentation for the current dashboard, visualization viewer, and publishing workflow.
- Reworked release checklists to emphasize version consistency across `pyproject.toml`, `setup.py`, and `loglensx/__init__.py`.
- Dashboard and explorer forms now include source file and time-window filters plus CSV export actions.
- Default `pytest` configuration no longer requires the optional coverage plugin; coverage is now an explicit command.

### Fixed

- Custom regex patterns passed to `LogParser` are now applied before built-in patterns.

## [1.0.3] - 2026-04-24

### Added

- Shared dashboard renderer for Flask and FastAPI integrations.
- Professional dashboard layout with metric cards, Plotly charts, responsive navigation, and richer log explorer pages.
- Searchable and sortable HTML log tables with level badges, source metadata, and expandable long messages.
- Flask `/api/files` endpoint parity with FastAPI.
- Local visualization viewer at `visualizations/index.html` for generated Plotly JSON files.
- Regression tests for shared dashboard and log explorer rendering.

### Changed

- Updated chart styling with consistent severity colors, improved Plotly hover templates, timeline fill, and top logger bar styling.
- Reduced duplicated dashboard HTML between Flask and FastAPI integrations.
- Improved direct-run behavior for example apps from a source checkout.

### Fixed

- Corrected package naming consistency in integration routes and imports.
- Fixed Flask template and URL references to use the consistent `loglensx` blueprint naming.
- Avoided blocking Flask-only usage when FastAPI optional dependencies are not installed, and vice versa.

## [1.0.1] - 2026-04-24

### Fixed

- Improved integration naming consistency.
- Verified route registration and package exports across Flask and FastAPI.

## [1.0.0] - 2026-04-23

### Added

- Initial release of `loglensx`.
- Core log parser with common pattern detection and custom regex support.
- Log analyzer with summaries, level counts, top loggers, error frequency, search, and filtering.
- FastAPI integration.
- Flask integration.
- Plotly chart generation for level distribution, error timeline, and top loggers.
- HTML table generation for log entries and statistics.
- CLI summary command.
- Examples for Flask, FastAPI, and standalone usage.
- Packaging configuration for PyPI.
- MIT License.

## [0.0.2] - 2026-04-23

### Added

- Project initialization.

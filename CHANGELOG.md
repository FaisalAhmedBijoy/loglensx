# Changelog

All notable changes to `loglensx` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Refreshed non-README project documentation for the current dashboard, visualization viewer, and publishing workflow.
- Reworked release checklists to emphasize version consistency across `pyproject.toml`, `setup.py`, and `loglensx/__init__.py`.

## [1.0.2] - 2026-04-24

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

## [1.0.0] - 2024-01-15

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

## [0.0.2] - 2024-01-01

### Added

- Project initialization.

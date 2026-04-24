# Publishing Guide

This guide describes how to build, verify, and publish `loglensx` to PyPI.

## Prerequisites

- Python 3.8 or newer.
- A PyPI account: https://pypi.org
- A TestPyPI account for release rehearsal: https://test.pypi.org
- API tokens for PyPI and TestPyPI.
- A clean working tree before building a release.

Install build tools:

```bash
python -m pip install --upgrade build twine
```

For full local checks, install development extras:

```bash
python -m pip install -e ".[dev,flask,fastapi]"
```

## Version Checklist

Before each release, choose the target version, for example `1.0.3`, and update every version source:

| File | Field |
| --- | --- |
| `pyproject.toml` | `project.version` |
| `setup.py` | `version=` |
| `loglensx/__init__.py` | `__version__` |
| `CHANGELOG.md` | Release heading and notes |

Verify with:

```bash
python -c "import loglensx; print(loglensx.__version__)"
python -m pip show loglensx
```

If the installed package is stale during local testing, reinstall it:

```bash
python -m pip install -e ".[dev,flask,fastapi]"
```

## Pre-Build Validation

Run syntax checks:

```bash
python -m compileall loglensx examples tests
```

Run tests:

```bash
pytest
```

If coverage tooling is not installed:

```bash
pytest -q -o addopts=""
```

Smoke-test examples when integration code changed:

```bash
python examples/flask_example.py
python examples/fastapi_example.py
python examples/standalone_example.py
```

## Clean Old Build Artifacts

```bash
rm -rf build dist *.egg-info
```

## Build

```bash
python -m build
```

Expected output:

```text
dist/loglensx-X.Y.Z.tar.gz
dist/loglensx-X.Y.Z-py3-none-any.whl
```

Validate the generated distributions:

```bash
twine check dist/*
```

## TestPyPI Rehearsal

Upload to TestPyPI:

```bash
twine upload --repository testpypi dist/*
```

Install from TestPyPI in a clean environment:

```bash
python -m venv /tmp/loglensx-test
source /tmp/loglensx-test/bin/activate
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ "loglensx[flask,fastapi]"
python -c "from loglensx import LogParser, LogAnalyzer; print('import ok')"
deactivate
```

The `--extra-index-url` flag lets pip resolve dependencies from PyPI while installing `loglensx` from TestPyPI.

## Publish to PyPI

Upload the verified distribution:

```bash
twine upload dist/*
```

Verify the project page:

```text
https://pypi.org/project/loglensx/
```

Install from PyPI in a clean environment:

```bash
python -m venv /tmp/loglensx-pypi-test
source /tmp/loglensx-pypi-test/bin/activate
pip install "loglensx[flask,fastapi]"
python -c "from loglensx import setup_flask_loglensx, setup_fastapi_loglensx; print('imports ok')"
deactivate
```

## Git Tag and Release

```bash
git status --short
git add pyproject.toml setup.py loglensx/__init__.py CHANGELOG.md
git commit -m "chore: release X.Y.Z"
git tag -a vX.Y.Z -m "Release X.Y.Z"
git push origin main
git push origin vX.Y.Z
```

Create a GitHub release using the matching `CHANGELOG.md` notes.

## Post-Release Checks

- Confirm `pip install loglensx` works.
- Confirm `pip install "loglensx[flask]"` works.
- Confirm `pip install "loglensx[fastapi]"` works.
- Confirm the PyPI README renders correctly.
- Confirm examples in the source checkout still run.
- Confirm `CHANGELOG.md` has an empty or updated `Unreleased` section for future work.

## Common Problems

### File already exists

PyPI does not allow replacing an uploaded distribution. Bump the version and rebuild.

### README does not render

Run:

```bash
twine check dist/*
```

Fix Markdown or metadata warnings before upload.

### Authorization failed

- Confirm the API token belongs to the correct PyPI project or account.
- Confirm `~/.pypirc` points to the correct repository.
- Try passing the repository explicitly: `twine upload --repository pypi dist/*`.

### TestPyPI dependencies fail to resolve

Use PyPI as an extra index:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ loglensx
```

## Useful Links

- Python packaging guide: https://packaging.python.org/
- PyPI: https://pypi.org/
- TestPyPI: https://test.pypi.org/
- Twine: https://twine.readthedocs.io/

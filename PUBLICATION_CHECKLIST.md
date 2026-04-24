# Publication Checklist

Use this checklist before publishing a new `loglensx` release.

## Release Metadata

- [ ] Choose the target version: `X.Y.Z`.
- [ ] Update `pyproject.toml`.
- [ ] Update `setup.py`.
- [ ] Update `loglensx/__init__.py`.
- [ ] Update `CHANGELOG.md`.
- [ ] Confirm all version values match.
- [ ] Confirm package name is consistently `loglensx`.

Version check commands:

```bash
rg -n "__version__|version=|version =" loglensx/__init__.py setup.py pyproject.toml
python -c "import loglensx; print(loglensx.__version__)"
```

## Documentation

- [ ] `README.md` describes the current dashboard, API routes, and examples.
- [ ] `QUICKSTART.md` is runnable and concise.
- [ ] `PROJECT_SUMMARY.md` matches current architecture.
- [ ] `PUBLISHING.md` has the current release process.
- [ ] `DELIVERABLES.md` matches shipped files and features.
- [ ] `CHANGELOG.md` includes release notes for `X.Y.Z`.
- [ ] Documentation avoids stale version numbers.

## Local Validation

- [ ] Install local package with all extras.

```bash
python -m pip install -e ".[dev,flask,fastapi]"
```

- [ ] Run syntax checks.

```bash
python -m compileall loglensx examples tests
```

- [ ] Run tests.

```bash
pytest
```

If coverage tools are not installed:

```bash
pytest -q -o addopts=""
```

- [ ] Run or smoke-test examples.

```bash
python examples/flask_example.py
python examples/fastapi_example.py
python examples/standalone_example.py
```

- [ ] Confirm visualization viewer instructions work.

```bash
python -m http.server 8080
```

Open:

```text
http://127.0.0.1:8080/visualizations/
```

## Clean Build

- [ ] Remove old build artifacts.

```bash
rm -rf build dist *.egg-info
```

- [ ] Build the package.

```bash
python -m build
```

- [ ] Confirm `dist/` contains exactly the new release files.
- [ ] Validate distributions.

```bash
twine check dist/*
```

## TestPyPI

- [ ] Upload to TestPyPI.

```bash
twine upload --repository testpypi dist/*
```

- [ ] Install in a clean environment.

```bash
python -m venv /tmp/loglensx-test
source /tmp/loglensx-test/bin/activate
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ "loglensx[flask,fastapi]"
python -c "from loglensx import LogParser, LogAnalyzer; print('core imports ok')"
python -c "from loglensx import setup_flask_loglensx, setup_fastapi_loglensx; print('integration imports ok')"
deactivate
```

- [ ] Confirm no unexpected dependency failures.

## PyPI Publication

- [ ] Upload to PyPI.

```bash
twine upload dist/*
```

- [ ] Visit the package page.

```text
https://pypi.org/project/loglensx/
```

- [ ] Confirm the README renders correctly.
- [ ] Confirm the version is correct.
- [ ] Confirm wheel and source distribution are available.

## Installation Verification

Test from PyPI in a clean environment:

```bash
python -m venv /tmp/loglensx-pypi
source /tmp/loglensx-pypi/bin/activate
pip install loglensx
python -c "from loglensx import LogParser, LogAnalyzer; print('core ok')"
pip install "loglensx[flask]"
python -c "from loglensx import setup_flask_loglensx; print('flask ok')"
pip install "loglensx[fastapi]"
python -c "from loglensx import setup_fastapi_loglensx; print('fastapi ok')"
deactivate
```

## Git Release

- [ ] Commit release changes.

```bash
git add pyproject.toml setup.py loglensx/__init__.py CHANGELOG.md
git commit -m "chore: release X.Y.Z"
```

- [ ] Tag release.

```bash
git tag -a vX.Y.Z -m "Release X.Y.Z"
git push origin main
git push origin vX.Y.Z
```

- [ ] Create GitHub release notes from `CHANGELOG.md`.

## Post-Release

- [ ] Confirm package installation in a new shell.
- [ ] Confirm examples still run from the source checkout.
- [ ] Monitor PyPI package page for issues.
- [ ] Watch GitHub issues.
- [ ] Start a new `Unreleased` section in `CHANGELOG.md` if needed.

## Failure Recovery

### Upload says file already exists

Do not try to replace files on PyPI. Bump the version, rebuild, and upload again.

### README rendering fails

Run:

```bash
twine check dist/*
```

Fix the reported Markdown or metadata issue.

### Framework import fails

Confirm optional extras are installed:

```bash
pip install "loglensx[flask]"
pip install "loglensx[fastapi]"
```

### Tests fail due to coverage plugin

Install dev dependencies or disable configured addopts:

```bash
pip install -e ".[dev]"
pytest -q -o addopts=""
```

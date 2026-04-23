# Publishing Guide for LogLens

## Prerequisites

1. Python 3.8 or higher installed
2. PyPI account (create at https://pypi.org)
3. TestPyPI account (optional but recommended, create at https://test.pypi.org)

## Step 1: Install Build Tools

```bash
pip install --upgrade build twine
```

## Step 2: Verify Project Structure

Ensure these files exist:
- `setup.py`
- `pyproject.toml`
- `README.md`
- `LICENSE`
- `CHANGELOG.md`
- `MANIFEST.in`

## Step 3: Test Build (Optional but Recommended)

```bash
python -m build
```

This creates `dist/` folder with `.tar.gz` and `.whl` files.

## Step 4: Test on TestPyPI (Optional)

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    testpypi
    pypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-...  # Your test PyPI token

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-...  # Your PyPI token
```

Test upload:

```bash
twine upload --repository testpypi dist/*
```

Test installation:

```bash
pip install --index-url https://test.pypi.org/simple/ loglensx
```

## Step 5: Update Version

Edit version in:
- `loglens/__init__.py`
- `setup.py`
- `pyproject.toml`

Add entry to `CHANGELOG.md`

## Step 6: Publish to PyPI

```bash
# Remove old builds
rm -rf build dist *.egg-info

# Build
python -m build

# Upload
twine upload dist/*
```

Enter your PyPI credentials when prompted.

## Step 7: Verify Publication

Visit: https://pypi.org/project/loglensx/

## Step 8: Tag Release (Git)

```bash
git tag v1.0.0
git push origin v1.0.0
```

## Installation After Publishing

Users can now install with:

```bash
pip install loglensx
pip install loglensx[fastapi]
pip install loglensx[flask]
pip install loglensx[dev]
```

## Troubleshooting

### "Invalid distribution" error

Verify `setup.py`, `pyproject.toml` syntax and all required fields.

### "File already exists" error

Delete the file from PyPI at https://pypi.org/project/loglensx/

or use a new version number.

### Long description not rendering

Check `README.md` format:
```bash
twine check dist/*
```

## Documentation

After publishing, update documentation:
1. Update README with installation instructions
2. Create GitHub releases with CHANGELOG
3. Setup ReadTheDocs if needed
4. Add badges to README

## Maintenance

- Monitor PyPI download stats
- Respond to issues
- Maintain version compatibility
- Keep CHANGELOG updated

---

For more info: https://packaging.python.org/

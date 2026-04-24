#!/usr/bin/env python3
"""
Pre-publication validation script for LogLens.
Run this before publishing to PyPI.
"""

import os
import sys
from pathlib import Path

def check_files():
    """Check if all required files exist."""
    required_files = [
        'setup.py',
        'pyproject.toml',
        'README.md',
        'LICENSE',
        'CHANGELOG.md',
        'MANIFEST.in',
        'PUBLISHING.md',
        'loglensx/__init__.py',
        'loglensx/core/__init__.py',
        'loglensx/core/parser.py',
        'loglensx/core/analyzer.py',
        'loglensx/integrations/__init__.py',
        'loglensx/integrations/fastapi_integration.py',
        'loglensx/integrations/flask_integration.py',
        'loglensx/visualizers/__init__.py',
        'loglensx/visualizers/charts.py',
        'loglensx/visualizers/tables.py',
        'loglensx/cli.py',
        'examples/fastapi_example.py',
        'examples/flask_example.py',
        'examples/standalone_example.py',
        'tests/test_loglens.py',
    ]

    print("✓ Checking required files...")
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
            print(f"  ✗ Missing: {file}")
        else:
            print(f"  ✓ Found: {file}")

    return len(missing) == 0


def check_python_syntax():
    """Check Python syntax of all .py files."""
    print("\n✓ Checking Python syntax...")
    import py_compile
    import tempfile

    errors = []
    for py_file in Path('.').rglob('*.py'):
        if '.git' in py_file.parts or '__pycache__' in py_file.parts:
            continue
        try:
            py_compile.compile(str(py_file), doraise=True)
            print(f"  ✓ {py_file}")
        except py_compile.PyCompileError as e:
            errors.append((py_file, str(e)))
            print(f"  ✗ {py_file}: {e}")

    return len(errors) == 0


def check_imports():
    """Check if core imports work."""
    print("\n✓ Checking imports...")
    try:
        sys.path.insert(0, str(Path.cwd()))
        from loglensx import LogParser, LogAnalyzer
        print("  ✓ LogParser imported successfully")
        print("  ✓ LogAnalyzer imported successfully")

        from loglensx.integrations import setup_fastapi_loglensx, setup_flask_loglensx
        print("  ✓ setup_fastapi_loglensx imported successfully")
        print("  ✓ setup_flask_loglensx imported successfully")

        from loglensx.visualizers import ChartGenerator, TableGenerator
        print("  ✓ ChartGenerator imported successfully")
        print("  ✓ TableGenerator imported successfully")

        return True
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False


def check_version_consistency():
    """Check version is consistent across files."""
    print("\n✓ Checking version consistency...")

    files_to_check = [
        'setup.py',
        'pyproject.toml',
        'loglensx/__init__.py',
    ]

    versions = {}
    for file in files_to_check:
        if not Path(file).exists():
            continue

        with open(file, 'r') as f:
            content = f.read()
            # Simple version extraction
            if 'version = "' in content:
                version = content.split('version = "')[1].split('"')[0]
                versions[file] = version
                print(f"  {file}: {version}")

    if len(set(versions.values())) == 1:
        print("  ✓ All versions match")
        return True
    else:
        print("  ✗ Version mismatch detected!")
        return False


def check_readme():
    """Check README format."""
    print("\n✓ Checking README...")

    if not Path('README.md').exists():
        print("  ✗ README.md not found")
        return False

    with open('README.md', 'r') as f:
        content = f.read()

    checks = [
        ('Has title', '# LogLens' in content),
        ('Has features', 'Features' in content or 'features' in content),
        ('Has installation', 'Installation' in content or 'installation' in content),
        ('Has license', 'MIT' in content or 'License' in content),
    ]

    all_pass = True
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
        if not result:
            all_pass = False

    return all_pass


def main():
    """Run all checks."""
    print("=" * 60)
    print("loglensx Pre-Publication Validation")
    print("=" * 60 + "\n")

    checks = [
        ("Required files", check_files),
        ("Python syntax", check_python_syntax),
        ("Imports", check_imports),
        ("Version consistency", check_version_consistency),
        ("README format", check_readme),
    ]

    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"\n✗ {check_name} failed with error: {e}")
            results.append((check_name, False))

    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)

    all_pass = True
    for check_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {check_name}")
        if not result:
            all_pass = False

    print("=" * 60)

    if all_pass:
        print("\n✓ All checks passed! Ready for PyPI publication.")
        print("\nNext steps:")
        print("1. Run: python -m build")
        print("2. Run: twine upload dist/*")
        print("3. Or see PUBLISHING.md for detailed instructions")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

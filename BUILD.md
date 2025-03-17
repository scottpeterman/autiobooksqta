# Building and Distributing AudiobooksQT

This document provides instructions for building and distributing the AudiobooksQT package.

## Prerequisites

Before building the package, ensure you have the necessary tools installed:

```bash
pip install setuptools wheel twine
```

## Building the Package

### 1. Clean previous builds (if any)

Remove any previous build artifacts:

```bash
rm -rf build/ dist/ *.egg-info/
```

On Windows:

```bash
rmdir /s /q build dist autiobooksqt.egg-info
```

### 2. Build the package

To build both source distribution and wheel:

```bash
python setup.py sdist bdist_wheel
```

This will create:
- A source distribution (`.tar.gz`) in the `dist/` directory
- A wheel file (`.whl`) in the `dist/` directory

## Testing the Package Locally

Before uploading to PyPI, you can test the package locally:

```bash
pip install dist/*.whl
```

Or install in development mode:

```bash
pip install -e .
```

## Uploading to PyPI

### 1. Test PyPI (recommended for first uploads)

First, upload to the test PyPI repository:

```bash
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

Install from Test PyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ autiobooksqt
```

### 2. Production PyPI

When ready to publish publicly:

```bash
twine upload dist/*
```

You'll be prompted for your PyPI username and password. To avoid this, you can create a `.pypirc` file in your home directory:

```ini
[pypi]
username = your_username
password = your_password

[testpypi]
repository = https://test.pypi.org/legacy/
username = your_username
password = your_password
```

## Version Management

Always update the version number in `setup.py` before building a new release:

```python
setup(
    name="autiobooksqt",
    version="0.1.1",  # Increment this for each release
    # ...
)
```

Follow semantic versioning:
- PATCH (0.0.x) - Bug fixes
- MINOR (0.x.0) - New features, backward compatible
- MAJOR (x.0.0) - Breaking changes

## Package Requirements

This package reads dependencies from `requirements.txt`. Always keep this file updated with the correct dependencies and versions.

## Including Non-Python Files

Non-Python files that should be included in the package are defined in `MANIFEST.in`. Update this file if you add new resources or documentation that should be part of the distribution.
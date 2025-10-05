# SLD API Backend - Development with UV

This project uses [uv](https://github.com/astral-sh/uv) as Python package manager for faster and more efficient development.

## 🚀 Installing UV

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# With pip (alternative)
pip install uv
```

## 📦 Dependency Management

### Install dependencies

```bash
# Install all project dependencies
uv pip install -e .

# Install with development dependencies
uv pip install -e ".[dev]"

# Sync with pyproject.toml
uv pip sync
```

### Add new dependencies

```bash
# Add a dependency to the project
# 1. Edit pyproject.toml manually
# 2. Install the new dependency
uv pip install package-name==version

# Or install and let uv update automatically
uv add package-name
```

### Update dependencies

```bash
# Update all dependencies
uv pip install --upgrade -e .

# Update a specific dependency
uv pip install --upgrade package-name
```

## 🏃 Running the Application

### Local development

```bash
# With uvicorn directly
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# With custom script
uv run python main.py
```

### Tests

```bash
# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=html

# Specific test
uv run pytest test/test_00_user_init.py
```

## 🐳 Docker

The Dockerfile is already configured to use `uv`. To build the image:

```bash
docker build -t sld-api-backend:latest .
```

## 🔧 Development Tools

### Code formatting

```bash
# Format with black
uv run black .

# Lint with ruff
uv run ruff check .

# Autofix with ruff
uv run ruff check --fix .
```

### Type checking

```bash
# Check types with mypy
uv run mypy src/
```

## 📝 Advantages of UV over pip

- ⚡ **10-100x faster** than pip for package installation
- 🔒 **More reliable dependency resolution**
- 💾 **Smart cache** that saves bandwidth
- 🎯 **pip compatible** - uses the same requirements format
- 🛡️ **Improved reproducibility** with lockfiles

## 🔄 Migration from pip

If you're coming from pip, here are the equivalent commands:

| pip | uv |
|-----|-----|
| `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| `pip install package` | `uv pip install package` |
| `pip install -e .` | `uv pip install -e .` |
| `pip freeze > requirements.txt` | `uv pip freeze > requirements.txt` |
| `pip list` | `uv pip list` |

## 📚 More Information

- [Official uv documentation](https://github.com/astral-sh/uv)
- [pyproject.toml guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)

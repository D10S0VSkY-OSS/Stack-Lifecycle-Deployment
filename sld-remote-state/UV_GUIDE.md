# UV Guide for SLD Remote State

## Installation

Install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Common Commands

### Install all dependencies
```bash
uv pip install -e .
```

### Install from requirements.txt (backwards compatibility)
```bash
uv pip install -r requirements.txt
```

### Install with dev dependencies
```bash
uv pip install -e ".[dev]"
```

### Sync dependencies (respects lock file)
```bash
uv pip sync
```

### Update a specific package
```bash
uv pip install --upgrade fastapi
```

### Run the application with uv
```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8080
```

### Run tests
```bash
uv run pytest
```

### Format code with black
```bash
uv run black .
```

### Lint with ruff
```bash
uv run ruff check .
```

## Development Workflow

1. Install dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```

2. Run the application:
   ```bash
   uv run python main.py
   ```

3. Run tests:
   ```bash
   uv run pytest
   ```

## Notes

- `uv` is significantly faster than pip
- Uses `pyproject.toml` as the source of truth
- Compatible with `requirements.txt` for backwards compatibility
- Supports lock files for reproducible builds

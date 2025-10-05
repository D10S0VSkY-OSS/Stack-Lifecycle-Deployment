# SLD API Backend - Development with UV

Este proyecto usa [uv](https://github.com/astral-sh/uv) como gestor de paquetes de Python para un desarrollo más rápido y eficiente.

## 🚀 Instalación de UV

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Con pip (alternativa)
pip install uv
```

## 📦 Gestión de Dependencias

### Instalar dependencias

```bash
# Instalar todas las dependencias del proyecto
uv pip install -e .

# Instalar con dependencias de desarrollo
uv pip install -e ".[dev]"

# Sincronizar con pyproject.toml
uv pip sync
```

### Agregar nuevas dependencias

```bash
# Agregar una dependencia al proyecto
# 1. Edita pyproject.toml manualmente
# 2. Instala la nueva dependencia
uv pip install nombre-paquete==version

# O instala y deja que uv actualice automáticamente
uv add nombre-paquete
```

### Actualizar dependencias

```bash
# Actualizar todas las dependencias
uv pip install --upgrade -e .

# Actualizar una dependencia específica
uv pip install --upgrade nombre-paquete
```

## 🏃 Ejecutar la aplicación

### Desarrollo local

```bash
# Con uvicorn directamente
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Con script personalizado
uv run python main.py
```

### Tests

```bash
# Ejecutar todos los tests
uv run pytest

# Con cobertura
uv run pytest --cov=src --cov-report=html

# Test específico
uv run pytest test/test_00_user_init.py
```

## 🐳 Docker

El Dockerfile ya está configurado para usar `uv`. Para construir la imagen:

```bash
docker build -t sld-api-backend:latest .
```

## 🔧 Herramientas de Desarrollo

### Formateo de código

```bash
# Formatear con black
uv run black .

# Lint con ruff
uv run ruff check .

# Autofix con ruff
uv run ruff check --fix .
```

### Type checking

```bash
# Verificar tipos con mypy
uv run mypy src/
```

## 📝 Ventajas de UV sobre pip

- ⚡ **10-100x más rápido** que pip para instalación de paquetes
- 🔒 **Resolución de dependencias más confiable**
- 💾 **Cache inteligente** que ahorra ancho de banda
- 🎯 **Compatible con pip** - usa el mismo formato de requirements
- 🛡️ **Reproducibilidad mejorada** con lockfiles

## 🔄 Migración desde pip

Si vienes de usar pip, estos son los comandos equivalentes:

| pip | uv |
|-----|-----|
| `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| `pip install package` | `uv pip install package` |
| `pip install -e .` | `uv pip install -e .` |
| `pip freeze > requirements.txt` | `uv pip freeze > requirements.txt` |
| `pip list` | `uv pip list` |

## 📚 Más información

- [Documentación oficial de uv](https://github.com/astral-sh/uv)
- [Guía de pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)

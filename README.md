# SOFTWARE-ENGINEER

A simple configurable Python greeting CLI.

Quickstart

- Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

- Install development dependencies and run tests:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
pytest -q
```

Alternative install using the package extras:

```bash
python -m pip install -e .[dev]
```

CLI usage

```bash
software-engineer World
python -m software_engineer World
```

Configuration

- Set runtime options with environment variables:
  - `APP_ENV` for environment mode (`development`, `production`)
  - `GREETING_PREFIX` to override the greeting prefix

Example

```bash
APP_ENV=production GREETING_PREFIX=Hi software-engineer World
```

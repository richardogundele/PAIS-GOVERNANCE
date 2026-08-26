# Installation

PAIS requires Python 3.10 or later.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn pais_governance.server:app --host 127.0.0.1 --port 8000
```

For tests and local quality checks:

```bash
pip install -e '.[dev]'
ruff check src tests
pytest
```

For the optional legacy spreadsheet-redaction module:

```bash
pip install -e '.[redaction]'
```

Container:

```bash
docker build -t pais-agent-gateway:local .
docker run --rm -p 8000:8000 -v "$PWD/logs:/app/logs" pais-agent-gateway:local
```

The default server has no built-in authentication. Bind it to localhost for development and place it behind an authenticated service boundary for any shared environment.

# WhatsApp ecosystem scaffold

A dependency-light Python foundation for a WhatsApp automation service. It currently
provides:

- SQLite-backed registration, login, and expense tracking.
- WhatsApp webhook challenge verification.
- Optional `X-Hub-Signature-256` HMAC verification.
- WhatsApp webhook message extraction.
- A `pyproject.toml` and pytest suite with no runtime dependencies.

## Setup

```bash
python -m pip install -e '.[dev]'
pytest
```

## Next integration step

Wrap `WhatsAppWebhook` in FastAPI, Flask, or another HTTP framework and connect
its parsed events to the WhatsApp Cloud API using credentials stored in environment
variables. Never commit access tokens or app secrets.

# Rift Backend

Python FastAPI backend for the Rift Batch Changes Platform.

## Setup

```bash
pip install -e ".[dev]"
```

## Running locally

```bash
uvicorn src.main:app --reload
```

## Tests

```bash
pytest tests/
```

## Notes

- Password storage uses a SHA-256 prehash before bcrypt so bootstrap and user passwords can exceed bcrypt's native 72-byte limit.
- Existing legacy raw `$2...` bcrypt hashes still verify during sign-in, so local MongoDB data does not need a one-off migration before starting the API.

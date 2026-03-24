FROM python:3.12-slim AS base

WORKDIR /app

# Install system deps needed by cryptography, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src/ ./src/
# Install runtime deps only (no dev extras)
RUN pip install --no-cache-dir -e .

# ── API target ──────────────────────────────────────────────────────────────
FROM base AS api
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

# ── Temporal Worker target ───────────────────────────────────────────────────
FROM base AS worker
CMD ["python", "-m", "src.workflows.worker"]

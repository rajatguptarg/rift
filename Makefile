.PHONY: dev dev-backend dev-frontend dev-cli \
        test test-backend test-frontend test-cli \
        lint lint-backend lint-frontend \
        format format-backend format-frontend \
        build clean \
        infra-up infra-down \
        docker-up docker-up-build docker-down docker-logs

# ───────────────────────────────────────────
# Dev servers
# ───────────────────────────────────────────
dev: infra-up dev-backend dev-frontend

dev-backend:
	cd backend && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

dev-cli:
	cd cli && npm run dev

# ───────────────────────────────────────────
# Tests
# ───────────────────────────────────────────
test: test-backend test-frontend test-cli

test-backend:
	cd backend && pytest --cov=src --cov-report=term-missing --cov-fail-under=80

test-frontend:
	cd frontend && npm test -- --run --coverage

test-cli:
	cd cli && npm test -- --run

# ───────────────────────────────────────────
# Lint
# ───────────────────────────────────────────
lint: lint-backend lint-frontend

lint-backend:
	cd backend && ruff check src tests

lint-frontend:
	cd frontend && npm run lint

# ───────────────────────────────────────────
# Format
# ───────────────────────────────────────────
format: format-backend format-frontend

format-backend:
	cd backend && ruff format src tests

format-frontend:
	cd frontend && npm run format

# ───────────────────────────────────────────
# Build
# ───────────────────────────────────────────
build:
	cd frontend && npm run build
	cd cli && npm run build

# ───────────────────────────────────────────
# Infrastructure (local — infra only)
# ───────────────────────────────────────────
infra-up:
	docker compose up -d mongodb redis temporal temporal-ui minio minio-init

infra-down:
	docker compose down

# ───────────────────────────────────────────
# Full stack (Docker — all services)
# ───────────────────────────────────────────
docker-up:
	docker compose up -d

docker-up-build:
	docker compose up -d --build

docker-down:
	docker compose down -v

docker-logs:
	docker compose logs -f api worker frontend

# ───────────────────────────────────────────
# Cleanup
# ───────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/dist frontend/coverage cli/dist

.PHONY: dev test build deploy lint format clean

# --- Development ---
dev:
	@echo "Starting DevinClaw Federal development servers..."
	@trap 'kill 0' EXIT; \
	uvicorn src.api.main:app --host 0.0.0.0 --port 8420 --reload & \
	cd dashboard && npm run dev & \
	wait

dev-api:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8420 --reload

dev-dashboard:
	cd dashboard && npm run dev

# --- Testing ---
test:
	pytest tests/ -v --cov=src --cov-report=term-missing
	cd dashboard && npm test -- --passWithNoTests

test-api:
	pytest tests/ -v --cov=src --cov-report=term-missing

test-dashboard:
	cd dashboard && npm test -- --passWithNoTests

# --- Linting ---
lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

format:
	ruff check --fix src/ tests/
	ruff format src/ tests/

# --- Build ---
build:
	docker build -f docker/Dockerfile.api -t devinclaw-api:latest .
	docker build -f docker/Dockerfile.dashboard -t devinclaw-dashboard:latest .

# --- Deploy ---
deploy:
	docker-compose up -d

deploy-down:
	docker-compose down

deploy-logs:
	docker-compose logs -f

# --- Database ---
db-migrate:
	alembic upgrade head

db-revision:
	alembic revision --autogenerate -m "$(msg)"

# --- Clean ---
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov

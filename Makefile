# Agentex Makefile
# Common development commands

.PHONY: help dev dev-backend dev-frontend install test lint format clean docker-up docker-down

# Default target
help:
	@echo "Agentex Development Commands"
	@echo "============================"
	@echo ""
	@echo "Development:"
	@echo "  make dev            - Start both backend and frontend"
	@echo "  make dev-backend    - Start backend server only"
	@echo "  make dev-frontend   - Start frontend dev server only"
	@echo ""
	@echo "Setup:"
	@echo "  make install        - Install all dependencies"
	@echo "  make install-backend  - Install backend dependencies"
	@echo "  make install-frontend - Install frontend dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run all tests"
	@echo "  make test-backend   - Run backend tests"
	@echo "  make test-frontend  - Run frontend tests"
	@echo "  make test-cov       - Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           - Run linters"
	@echo "  make format         - Format code"
	@echo "  make type-check     - Run type checking"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up      - Start all services"
	@echo "  make docker-down    - Stop all services"
	@echo "  make docker-logs    - View service logs"
	@echo ""
	@echo "Database:"
	@echo "  make db-migrate     - Run database migrations"
	@echo "  make db-reset       - Reset database"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Clean generated files"

# ======================
# Development
# ======================

dev: dev-backend dev-frontend

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

# ======================
# Installation
# ======================

install: install-backend install-frontend

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

# ======================
# Testing
# ======================

test: test-backend test-frontend

test-backend:
	cd backend && pytest tests/ -v

test-frontend:
	cd frontend && npm run test

test-cov:
	cd backend && pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# ======================
# Code Quality
# ======================

lint: lint-backend lint-frontend

lint-backend:
	cd backend && ruff check app/ tests/
	cd backend && mypy app/

lint-frontend:
	cd frontend && npm run lint

format: format-backend format-frontend

format-backend:
	cd backend && black app/ tests/
	cd backend && isort app/ tests/
	cd backend && ruff check --fix app/ tests/

format-frontend:
	cd frontend && npm run format

type-check:
	cd backend && mypy app/
	cd frontend && npm run type-check

# ======================
# Docker
# ======================

docker-up:
	docker-compose -f .devcontainer/docker-compose.yml up -d postgres redis milvus-standalone

docker-down:
	docker-compose -f .devcontainer/docker-compose.yml down

docker-logs:
	docker-compose -f .devcontainer/docker-compose.yml logs -f

docker-clean:
	docker-compose -f .devcontainer/docker-compose.yml down -v

# ======================
# Database
# ======================

db-migrate:
	cd backend && alembic upgrade head

db-reset:
	cd backend && alembic downgrade base
	cd backend && alembic upgrade head

# ======================
# Cleanup
# ======================

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true

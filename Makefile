.PHONY: help install dev lint format test coverage clean docker docs

help:
	@echo "PAIS-Governance Development Commands"
	@echo "===================================="
	@echo ""
	@echo "Setup:"
	@echo "  make install      Install dependencies"
	@echo "  make dev          Install dev dependencies"
	@echo ""
	@echo "Quality:"
	@echo "  make lint         Run linters (flake8, mypy)"
	@echo "  make format       Format code with black"
	@echo "  make lint-fix     Fix linting issues automatically"
	@echo ""
	@echo "Testing:"
	@echo "  make test         Run all tests"
	@echo "  make test-unit    Run unit tests only"
	@echo "  make test-int     Run integration tests only"
	@echo "  make coverage     Show test coverage report"
	@echo ""
	@echo "Running:"
	@echo "  make run          Start dev server (localhost:8000)"
	@echo "  make docker       Build Docker image"
	@echo "  make docker-run   Run in Docker container"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        Remove cache and build artifacts"
	@echo "  make clean-all    Also remove virtual environment"
	@echo ""

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

lint:
	flake8 src/ tests/
	mypy src/
	bandit -r src/ -ll

format:
	black src/ tests/

lint-fix:
	black src/ tests/
	flake8 src/ tests/ --select=E,W --fix-in-place

test:
	pytest tests/ -v --cov=src --cov-report=term-missing

test-unit:
	pytest tests/unit/ -v

test-int:
	pytest tests/integration/ -v

coverage:
	pytest tests/ --cov=src --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

run:
	python -m pais_governance.server

docker:
	docker build -t pais-governance:latest .

docker-run:
	docker-compose up -d

docker-logs:
	docker-compose logs -f

docker-stop:
	docker-compose down

clean:
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/ .mypy_cache/ .coverage htmlcov/

clean-all: clean
	rm -rf venv/

docs:
	@echo "Open docs at: docs/"

.DEFAULT_GOAL := help

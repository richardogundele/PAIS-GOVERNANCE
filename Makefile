.PHONY: install dev lint test run benchmark docker

install:
	python -m pip install -e .

dev:
	python -m pip install -e '.[dev]'

lint:
	ruff check src tests

test:
	pytest --cov=pais_governance --cov-report=term-missing

run:
	uvicorn pais_governance.server:app --reload

benchmark:
	python scripts/benchmark.py

docker:
	docker build -t pais-agent-gateway:local .

SHELL := /bin/sh
.PHONY: setup format lint test build security ci up down logs

setup:
	python -m pip install -r requirements-dev.txt

format:
	ruff format app tests

lint:
	ruff check app tests
	ruff format --check app tests

test:
	pytest

build:
	python -m compileall -q app
	docker build -t zttato:local .

security:
	python -m pip check

ci: lint test build security

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f app

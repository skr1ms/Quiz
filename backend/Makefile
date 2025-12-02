# Makefile - shortcuts for setup and common tasks

.PHONY: help install dev-install format lint test run migrate

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	python -m venv .venv
	source .venv/Scripts/activate
	pip install --upgrade pip setuptools wheel
	pip install -r requirements.txt
	pip install -e .

format: ## Format code with ruff
	scripts/format.sh

lint: ## Lint code with ruff
	ruff check src

test: ## Run tests
	pytest tests/ -v

run: ## Run the application
	python -m src.run

migrate: ## Run database migrations
	alembic upgrade head

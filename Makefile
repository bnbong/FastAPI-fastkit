.PHONY: help install install-dev install-test uninstall test test-verbose lint format format-check clean build build-docs serve-docs version-update all

# Default target
help: ## Show this help message
	@echo "FastAPI-fastkit Development Commands"
	@echo "===================================="
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation commands
install: ## Install the package in production mode
	pip install .

install-dev: ## Install the package with development dependencies
	pip install -e ".[dev]"

install-test: ## Install the package for testing purposes
	pip uninstall FastAPI-fastkit -y || true
	pip install -e .

uninstall: ## Uninstall the package
	pip uninstall FastAPI-fastkit -y

# Testing commands
test: ## Run all tests
	pytest

test-verbose: ## Run tests with verbose output
	pytest -v -s

test-coverage: ## Run tests with coverage report
	pytest --cov=src/fastapi_fastkit --cov-report=html --cov-report=term

# Code quality commands
lint: ## Run all linting checks
	@echo "Running isort check..."
	isort --sp pyproject.toml --check .
	@echo "Running black check..."
	black --config pyproject.toml --check .
	@echo "Running mypy check..."
	mypy --config-file pyproject.toml src

format: ## Format code using black and isort
	@echo "Running isort..."
	isort --sp pyproject.toml .
	@echo "Running black..."
	black --config pyproject.toml .

format-check: ## Check code formatting without making changes
	@echo "Checking isort..."
	isort --sp pyproject.toml --check-only --diff .
	@echo "Checking black..."
	black --config pyproject.toml --check --diff .

# Build commands
clean: ## Clean build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/

build: clean ## Build the package
	python -m build

build-wheel: clean ## Build wheel package only
	python -m build --wheel

build-sdist: clean ## Build source distribution only
	python -m build --sdist

# Documentation commands
build-docs: ## Build documentation
	mkdocs build

serve-docs: ## Serve documentation locally
	mkdocs serve

# Development workflow commands
dev-setup: ## Set up development environment from scratch
	@echo "Setting up development environment..."
	pip install --upgrade pip
	pip install -e ".[dev]"
	pip install -e ".[docs]" || pip install -r requirements-docs.txt
	pre-commit install
	@echo "Development environment setup complete!"

dev-check: ## Run all development checks (format, lint, test)
	@echo "Running development checks..."
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) test
	@echo "All checks passed!"

dev-fix: ## Fix formatting and run tests
	@echo "Fixing code formatting..."
	$(MAKE) format
	@echo "Running tests..."
	$(MAKE) test
	@echo "Development fixes complete!"

# Quick commands for contributors
quick-install: ## Quick install for testing (uninstall + install)
	$(MAKE) install-test

quick-test: ## Quick test after code changes
	$(MAKE) format
	$(MAKE) test

all: ## Run complete development workflow
	$(MAKE) clean
	$(MAKE) dev-setup
	$(MAKE) dev-check
	$(MAKE) build

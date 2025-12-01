.PHONY: help lint format-check format typecheck test test-cov test-verbose check

help:
	@echo "Available commands:"
	@echo "  make lint           - Run ruff linter (check only)"
	@echo "  make format-check   - Check if code is formatted"
	@echo "  make format         - Auto-format code with ruff"
	@echo "  make typecheck      - Run mypy type checker"
	@echo "  make test           - Run pytest"
	@echo "  make test-cov       - Run pytest with coverage"
	@echo "  make test-verbose   - Run pytest with verbose output"
	@echo "  make check          - Run all checks (lint + typecheck + test)"

lint:
	uv run ruff check .

format-check:
	uv run ruff format --check .

format:
	uv run ruff format .

typecheck:
	uv run mypy src/

test:
	uv run pytest

test-cov:
	uv run pytest --cov=src/faker_galactic --cov-report=html --cov-report=term

test-verbose:
	uv run pytest -vv

check: lint typecheck test
	@echo "✓ All checks passed!"

.DEFAULT_GOAL := help

.PHONY: help install-test test test-live test-all lint

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install-test: ## Install test dependencies
	uv sync --group test

test: install-test ## Run the mocked unit test suite (excludes live tests)
	uv run pytest

test-live: install-test ## Run the live test suite against the real Tado API (requires real credentials)
	uv run pytest -m live

test-all: install-test ## Run the full test suite, mocked and live
	uv run pytest -m ""

lint: ## Run ruff
	uv run --group lint ruff check .

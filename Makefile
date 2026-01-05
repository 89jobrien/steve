# Steve - Claude Code Components
# Common development workflows

.PHONY: help install dev lint format typecheck test clean index index-fast pre-commit hooks \
        run-index run-list run-install run-publish run-publish-all run-secrets run-metadata run-batch-metadata \
        health audit lint-components stale coverage

# Default target
help:
	@echo "Steve - Claude Code Components"
	@echo ""
	@echo "Setup:"
	@echo "  make install      Install dependencies"
	@echo "  make dev          Install dev dependencies"
	@echo "  make hooks        Install pre-commit hooks"
	@echo ""
	@echo "Quality:"
	@echo "  make lint         Run linter (ruff)"
	@echo "  make format       Format code (ruff)"
	@echo "  make typecheck    Run type checker (mypy)"
	@echo "  make check        Run all checks (lint + typecheck)"
	@echo "  make fix          Auto-fix all issues"
	@echo ""
	@echo "Testing:"
	@echo "  make test         Run tests"
	@echo "  make test-cov     Run tests with coverage"
	@echo ""
	@echo "Components:"
	@echo "  make index        Build component index"
	@echo "  make index-fast   Build index with caching (~4x faster)"
	@echo "  make list         List all components"
	@echo ""
	@echo "Analysis:"
	@echo "  make health       Workspace health report"
	@echo "  make audit        Security audit"
	@echo "  make lint-components  Lint all components"
	@echo "  make stale        Find stale components (use ARGS='--days N')"
	@echo "  make coverage     Tool coverage analysis"
	@echo ""
	@echo "Scripts:"
	@echo "  make run-index    Run build_index.py"
	@echo "  make run-list     Run list_components.py (use ARGS for options)"
	@echo "  make run-install  Run install_component.py (use ARGS='component-name')"
	@echo "  make run-publish  Run publish_to_gist.py (use ARGS for options)"
	@echo "  make run-publish-all Run publish_all.py (use ARGS for options)"
	@echo "  make run-secrets  Run detect_secrets.py"
	@echo "  make run-metadata Run add_metadata.py (use ARGS for options)"
	@echo "  make run-batch-metadata Run batch_add_metadata.py (use ARGS for options)"
	@echo ""
	@echo "Maintenance:"
	@echo "  make pre-commit   Run pre-commit on all files"
	@echo "  make clean        Remove build artifacts"
	@echo "  make update       Update dependencies"

# =============================================================================
# Setup
# =============================================================================

install:
	uv sync

dev:
	uv sync --dev

hooks:
	uv run pre-commit install

# =============================================================================
# Code Quality
# =============================================================================

lint:
	uv run ruff check steve/ scripts/

format:
	uv run ruff format steve/ scripts/

typecheck:
	uv run mypy steve/ scripts/

check: lint typecheck

fix:
	uv run ruff check --fix steve/ scripts/
	uv run ruff format steve/ scripts/

# =============================================================================
# Testing
# =============================================================================

test:
	uv run pytest scripts/tests/ steve/ -v

test-cov:
	uv run pytest scripts/tests/ steve/ -v --cov=steve --cov=scripts --cov-report=term-missing

# =============================================================================
# Components
# =============================================================================

index:
	uv run python scripts/build_index.py

index-fast:
	uv run python scripts/build_index.py --incremental

list:
	uv run python scripts/list_components.py

# =============================================================================
# Analysis
# =============================================================================

health:
	uv run python -m scripts.health

audit:
	uv run python -m scripts.audit

lint-components:
	uv run python -m scripts.lint

stale:
	uv run python -m scripts.stale $(ARGS)

coverage:
	uv run python -m scripts.coverage

# =============================================================================
# Scripts (use ARGS='...' for arguments)
# =============================================================================

ARGS ?=

run-index:
	uv run python scripts/build_index.py $(ARGS)

run-list:
	uv run python scripts/list_components.py $(ARGS)

run-install:
	@if [ -z "$(ARGS)" ]; then \
		echo "Error: Component name required"; \
		echo "Usage: make run-install ARGS='component-name'"; \
		exit 1; \
	fi
	uv run python scripts/install_component.py $(ARGS)

run-publish:
	@if [ -z "$(ARGS)" ]; then \
		echo "Publishing all markdown files in steve/..."; \
		count=0; \
		for file in $$(find steve -name "*.md" -type f | sort); do \
			echo "Publishing: $$file"; \
			if uv run python scripts/publish_to_gist.py "$$file"; then \
				count=$$((count + 1)); \
			else \
				echo "Failed to publish: $$file"; \
				exit 1; \
			fi; \
		done; \
		echo "Successfully published $$count files"; \
	else \
		if echo "$(ARGS)" | grep -q '\*'; then \
			echo "Publishing files matching: $(ARGS)"; \
			count=0; \
			for file in $(ARGS); do \
				echo "Publishing: $$file"; \
				if uv run python scripts/publish_to_gist.py "$$file"; then \
					count=$$((count + 1)); \
				else \
					echo "Failed to publish: $$file"; \
					exit 1; \
				fi; \
			done; \
			echo "Successfully published $$count files"; \
		else \
			echo "Publishing: $(ARGS)"; \
			uv run python scripts/publish_to_gist.py $(ARGS); \
		fi; \
	fi

run-publish-all:
	uv run python scripts/publish_all.py $(ARGS)

run-secrets:
	@if [ -z "$(ARGS)" ]; then \
		echo "Error: Argument required"; \
		echo "Usage:"; \
		echo "  make run-secrets ARGS='--scan'     - Scan for secrets"; \
		echo "  make run-secrets ARGS='--baseline' - Update baseline"; \
		exit 1; \
	fi
	uv run python scripts/detect_secrets.py $(ARGS)

run-metadata:
	@if [ -z "$(ARGS)" ]; then \
		echo "Error: Component path required"; \
		echo "Usage:"; \
		echo "  make run-metadata ARGS='path/to/component.md'"; \
		echo "  make run-metadata ARGS='path/to/component.md --gist-url https://...'"; \
		exit 1; \
	fi
	@if echo "$(ARGS)" | grep -q '\*'; then \
		echo "Adding metadata to files matching: $(ARGS)"; \
		count=0; \
		first_arg=$$(echo "$(ARGS)" | awk '{print $$1}'); \
		rest_args=$$(echo "$(ARGS)" | cut -d' ' -f2-); \
		for file in $$first_arg; do \
			echo "Processing: $$file"; \
			if [ "$$first_arg" = "$$rest_args" ]; then \
				uv run python scripts/add_metadata.py "$$file"; \
			else \
				uv run python scripts/add_metadata.py "$$file" $$rest_args; \
			fi && count=$$((count + 1)); \
		done; \
		echo "Processed $$count files"; \
	else \
		uv run python scripts/add_metadata.py $(ARGS); \
	fi

run-batch-metadata:
	@if [ -z "$(ARGS)" ]; then \
		echo "Error: Arguments required"; \
		echo "Usage:"; \
		echo "  make run-batch-metadata ARGS='steve/agents --key version 1.0'"; \
		echo "  make run-batch-metadata ARGS='steve/agents --key author \"Joseph OBrien\" --key status published'"; \
		echo "  make run-batch-metadata ARGS='steve/skills --dry-run'"; \
		exit 1; \
	fi
	uv run python scripts/batch_add_metadata.py $(ARGS)


# =============================================================================
# Pre-commit
# =============================================================================

pre-commit:
	uv run pre-commit run --all-files

# =============================================================================
# Maintenance
# =============================================================================

clean:
	rm -rf .ruff_cache .mypy_cache .pytest_cache __pycache__
	rm -rf steve/**/__pycache__ scripts/__pycache__
	rm -rf .coverage htmlcov
	rm -rf *.egg-info build dist
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

update:
	uv lock --upgrade
	uv sync --dev
	uv run pre-commit autoupdate

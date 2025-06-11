VENV_PATH := app/online_sys/.venv_online
CHECK_DIRS := .

SHELL := /bin/bash

define run_with_venv
	@if [ -f "$(VENV_PATH)/bin/activate" ]; then \
		source $(VENV_PATH)/bin/activate && $(1); \
	else \
		echo "Virtual environment not found at $(VENV_PATH)"; \
		exit 1; \
	fi
endef

.PHONY: pre-commit format-check lint-check format-fix lint-fix ci install setup-and-ci check

# Pre-commit
pre-commit:
	@echo "⚒️ Running pre-commit hooks..."
	$(call run_with_venv,pre-commit run --all-files)
	@echo "✅ Pre-commit hooks completed successfully!"

# -- CI --

format-check:
	@echo -en "\n⚒️ Running CI format check...\n"
	$(call run_with_venv,uv run ruff format --check $(CHECK_DIRS))
	$(call run_with_venv,uv run ruff check -e)
	$(call run_with_venv,uv run ruff check --select I -e)
	@echo "✅ Format check completed successfully!"

lint-check:
	@echo -en "\n⚒️ Running CI lint check...\n"
	$(call run_with_venv,uv run ruff check $(CHECK_DIRS))
	@echo "✅ Lint check completed successfully!"

format-fix:
	$(call run_with_venv,uv run ruff format $(CHECK_DIRS))
	$(call run_with_venv,uv run ruff check --select I --fix)

lint-fix:
	$(call run_with_venv,uv run ruff check --fix)

# Run all CI checks locally
ci: format-check lint-check

# Install dependencies
install:
	$(call run_with_venv,cd app/online_sys && uv sync --all-extras --dev)
	$(call run_with_venv,cd app/online_sys && uv pip install -e .)

# Setup everything and run checks
setup-and-ci: install ci

# Run full workflow
check: pre-commit ci

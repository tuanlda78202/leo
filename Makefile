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

.PHONY: pre-commit format-check lint-check format-fix lint-fix shellcheck ci install setup-and-ci check act-install act-list act-check act-push act-pull-request act-ci act-clean act-version act

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

shellcheck:
	@echo -en "\n⚒️ Running ShellCheck...\n"
	@if command -v shellcheck >/dev/null 2>&1; then \
		find . -name "*.sh" -type f -exec shellcheck -f gcc -S warning {} \; ; \
		echo "✅ ShellCheck completed successfully!"; \
	else \
		echo "❌ ShellCheck not installed. Install with: brew install shellcheck (macOS) or apt install shellcheck (Ubuntu)"; \
		exit 1; \
	fi

format-fix:
	$(call run_with_venv,uv run ruff format $(CHECK_DIRS))
	$(call run_with_venv,uv run ruff check --select I --fix)

lint-fix:
	$(call run_with_venv,uv run ruff check --fix)

# -- Act (GitHub Actions Local Runner) --

act-install:
	@echo "⚒️ Installing act as GitHub CLI extension..."
	@if command -v gh >/dev/null 2>&1; then \
		gh extension install https://github.com/nektos/gh-act || \
		echo "✅ Act extension already installed or installation completed"; \
	else \
		echo "❌ GitHub CLI not installed. Install with: brew install gh (macOS) or apt-get install gh (Ubuntu)"; \
		echo "   Or install act directly: curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash"; \
		exit 1; \
	fi
	@echo "✅ Act installation completed!"

act-version:
	@echo "📋 Checking act version and info..."
	@if command -v gh >/dev/null 2>&1 && gh extension list | grep -q gh-act; then \
		gh act --version || gh act --help | head -5; \
	elif command -v act >/dev/null 2>&1; then \
		act --version || act --help | head -5; \
	else \
		echo "❌ Act not found. Run 'make act-install' first"; \
		exit 1; \
	fi

act-check:
	@echo "⚒️ Validating GitHub Actions workflows..."
	@if command -v gh >/dev/null 2>&1 && gh extension list | grep -q gh-act; then \
		gh act -l; \
	elif command -v act >/dev/null 2>&1; then \
		act -l; \
	else \
		echo "❌ Act not found. Run 'make act-install' first"; \
		exit 1; \
	fi
	@echo "✅ Act workflow validation completed!"

act-push:
	@echo "⚒️ Running push event workflows locally..."
	@if command -v gh >/dev/null 2>&1 && gh extension list | grep -q gh-act; then \
		gh act push -v --container-architecture linux/amd64; \
	elif command -v act >/dev/null 2>&1; then \
		act push -v --container-architecture linux/amd64; \
	else \
		echo "❌ Act not found. Run 'make act-install' first"; \
		exit 1; \
	fi

act-pull-request:
	@echo "⚒️ Running pull request workflows locally..."
	@if command -v gh >/dev/null 2>&1 && gh extension list | grep -q gh-act; then \
		gh act pull_request -v --container-architecture linux/amd64; \
	elif command -v act >/dev/null 2>&1; then \
		act pull_request -v --container-architecture linux/amd64; \
	else \
		echo "❌ Act not found. Run 'make act-install' first"; \
		exit 1; \
	fi

act-ci:
	@echo "⚒️ Running CI workflow locally..."
	@if command -v gh >/dev/null 2>&1 && gh extension list | grep -q gh-act; then \
		gh act -j ci --container-architecture linux/amd64 || \
		gh act --container-architecture linux/amd64; \
	elif command -v act >/dev/null 2>&1; then \
		act -j ci --container-architecture linux/amd64 || \
		act --container-architecture linux/amd64; \
	else \
		echo "❌ Act not found. Run 'make act-install' first"; \
		exit 1; \
	fi

act-clean:
	@echo "⚒️ Cleaning up act containers and volumes..."
	@docker container prune -f --filter "label=act" 2>/dev/null || true
	@docker volume prune -f --filter "label=act" 2>/dev/null || true
	@docker image prune -f --filter "label=act" 2>/dev/null || true
	@echo "✅ Act cleanup completed!"

# Run all CI checks locally
ci: format-check lint-check shellcheck

# Install dependencies
install:
	$(call run_with_venv,cd app/online_sys && uv sync --all-extras --dev)
	$(call run_with_venv,cd app/online_sys && uv pip install -e .)

# Setup everything and run checks
setup-and-ci: install ci

# Run full workflows
check: pre-commit ci
act: act-check act-push act-clean

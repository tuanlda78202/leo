ifeq (,$(wildcard .env))
$(error .env file is missing. Please create one based on .env.example. Run: "cp .env.example .env" and fill in the missing values.)
endif

include .env

export UV_PROJECT_ENVIRONMENT=.venv_online
export PYTHONPATH = .

# --- Default ---

CHECK_DIRS := .
RETRIEVER_CONFIG ?= configs/rag_index.yaml

# --- Infrastructure ---
local-mongodb-up:
	@echo "Starting local mongodb..."
	docker compose -f ../infra/docker-compose.yml up --build -d 

local-mongodb-stop:
	@echo "Stopping local mongodb..."
	docker compose -f ../infra/docker-compose.yml stop

local-mongodb-down:
	@echo "Stopping and removing local mongodb..."
	docker compose -f ../infra/docker-compose.yml down

local-infra-up: local-mongodb-up

local-infra-stop: local-mongodb-stop

local-infra-down: local-mongodb-down

# --- App ---
run_app:
	uv run python -m tools.app --retriever-config=$(RETRIEVER_CONFIG) --ui

eval_app:
	uv run python -m tools.eval_app --retriever-config=$(RETRIEVER_CONFIG)

# -- CI --
format-fix:
	uv run ruff format $(CHECK_DIRS)
	uv run ruff check --select I --fix 

lint-fix:
	uv run ruff check --fix

format-check:
	uv run ruff format --check $(CHECK_DIRS) 
	uv run ruff check -e
	uv run ruff check --select I -e

lint-check:
	uv run ruff check $(CHECK_DIRS)
	
# --- Utilities ---

help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

check-rag-config:
	@if [ ! -f "$(RETRIEVER_CONFIG)" ]; then \
		echo "Error: Retriever config file '$(RETRIEVER_CONFIG)' does not exist"; \
		exit 1; \
	else \
		echo "Found retriever config file at '$(RETRIEVER_CONFIG)'"; \
	fi
include .env

export UV_PROJECT_ENVIRONMENT=.venv_offline
export PYTHONPATH = .

# --- Default ---

CHECK_DIRS := .
AWS_S3_BUCKET_NAME := decodingml-public-data
NOTION_LOCAL_DATA_PATH := data/notion
CRAWLED_LOCAL_DATA_PATH := data/crawled

# --- Infrastructure ---
local-mongodb-up:
	@echo "Starting local mongodb..."
	docker compose -f ../infra/docker/docker-compose.yml up --build -d 

local-mongodb-stop:
	@echo "Stopping local mongodb..."
	docker compose -f ../infra/docker/docker-compose.yml stop

local-mongodb-down:
	@echo "Stopping and removing local mongodb..."
	docker compose -f ../infra/docker/docker-compose.yml down

local-zenml-up:
	@echo "Starting local zenml server..."
	uv run zenml login --local

local-zenml-stop:
	@echo "Stopping local zenml server..."
	uv run zenml logout --local

local-infra-up: local-mongodb-up local-zenml-up

local-infra-stop: local-mongodb-stop local-zenml-stop

local-infra-down: local-mongodb-down local-zenml-stop
# --- S3 ---

# -- Offline ML pipelines -- 
collect-notion-data-pipeline:
	@echo "Collecting Notion data..."
	uv run python -m tools.run --run-collect-notion-data-pipeline --no-cache

# -- Test API -- 

# --- PyTest ---

# -- Format --
# --- Utilities ---
help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

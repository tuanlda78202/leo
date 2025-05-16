include .env

export UV_PROJECT_ENVIRONMENT=.venv
export PYTHONPATH = .

# --- Default ---

CHECK_DIRS := .
AWS_S3_BUCKET_NAME := decodingml-public-data
NOTION_LOCAL_DATA_PATH := data/notion
CRAWLED_LOCAL_DATA_PATH := data/crawled

# --- Infrastructure ---

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

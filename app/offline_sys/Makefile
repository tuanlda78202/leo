include .env

export UV_PROJECT_ENVIRONMENT=.venv_offline
export PYTHONPATH = .
export ZENML_AUTO_OPEN_DASHBOARD=false

# --- Default ---
CHECK_DIRS := .
AWS_S3_BUCKET_NAME := tuanlda78202-data
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

# --- AWS ---
validate_aws_credentials:
	@echo "Validating AWS credentials..."
	uv run python -m tools.validate_aws_credentials

s3-upload-notion: 
	@echo "Uploading raw Notion dataset to S3 bucket: $(AWS_S3_BUCKET_NAME)/llm-sys/notion"
	uv run python -m tools.use_s3 upload $(NOTION_LOCAL_DATA_PATH) $(AWS_S3_BUCKET_NAME) --s3-prefix llm-sys/notion

s3-download-notion:
	@echo "Downloading raw Notion dataset from S3 bucket: $(AWS_S3_BUCKET_NAME)/llm-sys/notion/notion.zip"
	uv run python -m tools.use_s3 download $(AWS_S3_BUCKET_NAME) llm-sys/notion/notion.zip $(NOTION_LOCAL_DATA_PATH) --no-sign-request

s3-upload-crawled:
	@echo "Uploading crawled dataset to S3 bucket: $(AWS_S3_BUCKET_NAME)/llm-sys/crawled"
	uv run python -m tools.use_s3 upload $(CRAWLED_LOCAL_DATA_PATH) $(AWS_S3_BUCKET_NAME) --s3-prefix llm-sys/crawled

s3-download-crawled:
	@echo "Downloading crawled dataset from S3 bucket: $(AWS_S3_BUCKET_NAME)/llm-sys/crawled/crawled.zip"
	uv run python -m tools.use_s3 download $(AWS_S3_BUCKET_NAME) llm-sys/crawled/crawled.zip $(CRAWLED_LOCAL_DATA_PATH) --no-sign-request


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

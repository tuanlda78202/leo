ifeq (,$(wildcard .env))
$(error .env file is missing. Please create one based on .env.example. Run: "cp .env.example .env" and fill in the missing values.)
endif

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
# ! MongoDB
offline-mongodb-up:
	@echo "Starting local mongodb..."
	docker compose -f ../infra/docker-compose.dev.yaml up --build -d leo-offline-db
offline-mongodb-stop:
	@echo "Stopping local mongodb..."
	docker compose -f ../infra/docker-compose.dev.yaml stop leo-offline-db
offline-mongodb-down:
	@echo "Stopping and removing local mongodb..."
	docker compose -f ../infra/docker-compose.dev.yaml down leo-offline-db

# ! ZenML
offline-zenml-up:
	@echo "Starting local zenml server..."
	uv run zenml login --local
offline-zenml-stop:
	@echo "Stopping local zenml server..."
	uv run zenml logout --local

# ! Full Infra
offline-infra-up: offline-mongodb-up offline-zenml-up
offline-infra-stop: offline-mongodb-stop offline-zenml-stop
offline-infra-down: offline-mongodb-down offline-zenml-stop

# --- AWS ---
validate_aws_credentials:
	@echo "Validating AWS credentials..."
	uv run python -m tools.validate_aws_credentials

s3-upload-notion:
	@echo "Uploading raw Notion dataset to S3 bucket: $(AWS_S3_BUCKET_NAME)/leo/notion"
	uv run python -m tools.use_s3 upload $(NOTION_LOCAL_DATA_PATH) $(AWS_S3_BUCKET_NAME) --s3-prefix leo/notion

s3-download-notion:
	@echo "Downloading raw Notion dataset from S3 bucket: $(AWS_S3_BUCKET_NAME)/leo/notion/notion.zip"
	uv run python -m tools.use_s3 download $(AWS_S3_BUCKET_NAME) leo/notion/notion.zip $(NOTION_LOCAL_DATA_PATH) --no-sign-request

s3-upload-crawled:
	@echo "Uploading crawled dataset to S3 bucket: $(AWS_S3_BUCKET_NAME)/leo/crawled"
	uv run python -m tools.use_s3 upload $(CRAWLED_LOCAL_DATA_PATH) $(AWS_S3_BUCKET_NAME) --s3-prefix leo/crawled

s3-download-crawled:
	@echo "Downloading crawled dataset from S3 bucket: $(AWS_S3_BUCKET_NAME)/leo/crawled/crawled.zip"
	uv run python -m tools.use_s3 download $(AWS_S3_BUCKET_NAME) leo/crawled/crawled.zip $(CRAWLED_LOCAL_DATA_PATH) --no-sign-request

# -- Offline ML pipelines --
collect-notion-data-pipeline:
	@echo "Collecting Notion data..."
	uv run python -m tools.run --run-collect-notion-data-pipeline --no-cache

etl-pipeline:
	@echo "Running ETL pipeline..."
	uv run python -m tools.run --run-etl-pipeline --no-cache

gen-data-pipeline:
	@echo "Generating summarization dataset..."
	uv run python -m tools.run --run-gen-data-pipeline --no-cache

rag-index-pipeline:
	@echo "Running RAG index pipeline..."
	uv run python -m tools.run --run-rag-index-pipeline --no-cache

# --- Utilities ---
help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

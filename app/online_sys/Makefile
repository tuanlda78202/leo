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
# ! MongoDB
offline-mongodb-up:
	@echo "✅ Starting local MongoDB..."
	docker compose -f ../infra/docker-compose.dev.yaml up --build -d leo-offline-db
offline-mongodb-stop:
	@echo "🛑 Stopping local MongoDB..."
	docker compose -f ../infra/docker-compose.dev.yaml stop leo-offline-db
offline-mongodb-down:
	@echo "❌Stopping and removing local MongoDB..."
	docker compose -f ../infra/docker-compose.dev.yaml down leo-offline-db

# ! BE
online-be-up:
	@echo "✅ Starting online BE..."
	docker compose -f ../infra/docker-compose.dev.yaml up --build -d leo-online-be
online-be-stop:
	@echo "🛑 Stopping online BE..."
	docker compose -f ../infra/docker-compose.dev.yaml stop leo-online-be
online-be-down:
	@echo "❌ Stopping and removing online BE..."
	docker compose -f ../infra/docker-compose.dev.yaml down leo-online-be

# ! FE
online-fe-up:
	@echo "✅ Starting online FE..."
	docker compose -f ../infra/docker-compose.dev.yaml up --build -d leo-online-fe
online-fe-stop:
	@echo "🛑 Stopping online FE..."
	docker compose -f ../infra/docker-compose.dev.yaml stop leo-online-fe
online-fe-down:
	@echo "❌ Stopping and removing online FE..."
	docker compose -f ../infra/docker-compose.dev.yaml down leo-online-fe

# ! Dev
online-dev-up: offline-mongodb-up online-be-up
online-dev-stop: offline-mongodb-stop online-be-stop
online-dev-down: offline-mongodb-down online-be-down

# ! Full Infra
online-infra-up: offline-mongodb-up online-be-up online-fe-up
online-infra-stop: offline-mongodb-stop online-be-stop online-fe-stop
online-infra-down: offline-mongodb-down online-be-down online-fe-down

# --- App ---
api:
	@echo "Starting API server..."
	uvicorn tools.api:app --host 0.0.0.0 --port 7820 --reload

eval-api:
	@echo "Testing API..."
	chmod +x ./tools/eval_api.sh
	./tools/eval_api.sh $(LEO_SK)

eval-app:
	uv run python -m tools.eval_app --retriever-config=$(RETRIEVER_CONFIG)

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

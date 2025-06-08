#!/bin/bash

# Get arguments or use defaults
API_KEY="${1:-leo-secret-api-key}"
BASE_URL="${2:-http://localhost:7820}"
TASK="${3:-What is the weather in Vietnam?}"

echo "Configuration:"
echo "  API Key: ${API_KEY:0:8}..."
echo "  Base URL: $BASE_URL"
echo "  Task: $TASK"
echo ""

echo "Testing health check..."
curl -X GET "$BASE_URL/health"

echo -e "\n\nTesting chat endpoint..."
curl -X POST "$BASE_URL/v1/chat" \
    -H "Content-Type: application/json" \
    -H "Leo-API-Key: $API_KEY" \
    -d "{\"task\": \"$TASK\"}" | jq '.'

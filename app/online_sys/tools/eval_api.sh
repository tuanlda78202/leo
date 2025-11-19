#!/bin/bash

if [ -f .env ]; then
    export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
fi

BASE_URL="${1:-http://localhost:7820}"
TASK="${2:-What is the current weather in Vietnam?}"

echo "Configuration:"
echo "  Leo API Key: ${LEO_SK:0:8}..."
echo "  Base URL: $BASE_URL"
echo "  Task: $TASK"
echo ""

# ! Health Test
echo "Testing health..."
curl -X GET "$BASE_URL/health"

# ! Chat Endpoint Test
echo -e "\n\nTesting chat endpoint..."
curl -X POST "$BASE_URL/v1/chat" \
    -H "Content-Type: application/json" \
    -H "Leo-API-Key: $LEO_SK" \
    -d "{\"task\": \"$TASK\"}" | jq '.'

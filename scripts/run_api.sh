#!/bin/bash

# OpenEncroachment API Server Runner
# This script starts the FastAPI server for the OpenEncroachment API

set -e

# Default values
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
WORKERS=${WORKERS:-1}
RELOAD=${RELOAD:-false}

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY environment variable is not set"
    echo "Please set it with: export OPENAI_API_KEY=your_key_here"
    exit 1
fi

echo "Starting OpenEncroachment API server..."
echo "Host: $HOST"
echo "Port: $PORT"
echo "Workers: $WORKERS"
echo "Reload: $RELOAD"

# Build reload flag
RELOAD_FLAG=""
if [ "$RELOAD" = "true" ]; then
    RELOAD_FLAG="--reload"
fi

# Run the server
uv run uvicorn \
    open_encroachment.api:app \
    --host $HOST \
    --port $PORT \
    --workers $WORKERS \
    $RELOAD_FLAG

echo "API server stopped."

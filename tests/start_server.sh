#!/bin/bash
# Helper script to start the Flask server for testing
# Usage: ./tests/start_server.sh [port]

PORT=${1:-5001}
HOST=${2:-0.0.0.0}

echo "Starting Flask server on $HOST:$PORT..."
echo "Press Ctrl+C to stop the server"
echo ""

# Activate conda environment
source ~/miniconda3/bin/activate whisper-hindi

# Start the server
python web_server.py --host $HOST --port $PORT
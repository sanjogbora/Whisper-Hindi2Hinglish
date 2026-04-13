#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Start the web server with GPU (CUDA) device on port 5001
python web_server.py --device cuda --port 5001
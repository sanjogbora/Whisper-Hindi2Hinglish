#!/bin/bash
# Start ComfyUI server for voice cloning

echo "Starting ComfyUI server..."

cd /home/ishanp/Documents/GitHub/ComfyUI

# Check if we need to activate a conda environment
if [ -n "$CONDA_DEFAULT_ENV" ]; then
    echo "Already in conda environment: $CONDA_DEFAULT_ENV"
else
    echo "Activating whisper-hindi environment..."
    source ~/miniconda3/etc/profile.d/conda.sh
    conda activate whisper-hindi
fi

# Check if ComfyUI is already running
if curl -s http://127.0.0.1:8188/system_stats > /dev/null 2>&1; then
    echo "ComfyUI is already running at http://127.0.0.1:8188"
    exit 0
fi

# Start ComfyUI
echo "Starting ComfyUI on http://127.0.0.1:8188"
python main.py --listen 127.0.0.1 --port 8188

# Alternative: Run in background
# nohup python main.py --listen 127.0.0.1 --port 8188 > comfyui.log 2>&1 &
# echo "ComfyUI started in background. PID: $!"
# echo "Logs: comfyui.log"
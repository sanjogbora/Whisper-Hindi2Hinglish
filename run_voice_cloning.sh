#!/bin/bash
# Quick start script for voice cloning pipeline

set -e

echo "============================================================"
echo "Voice Cloning Pipeline - Quick Start"
echo "============================================================"

# Activate conda environment
echo "[1/4] Activating conda environment..."
source ~/miniconda3/etc/profile.d/conda.sh
conda activate whisper-hindi

# Install additional dependencies
echo "[2/4] Installing additional dependencies..."
pip install -q requests librosa soundfile

# Start ComfyUI (in background)
echo "[3/4] Starting ComfyUI server..."
cd /home/ishanp/Documents/GitHub/ComfyUI

# Check if already running
if curl -s http://127.0.0.1:8188/system_stats > /dev/null 2>&1; then
    echo "ComfyUI is already running"
else
    echo "Starting ComfyUI in background..."
    nohup python main.py --listen 127.0.0.1 --port 8188 > /tmp/comfyui.log 2>&1 &
    COMFYUI_PID=$!
    echo "ComfyUI started (PID: $COMFYUI_PID)"
    echo "Waiting for server to be ready..."
    
    # Wait for server to start
    for i in {1..30}; do
        if curl -s http://127.0.0.1:8188/system_stats > /dev/null 2>&1; then
            echo "ComfyUI is ready!"
            break
        fi
        echo "  Waiting... ($i/30)"
        sleep 2
    done
fi

# Run voice cloning pipeline
echo "[4/4] Running voice cloning pipeline..."
cd /home/ishanp/Documents/GitHub/Whisper-Hindi2Hinglish
python voice_cloning_pipeline.py

# Ask if user wants to embed audio
echo ""
read -p "Embed audio into video? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python embed_audio.py
fi

echo ""
echo "============================================================"
echo "Pipeline complete!"
echo "============================================================"
echo ""
echo "Output files:"
echo "  Segments: voice_cloned_segments/"
echo "  Combined audio: The_Archetypical_Mind_VoiceCloned.wav"
echo "  Final video: The_Archetypical_Mind_VoiceCloned.mp4"
echo ""
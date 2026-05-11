#!/bin/bash
# Whisper-Hindi2Hinglish Video to SRT Converter
# Optimized for GPU with CUDA support

set -e

# Activate conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate whisper-hindi

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Whisper-Hindi2Hinglish Video to SRT Converter ===${NC}"
echo -e "${GREEN}Using GPU with CUDA acceleration${NC}"
echo ""

# Check if video file is provided
if [ -z "$1" ]; then
    echo -e "${YELLOW}Usage: $0 <video_path> [model_id]${NC}"
    echo ""
    echo "Available models:"
    echo "  - Swift: Oriserve/Whisper-Hindi2Hinglish-Swift (default, faster, works on GPU)"
    echo "  - Prime: Oriserve/Whisper-Hindi2Hinglish-Prime (better accuracy, needs more GPU memory)"
    echo ""
    echo "Examples:"
    echo "  $0 ~/Videos/video.mp4"
    echo "  $0 ~/Videos/video.mp4 Oriserve/Whisper-Hindi2Hinglish-Prime"
    exit 1
fi

VIDEO_PATH="$1"
MODEL_ID="${2:-Oriserve/Whisper-Hindi2Hinglish-Swift}"

# Check if video file exists
if [ ! -f "$VIDEO_PATH" ]; then
    echo -e "${YELLOW}Error: Video file not found: $VIDEO_PATH${NC}"
    exit 1
fi

echo "Video: $VIDEO_PATH"
echo "Model: $MODEL_ID"
echo ""

# Run the conversion
python video_to_srt.py "$VIDEO_PATH" --model-id "$MODEL_ID" --device cuda

echo ""
echo -e "${GREEN}=== Done! ===${NC}"
echo -e "${BLUE}SRT file: $(basename "$VIDEO_PATH" | sed 's/\.[^.]*$//').srt${NC}"
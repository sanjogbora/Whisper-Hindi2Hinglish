# Whisper-Hindi2Hinglish - Complete Workflow

## Quick Start

### GPU Mode (Recommended - 60x faster)

```bash
./convert-video.sh ~/Videos/your_video.mp4
```

### Using Prime Model (better accuracy, needs more GPU memory)

```bash
./convert-video.sh ~/Videos/your_video.mp4 Oriserve/Whisper-Hindi2Hinglish-Prime
```

### Using CPU Mode (fallback)

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate whisper-hindi
python video_to_srt.py ~/Videos/your_video.mp4 --model-id Oriserve/Whisper-Hindi2Hinglish-Prime --device cpu
```

## Performance Comparison

| Mode | Model | Time for 105s video | Speedup |
|------|-------|---------------------|---------|
| GPU  | Swift | 4 seconds           | 60x     |
| GPU  | Prime | N/A (OOM on 8GB)    | -       |
| CPU  | Prime | 4 minutes           | 1x      |
| CPU  | Swift | ~3 minutes          | 1.3x    |

## Setup (Already Done)

### 1. Conda Environment Created
```bash
conda create -n whisper-hindi python=3.11
```

### 2. CUDA PyTorch Installed
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 3. Dependencies Installed
```bash
pip install whisper-timestamped transformers librosa soundfile huggingface-hub
```

## Models

### Swift Model (Default)
- **Model ID**: `Oriserve/Whisper-Hindi2Hinglish-Swift`
- **Best for**: Fast processing, works well on GPU
- **Memory**: ~2-3 GB GPU
- **Quality**: Good for most use cases

### Prime Model
- **Model ID**: `Oriserve/Whisper-Hindi2Hinglish-Prime`
- **Best for**: Highest accuracy
- **Memory**: ~5-6 GB GPU (may not fit on 8GB GPU with desktop running)
- **Quality**: Best for final production

## Troubleshooting

### GPU Out of Memory
- Use Swift model instead of Prime
- Close other GPU applications (browser, games)
- Run on CPU as fallback

### CUDA Not Available
```bash
# Verify CUDA
python -c "import torch; print(torch.cuda.is_available())"

# If False, reinstall PyTorch with CUDA
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Conda Environment Issues
```bash
# Recreate environment
conda deactivate
conda remove -n whisper-hindi --all
conda create -n whisper-hindi python=3.11
conda activate whisper-hindi
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install whisper-timestamped transformers librosa soundfile huggingface-hub
```

## Web Server (Optional)

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate whisper-hindi
python web_server.py --device cuda --port 5001
```

Then open: http://localhost:5001

## Files

- `convert-video.sh` - Quick conversion script
- `video_to_srt.py` - Main conversion script
- `web_server.py` - Web interface
- `utils.py` - Utility functions
- `logger.py` - Logging module

## Output

SRT file is saved with the same name as the video:
- Input: `~/Videos/video.mp4`
- Output: `./video.srt`

## System Requirements

- Python 3.11 (via conda)
- CUDA 12.1
- NVIDIA GPU (tested on RTX 2060 SUPER 8GB)
- FFmpeg (for audio extraction)

## Notes

- Swift model is recommended for 8GB GPU
- Prime model may require 12GB+ GPU or CPU mode
- VAD is disabled (torchaudio compatibility issue with Python 3.14)
- Word-level timestamps work correctly
- Subtitle coverage is typically 99%+
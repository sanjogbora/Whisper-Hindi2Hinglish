# Installation Guide

Complete installation instructions for Whisper-Hindi2Hinglish + Video-to-SRT.

---

## Prerequisites

### Required Software

1. **Python 3.10 or higher**
   ```bash
   python --version  # Should show 3.10+
   ```

2. **FFmpeg** (Required for video/audio processing)

   **Windows:**
   ```bash
   # Download from: https://ffmpeg.org/download.html
   # Or use Chocolatey:
   choco install ffmpeg
   ```

   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```

   **macOS:**
   ```bash
   brew install ffmpeg
   ```

   **Verify installation:**
   ```bash
   ffmpeg -version
   ```

3. **Git** (for cloning)
   ```bash
   git --version
   ```

---

## Installation Methods

### Method 1: Quick Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/sanjogbora/Whisper-Hindi2Hinglish.git
cd Whisper-Hindi2Hinglish

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Method 2: Install from GitHub (pip)

```bash
pip install git+https://github.com/sanjogbora/Whisper-Hindi2Hinglish.git
```

### Method 3: Docker

```bash
# Clone repository
git clone https://github.com/sanjogbora/Whisper-Hindi2Hinglish.git
cd Whisper-Hindi2Hinglish

# Build and run
docker-compose up
```

---

## GPU Setup (Recommended for Performance)

### CUDA Installation

1. **Install NVIDIA CUDA Toolkit 12.1+**
   - Download from: https://developer.nvidia.com/cuda-downloads

2. **Verify CUDA:**
   ```bash
   nvidia-smi
   ```

3. **Install PyTorch with CUDA:**
   ```bash
   pip install torch==2.5.1+cu121 torchaudio==2.5.1+cu121 torchvision==0.20.1+cu121 --index-url https://download.pytorch.org/whl/cu121
   ```

4. **Verify PyTorch GPU:**
   ```python
   import torch
   print(torch.cuda.is_available())  # Should print: True
   print(torch.cuda.get_device_name(0))  # Shows your GPU
   ```

### Performance Comparison

| Hardware | Model | Processing Time (10 min video) |
|----------|-------|-------------------------------|
| CPU | Swift | ~15 minutes |
| CPU | Prime | ~30 minutes |
| GPU (RTX 3060) | Swift | ~2 minutes |
| GPU (RTX 3060) | Prime | ~4 minutes |

---

## Verification

### Test Video-to-SRT

```bash
# Start web server
python web_server.py

# Open browser
# http://localhost:5000
```

### Test WebSocket Streaming

```bash
# Terminal 1: Start server
python websocket_server.py

# Terminal 2: Test with file
python client_file.py --wav-path examples/example.wav
```

---

## Optional: Microphone Support

For real-time microphone transcription:

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

---

## Troubleshooting

### FFmpeg Not Found

**Error:** `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`

**Solution:**
- Ensure FFmpeg is in your PATH
- Restart terminal after installation
- Verify with: `ffmpeg -version`

### CUDA Out of Memory

**Error:** `torch.cuda.OutOfMemoryError`

**Solutions:**
- Use Swift model instead of Prime
- Reduce video resolution
- Close other GPU applications
- Use CPU mode: `--device cpu`

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'transformers'`

**Solution:**
```bash
pip install -r requirements.txt
```

---

## Next Steps

- **Video Subtitles**: [Video-to-SRT Guide](VIDEO_TO_SRT.md)
- **Real-time Transcription**: [WebSocket Streaming](WEBSOCKET_STREAMING.md)
- **API Integration**: [API Reference](API_REFERENCE.md)

---

[← Back to Documentation Index](README.md)

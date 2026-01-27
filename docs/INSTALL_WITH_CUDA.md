# Installation Guide with CUDA Support

This guide helps you install the Video to SRT Converter with GPU acceleration.

## Prerequisites

### 1. NVIDIA GPU
- Check if you have an NVIDIA GPU: `nvidia-smi`
- Note your CUDA version (e.g., 12.7, 12.1, 11.8)

### 2. FFmpeg
```bash
winget install ffmpeg
```
Verify: `ffmpeg -version`

## Installation Steps

### Step 1: Install PyTorch with CUDA

**For CUDA 12.1** (recommended for most systems):
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**For CUDA 11.8** (if you have older drivers):
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**For CUDA 12.4+** (latest):
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

### Step 2: Install Other Dependencies
```bash
pip install accelerate librosa numpy transformers webrtcvad websockets flask werkzeug
```

Or use the requirements file (but skip torch):
```bash
pip install accelerate==1.2.1 librosa==0.10.2.post1 numpy==1.26.4 transformers==4.47.1 webrtcvad==2.0.10 websockets==14.1 flask==3.0.0 werkzeug==3.0.1
```

### Step 3: Verify CUDA Installation
```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

Expected output:
```
CUDA available: True
GPU: NVIDIA GeForce RTX 4070 Laptop GPU
```

### Step 4: Start the Server
```bash
python api_server.py
```

## Troubleshooting

### "CUDA available: False"
**Problem**: PyTorch installed without CUDA support

**Solution**: Uninstall and reinstall with CUDA:
```bash
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### "Torch not compiled with CUDA enabled"
**Problem**: CPU version of PyTorch installed

**Solution**: Same as above - reinstall with CUDA support

### "CUDA out of memory"
**Problem**: GPU doesn't have enough memory

**Solutions**:
1. Close other GPU applications
2. Use CPU mode: `python api_server.py --device cpu`
3. Process shorter videos

### Wrong CUDA Version
**Problem**: PyTorch CUDA version doesn't match your system

**Solution**: 
1. Check your CUDA version: `nvidia-smi` (look at top right)
2. Install matching PyTorch version (see Step 1)
3. PyTorch CUDA 12.1 works with system CUDA 12.1-12.7

## Performance Comparison

| Mode | Speed | When to Use |
|------|-------|-------------|
| **GPU (CUDA)** | 10-20x faster | Default, recommended |
| **CPU** | Slower | No GPU or CUDA issues |

## CPU-Only Installation

If you don't have an NVIDIA GPU or want CPU mode:

```bash
pip install -r requirements.txt
python api_server.py --device cpu
```

## Verify Installation

Run the test script:
```bash
python test_video_to_srt.py
```

Should show:
- ✓ FFmpeg is installed
- ✓ torch is installed
- ✓ transformers is installed
- ✓ flask is installed

## Next Steps

1. Start server: `python api_server.py`
2. Open browser: http://localhost:5000
3. Upload video and test!

---

**Your Current Setup** (as of last check):
- GPU: NVIDIA GeForce RTX 4070 Laptop GPU ✓
- CUDA: 12.1 ✓
- PyTorch: 2.5.1+cu121 ✓
- Status: Ready to use! 🎉

# Automatic CPU Fallback

## Overview

The system now automatically detects if CUDA (GPU) is available and falls back to CPU if needed. This ensures the application works on any machine, whether it has a GPU or not.

## Problem (Before Fix)

Users without CUDA-enabled GPUs encountered this error:

```
Error processing video: Attempting to deserialize object on a CUDA device
but torch.cuda.is_available() is False. If you are running on a CPU-only
machine, please use torch.load with map_location=torch.device('cpu') to
map your storages to the CPU.
```

This happened because:
1. The code defaulted to `device='cuda'`
2. Models were loaded without checking CUDA availability
3. No automatic fallback to CPU was implemented

## Solution (After Fix)

### Automatic Device Detection

A new `get_device()` function in `utils.py` automatically:
1. ✅ Checks if CUDA is available
2. ✅ Falls back to CPU if CUDA is unavailable
3. ✅ Logs helpful messages about which device is being used
4. ✅ Provides installation instructions for CUDA if needed

### What Was Changed

**1. `utils.py` - New Device Detection Function**
```python
def get_device(preferred_device: str = "cuda") -> str:
    """
    Automatically detect available device with fallback to CPU.

    - If CUDA requested but unavailable → falls back to CPU with warning
    - If CPU requested → uses CPU
    - Logs GPU name if CUDA available
    - Provides CUDA installation instructions if needed
    """
```

**2. `utils.py` - Updated `load_pipe()` Function**
- Calls `get_device()` to ensure valid device
- Automatically switches to float32 for CPU (float16 not supported on CPU)

**3. `video_to_srt.py` - Updated `video_to_srt()` Function**
- Calls `get_device()` at the start
- Auto-detects device before model loading

**4. `web_server.py` - Updated Initialization**
- Calls `get_device()` when server starts
- Shows actual device being used in logs

**5. `websocket_server.py` - Already Fixed**
- Uses `load_pipe()` which now has automatic detection

---

## How It Works Now

### GPU Available (CUDA)
```bash
$ python web_server.py
✓ Using GPU: NVIDIA GeForce RTX 3080
Starting API server on http://0.0.0.0:5000
Using model: Oriserve/Whisper-Hindi2Hinglish-Swift
Device: cuda, dtype: torch.float16
```

### GPU Not Available (CPU Fallback)
```bash
$ python web_server.py
⚠ CUDA not available. Falling back to CPU (slower performance)
💡 To use GPU, install CUDA-enabled PyTorch:
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
Using CPU for inference
Starting API server on http://0.0.0.0:5000
Using model: Oriserve/Whisper-Hindi2Hinglish-Swift
Device: cpu, dtype: torch.float32
```

### Explicit CPU Request
```bash
$ python web_server.py --device cpu
Using CPU for inference
Starting API server on http://0.0.0.0:5000
Using model: Oriserve/Whisper-Hindi2Hinglish-Swift
Device: cpu, dtype: torch.float32
```

---

## Performance Impact

| Device | Model | Speed | Accuracy |
|--------|-------|-------|----------|
| **NVIDIA GPU (CUDA)** | Swift | ~10-15x real-time | High |
| **NVIDIA GPU (CUDA)** | Prime | ~5-8x real-time | Very High |
| **CPU (Intel i7/i9)** | Swift | ~0.5-1x real-time | High |
| **CPU (Intel i7/i9)** | Prime | ~0.2-0.5x real-time | Very High |

**Recommendation**: Use GPU for production, CPU works but is slower.

---

## For Users

### No Action Required!

The system automatically handles device selection. Just run your command:

```bash
# Video-to-SRT
python video_to_srt.py video.mp4

# Web Server
python web_server.py

# WebSocket Server
python websocket_server.py
```

The application will:
- ✅ Use GPU if available (fast)
- ✅ Fall back to CPU if no GPU (slower but works)
- ✅ Tell you which device is being used
- ✅ Provide GPU installation help if needed

### Want to Use GPU?

If you see the CPU fallback warning and want to use GPU:

**1. Check if you have an NVIDIA GPU:**
```bash
nvidia-smi
```

**2. Install CUDA Toolkit:**
- Download from: https://developer.nvidia.com/cuda-downloads

**3. Install CUDA-enabled PyTorch:**
```bash
pip uninstall torch torchvision torchaudio
pip install torch==2.5.1+cu121 torchvision==0.20.1+cu121 torchaudio==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121
```

**4. Verify:**
```python
import torch
print(torch.cuda.is_available())  # Should print True
```

---

## For Developers

### Using Device Detection in Your Code

```python
from utils import get_device

# Automatic detection with default preference for CUDA
device = get_device("cuda")  # Returns "cuda" or "cpu"

# Explicit CPU request
device = get_device("cpu")  # Always returns "cpu"

# Use in model loading
model = load_model(model_id, device=device)
```

### Testing CPU Fallback

To test CPU fallback even if you have a GPU:

```bash
# Force CPU usage
python video_to_srt.py video.mp4 --device cpu
python web_server.py --device cpu
python websocket_server.py --device cpu
```

### Troubleshooting Device Issues

**Problem**: CUDA available but still using CPU
**Solution**: Check for mixed PyTorch versions
```bash
pip list | grep torch
# All torch packages should have same CUDA version (+cu121)
```

**Problem**: CUDA error during model loading
**Solution**: Update GPU drivers
```bash
nvidia-smi  # Check driver version
# Update from: https://www.nvidia.com/drivers
```

---

## Technical Details

### Device Detection Logic

```python
if preferred_device == "cuda":
    if torch.cuda.is_available():
        device = "cuda"
        logger.info(f"✓ Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = "cpu"
        logger.warning("⚠ CUDA not available. Falling back to CPU")
        logger.info("💡 To use GPU, install CUDA-enabled PyTorch...")
else:
    device = "cpu"
    logger.info("Using CPU for inference")
```

### Dtype Adjustment for CPU

```python
if device == "cpu" and torch_dtype == torch.float16:
    logger.info("Switching to float32 for CPU compatibility")
    torch_dtype = torch.float32
```

**Why?** PyTorch on CPU doesn't support float16 operations efficiently. Float32 is the standard for CPU inference.

---

## Testing

### Unit Test
```python
from utils import get_device
import torch

def test_device_detection():
    device = get_device("cuda")
    assert device in ["cuda", "cpu"]

    if torch.cuda.is_available():
        assert device == "cuda"
    else:
        assert device == "cpu"
```

### Integration Test
```bash
# Run video conversion on CPU
python video_to_srt.py test_video.mp4 --device cpu

# Verify it completes without CUDA errors
```

---

## Changelog

### v1.0.1 (2026-01-30)
- ✅ Added automatic CPU fallback when CUDA unavailable
- ✅ Added `get_device()` helper function in `utils.py`
- ✅ Updated `video_to_srt.py`, `web_server.py`, `websocket_server.py`
- ✅ Added informative logging for device selection
- ✅ Added CUDA installation instructions in warnings
- ✅ Automatic float16 → float32 conversion for CPU

---

## See Also

- [Installation Guide](INSTALLATION.md) - Setting up GPU support
- [FAQ](FAQ.md) - Common device-related questions
- [Performance Tuning](../README.md#performance) - Optimizing for your hardware

---

[← Back to Documentation](README.md)

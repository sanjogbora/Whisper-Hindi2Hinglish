# Quick Start Guide

## Setup Complete ✓

Your Whisper-Hindi2Hinglish video caption generator is configured and ready!

## How to Use

### Option 1: Web Interface (Recommended)

1. Start the server:
   ```bash
   ./start.sh
   ```

2. Open your browser to: http://localhost:5001

3. Upload your video file (mp4, avi, mov, mkv, etc.)

4. Select model:
   - **Swift**: Faster processing (good for quick results)
   - **Prime**: Better accuracy (recommended for final captions)

5. Click "Generate SRT File" and download your subtitles!

### Option 2: Command Line

```bash
source venv/bin/activate
python video_to_srt.py your_video.mp4
```

### Option 3: Custom Server Options

```bash
source venv/bin/activate
python web_server.py --device cuda --port 5001
```

**Device options:**
- `cuda`: Use GPU (NVIDIA) - fastest processing
- `cpu`: Use CPU - slower but works on any system

## Features

- ✅ Hindi-English mixed language transcription
- ✅ Converts to Roman English (Hinglish)
- ✅ Accurate timestamps for subtitles
- ✅ Web interface for easy use
- ✅ Supports multiple video formats
- ✅ GPU acceleration (if available) or CPU fallback

## Notes

- First run will download the model (~1GB)
- **GPU Mode**: Fast processing using NVIDIA GeForce RTX 2060 SUPER
- Processing time: ~10-20x faster than CPU
- Output SRT files can be used with any video player/editor

## Troubleshooting

**Server won't start?**
- Check that port 5001 is not in use
- Try a different port: `python web_server.py --port 5002`

**GPU not detected?**
- Check NVIDIA drivers: `nvidia-smi`
- Verify CUDA: `python -c "import torch; print(torch.cuda.is_available())"`
- Fallback to CPU: `python web_server.py --device cpu --port 5001`

**Slow processing?**
- Use Swift model instead of Prime
- Ensure GPU mode is active (configured by default)

**Poor transcription?**
- Ensure audio is clear
- Use Prime model for better accuracy
- Check that speech is Hindi-English mix

## Project Location

This project is located at:
`/home/ishanp/Documents/GitHub/Whisper-Hindi2Hinglish`

Virtual environment is in: `./venv`
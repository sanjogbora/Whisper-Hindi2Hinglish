# Setup Checklist ✓

Follow this checklist to get your Video to SRT converter up and running!

## Prerequisites

### 1. Python Installation
- [ ] Python 3.10 or higher installed
- [ ] Verify: `python --version`

### 2. FFmpeg Installation
- [ ] FFmpeg installed and in PATH
- [ ] Verify: `ffmpeg -version`

**Install FFmpeg**:
```bash
# Windows
winget install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

### 3. GPU Support (Optional but Recommended)
- [ ] NVIDIA GPU available
- [ ] CUDA installed (for GPU acceleration)
- [ ] Verify: `nvidia-smi`

**Note**: CPU works too, just slower!

## Installation Steps

### 4. Clone/Download Repository
- [ ] Repository downloaded
- [ ] Navigate to project folder: `cd Whisper-Hindi2Hinglish`

### 5. Install Python Dependencies
```bash
pip install -r requirements.txt
```

- [ ] All packages installed successfully
- [ ] No error messages

**Common packages installed**:
- [ ] torch
- [ ] transformers
- [ ] flask
- [ ] librosa
- [ ] numpy

### 6. Test Installation
```bash
python test_video_to_srt.py
```

- [ ] All checks passed
- [ ] FFmpeg detected
- [ ] Python packages detected

## First Run

### 7. Start the Server
```bash
python api_server.py
```

Or double-click: `start_server.bat`

- [ ] Server starts without errors
- [ ] See message: "Starting WebSocket server..."
- [ ] Model loads successfully

**Expected output**:
```
Loading model Oriserve/Whisper-Hindi2Hinglish-Swift
Starting WebSocket server on ws://0.0.0.0:5000
Server is ready to accept connections...
```

### 8. Access Web Interface
- [ ] Open browser
- [ ] Go to: http://localhost:5000
- [ ] See upload page

### 9. Test Conversion
- [ ] Upload a test video
- [ ] Select model (Swift recommended for first test)
- [ ] Click "Generate SRT File"
- [ ] SRT file downloads successfully

## Troubleshooting

### Issue: "FFmpeg not found"
**Solution**:
- [ ] Install FFmpeg (see step 2)
- [ ] Restart terminal/command prompt
- [ ] Verify: `ffmpeg -version`

### Issue: "CUDA out of memory"
**Solution**:
- [ ] Use CPU mode: `python api_server.py --device cpu`
- [ ] Or close other GPU applications

### Issue: "Module not found"
**Solution**:
- [ ] Reinstall dependencies: `pip install -r requirements.txt`
- [ ] Check Python version: `python --version` (need 3.10+)

### Issue: "Port already in use"
**Solution**:
- [ ] Use different port: `python api_server.py --port 5001`
- [ ] Or stop other application using port 5000

### Issue: Poor transcription quality
**Solution**:
- [ ] Use Prime model instead of Swift
- [ ] Ensure video has clear audio
- [ ] Check that speech is Hindi-English mix

## Verification

### Final Checks
- [ ] Server starts successfully
- [ ] Web interface loads
- [ ] Can upload video
- [ ] SRT file generates correctly
- [ ] SRT file has proper timestamps
- [ ] Transcription is in Roman English (Hinglish)

## Next Steps

### You're all set! Now you can:

1. **Use Web Interface**:
   - Drag and drop videos
   - Download SRT files
   - Share with team

2. **Use Command Line**:
   ```bash
   python video_to_srt.py video.mp4
   ```

3. **Use API Programmatically**:
   - See `example_api_usage.py`
   - Integrate with your workflow
   - Batch process videos

4. **Read Documentation**:
   - [ ] `QUICK_START.md` - Quick reference
   - [ ] `VIDEO_TO_SRT_GUIDE.md` - Complete guide
   - [ ] `README.md` - About the model

## Support

Need help?
- [ ] Check `VIDEO_TO_SRT_GUIDE.md` troubleshooting section
- [ ] Run: `python test_video_to_srt.py`
- [ ] Contact: ai-team@oriserve.com

---

**Congratulations! You're ready to convert videos to SRT files! 🎉**

# 🚀 Quick Start - Video to SRT Converter

Convert your Hindi-English mixed videos to Roman English subtitles!

## 🎯 For Non-Technical Users (Easiest Method)

**Just double-click the launcher!**

- **Windows:** Double-click `START HERE.bat`
- **Mac:** Double-click `START HERE.command`
- **Linux:** Run `./START HERE.sh`

The launcher will:
- ✅ Check Python and FFmpeg
- ✅ Install missing dependencies automatically
- ✅ Start the web server
- ✅ Open your browser

**See [QUICK_START_VISUAL.md](../QUICK_START_VISUAL.md) for detailed visual guide**

---

## 🛠️ For Developers (Manual Setup)

### Step 1: Install FFmpeg

FFmpeg is required to extract audio from videos.

**Windows (easiest)**:
```bash
winget install ffmpeg
```

**Or download manually**:
1. Go to https://ffmpeg.org/download.html
2. Download Windows build
3. Extract and add to PATH

**Verify installation**:
```bash
ffmpeg -version
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- PyTorch (AI model)
- Transformers (Whisper model)
- Flask (web server)
- Other utilities

### Step 3: Start Using!

#### 🌐 Option A: Web Interface (Recommended)

**1. Start the server**:
```bash
python web_server.py
```

**2. Open browser**:
```
http://localhost:5000
```

**3. Upload and convert**:
- Drag & drop your video
- Choose model (Swift = faster, Prime = better quality)
- Click "Generate SRT File"
- Download starts automatically!

### 💻 Option B: Command Line

**Basic usage**:
```bash
python video_to_srt.py my_video.mp4
```
Creates: `my_video.srt`

**With custom output**:
```bash
python video_to_srt.py my_video.mp4 --output subtitles.srt
```

**Better quality (slower)**:
```bash
python video_to_srt.py my_video.mp4 --model-id Oriserve/Whisper-Hindi2Hinglish-Prime
```

## 🎯 What You Get

Your video with Hindi-English speech becomes an SRT file like this:

```srt
1
00:00:00,000 --> 00:00:03,500
Namaste dosto, aaj hum discuss karenge AI ke baare mein.

2
00:00:03,500 --> 00:00:07,200
Machine learning bahut important technology hai.
```

**Key Features**:
- ✅ Hindi words written in Roman/English script (Hinglish)
- ✅ Properly timed and synced
- ✅ Ready to use in video editors
- ✅ Works with mixed Hindi-English speech

## 🔧 Troubleshooting

### "FFmpeg not found"
→ Install FFmpeg (see Step 1)

### "CUDA out of memory"
→ Use CPU mode:
```bash
python web_server.py --device cpu
```

### Poor quality transcription
→ Use Prime model:
```bash
python video_to_srt.py video.mp4 --model-id Oriserve/Whisper-Hindi2Hinglish-Prime
```

## 📊 Model Comparison

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| Swift (default) | ⚡ Fast | ⭐⭐⭐ Good | Quick drafts, testing |
| Prime | 🐢 Slower | ⭐⭐⭐⭐⭐ Excellent | Final production, accuracy |

## 💡 Pro Tips

1. **Clear audio = better results**
   - Minimize background noise
   - Use good microphone
   - Speak clearly

2. **GPU is much faster**
   - With CUDA: ~10-20% of video duration
   - With CPU: ~50-100% of video duration

3. **Batch processing**
   - Use the API endpoint
   - Process multiple videos automatically

## 📝 Supported Formats

**Video**: MP4, AVI, MOV, MKV, WEBM, FLV, WMV, M4V
**Max Size**: 500MB (configurable)

## 🆘 Need Help?

1. **For launcher issues:**
   - See `docs/LAUNCHER_GUIDE.md` - Comprehensive launcher troubleshooting
   - See `QUICK_START_VISUAL.md` - Visual step-by-step guide

2. **For video conversion:**
   - `VIDEO_TO_SRT_GUIDE.md` - Complete documentation
   - `README.md` - About the AI model

3. Contact: ai-team@oriserve.com

---

**That's it! You're ready to convert videos to SRT files! 🎉**

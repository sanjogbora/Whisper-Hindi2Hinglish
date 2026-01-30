# 🎬 Quick Start - Whisper Hindi2Hinglish

## For Video Editors & Content Creators

> **No coding knowledge needed!** Just follow these simple steps.

---

## 📥 Step 1: Download

1. Click the green **"Code"** button at the top of this page
2. Click **"Download ZIP"**
3. Save to your Desktop or Downloads folder
4. **Extract the ZIP file** (right-click → Extract All)

✅ You should now have a folder called `Whisper-Hindi2Hinglish`

---

## 🚀 Step 2: Launch the App

Open the `Whisper-Hindi2Hinglish` folder and find the launcher for your system:

### Windows Users 🪟
**Double-click:** `START HERE.bat`

### Mac Users 🍎
**Double-click:** `START HERE.command`

*First time: Right-click → Open → Click "Open" in the popup*

### Linux Users 🐧
**In terminal:** `./START HERE.sh`

*First time: Run `chmod +x "START HERE.sh"` then try again*

---

## ⏳ Step 3: Wait for Setup (First Time Only)

The launcher will check and install everything needed:

```
[1/5] ✓ Checking Python...
[2/5] ✓ Checking FFmpeg...
[3/5] ⏳ Installing dependencies... (2-3 minutes)
[4/5] ✓ Starting server...
[5/5] ✓ Opening browser...
```

**Keep the window open!** Your browser will open automatically.

⚠️ **If something fails:** See [Troubleshooting](#troubleshooting) below

---

## 🌐 Step 4: Use the Web Interface

Your browser opens automatically to the app:

### System Status (Top of Page)
```
✅ Python - Installed
✅ FFmpeg - Installed
✅ Dependencies - Installed
💻 Processing Device - CPU/GPU
```

All green? You're ready! 🎉

---

## 🎥 Step 5: Upload Your Video

### Method 1: Drag & Drop (Easiest)
1. Drag your video file from File Explorer
2. Drop it in the upload area
3. See file name and size appear

### Method 2: Click to Browse
1. Click "Click to upload"
2. Browse to your video
3. Select and click "Open"

**Supported formats:** MP4, AVI, MOV, MKV, WEBM

---

## ⚙️ Step 6: Choose Quality

Pick one:

### 🏆 Prime (Recommended)
- **Best accuracy** for Hindi-English speech
- Takes a bit longer
- Use for: Important videos, final cuts

### ⚡ Swift
- **Faster processing**
- Still very good quality
- Use for: Quick previews, rough cuts

---

## ▶️ Step 7: Generate Subtitles

1. Click **"Generate SRT File"** button
2. Watch the progress bar fill up
3. Keep the browser tab open!

**Processing time depends on:**
- Video length (1 min video ≈ 30 sec - 1 min processing)
- Your computer (GPU is faster than CPU)
- Quality chosen (Prime takes longer)

---

## 💾 Step 8: Download Your SRT File

When done:
- ✅ Progress bar turns green
- 📥 SRT file downloads automatically
- 📁 Check your Downloads folder

**File name:** `your_video_name.srt`

---

## 🎬 Step 9: Use in Your Video Editor

### Adobe Premiere Pro
1. Import your video
2. File → Import → Import your .srt file
3. Drag subtitle file to timeline

### Final Cut Pro
1. Import your video
2. File → Import → Captions → Select your .srt file

### DaVinci Resolve
1. Import your video
2. File → Import → Subtitle → Browse to .srt file

### CapCut / Any Editor
1. Most editors support .srt files
2. Look for "Import Subtitles" or "Captions"
3. Select your .srt file

---

## 🔁 Step 10: Process More Videos

Want to convert another video?

1. **Keep the launcher window open**
2. Go back to the browser
3. Drag your next video
4. Click "Generate SRT File"
5. Repeat!

**To stop:** Close the launcher window or press Ctrl+C

---

## ❓ Troubleshooting

### Problem: "Python not found"

**Solution:**
1. Download Python from [python.org/downloads](https://www.python.org/downloads/)
2. During install: **✅ CHECK "Add Python to PATH"**
3. Click "Install Now"
4. Restart the launcher

---

### Problem: "FFmpeg not found"

The launcher tries to install it. If it fails:

**Windows:**
```
winget install ffmpeg
```

**Mac:**
```
brew install ffmpeg
```
(Need Homebrew? Visit [brew.sh](https://brew.sh))

**Linux:**
```
sudo apt install ffmpeg
```

Then restart the launcher.

---

### Problem: "Port 5000 in use"

**Solution 1:** Close other apps that might use port 5000

**Solution 2:** Use a different port
1. Close the launcher
2. Open Command Prompt / Terminal
3. Type: `python web_server.py --port 5001`
4. Open browser to: `http://localhost:5001`

---

### Problem: Browser doesn't open

**Solution:**
1. Check the launcher window says "Server running"
2. Manually open your browser
3. Go to: `http://localhost:5000`

---

### Problem: Processing takes forever

**Normal times:**
- 5 min video on GPU: 2-3 minutes
- 5 min video on CPU: 5-10 minutes

**If it's stuck:**
1. Check the progress bar is moving
2. Wait at least 10 minutes for long videos
3. Don't close the browser tab!

**CPU vs GPU:**
- GPU is much faster
- CPU still works, just slower
- Status shows which you're using

---

### Problem: Download didn't start

**Solution:**
1. Check your Downloads folder
2. Check browser's download area
3. Try generating the SRT again
4. Check browser isn't blocking downloads

---

### Problem: Launcher won't start

**Windows:**
- Right-click `START HERE.bat` → "Run as administrator"

**Mac:**
- Right-click `START HERE.command` → "Open"
- Click "Open" in security popup

**Linux:**
- Run: `chmod +x "START HERE.sh"`
- Then: `./START HERE.sh`

---

## 💡 Pro Tips

### Tip 1: Keep Everything Running
- Don't close the launcher window
- Keep it running in the background
- Process multiple videos without restarting

### Tip 2: Use Prime for Final Cuts
- Use Swift for testing and previews
- Use Prime for your final version
- Prime is more accurate but slower

### Tip 3: Break Up Long Videos
- Videos over 500MB won't upload
- Split long videos into shorter parts
- Process each part separately
- Combine SRT files in your editor

### Tip 4: Edit SRT Files
- SRT files are plain text
- Open with Notepad/TextEdit
- Fix any mistakes manually
- Format:
  ```
  1
  00:00:00,000 --> 00:00:05,000
  Your subtitle text here
  ```

### Tip 5: Batch Process
- Keep the app running
- Process all your videos in one session
- More efficient than restarting each time

---

## 🎯 What You Get

### Input
- Video file (MP4, AVI, MOV, etc.)
- Hindi, English, or mixed speech

### Output
- .srt subtitle file
- Hindi words in Roman script (Hinglish)
- Properly timed to your video
- Ready to use in any video editor

### Example
**Audio:** "Aaj ka weather kaisa hai?"
**Subtitle:** "Aaj ka weather kaisa hai?"

**Audio:** "This is very important point"
**Subtitle:** "This is very important point"

---

## 📊 System Requirements

### Minimum
- **OS:** Windows 10/11, macOS 10.15+, or Linux
- **RAM:** 8 GB
- **Disk:** 5 GB free space
- **Internet:** For first-time setup

### Recommended
- **RAM:** 16 GB or more
- **GPU:** NVIDIA GPU with CUDA (much faster!)
- **Disk:** 10 GB free space

---

## 🆘 Still Need Help?

1. **Read the detailed guide:** `docs/LAUNCHER_GUIDE.md`
2. **Check the FAQ:** See [README.md](README.md)
3. **GitHub Issues:** Report problems on GitHub
4. **Include in your report:**
   - Your operating system
   - Python version (run `python --version`)
   - FFmpeg version (run `ffmpeg -version`)
   - Error message from launcher window

---

## ✅ Success Checklist

Before you start:
- [ ] Downloaded and extracted the ZIP file
- [ ] Found the launcher file for your OS
- [ ] Python 3.10+ installed (with PATH checked)
- [ ] Internet connection available
- [ ] At least 5 GB free disk space

After first launch:
- [ ] Launcher completed all 5 checks
- [ ] Browser opened automatically
- [ ] All status indicators are green ✅
- [ ] Upload area is visible

Ready to process:
- [ ] Video file is ready (< 500MB)
- [ ] Chose quality (Prime or Swift)
- [ ] Clicked "Generate SRT File"
- [ ] Progress bar is moving
- [ ] SRT file downloaded

---

## 🎉 You're All Set!

You're now ready to convert Hindi-English videos to subtitles with ease!

**Remember:**
- ✅ Keep the launcher window open
- ✅ Don't close the browser tab during processing
- ✅ Use Prime for final videos, Swift for previews
- ✅ Your videos never leave your computer (100% local)

---

**Happy subtitle generating!** 🎬✨

---

*Made with ❤️ for video editors who don't want to code*

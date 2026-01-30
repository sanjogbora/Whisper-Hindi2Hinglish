# Launcher Guide - Whisper Hindi2Hinglish

## Overview

The one-click launcher system is designed to make Whisper Hindi2Hinglish accessible to non-technical users. No terminal knowledge, no Python commands - just double-click and go!

## What the Launcher Does

The launcher automatically performs these checks and setups:

1. ✅ **Checks Python Installation**
   - Verifies Python 3.10+ is installed
   - Provides installation instructions if missing

2. ✅ **Checks FFmpeg Installation**
   - Verifies FFmpeg is available for video processing
   - Attempts automatic installation (Windows: winget, Mac: brew, Linux: apt)
   - Provides manual installation instructions if auto-install fails

3. ✅ **Checks Python Dependencies**
   - Verifies all required packages are installed
   - Automatically installs missing packages via pip
   - Shows progress during installation

4. ✅ **Starts Web Server**
   - Launches Flask server in the background
   - Runs on port 5000 by default
   - Keeps running while you use the app

5. ✅ **Opens Browser**
   - Automatically opens your default browser
   - Navigates to http://localhost:5000
   - Shows the enhanced web interface

---

## Platform-Specific Instructions

### Windows (START HERE.bat)

**How to Run:**
1. Navigate to the project folder
2. Double-click `START HERE.bat`
3. A command prompt window will open showing progress
4. Browser opens automatically when ready

**What You'll See:**
```
========================================================
  Whisper Hindi2Hinglish - Video to SRT Converter
  Starting up...
========================================================

[1/5] Checking Python installation...
+ Python found: Python 3.10.0

[2/5] Checking FFmpeg installation...
+ FFmpeg found

[3/5] Checking Python dependencies...
+ Dependencies already installed

[4/5] Starting web server...
+ Server started

[5/5] Opening web interface...
+ Browser opened

========================================================
  Server running at http://localhost:5000
  Browser should open automatically
  Keep this window open while using the app
========================================================
```

**First-Time Setup:**
- If Python is missing, follow the instructions to install from python.org
- If FFmpeg is missing, the launcher will try `winget install ffmpeg`
- If dependencies are missing, they'll be installed automatically (takes 2-3 minutes)

**Stopping the Server:**
- Press `Ctrl+C` in the command prompt window
- Or just close the window

---

### Mac (START HERE.command)

**How to Run:**
1. Navigate to the project folder
2. Double-click `START HERE.command`
3. A terminal window will open showing progress
4. Browser opens automatically when ready

**First-Time Permissions:**
If you see "cannot be opened because it is from an unidentified developer":
1. Right-click `START HERE.command`
2. Select "Open"
3. Click "Open" in the dialog
4. You only need to do this once

**What You'll See:**
```
========================================================
  Whisper Hindi2Hinglish - Video to SRT Converter
  Starting up...
========================================================

[1/5] Checking Python installation...
✓ Python found: Python 3.10.0

[2/5] Checking FFmpeg installation...
✓ FFmpeg found

[3/5] Checking Python dependencies...
✓ Dependencies already installed

[4/5] Starting web server...
✓ Server started (PID: 12345)

[5/5] Opening web interface...
✓ Browser opened

========================================================
  🎉 Server running at http://localhost:5000
  Browser should open automatically
  Keep this terminal open while using the app
========================================================
```

**First-Time Setup:**
- If Python is missing, download from python.org
- If FFmpeg is missing, the launcher will try `brew install ffmpeg`
  - If Homebrew is not installed, you'll be prompted to install it first
- If dependencies are missing, they'll be installed automatically

**Stopping the Server:**
- Press `Ctrl+C` in the terminal window
- Or close the terminal window

---

### Linux (START HERE.sh)

**How to Run:**
1. Open terminal in the project folder
2. Make executable (first time only): `chmod +x "START HERE.sh"`
3. Run: `./START HERE.sh`
4. Browser opens automatically when ready

**What You'll See:**
```
========================================================
  Whisper Hindi2Hinglish - Video to SRT Converter
  Starting up...
========================================================

[1/5] Checking Python installation...
✓ Python found: Python 3.10.0

[2/5] Checking FFmpeg installation...
✓ FFmpeg found

[3/5] Checking Python dependencies...
✓ Dependencies already installed

[4/5] Starting web server...
✓ Server started (PID: 12345)

[5/5] Opening web interface...
✓ Browser opened

========================================================
  🎉 Server running at http://localhost:5000
  Browser should open automatically
  Keep this terminal open while using the app
========================================================
```

**First-Time Setup:**
- If Python is missing, install via package manager:
  - Ubuntu/Debian: `sudo apt install python3 python3-pip`
  - Fedora/RHEL: `sudo dnf install python3 python3-pip`
  - Arch: `sudo pacman -S python python-pip`
- If FFmpeg is missing, the launcher will detect your package manager and install it
- If dependencies are missing, they'll be installed automatically

**Stopping the Server:**
- Press `Ctrl+C` in the terminal
- Or close the terminal window

---

## Using the Web Interface

Once the launcher starts the server and opens your browser, you'll see:

### System Status Dashboard

At the top of the page, you'll see the system status:

- **Python ✅** - Python is installed and working
- **FFmpeg ✅** - FFmpeg is installed for video processing
- **Dependencies ✅** - All required packages are installed
- **Processing Device** - Shows whether you're using GPU (fast) or CPU

All indicators should be green (✅). If any are red (❌), the launcher will guide you to fix them.

### Video Upload Section

1. **Drag and Drop:** Drag your video file onto the upload area
   - Or click to browse and select a file
   - Supported formats: MP4, AVI, MOV, MKV, WEBM

2. **Choose Quality:**
   - **Prime** - Best accuracy (recommended for important videos)
   - **Swift** - Faster processing, good quality

3. **Generate SRT:** Click the button and wait
   - Progress bar shows status
   - Processing time depends on video length
   - Keep the browser tab open

4. **Download:** SRT file downloads automatically when done

### Help Section

The interface includes a "First Time Here?" guide with step-by-step instructions.

---

## Troubleshooting

### Launcher Won't Start

**Windows:**
- Right-click `START HERE.bat` → "Run as administrator"
- Check Windows Defender isn't blocking it

**Mac:**
- Right-click `START HERE.command` → "Open"
- Check System Preferences → Security & Privacy

**Linux:**
- Make sure the script is executable: `chmod +x "START HERE.sh"`
- Run from terminal to see error messages

---

### Python Not Found

**Solution:**
1. Download Python 3.10+ from [python.org/downloads](https://www.python.org/downloads/)
2. During installation, **check "Add Python to PATH"**
3. Restart the launcher

**Verify Installation:**
```bash
python --version
# Should show: Python 3.10.x or higher
```

---

### FFmpeg Not Found

**Windows:**
```bash
winget install ffmpeg
```
Or download from [ffmpeg.org](https://ffmpeg.org/download.html)

**Mac:**
```bash
brew install ffmpeg
```
If Homebrew isn't installed: https://brew.sh

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Fedora/RHEL
sudo dnf install ffmpeg

# Arch
sudo pacman -S ffmpeg
```

**Verify Installation:**
```bash
ffmpeg -version
# Should show FFmpeg version info
```

---

### Dependencies Installation Failed

**Common causes:**
- No internet connection
- Firewall blocking pip
- Insufficient disk space
- Python pip not installed

**Solution:**
```bash
# Manually install dependencies
pip install -r requirements.txt

# If pip command not found
python -m pip install -r requirements.txt

# If permissions error (Linux/Mac)
pip install --user -r requirements.txt
```

---

### Port 5000 Already in Use

**Find what's using port 5000:**

**Windows:**
```bash
netstat -ano | findstr :5000
```

**Mac/Linux:**
```bash
lsof -i :5000
```

**Solutions:**
1. Close the application using port 5000
2. Or use a different port:
   ```bash
   python web_server.py --port 5001
   ```
   Then open: http://localhost:5001

---

### Browser Doesn't Open Automatically

**Manual Solution:**
1. Look for the message "Server running at http://localhost:5000"
2. Manually open your browser
3. Navigate to: http://localhost:5000

**Check if server is running:**
- The launcher window should still be open
- Should say "Server running"

---

### "Server stopped unexpectedly"

**Possible causes:**
- Python error during startup
- Missing dependencies
- Port already in use

**Solution:**
1. Look for error messages in the launcher window
2. Try running manually to see full error:
   ```bash
   python web_server.py
   ```
3. Fix the error shown, then restart the launcher

---

### GPU/CUDA Errors

**Don't worry!** The app automatically falls back to CPU if GPU isn't available.

**What you'll see:**
- "Processing Device: CPU" in the system status
- Processing will be slower but will work fine

**To use GPU (optional):**
1. Install CUDA Toolkit (NVIDIA GPUs only)
2. Install PyTorch with CUDA support
3. Restart the launcher

For most users, CPU processing is perfectly fine for occasional use.

---

## Advanced Usage

### Running on a Different Port

Edit the launcher script or run manually:

**Windows (START HERE.bat):**
Change line: `start /B python web_server.py`
To: `start /B python web_server.py --port 5001`

**Mac/Linux:**
Change line: `python3 web_server.py &`
To: `python3 web_server.py --port 5001 &`

### Using a Specific Python Version

If you have multiple Python versions:

**Windows:**
```bash
py -3.10 web_server.py
```

**Mac/Linux:**
```bash
python3.10 web_server.py
```

### Running in Developer Mode

For developers who want to see full output:

```bash
python web_server.py --host 0.0.0.0 --port 5000
```

This allows access from other devices on your network at `http://your-ip:5000`

---

## FAQ

### Q: Do I need to install anything manually?

**A:** Only Python. The launcher handles everything else automatically.

### Q: How long does first-time setup take?

**A:** 2-5 minutes for downloading and installing dependencies.

### Q: Can I use this offline after setup?

**A:** Yes! After first-time setup, you only need internet to download models (happens automatically when you process your first video).

### Q: Is my video uploaded to the cloud?

**A:** No! Everything runs locally on your computer. Your videos never leave your machine.

### Q: Can I process multiple videos at once?

**A:** One at a time. Wait for the first video to finish before uploading another.

### Q: What video formats are supported?

**A:** MP4, AVI, MOV, MKV, WEBM, FLV, WMV, M4V

### Q: What's the maximum video size?

**A:** 500MB. For larger videos, consider compressing them first or splitting them into smaller parts.

### Q: How accurate are the subtitles?

**A:** Very accurate for Hindi-English mixed speech. Prime model offers the best accuracy.

### Q: Can I edit the SRT file?

**A:** Yes! SRT files are plain text. Open with any text editor.

### Q: Does this work on Windows 11?

**A:** Yes! Works on Windows 10, 11, macOS, and Linux.

---

## Getting Help

Still having issues?

1. Check the [main README.md](../README.md) for general information
2. Look for error messages in the launcher window
3. Try running manually: `python web_server.py` to see detailed errors
4. Open an issue on GitHub with:
   - Your operating system
   - Python version (`python --version`)
   - FFmpeg version (`ffmpeg -version`)
   - Full error message from launcher

---

## Technical Details (For Developers)

### What the Launcher Does Behind the Scenes

1. **Environment Check:**
   - Verifies Python installation
   - Verifies FFmpeg availability
   - Checks for required Python packages

2. **Auto-Installation:**
   - Uses platform-specific package managers (winget, brew, apt)
   - Installs pip packages via requirements.txt
   - Shows progress and errors clearly

3. **Server Management:**
   - Starts Flask server as background process
   - Captures process ID for clean shutdown
   - Handles Ctrl+C gracefully

4. **User Experience:**
   - Visual progress indicators (1/5, 2/5, etc.)
   - Clear success/error messages
   - Auto-opens browser when ready
   - Keeps server running until user stops it

### Launcher Architecture

```
START HERE.bat/command/sh
│
├─ Check Python (required)
│  └─ Exit if not found with install instructions
│
├─ Check FFmpeg (required)
│  ├─ Auto-install via package manager
│  └─ Exit if auto-install fails with manual instructions
│
├─ Check Dependencies (required)
│  └─ Auto-install via pip install -r requirements.txt
│
├─ Start Server (background process)
│  └─ python web_server.py &
│
└─ Open Browser
   └─ open http://localhost:5000
```

### Files Created/Modified

The launcher system includes:

- `START HERE.bat` - Windows launcher
- `START HERE.command` - Mac launcher
- `START HERE.sh` - Linux launcher
- `templates/launcher.html` - Enhanced web interface
- `web_server.py` - Backend with `/api/status` endpoint

### API Endpoints

**`GET /`**
- Serves enhanced launcher.html interface

**`GET /api/status`**
- Returns system status JSON:
  ```json
  {
    "python": true,
    "python_version": "3.10.0",
    "ffmpeg": true,
    "dependencies": true,
    "device": "CUDA GPU (NVIDIA GeForce RTX 3080)",
    "server": true
  }
  ```

**`POST /upload`**
- Uploads video and returns SRT file
- Parameters: video (file), model (prime/swift)

---

Made with ❤️ for non-technical users

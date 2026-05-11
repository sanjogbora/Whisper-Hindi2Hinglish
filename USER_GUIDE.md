# Video Caption Editor - User Guide

Complete guide to using the Whisper-Hindi2Hinglish Video Caption Editor for creating professional captioned videos.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Starting the Editor](#starting-the-editor)
5. [Editor Interface Tour](#editor-interface-tour)
6. [Step-by-Step Tutorial](#step-by-step-tutorial)
7. [Style Customization](#style-customization)
8. [Advanced Features](#advanced-features)
9. [Tips and Best Practices](#tips-and-best-practices)
10. [FAQ](#faq)

---

## Getting Started

The Video Caption Editor is a web-based application that allows you to:
- Upload videos and automatically generate Hindi-English captions
- Edit captions visually with a timeline preview
- Apply professional style presets (Reels, Shorts, etc.)
- Preview captions frame-by-frame with 1fps playback
- Embed captions directly into videos for social media

**Quick Start:**
```bash
python web_server.py
# Then visit: http://localhost:5000/editor/new
```

---

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.10 or newer
- **RAM**: 8 GB minimum (16 GB recommended)
- **Disk Space**: 2 GB free space + space for your videos
- **Internet**: Required for first-time model download

### Recommended Requirements
- **GPU**: NVIDIA GPU with CUDA support (for faster processing)
- **RAM**: 16 GB or more
- **Processor**: Multi-core CPU (4+ cores)
- **Browser**: Chrome 90+, Firefox 88+, Safari 14+, or Edge 90+

### Software Dependencies
- **FFmpeg**: Required for video processing (installed automatically if possible)
- **Python Packages**: Listed in `requirements.txt`

---

## Installation

### Option 1: Automatic Installation (Recommended)

Use the launcher scripts for automatic setup:

**Windows:**
1. Download and extract the project
2. Double-click `START HERE.bat`
3. Wait for automatic installation
4. Browser opens automatically when ready

**Mac:**
1. Download and extract the project
2. Double-click `START HERE.command`
3. Wait for automatic installation
4. Browser opens automatically when ready

**Linux:**
1. Download and extract the project
2. Run `./START HERE.sh`
3. Wait for automatic installation
4. Open browser to http://localhost:5000

### Option 2: Manual Installation

1. **Install Python 3.10+**
   - Download from [python.org](https://www.python.org/downloads/)
   - **IMPORTANT:** Check "Add Python to PATH" during installation

2. **Install FFmpeg**
   - **Windows:** `winget install ffmpeg`
   - **Mac:** `brew install ffmpeg` (requires [Homebrew](https://brew.sh))
   - **Linux:** `sudo apt install ffmpeg` (Ubuntu/Debian)

3. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Installation**
   ```bash
   ffmpeg -version  # Should show FFmpeg version
   python -c "import torch; print('PyTorch:', torch.__version__)"
   ```

---

## Starting the Editor

### Start the Server

Run the web server:

```bash
python web_server.py
```

By default, the server starts on:
- **URL**: http://localhost:5000
- **Port**: 5000 (can be changed with `--port` flag)

**Options:**
```bash
python web_server.py --port 5001  # Use different port
python web_server.py --device cpu  # Force CPU processing
```

### Access the Editor

Open your web browser and navigate to:
- **Caption Editor**: http://localhost:5000/editor/new
- **Simple Upload**: http://localhost:5000/upload
- **Landing Page**: http://localhost:5000

---

## Editor Interface Tour

The caption editor is divided into several sections:

```
┌─────────────────────────────────────────────────────────────┐
│  HEADER                                                      │
│  🎬 Caption Editor          [Preview] [Embed & Download]    │
├──────────────────────────────┬──────────────────────────────┤
│  VIDEO PREVIEW PANEL         │  CONTROL PANEL                │
│                              │                               │
│  ┌──────────────────────┐   │  Style Presets:               │
│  │                      │   │  [Reels ▼]                    │
│  │   Video Player       │   │                               │
│  │                      │   │  Typography:                  │
│  └──────────────────────┘   │  Font: [Roboto Bold ▼]        │
│                              │  Size: [======●===] 36px      │
│  TIMELINE                    │  Color: [■]                   │
│  ┌──────────────────────┐   │                               │
│  │ Frame1 Frame2 Frame3 │   │  Position:                    │
│  │ ┌────┐ ┌────┐ ┌────┐ │   │  X: [===●=======] 50%         │
│  │ │[📝]│ │[📝]│ │    │ │   │  Y: [========●==] 80%         │
│  │ └────┘ └────┘ └────┘ │   │                               │
│  └──────────────────────┘   │  Effects:                     │
│                              │  ☑ Outline  ☑ Shadow          │
│                              │  ☐ Background                 │
│                              │                               │
│                              │  Captions:                    │
│                              │  ┌─────────────────────────┐  │
│                              │  │ 0:00 → Kal mainne kaha │  │
│                              │  │ 0:02 → wealth hustle se │  │
│                              │  └─────────────────────────┘  │
│                              │                               │
└──────────────────────────────┴──────────────────────────────┘
```

### Header
- **Title**: "🎬 Caption Editor"
- **Generate Preview**: Creates a preview image with caption overlays
- **Embed & Download**: Burns captions into video and starts download

### Video Preview Panel (Left)
- **Video Player**: HTML5 video player with custom controls
- **Timeline Strip**: 1fps thumbnail sequence for navigation
- **Caption Markers**: Visual indicators showing when captions appear

### Control Panel (Right)
- **Style Presets**: Quick-access dropdown for built-in styles
- **Typography**: Font family, size, and color controls
- **Position**: X/Y sliders for caption placement
- **Effects**: Toggle outline, shadow, and background
- **Caption List**: Editable list of all captions

---

## Step-by-Step Tutorial

### Step 1: Upload Media

1. **Navigate to the Editor**
   - Open http://localhost:5000/editor/new in your browser

2. **Drag and Drop Your Video**
   - Click the upload area or drag your video file onto it
   - Supported formats: MP4, MOV, MKV, WEBM, AVI, FLV, WMV

3. **Choose Transcription Quality**
   - **Prime**: Best accuracy, slower processing (recommended)
   - **Swift**: Faster processing, good accuracy

4. **Click "Generate Captions"**
   - The server will:
     - Extract audio from your video
     - Transcribe using Whisper-Hindi2Hinglish
     - Generate SRT file with timestamps
     - Create an editing session

5. **Wait for Processing**
   - Progress bar shows transcription status
   - Time depends on video length and your hardware
   - Approximate times:
     - 1-minute video: 30-60 seconds (CPU), 10-20 seconds (GPU)
     - 5-minute video: 2-5 minutes (CPU), 30-60 seconds (GPU)

### Step 2: Review Captions

Once transcription is complete, you'll see:

1. **Video Player**
   - Your video is loaded and ready to play
   - Captions are not yet visible (they're in the session data)

2. **Timeline Preview**
   - 1fps thumbnails show the video content
   - Caption markers indicate where captions appear
   - Click any frame to seek the video

3. **Caption List**
   - All generated captions listed in order
   - Each caption shows:
     - Start time
     - End time
     - Transcribed text (Hinglish)

### Step 3: Edit Captions

1. **Play the Video**
   - Click the play button in the video player
   - Watch the video to verify caption accuracy

2. **Edit Caption Text**
   - Find the caption you want to modify in the caption list
   - Click on the text field
   - Type your changes
   - Changes auto-save when you click away

3. **Adjust Timing**
   - Edit the start/end time fields
   - Format: `MM:SS` or `SS.sss` (seconds with milliseconds)
   - Example: `0:05` or `5.250`

4. **Add New Captions**
   - Click the "+ Add Caption" button
   - Enter the text and timing
   - The caption is added to the list

5. **Delete Captions**
   - Click the "×" button next to any caption
   - Confirm deletion if prompted

### Step 4: Apply Styles

1. **Choose a Preset**
   - Click the "Style Preset" dropdown
   - Select from:
     - **Reels Standard**: Best for Instagram Reels/TikTok
     - **YouTube Shorts Safe**: Optimized for YouTube Shorts
     - **Minimal Clean**: Clean, documentary-style
     - **Bold Impact**: High contrast, attention-grabbing
     - **Cinematic**: Elegant, professional

2. **Customize Typography**
   - **Font Family**: Choose from available fonts
     - Roboto Bold (default)
     - Arial Bold
     - Helvetica
     - Noto Sans Devanagari (for Hindi text)
   - **Font Size**: Use slider (20-72px)
   - **Font Color**: Click color picker to choose

3. **Adjust Position**
   - **Horizontal (X)**: 10-90% (left to right)
     - 50% = centered
     - Lower values = left aligned
     - Higher values = right aligned
   - **Vertical (Y)**: 10-90% (top to bottom)
     - 80-90% = bottom (standard)
     - Lower values = higher on screen

4. **Enable Effects**
   - **☑ Outline**: Black border around text for readability
   - **☑ Shadow**: Drop shadow for depth
   - **☐ Background**: Semi-transparent box behind text

### Step 5: Generate Preview

1. **Click "Generate Preview"**
   - The server creates an image with caption overlay
   - Shows the frame at current video timestamp

2. **Review the Preview**
   - Check caption placement
   - Verify text readability
   - Ensure no overlapping with video content

3. **Adjust if Needed**
   - Make changes to style or position
   - Generate another preview
   - Repeat until satisfied

4. **Use Timeline for Frame-by-Frame Review**
   - Click timeline frames to seek to specific times
   - Generate preview at multiple timestamps
   - Check caption placement throughout the video

### Step 6: Embed and Download

1. **Click "Embed & Download"**
   - The server starts the caption embedding process
   - Progress modal shows:
     - Progress bar (0-100%)
     - Current status message
     - Estimated time remaining

2. **Wait for Processing**
   - Time depends on:
     - Video length
     - Video resolution
     - Hardware performance
   - Approximate times:
     - 1-minute 1080p video: 1-2 minutes
     - 5-minute 1080p video: 5-10 minutes

3. **Download the Result**
   - When complete, download starts automatically
   - File name: `original_captioned.mp4`
   - Captions are "burned" into the video (permanent)

4. **Use Your Captioned Video**
   - Upload to social media (Instagram, TikTok, YouTube)
   - No need for separate caption files
   - Captions display consistently on all platforms

---

## Style Customization

### Understanding Style Components

A caption style consists of:

1. **Typography**
   - Font family
   - Font size
   - Font color
   - Font opacity

2. **Positioning**
   - Horizontal position (X)
   - Vertical position (Y)
   - Text alignment (left/center/right)

3. **Effects**
   - Text outline (stroke)
   - Text shadow
   - Background box

### Creating Custom Styles

**Example: High-Contrast for Noisy Backgrounds**

1. Start with **Bold Impact** preset
2. Adjust settings:
   - Font Size: 44px (increase for visibility)
   - Outline Width: 4px (thicker border)
   - Shadow Blur: 6px (deeper shadow)
   - Background: Enabled (semi-transparent black)

**Example: Minimalist for Clean Video**

1. Start with **Minimal Clean** preset
2. Adjust settings:
   - Font Size: 28px (smaller, elegant)
   - Background Opacity: 0.4 (more transparent)
   - Outline: Disabled
   - Shadow: Disabled

### Saving Custom Presets

Currently, custom presets can be created by editing the preset configuration files. To create a custom preset:

1. Locate the `presets/` directory
2. Create a new JSON file: `my_custom_preset.json`
3. Add your configuration:
   ```json
   {
     "name": "My Custom Preset",
     "description": "Description of my style",
     "font_family": "Roboto Bold",
     "font_size": 36,
     "font_color": "#FFFFFF",
     "position_x": 50,
     "position_y": 80,
     "outline_enabled": true,
     "outline_color": "#000000",
     "outline_width": 2
   }
   ```

4. Restart the server to load the new preset

---

## Advanced Features

### Caption Editing Techniques

**Split Long Captions**
- Long captions can be hard to read quickly
- Split into two shorter captions:
  1. Click "+ Add Caption"
  2. Copy half the text to new caption
  3. Adjust timing for both

**Merge Short Captions**
- Very short captions can be distracting
- Merge into one longer caption:
  1. Copy text from first caption
  2. Paste into second caption
  3. Delete first caption
  4. Adjust timing

**Adjust for Speaker Changes**
- When speakers change, use timing to separate:
  1. Note when speaker changes
  2. Split caption at that timestamp
  3. Adjust end time of first caption
  4. Adjust start time of second caption

### Timeline Navigation

**Quick Navigation:**
- Click any timeline frame to seek
- Use keyboard arrows for fine-tuning

**Frame-by-Frame Review:**
1. Click timeline frame at 0:00
2. Generate preview
3. Click next frame (0:01)
4. Generate preview
5. Repeat to check caption placement throughout

**Caption Markers:**
- Dark markers indicate caption presence
- Light markers indicate no caption
- Use to identify gaps in captioning

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Space` | Play/pause video |
| `←` | Seek -5 seconds |
| `→` | Seek +5 seconds |
| `↑` | Seek -1 second |
| `↓` | Seek +1 second |
| `F` | Toggle fullscreen |
| `Ctrl+S` / `Cmd+S` | Save current style |
| `Esc` | Close modal |

### Batch Operations

**Apply Style to Multiple Videos:**
Currently, the editor processes one video at a time. For batch processing, use the command-line tools:

```bash
# Process multiple videos
for video in videos/*.mp4; do
    python video_to_srt.py "$video"
done
```

**Export SRT Only:**
If you only need the SRT file (not captioned video):

1. Upload video to editor
2. Generate captions
3. Use the "Download SRT" button (if available)
4. Or find the SRT file in your Downloads folder

---

## Tips and Best Practices

### For Reels and Short-Form Content

**Optimal Settings:**
- Use **Reels Standard** or **Shorts Safe** preset
- Font size: 32-40px (larger for mobile viewing)
- Position: 75-85% vertical (avoid UI elements)
- Outline: Always enabled for readability

**Caption Length:**
- Keep captions short (2-3 lines max)
- Use conversational language
- Match the pacing of the video

**Timing:**
- Sync captions with speech
- Leave captions on screen 0.5-1 second after speech ends
- Avoid rapid-fire captions (allow reading time)

### For Long-Form Content

**Optimal Settings:**
- Use **Minimal Clean** or **Cinematic** preset
- Font size: 28-32px (smaller, elegant)
- Position: 80-90% vertical
- Outline: Optional (depends on background)

**Caption Length:**
- Can use longer captions (up to 4 lines)
- Include full sentences
- Match the narrative flow

**Timing:**
- Allow more reading time (1-2 seconds per line)
- Sync with visual cues
- Consider breaking at natural pauses

### For Noisy/Complex Backgrounds

**Optimal Settings:**
- Use **Bold Impact** preset
- Font size: 40-48px (very large)
- Outline: Thick (3-4px)
- Shadow: Strong (blur 4-6px)
- Background: Semi-transparent (opacity 0.5-0.7)

**Tips:**
- Test preview at multiple timestamps
- Adjust position to avoid visual clutter
- Consider repositioning captions for different scenes

### Performance Optimization

**Faster Processing:**
- Use **Swift** model for testing (lower accuracy but faster)
- Process shorter videos first
- Use GPU if available
- Close other applications

**Reduce Preview Time:**
- Generate preview at key timestamps only
- Use timeline to identify critical frames
- Avoid generating preview for every change

**Reduce Embedding Time:**
- Test with lower resolution first
- Use smaller video for initial testing
- Consider embedding overnight for long videos

### Common Pitfalls

**Avoid These Mistakes:**
1. **Captions too small**: Increase font size for mobile viewers
2. **Captions too low**: Avoid 90%+ vertical (may be cut off)
3. **Poor contrast**: Always use outline or background
4. **Rapid captions**: Allow sufficient reading time
5. **Inaccurate transcription**: Always review and edit generated captions

**Quality Checklist:**
- [ ] All captions are readable
- [ ] Timing matches speech
- [ ] No spelling/grammar errors
- [ ] Captions don't overlap video content
- [ ] Style is consistent throughout
- [ ] Tested on mobile device

---

## FAQ

### General Questions

**Q: What video formats are supported?**
A: MP4, MOV, MKV, WEBM, AVI, FLV, WMV, M4V

**Q: What's the maximum file size?**
A: 500 MB (can be changed in web_server.py)

**Q: How long does processing take?**
A: Depends on video length and hardware:
- 1-minute video: 30-60 seconds (CPU), 10-20 seconds (GPU)
- 5-minute video: 2-5 minutes (CPU), 30-60 seconds (GPU)

**Q: Can I use this for free?**
A: Yes! The project is open-source under Apache-2.0 license.

**Q: Do I need an internet connection?**
A: Only for first-time model download. After that, it works offline.

### Technical Questions

**Q: Why does FFmpeg installation fail?**
A: Try manual installation:
- Windows: Download from ffmpeg.org
- Mac: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

**Q: Can I use my own fonts?**
A: Yes! Place TTF font files in the `fonts/` directory and restart the server.

**Q: How do I enable GPU acceleration?**
A: Install CUDA and PyTorch with CUDA support. The app will automatically use GPU if available.

**Q: Can I process multiple videos at once?**
A: Currently, the editor processes one video at a time. Use command-line tools for batch processing.

**Q: What's the difference between Prime and Swift models?**
A:
- **Prime**: Best accuracy, slower (recommended for final output)
- **Swift**: Faster processing, good accuracy (good for testing)

### Editing Questions

**Q: Can I undo changes?**
A: Currently, there's no undo. Save your work frequently and keep backups.

**Q: Can I add animations to captions?**
A: Not yet. This feature is planned for future updates.

**Q: Can I export captions as SRT only?**
A: Yes. After transcription, the SRT file is saved in your Downloads folder.

**Q: How do I fix Hindi text rendering issues?**
A: Ensure Noto Sans Devanagari font is in the `fonts/` directory.

**Q: Can I change the video format during export?**
A: Currently, output is always MP4. Use FFmpeg to convert if needed.

### Social Media Questions

**Q: Which preset is best for Instagram Reels?**
A: Use **Reels Standard** preset. It's optimized for 9:16 vertical format.

**Q: Which preset is best for YouTube Shorts?**
A: Use **Shorts Safe** preset. It accounts for YouTube's UI elements.

**Q: Will captions display on all platforms?**
A: Yes! Because captions are "burned in", they display consistently everywhere.

**Q: What's the ideal video length for Reels?**
A: 15-60 seconds. Keep captions short and punchy.

**Q: Can I add custom branding?**
A: Currently, no. This feature is planned for future updates.

### Troubleshooting

**Q: The server won't start. What do I do?**
A:
1. Check Python is installed: `python --version`
2. Check port 5000 is not in use
3. Try a different port: `python web_server.py --port 5001`
4. Check error messages in terminal

**Q: Preview generation is very slow. What can I do?**
A:
1. Use a smaller video for testing
2. Generate preview at fewer timestamps
3. Close other applications
4. Use GPU if available

**Q: Caption embedding fails. What's wrong?**
A:
1. Check FFmpeg is installed: `ffmpeg -version`
2. Ensure sufficient disk space
3. Try with a smaller video
4. Check server logs for error details

**Q: My captions are inaccurate. How can I improve?**
A:
1. Use the **Prime** model for better accuracy
2. Edit captions manually in the editor
3. Ensure clear audio (reduce background noise)
4. Speak clearly and at moderate pace

**Q: The editor is slow/laggy. What can I do?**
A:
1. Close other browser tabs
2. Use a modern browser (Chrome/Firefox)
3. Increase system RAM if possible
4. Use a shorter video for testing

---

## Getting Help

If you need further assistance:

1. **Documentation**
   - [README.md](README.md) - Project overview
   - [docs/API_REFERENCE.md](docs/API_REFERENCE.md) - API documentation
   - [docs/QUICK_START.md](docs/QUICK_START.md) - Quick start guide

2. **Community**
   - Report issues on GitHub
   - Check existing discussions
   - Contribute to the project

3. **Contact**
   - Email: ai-team@oriserve.com
   - For business inquiries and support

---

**Happy Captioning! 🎬✨**
# Whisper-Hindi2Hinglish Auto-Captioning Infrastructure

> **🚀 CRITICAL FOR AI AGENTS**: 
> - **ALWAYS** activate conda environment first: `conda activate whisper-hindi` or `source ~/miniconda3/bin/activate whisper-hindi`
> - **NEVER** use venv - it has been removed from this project
> - **GPU Memory**: Process files one at a time, clear memory between runs, use CPU fallback when GPU is full
> - **Audio Format**: Whisper requires 16kHz mono WAV - use `ffmpeg -i input -ar 16000 -ac 1 output.wav`
> - See [Section 11](#11-ai-agent-quick-reference) for quick reference commands
>
> **Comprehensive guide for understanding and utilizing the auto-captioning infrastructure**

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Quick Start](#quick-start)
5. [API Documentation](#api-documentation)
6. [Usage Examples](#usage-examples)
7. [Configuration](#configuration)
8. [Caption Styling](#caption-styling)
9. [Model Information](#model-information)
10. [Output Structure](#output-structure)
11. [AI Agent Quick Reference](#11-ai-agent-quick-reference)
12. [Troubleshooting](#12-troubleshooting)
13. [Development Guidelines](#development-guidelines)
14. [Technical Details](#technical-details)
15. [Examples & Workflows](#examples--workflows)

---

## 1. Project Overview

### Purpose and Goal

The Whisper-Hindi2Hinglish Auto-Captioning Infrastructure is a comprehensive system designed to automatically generate high-quality captions for Hindi-English (Hinglish) mixed content. It leverages the fine-tuned Whisper model optimized for Indian accents and noisy environments to produce accurate transcriptions in Roman script.

### What This Infrastructure Does

- **Transcription**: Converts Hindi-English mixed audio/video content to Roman English (Hinglish) subtitles
- **Video Processing**: Extracts audio from videos and generates time-synchronized captions
- **Caption Styling**: Applies professional caption styling optimized for social media platforms
- **Video Embedding**: Burns captions directly into videos with customizable fonts, colors, and positioning
- **Web Interface**: Provides a user-friendly web UI for caption editing and preview
- **REST API**: Offers programmatic access for automation and integration
- **Batch Processing**: Supports processing multiple videos efficiently

### Target Platforms

The infrastructure is optimized for short-form video content on:

- **Instagram Reels** (9:16 vertical format)
- **YouTube Shorts** (9:16 vertical format)
- **TikTok** (9:16 vertical format)
- **Facebook Reels** (9:16 vertical format)

Also supports:
- YouTube videos (16:9 horizontal)
- TikTok videos (9:16 vertical)
- Any custom aspect ratio videos

---

## 2. Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Web UI     │  │  REST API    │  │    CLI       │          │
│  │ (Browser)    │  │  (External)  │  │ (Terminal)   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼─────────────────┼─────────────────┼──────────────────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────┐
│                   WEB SERVER LAYER (Flask)                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Video Caption Editor | Session Manager | Media Handler  │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────┼─────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────┐
│                    PIPELINE LAYER                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  VideoCaptionPipeline | CaptionStyling | FrameExtractor   │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────┼─────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────┐
│                    PROCESSING LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Whisper AI  │  │   FFmpeg     │  │  Font Mgr    │          │
│  │  Transcribe  │  │  Process     │  │  Rendering   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. **Web Server** (`web_server.py`)
- Flask-based REST API server
- Handles file uploads and downloads
- Manages session creation and lifecycle
- Serves web UI for caption editing
- Exposes endpoints for programmatic access

#### 2. **Session Manager** (`session_manager.py`)
- Manages caption editing sessions
- Persists session state to JSON files
- Auto-cleanup expired sessions (24 hours)
- Tracks session status (transcribed, edited, complete, error)

#### 3. **Video Caption Pipeline** (`video_caption_pipeline.py`)
- Main orchestration module
- Coordinates caption generation, styling, and embedding
- Handles frame extraction for timeline preview
- Converts SRT to ASS format for FFmpeg
- Manages video rendering with caption overlays

#### 4. **Caption Generator** (`caption_generator.py`)
- Wraps Whisper model for transcription
- Generates word-level timestamps
- Groups words into subtitle-friendly chunks
- Produces SRT format output

#### 5. **Caption Styling** (`caption_styling.py`)
- Manages style presets (Reels, Shorts, Minimal, etc.)
- Handles font management
- Converts styles to ASS format
- Provides custom styling options

#### 6. **Media Handler** (`media_handler.py`)
- Validates media files
- Detects media type (video/audio)
- Extracts audio for processing
- Gets media metadata (duration, resolution)

#### 7. **WebSocket Server** (`websocket_server.py`)
- Real-time streaming transcription
- Supports microphone input
- Low-latency processing

### Data Flow

```
1. Upload/Select Media File
   ↓
2. Create Session (Session Manager)
   ↓
3. Extract Audio (Media Handler)
   ↓
4. Transcribe with Whisper (Caption Generator)
   ↓
5. Generate SRT File
   ↓
6. Parse Captions & Extract Frames (Video Caption Pipeline)
   ↓
7. Apply Caption Style (Caption Styling)
   ↓
8. Generate Preview (Timeline + Caption Overlays)
   ↓
9. Convert SRT to ASS
   ↓
10. Embed Captions with FFmpeg (Burn-in)
   ↓
11. Output: Captioned Video + SRT + WAV
```

### Integration Points

- **Hugging Face**: Model downloads (`Oriserve/Whisper-Hindi2Hinglish-Prime`)
- **FFmpeg/libass**: Video processing and caption rendering
- **PyTorch**: Model inference (CPU/GPU)
- **Flask**: Web server and REST API
- **WebSocket**: Real-time streaming

---

## 3. Installation & Setup

### Prerequisites

#### System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.10 or newer
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 10GB free space (for models and temporary files)
- **GPU** (optional): NVIDIA GPU with CUDA support for faster processing

#### Required Software

1. **Python 3.10+**
   ```bash
   # Check version
   python --version

   # Download from: https://www.python.org/downloads/
   # IMPORTANT: Check "Add Python to PATH" during installation
   ```

2. **FFmpeg** (video processing)
   ```bash
   # Linux (Ubuntu/Debian)
   sudo apt update && sudo apt install ffmpeg

   # macOS
   brew install ffmpeg

   # Windows (winget)
   winget install ffmpeg

   # Verify installation
   ffmpeg -version
   ```

3. **CUDA Toolkit** (optional, for GPU acceleration)
   ```bash
   # Install from: https://developer.nvidia.com/cuda-downloads
   # Ensure version matches your PyTorch CUDA version
   ```

### Installation Steps

#### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/OriserveAI/Whisper-Hindi2Hinglish.git
cd Whisper-Hindi2Hinglish
```

#### Step 2: Use Conda Environment

```bash
# Create conda environment (if not already created)
conda create -n whisper-hindi python=3.10

# Activate conda environment
conda activate whisper-hindi
```

#### Step 3: Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# For CUDA support (GPU)
pip install -r requirements-cuda.txt

# For development
pip install -r requirements-dev.txt
```

### Environment Configuration

Create a `.env` file (optional) in the project root:

```bash
# Server Configuration
FLASK_PORT=5000
FLASK_HOST=0.0.0.0

# Model Configuration
MODEL_ID=Oriserve/Whisper-Hindi2Hinglish-Prime
DEVICE=cuda  # or 'cpu'
DTYPE=float16  # or 'float32'

# Storage Configuration
SESSIONS_DIR=sessions
FONTS_DIR=fonts
UPLOAD_FOLDER=/home/user/Downloads

# Processing Configuration
MAX_FILE_SIZE=524288000  # 500MB in bytes
MAX_VIDEO_DURATION=300  # 5 minutes in seconds

# Logging
LOG_LEVEL=INFO
```

### Font Setup

The infrastructure uses custom fonts for caption rendering. Fonts should be placed in the `fonts/` directory:

```bash
# Create fonts directory
mkdir -p fonts

# Add your fonts (supported formats: .ttf, .otf, .woff, .woff2)
# Example fonts included:
# - Fira Sans Compressed Medium
# - Roboto Bold
# - Noto Sans Devanagari
```

### Model Downloading

Models are automatically downloaded from Hugging Face on first use. To download manually:

```python
from transformers import WhisperForConditionalGeneration, WhisperProcessor

# Download Prime model (best quality)
model = WhisperForConditionalGeneration.from_pretrained(
    "Oriserve/Whisper-Hindi2Hinglish-Prime"
)
processor = WhisperProcessor.from_pretrained(
    "Oriserve/Whisper-Hindi2Hinglish-Prime"
)

# Or download Swift model (faster)
model = WhisperForConditionalGeneration.from_pretrained(
    "Oriserve/Whisper-Hindi2Hinglish-Swift"
)
processor = WhisperProcessor.from_pretrained(
    "Oriserve/Whisper-Hindi2Hinglish-Swift"
)
```

---

## 4. Quick Start

### Getting Started Quickly

#### Option 1: Web UI (Easiest)

```bash
# Start the web server
python web_server.py

# Open your browser to:
# http://localhost:5000
```

#### Option 2: Command Line (SRT Generation)

```bash
# Process a video file
python video_to_srt.py your_video.mp4

# Process an audio file
python audio_to_srt.py your_audio.mp3

# Process any media (auto-detects type)
python caption_generator.py your_media.mp4
```

#### Option 3: Python API (Programmatic)

```python
from video_caption_pipeline import VideoCaptionPipeline

# Initialize pipeline
pipeline = VideoCaptionPipeline()

# Create caption session
session_id = pipeline.create_caption_session("video.mp4")

# Apply style preset
pipeline.apply_caption_style(session_id, "reels_standard")

# Generate preview
preview_data = pipeline.generate_caption_preview(session_id)

# Embed captions and download
output_path = pipeline.embed_captions_to_video(session_id)
print(f"Captioned video saved to: {output_path}")
```

### Basic Usage Example

```bash
# 1. Start the server
python web_server.py

# 2. Open browser to http://localhost:5000

# 3. Upload a video file
#    - Drag and drop or click to select
#    - Supported formats: MP4, MOV, MKV, WEBM, AVI, FLV, WMV, M4V

# 4. Choose model quality
#    - Prime: Best accuracy (slower)
#    - Swift: Faster processing (good for quick results)

# 5. Click "Generate Captions"
#    - Wait for transcription to complete

# 6. Edit captions (optional)
#    - Click on caption text to edit
#    - Adjust timing if needed

# 7. Choose style preset
#    - Reels Standard (Instagram/TikTok)
#    - YouTube Shorts Safe
#    - Minimal Clean
#    - Bold Impact
#    - Cinematic

# 8. Preview captions
#    - Click "Generate Preview"
#    - Use timeline to scrub through video
#    - Verify caption placement

# 9. Embed and download
#    - Click "Embed & Download"
#    - Wait for rendering to complete
#    - Download the captioned video

# 10. Find output files
#     Output directory: ~/Videos/Video-Name/
#     Files:
#       - Video-Name_captioned.mp4 (captioned video)
#       - Video-Name.srt (subtitle file)
#       - Video-Name.wav (extracted audio)
```

### Expected Output

After successful processing, you will find:

```
~/Videos/Video-Name/
├── Video-Name_captioned.mp4  # Captioned video (final output)
├── Video-Name.srt            # SRT subtitle file
└── Video-Name.wav            # Extracted audio (16kHz, mono)
```

---

## 5. API Documentation

### Base URL

```
http://localhost:5000
```

### Authentication

Currently, no authentication is required. Rate limiting is implemented at the server level.

### Rate Limiting

- Maximum file size: 500MB
- Maximum concurrent sessions: No hard limit
- Session lifetime: 24 hours (auto-cleanup)

### Endpoints

#### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "device": "cuda"
}
```

---

#### Session Management

##### Create Session

```http
POST /api/sessions
Content-Type: application/json

{
  "media_path": "/path/to/video.mp4",
  "model_name": "prime"
}
```

**Response:**
```json
{
  "session_id": "52c5d036-94cc-4822-97ca-4700d28644df",
  "status": "transcribed",
  "video_path": "/path/to/video.mp4",
  "captions_path": "/path/to/captions.srt",
  "created_at": "2024-01-15T10:30:00Z"
}
```

##### List Sessions

```http
GET /api/sessions
```

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "52c5d036-94cc-4822-97ca-4700d28644df",
      "status": "complete",
      "video_path": "/path/to/video.mp4",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

##### Get Session

```http
GET /api/sessions/{session_id}
```

**Response:**
```json
{
  "session_id": "52c5d036-94cc-4822-97ca-4700d28644df",
  "status": "complete",
  "video_path": "/path/to/video.mp4",
  "captions_path": "/path/to/captions.srt",
  "caption_style": "reels_standard",
  "created_at": "2024-01-15T10:30:00Z",
  "metadata": {
    "media_type": "video",
    "duration": 45.5,
    "resolution": "1080x1920"
  }
}
```

##### Delete Session

```http
DELETE /api/sessions/{session_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Session deleted successfully"
}
```

---

#### Caption Operations

##### Get Captions

```http
GET /api/sessions/{session_id}/captions
```

**Response:**
```json
{
  "captions": [
    {
      "index": 1,
      "start": 0.0,
      "end": 2.5,
      "text": "Hello, welcome to this video"
    },
    {
      "index": 2,
      "start": 2.5,
      "end": 5.0,
      "text": "Today we will learn about captioning"
    }
  ]
}
```

##### Update Captions

```http
PUT /api/sessions/{session_id}/captions
Content-Type: application/json

{
  "captions": [
    {
      "index": 1,
      "start": 0.0,
      "end": 2.5,
      "text": "Hello, welcome to this video"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Captions updated successfully"
}
```

##### Apply Style

```http
PUT /api/sessions/{session_id}/style
Content-Type: application/json

{
  "preset_name": "reels_standard",
  "style_overrides": {
    "font_size": 40,
    "color": "#FF0000"
  }
}
```

**Response:**
```json
{
  "success": true,
  "style": {
    "font_family": "Fira Sans Compressed Medium",
    "font_size": 40,
    "color": "#FF0000",
    "bold": true,
    "outline_color": "#000000",
    "outline_width": 15
  }
}
```

##### Generate Preview

```http
GET /api/sessions/{session_id}/preview?fps=1&max_frames=60
```

**Response:**
```json
{
  "preview_frames": [
    {
      "timestamp": 0.0,
      "frame_path": "/sessions/{id}/preview_frames/frame_00000.jpg",
      "caption": "Hello, welcome to this video"
    },
    {
      "timestamp": 1.0,
      "frame_path": "/sessions/{id}/preview_frames/frame_00001.jpg",
      "caption": "Hello, welcome to this video"
    }
  ]
}
```

---

#### Video Operations

##### Upload Video & Create Session

```http
POST /api/editor/upload
Content-Type: multipart/form-data

video: (binary file)
model_name: prime
```

**Response:**
```json
{
  "session_id": "52c5d036-94cc-4822-97ca-4700d28644df",
  "status": "transcribed",
  "redirect_url": "/editor/52c5d036-94cc-4822-97ca-4700d28644df"
}
```

##### Stream Original Video

```http
GET /api/sessions/{session_id}/video
```

**Response:** Video stream (video/mp4)

##### Embed Captions

```http
POST /api/sessions/{session_id}/embed
Content-Type: application/json

{
  "burn": true,
  "output_path": "/custom/output/path.mp4"
}
```

**Response:**
```json
{
  "success": true,
  "output_path": "/home/user/Videos/Video-Name/Video-Name_captioned.mp4",
  "duration": 15.2
}
```

##### Download Captioned Video

```http
GET /api/sessions/{session_id}/download
```

**Response:** File download (video/mp4)

---

#### Resources

##### List Presets

```http
GET /api/presets
```

**Response:**
```json
{
  "presets": [
    {
      "id": "reels_standard",
      "name": "Reels Standard",
      "description": "Optimized for Instagram Reels and TikTok",
      "category": "social",
      "target_aspect_ratio": "9:16"
    },
    {
      "id": "shorts_safe",
      "name": "YouTube Shorts Safe",
      "description": "Safe area for YouTube interface elements",
      "category": "social",
      "target_aspect_ratio": "9:16"
    }
  ]
}
```

##### Get Preset

```http
GET /api/presets/{preset_name}
```

**Response:**
```json
{
  "id": "reels_standard",
  "name": "Reels Standard",
  "description": "Optimized for Instagram Reels and TikTok",
  "text_style": {
    "font_family": "Fira Sans Compressed Medium",
    "font_size": 36,
    "color": "#FFFFFF",
    "bold": true,
    "italic": false,
    "outline_color": "#000000",
    "outline_width": 15,
    "shadow": true,
    "position_x": 50,
    "position_y": 50,
    "alignment": "center"
  },
  "target_aspect_ratio": "9:16",
  "category": "social"
}
```

##### List Fonts

```http
GET /api/fonts
```

**Response:**
```json
{
  "fonts": [
    {
      "id": "fira_sans_compressed_medium",
      "name": "Fira Sans Compressed Medium",
      "file": "FiraSansCompressed-Medium.ttf",
      "path": "/fonts/FiraSansCompressed-Medium.ttf"
    }
  ]
}
```

---

## 6. Usage Examples

### Programmatic Usage (Python API)

#### Basic Workflow

```python
from video_caption_pipeline import VideoCaptionPipeline

# Initialize pipeline
pipeline = VideoCaptionPipeline(
    sessions_dir="sessions",
    font_dir="fonts"
)

# Step 1: Create caption session
session_id = pipeline.create_caption_session(
    media_path="my_video.mp4",
    model_name="prime"  # or "swift"
)
print(f"Session created: {session_id}")

# Step 2: Apply style preset
pipeline.apply_caption_style(
    session_id,
    preset_name="reels_standard"
)

# Step 3: Generate preview frames
preview_data = pipeline.generate_caption_preview(
    session_id,
    fps=1,
    max_frames=60
)
print(f"Generated {len(preview_data)} preview frames")

# Step 4: Embed captions
output_path = pipeline.embed_captions_to_video(
    session_id,
    burn=True
)
print(f"Captioned video saved to: {output_path}")

# Step 5: Get session info
session_info = pipeline.get_session_info(session_id)
print(f"Session status: {session_info['status']}")
```

#### Custom Styling

```python
from video_caption_pipeline import VideoCaptionPipeline
from caption_styling import TextStyle

pipeline = VideoCaptionPipeline()

# Create custom style
custom_style = TextStyle(
    font_family="Roboto Bold",
    font_size=40,
    color="#FF5733",
    bold=True,
    italic=False,
    outline_color="#000000",
    outline_width=20,
    shadow=True,
    position_x=50,
    position_y=75,
    alignment="center"
)

# Apply custom style with overrides
pipeline.apply_caption_style(
    session_id,
    preset_name="reels_standard",
    style_overrides={
        "font_size": 40,
        "color": "#FF5733",
        "position_y": 75
    }
)
```

#### Batch Processing

```python
from pathlib import Path
from video_caption_pipeline import VideoCaptionPipeline

pipeline = VideoCaptionPipeline()

# Process all videos in a directory
video_dir = Path("~/Videos/raw").expanduser()
output_dir = Path("~/Videos/processed").expanduser()

for video_file in video_dir.glob("*.mp4"):
    try:
        print(f"Processing: {video_file.name}")

        # Create session
        session_id = pipeline.create_caption_session(str(video_file))

        # Apply style
        pipeline.apply_caption_style(session_id, "reels_standard")

        # Embed captions
        output_path = pipeline.embed_captions_to_video(
            session_id,
            burn=True
        )

        # Move to output directory
        output_file = Path(output_path)
        output_file.rename(output_dir / output_file.name)

        print(f"✓ Completed: {video_file.name}")

        # Cleanup session
        pipeline.delete_session(session_id)

    except Exception as e:
        print(f"✗ Failed: {video_file.name} - {e}")
```

### Web Interface Usage

#### Uploading and Processing

1. **Navigate to Editor**
   ```
   http://localhost:5000/editor/new
   ```

2. **Upload Video**
   - Click "Choose File" or drag and drop
   - Select video file (MP4, MOV, MKV, etc.)
   - Click "Upload & Generate Captions"

3. **Wait for Processing**
   - Status updates in real-time
   - Progress bar shows transcription progress

4. **Edit Captions**
   - Click on caption text to edit
   - Adjust start/end times
   - Delete unwanted captions
   - Add new captions

5. **Apply Style**
   - Select preset from dropdown
   - Adjust styling options
   - Preview changes in real-time

6. **Generate Preview**
   - Click "Generate Preview"
   - Scrub through timeline
   - Verify caption placement

7. **Export**
   - Click "Embed & Download"
   - Wait for rendering
   - Download captioned video

### Command-Line Interface

#### Simple SRT Generation

```bash
# Generate SRT from video
python video_to_srt.py input.mp4

# Specify output path
python video_to_srt.py input.mp4 --output output.srt

# Use different model
python video_to_srt.py input.mp4 --model swift

# Process audio file
python audio_to_srt.py input.mp3

# Any media (auto-detect)
python caption_generator.py input.mp4
```

#### Advanced Options

```bash
# Start web server with custom port
python web_server.py --port 8080

# Start with custom host
python web_server.py --host 0.0.0.0 --port 8080

# Start WebSocket server
python websocket_server.py --port 8000 --model-id Oriserve/Whisper-Hindi2Hinglish-Prime

# Stream from file
python client_file.py --uri ws://localhost:8000 --wav-path audio.wav --chunk-duration 10

# Stream from microphone
python client_mic.py --uri ws://localhost:8000 --device-index 0 --chunk-duration 10
```

### Batch Processing

#### Using Shell Script

```bash
#!/bin/bash

# batch_process.sh - Process multiple videos

INPUT_DIR="~/Videos/raw"
OUTPUT_DIR="~/Videos/processed"
MODEL="prime"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Process each video
for video in "$INPUT_DIR"/*.mp4; do
    filename=$(basename "$video")
    echo "Processing: $filename"

    # Generate captions
    python video_to_srt.py "$video" --model "$MODEL"

    # Move output
    mv "${video%.*}.srt" "$OUTPUT_DIR/"

    echo "✓ Completed: $filename"
done

echo "Batch processing complete!"
```

#### Using Python

```python
#!/usr/bin/env python3
# batch_process.py

import sys
from pathlib import Path
from video_caption_pipeline import VideoCaptionPipeline

def batch_process(input_dir, output_dir, style="reels_standard"):
    """Process all videos in input directory."""
    pipeline = VideoCaptionPipeline()
    input_path = Path(input_dir).expanduser()
    output_path = Path(output_dir).expanduser()
    output_path.mkdir(parents=True, exist_ok=True)

    results = {"success": [], "failed": []}

    for video_file in input_path.glob("*.mp4"):
        try:
            print(f"Processing: {video_file.name}")

            # Create session
            session_id = pipeline.create_caption_session(str(video_file))

            # Apply style
            pipeline.apply_caption_style(session_id, style)

            # Embed captions
            output_video = pipeline.embed_captions_to_video(session_id)

            # Copy to output
            final_output = output_path / Path(output_video).name
            Path(output_video).rename(final_output)

            results["success"].append(str(video_file))

            # Cleanup
            pipeline.delete_session(session_id)

        except Exception as e:
            print(f"✗ Failed: {video_file.name} - {e}")
            results["failed"].append(str(video_file))

    return results

if __name__ == "__main__":
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "~/Videos/raw"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "~/Videos/processed"

    results = batch_process(input_dir, output_dir)

    print(f"\n✓ Success: {len(results['success'])}")
    print(f"✗ Failed: {len(results['failed'])}")
```

### Different Workflows

#### Workflow 1: Quick Caption Generation

```bash
# Generate SRT only (no video embedding)
python video_to_srt.py video.mp4

# Output: video.srt
# Use this with video editors that support SRT
```

#### Workflow 2: Full Captioned Video

```python
from video_caption_pipeline import VideoCaptionPipeline

pipeline = VideoCaptionPipeline()
session_id = pipeline.create_caption_session("video.mp4")
pipeline.apply_caption_style(session_id, "reels_standard")
output = pipeline.embed_captions_to_video(session_id)

# Output: video_captioned.mp4 (ready for social media)
```

#### Workflow 3: Real-Time Transcription

```bash
# Start WebSocket server
python websocket_server.py --port 8000

# Stream from microphone
python client_mic.py --uri ws://localhost:8000 --device-index 0

# Stream from file
python client_file.py --uri ws://localhost:8000 --wav-path audio.wav
```

#### Workflow 4: API Integration

```python
import requests

# Upload and create session
with open("video.mp4", "rb") as f:
    response = requests.post(
        "http://localhost:5000/api/editor/upload",
        files={"video": f},
        data={"model_name": "prime"}
    )
    session_id = response.json()["session_id"]

# Apply style
requests.put(
    f"http://localhost:5000/api/sessions/{session_id}/style",
    json={"preset_name": "reels_standard"}
)

# Embed captions
response = requests.post(
    f"http://localhost:5000/api/sessions/{session_id}/embed",
    json={"burn": True}
)
output_path = response.json()["output_path"]

# Download captioned video
response = requests.get(
    f"http://localhost:5000/api/sessions/{session_id}/download"
)
with open("captioned_video.mp4", "wb") as f:
    f.write(response.content)
```

---

## 7. Configuration

### Style Presets

The infrastructure includes 5 built-in style presets:

1. **reels_standard** - Instagram Reels & TikTok
2. **shorts_safe** - YouTube Shorts (safe area)
3. **minimal_clean** - Minimalist design
4. **bold_impact** - High contrast
5. **cinematic** - Elegant/professional

### Model Configuration

```python
# In web_server.py or your code
MODEL_CONFIG = {
    "model_id": "Oriserve/Whisper-Hindi2Hinglish-Prime",  # or "Swift"
    "device": "cuda",  # or "cpu"
    "dtype": torch.float16,  # or torch.float32
}

# Usage
from caption_generator import media_to_srt
media_to_srt(
    "video.mp4",
    "output.srt",
    model_id="Oriserve/Whisper-Hindi2Hinglish-Prime"
)
```

### Caption Styling Options

```python
from caption_styling import TextStyle

# Create custom style
style = TextStyle(
    font_family="Fira Sans Compressed Medium",
    font_size=36,
    color="#FFFFFF",
    bold=True,
    italic=False,
    outline_color="#000000",
    outline_width=15,
    shadow=True,
    position_x=50,  # 0-100 (percentage)
    position_y=50,  # 0-100 (percentage)
    alignment="center"  # "left", "center", "right"
)
```

### Output Options

```python
# Output directory configuration
output_path = pipeline.embed_captions_to_video(
    session_id,
    output_path="/custom/path/output.mp4",  # Optional
    burn=True  # True = hard subtitles, False = soft subtitles
)

# Output files generated:
# - captioned_video.mp4 (with burned captions)
# - captions.srt (subtitle file)
# - audio.wav (extracted audio)
```

### Server Configuration

```bash
# Command-line options
python web_server.py \
    --host 0.0.0.0 \
    --port 5000 \
    --debug

# Environment variables
export FLASK_PORT=5000
export FLASK_HOST=0.0.0.0
export MODEL_ID=Oriserve/Whisper-Hindi2Hinglish-Prime
export DEVICE=cuda
export DTYPE=float16
```

---

## 8. Caption Styling

### Available Presets

#### 1. Reels Standard (`reels_standard`)

**Best for:** Instagram Reels, TikTok, Facebook Reels

**Properties:**
- Font: Fira Sans Compressed Medium
- Size: 36px
- Color: White (#FFFFFF)
- Outline: Black (#000000), 15px
- Shadow: Enabled
- Position: Center, 50% horizontal, 50% vertical
- Alignment: Center

**Style Definition:**
```json
{
  "font_family": "Fira Sans Compressed Medium",
  "font_size": 36,
  "color": "#FFFFFF",
  "bold": true,
  "italic": false,
  "outline_color": "#000000",
  "outline_width": 15,
  "shadow": true,
  "position_x": 50,
  "position_y": 50,
  "alignment": "center"
}
```

#### 2. YouTube Shorts Safe (`shorts_safe`)

**Best for:** YouTube Shorts (avoids UI elements)

**Properties:**
- Font: Fira Sans Compressed Medium
- Size: 32px
- Color: White (#FFFFFF)
- Outline: Black (#000000), 15px
- Shadow: Enabled
- Position: Center, 50% horizontal, 50% vertical
- Alignment: Center

**Note:** Higher vertical position to avoid YouTube interface elements

#### 3. Minimal Clean (`minimal_clean`)

**Best for:** Documentary-style videos, clean aesthetics

**Properties:**
- Font: Fira Sans Compressed Medium
- Size: 32px
- Color: White (#FFFFFF)
- Bold: Disabled
- Outline: Black (#000000), 15px
- Shadow: Enabled
- Position: Center, 50% horizontal, 50% vertical
- Alignment: Center

**Style:** Minimalist with subtle contrast

#### 4. Bold Impact (`bold_impact`)

**Best for:** Attention-grabbing captions, promotional content

**Properties:**
- Font: Fira Sans Compressed Medium
- Size: 40px
- Color: White (#FFFFFF)
- Bold: Enabled
- Outline: Black (#000000), 15px
- Shadow: Enabled
- Position: Center, 50% horizontal, 50% vertical
- Alignment: Center

**Style:** Maximum readability with large font

#### 5. Cinematic (`cinematic`)

**Best for:** Narrative content, professional videos

**Properties:**
- Font: Fira Sans Compressed Medium
- Size: 34px
- Color: White (#FFFFFF)
- Bold: Disabled
- Italic: Enabled
- Outline: Black (#000000), 15px
- Shadow: Enabled
- Position: Center, 50% horizontal, 50% vertical
- Alignment: Center

**Style:** Elegant with italic text

### Custom Styling Options

#### Font Configuration

```python
from caption_styling import TextStyle

# Custom font
custom_style = TextStyle(
    font_family="Your Custom Font",
    font_size=40,
    color="#FF5733",
    bold=True,
    italic=False,
    outline_color="#000000",
    outline_width=20,
    shadow=True,
    position_x=50,
    position_y=75,
    alignment="center"
)

# Apply to session
pipeline.apply_caption_style(
    session_id,
    preset_name="reels_standard",
    style_overrides=custom_style.to_dict()
)
```

#### Positioning Options

```python
# Position as percentage (0-100)
position_x=50  # Horizontal: 0=left, 50=center, 100=right
position_y=50  # Vertical: 0=top, 50=middle, 100=bottom

# Safe areas for different platforms:
# Instagram Reels: 0-90% vertical (avoid bottom 10%)
# YouTube Shorts: 0-80% vertical (avoid bottom 20% for UI)
# TikTok: 0-95% vertical (avoid bottom 5%)
```

#### Color Schemes

```python
# Popular color schemes

# High contrast (dark videos)
color="#FFFFFF"  # White text
outline_color="#000000"  # Black outline

# Light videos
color="#000000"  # Black text
outline_color="#FFFFFF"  # White outline

# Brand colors
color="#FF5733"  # Orange
color="#3498DB"  # Blue
color="#2ECC71"  # Green
color="#9B59B6"  # Purple

# Gradient effect (use outline)
color="#FFFFFF"
outline_color="#FF5733"  # Colored outline
outline_width=20
```

#### Creating Custom Presets

```python
from caption_styling import PresetManager, TextStyle, CaptionPreset

manager = PresetManager()

# Create custom preset
custom_preset = manager.create_preset(
    preset_id="my_custom_preset",
    name="My Custom Style",
    description="Custom styling for brand videos",
    text_style=TextStyle(
        font_family="Roboto Bold",
        font_size=42,
        color="#FF5733",
        bold=True,
        outline_color="#000000",
        outline_width=18,
        shadow=True,
        position_x=50,
        position_y=70,
        alignment="center"
    ),
    target_aspect_ratio="9:16",
    category="custom",
    save_to_file=True  # Saves to presets/ directory
)

# Use custom preset
pipeline.apply_caption_style(session_id, "my_custom_preset")
```

---

## 9. Model Information

### Oriserve/Whisper-Hindi2Hinglish-Prime

**Model Type:** Fine-tuned Whisper Large V3

**Language:** Hindi-English (Hinglish)

**Script Output:** Roman English (Latin script)

**Training Data:** ~550 hours of noisy Indian-accented Hindi data

#### Model Capabilities

✅ **Strengths:**
- High accuracy on Indian accents
- Excellent noise resistance
- Handles mixed Hindi-English (Hinglish)
- Word-level timestamps for precise timing
- Minimizes hallucinations in noisy environments
- Fast inference with streaming support

✅ **Supported Features:**
- Audio transcription to Hinglish
- Word-level timestamps
- VAD (Voice Activity Detection)
- Streaming transcription
- Batch processing

#### Model Limitations

⚠️ **Limitations:**
- Primarily trained on Hindi-English (may not perform well on other languages)
- Optimized for Indian accents (may struggle with other accents)
- Best performance on conversational speech
- May have errors on very fast speech
- Limited to audio transcription (no speaker diarization)

#### Performance Considerations

**Prime Model (Best Quality):**
- Model size: Large V3 (~3GB)
- Inference time: ~2-3x real-time on CPU
- WER (Word Error Rate): 28.68% (FLEURS)
- Best for: Production use, high accuracy requirements

**Swift Model (Faster):**
- Model size: Medium (~1.5GB)
- Inference time: ~1-2x real-time on CPU
- WER (Word Error Rate): 35.09% (FLEURS)
- Best for: Quick results, batch processing

**GPU Acceleration:**
- CUDA GPU: 10-20x faster than CPU
- VRAM required: 6GB+ (Prime), 4GB+ (Swift)
- Recommended: NVIDIA RTX 3060 or better

### Performance Benchmarks

| Dataset | Whisper Large V3 | Prime Model | Swift Model |
|---------|-----------------|-------------|-------------|
| Common Voice | 61.94% WER | 32.43% WER | 38.65% WER |
| FLEURS | 50.84% WER | 28.68% WER | 35.09% WER |
| Indic Voices | 82.56% WER | 60.82% WER | 65.21% WER |

**WER = Word Error Rate (lower is better)**

### Model Selection Guide

```python
# Choose model based on your needs

# Scenario 1: Production, high accuracy
model_id = "Oriserve/Whisper-Hindi2Hinglish-Prime"

# Scenario 2: Quick preview, batch processing
model_id = "Oriserve/Whisper-Hindi2Hinglish-Swift"

# Scenario 3: Resource-constrained environment
model_id = "Oriserve/Whisper-Hindi2Hinglish-Swift"
device = "cpu"

# Scenario 4: Maximum performance
model_id = "Oriserve/Whisper-Hindi2Hinglish-Prime"
device = "cuda"
dtype = torch.float16
```

---

## 10. Output Structure

### Directory Structure

```
~/Videos/Video-Name/
├── Video-Name_captioned.mp4  # Captioned video (final output)
├── Video-Name.srt            # SRT subtitle file
└── Video-Name.wav            # Extracted audio (16kHz, mono)
```

### Files Generated

#### 1. Captioned Video (`*_captioned.mp4`)

**Format:** MP4 (H.264 video, AAC audio)

**Resolution:** Same as input video

**Caption Type:** Hard subtitles (burned into video)

**Usage:** Ready for upload to social media platforms

**Specs:**
- Video codec: H.264 (libx264)
- Audio codec: AAC (copy from source)
- Preset: medium (balanced speed/quality)
- CRF: 23 (quality setting)

#### 2. SRT Subtitle File (`*.srt`)

**Format:** SubRip Text

**Encoding:** UTF-8

**Structure:**
```srt
1
00:00:00,000 --> 00:00:02,500
First caption text here

2
00:00:02,500 --> 00:00:05,000
Second caption text here

3
00:00:05,000 --> 00:00:07,500
Third caption text here
```

**Usage:**
- Import into video editors (Premiere, Final Cut, DaVinci)
- Use with media players (VLC, MPC-HC)
- Upload as closed captions to YouTube

#### 3. Audio File (`*.wav`)

**Format:** WAV (PCM)

**Sample Rate:** 16000 Hz

**Channels:** Mono (1 channel)

**Bit Depth:** 16-bit

**Usage:**
- Audio analysis
- Re-transcription with different settings
- Voice cloning

### Naming Conventions

**Input:** `my_video.mp4`

**Output:**
```
~/Videos/my_video/
├── my_video_captioned.mp4
├── my_video.srt
└── my_video.wav
```

**Rules:**
- Directory name = input filename (without extension)
- Video output = `{name}_captioned.mp4`
- SRT output = `{name}.srt`
- Audio output = `{name}.wav`

### File Formats and Specifications

#### Video Formats Supported

**Input:**
- MP4 (H.264, H.265)
- MOV (QuickTime)
- MKV (Matroska)
- AVI (Audio Video Interleave)
- WEBM (WebM)
- FLV (Flash Video)
- WMV (Windows Media Video)
- M4V (iTunes Video)

**Output:**
- MP4 (H.264, AAC) - Universal compatibility

#### Audio Formats Supported

**Input:**
- MP3 (MPEG Audio Layer 3)
- WAV (Waveform Audio)
- OGG (Ogg Vorbis)
- M4A (AAC in MP4)
- FLAC (Free Lossless Audio Codec)
- AAC (Advanced Audio Coding)
- WMA (Windows Media Audio)
- OPUS (Opus Audio Codec)

**Output:**
- WAV (PCM, 16kHz, mono) - For transcription

#### Caption Formats

**Generated:**
- SRT (SubRip Text) - Standard subtitle format
- ASS (Advanced Substation Alpha) - Internal use for styling

**Supported for Import:**
- SRT
- VTT (WebVTT) - Not directly supported, convert to SRT first

---

## 11. AI Agent Quick Reference

> **IMPORTANT FOR AI AGENTS**: This section provides quick reference commands and workflows for automated/programmatic use of the infrastructure.

### Environment Activation (Required)

```bash
# ALWAYS activate conda environment first
source ~/miniconda3/bin/activate whisper-hindi
# OR
conda activate whisper-hindi
```

### Quick Commands for Common Tasks

#### Generate SRT from Audio File (Simple)

```bash
# Basic SRT generation
source ~/miniconda3/bin/activate whisper-hindi
python -c "from caption_generator import media_to_srt; media_to_srt('/path/to/audio.wav', '/path/to/output.srt', model_id='Oriserve/Whisper-Hindi2Hinglish-Prime', device='cuda')"
```

#### Generate SRT from Video File

```bash
# Extract audio and generate SRT
source ~/miniconda3/bin/activate whisper-hindi
python -c "from caption_generator import media_to_srt; media_to_srt('/path/to/video.mp4', '/path/to/output.srt', model_id='Oriserve/Whisper-Hindi2Hinglish-Prime', device='cuda')"
```

#### Batch Process Videos (One at a Time)

Use the provided script which processes videos sequentially with GPU memory clearing:

```bash
source ~/miniconda3/bin/activate whisper-hindi
python batch_generate_srt.py
```

**Note**: Edit `batch_generate_srt.py` to update the video list before running.

#### Extract MP3 from Video

```bash
cd /path/to/video/directory
for video in *.mkv; do ffmpeg -i "$video" -vn -acodec libmp3lame -q:a 2 "${video%.*}.mp3"; done
```

#### Convert Audio to 16kHz Mono (Required for Whisper)

```bash
ffmpeg -i input.wav -ar 16000 -ac 1 -acodec pcm_s16le output_16khz.wav
```

### Direct Python API Usage

```python
# Always activate conda environment first in bash
# Then use this Python code:

import whisper_timestamped as whisper
import torch
from caption_generator import generate_srt, get_media_duration

# Load audio
audio = whisper.load_audio('/path/to/audio.wav')
print(f"Audio loaded: {len(audio)} samples, {len(audio)/16000:.2f}s")

# Check GPU availability and choose device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load model
model = whisper.load_model("Oriserve/Whisper-Hindi2Hinglish-Prime", device=device)

# Transcribe
result = whisper.transcribe(
    model,
    audio,
    language="hi",  # Hindi/Hinglish
    vad=False,
    condition_on_previous_text=False,
    remove_empty_words=True,
)

print(f"Transcription complete: {len(result['segments'])} segments")

# Generate SRT
media_duration = get_media_duration('/path/to/audio.wav')
generate_srt(result, "/path/to/output.srt", media_duration)
print("SRT file generated")
```

### GPU Memory Management

**For AI Agents**: Always check GPU availability and memory before processing:

```bash
# Check GPU status
nvidia-smi

# Check available memory
source ~/miniconda3/bin/activate whisper-hindi
python -c "import torch; print(f'GPU available: {torch.cuda.is_available()}'); print(f'GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB'); print(f'Free memory: {(torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated()) / 1024**3:.2f} GB')"
```

**Best Practices**:
- Process videos one at a time (don't batch process)
- Clear GPU memory between videos: `torch.cuda.empty_cache(); gc.collect()`
- Use CPU fallback when GPU is full (>80% usage)
- For videos >1 hour, consider using CPU instead of CUDA

### Model Selection Guide

```python
# Best for accuracy (use when GPU available and memory sufficient)
model_id = "Oriserve/Whisper-Hindi2Hinglish-Prime"
device = "cuda"

# Best for speed or when GPU memory is limited
model_id = "Oriserve/Whisper-Hindi2Hinglish-Swift"
device = "cuda"

# Best for very long files or when GPU is not available
model_id = "Oriserve/Whisper-Hindi2Hinglish-Prime"
device = "cpu"
```

### Conda Environment Details

The `whisper-hindi` conda environment contains:

```bash
# Check installed packages
source ~/miniconda3/bin/activate whisper-hindi
pip list | grep -E "torch|whisper|transformers|librosa|soundfile"
```

**Key Dependencies**:
- `torch` 2.5.1+cu121 (CUDA 12.1 support)
- `whisper-timestamped` 1.15.9
- `transformers` 5.1.0
- `librosa` 0.11.0
- `soundfile` 0.13.1

### Troubleshooting Common AI Agent Issues

#### Issue: "CUDA out of memory"
```python
# Solution 1: Use CPU instead
device = "cpu"

# Solution 2: Clear GPU memory
import torch, gc
torch.cuda.empty_cache()
gc.collect()

# Solution 3: Use smaller model
model_id = "Oriserve/Whisper-Hindi2Hinglish-Swift"
```

#### Issue: Audio format not supported by Whisper
```bash
# Solution: Convert to 16kHz mono WAV
ffmpeg -i input_file.wav -ar 16000 -ac 1 -acodec pcm_s16le output_file.wav
```

#### Issue: ModuleNotFoundError
```bash
# Solution: Ensure conda environment is activated
source ~/miniconda3/bin/activate whisper-hindi
```

### File Paths and Directories

**Working Directory**: `/home/ishanp/Documents/GitHub/Whisper-Hindi2Hinglish`

**Key Scripts**:
- `caption_generator.py` - Core SRT generation module
- `video_to_srt.py` - CLI wrapper for video to SRT
- `audio_to_srt.py` - CLI wrapper for audio to SRT
- `batch_generate_srt.py` - Batch processing script (processes one at a time)
- `media_handler.py` - Media validation and audio extraction
- `caption_styling.py` - Caption styling presets

**Output Locations**:
- SRT files are saved in the same directory as input media (unless specified)
- Default naming: `{input_filename}.srt`

### Example Complete Workflow for AI Agent

```bash
#!/bin/bash
# Complete workflow for processing a video

# 1. Activate conda environment
source ~/miniconda3/bin/activate whisper-hindi

# 2. Check GPU availability
python -c "import torch; print(f'GPU available: {torch.cuda.is_available()}')"

# 3. Process video to SRT
python -c "
from caption_generator import media_to_srt
import torch

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model_id = 'Oriserve/Whisper-Hindi2Hinglish-Prime'

media_to_srt(
    media_path='/path/to/video.mp4',
    output_srt_path='/path/to/output.srt',
    model_id=model_id,
    device=device
)
print('✓ SRT generation complete')
"

# 4. Verify output
ls -lh /path/to/output.srt
head -20 /path/to/output.srt
```

---

## 12. Troubleshooting

### Common Issues and Solutions

#### Issue 1: "FFmpeg not found"

**Symptoms:**
- Error: `FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.`
- Video processing fails
- Frame extraction fails

**Solutions:**

```bash
# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows (winget)
winget install ffmpeg

# Windows (manual)
# Download from: https://ffmpeg.org/download.html
# Add to PATH: System Properties > Environment Variables
```

**Verify Installation:**
```bash
ffmpeg -version
```

---

#### Issue 2: "CUDA out of memory"

**Symptoms:**
- Error: `CUDA out of memory`
- GPU memory exceeded
- Processing crashes mid-way

**Solutions:**

**Option 1: Use CPU instead**
```python
# In web_server.py or your code
MODEL_CONFIG = {
    "device": "cpu",  # Switch to CPU
    "dtype": torch.float32
}
```

**Option 2: Use smaller model**
```python
# Use Swift model instead of Prime
model_id = "Oriserve/Whisper-Hindi2Hinglish-Swift"
```

**Option 3: Process in chunks**
```python
# Split long videos into smaller segments
# Process each segment separately
# Merge results
```

**Option 4: Reduce batch size**
```python
# If using custom inference code
model.config.max_length = 448  # Reduce from default
```

---

#### Issue 3: "Port 5000 is in use"

**Symptoms:**
- Error: `Address already in use`
- Server fails to start

**Solutions:**

```bash
# Option 1: Use different port
python web_server.py --port 5001

# Option 2: Kill process using port 5000
# Linux/macOS
lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

---

#### Issue 4: "Caption embedding fails"

**Symptoms:**
- Error: `Failed to burn captions`
- FFmpeg error during rendering
- Output video not created

**Solutions:**

**Check FFmpeg version:**
```bash
ffmpeg -version
# Should be 4.0 or higher
```

**Check libass support:**
```bash
ffmpeg -filters | grep ass
# Should show "ass" filter
```

**Check disk space:**
```bash
df -h
# Need at least 2x video size free
```

**Try different quality settings:**
```python
# In burn_captions_into_video() function
# Change CRF value (lower = better quality, larger file)
command = [
    "ffmpeg",
    "-i", video_path,
    "-vf", vf_filter,
    "-c:v", "libx264",
    "-preset", "medium",  # or "fast", "slow"
    "-crf", "28",  # Increase from 23 to 28 (faster, smaller)
    "-c:a", "copy",
    "-y",
    output_path
]
```

---

#### Issue 5: "Poor transcription accuracy"

**Symptoms:**
- Many transcription errors
- Wrong words
- Missed words

**Solutions:**

**Use Prime model:**
```python
model_id = "Oriserve/Whisper-Hindi2Hinglish-Prime"
```

**Check audio quality:**
```bash
# Extract audio and check
ffmpeg -i video.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
# Play audio.wav to verify clarity
```

**Reduce background noise:**
```bash
# Use noise reduction (optional)
# Install sox: sudo apt install sox
sox input.wav output.wav noisered profile.noise-prof 0.21
```

**Adjust transcription parameters:**
```python
# In caption_generator.py
# Adjust word grouping parameters
subtitles = group_words_for_subtitles(
    segments,
    max_words=3,  # Reduce from 4
    max_chars=35,  # Reduce from 42
    max_pause_gap=0.3  # Reduce from 0.5
)
```

---

#### Issue 6: "Hindi text not rendering correctly"

**Symptoms:**
- Hindi characters appear as squares
- Font not found error
- Garbled text

**Solutions:**

**Check font availability:**
```bash
ls fonts/
# Should see .ttf or .otf files
```

**Install Devanagari fonts:**
```bash
# Linux
sudo apt install fonts-noto

# macOS
brew install font-noto

# Windows
# Download from: https://www.google.com/get/noto/
# Install Noto Sans Devanagari
```

**Add custom font:**
```bash
# Copy font file to fonts/ directory
cp /path/to/your/font.ttf fonts/
```

**Update font in style:**
```python
pipeline.apply_caption_style(
    session_id,
    style_overrides={
        "font_family": "Noto Sans Devanagari"
    }
)
```

---

#### Issue 7: "Session expired"

**Symptoms:**
- Error: `Session not found`
- Session ID invalid
- Data lost

**Solutions:**

**Check session lifetime:**
```python
# Default: 24 hours
# Check session_manager.py
SESSION_LIFETIME = 24 * 60 * 60  # 24 hours in seconds
```

**Extend session lifetime:**
```python
# In session_manager.py
SESSION_LIFETIME = 7 * 24 * 60 * 60  # 7 days
```

**Download before expiry:**
```python
# Always download captioned video before session expires
output_path = pipeline.embed_captions_to_video(session_id)
```

**Export session data:**
```python
# Get session info
session_info = pipeline.get_session_info(session_id)

# Save to JSON
import json
with open("session_backup.json", "w") as f:
    json.dump(session_info, f)
```

---

### Error Messages and Their Meanings

| Error Message | Meaning | Solution |
|---------------|---------|----------|
| `Media file not found` | Input file doesn't exist | Check file path |
| `Unsupported media format` | File format not supported | Use MP4, MOV, MKV, etc. |
| `FFmpeg not found` | FFmpeg not installed | Install FFmpeg |
| `CUDA out of memory` | GPU memory exceeded | Use CPU or smaller model |
| `Failed to parse SRT` | SRT file corrupted | Regenerate captions |
| `Preset not found` | Style preset invalid | Check preset name |
| `Font not found` | Font file missing | Add font to fonts/ |
| `Session not found` | Session expired/invalid | Create new session |
| `Failed to burn captions` | FFmpeg rendering failed | Check FFmpeg, disk space |

### Debugging Tips

#### Enable Debug Logging

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Or in code
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Check Server Logs

```bash
# Server logs show detailed error information
python web_server.py 2>&1 | tee server.log
```

#### Test Individual Components

```python
# Test media handler
from media_handler import get_media_type, validate_media_file
media_type = get_media_type("video.mp4")
is_valid = validate_media_file("video.mp4")

# Test caption generator
from caption_generator import media_to_srt
media_to_srt("video.mp4", "test.srt")

# Test frame extraction
from video_caption_pipeline import extract_frames_at_fps
frames = extract_frames_at_fps("video.mp4", "test_frames", fps=1)
```

#### Verify FFmpeg Commands

```bash
# Test frame extraction
ffmpeg -i video.mp4 -vf "fps=1,scale=160:-1" -q:v 2 frame_%05d.jpg

# Test caption burning
ffmpeg -i video.mp4 -vf "ass=captions.ass" -c:v libx264 -preset medium -crf 23 output.mp4
```

### Performance Optimization

#### Reduce Processing Time

```python
# 1. Use Swift model for quick results
model_id = "Oriserve/Whisper-Hindi2Hinglish-Swift"

# 2. Reduce preview frame count
preview = pipeline.generate_caption_preview(
    session_id,
    fps=1,
    max_frames=30  # Reduce from 60
)

# 3. Use GPU if available
device = "cuda"  # Instead of "cpu"

# 4. Disable preview generation (skip if not needed)
# Skip: generate_caption_preview()
```

#### Optimize Video Rendering

```python
# In burn_captions_to_video() function
command = [
    "ffmpeg",
    "-i", video_path,
    "-vf", vf_filter,
    "-c:v", "libx264",
    "-preset", "fast",  # Use "fast" instead of "medium"
    "-crf", "28",  # Increase from 23 to 28 (faster)
    "-c:a", "copy",
    "-threads", "4",  # Use 4 threads
    "-y",
    output_path
]
```

#### Batch Processing Optimization

```python
# Process multiple videos sequentially
# Don't process in parallel unless you have enough RAM

import concurrent.futures

def process_video(video_path):
    pipeline = VideoCaptionPipeline()
    session_id = pipeline.create_caption_session(video_path)
    pipeline.apply_caption_style(session_id, "reels_standard")
    output = pipeline.embed_captions_to_video(session_id)
    pipeline.delete_session(session_id)
    return output

# Use ThreadPoolExecutor with limited workers
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    futures = [executor.submit(process_video, v) for v in videos]
    results = [f.result() for f in futures]
```

---

## 12. Development Guidelines

### How to Add New Features

#### 1. Add New Style Preset

```python
# In caption_styling.py, add to DEFAULT_PRESETS
DEFAULT_PRESETS = {
    # ... existing presets ...
    "my_new_preset": {
        "name": "My New Preset",
        "description": "Description of preset",
        "text_style": {
            "font_family": "Font Name",
            "font_size": 36,
            "color": "#FFFFFF",
            "bold": True,
            "italic": False,
            "outline_color": "#000000",
            "outline_width": 15,
            "shadow": True,
            "position_x": 50,
            "position_y": 50,
            "alignment": "center"
        },
        "target_aspect_ratio": "9:16",
        "category": "custom"
    }
}
```

#### 2. Add New API Endpoint

```python
# In web_server.py
@app.route("/api/new-endpoint", methods=["POST"])
def new_endpoint():
    """Description of endpoint"""
    data = request.get_json()

    # Your logic here
    result = process_request(data)

    return jsonify({
        "success": True,
        "data": result
    })
```

#### 3. Add New Caption Feature

```python
# In video_caption_pipeline.py
class VideoCaptionPipeline:
    def new_feature(self, session_id: str, params: dict):
        """
        Description of new feature.

        Args:
            session_id: Session ID
            params: Feature parameters

        Returns:
            Result of feature
        """
        session = self.session_manager.get_session_or_raise(session_id)

        # Your logic here
        result = process_feature(session, params)

        return result
```

### Code Organization

```
Whisper-Hindi2Hinglish/
├── web_server.py              # Flask API server
├── websocket_server.py        # WebSocket streaming server
├── session_manager.py         # Session management
├── caption_styling.py         # Style presets and fonts
├── video_caption_pipeline.py  # Main pipeline orchestration
├── caption_generator.py       # Whisper transcription
├── media_handler.py           # Media file handling
├── utils.py                   # Utility functions
├── logger.py                  # Logging configuration
├── client_file.py             # File streaming client
├── client_mic.py              # Microphone streaming client
├── video_to_srt.py            # CLI: Video to SRT
├── audio_to_srt.py            # CLI: Audio to SRT
├── caption_generator.py       # CLI: Media to SRT
├── templates/                 # HTML templates
│   ├── launcher.html         # Landing page
│   ├── upload.html           # Upload interface
│   ├── editor.html           # Caption editor
│   └── sessions.html         # Session list
├── fonts/                     # Font files
├── presets/                   # Custom presets
├── sessions/                  # Session data
├── tests/                     # Test files
├── docs/                      # Documentation
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

### Testing Guidelines

#### Unit Tests

```python
# tests/test_caption_styling.py
import pytest
from caption_styling import TextStyle, PresetManager

def test_text_style_creation():
    style = TextStyle(
        font_family="Roboto",
        font_size=36,
        color="#FFFFFF"
    )
    assert style.font_family == "Roboto"
    assert style.font_size == 36

def test_preset_manager():
    manager = PresetManager()
    preset = manager.get_preset("reels_standard")
    assert preset is not None
    assert preset.name == "Reels Standard"

def test_invalid_color():
    with pytest.raises(ValueError):
        TextStyle(color="invalid")
```

#### Integration Tests

```python
# tests/test_pipeline.py
import pytest
from video_caption_pipeline import VideoCaptionPipeline
from pathlib import Path

@pytest.fixture
def pipeline():
    return VideoCaptionPipeline()

def test_create_session(pipeline):
    session_id = pipeline.create_caption_session("test_video.mp4")
    assert session_id is not None
    assert len(session_id) == 36  # UUID length

def test_apply_style(pipeline):
    session_id = pipeline.create_session("test_video.mp4")
    result = pipeline.apply_caption_style(session_id, "reels_standard")
    assert result is True

def test_embed_captions(pipeline):
    session_id = pipeline.create_session("test_video.mp4")
    pipeline.apply_caption_style(session_id, "reels_standard")
    output_path = pipeline.embed_captions_to_video(session_id)
    assert Path(output_path).exists()
```

#### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_caption_styling.py

# Run with coverage
pytest --cov=. tests/

# Run with verbose output
pytest -v tests/
```

### Contributing Guidelines

#### 1. Code Style

- Follow PEP 8 style guide
- Use type hints for function signatures
- Add docstrings to all functions and classes
- Use meaningful variable names

#### 2. Commit Messages

```
feat: Add new style preset for TikTok

- Add tiktok_viral preset to DEFAULT_PRESETS
- Update preset documentation
- Add unit tests for new preset

Closes #123
```

#### 3. Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes
4. Add tests
5. Commit your changes
6. Push to the branch (`git push origin feature/new-feature`)
7. Open a Pull Request

#### 4. Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] All tests pass

---

## 13. Technical Details

### Dependencies and Versions

#### Core Dependencies

```
accelerate>=1.2.1
librosa>=0.10.2
numpy>=1.24.0
torch>=2.9.0
torchvision>=0.20.0
torchaudio>=2.9.0
transformers>=4.47.0
webrtcvad>=2.0.10
websockets>=14.1
flask>=3.0.0
werkzeug>=3.0.1
whisper-timestamped>=1.15.9
```

#### Development Dependencies

```
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0
```

#### Optional Dependencies

```
flask-cors>=4.0.0  # For CORS support
Pillow>=10.0.0     # For image processing
```

### System Requirements

#### Minimum Requirements

- **CPU:** 4 cores
- **RAM:** 8GB
- **Storage:** 10GB
- **Python:** 3.10

#### Recommended Requirements

- **CPU:** 8 cores
- **RAM:** 16GB
- **Storage:** 20GB SSD
- **Python:** 3.11
- **GPU:** NVIDIA RTX 3060 (6GB VRAM)

#### For GPU Acceleration

- **CUDA:** 11.8 or 12.x
- **cuDNN:** 8.6 or newer
- **VRAM:** 6GB+ (Prime), 4GB+ (Swift)
- **Driver:** NVIDIA driver 525.60.11 or newer

### Performance Benchmarks

#### Transcription Speed

| Hardware | Model | Speed |
|----------|-------|-------|
| CPU (8 cores) | Prime | 0.3x real-time |
| CPU (8 cores) | Swift | 0.5x real-time |
| GPU (RTX 3060) | Prime | 3x real-time |
| GPU (RTX 3060) | Swift | 5x real-time |
| GPU (RTX 4090) | Prime | 8x real-time |
| GPU (RTX 4090) | Swift | 12x real-time |

#### Video Rendering Speed

| Hardware | Resolution | Speed |
|----------|------------|-------|
| CPU (8 cores) | 1080p | 0.5x real-time |
| GPU (RTX 3060) | 1080p | 2x real-time |
| GPU (RTX 4090) | 1080p | 5x real-time |

#### Memory Usage

| Component | CPU | GPU |
|-----------|-----|-----|
| Prime Model | 3GB RAM | 6GB VRAM |
| Swift Model | 1.5GB RAM | 4GB VRAM |
| Frame Extraction | 500MB RAM | N/A |
| Video Rendering | 1GB RAM | 2GB VRAM |

### Known Limitations

#### Transcription Limitations

- Maximum audio duration: ~10 minutes (practical limit)
- Best performance on conversational speech
- May struggle with very fast speech
- Limited to Hindi-English (Hinglish)
- No speaker diarization
- No emotion detection

#### Video Processing Limitations

- Maximum file size: 500MB
- Supported formats: MP4, MOV, MKV, WEBM, AVI, FLV, WMV, M4V
- Output resolution: Same as input (no upscaling)
- No video editing (only caption embedding)
- No automatic aspect ratio conversion

#### Caption Styling Limitations

- Maximum font size: 200px
- Limited to TrueType/OpenType fonts
- No animated captions
- No multi-language support
- Limited positioning options

#### Server Limitations

- No authentication (open access)
- No rate limiting per user
- Session lifetime: 24 hours
- No persistent storage beyond sessions
- No user management

---

## 14. Examples & Workflows

### Complete Workflow Example

```python
#!/usr/bin/env python3
"""
Complete workflow example:
1. Upload video
2. Generate captions
3. Edit captions
4. Apply style
5. Generate preview
6. Embed captions
7. Download results
"""

from pathlib import Path
from video_caption_pipeline import VideoCaptionPipeline
import json

def complete_workflow(input_video: str, output_dir: str = None):
    """Complete caption workflow."""

    # Initialize pipeline
    pipeline = VideoCaptionPipeline()

    print(f"📹 Processing: {input_video}")

    # Step 1: Create caption session
    print("⏳ Generating captions...")
    session_id = pipeline.create_caption_session(input_video, model_name="prime")
    print(f"✓ Session created: {session_id}")

    # Step 2: Get session info
    session_info = pipeline.get_session_info(session_id)
    print(f"  Video duration: {session_info['metadata'].get('duration', 'N/A')}s")

    # Step 3: Get captions
    print("\n📝 Captions:")
    from video_caption_pipeline import parse_srt_captions
    captions = parse_srt_captions(session_info['captions_path'])
    for caption in captions[:5]:  # Show first 5
        print(f"  [{caption.start_time:.1f}s - {caption.end_time:.1f}s] {caption.text}")

    # Step 4: Apply style
    print("\n🎨 Applying style preset...")
    pipeline.apply_caption_style(session_id, "reels_standard")
    print("✓ Style applied: reels_standard")

    # Step 5: Generate preview
    print("\n🖼️ Generating preview frames...")
    preview_data = pipeline.generate_caption_preview(
        session_id,
        fps=1,
        max_frames=30
    )
    print(f"✓ Generated {len(preview_data)} preview frames")

    # Step 6: Embed captions
    print("\n🎬 Embedding captions...")
    output_path = pipeline.embed_captions_to_video(session_id)
    print(f"✓ Captioned video: {output_path}")

    # Step 7: Show output files
    output_dir = Path(output_path).parent
    print(f"\n📁 Output directory: {output_dir}")
    print("  Files generated:")
    for file in output_dir.glob("*"):
        print(f"    - {file.name} ({file.stat().st_size / 1024 / 1024:.1f} MB)")

    # Step 8: Cleanup (optional)
    print("\n🧹 Cleanup...")
    pipeline.delete_session(session_id)
    print("✓ Session deleted")

    return output_path

if __name__ == "__main__":
    # Example usage
    input_video = "my_video.mp4"
    output = complete_workflow(input_video)
    print(f"\n✅ Complete! Output: {output}")
```

### Batch Processing Example

```python
#!/usr/bin/env python3
"""
Batch processing example:
Process multiple videos in a directory
"""

import sys
from pathlib import Path
from video_caption_pipeline import VideoCaptionPipeline
import time
from datetime import datetime

def batch_process_videos(
    input_dir: str,
    output_dir: str,
    style: str = "reels_standard",
    model: str = "prime"
):
    """Process all videos in input directory."""

    # Initialize pipeline
    pipeline = VideoCaptionPipeline()

    # Setup paths
    input_path = Path(input_dir).expanduser()
    output_path = Path(output_dir).expanduser()
    output_path.mkdir(parents=True, exist_ok=True)

    # Find all videos
    video_files = list(input_path.glob("*.mp4"))
    if not video_files:
        print(f"No videos found in {input_dir}")
        return

    print(f"Found {len(video_files)} videos to process")
    print(f"Output directory: {output_path}")
    print("=" * 60)

    # Process each video
    results = {
        "success": [],
        "failed": [],
        "total": len(video_files),
        "start_time": datetime.now().isoformat()
    }

    for idx, video_file in enumerate(video_files, 1):
        print(f"\n[{idx}/{len(video_files)}] Processing: {video_file.name}")
        start_time = time.time()

        try:
            # Create session
            session_id = pipeline.create_caption_session(
                str(video_file),
                model_name=model
            )

            # Apply style
            pipeline.apply_caption_style(session_id, style)

            # Embed captions
            output_video = pipeline.embed_captions_to_video(session_id)

            # Copy to output directory
            final_output = output_path / Path(output_video).name
            Path(output_video).rename(final_output)

            # Calculate time
            elapsed = time.time() - start_time
            file_size = final_output.stat().st_size / 1024 / 1024

            print(f"✓ Completed in {elapsed:.1f}s ({file_size:.1f} MB)")
            results["success"].append({
                "file": str(video_file),
                "output": str(final_output),
                "time": elapsed,
                "size": file_size
            })

            # Cleanup session
            pipeline.delete_session(session_id)

        except Exception as e:
            print(f"✗ Failed: {e}")
            results["failed"].append({
                "file": str(video_file),
                "error": str(e)
            })

    # Summary
    results["end_time"] = datetime.now().isoformat()
    print("\n" + "=" * 60)
    print("Batch Processing Summary:")
    print(f"  Total: {results['total']}")
    print(f"  Success: {len(results['success'])}")
    print(f"  Failed: {len(results['failed'])}")

    if results["success"]:
        total_time = sum(r["time"] for r in results["success"])
        avg_time = total_time / len(results["success"])
        total_size = sum(r["size"] for r in results["success"])
        print(f"  Total time: {total_time:.1f}s")
        print(f"  Average time: {avg_time:.1f}s")
        print(f"  Total output: {total_size:.1f} MB")

    # Save results
    results_file = output_path / "batch_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_file}")

    return results

if __name__ == "__main__":
    # Example usage
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "~/Videos/raw"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "~/Videos/processed"

    results = batch_process_videos(input_dir, output_dir)
```

### Custom Styling Example

```python
#!/usr/bin/env python3
"""
Custom styling example:
Create and apply custom caption styles
"""

from video_caption_pipeline import VideoCaptionPipeline
from caption_styling import TextStyle, PresetManager

def custom_styling_example(input_video: str):
    """Create and apply custom styles."""

    pipeline = VideoCaptionPipeline()
    preset_manager = PresetManager()

    # Create session
    session_id = pipeline.create_caption_session(input_video)

    # Example 1: Brand colors
    print("Example 1: Brand colors")
    brand_style = TextStyle(
        font_family="Fira Sans Compressed Medium",
        font_size=38,
        color="#FF5733",  # Orange
        bold=True,
        outline_color="#000000",
        outline_width=18,
        shadow=True,
        position_x=50,
        position_y=70,
        alignment="center"
    )
    pipeline.apply_caption_style(
        session_id,
        preset_name="reels_standard",
        style_overrides=brand_style.to_dict()
    )

    # Example 2: High contrast for dark videos
    print("Example 2: High contrast")
    high_contrast = TextStyle(
        font_family="Roboto Bold",
        font_size=44,
        color="#FFFFFF",
        bold=True,
        outline_color="#000000",
        outline_width=20,
        shadow=True,
        position_x=50,
        position_y=75,
        alignment="center"
    )
    pipeline.apply_caption_style(
        session_id,
        style_overrides=high_contrast.to_dict()
    )

    # Example 3: Save as custom preset
    print("Example 3: Create custom preset")
    custom_preset = preset_manager.create_preset(
        preset_id="my_brand_style",
        name="My Brand Style",
        description="Custom brand colors for captions",
        text_style=brand_style,
        target_aspect_ratio="9:16",
        category="custom",
        save_to_file=True
    )

    # Apply custom preset
    pipeline.apply_caption_style(session_id, "my_brand_style")

    # Generate output
    output = pipeline.embed_captions_to_video(session_id)
    print(f"✓ Output: {output}")

    return output

if __name__ == "__main__":
    custom_styling_example("my_video.mp4")
```

### Different Video Formats Supported

```python
#!/usr/bin/env python3
"""
Video format compatibility example
"""

from pathlib import Path
from video_caption_pipeline import VideoCaptionPipeline

def test_video_formats(input_dir: str):
    """Test processing different video formats."""

    pipeline = VideoCaptionPipeline()
    input_path = Path(input_dir).expanduser()

    # Supported formats
    supported_formats = {
        ".mp4": "MP4 (H.264/H.265)",
        ".mov": "MOV (QuickTime)",
        ".mkv": "MKV (Matroska)",
        ".avi": "AVI (Audio Video Interleave)",
        ".webm": "WebM",
        ".flv": "FLV (Flash Video)",
        ".wmv": "WMV (Windows Media)",
        ".m4v": "M4V (iTunes Video)"
    }

    print("Testing video format compatibility:")
    print("=" * 60)

    for ext, desc in supported_formats.items():
        # Find test file
        test_files = list(input_path.glob(f"*{ext}"))
        if test_files:
            test_file = test_files[0]
            print(f"\n{ext.upper()} - {desc}")
            print(f"  File: {test_file.name}")

            try:
                # Process file
                session_id = pipeline.create_caption_session(str(test_file))
                pipeline.apply_caption_style(session_id, "reels_standard")
                output = pipeline.embed_captions_to_video(session_id)

                # Check output
                output_path = Path(output)
                if output_path.exists():
                    print(f"  ✓ Success - Output: {output_path.name}")
                else:
                    print(f"  ✗ Failed - Output not created")

                # Cleanup
                pipeline.delete_session(session_id)

            except Exception as e:
                print(f"  ✗ Failed - Error: {e}")
        else:
            print(f"\n{ext.upper()} - {desc}")
            print(f"  No test file found")

if __name__ == "__main__":
    test_video_formats("~/Videos/test")
```

---

## 📞 Support & Resources

### Documentation

- **Quick Start Guide:** `docs/QUICK_START.md`
- **API Reference:** `docs/API_REFERENCE.md`
- **Installation Guide:** `docs/INSTALLATION.md`
- **User Guide:** `USER_GUIDE.md`

### Getting Help

- **GitHub Issues:** [Report bugs and request features](https://github.com/OriserveAI/Whisper-Hindi2Hinglish/issues)
- **Discussions:** [Ask questions and share ideas](https://github.com/OriserveAI/Whisper-Hindi2Hinglish/discussions)
- **Email:** ai-team@oriserve.com

### Related Projects

- [Original Whisper](https://github.com/openai/whisper) - OpenAI's Whisper model
- [Whisper-Timestamped](https://github.com/linto-ai/whisper-timestamped) - Word-level timestamps
- [FFmpeg](https://ffmpeg.org/) - Video processing framework

### License

Apache-2.0 - See [LICENSE](LICENSE) file for details

### Citation

If you use this project in your research, please cite:

```bibtex
@software{whisper_hindi2hinglish,
  title={Whisper-Hindi2Hinglish: Hindi-English ASR for Indian Accents},
  author={Oriserve AI Team},
  year={2024},
  url={https://github.com/OriserveAI/Whisper-Hindi2Hinglish}
}
```

---

## 🎉 Conclusion

This auto-captioning infrastructure provides a comprehensive solution for generating high-quality Hindi-English captions for short-form video content. With its modular architecture, extensive API, and user-friendly web interface, it can be easily integrated into various workflows and production environments.

**Key Benefits:**
- ✅ High accuracy on Indian accents
- ✅ Optimized for social media platforms
- ✅ Flexible styling options
- ✅ Multiple integration methods (API, CLI, Web UI)
- ✅ Batch processing support
- ✅ GPU acceleration

**Getting Started:**
1. Install dependencies (`pip install -r requirements.txt`)
2. Start the server (`python web_server.py`)
3. Open browser to `http://localhost:5000`
4. Upload your video and generate captions!

For more information, see the documentation in the `docs/` directory.

---

**Version:** 2.0.0
**Last Updated:** February 2026
**Maintained By:** Oriserve AI Team (ai-team@oriserve.com)
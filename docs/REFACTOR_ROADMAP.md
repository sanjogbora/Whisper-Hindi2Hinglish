# Video Caption Editor & Embedder - Refactoring Roadmap

**Project:** Whisper-Hindi2Hinglish - Video Caption Upgrade  
**Version:** 2.0  
**Last Updated:** 2026-02-11  
**Status:** Planning Phase  

---

## Executive Summary

This roadmap outlines the complete upgrade of the Whisper-Hindi2Hinglish application from a simple SRT generation tool to a full-featured video caption editor and embedder. The new system will provide:

1. **Multi-modal processing** - Audio-to-SRT (existing) + Video-to-captioned-video (new)
2. **Visual editor interface** - 1fps timeline preview with real-time caption editing
3. **Caption embedding pipeline** - Burn captions directly into videos with customizable styling
4. **Reels/Shorts optimization** - Pre-configured presets for social media formats (9:16 vertical)
5. **Three-step workflow** - Upload → Edit → Export

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Current System Analysis](#current-system-analysis)
3. [New Features Specification](#new-features-specification)
4. [Backend Implementation](#backend-implementation)
5. [Frontend Implementation](#frontend-implementation)
6. [Database & Session Management](#database--session-management)
7. [API Specification](#api-specification)
8. [Implementation Phases](#implementation-phases)
9. [Testing Strategy](#testing-strategy)
10. [Deployment Checklist](#deployment-checklist)

---

## Architecture Overview

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Browser                          │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │ Upload Page │  │ Editor Page │  │ Export/Download  │   │
│  └─────────────┘  └─────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ HTTP/WebSocket
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Flask Backend Server                       │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              API Layer (web_server.py)                │  │
│  │  /api/upload   /api/editor   /api/render   /api/get   │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                 │
│  ┌────────────────────────┼──────────────────────────────┐  │
│  │                   Service Layer                        │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │  │
│  │  │ Transcription│  │    Editor    │  │  Renderer │  │  │
│  │  │  Service     │  │   Service    │  │  Service  │  │  │
│  │  └──────────────┘  └──────────────┘  └───────────┘  │  │
│  └────────────────────────┼──────────────────────────────┘  │
│                           │                                 │
│  ┌────────────────────────┼──────────────────────────────┐  │
│  │                  Processing Layer                      │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │  │
│  │  │   Whisper    │  │  Frame       │  │  FFmpeg   │  │  │
│  │  │  (AI Model)  │  │  Extractor   │  │  Encoder  │  │  │
│  │  └──────────────┘  └──────────────┘  └───────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Storage Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Uploads    │  │   Sessions   │  │   Font Assets    │  │
│  │  (Temp Dir)  │  │  (JSON/DB)   │  │  (Roboto/etc)   │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Current System Analysis

### Existing Components

| Component | File | Current Function | Status |
|-----------|------|-----------------|--------|
| Web Server | `web_server.py` | Flask API, file upload/download | ✅ Reuse |
| Caption Generator | `caption_generator.py` | Whisper transcription to SRT | ✅ Reuse |
| Media Handler | `media_handler.py` | Audio/video I/O abstraction | ✅ Reuse |
| Utils | `utils.py` | Device detection, torch helpers | ✅ Reuse |
| Templates | `templates/` | HTML interfaces | 🔄 Major Update |

### Current Limitations

1. **One-way workflow** - Can only download SRT, no embedding
2. **No preview capability** - Users can't see captions before export
3. **No editing interface** - Cannot modify captions visually
4. **Limited styling** - No font, color, or positioning control
5. **No timeline view** - Cannot scrub through video with caption context

---

## New Features Specification

### Feature 1: Dual Mode Operation

**Mode A: SRT Generation Only (Existing)**
- Upload audio/video → Get SRT file
- Use case: Professional editors, separate caption files

**Mode B: Caption Editor & Embedder (New)**
- Upload video → Edit captions → Export video with burned captions
- Use case: Social media creators, quick publishing

### Feature 2: 1fps Timeline Preview

**Requirements:**
- Extract frames at exactly 1 frame per second
- Display as horizontal scrollable strip
- Show caption markers overlaid on timeline
- Click timeline to seek video player
- Hover to preview caption at that timestamp

**Technical Specs:**
- Frame size: 160x90px (16:9) or 90x160px (9:16) thumbnails
- Format: JPEG quality 80 for performance
- Storage: Temp directory, auto-cleanup after 24h

### Feature 3: Visual Caption Editor

**Components:**
- **Video Player** - HTML5 video with custom controls
- **Timeline Strip** - 1fps thumbnail sequence
- **Style Panel** - Font, color, position controls
- **Caption List** - Editable table with timing/text

### Feature 4: Pre-configured Presets

**Preset: "Reels Standard" (Default)**
```yaml
name: "Reels Standard"
description: "Optimized for Instagram Reels and TikTok"
aspect_ratio: "9:16"
font:
  family: "Roboto Bold"
  size: 36
  color: "#FFFFFF"
  opacity: 1.0
position:
  x: 50  # Percent, center
  y: 80  # Percent, bottom-safe area
  alignment: "center"
effects:
  outline:
    enabled: true
    color: "#000000"
    width: 2
  shadow:
    enabled: true
    color: "#000000"
    blur: 2
    offset_x: 2
    offset_y: 2
  background:
    enabled: false
```

**Preset: "YouTube Shorts"**
```yaml
name: "YouTube Shorts"
description: "Safe area for YouTube interface"
position:
  y: 75  # Higher to avoid UI elements
font:
  size: 32
```

**Preset: "Minimal Clean"**
```yaml
name: "Minimal Clean"
effects:
  outline:
    enabled: false
  background:
    enabled: true
    color: "#000000"
    opacity: 0.6
    padding: 10
```

### Feature 5: Caption Rendering Pipeline

**Input:** Video + SRT + Style Config  
**Output:** Video with burned-in captions

**Process:**
1. Convert SRT to ASS format with styling
2. Use FFmpeg libass filter to burn captions
3. Re-encode video with H.264
4. Copy audio stream (no re-encode)
5. Generate progress updates

---

## Backend Implementation

### New Module: `video_caption_pipeline.py`

**Location:** `/home/ishanp/Documents/GitHub/Whisper-Hindi2Hinglish/video_caption_pipeline.py`

**Purpose:** Main orchestration module for the caption editing pipeline

**Classes:**

```python
class CaptionSession:
    """Manages state for a single video editing session"""
    
    Attributes:
        session_id (str): UUID for session
        video_path (str): Path to uploaded video
        srt_path (str): Path to generated SRT
        captions (list[Caption]): Parsed caption objects
        style (StyleConfig): Current styling configuration
        preview_frames (list[str]): Paths to 1fps frame images
        status (str): 'uploaded', 'transcribed', 'editing', 'rendering', 'complete'
        created_at (datetime): Session creation time
        expires_at (datetime): Auto-cleanup time
    
    Methods:
        to_dict() -> dict: Serialize session
        from_dict(data: dict) -> CaptionSession: Deserialize
        cleanup(): Remove temp files

class Caption:
    """Individual caption/subtitle entry"""
    
    Attributes:
        index (int): Caption number
        start_time (float): Start in seconds
        end_time (float): End in seconds
        text (str): Caption text
        words (list[Word]): Word-level timestamps (optional)

class StyleConfig:
    """Caption styling configuration"""
    
    Attributes:
        preset_name (str): Name of preset
        font_family (str): Font file name
        font_size (int): Size in pixels
        font_color (str): Hex color
        position_x (int): X position (0-100 percent)
        position_y (int): Y position (0-100 percent)
        alignment (str): 'left', 'center', 'right'
        outline_enabled (bool)
        outline_color (str)
        outline_width (int)
        shadow_enabled (bool)
        shadow_color (str)
        shadow_blur (int)
        background_enabled (bool)
        background_color (str)
        background_opacity (float)

class CaptionPipeline:
    """Main pipeline orchestrator"""
    
    Methods:
        create_session(video_path: str) -> CaptionSession
        transcribe(session_id: str) -> None
        extract_preview_frames(session_id: str) -> list[str]
        generate_preview_image(session_id: str, timestamp: float) -> bytes
        update_captions(session_id: str, captions: list[dict]) -> None
        update_style(session_id: str, style: dict) -> None
        render_video(session_id: str, output_path: str) -> None
        get_render_progress(session_id: str) -> float
```

**Key Functions:**

```python
def extract_frames_at_fps(
    video_path: str, 
    output_dir: str, 
    fps: int = 1,
    width: int = 160
) -> list[str]:
    """
    Extract frames at specified FPS for timeline preview.
    
    Args:
        video_path: Path to video file
        output_dir: Directory to save frames
        fps: Frames per second (default 1)
        width: Width of thumbnails (maintains aspect ratio)
    
    Returns:
        List of frame file paths sorted by time
    """
    pass

def srt_to_ass(
    srt_path: str, 
    ass_path: str, 
    style: StyleConfig,
    video_resolution: tuple[int, int]
) -> None:
    """
    Convert SRT to ASS format with styling.
    
    Args:
        srt_path: Input SRT file
        ass_path: Output ASS file
        style: Style configuration
        video_resolution: (width, height) for scaling
    """
    pass

def burn_captions_into_video(
    video_path: str,
    ass_path: str,
    output_path: str,
    progress_callback: callable = None
) -> None:
    """
    Burn captions into video using FFmpeg.
    
    Args:
        video_path: Input video
        ass_path: ASS subtitle file with styles
        output_path: Output video path
        progress_callback: Function(progress_pct) for updates
    """
    pass

def generate_caption_overlay_preview(
    frame_path: str,
    caption_text: str,
    style: StyleConfig,
    video_resolution: tuple[int, int]
) -> bytes:
    """
    Generate preview image with caption overlay.
    
    Uses PIL to draw text with effects on extracted frame.
    Returns JPEG bytes for browser display.
    """
    pass
```

### New Module: `caption_styling.py`

**Location:** `/home/ishanp/Documents/GitHub/Whisper-Hindi2Hinglish/caption_styling.py`

**Purpose:** Manage presets and style configurations

```python
# Default Presets Dictionary
DEFAULT_PRESETS = {
    "reels_standard": {
        "name": "Reels Standard",
        "description": "Optimized for Instagram Reels and TikTok",
        "aspect_ratio": "9:16",
        "font_family": "Roboto Bold",
        "font_size": 36,
        "font_color": "#FFFFFF",
        "font_opacity": 1.0,
        "position_x": 50,
        "position_y": 80,
        "alignment": "center",
        "outline_enabled": True,
        "outline_color": "#000000",
        "outline_width": 2,
        "shadow_enabled": True,
        "shadow_color": "#000000",
        "shadow_blur": 2,
        "shadow_offset_x": 2,
        "shadow_offset_y": 2,
        "background_enabled": False,
    },
    "shorts_safe": {
        "name": "YouTube Shorts Safe",
        "description": "Safe area for YouTube interface elements",
        "inherits": "reels_standard",
        "position_y": 75,
    },
    "minimal_clean": {
        "name": "Minimal Clean",
        "description": "Clean look with semi-transparent background",
        "font_family": "Helvetica",
        "font_size": 32,
        "position_y": 85,
        "outline_enabled": False,
        "shadow_enabled": False,
        "background_enabled": True,
        "background_color": "#000000",
        "background_opacity": 0.6,
    },
    "bold_impact": {
        "name": "Bold Impact",
        "description": "High contrast for maximum readability",
        "font_family": "Arial Bold",
        "font_size": 40,
        "outline_width": 3,
        "shadow_blur": 4,
    }
}

def get_preset(preset_id: str) -> dict:
    """Get preset configuration by ID"""
    pass

def list_presets() -> list[dict]:
    """List all available presets"""
    pass

def get_available_fonts() -> list[str]:
    """List available font files in fonts/ directory"""
    pass

def validate_style_config(config: dict) -> tuple[bool, str]:
    """Validate style configuration, return (is_valid, error_message)"""
    pass
```

### New Module: `session_manager.py`

**Location:** `/home/ishanp/Documents/GitHub/Whisper-Hindi2Hinglish/session_manager.py`

**Purpose:** Manage editing sessions with persistence

```python
import json
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path

SESSION_DIR = Path.home() / ".whisper_caption_sessions"
SESSION_TIMEOUT_HOURS = 24

class SessionManager:
    """Manages caption editing sessions"""
    
    def __init__(self):
        SESSION_DIR.mkdir(exist_ok=True)
    
    def create_session(self, video_filename: str) -> str:
        """Create new session, return session_id"""
        session_id = str(uuid.uuid4())
        session_dir = SESSION_DIR / session_id
        session_dir.mkdir(exist_ok=True)
        
        session_data = {
            "session_id": session_id,
            "video_filename": video_filename,
            "video_path": None,
            "srt_path": None,
            "status": "created",
            "style_preset": "reels_standard",
            "captions": [],
            "preview_frames": [],
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=SESSION_TIMEOUT_HOURS)).isoformat()
        }
        
        self._save_session(session_id, session_data)
        return session_id
    
    def get_session(self, session_id: str) -> dict:
        """Get session data"""
        pass
    
    def update_session(self, session_id: str, updates: dict) -> None:
        """Update session fields"""
        pass
    
    def delete_session(self, session_id: str) -> None:
        """Delete session and cleanup files"""
        pass
    
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions, return count cleaned"""
        pass
    
    def _save_session(self, session_id: str, data: dict) -> None:
        """Persist session to disk"""
        session_file = SESSION_DIR / f"{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(data, f, indent=2)
```

---

## Frontend Implementation

### New Template: `editor.html`

**Location:** `/home/ishanp/Documents/GitHub/Whisper-Hindi2Hinglish/templates/editor.html`

**Layout Structure:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Video Caption Editor</title>
    <!-- Tailwind CSS -->
    <!-- Video.js for player -->
    <!-- Custom styles -->
</head>
<body class="bg-slate-900 text-white h-screen flex flex-col">
    
    <!-- Header -->
    <header class="bg-slate-800 p-4 flex justify-between items-center">
        <h1 class="text-xl font-bold">🎬 Caption Editor</h1>
        <div class="flex gap-2">
            <button id="btnPreview" class="px-4 py-2 bg-blue-600 rounded">Live Preview</button>
            <button id="btnExport" class="px-4 py-2 bg-green-600 rounded">Export Video</button>
        </div>
    </header>
    
    <!-- Main Content -->
    <div class="flex-1 flex overflow-hidden">
        
        <!-- Left Panel: Video Preview -->
        <div class="w-1/2 p-4 flex flex-col">
            <div class="bg-black rounded-lg overflow-hidden flex-1 flex items-center justify-center">
                <video id="videoPlayer" class="max-h-full max-w-full" controls>
                    <source src="" type="video/mp4">
                </video>
            </div>
            
            <!-- Timeline -->
            <div class="mt-4 bg-slate-800 rounded-lg p-4">
                <div class="text-sm text-gray-400 mb-2">Timeline (1fps) - Click to seek</div>
                <div id="timeline" class="flex gap-1 overflow-x-auto h-24">
                    <!-- Thumbnails injected here -->
                </div>
                <div id="captionMarkers" class="relative h-6 mt-1">
                    <!-- Caption markers overlay -->
                </div>
            </div>
        </div>
        
        <!-- Right Panel: Controls -->
        <div class="w-1/2 bg-slate-800 p-4 flex flex-col gap-4 overflow-y-auto">
            
            <!-- Style Presets -->
            <div class="bg-slate-700 rounded-lg p-4">
                <h3 class="font-semibold mb-2">Style Preset</h3>
                <select id="presetSelect" class="w-full p-2 bg-slate-600 rounded">
                    <option value="reels_standard">Reels Standard</option>
                    <option value="shorts_safe">YouTube Shorts Safe</option>
                    <option value="minimal_clean">Minimal Clean</option>
                    <option value="bold_impact">Bold Impact</option>
                </select>
            </div>
            
            <!-- Font Controls -->
            <div class="bg-slate-700 rounded-lg p-4">
                <h3 class="font-semibold mb-2">Typography</h3>
                
                <label class="block text-sm text-gray-400 mb-1">Font Family</label>
                <select id="fontFamily" class="w-full p-2 bg-slate-600 rounded mb-3">
                    <!-- Options loaded from API -->
                </select>
                
                <label class="block text-sm text-gray-400 mb-1">Size: <span id="fontSizeVal">36</span>px</label>
                <input type="range" id="fontSize" min="20" max="72" value="36" class="w-full mb-3">
                
                <label class="block text-sm text-gray-400 mb-1">Color</label>
                <input type="color" id="fontColor" value="#FFFFFF" class="w-full h-10 rounded mb-3">
            </div>
            
            <!-- Position Controls -->
            <div class="bg-slate-700 rounded-lg p-4">
                <h3 class="font-semibold mb-2">Position</h3>
                
                <label class="block text-sm text-gray-400 mb-1">Horizontal: <span id="posXVal">50</span>%</label>
                <input type="range" id="posX" min="10" max="90" value="50" class="w-full mb-3">
                
                <label class="block text-sm text-gray-400 mb-1">Vertical: <span id="posYVal">80</span>%</label>
                <input type="range" id="posY" min="10" max="90" value="80" class="w-full mb-3">
                
                <label class="block text-sm text-gray-400 mb-1">Alignment</label>
                <div class="flex gap-2">
                    <button class="flex-1 p-2 bg-slate-600 rounded text-left">Left</button>
                    <button class="flex-1 p-2 bg-blue-600 rounded text-center">Center</button>
                    <button class="flex-1 p-2 bg-slate-600 rounded text-right">Right</button>
                </div>
            </div>
            
            <!-- Effects -->
            <div class="bg-slate-700 rounded-lg p-4">
                <h3 class="font-semibold mb-2">Effects</h3>
                
                <label class="flex items-center gap-2 mb-2">
                    <input type="checkbox" id="outlineEnabled" checked>
                    <span>Text Outline</span>
                </label>
                
                <label class="flex items-center gap-2 mb-2">
                    <input type="checkbox" id="shadowEnabled" checked>
                    <span>Text Shadow</span>
                </label>
                
                <label class="flex items-center gap-2">
                    <input type="checkbox" id="backgroundEnabled">
                    <span>Background Box</span>
                </label>
            </div>
            
            <!-- Caption List -->
            <div class="bg-slate-700 rounded-lg p-4 flex-1">
                <div class="flex justify-between items-center mb-2">
                    <h3 class="font-semibold">Captions</h3>
                    <button id="addCaption" class="text-sm px-2 py-1 bg-blue-600 rounded">+ Add</button>
                </div>
                <div id="captionList" class="space-y-2 max-h-64 overflow-y-auto">
                    <!-- Caption items injected here -->
                </div>
            </div>
            
        </div>
    </div>
    
    <!-- Export Progress Modal -->
    <div id="exportModal" class="hidden fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center">
        <div class="bg-slate-800 rounded-lg p-8 max-w-md w-full">
            <h2 class="text-xl font-bold mb-4">Rendering Video...</h2>
            <div class="w-full bg-slate-700 rounded-full h-4 mb-4">
                <div id="renderProgress" class="bg-blue-600 h-4 rounded-full transition-all" style="width: 0%"></div>
            </div>
            <p id="renderStatus" class="text-center text-gray-400">Initializing...</p>
        </div>
    </div>
    
    <script>
        // JavaScript implementation (see below)
    </script>
</body>
</html>
```

### Frontend JavaScript Architecture

```javascript
// Main Application State
const AppState = {
    sessionId: null,
    videoInfo: null,
    captions: [],
    style: {},
    currentTime: 0,
    isRendering: false,
    previewCache: new Map()
};

// API Client
const API = {
    async uploadVideo(file, model = 'prime') {
        const formData = new FormData();
        formData.append('video', file);
        formData.append('model', model);
        
        const response = await fetch('/api/video/upload', {
            method: 'POST',
            body: formData
        });
        return response.json();
    },
    
    async getPreviewFrames(sessionId) {
        const response = await fetch(`/api/video/preview/${sessionId}`);
        return response.json();
    },
    
    async getCaptions(sessionId) {
        const response = await fetch(`/api/video/captions/${sessionId}`);
        return response.json();
    },
    
    async updateCaptions(sessionId, captions) {
        const response = await fetch(`/api/video/captions/${sessionId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ captions })
        });
        return response.json();
    },
    
    async updateStyle(sessionId, style) {
        const response = await fetch(`/api/video/style/${sessionId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ style })
        });
        return response.json();
    },
    
    async renderVideo(sessionId) {
        const response = await fetch(`/api/video/render/${sessionId}`, {
            method: 'POST'
        });
        return response.json();
    },
    
    async getRenderProgress(sessionId) {
        const response = await fetch(`/api/video/progress/${sessionId}`);
        return response.json();
    },
    
    async getLivePreview(sessionId, timestamp) {
        const response = await fetch(`/api/video/preview-frame/${sessionId}?t=${timestamp}`);
        return response.blob();
    }
};

// Timeline Controller
const TimelineController = {
    init(frames) {
        this.renderTimeline(frames);
        this.bindEvents();
    },
    
    renderTimeline(frames) {
        const container = document.getElementById('timeline');
        container.innerHTML = frames.map((frame, idx) => `
            <div class="timeline-frame flex-shrink-0 cursor-pointer hover:opacity-80" 
                 data-time="${idx}" title="${idx}s">
                <img src="${frame.url}" class="w-24 h-14 object-cover rounded">
            </div>
        `).join('');
    },
    
    bindEvents() {
        document.getElementById('timeline').addEventListener('click', (e) => {
            const frame = e.target.closest('.timeline-frame');
            if (frame) {
                const time = parseInt(frame.dataset.time);
                VideoPlayer.seek(time);
            }
        });
    },
    
    updatePlayhead(currentTime) {
        // Update visual playhead position on timeline
    }
};

// Style Controller
const StyleController = {
    currentStyle: {},
    
    init() {
        this.bindControls();
        this.loadPresets();
    },
    
    bindControls() {
        // Font size slider
        document.getElementById('fontSize').addEventListener('input', (e) => {
            this.currentStyle.font_size = parseInt(e.target.value);
            document.getElementById('fontSizeVal').textContent = e.target.value;
            this.debouncedUpdate();
        });
        
        // Position sliders
        document.getElementById('posX').addEventListener('input', (e) => {
            this.currentStyle.position_x = parseInt(e.target.value);
            document.getElementById('posXVal').textContent = e.target.value;
            this.debouncedUpdate();
        });
        
        // Color picker
        document.getElementById('fontColor').addEventListener('change', (e) => {
            this.currentStyle.font_color = e.target.value;
            this.debouncedUpdate();
        });
        
        // Preset selection
        document.getElementById('presetSelect').addEventListener('change', (e) => {
            this.loadPreset(e.target.value);
        });
    },
    
    debouncedUpdate: debounce(async function() {
        await API.updateStyle(AppState.sessionId, this.currentStyle);
        PreviewRenderer.update();
    }, 300),
    
    async loadPreset(presetId) {
        const response = await fetch(`/api/styles/presets/${presetId}`);
        const preset = await response.json();
        this.applyPreset(preset);
    }
};

// Preview Renderer
const PreviewRenderer = {
    async update() {
        const timestamp = VideoPlayer.currentTime;
        const cacheKey = `${AppState.sessionId}_${timestamp}_${JSON.stringify(AppState.style)}`;
        
        if (AppState.previewCache.has(cacheKey)) {
            this.displayPreview(AppState.previewCache.get(cacheKey));
            return;
        }
        
        try {
            const blob = await API.getLivePreview(AppState.sessionId, timestamp);
            const url = URL.createObjectURL(blob);
            AppState.previewCache.set(cacheKey, url);
            this.displayPreview(url);
        } catch (error) {
            console.error('Preview generation failed:', error);
        }
    },
    
    displayPreview(imageUrl) {
        // Update preview display
    }
};

// Video Player Wrapper
const VideoPlayer = {
    element: null,
    currentTime: 0,
    
    init(videoUrl) {
        this.element = document.getElementById('videoPlayer');
        this.element.src = videoUrl;
        this.bindEvents();
    },
    
    bindEvents() {
        this.element.addEventListener('timeupdate', () => {
            this.currentTime = this.element.currentTime;
            TimelineController.updatePlayhead(this.currentTime);
        });
    },
    
    seek(time) {
        this.element.currentTime = time;
        this.currentTime = time;
    }
};

// Export Controller
const ExportController = {
    async startRender() {
        AppState.isRendering = true;
        document.getElementById('exportModal').classList.remove('hidden');
        
        const { render_id } = await API.renderVideo(AppState.sessionId);
        this.pollProgress(render_id);
    },
    
    async pollProgress(renderId) {
        const interval = setInterval(async () => {
            const progress = await API.getRenderProgress(renderId);
            
            document.getElementById('renderProgress').style.width = `${progress.percent}%`;
            document.getElementById('renderStatus').textContent = progress.status;
            
            if (progress.status === 'complete') {
                clearInterval(interval);
                this.downloadVideo(progress.output_url);
            }
        }, 1000);
    },
    
    downloadVideo(url) {
        // Trigger download
    }
};

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    // Parse session ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    AppState.sessionId = urlParams.get('session');
    
    if (AppState.sessionId) {
        initializeEditor();
    }
});

async function initializeEditor() {
    // Load session data
    const frames = await API.getPreviewFrames(AppState.sessionId);
    const captions = await API.getCaptions(AppState.sessionId);
    
    AppState.captions = captions;
    
    // Initialize components
    TimelineController.init(frames);
    VideoPlayer.init(frames.video_url);
    StyleController.init();
    
    // Render caption list
    renderCaptionList();
}

function renderCaptionList() {
    const container = document.getElementById('captionList');
    container.innerHTML = AppState.captions.map((cap, idx) => `
        <div class="bg-slate-600 rounded p-3 flex gap-2" data-index="${idx}">
            <span class="text-gray-400 text-sm">${formatTime(cap.start)}</span>
            <input type="text" value="${cap.text}" 
                   class="flex-1 bg-transparent border-b border-gray-500 focus:border-blue-500 outline-none"
                   onchange="updateCaptionText(${idx}, this.value)">
            <button onclick="deleteCaption(${idx})" class="text-red-400 hover:text-red-300">×</button>
        </div>
    `).join('');
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}
```

---

## API Specification

### 1. Video Upload & Initialization

**Endpoint:** `POST /api/video/upload`

**Request:**
```http
Content-Type: multipart/form-data

video: <binary file>
model: "prime" | "swift" (optional, default: "prime")
```

**Response:**
```json
{
    "success": true,
    "session_id": "uuid-string",
    "video_info": {
        "filename": "input.mp4",
        "duration": 120.5,
        "resolution": [1080, 1920],
        "fps": 60
    },
    "redirect_url": "/editor?session=uuid-string"
}
```

### 2. Get Preview Frames

**Endpoint:** `GET /api/video/preview/{session_id}`

**Response:**
```json
{
    "frames": [
        {
            "timestamp": 0,
            "url": "/api/video/frame/{session_id}/0",
            "has_caption": true
        },
        {
            "timestamp": 1,
            "url": "/api/video/frame/{session_id}/1",
            "has_caption": false
        }
    ],
    "total_frames": 121,
    "video_url": "/api/video/stream/{session_id}"
}
```

### 3. Get Caption Frame Preview

**Endpoint:** `GET /api/video/preview-frame/{session_id}?t={timestamp}`

**Query Parameters:**
- `t`: Timestamp in seconds (float)

**Response:**
```http
Content-Type: image/jpeg

<binary image data with caption overlay>
```

### 4. Get Captions

**Endpoint:** `GET /api/video/captions/{session_id}`

**Response:**
```json
{
    "captions": [
        {
            "index": 1,
            "start": 0.2,
            "end": 1.36,
            "text": "Kal mainne kaha tha"
        },
        {
            "index": 2,
            "start": 1.36,
            "end": 3.16,
            "text": "wealth hustle se nahin"
        }
    ],
    "style": {
        "preset": "reels_standard",
        "font_family": "Roboto Bold",
        "font_size": 36,
        "font_color": "#FFFFFF",
        "position_x": 50,
        "position_y": 80
    }
}
```

### 5. Update Captions

**Endpoint:** `PUT /api/video/captions/{session_id}`

**Request:**
```json
{
    "captions": [
        {
            "index": 1,
            "start": 0.2,
            "end": 1.36,
            "text": "Modified caption text"
        }
    ]
}
```

**Response:**
```json
{
    "success": true,
    "updated_count": 1
}
```

### 6. Update Style

**Endpoint:** `PUT /api/video/style/{session_id}`

**Request:**
```json
{
    "style": {
        "preset": "custom",
        "font_family": "Roboto Bold",
        "font_size": 40,
        "font_color": "#FFFF00",
        "position_x": 50,
        "position_y": 85,
        "outline_enabled": true,
        "outline_width": 3
    }
}
```

**Response:**
```json
{
    "success": true,
    "preview_url": "/api/video/preview-frame/{session_id}?t=5&style_hash=abc123"
}
```

### 7. Get Style Presets

**Endpoint:** `GET /api/styles/presets`

**Response:**
```json
{
    "presets": [
        {
            "id": "reels_standard",
            "name": "Reels Standard",
            "description": "Optimized for Instagram Reels",
            "thumbnail": "/static/presets/reels_standard.jpg"
        },
        {
            "id": "minimal_clean",
            "name": "Minimal Clean",
            "description": "Clean look with background",
            "thumbnail": "/static/presets/minimal_clean.jpg"
        }
    ]
}
```

**Endpoint:** `GET /api/styles/presets/{preset_id}`

**Response:**
```json
{
    "id": "reels_standard",
    "name": "Reels Standard",
    "config": {
        "font_family": "Roboto Bold",
        "font_size": 36,
        "font_color": "#FFFFFF",
        "position_x": 50,
        "position_y": 80
        // ... full config
    }
}
```

### 8. Render Video

**Endpoint:** `POST /api/video/render/{session_id}`

**Request:**
```json
{
    "quality": "high" | "medium" | "low" (optional, default: "high")
}
```

**Response:**
```json
{
    "success": true,
    "render_id": "render-uuid",
    "status": "queued",
    "estimated_time": 45
}
```

### 9. Get Render Progress

**Endpoint:** `GET /api/video/progress/{render_id}`

**Response:**
```json
{
    "render_id": "render-uuid",
    "status": "rendering",  // queued, rendering, complete, error
    "percent": 65,
    "current_frame": 4500,
    "total_frames": 7200,
    "eta_seconds": 18,
    "output_url": null  // populated when complete
}
```

### 10. Download Rendered Video

**Endpoint:** `GET /api/video/download/{render_id}`

**Response:**
```http
Content-Type: video/mp4
Content-Disposition: attachment; filename="video_with_captions.mp4"

<binary video data>
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)

**Day 1-2: Backend Core**
- [ ] Create `session_manager.py` with session persistence
- [ ] Create `caption_styling.py` with preset definitions
- [ ] Set up fonts directory with default fonts (Roboto)

**Day 3-4: Video Processing**
- [ ] Implement frame extraction at 1fps
- [ ] Implement SRT to ASS conversion
- [ ] Implement FFmpeg caption burning

**Day 5: API Development**
- [ ] Add `/api/video/upload` endpoint
- [ ] Add `/api/video/preview/{id}` endpoint
- [ ] Add `/api/video/captions/{id}` endpoints

**Deliverable:** Functional backend with frame extraction and caption rendering

### Phase 2: Editor Interface (Week 2)

**Day 1-2: Frontend Layout**
- [ ] Create `editor.html` with two-panel layout
- [ ] Implement video player integration
- [ ] Implement 1fps timeline strip

**Day 3-4: Style Controls**
- [ ] Implement preset selector
- [ ] Implement font/color/position controls
- [ ] Implement live preview updates

**Day 5: Caption Management**
- [ ] Implement caption list editor
- [ ] Implement add/edit/delete captions
- [ ] Implement caption synchronization with video

**Deliverable:** Functional editor with visual controls

### Phase 3: Integration & Polish (Week 3)

**Day 1-2: Workflow Integration**
- [ ] Connect upload page to editor
- [ ] Implement render pipeline
- [ ] Implement progress tracking

**Day 3-4: Testing & Optimization**
- [ ] Test with various video formats
- [ ] Optimize preview generation (caching)
- [ ] Test Hindi text rendering

**Day 5: Documentation & Cleanup**
- [ ] Update README with new features
- [ ] Add inline help tooltips
- [ ] Code cleanup and refactoring

**Deliverable:** Production-ready system

---

## Testing Strategy

### Unit Tests

**File:** `tests/test_caption_pipeline.py`

```python
def test_frame_extraction():
    """Test 1fps frame extraction"""
    frames = extract_frames_at_fps("test_video.mp4", "/tmp/frames", fps=1)
    assert len(frames) == 60  # For 60s video

def test_srt_to_ass_conversion():
    """Test SRT to ASS conversion with styling"""
    srt_to_ass("test.srt", "output.ass", StyleConfig(), (1080, 1920))
    assert os.path.exists("output.ass")
    with open("output.ass") as f:
        content = f.read()
        assert "Style: Default" in content

def test_caption_burning():
    """Test FFmpeg caption burning"""
    burn_captions_into_video("input.mp4", "captions.ass", "output.mp4")
    assert os.path.exists("output.mp4")
    # Verify video has captions by extracting a frame
```

### Integration Tests

**File:** `tests/test_editor_workflow.py`

```python
def test_full_workflow():
    """Test complete workflow: upload → edit → render"""
    # Upload video
    session = api.upload_video("test.mp4")
    
    # Get preview frames
    frames = api.get_preview_frames(session["session_id"])
    assert len(frames["frames"]) > 0
    
    # Update style
    api.update_style(session["session_id"], {
        "font_size": 40,
        "position_y": 85
    })
    
    # Render video
    render = api.render_video(session["session_id"])
    
    # Poll until complete
    while True:
        progress = api.get_render_progress(render["render_id"])
        if progress["status"] == "complete":
            break
        time.sleep(1)
    
    assert os.path.exists(progress["output_url"])
```

### Manual Testing Checklist

**Upload & Transcription:**
- [ ] Upload MP4 video (vertical 9:16)
- [ ] Verify transcription generates captions
- [ ] Check Hindi text is properly captured

**Editor Functionality:**
- [ ] Timeline displays 1fps frames
- [ ] Click timeline seeks video
- [ ] Caption markers visible on timeline
- [ ] Edit caption text updates preview

**Style Controls:**
- [ ] Preset selection changes preview
- [ ] Font size slider works
- [ ] Color picker updates text color
- [ ] Position sliders move caption

**Export:**
- [ ] Render video completes successfully
- [ ] Output video has burned captions
- [ ] Caption styling matches editor preview
- [ ] Download works correctly

**Edge Cases:**
- [ ] Long caption text wraps properly
- [ ] Special characters (Hindi) render correctly
- [ ] Very short videos (< 5s) work
- [ ] Very long videos (> 5min) handle gracefully

---

## Deployment Checklist

### Pre-deployment

- [ ] All tests passing
- [ ] Dependencies updated in `requirements.txt`
- [ ] Font files included in package
- [ ] Documentation updated

### Environment Setup

```bash
# Create fonts directory
mkdir -p fonts/
cp /usr/share/fonts/truetype/roboto/Roboto-Bold.ttf fonts/
cp /usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf fonts/

# Verify FFmpeg capabilities
ffmpeg -filters | grep ass  # Should show 'ass' filter

# Test transcription model download
python -c "from caption_generator import media_to_srt; print('Models ready')"
```

### Configuration

**Environment Variables:**
```bash
export CAPTION_SESSION_TIMEOUT=24  # hours
export CAPTION_MAX_FILE_SIZE=500   # MB
export CAPTION_PREVIEW_CACHE_SIZE=100  # entries
export CAPTION_RENDER_THREADS=4
```

### Monitoring

**Log Files:**
- `/var/log/whisper-captions/web.log` - Web server
- `/var/log/whisper-captions/render.log` - Rendering jobs
- `/var/log/whisper-captions/session.log` - Session management

**Metrics to Track:**
- Upload success rate
- Transcription accuracy
- Render completion rate
- Average render time
- Session cleanup efficiency

---

## Appendix A: Font Setup

### Required Fonts

Install these fonts on the server:

```bash
# Ubuntu/Debian
sudo apt-get install fonts-roboto fonts-noto-core

# Or download manually
wget https://github.com/googlefonts/roboto/releases/download/v2.138/roboto-android.zip
unzip roboto-android.zip -d fonts/
```

### Font Configuration

Create `fonts/fonts.json`:

```json
{
    "fonts": [
        {
            "id": "roboto_bold",
            "name": "Roboto Bold",
            "file": "Roboto-Bold.ttf",
            "supports_hindi": false
        },
        {
            "id": "noto_sans_devanagari",
            "name": "Noto Sans Devanagari",
            "file": "NotoSansDevanagari-Bold.ttf",
            "supports_hindi": true
        }
    ]
}
```

---

## Appendix B: ASS Format Reference

### Complete ASS Template

```ini
[Script Info]
Title: Whisper Captions
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Roboto Bold,36,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.20,0:00:01.36,Default,,0,0,0,,Kal mainne kaha tha
Dialogue: 0,0:00:01.36,0:00:03.16,Default,,0,0,0,,wealth hustle se nahin
```

### Alignment Values

| Value | Position          |
|-------|-------------------|
| 1     | Bottom Left       |
| 2     | Bottom Center     |
| 3     | Bottom Right      |
| 4     | Middle Left       |
| 5     | Middle Center     |
| 6     | Middle Right      |
| 7     | Top Left          |
| 8     | Top Center        |
| 9     | Top Right         |

---

## Appendix C: Troubleshooting Guide

### Common Issues

**1. Hindi text not rendering**
- Verify Noto Sans Devanagari font is installed
- Check `supports_hindi: true` in font config
- Ensure FFmpeg compiled with libass

**2. Preview generation slow**
- Enable preview caching
- Reduce preview image size
- Use WebP format instead of JPEG

**3. Render fails with large videos**
- Check available disk space
- Increase render timeout
- Use lower quality preset for testing

**4. Session timeout errors**
- Increase `CAPTION_SESSION_TIMEOUT`
- Implement auto-save
- Add session recovery

---

## Conclusion

This roadmap provides a complete specification for upgrading the Whisper-Hindi2Hinglish application with video caption editing capabilities. The implementation follows a modular approach with clear separation of concerns:

1. **Backend** - Session management, video processing, rendering pipeline
2. **Frontend** - Visual editor with real-time preview and controls
3. **API** - RESTful endpoints for all operations
4. **Styling** - Preset system for quick configuration

The system is designed to be extensible, allowing for future enhancements like additional presets, animation effects, and batch processing.

**Next Steps:**
1. Review and approve roadmap
2. Set up development environment
3. Begin Phase 1 implementation
4. Weekly progress reviews

---

*Document Version: 1.0*  
*Last Updated: 2026-02-11*  
*Maintainer: Development Team*
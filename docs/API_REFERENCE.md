# API Reference

Complete API documentation for Whisper-Hindi2Hinglish + Video-to-SRT and Video Caption Editor.

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URL](#base-url)
4. [Common Response Format](#common-response-format)
5. [Error Codes](#error-codes)
6. [Video-to-SRT API (Legacy)](#video-to-srt-api-legacy)
7. [WebSocket Streaming API](#websocket-streaming-api)
8. [Python API](#python-api)
9. [Video Caption Editor API (New)](#video-caption-editor-api-new)
10. [Integration Examples](#integration-examples)

---

## Overview

The Whisper-Hindi2Hinglish application provides multiple APIs:
- **Video-to-SRT API**: Simple REST API for converting videos to SRT files
- **WebSocket Streaming API**: Real-time audio streaming and transcription
- **Python API**: Direct Python function calls
- **Video Caption Editor API**: Full-featured REST API for caption editing and embedding

---

## Authentication

Currently, all APIs are open for local development.

**Future Plans:**
- API key authentication
- OAuth2 support
- Rate limiting

---

## Base URL

```
http://localhost:5000
```

---

## Common Response Format

### Success Response
```json
{
  "success": true,
  "data": {
    // Response-specific data
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  }
}
```

---

## Error Codes

| HTTP Code | Error Code | Description |
|-----------|------------|-------------|
| 200 | - | Success |
| 400 | INVALID_REQUEST | Invalid request parameters |
| 400 | BAD_REQUEST | Bad request |
| 404 | NOT_FOUND | Resource not found |
| 404 | SESSION_NOT_FOUND | Session ID not found |
| 410 | SESSION_EXPIRED | Session has expired |
| 413 | FILE_TOO_LARGE | File exceeds size limit (>500MB) |
| 415 | UNSUPPORTED_FORMAT | Unsupported file format |
| 500 | INTERNAL_ERROR | Server error |
| 500 | TRANSCRIPTION_FAILED | Transcription process failed |
| 500 | EMBEDDING_FAILED | Caption embedding failed |

---

## Video-to-SRT API (Legacy)

### POST /upload

Convert video to SRT subtitle file.

**Endpoint:** `http://localhost:5000/upload`

**Method:** `POST`

**Content-Type:** `multipart/form-data`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `video` | File | Yes | Video file to convert |
| `model` | String | No | Model name (default: Swift) |

**Supported Formats:** mp4, avi, mov, mkv, webm, flv, wmv, m4v

**Max File Size:** 500 MB

**Example (curl):**
```bash
curl -X POST http://localhost:5000/upload \
  -F "video=@myvideo.mp4" \
  -F "model=Oriserve/Whisper-Hindi2Hinglish-Swift" \
  -o output.srt
```

**Example (Python):**
```python
import requests

url = "http://localhost:5000/upload"
files = {"video": open("myvideo.mp4", "rb")}
data = {"model": "Oriserve/Whisper-Hindi2Hinglish-Swift"}

response = requests.post(url, files=files, data=data)

if response.status_code == 200:
    with open("output.srt", "wb") as f:
        f.write(response.content)
    print("SRT file saved!")
else:
    print(f"Error: {response.json()['error']}")
```

**Response:**

- **Success (200):** Binary SRT file
- **Error (400):** `{"error": "Error message"}`

### GET /

Web interface for uploading videos.

**Endpoint:** `http://localhost:5000/`

**Returns:** HTML page with upload form

### GET /health

Health check endpoint.

**Endpoint:** `http://localhost:5000/health`

**Response:**
```json
{
  "status": "ok",
  "model": "Oriserve/Whisper-Hindi2Hinglish-Swift"
}
```

---

## WebSocket Streaming API

### Connection

**Endpoint:** `ws://localhost:8000`

**Protocol:** Binary WebSocket

### Message Format

#### Client → Server (Audio Data)

**Format:** Binary audio data

**Requirements:**
- 16-bit linear PCM
- Mono audio
- Sample rate: 8kHz, 16kHz, 32kHz, or 48kHz
- Chunk size: 10ms, 20ms, or 30ms of audio

**Example:**
```python
import websockets
import asyncio

async def stream_audio():
    uri = "ws://localhost:8000"
    async with websockets.connect(uri) as websocket:
        # Read audio file
        with open("audio.wav", "rb") as f:
            audio_data = f.read()

        # Send in chunks (320 bytes = 10ms at 16kHz)
        chunk_size = 320
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i+chunk_size]
            await websocket.send(chunk)
            await asyncio.sleep(0.01)  # 10ms delay

            # Receive transcriptions
            try:
                transcription = await asyncio.wait_for(
                    websocket.recv(),
                    timeout=0.01
                )
                print(f"Transcription: {transcription}")
            except asyncio.TimeoutError:
                pass

asyncio.run(stream_audio())
```

#### Server → Client (Transcriptions)

**Format:** UTF-8 text string

**Returns:** Transcription text when speech is detected and silence follows

---

## Python API

### Video to SRT Function

```python
from video_to_srt import video_to_srt

# Basic usage
srt_path = video_to_srt("input.mp4")
print(f"SRT saved to: {srt_path}")

# Advanced usage
srt_path = video_to_srt(
    video_path="input.mp4",
    output_srt_path="custom_output.srt",
    model_name="Oriserve/Whisper-Hindi2Hinglish-Prime",
    device="cuda",
    dtype="float16"
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `video_path` | str | Required | Path to input video |
| `output_srt_path` | str | Auto | Output SRT path |
| `model_name` | str | Swift | Model to use |
| `device` | str | `cuda` | Device (`cuda`/`cpu`) |
| `dtype` | str | `float16` | Data type |

**Returns:** Path to generated SRT file

---

## Video Caption Editor API (New)

### Session Management

#### POST /api/sessions

Create a new caption editing session.

**Request:**
```json
{
  "video_filename": "my_video.mp4"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "created",
    "video_filename": "my_video.mp4",
    "created_at": "2026-02-11T10:30:00Z",
    "expires_at": "2026-02-12T10:30:00Z"
  }
}
```

#### GET /api/sessions

List all active sessions.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "session_id": "550e8400-e29b-41d4-a716-446655440000",
        "video_filename": "my_video.mp4",
        "status": "editing"
      }
    ],
    "count": 1
  }
}
```

#### GET /api/sessions/{session_id}

Get session details.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "video_filename": "my_video.mp4",
    "status": "editing",
    "caption_style": {
      "preset_name": "reels_standard",
      "font_family": "Roboto Bold",
      "font_size": 36,
      "font_color": "#FFFFFF",
      "position_x": 50,
      "position_y": 80
    }
  }
}
```

#### DELETE /api/sessions/{session_id}

Delete a session.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message": "Session deleted successfully"
  }
}
```

### Caption Operations

#### GET /api/sessions/{session_id}/captions

Get captions for session.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "captions": [
      {
        "index": 1,
        "start": 0.2,
        "end": 1.36,
        "text": "Kal maine kaha tha"
      }
    ],
    "count": 1
  }
}
```

#### PUT /api/sessions/{session_id}/captions

Update captions.

**Request:**
```json
{
  "captions": [
    {
      "index": 1,
      "start": 0.2,
      "end": 1.5,
      "text": "Kal maine kaha tha (edited)"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "updated_count": 1
  }
}
```

#### PUT /api/sessions/{session_id}/style

Update caption style.

**Request:**
```json
{
  "style": {
    "preset_name": "custom",
    "font_family": "Roboto Bold",
    "font_size": 40,
    "font_color": "#FFFF00",
    "position_x": 50,
    "position_y": 85
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message": "Style updated successfully"
  }
}
```

#### GET /api/sessions/{session_id}/preview

Generate preview image with caption overlay.

**Query Parameters:**
- `timestamp` (float, optional): Timestamp in seconds

**Response (200 OK):**
```
Content-Type: image/jpeg

<binary image data>
```

### Video Operations

#### POST /api/editor/upload

Upload video and create session.

**Request:**
```
Content-Type: multipart/form-data

video: <binary file>
model: "prime" | "swift" (optional)
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "video_info": {
      "filename": "my_video.mp4",
      "duration": 120.5,
      "resolution": [1080, 1920],
      "fps": 60
    },
    "captions": [
      {
        "index": 1,
        "start": 0.2,
        "end": 1.36,
        "text": "Kal mainne kaha tha"
      }
    ]
  }
}
```

#### GET /api/sessions/{session_id}/video

Stream original video.

**Response (200 OK):**
```
Content-Type: video/mp4

<binary video data>
```

#### POST /api/sessions/{session_id}/embed

Embed captions and render video.

**Request (Optional):**
```json
{
  "quality": "high" | "medium" | "low"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "render_id": "render-123e4567-e89b-12d3-a456-426614174000",
    "status": "queued",
    "estimated_time": 45
  }
}
```

#### GET /api/sessions/{session_id}/download

Download captioned video.

**Response (200 OK):**
```
Content-Type: video/mp4
Content-Disposition: attachment; filename="my_video_captioned.mp4"

<binary video data>
```

### Resources

#### GET /api/presets

List all style presets.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "presets": [
      {
        "id": "reels_standard",
        "name": "Reels Standard",
        "description": "Optimized for Instagram Reels"
      },
      {
        "id": "shorts_safe",
        "name": "YouTube Shorts Safe",
        "description": "Safe area for YouTube interface"
      },
      {
        "id": "minimal_clean",
        "name": "Minimal Clean",
        "description": "Clean look with background"
      },
      {
        "id": "bold_impact",
        "name": "Bold Impact",
        "description": "High contrast for readability"
      },
      {
        "id": "cinematic",
        "name": "Cinematic",
        "description": "Elegant, professional appearance"
      }
    ],
    "count": 5
  }
}
```

#### GET /api/presets/{preset_name}

Get preset configuration.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "reels_standard",
    "name": "Reels Standard",
    "config": {
      "font_family": "Roboto Bold",
      "font_size": 36,
      "font_color": "#FFFFFF",
      "position_x": 50,
      "position_y": 80,
      "outline_enabled": true,
      "outline_color": "#000000",
      "outline_width": 2
    }
  }
}
```

#### GET /api/fonts

List available fonts.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
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
    ],
    "count": 2
  }
}
```

---

## Integration Examples

### JavaScript/Node.js - Simple Upload

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

async function convertVideoToSRT(videoPath) {
    const form = new FormData();
    form.append('video', fs.createReadStream(videoPath));
    form.append('model', 'Oriserve/Whisper-Hindi2Hinglish-Swift');

    const response = await axios.post(
        'http://localhost:5000/upload',
        form,
        {
            headers: form.getHeaders(),
            responseType: 'arraybuffer'
        }
    );

    fs.writeFileSync('output.srt', response.data);
    console.log('SRT file saved!');
}

convertVideoToSRT('myvideo.mp4');
```

### PHP - Simple Upload

```php
<?php
$url = 'http://localhost:5000/upload';
$video_path = 'myvideo.mp4';

$ch = curl_init();

$postFields = array(
    'video' => new CURLFile($video_path),
    'model' => 'Oriserve/Whisper-Hindi2Hinglish-Swift'
);

curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_POSTFIELDS, $postFields);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);

$response = curl_exec($ch);
curl_close($ch);

file_put_contents('output.srt', $response);
echo "SRT file saved!";
?>
```

### Python - Complete Editor Workflow

```python
import requests
import time

BASE_URL = "http://localhost:5000"

class CaptionEditorClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url

    def upload_video(self, video_path, model="prime"):
        """Upload video and create session"""
        with open(video_path, 'rb') as f:
            files = {'video': f}
            data = {'model': model}
            response = requests.post(
                f"{self.base_url}/api/editor/upload",
                files=files,
                data=data
            )
        return response.json()

    def update_style(self, session_id, style_config):
        """Update caption style"""
        response = requests.put(
            f"{self.base_url}/api/sessions/{session_id}/style",
            json={"style": style_config}
        )
        return response.json()

    def embed_captions(self, session_id, quality="high"):
        """Embed captions into video"""
        response = requests.post(
            f"{self.base_url}/api/sessions/{session_id}/embed",
            json={"quality": quality}
        )
        return response.json()

    def download_video(self, session_id, output_path):
        """Download captioned video"""
        response = requests.get(
            f"{self.base_url}/api/sessions/{session_id}/download",
            stream=True
        )
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True

# Usage
client = CaptionEditorClient()

# Upload video
result = client.upload_video("my_video.mp4", model="prime")
session_id = result["data"]["session_id"]
print(f"Session created: {session_id}")

# Update style
style = {
    "preset_name": "reels_standard",
    "font_size": 40,
    "font_color": "#FFFF00"
}
client.update_style(session_id, style)

# Embed captions
client.embed_captions(session_id, quality="high")
time.sleep(60)  # Wait for embedding

# Download result
client.download_video(session_id, "my_video_captioned.mp4")
print("Captioned video downloaded!")
```

### JavaScript/Fetch - Editor Client

```javascript
const BASE_URL = "http://localhost:5000";

class CaptionEditorClient {
  async uploadVideo(videoFile, model = "prime") {
    const formData = new FormData();
    formData.append("video", videoFile);
    formData.append("model", model);

    const response = await fetch(`${BASE_URL}/api/editor/upload`, {
      method: "POST",
      body: formData,
    });

    return await response.json();
  }

  async updateStyle(sessionId, styleConfig) {
    const response = await fetch(
      `${BASE_URL}/api/sessions/${sessionId}/style`,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ style: styleConfig }),
      }
    );
    return await response.json();
  }

  async embedCaptions(sessionId, quality = "high") {
    const response = await fetch(
      `${BASE_URL}/api/sessions/${sessionId}/embed`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quality }),
      }
    );
    return await response.json();
  }

  async downloadVideo(sessionId) {
    const response = await fetch(
      `${BASE_URL}/api/sessions/${sessionId}/download`
    );
    return await response.blob();
  }
}

// Usage
const client = new CaptionEditorClient();
```

---

## Rate Limiting

Currently, no rate limiting is implemented for local development.

**Future Plans:**
- 100 requests per minute per IP
- 10 concurrent uploads per user
- Queue-based processing for heavy operations

---

## Versioning

The API follows semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

**Current Version:** 2.0.0

---

## Changelog

### v2.0.0 (2026-02-11)
- Added Video Caption Editor API
- Session-based editing
- Caption styling
- Preview generation
- Caption embedding
- Style presets

### v1.0.0 (Initial Release)
- Basic video upload
- SRT generation
- Simple REST API
- WebSocket streaming
- Python API

---

## Support

For API support:
- Email: ai-team@oriserve.com
- GitHub Issues: Report bugs and feature requests
- Documentation: See [README.md](../README.md) and [USER_GUIDE.md](../USER_GUIDE.md)

---

**Last Updated:** 2026-02-11
**API Version:** 2.0.0
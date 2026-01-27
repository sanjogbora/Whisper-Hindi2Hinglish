# API Reference

Complete API documentation for Whisper-Hindi2Hinglish + Video-to-SRT.

---

## Video-to-SRT API

### REST API (Flask)

The web server provides a REST API for video-to-SRT conversion.

#### POST /upload

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

#### GET /

Web interface for uploading videos.

**Endpoint:** `http://localhost:5000/`

**Returns:** HTML page with upload form

#### GET /health

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

## Integration Examples

### JavaScript/Node.js

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

### PHP

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

---

## Error Codes

| HTTP Code | Meaning |
|-----------|---------|
| 200 | Success |
| 400 | Bad request (invalid file, format, etc.) |
| 413 | File too large (>500MB) |
| 500 | Server error (processing failed) |

---

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider:
- Adding authentication
- Implementing rate limits
- Queueing long-running requests

---

[← Back to Documentation Index](README.md)

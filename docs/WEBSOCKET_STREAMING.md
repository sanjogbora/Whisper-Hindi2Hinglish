# WebSocket Streaming Guide

> **Original Feature**: This functionality is from [OriserveAI/Whisper-Hindi2Hinglish](https://github.com/OriserveAI/Whisper-Hindi2Hinglish)

Real-time audio transcription using WebSocket connections.

---

## Overview

The WebSocket streaming system allows you to transcribe audio in real-time by streaming audio chunks to a server that processes them and returns transcriptions immediately.

### Features
- ✅ Real-time transcription (sub-second latency)
- ✅ Voice Activity Detection (VAD) to reduce false transcriptions
- ✅ Supports streaming from files or microphone
- ✅ Concurrent client support
- ✅ Model selection (Swift/Prime)
- ✅ GPU acceleration support

---

## Quick Start

### 1. Start the WebSocket Server

```bash
python websocket_server.py
```

**Server Options:**
```bash
python websocket_server.py \
    --host 0.0.0.0 \
    --port 8000 \
    --model-id Oriserve/Whisper-Hindi2Hinglish-Swift \
    --device cuda \
    --dtype float16
```

| Argument | Default | Description |
|----------|---------|-------------|
| `--host` | `0.0.0.0` | Server host |
| `--port` | `8000` | Server port |
| `--model-id` | Swift model | Model to use |
| `--device` | `cuda` | `cuda` or `cpu` |
| `--dtype` | `float16` | `float16` or `float32` |

### 2. Connect a Client

#### Option A: Stream from Audio File

```bash
python client_file.py --uri ws://localhost:8000 --wav-path audio.wav
```

**Client Options:**
```bash
python client_file.py \
    --uri ws://localhost:8000 \
    --wav-path path/to/audio.wav \
    --chunk-duration 10
```

#### Option B: Stream from Microphone

```bash
python client_mic.py --uri ws://localhost:8000
```

**With Device Selection:**
```bash
python client_mic.py \
    --uri ws://localhost:8000 \
    --device-index 0 \
    --chunk-duration 10
```

---

## Architecture

```
┌─────────────┐          WebSocket          ┌─────────────┐
│   Client    │◄────────────────────────────►│   Server    │
│             │                              │             │
│ • File      │     Binary Audio Chunks      │ • VAD       │
│ • Mic       │─────────────────────────────►│ • Buffer    │
│             │                              │ • Whisper   │
│             │◄─────────────────────────────│ • Transc.   │
└─────────────┘    Text Transcriptions       └─────────────┘
```

### How It Works

1. **Client** reads audio in small chunks (10ms recommended)
2. **Client** sends binary audio data via WebSocket
3. **Server** uses VAD to detect speech presence
4. **Server** buffers audio until silence is detected
5. **Server** transcribes buffered audio using Whisper
6. **Server** sends transcription back to client
7. **Client** displays transcription in real-time

---

## File Streaming

### Basic Usage

```bash
python client_file.py --uri ws://localhost:8000 --wav-path audio.wav
```

### Audio Requirements

**Supported Format:**
- 16-bit linear PCM
- Mono (single channel)
- Sample rates: 8kHz, 16kHz, 32kHz, or 48kHz (16kHz recommended)

**Converting Audio:**
```bash
# Using FFmpeg to convert to correct format
ffmpeg -i input.mp3 -ar 16000 -ac 1 -sample_fmt s16 output.wav
```

### Chunk Duration

The `--chunk-duration` parameter controls how frequently audio is sent:

```bash
# Send audio every 10ms (recommended for real-time)
python client_file.py --wav-path audio.wav --chunk-duration 10

# Send audio every 30ms (lower network usage)
python client_file.py --wav-path audio.wav --chunk-duration 30
```

**Valid chunk durations**: 10, 20, or 30 milliseconds (WebRTC VAD requirement)

---

## Microphone Streaming

### Finding Your Microphone

Run this script to list available audio devices:

```python
import pyaudio

p = pyaudio.PyAudio()

for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f"Device {i}: {info['name']}")
        print(f"  - Channels: {info['maxInputChannels']}")
        print(f"  - Sample Rate: {info['defaultSampleRate']}")
```

### Using Specific Microphone

```bash
# Use device index 0 (usually default mic)
python client_mic.py --device-index 0

# Use device index 2 (external mic)
python client_mic.py --device-index 2
```

### PyAudio Installation

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

---

## Configuration

### Model Selection

**Swift Model** (Default):
- Faster inference
- Lower latency
- Good for real-time applications
```bash
python websocket_server.py --model-id Oriserve/Whisper-Hindi2Hinglish-Swift
```

**Prime Model**:
- Higher accuracy
- Slower inference
- Better for difficult audio
```bash
python websocket_server.py --model-id Oriserve/Whisper-Hindi2Hinglish-Prime
```

### GPU vs CPU

**GPU (Recommended):**
```bash
python websocket_server.py --device cuda --dtype float16
```

**CPU:**
```bash
python websocket_server.py --device cpu --dtype float32
```

---

## Troubleshooting

### Server Won't Start

**Issue**: Port already in use
```
Error: Address already in use
```

**Solution**: Use a different port
```bash
python websocket_server.py --port 8001
```

### No Transcription Output

**Issue**: VAD not detecting speech

**Solutions:**
- Check audio format (must be 16-bit mono PCM)
- Ensure sample rate is 8k/16k/32k/48kHz
- Increase microphone volume
- Reduce background noise

### Poor Transcription Quality

**Solutions:**
- Use Prime model instead of Swift
- Reduce background noise
- Use external microphone
- Ensure clear speech with minimal overlapping speakers

### Connection Drops

**Issue**: WebSocket connection keeps disconnecting

**Solutions:**
- Check network stability
- Reduce chunk duration (less data per send)
- Ensure server has sufficient resources
- Check firewall settings

### Import Error: pyaudio

**Error:**
```
ModuleNotFoundError: No module named 'pyaudio'
```

**Solution:** See [PyAudio Installation](#pyaudio-installation) above

---

## Advanced Usage

### Custom Server Script

```python
import asyncio
import websockets

async def custom_handler(websocket, path):
    # Your custom logic here
    async for message in websocket:
        # Process audio chunks
        pass

async def main():
    async with websockets.serve(custom_handler, "0.0.0.0", 8000):
        await asyncio.Future()  # run forever

asyncio.run(main())
```

### Integrating with Other Applications

The WebSocket protocol allows integration from any programming language:

**JavaScript Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000');

ws.onopen = () => {
    // Send binary audio data
    ws.send(audioBuffer);
};

ws.onmessage = (event) => {
    console.log('Transcription:', event.data);
};
```

**Python Example:**
```python
import websockets
import asyncio

async def transcribe():
    uri = "ws://localhost:8000"
    async with websockets.connect(uri) as websocket:
        # Send audio
        await websocket.send(audio_bytes)
        # Receive transcription
        transcription = await websocket.recv()
        print(transcription)

asyncio.run(transcribe())
```

---

## Performance Tips

1. **Use GPU**: 10-20x faster than CPU
2. **Choose Swift model**: For real-time applications
3. **Optimize chunk duration**: 10-20ms for best balance
4. **Reduce model precision**: float16 on GPU (2x faster)
5. **Batch processing**: For multiple files, use video-to-SRT instead

---

## Next Steps

- **Batch Processing**: See [Video-to-SRT Guide](VIDEO_TO_SRT.md)
- **API Integration**: See [API Reference](API_REFERENCE.md)
- **Troubleshooting**: See [FAQ](FAQ.md)

---

[← Back to Documentation Index](README.md)

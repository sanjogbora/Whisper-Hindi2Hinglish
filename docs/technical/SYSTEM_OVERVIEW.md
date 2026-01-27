# System Overview

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     VIDEO TO SRT SYSTEM                      │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐
│   Your Video │  (Hindi-English mixed speech)
│   (MP4/AVI)  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│                    INPUT OPTIONS                              │
├──────────────────────────────────────────────────────────────┤
│  1. Web Interface (http://localhost:5000)                    │
│     - Drag & drop upload                                      │
│     - Model selection                                         │
│     - Automatic download                                      │
│                                                               │
│  2. Command Line                                              │
│     - python video_to_srt.py video.mp4                       │
│                                                               │
│  3. REST API                                                  │
│     - POST /upload with video file                           │
│     - Returns SRT file                                        │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                  PROCESSING PIPELINE                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Step 1: Audio Extraction (FFmpeg)                           │
│  ┌─────────────────────────────────────────┐                │
│  │ Video → Audio (16kHz, Mono, PCM)        │                │
│  └─────────────────────────────────────────┘                │
│                       │                                       │
│                       ▼                                       │
│  Step 2: Speech Recognition (Whisper-Hindi2Hinglish)        │
│  ┌─────────────────────────────────────────┐                │
│  │ Audio → Text with Timestamps            │                │
│  │ Model: Swift (fast) or Prime (accurate) │                │
│  │ Output: Hinglish (Roman script)         │                │
│  └─────────────────────────────────────────┘                │
│                       │                                       │
│                       ▼                                       │
│  Step 3: SRT Generation                                      │
│  ┌─────────────────────────────────────────┐                │
│  │ Format timestamps → SRT file            │                │
│  │ Sequence numbers, time codes, text      │                │
│  └─────────────────────────────────────────┘                │
│                                                               │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                      OUTPUT                                   │
├──────────────────────────────────────────────────────────────┤
│  SRT Subtitle File                                           │
│  ┌────────────────────────────────────────┐                 │
│  │ 1                                       │                 │
│  │ 00:00:00,000 --> 00:00:03,500          │                 │
│  │ Namaste dosto, aaj hum baat karenge... │                 │
│  │                                         │                 │
│  │ 2                                       │                 │
│  │ 00:00:03,500 --> 00:00:07,200          │                 │
│  │ AI ke baare mein discuss karte hain... │                 │
│  └────────────────────────────────────────┘                 │
└──────────────────────────────────────────────────────────────┘
```

## Components

### 1. Frontend (Web Interface)
**File**: `templates/upload.html`
- Beautiful drag-and-drop interface
- Model selection (Swift/Prime)
- Progress tracking
- Automatic download

### 2. API Server
**File**: `api_server.py`
- Flask web server
- Handles file uploads
- Manages processing pipeline
- Serves web interface and API endpoints

### 3. Video Processing
**File**: `video_to_srt.py`
- Audio extraction using FFmpeg
- Transcription with Whisper model
- SRT file generation
- Can be used standalone or via API

### 4. AI Model
**Models**: 
- `Oriserve/Whisper-Hindi2Hinglish-Swift` (default)
- `Oriserve/Whisper-Hindi2Hinglish-Prime` (better quality)

**Capabilities**:
- Hindi-English mixed speech recognition
- Outputs Roman English (Hinglish)
- Handles Indian accents
- Noise resistant
- Timestamp generation

### 5. Utilities
**Files**: `utils.py`, `logger.py`
- Audio preprocessing
- Model loading
- Logging

## Data Flow

```
User Upload → Temp Storage → Audio Extraction → AI Model → SRT Generation → Download → Cleanup
```

### Detailed Flow:

1. **Upload** (Web/API/CLI)
   - Video file received
   - Saved to temporary location
   - Validated (format, size)

2. **Audio Extraction**
   - FFmpeg extracts audio track
   - Converts to 16kHz mono PCM
   - Temporary WAV file created

3. **Transcription**
   - Whisper model loads (if not already loaded)
   - Audio processed in chunks (30s)
   - Text + timestamps generated
   - Output in Hinglish

4. **SRT Generation**
   - Timestamps formatted (HH:MM:SS,mmm)
   - Sequence numbers added
   - Text cleaned and formatted
   - SRT file created

5. **Delivery**
   - SRT file sent to user
   - Temporary files cleaned up
   - Ready for next request

## Performance

### Processing Time (Approximate)

| Video Length | GPU (CUDA) | CPU |
|--------------|------------|-----|
| 1 minute     | 6-12 sec   | 30-60 sec |
| 5 minutes    | 30-60 sec  | 2.5-5 min |
| 10 minutes   | 1-2 min    | 5-10 min |
| 30 minutes   | 3-6 min    | 15-30 min |

**Factors affecting speed**:
- Model choice (Swift vs Prime)
- Hardware (GPU vs CPU)
- Audio quality
- Speech density

### Resource Usage

**GPU Mode**:
- VRAM: ~2-4 GB
- RAM: ~4-6 GB
- CPU: Low usage

**CPU Mode**:
- RAM: ~4-8 GB
- CPU: High usage (all cores)

## File Structure

```
Whisper-Hindi2Hinglish/
├── api_server.py              # Flask API server
├── video_to_srt.py            # Core conversion logic
├── app.py                     # WebSocket streaming server
├── client_file.py             # File streaming client
├── client_mic.py              # Microphone streaming client
├── utils.py                   # Utility functions
├── logger.py                  # Logging configuration
├── requirements.txt           # Python dependencies
├── start_server.bat           # Windows quick start
├── test_video_to_srt.py       # System check script
├── example_api_usage.py       # API usage examples
│
├── templates/
│   └── upload.html            # Web interface
│
├── examples/                  # Example audio files
│   └── *.wav
│
└── Documentation/
    ├── README.md              # Main documentation
    ├── QUICK_START.md         # Quick start guide
    ├── VIDEO_TO_SRT_GUIDE.md  # Complete guide
    ├── SETUP_CHECKLIST.md     # Setup checklist
    └── SYSTEM_OVERVIEW.md     # This file
```

## API Endpoints

### GET /
- Returns: Web interface (HTML)
- Use: Browser access

### GET /api
- Returns: API documentation (JSON)
- Use: API reference

### GET /health
- Returns: Server status (JSON)
- Use: Health checks

### POST /upload
- Accepts: multipart/form-data
  - `video`: Video file
  - `model`: "swift" or "prime"
- Returns: SRT file (text/plain)
- Use: Video to SRT conversion

## Security Considerations

1. **File Size Limit**: 500MB default (configurable)
2. **File Type Validation**: Only allowed video formats
3. **Temporary Storage**: Files cleaned up after processing
4. **No Persistence**: Videos not stored permanently
5. **Local Deployment**: Runs on localhost by default

## Scalability

### Single User
- Current setup works great
- No modifications needed

### Multiple Users
Consider:
- Queue system for requests
- Multiple worker processes
- Load balancer
- Persistent storage for results
- Authentication

### Production Deployment
Recommendations:
- Use Gunicorn/uWSGI
- Add Redis for queue management
- Implement rate limiting
- Add monitoring (Prometheus/Grafana)
- Use cloud storage (S3/GCS)
- Add CDN for static files

## Customization

### Change Model
```python
# In api_server.py or video_to_srt.py
model_id = "Oriserve/Whisper-Hindi2Hinglish-Prime"
```

### Change Port
```bash
python api_server.py --port 8080
```

### Adjust File Size Limit
```python
# In api_server.py
MAX_FILE_SIZE = 1000 * 1024 * 1024  # 1GB
```

### Use CPU Instead of GPU
```bash
python api_server.py --device cpu
```

## Troubleshooting

### Common Issues

1. **FFmpeg not found**
   - Install FFmpeg
   - Add to PATH
   - Restart terminal

2. **CUDA out of memory**
   - Use CPU mode
   - Close other GPU apps
   - Use Swift model

3. **Poor quality**
   - Use Prime model
   - Check audio quality
   - Reduce background noise

4. **Slow processing**
   - Use GPU if available
   - Use Swift model
   - Reduce video length

## Future Enhancements

Potential improvements:
- [ ] Support for more languages
- [ ] Real-time streaming transcription
- [ ] Speaker diarization (who said what)
- [ ] Automatic punctuation
- [ ] Translation to other languages
- [ ] Video preview with subtitles
- [ ] Batch processing UI
- [ ] Cloud deployment option

---

**For more information, see the other documentation files!**

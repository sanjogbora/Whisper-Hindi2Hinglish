# Video to SRT Converter Guide

Convert Hindi-English mixed videos to Roman English SRT subtitle files.

## 🚀 Quick Start

### Prerequisites

1. **Install FFmpeg** (required for video processing):
   - Windows: Download from https://ffmpeg.org/download.html
   - Or use: `winget install ffmpeg`
   - Verify: `ffmpeg -version`

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Option 1: Web Interface (Easiest)

1. **Start the server**:
   ```bash
   python api_server.py
   ```

2. **Open browser**:
   - Go to: http://localhost:5000
   - Upload your video
   - Select model quality (Swift or Prime)
   - Click "Generate SRT File"
   - Download will start automatically

### Option 2: Command Line

```bash
python video_to_srt.py your_video.mp4
```

This will create `your_video.srt` in the same directory.

**Custom output path**:
```bash
python video_to_srt.py your_video.mp4 --output subtitles.srt
```

**Use Prime model (better quality)**:
```bash
python video_to_srt.py your_video.mp4 --model-id Oriserve/Whisper-Hindi2Hinglish-Prime
```

### Option 3: API Endpoint

**Upload via curl**:
```bash
curl -X POST -F "video=@your_video.mp4" -F "model=swift" \
  http://localhost:5000/upload -o output.srt
```

**Upload via Python**:
```python
import requests

with open('your_video.mp4', 'rb') as f:
    files = {'video': f}
    data = {'model': 'swift'}  # or 'prime'
    response = requests.post('http://localhost:5000/upload', files=files, data=data)
    
    with open('output.srt', 'wb') as out:
        out.write(response.content)
```

## 📋 Features

- ✅ Supports multiple video formats (MP4, AVI, MOV, MKV, WEBM, FLV, WMV, M4V)
- ✅ Automatic audio extraction from video
- ✅ Hindi-English mixed speech recognition
- ✅ Output in Roman English (Hinglish) script
- ✅ Properly timed and synced subtitles
- ✅ Two model options (Swift for speed, Prime for quality)
- ✅ Web interface with drag-and-drop
- ✅ REST API for integration

## 🎯 How It Works

1. **Video Upload**: You upload a video file
2. **Audio Extraction**: FFmpeg extracts audio (16kHz, mono, PCM)
3. **Transcription**: Whisper-Hindi2Hinglish model transcribes with timestamps
4. **SRT Generation**: Creates properly formatted SRT file
5. **Download**: You get the SRT file

## 🔧 Configuration

### Server Options

```bash
python api_server.py \
  --host 0.0.0.0 \
  --port 5000 \
  --model-id Oriserve/Whisper-Hindi2Hinglish-Swift \
  --device cuda \
  --dtype float16
```

**Parameters**:
- `--host`: Server host (default: 0.0.0.0)
- `--port`: Server port (default: 5000)
- `--model-id`: Model to use (Swift or Prime)
- `--device`: cuda or cpu
- `--dtype`: float16 or float32

### Command Line Options

```bash
python video_to_srt.py VIDEO_PATH \
  --output OUTPUT.srt \
  --model-id Oriserve/Whisper-Hindi2Hinglish-Prime \
  --device cuda \
  --dtype float16
```

## 📊 Model Comparison

| Model | Speed | Quality | Use Case |
|-------|-------|---------|----------|
| **Swift** | Fast | Good | Quick transcriptions, real-time needs |
| **Prime** | Slower | Best | High accuracy requirements, final production |

## 🎬 Example SRT Output

```srt
1
00:00:00,000 --> 00:00:03,500
Namaste dosto, aaj hum baat karenge AI ke baare mein.

2
00:00:03,500 --> 00:00:07,200
Artificial Intelligence bahut important hai aajkal.

3
00:00:07,200 --> 00:00:11,800
Isse humari life mein bahut saare changes aa rahe hain.
```

## 🔍 Troubleshooting

### FFmpeg not found
```
Error: ffmpeg not found
```
**Solution**: Install FFmpeg and add to PATH

### CUDA out of memory
```
Error: CUDA out of memory
```
**Solution**: Use CPU or reduce batch size:
```bash
python api_server.py --device cpu
```

### File too large
```
Error: File exceeds maximum size
```
**Solution**: Edit `MAX_FILE_SIZE` in `api_server.py` or compress video first

### Poor transcription quality
**Solutions**:
- Use Prime model instead of Swift
- Ensure audio is clear with minimal background noise
- Check that speech is primarily Hindi-English mix

## 🌐 API Endpoints

### GET /
Web interface for uploading videos

### GET /api
API documentation (JSON)

### GET /health
Health check endpoint

### POST /upload
Upload video and get SRT file

**Request**:
- Method: POST
- Content-Type: multipart/form-data
- Body:
  - `video`: Video file (required)
  - `model`: "swift" or "prime" (optional, default: swift)

**Response**:
- Content-Type: text/plain
- Body: SRT file content
- Headers: Content-Disposition with filename

## 💡 Tips

1. **Better Results**:
   - Use videos with clear audio
   - Minimize background noise
   - Ensure speakers face the camera/mic

2. **Performance**:
   - GPU (CUDA) is 10-20x faster than CPU
   - Swift model is 2-3x faster than Prime
   - Processing time ≈ 10-20% of video duration (GPU)

3. **Integration**:
   - Use the API for batch processing
   - Integrate with video editing workflows
   - Automate subtitle generation pipelines

## 📝 License

Same as the main Whisper-Hindi2Hinglish project.

## 🤝 Support

For issues or questions:
- Check existing issues in the repository
- Contact: ai-team@oriserve.com

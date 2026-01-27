# Attribution

## Fork Information

This repository is a **fork** of [Whisper-Hindi2Hinglish](https://github.com/OriserveAI/Whisper-Hindi2Hinglish) by OriserveAI.

- **Original Repository**: https://github.com/OriserveAI/Whisper-Hindi2Hinglish
- **Original Authors**: OriserveAI (ai-team@oriserve.com)
- **License**: Apache License 2.0
- **Fork Maintainer**: Sanjog Bora ([@sanjogbora](https://github.com/sanjogbora))

---

## Original Work (OriserveAI)

The following components are from the original OriserveAI repository:

### Core Streaming Functionality
- **`app.py`** (renamed to `websocket_server.py`) - WebSocket server for real-time transcription
- **`client_file.py`** - Client for streaming audio from files
- **`client_mic.py`** - Client for streaming audio from microphone
- **`utils.py`** - Audio preprocessing and model loading utilities
- **`logger.py`** - Logging configuration
- **`examples/`** - Sample WAV audio files

### Models
- **Whisper-Hindi2Hinglish-Prime** - High-accuracy model
- **Whisper-Hindi2Hinglish-Swift** - Fast inference model
- Training methodology and fine-tuning approach
- VAD implementation for noise handling

### Key Innovations (OriserveAI)
- **Hinglish transcription** (Hindi in Roman script) instead of Devanagari
- **Noise-resistant models** trained on 550+ hours of noisy Indian-accented audio
- **Hallucination mitigation** techniques
- **Real-time streaming** architecture with WebSocket
- **WebRTC VAD integration** for speech detection

---

## Fork Additions (Sanjog Bora)

The following features were added in this fork:

### Video-to-SRT Conversion System
- **`api_server.py`** (renamed to `web_server.py`) - Flask web server with REST API
- **`video_to_srt.py`** - Complete video-to-SRT conversion pipeline
- **`templates/upload.html`** - Modern web UI with drag-and-drop upload
- **Word-level timestamp generation** using `whisper-timestamped`
- **Smart subtitle grouping** (max 42 characters per line, Netflix standard)
- **Multi-format video support** (mp4, avi, mov, mkv, webm, flv, wmv, m4v)

### Testing
- **`test_video_to_srt.py`** - Video conversion tests
- **`test_grouping.py`** - Subtitle grouping logic tests
- **`test_vad_splitting.py`** - VAD splitting tests

### Documentation (Fork-specific)
- **`QUICK_START.md`** - Quick start guide for video-to-SRT
- **`VIDEO_TO_SRT_GUIDE.md`** - Comprehensive video conversion guide
- **`SETUP_CHECKLIST.md`** - Step-by-step setup checklist
- Various technical documentation about implementation

### Infrastructure
- **Docker support** - Dockerfile and docker-compose.yml
- **Python packaging** - setup.py for pip installation
- **GitHub Actions** - CI/CD workflows
- **Quick start scripts** - Automated setup helpers

---

## Feature Comparison

| Feature | Original (OriserveAI) | Fork Addition (Sanjog Bora) |
|---------|----------------------|----------------------------|
| Real-time streaming | ✅ | - |
| WebSocket server | ✅ | - |
| Microphone input | ✅ | - |
| File streaming | ✅ | - |
| Video-to-SRT conversion | - | ✅ |
| Web UI | - | ✅ |
| REST API | - | ✅ |
| Command-line interface | - | ✅ |
| Word-level timestamps | - | ✅ |
| Subtitle grouping | - | ✅ |
| Docker support | - | ✅ |
| Pip installable | - | ✅ |

---

## Contributions

### To This Fork
For issues or improvements related to video-to-SRT functionality, please:
- Open issues on: https://github.com/sanjogbora/Whisper-Hindi2Hinglish/issues
- Submit pull requests to this repository

### To Upstream (OriserveAI)
For issues or improvements related to the core streaming functionality or models, please:
- Open issues on: https://github.com/OriserveAI/Whisper-Hindi2Hinglish/issues
- Contact: ai-team@oriserve.com

---

## Credits

### OriserveAI Team
Thank you to the OriserveAI team for:
- Creating the excellent Whisper-Hindi2Hinglish models
- Solving the challenging problem of Indian-accented speech recognition
- Open-sourcing their work under Apache 2.0 license
- Building the robust streaming architecture
- Training on 550+ hours of real-world Indian audio

### Open Source Dependencies
Both the original and fork rely on:
- **OpenAI Whisper** - Base model architecture
- **HuggingFace Transformers** - Model loading and inference
- **whisper-timestamped** - Word-level timestamp alignment
- **WebRTC VAD** - Voice activity detection
- **FFmpeg** - Audio/video processing

---

## License

Both the original work and fork additions are licensed under the **Apache License 2.0**.

See the [LICENSE](LICENSE) file for the full license text.
See the [NOTICE](NOTICE) file for copyright notices and attributions.

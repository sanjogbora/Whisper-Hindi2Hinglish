# Changelog

All notable changes to this fork will be documented in this file.

## [Fork v1.0.0] - 2026-01-27

### Added (Fork Contributions by Sanjog Bora)

#### Video-to-SRT Conversion System
- Complete video-to-SRT conversion pipeline with word-level timestamps
- Flask web server with beautiful Bootstrap/Tailwind UI
- REST API for video upload and processing
- Command-line interface for batch video processing
- Web interface with drag-and-drop file upload
- Support for 8 video formats (mp4, avi, mov, mkv, webm, flv, wmv, m4v)
- Smart subtitle grouping (max 42 characters per line, Netflix standard)
- Automatic subtitle timing with proper gaps
- Word-level timestamp generation using `whisper-timestamped`
- Model selection (Swift vs Prime) in web UI

#### Documentation
- QUICK_START.md - Quick start guide for video-to-SRT
- VIDEO_TO_SRT_GUIDE.md - Comprehensive video conversion guide
- SETUP_CHECKLIST.md - Step-by-step setup checklist
- WORD_LEVEL_TIMESTAMPS_FIX.md - Technical implementation details
- VAD_IMPLEMENTATION_SUMMARY.md - VAD system documentation
- SYSTEM_OVERVIEW.md - Architecture overview

#### Testing
- test_video_to_srt.py - Video conversion pipeline tests
- test_grouping.py - Subtitle grouping logic tests
- test_vad_splitting.py - VAD splitting tests

#### Infrastructure
- Docker support (Dockerfile, docker-compose.yml, .dockerignore)
- Python packaging (setup.py) for pip installation
- GitHub Actions CI/CD workflows
- Comprehensive .gitignore
- Quick start automation scripts

### From Upstream (OriserveAI)

The following features are from the original [OriserveAI/Whisper-Hindi2Hinglish](https://github.com/OriserveAI/Whisper-Hindi2Hinglish) repository:

#### Core Streaming Functionality
- WebSocket streaming server for real-time transcription
- File-based streaming client (client_file.py)
- Microphone streaming client (client_mic.py)
- Audio preprocessing utilities
- Logging configuration
- Sample audio files in examples/

#### Models
- Whisper-Hindi2Hinglish-Prime (high accuracy)
- Whisper-Hindi2Hinglish-Swift (fast inference)
- Training on 550+ hours of noisy Indian-accented audio
- Hinglish transcription (Roman script instead of Devanagari)
- Hallucination mitigation techniques
- WebRTC VAD for noise handling

---

## Contributing

### For Video-to-SRT Features
Submit issues and PRs to: https://github.com/sanjogbora/Whisper-Hindi2Hinglish

### For Core Streaming Features
Submit to upstream: https://github.com/OriserveAI/Whisper-Hindi2Hinglish

---

## License

Apache License 2.0 - See [LICENSE](LICENSE) and [NOTICE](NOTICE) for details.

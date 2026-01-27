# Documentation Index

Welcome to the Whisper-Hindi2Hinglish + Video-to-SRT documentation!

## Quick Navigation

### Getting Started
- **[Installation Guide](INSTALLATION.md)** - Complete setup instructions for CPU and GPU
- **[Quick Start](QUICK_START.md)** - Get up and running in 3 steps

### Features

#### Video-to-SRT Conversion (Fork Addition)
- **[Video-to-SRT Guide](VIDEO_TO_SRT.md)** - Complete guide to video subtitle generation
- **[Web Interface](VIDEO_TO_SRT.md#web-interface)** - Using the browser-based UI
- **[Command Line](VIDEO_TO_SRT.md#command-line)** - CLI usage for batch processing
- **[API Usage](API_REFERENCE.md#video-to-srt-api)** - REST API integration

#### Real-time Streaming (Original OriserveAI Feature)
- **[WebSocket Streaming Guide](WEBSOCKET_STREAMING.md)** - Real-time transcription
- **[File Streaming](WEBSOCKET_STREAMING.md#file-streaming)** - Stream from audio files
- **[Microphone Streaming](WEBSOCKET_STREAMING.md#microphone-streaming)** - Live mic transcription

### Reference
- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[FAQ](FAQ.md)** - Frequently asked questions and troubleshooting

### Technical Documentation
- **[System Overview](technical/SYSTEM_OVERVIEW.md)** - Architecture and design
- **[VAD Implementation](technical/VAD_IMPLEMENTATION_SUMMARY.md)** - Voice activity detection
- **[Word Timestamps](technical/WORD_LEVEL_TIMESTAMPS_FIX.md)** - Timestamp generation

---

## Quick Start by Use Case

### "I want to add subtitles to my Hindi/Hinglish videos"
1. Read [Installation Guide](INSTALLATION.md)
2. Follow [Video-to-SRT Guide](VIDEO_TO_SRT.md)
3. Use the web interface: `python web_server.py`

### "I want real-time transcription from my microphone"
1. Read [Installation Guide](INSTALLATION.md)
2. Follow [WebSocket Streaming Guide](WEBSOCKET_STREAMING.md)
3. Start server: `python websocket_server.py`
4. Run client: `python client_mic.py`

### "I want to integrate this into my application"
1. Read [API Reference](API_REFERENCE.md)
2. See [Integration Examples](API_REFERENCE.md#examples)
3. Check [FAQ](FAQ.md) for common issues

---

## Model Information

This project uses Whisper-Hindi2Hinglish models from OriserveAI:

| Model | Speed | Accuracy | Use Case |
|-------|-------|----------|----------|
| **Swift** | Fast | Good | Real-time, quick processing |
| **Prime** | Slower | Excellent | High-quality transcription |

- **Swift**: `Oriserve/Whisper-Hindi2Hinglish-Swift`
- **Prime**: `Oriserve/Whisper-Hindi2Hinglish-Prime`

---

## Need Help?

- **Issues with setup?** → [FAQ](FAQ.md) or [Installation Guide](INSTALLATION.md)
- **Feature requests?** → [GitHub Issues](https://github.com/sanjogbora/Whisper-Hindi2Hinglish/issues)
- **Questions about original features?** → [OriserveAI Repository](https://github.com/OriserveAI/Whisper-Hindi2Hinglish)

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.

## License

Apache License 2.0 - See [LICENSE](../LICENSE) and [ATTRIBUTION](../ATTRIBUTION.md)

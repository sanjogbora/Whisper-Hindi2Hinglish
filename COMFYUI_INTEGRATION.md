# ComfyUI Integration for Whisper Hindi2Hinglish

This document describes the ComfyUI custom node integration for the Whisper Hindi2Hinglish caption generation system.

## Overview

A ComfyUI custom node package has been created to integrate the Whisper Hindi2Hinglish model into ComfyUI workflows. This enables seamless content creation pipelines where audio can be transcribed to subtitles within ComfyUI.

## Installation Location

```
~/comfy/ComfyUI/custom_nodes/comfyui-whisper-hindi2hinglish/
```

## Features

### Available Nodes

1. **WhisperHindi2Hinglish** - Generate SRT subtitles from audio
   - Supports Prime and Swift models
   - CUDA and CPU device selection
   - Configurable subtitle parameters
   - Word-level timestamps

2. **QwenTTS** - Text-to-speech generation (placeholder)
   - Awaiting Qwen-TTS integration
   - Will enable complete Text → Audio → Subtitles pipeline

3. **LoadAudioFromFile** - Load audio files for processing
   - Supports MP3, WAV, and other audio formats
   - Automatic resampling to 16kHz
   - Mono conversion

4. **SaveSRTToFile** - Save generated SRT files
   - Configurable output directory
   - Custom filename support

## Installation

### Quick Install

```bash
cd ~/comfy/ComfyUI/custom_nodes/comfyui-whisper-hindi2hinglish
bash install.sh
```

### Manual Install

```bash
cd ~/comfy/ComfyUI/custom_nodes/comfyui-whisper-hindi2hinglish
pip install -r requirements.txt
mkdir -p /home/ishanp/Videos/ComfyUI_Output
```

### Restart ComfyUI

```bash
cd ~/comfy/ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

## Workflow

### Current: Audio → Subtitles

```
LoadAudioFromFile → WhisperHindi2Hinglish → SaveSRTToFile
```

### Future: Text → Audio → Subtitles

```
TextInput → QwenTTS → WhisperHindi2Hinglish → SRT
```

## Example Usage

### Workflow Configuration

1. **Load Audio**
   - Node: `LoadAudioFromFile`
   - Parameter: `audio_path = "/path/to/audio.mp3"`

2. **Generate Subtitles**
   - Node: `WhisperHindi2Hinglish`
   - Parameters:
     - `model = "Oriserve/Whisper-Hindi2Hinglish-Prime"`
     - `device = "cuda"`
     - `output_dir = "/home/ishanp/Videos/ComfyUI_Output"`
     - `max_words = 4`
     - `max_chars = 42`

3. **Save SRT**
   - Node: `SaveSRTToFile`
   - Parameters:
     - `filename = "subtitles.srt"`
     - `output_dir = "/home/ishanp/Videos/ComfyUI_Output"`

### Output Files

```
/home/ishanp/Videos/ComfyUI_Output/
├── generated_subtitles.srt
└── subtitles.srt
```

## Model Selection

### Prime Model
- **Best for**: Production content, high accuracy requirements
- **Speed**: ~10-20x real-time (CUDA)
- **Accuracy**: ~95% on clear speech
- **Memory**: ~6GB VRAM

### Swift Model
- **Best for**: Quick previews, iterative work
- **Speed**: ~20-30x real-time (CUDA)
- **Accuracy**: ~90% on clear speech
- **Memory**: ~4GB VRAM

## Configuration

### Output Directory

Default: `/home/ishanp/Videos/ComfyUI_Output`

Change in node parameters as needed.

### Device Selection

- **CUDA**: GPU acceleration (requires NVIDIA GPU)
- **CPU**: Fallback processing

### Subtitle Parameters

- `max_words`: Words per subtitle (3-5 recommended)
- `max_chars`: Characters per subtitle (35-45 recommended)

## Content Creation Pipeline

### Complete Pipeline (Future with Qwen-TTS)

```
1. Text Input
   ↓
2. QwenTTS (Text → Audio)
   ↓
3. WhisperHindi2Hinglish (Audio → SRT)
   ↓
4. SaveSRTToFile
   ↓
5. Import to Video Editor
   ↓
6. Final Video with Captions
```

### Current Pipeline (Audio → Subtitles)

```
1. LoadAudioFromFile
   ↓
2. WhisperHindi2Hinglish (Generate Subtitles)
   ↓
3. SaveSRTToFile
   ↓
4. Import SRT to Video Editor
   ↓
5. Final Video with Captions
```

## Use Cases

### Social Media Content
- Instagram Reels
- TikTok videos
- YouTube Shorts
- Facebook Reels

### Educational Content
- Online courses
- Tutorials
- Explainer videos

### Video Production
- Content localization
- Accessibility features
- Multi-language support

## Integration with Main Repository

This ComfyUI integration uses the same core functionality as the main Whisper Hindi2Hinglish repository:

- **Model**: `Oriserve/Whisper-Hindi2Hinglish-Prime`
- **Library**: `whisper-timestamped`
- **SRT Generation**: Same algorithm as `caption_generator.py`

### Key Differences

- ComfyUI integration provides a visual workflow interface
- Uses ComfyUI's audio format instead of direct file paths
- Can be combined with other ComfyUI nodes for complex pipelines

## Documentation

- **README.md**: Main documentation
- **PIPELINE_GUIDE.md**: Content creation pipeline guide
- **workflow_example.json**: Example workflow JSON
- **INSTALLATION_SUMMARY.md**: Installation guide

## Dependencies

```txt
torch>=2.0.0
whisper-timestamped>=1.15.0
librosa>=0.10.0
soundfile>=0.12.0
transformers>=5.0.0
numpy>=1.24.0
pillow>=10.0.0
```

## Troubleshooting

### Node not appearing
1. Restart ComfyUI
2. Verify dependencies installed
3. Check `__init__.py` has correct mappings

### CUDA out of memory
1. Switch to CPU device
2. Use Swift model
3. Process shorter audio segments

### Poor subtitle quality
1. Use Prime model
2. Improve audio quality
3. Reduce background noise

## Future Enhancements

### Qwen-TTS Integration
- Text-to-speech generation
- Voice customization
- Complete Text → Audio → Subtitles pipeline

### Additional Features
- Batch processing
- Multiple language support
- Advanced subtitle styling
- Video output generation

## Support

For issues and questions:
- ComfyUI Custom Node: See `~/comfy/ComfyUI/custom_nodes/comfyui-whisper-hindi2hinglish/README.md`
- Main Repository: https://github.com/OriserveAI/Whisper-Hindi2Hinglish

## License

MIT License - See `~/comfy/ComfyUI/custom_nodes/comfyui-whisper-hindi2hinglish/LICENSE`
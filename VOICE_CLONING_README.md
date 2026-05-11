# Voice Cloning Pipeline

Clone your voice using Qwen3 TTS in ComfyUI and generate audio based on subtitle files.

## Overview

This pipeline:
1. Parses SRT subtitle files and extracts natural speech segments
2. Uses ComfyUI's Qwen3 TTS to clone voice from a reference audio sample
3. Generates voice-cloned audio for each segment
4. Adjusts timing to match original subtitle durations
5. Stitches segments together with proper gaps
6. Embeds the new audio into the original video

## Prerequisites

- ComfyUI installed at `/home/ishanp/Documents/GitHub/ComfyUI/`
- ComfyUI-Qwen-TTS custom node installed
- Qwen3 TTS models downloaded (0.6B Base recommended for speed)
- CUDA-capable GPU (optional but recommended)
- FFmpeg installed

## File Structure

```
Whisper-Hindi2Hinglish/
├── voice_cloning_pipeline.py      # Main pipeline script
├── embed_audio.py                 # Audio embedding script
├── run_voice_cloning.sh           # Quick start script
├── start_comfyui.sh               # ComfyUI launcher
├── voice_cloning_requirements.txt # Additional dependencies
├── The_Archetypical_Mind.srt      # Input subtitles
├── voice_cloned_segments/         # Generated segment audio (created)
├── The_Archetypical_Mind_VoiceCloned.wav  # Combined audio (created)
└── The_Archetypical_Mind_VoiceCloned.mp4  # Final video (created)
```

## Quick Start

```bash
./run_voice_cloning.sh
```

This will:
1. Activate the conda environment
2. Install additional dependencies
3. Start ComfyUI server
4. Run the voice cloning pipeline
5. Ask if you want to embed audio into video

## Manual Execution

### Step 1: Start ComfyUI

```bash
./start_comfyui.sh
```

Or manually:
```bash
cd /home/ishanp/Documents/GitHub/ComfyUI
python main.py --listen 127.0.0.1 --port 8188
```

### Step 2: Install Dependencies

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate whisper-hindi
pip install -r voice_cloning_requirements.txt
```

### Step 3: Run Pipeline

```bash
python voice_cloning_pipeline.py
```

### Step 4: Embed Audio (Optional)

```bash
python embed_audio.py
```

## Configuration

Edit the `main()` function in `voice_cloning_pipeline.py`:

```python
srt_path = "/path/to/your/subtitles.srt"
ref_audio_path = "/path/to/your/voice_sample.wav"
output_dir = "/path/to/output/segments"
final_output = "/path/to/output/audio.wav"
```

## Segment Analysis

The pipeline automatically groups subtitles into natural speech segments based on gaps.

**Default settings:**
- Gap threshold: 0.3 seconds
- Groups subtitles with gaps < 0.3s into single segments

**Example output for The_Archetypical_Mind.srt:**
- 309 subtitles → 20 segments
- Segment duration: 2.54s - 53.86s (avg: 20s)
- Average 15.45 subtitles per segment

## Audio Processing

### Duration Adjustment

Generated audio is adjusted to match target duration:

- **If shorter**: Adds silence padding at the end
- **If longer**: Time-stretches using librosa to reduce speed

### Gaps

Original gaps between segments are preserved using silence.

## ComfyUI Workflow

The pipeline uses a simple 3-node workflow:

1. **LoadAudio** - Loads reference audio (`#1.wav`)
2. **VoiceCloneNode** - Generates cloned voice for target text
3. **SaveAudio** - Saves output to file

**Model settings:**
- Model: Qwen3-TTS-12Hz-0.6B-Base (fast, good quality)
- Device: auto (CUDA if available)
- Precision: bf16
- Language: Auto

## Performance

**Estimated times (RTX 2060 SUPER 8GB):**
- Loading model: ~5 seconds (first segment)
- Generation per segment: ~2-5 seconds
- Total for 20 segments: ~1-2 minutes

**Factors affecting speed:**
- Segment length
- Model size (0.6B vs 1.7B)
- GPU availability
- CPU performance

## Troubleshooting

### ComfyUI not starting

Check if port 8188 is already in use:
```bash
lsof -i :8188
```

### Import errors

Ensure all dependencies are installed:
```bash
pip install -r voice_cloning_requirements.txt
```

### Audio not generating

Check ComfyUI logs for errors:
```bash
tail -f /tmp/comfyui.log
```

### Timing mismatch

The pipeline automatically adjusts duration, but if issues persist:
- Increase gap threshold in `extract_segments()`
- Manually edit SRT file for better segmentation

## API Usage

You can also use the pipeline as a Python module:

```python
from voice_cloning_pipeline import SRTParser, ComfyUIClient, VoiceCloningWorkflow, AudioProcessor

# Parse SRT
parser = SRTParser("subtitles.srt")
segments = parser.extract_segments(gap_threshold=0.3)

# Connect to ComfyUI
client = ComfyUIClient("http://127.0.0.1:8188")
workflow = VoiceCloningWorkflow(client, "reference.wav", "output/")

# Generate audio
for i, segment in enumerate(segments):
    audio_file = workflow.generate_audio(segment, i)

# Stitch and save
processor = AudioProcessor()
combined = processor.stitch_segments(segments, audio_files)
processor.save_audio(combined, "output.wav", 24000)
```

## Notes

- The reference audio should be clean speech (3-30 seconds recommended)
- Longer segments may generate faster than many short segments
- Model stays loaded after first generation for faster subsequent generations
- Audio output is 24kHz mono (Qwen3 TTS standard)

## Next Steps

- Experiment with different segment gap thresholds
- Try different model sizes (1.7B for better quality)
- Adjust TTS parameters (temperature, top_p, etc.) in the workflow
- Use VoiceClonePromptNode for batch processing with same voice characteristics
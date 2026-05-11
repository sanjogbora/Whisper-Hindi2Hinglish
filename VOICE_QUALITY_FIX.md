# Voice Quality Improvement Guide

## Current Issues

The voice quality is poor due to these settings:

| Parameter | Current | Problem | Solution |
|-----------|---------|---------|----------|
| Model | 0.6B | Too small, lower quality | Use 1.7B |
| Mode | x_vector_only=True | Fast mode, less accurate | Use False (ICL mode) |
| Reference Text | Empty | No voice context | Add transcribed text |
| Temperature | 1.0 | Too random | Use 0.7 |
| Precision | bf16 | Minor quality loss | Use fp32 |

## Quick Fixes

### 1. Use the Updated Pipeline
Run the pipeline again with improved settings:
```bash
source /home/ishanp/micromamba/envs/qwen3-tts/lib/python3.12/venv/scripts/common/activate
python voice_cloning_pipeline.py
```

The pipeline now uses:
- **1.7B model** (better quality)
- **ICL mode** with reference text
- **Temperature 0.7** (more stable)
- **FP32 precision** (higher accuracy)

### 2. Add Reference Text (Important!)

Transcribe your reference audio:
```bash
whisper /home/ishanp/Videos/#1.wav --model base --output_format txt
```

Then update the pipeline to use this text in the `ref_text` parameter.

### 3. Improve Reference Audio

**Best practices for voice samples:**
- Length: 10-30 seconds
- Clear, clean speech
- Minimal background noise
- Consistent speaking style
- Good microphone quality

**Clean your reference audio:**
```bash
# Remove background noise
ffmpeg -i #1.wav -af "highpass=f=100,lowpass=f=8000" #1_clean.wav

# Normalize audio
ffmpeg -i #1_clean.wav -af "loudnorm" #1_norm.wav
```

### 4. Post-Processing

After generating the audio, improve quality:

```bash
# Upsample to 48kHz
ffmpeg -i The_Archetypical_Mind_VoiceCloned.wav \
  -ar 48000 -ac 2 \
  The_Archetypical_Mind_VoiceCloned_hq.wav

# Add slight reverb for natural sound
ffmpeg -i The_Archetypical_Mind_VoiceCloned_hq.wav \
  -af "aecho=0.8:0.9:1000|0.8:0.9:1500" \
  The_Archetypical_Mind_VoiceCloned_final.wav

# Normalize audio levels
ffmpeg -i The_Archetypical_Mind_VoiceCloned_final.wav \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
  The_Archetypical_Mind_VoiceCloned_mastered.wav
```

## Quality Settings Comparison

### Fast Mode (Current - Poor Quality)
```python
{
    "model_choice": "0.6B",
    "x_vector_only": True,
    "temperature": 1.0,
    "precision": "bf16",
    "ref_text": ""
}
```
- Speed: Fast (~2-5 seconds per segment)
- Quality: Poor
- Use case: Quick testing

### Quality Mode (Recommended)
```python
{
    "model_choice": "1.7B",
    "x_vector_only": False,
    "temperature": 0.7,
    "precision": "fp32",
    "ref_text": "transcribed_text_here"
}
```
- Speed: Slower (~10-30 seconds per segment)
- Quality: Excellent
- Use case: Final production

### Ultra Mode (Best Quality)
```python
{
    "model_choice": "1.7B",
    "x_vector_only": False,
    "temperature": 0.6,
    "precision": "fp32",
    "ref_text": "transcribed_text_here",
    "top_p": 0.95,
    "top_k": 50,
    "repetition_penalty": 1.15
}
```
- Speed: Very slow (~30-60 seconds per segment)
- Quality: Best possible
- Use case: Critical applications

## Troubleshooting

### Voice sounds robotic
- Lower temperature (0.6-0.7)
- Increase top_k (30-50)
- Use ICL mode with reference text

### Voice doesn't match reference
- Ensure reference audio is clean
- Add accurate reference text
- Use 1.7B model
- Lower temperature

### Audio has artifacts
- Use fp32 precision
- Check reference audio quality
- Try different seed values

### Voice is too fast/slow
- Adjust timing in post-processing
- Use librosa time-stretching
- Modify segment grouping

## Recommended Workflow

1. **Prepare reference audio** (clean, 10-30s)
2. **Transcribe reference audio** (Whisper)
3. **Run pipeline with quality settings** (1.7B, ICL mode)
4. **Post-process** (upsample, normalize, add reverb)
5. **Compare with original** and adjust parameters

## Files

- `voice_cloning_pipeline.py` - Main pipeline (updated with quality settings)
- `voice_cloning_hq.py` - High-quality test script
- `voice_cloned_segments/` - Generated segments
- `The_Archetypical_Mind_VoiceCloned.wav` - Final output
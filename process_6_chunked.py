#!/usr/bin/env python3
"""
Process #6.mp4.mov with Prime model on CUDA using audio chunking
"""

import gc
import torch
import numpy as np
import subprocess
import tempfile
import os
from pathlib import Path
import whisper_timestamped as whisper


def clear_gpu_memory():
    """Clear GPU memory"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()


def split_audio(audio_path, chunk_duration=30):
    """Split audio into chunks of specified duration"""
    import wave
    import audioop

    with wave.open(audio_path, "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        width = wf.getsampwidth()
        channels = wf.getnchannels()

        chunk_frames = int(chunk_duration * rate)
        chunks = []

        for i in range(0, frames, chunk_frames):
            chunk_data = wf.readframes(min(chunk_frames, frames - i))
            chunks.append(chunk_data)

    return chunks, rate, width, channels


def transcribe_chunk(audio_data, rate, width, channels, model):
    """Transcribe a single audio chunk"""
    # Convert raw audio to numpy array
    audio_array = np.frombuffer(audio_data, dtype=np.int16)

    # Convert to float16 and normalize
    audio_float = audio_array.astype(np.float16) / 32768.0

    # Resample to 16kHz if needed
    if rate != 16000:
        import librosa

        audio_float = librosa.resample(audio_float, orig_sr=rate, target_sr=16000)

    # Transcribe
    result = whisper.transcribe(
        model,
        audio_float,
        language="hi",
        vad=False,
        condition_on_previous_text=False,
        remove_empty_words=True,
        plot_word_alignment=False,
    )

    return result


def main():
    video_path = "/home/ishanp/Videos/#6.mp4.mov"

    print(f"Processing: {video_path}")
    print("=" * 60)

    # Load model FIRST before extracting audio
    print("Loading Prime model in float16...")
    model = whisper.load_model("Oriserve/Whisper-Hindi2Hinglish-Prime", device="cpu")
    model = model.half().to("cuda")
    print("Model loaded")
    clear_gpu_memory()

    # Extract audio
    print("Extracting audio...")
    temp_dir = tempfile.mkdtemp()
    audio_path = os.path.join(temp_dir, "audio.wav")

    cmd = [
        "ffmpeg",
        "-i",
        video_path,
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        "-y",
        audio_path,
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    print(f"Audio extracted to: {audio_path}")

    # Get audio duration
    import wave

    with wave.open(audio_path, "rb") as wf:
        duration = wf.getnframes() / wf.getframerate()
        print(f"Audio duration: {duration:.2f}s")

    # Split audio into chunks
    chunk_duration = 30  # seconds
    print(f"Splitting audio into {chunk_duration}s chunks...")
    chunks, rate, width, channels = split_audio(audio_path, chunk_duration)
    print(f"Created {len(chunks)} chunks")

    # Transcribe each chunk
    all_segments = []
    current_time = 0

    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i + 1}/{len(chunks)}...")

        try:
            result = transcribe_chunk(chunk, rate, width, channels, model)

            # Adjust timestamps
            for segment in result["segments"]:
                segment["start"] += current_time
                segment["end"] += current_time
                all_segments.append(segment)

            current_time += chunk_duration

            # Clear GPU memory
            clear_gpu_memory()

        except Exception as e:
            print(f"Error processing chunk {i + 1}: {e}")
            clear_gpu_memory()
            continue

    # Generate SRT
    print("Generating SRT...")
    srt_path = "/home/ishanp/Videos/#6.mp4.srt"

    with open(srt_path, "w", encoding="utf-8") as f:
        for idx, segment in enumerate(all_segments, 1):
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])
            text = segment["text"].strip()

            if text:
                f.write(f"{idx}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")

    print(f"✓ SRT generated: {srt_path}")
    print(f"  Total segments: {len(all_segments)}")

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir)
    clear_gpu_memory()


def format_timestamp(seconds):
    """Format seconds to SRT timestamp format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


if __name__ == "__main__":
    main()

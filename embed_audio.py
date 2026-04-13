#!/usr/bin/env python3
"""
Embed generated audio into video
Replaces original audio track with voice-cloned audio
"""

import subprocess
import sys
import os
from pathlib import Path


def embed_audio(video_path: str, audio_path: str, output_path: str):
    """
    Embed new audio into video using ffmpeg

    Args:
        video_path: Path to original video
        audio_path: Path to new audio file
        output_path: Path to output video
    """

    # Check if files exist
    if not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        return False

    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found: {audio_path}")
        return False

    print(f"Embedding audio...")
    print(f"  Video: {video_path}")
    print(f"  Audio: {audio_path}")
    print(f"  Output: {output_path}")

    # FFmpeg command to replace audio
    # -map 0:v:0 - use video stream from first input
    # -map 1:a:0 - use audio stream from second input
    # -c:v copy - copy video stream without re-encoding
    # -c:a aac - encode audio as AAC
    # -shortest - use shortest duration
    cmd = [
        "ffmpeg",
        "-i",
        video_path,
        "-i",
        audio_path,
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        "-y",  # Overwrite output file
        output_path,
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"\nSuccessfully created video: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nError embedding audio:")
        print(f"  Return code: {e.returncode}")
        print(f"  Stdout: {e.stdout}")
        print(f"  Stderr: {e.stderr}")
        return False


def verify_output(output_path: str):
    """Verify the output video was created"""
    if os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"\nOutput video verified:")
        print(f"  Path: {output_path}")
        print(f"  Size: {size_mb:.2f} MB")

        # Get video info
        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            output_path,
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            duration = float(result.stdout.strip())
            print(f"  Duration: {duration:.2f}s")
        except:
            pass

        return True
    else:
        print(f"\nWarning: Output file not found: {output_path}")
        return False


def main():
    """Main execution"""

    # Configuration
    video_path = "/home/ishanp/Downloads/The_Archetypical_Mind.mp4"
    audio_path = "/home/ishanp/Documents/GitHub/Whisper-Hindi2Hinglish/The_Archetypical_Mind_VoiceCloned.wav"
    output_path = "/home/ishanp/Documents/GitHub/Whisper-Hindi2Hinglish/The_Archetypical_Mind_VoiceCloned.mp4"

    print("=" * 60)
    print("Audio Embedding Pipeline")
    print("=" * 60)

    # Embed audio
    success = embed_audio(video_path, audio_path, output_path)

    if success:
        # Verify output
        verify_output(output_path)

        print("\n" + "=" * 60)
        print("Embedding complete!")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("Embedding failed!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

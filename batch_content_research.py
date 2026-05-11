#!/usr/bin/env python3
"""
Batch process videos to generate SRT files using Hinglish model with CPU
For Content-Research analysis - generates transcripts for all videos

IMPORTANT: Run this script using the conda environment:
    conda activate whisper-hindi
    python batch_content_research.py
"""

import gc
from pathlib import Path
import torch
from caption_generator import media_to_srt

VIDEO_DIR = Path("/home/ishanp/Videos/Content-Research")

MODEL_ID = "Oriserve/Whisper-Hindi2Hinglish-Prime"
DEVICE = "cpu"


def clear_memory():
    """Clear memory between videos"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()


def get_all_videos():
    """Get all MP4 video files from directory that don't have SRT yet"""
    all_videos = sorted(VIDEO_DIR.glob("*.mp4"))
    videos_without_srt = []
    for video in all_videos:
        srt_path = video.with_suffix(".srt")
        if not srt_path.exists():
            videos_without_srt.append(video)
        else:
            print(f"Skipping (already has SRT): {video.name}")
    return videos_without_srt


def main():
    videos = get_all_videos()

    if not videos:
        print(f"❌ No MP4 videos found in {VIDEO_DIR}")
        return

    print(f"Found {len(videos)} videos to process")
    print(f"Output directory: {VIDEO_DIR}")
    print(f"Model: {MODEL_ID}")
    print(f"Device: {DEVICE}")
    print("=" * 60)

    success_count = 0
    failed_count = 0
    failed_files = []

    for idx, video_path in enumerate(videos, 1):
        print(f"\n[{idx}/{len(videos)}] Processing: {video_path.name}")
        print("-" * 60)

        try:
            output_srt = media_to_srt(
                media_path=str(video_path),
                output_srt_path=str(video_path.with_suffix(".srt")),
                model_id=MODEL_ID,
                device=DEVICE,
            )
            print(f"✓ SRT generated: {output_srt}")
            success_count += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            failed_count += 1
            failed_files.append(video_path.name)
        finally:
            clear_memory()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total videos: {len(videos)}")
    print(f"✓ Successful: {success_count}")
    print(f"❌ Failed: {failed_count}")

    if failed_files:
        print("\nFailed files:")
        for f in failed_files:
            print(f"  - {f}")


if __name__ == "__main__":
    main()

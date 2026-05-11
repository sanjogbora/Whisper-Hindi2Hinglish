#!/usr/bin/env python3
"""
Process #6.mp4.mov with Prime model on CUDA
"""

import sys
import gc
import torch
from caption_generator import media_to_srt


def clear_gpu_memory():
    """Clear GPU memory"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()


if __name__ == "__main__":
    video_path = "/home/ishanp/Videos/#6.mp4.mov"

    print(f"Processing: {video_path}")
    print("=" * 60)

    try:
        output_srt = media_to_srt(
            media_path=video_path,
            model_id="Oriserve/Whisper-Hindi2Hinglish-Prime",
            device="cpu",
        )
        print(f"✓ SRT generated: {output_srt}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        clear_gpu_memory()

#!/usr/bin/env python3
"""
Process a single audio file to generate SRT using Prime model with memory management
"""

import sys
import gc
import torch
from pathlib import Path
from caption_generator import media_to_srt


def clear_gpu_memory():
    """Clear GPU memory"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python process_single.py <mp3_file>")
        sys.exit(1)

    mp3_file = sys.argv[1]
    mp3_path = Path("/home/ishanp/Videos/todo_captions") / mp3_file

    if not mp3_path.exists():
        print(f"❌ File not found: {mp3_path}")
        sys.exit(1)

    print(f"Processing: {mp3_file}")
    print("=" * 60)

    try:
        output_srt = media_to_srt(
            media_path=str(mp3_path),
            model_id="Oriserve/Whisper-Hindi2Hinglish-Prime",
            device="cpu",
        )
        print(f"✓ SRT generated: {output_srt}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        clear_gpu_memory()

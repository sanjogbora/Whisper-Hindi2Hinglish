#!/usr/bin/env python3
"""
Batch process videos to generate SRT files using Hinglish model with CUDA

IMPORTANT: Run this script using the conda environment:
    conda activate whisper-hindi
    python batch_generate_srt.py
"""

import gc
from pathlib import Path
import torch
from caption_generator import media_to_srt

VIDEO_DIR = Path("/home/ishanp/Videos/todo_captions")

VIDEOS = [
    "Aapka Mann_ Auzaar ya Jaal_ _ Spirit ka Pehla Discipline _ Law of One (Session 5) [yLdrKyk6jjs].mp3",
    "Apne Inner Universe ko Master Karein_ Mann ke Anushasan ko Samjhein _ The Law of One (Session 5) [gpjRTphLVUg].mp3",
    "Archetypical Mind_ Reflections on the Architecture of the Reality [bElZuxIlBTs].mp3",
    "Archetypical Mind_ Understanding Our Logos [yE4f4FGd0CU].mp3",
    "Break Free_ The Truth About Financial Intelligence P1 [d9NDRqEFBBg].mp3",
    "Dream World के Secret दरवाज़े खोलें _ Lucid Dreaming & The Law of One (Lucidology 101) [PcxnpErRMl4].mp3",
    "From Trauma to Transformation_ My Journey of Healing & Self-Actualization  Ishan Parihar.mp3",
    "Man ki Chabi hai Khamoshi_ Asli Healing ka Raasta _ The Law of One Session 5 (Hindi) [uk3uy3kAlk8].mp3",
    "Ra Reveals the Pyramid's ULTIMATE Secret_ A Gateway to Higher Consciousness _ Law of One (Session 4) [YcZUH1PPjzw].mp3",
    "RA's Secret Ritual & How to Move Objects With Your Mind _ The Law of One Session 2.6-3.8 [0N-E3GYKNyk].mp3",
    "Ra का सबसे गहरा ज्ञान_ Healing का पहला और सबसे ज़रूरी कदम _ Law of One (4.18-4.20) Hindi [UkLsvweAU5g].mp3",
    "Secrets of Your Mind Unlocked_ Kundalini, Dream Powers & The Law of One _ Live Q&A (5-Jul-25) [mePwM8EXWsE].mp3",
    "Tree of Life_ A Blueprint of Reality presented by Ishan Parihar [s6aza0wY4bs].mp3",
    "_पिरामिड हमारे विचारों से बने थे_ - रा _ चेतना से रचना का रहस्य _ Reading Session 27 Jun 2025 [yA2ISR9nxdc].mp3",
]

MODEL_ID = "Oriserve/Whisper-Hindi2Hinglish-Prime"
DEVICE = "cuda"


def clear_gpu_memory():
    """Clear GPU memory between videos"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()


def main():
    for video_file in VIDEOS:
        video_path = VIDEO_DIR / video_file

        if not video_path.exists():
            print(f"❌ Video not found: {video_path}")
            continue

        print(f"\n{'=' * 60}")
        print(f"Processing: {video_file}")
        print(f"{'=' * 60}")

        try:
            output_srt = media_to_srt(
                media_path=str(video_path),
                model_id=MODEL_ID,
                device=DEVICE,
            )
            print(f"✓ SRT generated: {output_srt}")
        except Exception as e:
            print(f"❌ Error processing {video_file}: {e}")
        finally:
            clear_gpu_memory()


if __name__ == "__main__":
    main()

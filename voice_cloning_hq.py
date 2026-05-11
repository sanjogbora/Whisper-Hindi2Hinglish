#!/usr/bin/env python3
"""
High-Quality Voice Cloning Pipeline
Uses 1.7B model, ICL mode, and better parameters
"""

import os
import re
import time
import requests
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import List, Dict, Optional


def transcribe_reference_audio(audio_path: str) -> str:
    """Quick transcription using Whisper for reference text"""
    try:
        import whisper

        model = whisper.load_model("large")
        result = model.transcribe(audio_path)
        return result["text"].strip()
    except:
        return ""


class QualityVoiceCloning:
    def __init__(self, comfy_client, ref_audio_path: str, output_dir: str):
        self.client = comfy_client
        self.ref_audio_path = ref_audio_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.comfy_input_dir = Path("/home/ishanp/Documents/GitHub/ComfyUI/input")
        self.comfy_ref_audio = self.comfy_input_dir / Path(ref_audio_path).name
        self._copy_reference_audio()
        self.ref_text = transcribe_reference_audio(ref_audio_path)
        print(f"Reference text: {self.ref_text[:100]}...")

    def _copy_reference_audio(self):
        import shutil

        if not self.comfy_ref_audio.exists():
            shutil.copy(self.ref_audio_path, self.comfy_ref_audio)
            print(f"Copied reference audio to {self.comfy_ref_audio}")

    def create_workflow(self, target_text: str, output_filename: str) -> dict:
        """Create workflow with high-quality settings"""
        return {
            "1": {
                "inputs": {"audio": self.comfy_ref_audio.name},
                "class_type": "LoadAudio",
            },
            "2": {
                "inputs": {
                    "target_text": target_text,
                    "model_choice": "1.7B",  # Better quality model
                    "device": "auto",
                    "precision": "fp32",  # Higher precision
                    "language": "Auto",
                    "ref_audio": ["1", 0],
                    "ref_text": self.ref_text,  # Use transcribed text
                    "seed": 42,  # Fixed seed for consistency
                    "max_new_tokens": 2048,
                    "top_p": 0.9,  # More variety
                    "top_k": 30,  # More options
                    "temperature": 0.7,  # Lower temperature for more stable voice
                    "repetition_penalty": 1.1,  # Reduce repetition
                    "x_vector_only": False,  # ICL mode for better quality
                    "attention": "auto",
                    "unload_model_after_generate": False,
                },
                "class_type": "FB_Qwen3TTSVoiceClone",
            },
            "3": {
                "inputs": {"audio": ["2", 0], "filename_prefix": output_filename},
                "class_type": "SaveAudio",
            },
        }


def main():
    srt_path = (
        "/home/ishanp/Documents/GitHub/Whisper-Hindi2Hinglish/The_Archetypical_Mind.srt"
    )
    ref_audio_path = "/home/ishanp/Videos/#1.wav"
    output_dir = "/home/ishanp/Documents/GitHub/Whisper-Hindi2Hinglish/voice_cloned_hq"
    final_output = "/home/ishanp/Documents/GitHub/Whisper-Hindi2Hinglish/The_Archetypical_Mind_VoiceCloned_HQ.wav"

    print("=" * 60)
    print("High-Quality Voice Cloning Pipeline")
    print("=" * 60)

    # Parse SRT
    with open(srt_path) as f:
        content = f.read()
    pattern = r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\d+\n|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)

    def time_to_seconds(t):
        h, m, s = t.replace(",", ".").split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)

    # Extract segments
    segments = []
    current_segment = []
    segment_start = None
    prev_end = None

    for idx, start, end, text in matches:
        s = time_to_seconds(start)
        e = time_to_seconds(end)
        if prev_end is None:
            current_segment.append((idx, s, e, text.strip()))
            segment_start = s
        else:
            gap = s - prev_end
            if gap > 0.3:
                segments.append(
                    {
                        "index": len(segments),
                        "start": segment_start,
                        "end": prev_end,
                        "duration": prev_end - segment_start,
                        "text": " ".join([t[3] for t in current_segment]),
                        "gap": gap,
                    }
                )
                current_segment = [(idx, s, e, text.strip())]
                segment_start = s
            else:
                current_segment.append((idx, s, e, text.strip()))
        prev_end = e

    if current_segment:
        segments.append(
            {
                "index": len(segments),
                "start": segment_start,
                "end": prev_end,
                "duration": prev_end - segment_start,
                "text": " ".join([t[3] for t in current_segment]),
                "gap": 0.0,
            }
        )

    print(f"Total segments: {len(segments)}")

    # Initialize workflow with high quality settings
    class ComfyClient:
        def __init__(self, url):
            self.url = url
            self.client_id = str(int(time.time()))

        def queue_prompt(self, workflow):
            return requests.post(
                f"{self.url}/prompt",
                json={"prompt": workflow, "client_id": self.client_id},
            ).json()

        def wait_for_completion(self, prompt_id, timeout=300):
            start = time.time()
            while time.time() - start < timeout:
                history = requests.get(f"{self.url}/history/{prompt_id}").json()
                if prompt_id in history:
                    status = history[prompt_id].get("status", {})
                    if status.get("completed", False):
                        return history[prompt_id]
                    if status.get("error", False):
                        print(f"Error: {status.get('messages', {}).get('error', {})}")
                        return None
                time.sleep(1)
            return None

    client = ComfyClient("http://127.0.0.1:8188")
    workflow = QualityVoiceCloning(client, ref_audio_path, output_dir)

    # Generate segments
    audio_files = []
    for i, seg in enumerate(segments[:3]):  # Test with first 3 segments first
        print(f"\nProcessing segment {i + 1}/3 ({seg['duration']:.2f}s)")
        print(f"  Text: {seg['text'][:80]}...")

        workflow_obj = workflow.create_workflow(seg["text"], f"segment_hq_{i:03d}")
        response = client.queue_prompt(workflow_obj)

        if "prompt_id" not in response:
            print(f"  Failed: {response}")
            continue

        prompt_id = response["prompt_id"]
        print(f"  Queued: {prompt_id}")

        history_data = client.wait_for_completion(prompt_id, timeout=180)
        if history_data is None:
            continue

        outputs = history_data.get("outputs", {})
        if "3" in outputs:
            audio = outputs["3"].get("audio", [])
            if isinstance(audio, list) and audio:
                filename = audio[0].get("filename")
                src_path = (
                    Path("/home/ishanp/Documents/GitHub/ComfyUI/output") / filename
                )
                output_path = workflow.output_dir / f"segment_hq_{i:03d}.wav"
                if src_path.exists():
                    import shutil

                    shutil.copy(src_path, output_path)
                    info = sf.info(output_path)
                    print(f"  Generated: {info.duration:.2f}s")
                    audio_files.append(str(output_path))

    print("\n" + "=" * 60)
    print("Test complete! Check voice quality of first 3 segments.")
    print(f"Segment files in: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()

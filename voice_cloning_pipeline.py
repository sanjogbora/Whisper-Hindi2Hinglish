#!/usr/bin/env python3
"""
Voice Cloning Pipeline using ComfyUI Qwen3 TTS
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


class SRTParser:
    def __init__(self, srt_path: str):
        self.srt_path = srt_path
        self.subtitles = []
        self.segments = []

    def parse(self):
        with open(self.srt_path, "r", encoding="utf-8") as f:
            content = f.read()
        pattern = r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\d+\n|\Z)"
        matches = re.findall(pattern, content, re.DOTALL)
        for idx, start, end, text in matches:
            self.subtitles.append(
                {
                    "index": int(idx),
                    "start_time": self._time_to_seconds(start),
                    "end_time": self._time_to_seconds(end),
                    "text": text.strip(),
                }
            )
        return self.subtitles

    def extract_segments(self, gap_threshold: float = 0.3) -> List[Dict]:
        if not self.subtitles:
            self.parse()
        segments = []
        current_segment = []
        segment_start = None
        prev_end = None
        for sub in self.subtitles:
            if prev_end is None:
                current_segment.append(sub)
                segment_start = sub["start_time"]
            else:
                gap = sub["start_time"] - prev_end
                if gap > gap_threshold:
                    segments.append(
                        {
                            "index": len(segments),
                            "start_time": segment_start,
                            "end_time": prev_end,
                            "duration": prev_end - segment_start,
                            "text": " ".join([s["text"] for s in current_segment]),
                            "subtitles": current_segment.copy(),
                            "gap_after": gap,
                        }
                    )
                    current_segment = [sub]
                    segment_start = sub["start_time"]
                else:
                    current_segment.append(sub)
            prev_end = sub["end_time"]
        if current_segment:
            segments.append(
                {
                    "index": len(segments),
                    "start_time": segment_start,
                    "end_time": prev_end,
                    "duration": prev_end - segment_start,
                    "text": " ".join([s["text"] for s in current_segment]),
                    "subtitles": current_segment.copy(),
                    "gap_after": 0.0,
                }
            )
        self.segments = segments
        return segments

    @staticmethod
    def _time_to_seconds(time_str: str) -> float:
        h, m, s = time_str.replace(",", ".").split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)


class ComfyUIClient:
    def __init__(self, server_url: str = "http://127.0.0.1:8188"):
        self.server_url = server_url
        self.client_id = str(int(time.time()))

    def queue_prompt(self, workflow: dict) -> dict:
        p = {"prompt": workflow, "client_id": self.client_id}
        response = requests.post(f"{self.server_url}/prompt", json=p)
        return response.json()

    def get_history(self, prompt_id: str) -> dict:
        response = requests.get(f"{self.server_url}/history/{prompt_id}")
        return response.json()

    def wait_for_completion(self, prompt_id: str, timeout: int = 300) -> Optional[dict]:
        start_time = time.time()
        while time.time() - start_time < timeout:
            history = self.get_history(prompt_id)
            if prompt_id in history:
                history_data = history[prompt_id]
                if "status" in history_data:
                    status = history_data["status"]
                    if status.get("completed", False):
                        return history_data
                    if status.get("error", False):
                        print(f"Error: {status.get('messages', {}).get('error', {})}")
                        return None
            time.sleep(0.5)
        print(f"Timeout waiting for prompt {prompt_id}")
        return None

    def get_workflow_output(self, history_data: dict, node_id: int) -> Optional[dict]:
        outputs = history_data.get("outputs", {})
        if str(node_id) in outputs:
            return outputs[str(node_id)]
        return None


class VoiceCloningWorkflow:
    def __init__(
        self, comfy_client: ComfyUIClient, ref_audio_path: str, output_dir: str
    ):
        self.client = comfy_client
        self.ref_audio_path = ref_audio_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.comfy_input_dir = Path("/home/ishanp/Documents/GitHub/ComfyUI/input")
        self.comfy_ref_audio = self.comfy_input_dir / Path(ref_audio_path).name
        self._copy_reference_audio()

    def _copy_reference_audio(self):
        import shutil

        if not self.comfy_ref_audio.exists():
            shutil.copy(self.ref_audio_path, self.comfy_ref_audio)
            print(f"Copied reference audio to {self.comfy_ref_audio}")

    def create_workflow(self, target_text: str, output_filename: str) -> dict:
        """Create ComfyUI workflow for voice cloning"""
        return {
            "1": {
                "inputs": {"audio": self.comfy_ref_audio.name},
                "class_type": "LoadAudio",
            },
            "2": {
                "inputs": {
                    "target_text": target_text,
                    "model_choice": "1.7B",  # Better quality
                    "device": "auto",
                    "precision": "fp32",  # Higher precision
                    "language": "Auto",
                    "ref_audio": ["1", 0],
                    "ref_text": "",  # Add transcribed text for ICL mode
                    "seed": 42,  # Fixed seed for consistency
                    "max_new_tokens": 2048,
                    "top_p": 0.9,  # More variety
                    "top_k": 30,  # More options
                    "temperature": 0.7,  # More stable voice
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
        return workflow

    def generate_audio(self, segment: Dict, segment_index: int) -> Optional[str]:
        output_filename = f"segment_{segment_index:03d}"
        output_path = self.output_dir / f"{output_filename}.wav"
        workflow = self.create_workflow(segment["text"], output_filename)
        response = self.client.queue_prompt(workflow)
        if "prompt_id" not in response:
            print(f"Failed to queue prompt for segment {segment_index}: {response}")
            return None
        prompt_id = response["prompt_id"]
        print(
            f"Queued segment {segment_index}: {segment['text'][:50]}... (prompt_id: {prompt_id})"
        )
        history_data = self.client.wait_for_completion(prompt_id)
        if history_data is None:
            return None
        output = self.client.get_workflow_output(history_data, 3)
        if output is None:
            return None
        # Handle different output formats
        audio_output = output.get("audio", [])
        if isinstance(audio_output, list) and audio_output:
            comfy_output_file = audio_output[0].get("filename")
        elif isinstance(audio_output, dict):
            comfy_output_file = list(audio_output.values())[0].get("filename")
        else:
            print(f"Unexpected output format: {type(audio_output)}")
            return None
        src_path = (
            Path("/home/ishanp/Documents/GitHub/ComfyUI/output") / comfy_output_file
        )
        if src_path.exists():
            import shutil

            shutil.copy(src_path, output_path)
            print(f"Saved audio to {output_path}")
            return str(output_path)
        return None


class AudioProcessor:
    def __init__(self, sample_rate: int = 24000):
        self.sample_rate = sample_rate

    def adjust_duration(
        self, audio: np.ndarray, target_duration: float, sr: int
    ) -> np.ndarray:
        current_duration = len(audio) / sr
        if abs(current_duration - target_duration) < 0.1:
            return audio
        if current_duration < target_duration:
            silence_samples = int((target_duration - current_duration) * sr)
            silence = np.zeros(silence_samples, dtype=audio.dtype)
            return np.concatenate([audio, silence])
        else:
            rate = current_duration / target_duration
            return librosa.effects.time_stretch(audio, rate=rate)

    def stitch_segments(
        self, segments: List[Dict], audio_files: List[str]
    ) -> np.ndarray:
        combined_audio = []
        sr = None
        for i, (segment, audio_file) in enumerate(zip(segments, audio_files)):
            if audio_file is None or not os.path.exists(audio_file):
                continue
            audio, sr = sf.read(audio_file)
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)
            audio = self.adjust_duration(audio, segment["duration"], sr)
            combined_audio.append(audio)
            if i < len(segments) - 1 and segment["gap_after"] > 0:
                gap_silence = np.zeros(
                    int(segment["gap_after"] * sr), dtype=audio.dtype
                )
                combined_audio.append(gap_silence)
        if not combined_audio:
            return None
        return np.concatenate(combined_audio)

    def save_audio(self, audio: np.ndarray, output_path: str, sr: int):
        sf.write(output_path, audio, sr)
        print(f"Saved combined audio to {output_path}")


def main():
    srt_path = (
        "/home/ishanp/Documents/GitHub/Whisper-Hindi2Hinglish/The_Archetypical_Mind.srt"
    )
    ref_audio_path = "/home/ishanp/Videos/#1.wav"
    output_dir = (
        "/home/ishanp/Documents/GitHub/Whisper-Hindi2Hinglish/voice_cloned_segments"
    )
    final_output = "/home/ishanp/Documents/GitHub/Whisper-Hindi2Hinglish/The_Archetypical_Mind_VoiceCloned.wav"

    print("=" * 60)
    print("Voice Cloning Pipeline")
    print("=" * 60)

    parser = SRTParser(srt_path)
    parser.parse()
    segments = parser.extract_segments(gap_threshold=0.3)
    print(f"Total subtitles: {len(parser.subtitles)}")
    print(f"Total segments: {len(segments)}")

    client = ComfyUIClient("http://127.0.0.1:8188")
    workflow = VoiceCloningWorkflow(client, ref_audio_path, output_dir)

    audio_files = []
    for i, segment in enumerate(segments):
        print(
            f"\nProcessing segment {i + 1}/{len(segments)} ({segment['duration']:.2f}s)"
        )
        print(f"  Text: {segment['text'][:80]}...")
        audio_file = workflow.generate_audio(segment, i)
        audio_files.append(audio_file)
        if audio_file and os.path.exists(audio_file):
            info = sf.info(audio_file)
            print(f"  Generated: {info.duration:.2f}s")
        time.sleep(1)

    processor = AudioProcessor()
    combined_audio = processor.stitch_segments(segments, audio_files)
    if combined_audio is not None:
        processor.save_audio(combined_audio, final_output, 24000)
        final_duration = len(combined_audio) / 24000
        original_duration = segments[-1]["end_time"]
        print(
            f"\nFinal audio: {final_duration:.2f}s | Original: {original_duration:.2f}s | Diff: {abs(final_duration - original_duration):.2f}s"
        )

    print("\n" + "=" * 60)
    print("Pipeline complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

"""
Video to SRT Converter - Wrapper for backward compatibility
This module now wraps the caption_generator module to maintain backward compatibility
For new code, use caption_generator.media_to_srt() directly

IMPORTANT: Run this script using the conda environment:
    conda activate whisper-hindi
"""

import argparse
from caption_generator import media_to_srt


def video_to_srt(
    video_path: str,
    output_srt_path: str = None,
    model_id: str = "Oriserve/Whisper-Hindi2Hinglish-Apex",
    device: str = "cpu",
    dtype=None,
):
    """
    Convert video to SRT subtitle file using whisper-timestamped for word-level alignment.
    Default: Apex model on CPU (Hinglish output).
    This is a wrapper function for backward compatibility.

    Args:
        video_path: Path to input video file
        output_srt_path: Path to save SRT file (optional)
        model_id: Whisper model ID (default: Oriserve/Whisper-Hindi2Hinglish-Apex)
        device: Device to run model on (default: cpu)
        dtype: Data type for model (optional, auto-detected if None)

    Returns:
        str: Path to generated SRT file
    """
    import torch
    from utils import torch_dtype_from_str

    # Auto-detect dtype if not provided
    if dtype is None:
        dtype = torch_dtype_from_str("float16", device)

    # Call the new media_to_srt function
    return media_to_srt(video_path, output_srt_path, model_id, device, dtype)


def main():
    """CLI entry point for video-to-SRT conversion"""
    parser = argparse.ArgumentParser(
        description="Convert video to SRT subtitle file with word-level timestamps"
    )
    parser.add_argument("video_path", help="Path to input video file")
    parser.add_argument(
        "--output", "-o", help="Path to output SRT file (default: same name as video)"
    )
    parser.add_argument(
        "--model-id",
        default="Oriserve/Whisper-Hindi2Hinglish-Apex",
        help="Whisper model ID (default: Oriserve/Whisper-Hindi2Hinglish-Apex)",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help="Device to run model on: cuda or cpu (default: cpu)",
    )
    parser.add_argument(
        "--dtype",
        default="float16",
        help="Data type for model (default: float16)",
    )

    args = parser.parse_args()

    # Import torch for dtype conversion
    import torch

    from utils import torch_dtype_from_str

    # Convert dtype string to torch dtype
    dtype = torch_dtype_from_str(args.dtype, args.device)

    # Run conversion
    video_to_srt(args.video_path, args.output, args.model_id, args.device, dtype)


if __name__ == "__main__":
    main()

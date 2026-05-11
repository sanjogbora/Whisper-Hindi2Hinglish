"""
Audio to SRT Converter - CLI for converting audio files to SRT subtitles
Dedicated interface for audio file processing
"""

import argparse
from caption_generator import media_to_srt


def main():
    """CLI entry point for audio-to-SRT conversion"""
    parser = argparse.ArgumentParser(
        description="Convert audio file to SRT subtitle file with word-level timestamps"
    )
    parser.add_argument(
        "audio_path",
        help="Path to input audio file (mp3, wav, ogg, m4a, flac, aac, wma, opus)",
    )
    parser.add_argument(
        "--output", "-o", help="Path to output SRT file (default: same name as audio)"
    )
    parser.add_argument(
        "--model-id",
        default="large",
        help="Whisper model size (default: large. Options: tiny, base, small, medium, large, large-v2, large-v3)",
    )
    parser.add_argument(
        "--device",
        default="cuda",
        help="Device to run model on: cuda or cpu (default: cuda)",
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
    media_to_srt(args.audio_path, args.output, args.model_id, args.device, dtype)


if __name__ == "__main__":
    main()

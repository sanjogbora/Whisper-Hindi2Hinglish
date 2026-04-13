"""
Caption Generator - Generates SRT subtitle files from media (video or audio)
Refactored from video_to_srt.py to support both video and audio input

IMPORTANT: This module requires the conda environment:
    conda activate whisper-hindi
"""

import argparse
import os
from pathlib import Path

import numpy as np
import torch
import whisper_timestamped as whisper

from logger import logger
from media_handler import (
    get_media_duration,
    prepare_audio_for_processing,
    cleanup_temp_file,
    get_media_type,
)
from utils import torch_dtype_from_str, get_device


def format_timestamp(seconds: float) -> str:
    """
    Convert seconds to SRT timestamp format (HH:MM:SS,mmm)

    Args:
        seconds: Time in seconds

    Returns:
        str: Formatted timestamp
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def group_words_for_subtitles(
    segments: list[dict],
    max_words: int = 4,
    max_chars: int = 42,
    max_pause_gap: float = 0.5,
) -> list[tuple[str, float, float]]:
    """
    Group words from whisper-timestamped output into subtitle-friendly chunks.

    Args:
        segments: List of segments from whisper-timestamped with 'words' key
        max_words: Maximum words per subtitle (default 4)
        max_chars: Maximum characters per subtitle (default 42 - Netflix standard)
        max_pause_gap: Maximum gap between words to keep in same subtitle (default 0.5s)

    Returns:
        List of tuples: (text, start_time, end_time)
    """
    all_words = []

    # Extract all words from all segments
    for segment in segments:
        if "words" in segment and segment["words"]:
            all_words.extend(segment["words"])
        else:
            segment_text = segment.get("text", "").strip()
            if segment_text:
                synthetic_word = {
                    "text": segment_text,
                    "start": segment.get("start", 0.0),
                    "end": segment.get("end", 0.0),
                }
                all_words.append(synthetic_word)

    if not all_words:
        logger.error("No words found in any segment - transcription may have failed")
        return []

    subtitles = []
    current_group = []
    current_text = ""

    for i, word_data in enumerate(all_words):
        word = word_data.get("text", "").strip()
        start = word_data.get("start")
        end = word_data.get("end")

        if not word or start is None or end is None:
            # Log the issue
            logger.debug(
                f"Word at index {i} has invalid data: text='{word}', start={start}, end={end}"
            )

            # Try to recover if word has text but missing timestamps
            if word and current_group:
                # Estimate timestamps based on previous word
                last_word = current_group[-1]
                estimated_start = last_word["end"]
                estimated_end = estimated_start + 0.5  # Conservative 0.5s duration

                logger.debug(
                    f"Estimated timestamps for '{word}': {estimated_start:.2f}s - {estimated_end:.2f}s"
                )

                # Create recovered word entry
                word_data = {
                    "text": word,
                    "start": estimated_start,
                    "end": estimated_end,
                }
                # Don't continue, process this word with estimated timestamps
                start = estimated_start
                end = estimated_end
            else:
                # Can't recover, skip this word
                continue

        # Check if we should start a new group
        should_break = False

        if len(current_group) == 0:
            # First word - start new group
            should_break = False
        elif len(current_group) >= max_words:
            # Reached max words
            should_break = True
        elif len(current_text) + len(word) + 1 > max_chars:
            # Would exceed character limit
            should_break = True
        else:
            # Check pause gap
            last_word = current_group[-1]
            gap = start - last_word["end"]
            if gap > max_pause_gap:
                # Long pause - break here
                should_break = True

        if should_break and current_group:
            # Save current group
            group_text = " ".join(w["text"].strip() for w in current_group)
            group_start = current_group[0]["start"]
            group_end = current_group[-1]["end"]
            subtitles.append((group_text, group_start, group_end))

            # Reset
            current_group = []
            current_text = ""

        # Add word to current group
        current_group.append(word_data)
        current_text = current_text + " " + word if current_text else word

    # Don't forget last group
    if current_group:
        group_text = " ".join(w["text"].strip() for w in current_group)
        group_start = current_group[0]["start"]
        group_end = current_group[-1]["end"]
        subtitles.append((group_text, group_start, group_end))

    logger.info(f"Grouped {len(all_words)} words into {len(subtitles)} subtitles")
    return subtitles


def generate_srt(
    transcription_result: dict, output_srt_path: str, media_duration: float = 0.0
):
    """
    Generate SRT file from whisper-timestamped transcription with word-level timestamps.

    Args:
        transcription_result: Dict with 'segments' containing 'words' with timestamps
        output_srt_path: Path to save SRT file
        media_duration: Optional media duration in seconds for comparison
    """
    # Validate input
    if not transcription_result:
        raise ValueError("Transcription result is empty or None")

    segments = transcription_result.get("segments") or []

    if not segments:
        logger.warning("No segments available, creating single subtitle from full text")
        text = transcription_result.get("text", "").strip()
        if text:
            with open(output_srt_path, "w", encoding="utf-8") as f:
                f.write("1\n00:00:00,000 --> 00:00:10,000\n")
                f.write(f"{text}\n\n")
            logger.info(f"SRT file generated with single subtitle: {output_srt_path}")
            return
        else:
            raise ValueError("No transcription text available")

    # Group words into subtitle-friendly chunks
    # Enhanced diagnostic logging
    logger.info(f"Processing {len(segments)} segments")

    # Analyze segment structure
    total_words = 0
    segments_with_words = 0
    segments_without_words = 0
    first_segment_start = None
    last_segment_end = None

    for seg in segments:
        seg_start = seg.get("start")
        seg_end = seg.get("end")

        if first_segment_start is None and seg_start is not None:
            first_segment_start = seg_start
        if seg_end is not None:
            last_segment_end = seg_end

        words = seg.get("words")
        if words:
            segments_with_words += 1
            total_words += len(words)
        else:
            segments_without_words += 1

    logger.info(f"  Total words across all segments: {total_words}")
    logger.info(f"  Segments WITH word-level timestamps: {segments_with_words}")
    if segments_without_words > 0:
        logger.warning(
            f"  Segments WITHOUT word-level timestamps: {segments_without_words} (will use fallback)"
        )

    # Log timeline coverage from segments
    if first_segment_start is not None and last_segment_end is not None:
        segment_duration = last_segment_end - first_segment_start
        logger.info(
            f"  Segment timeline coverage: {first_segment_start:.2f}s - {last_segment_end:.2f}s ({segment_duration:.2f}s total)"
        )
    else:
        logger.warning(f"  Could not determine segment timeline coverage")

    # Log first segment structure for debugging
    if segments:
        first_seg = segments[0]
        logger.debug(f"First segment keys: {list(first_seg.keys())}")
        logger.debug(
            f"First segment: text='{first_seg.get('text', '')[:50]}...', start={first_seg.get('start')}, end={first_seg.get('end')}"
        )
        if "words" in first_seg and first_seg["words"]:
            logger.debug(f"First segment has {len(first_seg['words'])} words")
            logger.debug(f"First word: {first_seg['words'][0]}")

    # Group words - one word per subtitle
    subtitles = group_words_for_subtitles(
        segments, max_words=1, max_chars=42, max_pause_gap=0.5
    )

    # Validate output
    if not subtitles:
        logger.error("❌ No subtitles generated!")
        logger.error("Possible causes:")
        logger.error("  1. No words extracted from segments")
        logger.error("  2. All words had invalid timestamps")
        logger.error("  3. Model doesn't support word-level timestamps")
        logger.error("  4. Transcription produced no segments")
        raise ValueError(
            "Failed to generate subtitles - no valid word timestamps found"
        )

    # Log success metrics
    total_duration = subtitles[-1][2] - subtitles[0][1] if subtitles else 0
    logger.info(f"✓ Generated {len(subtitles)} subtitles")
    logger.info(
        f"  Duration: {subtitles[0][1]:.2f}s - {subtitles[-1][2]:.2f}s ({total_duration:.2f}s total)"
    )
    logger.info(f"  Average: {total_words / len(subtitles):.1f} words per subtitle")

    # Compare with media duration if available
    if media_duration > 0:
        subtitle_end = subtitles[-1][2] if subtitles else 0
        coverage_percent = (
            (subtitle_end / media_duration * 100) if media_duration > 0 else 0
        )
        gap = media_duration - subtitle_end

        logger.info(f"Media duration comparison:")
        logger.info(f"  Media duration: {media_duration:.2f}s")
        logger.info(
            f"  Subtitle coverage: {subtitle_end:.2f}s ({coverage_percent:.1f}%)"
        )

        if gap > 1.0:
            logger.warning(
                f"⚠ COVERAGE GAP: {gap:.2f}s of media NOT covered by subtitles!"
            )
            logger.warning(
                f"  This means the last {gap:.2f}s of the media has no subtitles"
            )
            logger.warning(f"  Possible causes:")
            logger.warning(
                f"    1. Silence or music at end (Whisper stops transcribing)"
            )
            logger.warning(f"    2. Audio quality issues in final section")
            logger.warning(f"    3. Speech not detected by Whisper's VAD")
            logger.warning(f"  Solutions:")
            logger.warning(
                f"    - Check if there's actually speech in the last {gap:.2f}s"
            )
            logger.warning(f"    - Check audio levels in media editor")
        else:
            logger.info(f"  ✓ Good coverage! Gap is only {gap:.2f}s")

    # Write to SRT file
    with open(output_srt_path, "w", encoding="utf-8") as f:
        for i, (text, start_time, end_time) in enumerate(subtitles, 1):
            f.write(f"{i}\n")
            f.write(
                f"{format_timestamp(start_time)} --> {format_timestamp(end_time)}\n"
            )
            f.write(f"{text}\n\n")

    logger.info(
        f"SRT file generated with {len(subtitles)} subtitles: {output_srt_path}"
    )


def media_to_srt(
    media_path: str,
    output_srt_path: str = None,
    model_id: str = "Oriserve/Whisper-Hindi2Hinglish-Apex",
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
):
    """
    Convert media (video or audio) to SRT subtitle file using whisper-timestamped for word-level alignment.

    Default model: Oriserve/Whisper-Hindi2Hinglish-Apex (CPU, Hinglish output).
    Apex outputs Hinglish (Latin script) directly — no transliteration needed.

    Args:
        media_path: Path to input media file (video or audio)
        output_srt_path: Path to save SRT file (optional)
        model_id: Whisper model ID (default: Oriserve/Whisper-Hindi2Hinglish-Apex)
        device: Device to run model on (default: cpu)
        dtype: Data type for model (not used by whisper-timestamped, kept for compatibility)

    Returns:
        str: Path to generated SRT file
    """
    # Automatically detect available device with CPU fallback
    device = get_device(device)

    # Validate media file
    is_valid, result = validate_media_file(media_path)
    if not is_valid:
        raise Exception(result)

    media_type = result
    logger.info(f"Processing {media_type} file: {media_path}")

    # Set default output path
    if output_srt_path is None:
        media_name = Path(media_path).stem
        output_srt_path = f"{media_name}.srt"

    temp_audio_path = None

    try:
        # Step 0: Get media duration for comparison
        media_duration = get_media_duration(media_path)

        # Step 1: Prepare audio for processing
        logger.info(f"Preparing audio for processing")
        temp_audio_path = prepare_audio_for_processing(media_path, keep_temporary=True)

        # Step 2: Load audio for whisper-timestamped
        logger.info(f"Loading audio for processing")
        audio = whisper.load_audio(temp_audio_path)

        # Log audio duration
        audio_duration = len(audio) / 16000.0  # Sample rate is 16kHz
        logger.info(f"Audio duration: {audio_duration:.2f}s")

        audio_rms = float(np.sqrt(np.mean(audio.astype(np.float64) ** 2)))
        if audio_rms < 1e-6:
            logger.warning(
                f"Audio appears to be silent (RMS={audio_rms:.8f}). "
                f"Transcription will produce empty segments."
            )
        else:
            logger.info(f"Audio RMS: {audio_rms:.6f}")

        if media_duration > 0:
            audio_diff = abs(audio_duration - media_duration)
            if audio_diff > 0.5:
                logger.warning(
                    f"Audio duration ({audio_duration:.2f}s) differs from media duration ({media_duration:.2f}s) by {audio_diff:.2f}s"
                )
            else:
                logger.info(
                    f"✓ Audio extraction complete ({audio_duration:.2f}s matches media {media_duration:.2f}s)"
                )

        # Step 3: Load model for whisper-timestamped
        logger.info(f"Loading Whisper model: {model_id}")
        model = whisper.load_model(model_id, device=device)

        # Step 4: Transcribe with forced alignment for word-level timestamps
        logger.info(
            "Transcribing audio with forced alignment for word-level timestamps..."
        )
        logger.info(
            "Conditioning on previous text: DISABLED - prevents stopping at pauses"
        )
        result = whisper.transcribe(
            model,
            audio,
            language="hi",
            vad=False,
            condition_on_previous_text=False,
            remove_empty_words=True,
            plot_word_alignment=False,
            word_alignment_most_top_layers=6,
        )

        # Validate transcription result
        logger.info(f"Transcription complete")
        logger.info(f"Result keys: {list(result.keys())}")

        segments = result.get("segments", [])
        logger.info(f"Number of segments: {len(segments)}")

        if not segments:
            logger.error("❌ Transcription produced no segments!")
            raise ValueError("Transcription failed - no segments generated")

        # Check if first segment has word-level timestamps
        first_seg = segments[0]
        logger.info(f"First segment keys: {list(first_seg.keys())}")

        if "words" not in first_seg:
            logger.warning("⚠ Segments do NOT have 'words' key!")
            logger.warning(
                f"Model '{model_id}' may not support word-level timestamps with whisper-timestamped"
            )
            logger.warning("Will fall back to segment-level timestamps")
        else:
            word_count = len(first_seg.get("words", []))
            logger.info(f"✓ First segment has {word_count} words with timestamps")
            if word_count > 0:
                logger.info(f"  First word: {first_seg['words'][0]}")

        # Log all segment boundaries to identify coverage gaps
        logger.info("Segment timeline:")
        for i, seg in enumerate(segments[:5]):  # Show first 5 segments
            seg_text = seg.get("text", "")[:50]
            logger.info(
                f"  Segment {i + 1}: {seg.get('start', 0):.2f}s - {seg.get('end', 0):.2f}s | '{seg_text}...'"
            )
        if len(segments) > 5:
            logger.info(f"  ... ({len(segments) - 5} more segments)")
            # Show last segment
            last_seg = segments[-1]
            last_seg_text = last_seg.get("text", "")[:50]
            logger.info(
                f"  Segment {len(segments)}: {last_seg.get('start', 0):.2f}s - {last_seg.get('end', 0):.2f}s | '{last_seg_text}...'"
            )

        # Step 5: Generate SRT file
        logger.info("Generating SRT file...")
        generate_srt(result, output_srt_path, media_duration)

        logger.info(f"✓ SRT file created successfully: {output_srt_path}")
        return output_srt_path

    finally:
        # Cleanup temporary audio file
        if temp_audio_path and temp_audio_path != media_path:
            cleanup_temp_file(temp_audio_path)


def validate_media_file(media_path: str):
    """
    Validate media file exists and has supported format
    Import from media_handler for backward compatibility

    Args:
        media_path: Path to media file

    Returns:
        Tuple[bool, str]: (is_valid, error_message or media_type)
    """
    from media_handler import validate_media_file as vf

    return vf(media_path)


def main():
    """CLI entry point for media-to-SRT conversion"""
    parser = argparse.ArgumentParser(
        description="Convert media (video or audio) to SRT subtitle file with word-level timestamps using whisper-timestamped"
    )
    parser.add_argument("media_path", help="Path to input media file (video or audio)")
    parser.add_argument(
        "--output", "-o", help="Path to output SRT file (default: same name as media)"
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
        help="Data type for model (default: float16, kept for compatibility)",
    )

    args = parser.parse_args()

    # Convert dtype string to torch dtype
    dtype = torch_dtype_from_str(args.dtype, args.device)

    # Run conversion
    media_to_srt(args.media_path, args.output, args.model_id, args.device, dtype)


if __name__ == "__main__":
    main()

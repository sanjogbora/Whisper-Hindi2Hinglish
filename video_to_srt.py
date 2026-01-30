"""
Video to SRT Converter
Extracts audio from video and generates SRT subtitle file with timestamps
Uses whisper-timestamped for accurate word-level timestamps via forced alignment
"""
import argparse
import os
import subprocess
import tempfile
from pathlib import Path

import torch
import whisper_timestamped as whisper

from logger import logger
from utils import torch_dtype_from_str, get_device


def get_video_duration(video_path: str) -> float:
    """
    Get video duration in seconds using ffprobe

    Args:
        video_path: Path to video file

    Returns:
        float: Duration in seconds, or 0.0 if unable to determine
    """
    try:
        command = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            duration = float(result.stdout.strip())
            logger.info(f"Video duration: {duration:.2f}s")
            return duration
        else:
            logger.warning(f"Could not determine video duration: {result.stderr}")
            return 0.0

    except Exception as e:
        logger.warning(f"Error getting video duration: {e}")
        return 0.0


def extract_audio_from_video(video_path: str, output_audio_path: str) -> bool:
    """
    Extract audio from video file using ffmpeg

    Args:
        video_path: Path to input video file
        output_audio_path: Path to save extracted audio

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        command = [
            'ffmpeg',
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # 16-bit PCM
            '-ar', '16000',  # 16kHz sample rate
            '-ac', '1',  # Mono
            '-y',  # Overwrite output file
            output_audio_path
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr}")
            return False

        logger.info(f"Audio extracted successfully to {output_audio_path}")
        return True

    except Exception as e:
        logger.error(f"Error extracting audio: {e}")
        return False


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
    max_pause_gap: float = 0.5
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
        if 'words' in segment and segment['words']:
            # Best case: segment has word-level timestamps
            all_words.extend(segment['words'])
        else:
            # Fallback: Create synthetic word entry from segment-level data
            logger.warning(f"Segment missing 'words' key, using segment-level fallback")
            segment_text = segment.get('text', '').strip()
            if segment_text:
                # Create one "word" entry per segment as fallback
                synthetic_word = {
                    'text': segment_text,
                    'start': segment.get('start', 0.0),
                    'end': segment.get('end', 0.0)
                }
                all_words.append(synthetic_word)
                logger.info(f"Created fallback word: '{segment_text[:30]}...' ({synthetic_word['start']:.2f}s - {synthetic_word['end']:.2f}s)")

    if not all_words:
        logger.error("No words found in any segment - transcription may have failed")
        return []

    subtitles = []
    current_group = []
    current_text = ""

    for i, word_data in enumerate(all_words):
        word = word_data.get('text', '').strip()
        start = word_data.get('start')
        end = word_data.get('end')

        if not word or start is None or end is None:
            # Log the issue
            logger.debug(f"Word at index {i} has invalid data: text='{word}', start={start}, end={end}")

            # Try to recover if word has text but missing timestamps
            if word and current_group:
                # Estimate timestamps based on previous word
                last_word = current_group[-1]
                estimated_start = last_word['end']
                estimated_end = estimated_start + 0.5  # Conservative 0.5s duration

                logger.debug(f"Estimated timestamps for '{word}': {estimated_start:.2f}s - {estimated_end:.2f}s")

                # Create recovered word entry
                word_data = {
                    'text': word,
                    'start': estimated_start,
                    'end': estimated_end
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
            gap = start - last_word['end']
            if gap > max_pause_gap:
                # Long pause - break here
                should_break = True

        if should_break and current_group:
            # Save current group
            group_text = ' '.join(w['text'].strip() for w in current_group)
            group_start = current_group[0]['start']
            group_end = current_group[-1]['end']
            subtitles.append((group_text, group_start, group_end))

            # Reset
            current_group = []
            current_text = ""

        # Add word to current group
        current_group.append(word_data)
        current_text = current_text + ' ' + word if current_text else word

    # Don't forget last group
    if current_group:
        group_text = ' '.join(w['text'].strip() for w in current_group)
        group_start = current_group[0]['start']
        group_end = current_group[-1]['end']
        subtitles.append((group_text, group_start, group_end))

    logger.info(f"Grouped {len(all_words)} words into {len(subtitles)} subtitles")
    return subtitles


def generate_srt(transcription_result: dict, output_srt_path: str, video_duration: float = 0.0):
    """
    Generate SRT file from whisper-timestamped transcription with word-level timestamps.

    Args:
        transcription_result: Dict with 'segments' containing 'words' with timestamps
        output_srt_path: Path to save SRT file
        video_duration: Optional video duration in seconds for comparison
    """
    # Validate input
    if not transcription_result:
        raise ValueError("Transcription result is empty or None")

    segments = transcription_result.get('segments') or []

    if not segments:
        logger.warning("No segments available, creating single subtitle from full text")
        text = transcription_result.get('text', '').strip()
        if text:
            with open(output_srt_path, 'w', encoding='utf-8') as f:
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
        # Track timeline coverage
        seg_start = seg.get('start')
        seg_end = seg.get('end')

        if first_segment_start is None and seg_start is not None:
            first_segment_start = seg_start
        if seg_end is not None:
            last_segment_end = seg_end

        if 'words' in seg and seg['words']:
            segments_with_words += 1
            total_words += len(seg['words'])
        else:
            segments_without_words += 1

    # Log segment coverage
    logger.info(f"  Total words across all segments: {total_words}")
    logger.info(f"  Segments WITH word-level timestamps: {segments_with_words}")
    if segments_without_words > 0:
        logger.warning(f"  Segments WITHOUT word-level timestamps: {segments_without_words} (will use fallback)")

    # Log timeline coverage from segments
    if first_segment_start is not None and last_segment_end is not None:
        segment_duration = last_segment_end - first_segment_start
        logger.info(f"  Segment timeline coverage: {first_segment_start:.2f}s - {last_segment_end:.2f}s ({segment_duration:.2f}s total)")
    else:
        logger.warning(f"  Could not determine segment timeline coverage")

    # Log first segment structure for debugging
    if segments:
        first_seg = segments[0]
        logger.debug(f"First segment keys: {list(first_seg.keys())}")
        logger.debug(f"First segment: text='{first_seg.get('text', '')[:50]}...', start={first_seg.get('start')}, end={first_seg.get('end')}")
        if 'words' in first_seg and first_seg['words']:
            logger.debug(f"First segment has {len(first_seg['words'])} words")
            logger.debug(f"First word: {first_seg['words'][0]}")

    # Group words
    subtitles = group_words_for_subtitles(
        segments,
        max_words=4,
        max_chars=42,
        max_pause_gap=0.5
    )

    # Validate output
    if not subtitles:
        logger.error("❌ No subtitles generated!")
        logger.error("Possible causes:")
        logger.error("  1. No words extracted from segments")
        logger.error("  2. All words had invalid timestamps")
        logger.error("  3. Model doesn't support word-level timestamps")
        logger.error("  4. Transcription produced no segments")
        raise ValueError("Failed to generate subtitles - no valid word timestamps found")

    # Log success metrics
    total_duration = subtitles[-1][2] - subtitles[0][1] if subtitles else 0
    logger.info(f"✓ Generated {len(subtitles)} subtitles")
    logger.info(f"  Duration: {subtitles[0][1]:.2f}s - {subtitles[-1][2]:.2f}s ({total_duration:.2f}s total)")
    logger.info(f"  Average: {total_words / len(subtitles):.1f} words per subtitle")

    # Compare with video duration if available
    if video_duration > 0:
        subtitle_end = subtitles[-1][2] if subtitles else 0
        coverage_percent = (subtitle_end / video_duration * 100) if video_duration > 0 else 0
        gap = video_duration - subtitle_end

        logger.info(f"Video duration comparison:")
        logger.info(f"  Video duration: {video_duration:.2f}s")
        logger.info(f"  Subtitle coverage: {subtitle_end:.2f}s ({coverage_percent:.1f}%)")

        if gap > 1.0:
            logger.warning(f"⚠ COVERAGE GAP: {gap:.2f}s of video NOT covered by subtitles!")
            logger.warning(f"  This means the last {gap:.2f}s of the video has no subtitles")
            logger.warning(f"  Possible causes:")
            logger.warning(f"    1. Silence or music at end (Whisper stops transcribing)")
            logger.warning(f"    2. Audio quality issues in final section")
            logger.warning(f"    3. Speech not detected by Whisper's VAD")
            logger.warning(f"  Solutions:")
            logger.warning(f"    - Check if there's actually speech in the last {gap:.2f}s")
            logger.warning(f"    - Try with a different model (base, small) for better detection")
            logger.warning(f"    - Check audio levels in video editor")
        else:
            logger.info(f"  ✓ Good coverage! Gap is only {gap:.2f}s")

    # Write to SRT file
    with open(output_srt_path, 'w', encoding='utf-8') as f:
        for i, (text, start_time, end_time) in enumerate(subtitles, 1):
            f.write(f"{i}\n")
            f.write(f"{format_timestamp(start_time)} --> {format_timestamp(end_time)}\n")
            f.write(f"{text}\n\n")

    logger.info(f"SRT file generated with {len(subtitles)} subtitles: {output_srt_path}")


def video_to_srt(
    video_path: str,
    output_srt_path: str = None,
    model_id: str = "Oriserve/Whisper-Hindi2Hinglish-Swift",
    device: str = "cuda",
    dtype: torch.dtype = torch.float16
):
    """
    Convert video to SRT subtitle file using whisper-timestamped for word-level alignment.

    Args:
        video_path: Path to input video file
        output_srt_path: Path to save SRT file (optional)
        model_id: Whisper model size (tiny, base, small, medium, large, or HF model ID)
        device: Device to run model on (auto-detects if CUDA unavailable)
        dtype: Data type for model (not used by whisper-timestamped, kept for compatibility)

    Returns:
        str: Path to generated SRT file
    """
    # Automatically detect available device with CPU fallback
    device = get_device(device)

    # Set default output path
    if output_srt_path is None:
        video_name = Path(video_path).stem
        output_srt_path = f"{video_name}.srt"

    # Create temporary audio file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
        temp_audio_path = temp_audio.name

    try:
        # Step 0: Get video duration for comparison
        video_duration = get_video_duration(video_path)

        # Step 1: Extract audio from video
        logger.info(f"Extracting audio from {video_path}")
        if not extract_audio_from_video(video_path, temp_audio_path):
            raise Exception("Failed to extract audio from video")

        # Step 2: Load audio for whisper-timestamped
        logger.info(f"Loading audio for processing")
        audio = whisper.load_audio(temp_audio_path)

        # Log audio duration
        audio_duration = len(audio) / 16000.0  # Sample rate is 16kHz
        logger.info(f"Audio duration: {audio_duration:.2f}s")

        if video_duration > 0:
            audio_diff = abs(audio_duration - video_duration)
            if audio_diff > 0.5:
                logger.warning(f"Audio duration ({audio_duration:.2f}s) differs from video duration ({video_duration:.2f}s) by {audio_diff:.2f}s")
            else:
                logger.info(f"✓ Audio extraction complete ({audio_duration:.2f}s matches video {video_duration:.2f}s)")

        # Step 3: Load model for whisper-timestamped
        logger.info(f"Loading Whisper model: {model_id}")
        # For standard Whisper models, use model_id directly
        # For HuggingFace models, whisper-timestamped may not support them
        # We'll use 'tiny' as default which is fast and works well
        try:
            model = whisper.load_model(model_id, device=device)
        except Exception as e:
            logger.warning(f"Failed to load {model_id}, falling back to 'tiny' model: {e}")
            model = whisper.load_model("tiny", device=device)

        # Step 4: Transcribe with forced alignment for word-level timestamps
        logger.info("Transcribing audio with forced alignment for word-level timestamps...")
        logger.info("VAD filtering: ENABLED (silero) - reduces hallucinations")
        logger.info("Conditioning on previous text: DISABLED - prevents stopping at pauses")
        result = whisper.transcribe(
            model,
            audio,
            language="hi",  # Hindi/Hinglish
            vad=True,  # Enable VAD to reduce hallucinations
            condition_on_previous_text=False,  # CRITICAL: Prevents stopping at gaps/pauses
            remove_empty_words=True,  # Clean up output
            plot_word_alignment=False  # Set True for debugging
        )

        # Validate transcription result
        logger.info(f"Transcription complete")
        logger.info(f"Result keys: {list(result.keys())}")

        segments = result.get('segments', [])
        logger.info(f"Number of segments: {len(segments)}")

        if not segments:
            logger.error("❌ Transcription produced no segments!")
            raise ValueError("Transcription failed - no segments generated")

        # Check if first segment has word-level timestamps
        first_seg = segments[0]
        logger.info(f"First segment keys: {list(first_seg.keys())}")

        if 'words' not in first_seg:
            logger.warning("⚠ Segments do NOT have 'words' key!")
            logger.warning(f"Model '{model_id}' may not support word-level timestamps with whisper-timestamped")
            logger.warning("Will fall back to segment-level timestamps")
        else:
            word_count = len(first_seg.get('words', []))
            logger.info(f"✓ First segment has {word_count} words with timestamps")
            if word_count > 0:
                logger.info(f"  First word: {first_seg['words'][0]}")

        # Log all segment boundaries to identify coverage gaps
        logger.info("Segment timeline:")
        for i, seg in enumerate(segments[:5]):  # Show first 5 segments
            seg_text = seg.get('text', '')[:50]
            logger.info(f"  Segment {i+1}: {seg.get('start', 0):.2f}s - {seg.get('end', 0):.2f}s | '{seg_text}...'")
        if len(segments) > 5:
            logger.info(f"  ... ({len(segments) - 5} more segments)")
            # Show last segment
            last_seg = segments[-1]
            last_seg_text = last_seg.get('text', '')[:50]
            logger.info(f"  Segment {len(segments)}: {last_seg.get('start', 0):.2f}s - {last_seg.get('end', 0):.2f}s | '{last_seg_text}...'")

        # Step 5: Generate SRT file
        logger.info("Generating SRT file...")
        generate_srt(result, output_srt_path, video_duration)

        logger.info(f"✓ SRT file created successfully: {output_srt_path}")
        return output_srt_path

    finally:
        # Cleanup temporary audio file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)


def main():
    """CLI entry point for video-to-SRT conversion"""
    parser = argparse.ArgumentParser(
        description="Convert video to SRT subtitle file with word-level timestamps using whisper-timestamped"
    )
    parser.add_argument(
        "video_path",
        help="Path to input video file"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Path to output SRT file (default: same name as video)"
    )
    parser.add_argument(
        "--model-id",
        default="Oriserve/Whisper-Hindi2Hinglish-Swift",
        help="Whisper model ID (default: Oriserve/Whisper-Hindi2Hinglish-Swift) or size: tiny, base, small, medium, large"
    )
    parser.add_argument(
        "--device",
        default="cuda",
        help="Device to run model on: cuda or cpu (default: cuda)"
    )
    parser.add_argument(
        "--dtype",
        default="float16",
        help="Data type for model (default: float16, kept for compatibility)"
    )

    args = parser.parse_args()

    # Convert dtype string to torch dtype
    dtype = torch_dtype_from_str(args.dtype, args.device)

    # Run conversion
    video_to_srt(
        args.video_path,
        args.output,
        args.model_id,
        args.device,
        dtype
    )

if __name__ == "__main__":
    main()

"""
Media Handler - Abstraction layer for audio/video file processing
Provides unified interface for handling both video and audio media files
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple

from logger import logger


def get_media_type(media_path: str) -> str:
    """
    Determine if media file is video or audio based on file extension

    Args:
        media_path: Path to media file

    Returns:
        str: 'video', 'audio', or 'unknown'
    """
    video_extensions = {
        "mp4",
        "avi",
        "mov",
        "mkv",
        "webm",
        "flv",
        "wmv",
        "m4v",
        "mpg",
        "mpeg",
        "3gp",
        "ts",
        "mts",
    }
    audio_extensions = {
        "mp3",
        "wav",
        "ogg",
        "m4a",
        "flac",
        "aac",
        "wma",
        "opus",
        "aiff",
        "au",
        "ra",
        "amr",
        "caf",
    }

    ext = Path(media_path).suffix.lower().lstrip(".")

    if ext in video_extensions:
        return "video"
    elif ext in audio_extensions:
        return "audio"
    else:
        return "unknown"


def validate_media_file(media_path: str) -> Tuple[bool, str]:
    """
    Validate media file exists and has supported format

    Args:
        media_path: Path to media file

    Returns:
        Tuple[bool, str]: (is_valid, error_message or media_type)
    """
    if not os.path.exists(media_path):
        return False, f"File not found: {media_path}"

    media_type = get_media_type(media_path)

    if media_type == "unknown":
        return False, f"Unsupported file format: {Path(media_path).suffix}"

    return True, media_type


def get_media_duration(media_path: str) -> float:
    """
    Get media duration in seconds using ffprobe
    Works for both video and audio files

    Args:
        media_path: Path to media file

    Returns:
        float: Duration in seconds, or 0.0 if unable to determine
    """
    try:
        command = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            media_path,
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            duration = float(result.stdout.strip())
            media_type = get_media_type(media_path)
            logger.info(f"{media_type.capitalize()} duration: {duration:.2f}s")
            return duration
        else:
            logger.warning(f"Could not determine media duration: {result.stderr}")
            return 0.0

    except Exception as e:
        logger.warning(f"Error getting media duration: {e}")
        return 0.0


def extract_audio_if_needed(
    media_path: str, output_audio_path: Optional[str] = None
) -> str:
    """
    Extract audio from media file if it's a video, otherwise copy as-is

    Args:
        media_path: Path to input media file
        output_audio_path: Path to save audio (optional, auto-generated if None)

    Returns:
        str: Path to audio file

    Raises:
        Exception: If extraction fails
    """
    media_type = get_media_type(media_path)

    # If it's already audio, just return the path (or copy if output specified)
    if media_type == "audio":
        if output_audio_path is None:
            return media_path

        # Copy to specified location
        try:
            import shutil

            shutil.copy2(media_path, output_audio_path)
            logger.info(f"Audio file copied to {output_audio_path}")
            return output_audio_path
        except Exception as e:
            logger.error(f"Error copying audio file: {e}")
            return media_path

    # Extract audio from video
    if output_audio_path is None:
        output_audio_path = media_path.rsplit(".", 1)[0] + "_extracted.wav"

    return extract_audio_from_video(media_path, output_audio_path)


def extract_audio_from_video(video_path: str, output_audio_path: str) -> str:
    """
    Extract audio from video file using ffmpeg

    Args:
        video_path: Path to input video file
        output_audio_path: Path to save extracted audio

    Returns:
        str: Path to extracted audio file

    Raises:
        Exception: If extraction fails
    """
    try:
        command = [
            "ffmpeg",
            "-i",
            video_path,
            "-vn",  # No video
            "-acodec",
            "pcm_s16le",  # 16-bit PCM
            "-ar",
            "16000",  # 16kHz sample rate
            "-ac",
            "1",  # Mono
            "-y",  # Overwrite output file
            output_audio_path,
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            error_msg = result.stderr or "Unknown error"
            logger.error(f"FFmpeg error: {error_msg}")
            raise Exception(f"Failed to extract audio from video: {error_msg}")

        logger.info(f"Audio extracted successfully to {output_audio_path}")
        return output_audio_path

    except FileNotFoundError:
        raise Exception(
            "FFmpeg not found. Please install FFmpeg and ensure it's in your PATH."
        )
    except Exception as e:
        logger.error(f"Error extracting audio: {e}")
        raise


def prepare_audio_for_processing(media_path: str, keep_temporary: bool = True) -> str:
    """
    Prepare audio file for Whisper processing
    - If video: extracts audio
    - If audio: verifies/converts to 16kHz mono PCM
    Returns path to ready-to-use audio file

    Args:
        media_path: Path to media file (video or audio)
        keep_temporary: If True, keeps temporary files (default: True for Whisper processing)

    Returns:
        str: Path to processed audio file ready for Whisper

    Raises:
        Exception: If preparation fails
    """
    media_type = get_media_type(media_path)

    # Validate file
    is_valid, result = validate_media_file(media_path)
    if not is_valid:
        raise Exception(result)

    # For video, extract audio
    if media_type == "video":
        temp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        audio_path = temp_audio.name
        extract_audio_from_video(media_path, audio_path)
        return audio_path

    # For audio, check if conversion is needed
    # Whisper expects 16kHz mono PCM
    try:
        command = [
            "ffprobe",
            "-v",
            "quiet",
            "-show_entries",
            "stream=codec_name,sample_rate,channels",
            "-of",
            "json",
            media_path,
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        # Check if audio needs conversion
        needs_conversion = True

        if result.returncode == 0:
            import json

            try:
                info = json.loads(result.stdout)
                if "streams" in info:
                    for stream in info["streams"]:
                        if stream.get("codec_type") == "audio":
                            codec = stream.get("codec_name", "")
                            sr = int(stream.get("sample_rate", 0))
                            channels = int(stream.get("channels", 0))

                            # Acceptable formats: 16kHz mono PCM
                            if (
                                codec in ["pcm_s16le", "pcm_s16be"]
                                and sr == 16000
                                and channels == 1
                            ):
                                needs_conversion = False
                                logger.info(
                                    "Audio is already in correct format (16kHz mono PCM)"
                                )
                                break
            except (json.JSONDecodeError, ValueError, KeyError):
                pass

        if needs_conversion:
            logger.info("Converting audio to 16kHz mono PCM")
            temp_audio = tempfile.NamedTemporaryFile(
                suffix=".wav", delete=not keep_temporary
            )
            audio_path = temp_audio.name

            command = [
                "ffmpeg",
                "-i",
                media_path,
                "-acodec",
                "pcm_s16le",
                "-ar",
                "16000",
                "-ac",
                "1",
                "-y",
                audio_path,
            ]

            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Failed to convert audio: {result.stderr}")

            logger.info(f"Audio converted to {audio_path}")
            return audio_path
        else:
            # Audio is already in correct format
            return media_path

    except FileNotFoundError:
        raise Exception(
            "FFmpeg not found. Please install FFmpeg and ensure it's in your PATH."
        )
    except Exception as e:
        logger.error(f"Error preparing audio: {e}")
        raise


def cleanup_temp_file(file_path: str):
    """
    Safely remove temporary file

    Args:
        file_path: Path to file to remove
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.warning(f"Could not remove temporary file {file_path}: {e}")

"""
Video Caption Pipeline - Main orchestration module for caption generation, styling, and embedding

This module provides the VideoCaptionPipeline class that coordinates the entire workflow:
1. Create caption sessions from video/audio files
2. Generate SRT captions using Whisper
3. Apply styling presets to captions
4. Generate preview frames (1fps timeline)
5. Embed captions into videos (hard/soft subtitles)

Usage:
    >>> pipeline = VideoCaptionPipeline(sessions_dir="sessions", font_dir="fonts")
    >>> session_id = pipeline.create_caption_session("video.mp4")
    >>> pipeline.apply_caption_style(session_id, preset_name="reels_standard")
    >>> frames = pipeline.generate_caption_preview(session_id, fps=1, max_frames=60)
    >>> output_path = pipeline.embed_captions_to_video(session_id, burn=True)
"""

__all__ = [
    "VideoCaptionPipeline",
    "Caption",
    "PipelineError",
    "extract_frames_at_fps",
    "srt_to_ass",
    "burn_captions_into_video",
    "parse_srt_captions",
]

import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from caption_generator import media_to_srt
from caption_styling import (
    CaptionPreset,
    FontManager,
    PresetManager,
    TextStyle,
)
from logger import logger
from media_handler import (
    get_media_duration,
    get_media_type,
    prepare_audio_for_processing,
)
from session_manager import Session, SessionManager, SessionNotFoundError


class PipelineError(Exception):
    """Base exception for pipeline-related errors."""

    pass


@dataclass
class Caption:
    """
    Represents a single caption/subtitle entry.

    Attributes:
        index: Caption number (starting from 1)
        start_time: Start time in seconds
        end_time: End time in seconds
        text: Caption text content
    """

    index: int
    start_time: float
    end_time: float
    text: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert caption to dictionary."""
        return {
            "index": self.index,
            "start": self.start_time,
            "end": self.end_time,
            "text": self.text,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Caption":
        """Create Caption from dictionary."""
        return cls(
            index=data["index"],
            start_time=data["start"],
            end_time=data["end"],
            text=data["text"],
        )


def parse_srt_time(srt_time: str) -> float:
    """
    Parse SRT timestamp to seconds.

    Args:
        srt_time: SRT timestamp format (HH:MM:SS,mmm)

    Returns:
        Time in seconds as float
    """
    # Parse HH:MM:SS,mmm format
    match = re.match(r"(\d+):(\d+):(\d+),(\d+)", srt_time)
    if not match:
        raise ValueError(f"Invalid SRT timestamp: {srt_time}")

    hours = int(match.group(1))
    minutes = int(match.group(2))
    seconds = int(match.group(3))
    milliseconds = int(match.group(4))

    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000


def parse_srt_captions(srt_path: str) -> List[Caption]:
    """
    Parse SRT file into list of Caption objects.

    Args:
        srt_path: Path to SRT file

    Returns:
        List of Caption objects

    Raises:
        PipelineError: If parsing fails
    """
    captions = []

    try:
        with open(srt_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Split into caption blocks (double newline separator)
        blocks = re.split(r"\n\s*\n", content.strip())

        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) < 3:
                continue

            # Parse index
            try:
                index = int(lines[0].strip())
            except ValueError:
                continue

            # Parse time range
            time_match = re.match(r"(.+?)\s*-->\s*(.+)", lines[1])
            if not time_match:
                continue

            start_time = parse_srt_time(time_match.group(1))
            end_time = parse_srt_time(time_match.group(2))

            # Parse text (may span multiple lines)
            text = "\n".join(lines[2:]).strip()

            captions.append(
                Caption(
                    index=index, start_time=start_time, end_time=end_time, text=text
                )
            )

        logger.info(f"Parsed {len(captions)} captions from {srt_path}")
        return captions

    except Exception as e:
        raise PipelineError(f"Failed to parse SRT file {srt_path}: {e}")


def extract_frames_at_fps(
    video_path: str,
    output_dir: str,
    fps: int = 1,
    width: int = 160,
    max_frames: Optional[int] = None,
) -> List[str]:
    """
    Extract frames from video at specified FPS for timeline preview.

    Uses FFmpeg to extract frames at exactly the specified FPS.
    Frames are saved as JPEG images for efficient web delivery.

    Args:
        video_path: Path to input video file
        output_dir: Directory to save extracted frames
        fps: Frames per second to extract (default 1 for 1fps preview)
        width: Width of thumbnail frames (maintains aspect ratio)
        max_frames: Maximum number of frames to extract (optional)

    Returns:
        List of frame file paths sorted by timestamp

    Raises:
        PipelineError: If frame extraction fails
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Get video duration to limit extraction
    try:
        duration = get_media_duration(video_path)
        # FIX: More robust validation of duration
        if duration is None or not isinstance(duration, (int, float)):
            raise PipelineError(
                f"Could not determine video duration (got: {duration}): {video_path}"
            )
        if duration <= 0:
            raise PipelineError(f"Invalid video duration ({duration}s): {video_path}")
    except PipelineError:
        raise
    except Exception as e:
        raise PipelineError(f"Failed to get video duration: {e}")

    # Calculate frame count
    total_frames = int(duration * fps)
    if max_frames and total_frames > max_frames:
        # Limit to max_frames by adjusting the FPS
        fps = max_frames / duration
        logger.info(
            f"Limiting extraction to {max_frames} frames (adjusted FPS: {fps:.3f})"
        )
        total_frames = max_frames

    logger.info(f"Extracting {total_frames} frames at {fps} fps from {video_path}")

    # FFmpeg command to extract frames
    # -vf "fps={fps},scale={width}:-1" extracts at specified fps and scales to width
    # -q:v 2 sets JPEG quality (2 is high quality, 31 is lowest)
    # frame_%05d.jpg creates sequentially numbered frames
    output_pattern = str(output_path / "frame_%05d.jpg")

    command = [
        "ffmpeg",
        "-i",
        video_path,
        "-vf",
        f"fps={fps},scale={width}:-1",
        "-q:v",
        "2",  # High quality JPEG
        "-y",  # Overwrite output files
        output_pattern,
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        # Collect generated frame files
        frame_files = sorted(output_path.glob("frame_*.jpg"))

        if len(frame_files) == 0:
            raise PipelineError("No frames were extracted")

        logger.info(f"✓ Extracted {len(frame_files)} frames to {output_dir}")
        return [str(f) for f in frame_files]

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or "Unknown error"
        raise PipelineError(f"FFmpeg frame extraction failed: {error_msg}")
    except FileNotFoundError:
        raise PipelineError(
            "FFmpeg not found. Please install FFmpeg and ensure it's in your PATH."
        )
    except Exception as e:
        raise PipelineError(f"Unexpected error during frame extraction: {e}")


def srt_to_ass(
    srt_path: str,
    ass_path: str,
    text_style: TextStyle,
    video_resolution: Tuple[int, int] = (1080, 1920),
) -> None:
    """
    Convert SRT file to ASS (Advanced Substation Alpha) format with styling.

    ASS format allows for advanced styling including fonts, colors, positioning,
    and effects that are compatible with FFmpeg's libass filter.

    Args:
        srt_path: Path to input SRT file
        ass_path: Path to output ASS file
        text_style: TextStyle object with caption styling configuration
        video_resolution: Video resolution as (width, height) for PlayResX/Y

    Raises:
        PipelineError: If conversion fails
    """
    width, height = video_resolution

    # Parse SRT captions
    captions = parse_srt_captions(srt_path)

    if not captions:
        raise PipelineError(f"No captions found in SRT file: {srt_path}")

    # Get ASS style configuration from TextStyle
    ass_style_config = text_style.to_ass_style()

    # Build ASS file header
    ass_content = f"""[Script Info]
Title: Whisper Captions
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: {width}
PlayResY: {height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: {ass_style_config}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    # Add captions
    for caption in captions:
        # Convert times to ASS format (H:MM:SS.cc)
        def format_ass_time(seconds: float) -> str:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            centis = int((seconds % 1) * 100)
            return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"

        # Escape special characters in ASS format
        # ASS uses \\ for line breaks, {\\} for literal braces
        text = (
            caption.text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
        )

        ass_content += f"Dialogue: 0,{format_ass_time(caption.start_time)},{format_ass_time(caption.end_time)},Default,,0,0,0,,{text.upper()}\n"

    # Write ASS file
    try:
        Path(ass_path).parent.mkdir(parents=True, exist_ok=True)
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(ass_content)

        logger.info(f"✓ Converted SRT to ASS: {ass_path}")

    except Exception as e:
        raise PipelineError(f"Failed to write ASS file: {e}")


def burn_captions_into_video(
    video_path: str,
    ass_path: str,
    output_path: str,
    font_dir: str = "fonts",
    progress_callback: Optional[callable] = None,
) -> None:
    """
    Burn captions into video using FFmpeg with libass filter.

    This function hardcodes captions into the video, creating a new video file
    with the captions permanently embedded.

    Args:
        video_path: Path to input video file
        ass_path: Path to ASS subtitle file with styling
        output_path: Path to output video file with burned captions
        font_dir: Directory containing font files for ASS rendering
        progress_callback: Optional callback function(progress_pct) for progress updates

    Raises:
        PipelineError: If burning fails
    """
    # Ensure fonts directory exists
    font_path = Path(font_dir)
    if not font_path.exists():
        font_path.mkdir(parents=True, exist_ok=True)

    # Build FFmpeg command with libass filter
    # -vf "ass=filename.ass[:fontsdir=/path/to/fonts]" applies the ASS subtitles
    # -c:a copy copies audio stream without re-encoding (faster)
    # -c:v libx264 re-encodes video with H.264 codec
    # -preset medium balances speed and quality
    # -crf 23 sets quality (18-28 is good range, lower = better quality)

    # Check if fonts directory has any fonts, otherwise use system fonts
    if font_path.exists() and any(font_path.iterdir()):
        # Use custom fonts directory if it has fonts
        vf_filter = f"ass={ass_path}:fontsdir={font_path.absolute()}"
        logger.info(f"Using custom fonts directory: {font_path.absolute()}")
    else:
        # Use system fonts via fontconfig (omit fontsdir parameter)
        vf_filter = f"ass={ass_path}"
        logger.warning(
            f"Fonts directory is empty or not found: {font_path}, using system fonts"
        )

    command = [
        "ffmpeg",
        "-i",
        video_path,
        "-vf",
        vf_filter,
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "23",
        "-c:a",
        "copy",  # Copy audio without re-encoding
        "-y",  # Overwrite output file
        output_path,
    ]

    logger.info(f"Burning captions into video: {video_path} -> {output_path}")
    logger.info(f"FFmpeg command: {' '.join(command)}")

    try:
        # Run FFmpeg with progress monitoring
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )

        # Parse FFmpeg output for progress
        duration = None
        for line in process.stdout:
            # Try to extract video duration
            if duration is None:
                match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})", line)
                if match:
                    hours = int(match.group(1))
                    minutes = int(match.group(2))
                    seconds = int(match.group(3))
                    centis = int(match.group(4))
                    duration = hours * 3600 + minutes * 60 + seconds + centis / 100

            # Try to extract current time for progress
            if duration:
                match = re.search(r"time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})", line)
                if match:
                    hours = int(match.group(1))
                    minutes = int(match.group(2))
                    seconds = int(match.group(3))
                    centis = int(match.group(4))
                    current_time = hours * 3600 + minutes * 60 + seconds + centis / 100

                    progress_pct = (current_time / duration) * 100
                    if progress_callback:
                        progress_callback(progress_pct)

        # Wait for process to complete
        returncode = process.wait()

        if returncode != 0:
            raise PipelineError(f"FFmpeg exited with code {returncode}")

        # Verify output file exists
        if not Path(output_path).exists():
            raise PipelineError("Output video file was not created")

        logger.info(f"✓ Captions burned successfully: {output_path}")

    except FileNotFoundError:
        raise PipelineError(
            "FFmpeg not found. Please install FFmpeg and ensure it's in your PATH."
        )
    except Exception as e:
        raise PipelineError(f"Failed to burn captions: {e}")


class VideoCaptionPipeline:
    """
    Main pipeline orchestrator for video caption editing and embedding.

    This class provides a high-level API for the complete caption workflow:
    - Create caption sessions from media files
    - Generate SRT captions using Whisper
    - Apply styling presets to captions
    - Generate preview frames for timeline
    - Embed captions into videos (hard or soft subtitles)

    Example:
        >>> pipeline = VideoCaptionPipeline(sessions_dir="sessions", font_dir="fonts")
        >>> session_id = pipeline.create_caption_session("video.mp4")
        >>> pipeline.apply_caption_style(session_id, "reels_standard")
        >>> output = pipeline.embed_captions_to_video(session_id, burn=True)
    """

    def __init__(self, sessions_dir: str = "sessions", font_dir: str = "fonts"):
        """
        Initialize the VideoCaptionPipeline.

        Args:
            sessions_dir: Directory for session storage (default: "sessions")
            font_dir: Directory for font files (default: "fonts")
        """
        # Create font directory if needed
        Path(font_dir).mkdir(parents=True, exist_ok=True)

        # Initialize managers
        self.session_manager = SessionManager(sessions_dir=sessions_dir)
        self.preset_manager = PresetManager()
        self.font_manager = FontManager(fonts_dir=font_dir)

        logger.info(
            f"VideoCaptionPipeline initialized (sessions={sessions_dir}, fonts={font_dir})"
        )

    def create_caption_session(self, media_path: str, model_name: str = "prime") -> str:
        """
        Create a new caption session from media file.

        This method:
        1. Detects media type (video or audio)
        2. Creates a new session via SessionManager
        3. Generates SRT captions using Whisper
        4. Stores session data with caption file path

        Args:
            media_path: Path to input media file (video or audio)
            model_name: Whisper model size (default: "large")

        Returns:
            Session ID (UUID string)

        Raises:
            PipelineError: If session creation or caption generation fails
        """
        # Validate media file
        if not Path(media_path).exists():
            raise PipelineError(f"Media file not found: {media_path}")

        media_type = get_media_type(media_path)
        if media_type == "unknown":
            raise PipelineError(f"Unsupported media format: {media_path}")

        logger.info(f"Creating caption session for {media_type}: {media_path}")

        # Create session
        try:
            session_id = self.session_manager.create_session(video_path=media_path)
            logger.info(f"Created session: {session_id}")
        except Exception as e:
            raise PipelineError(f"Failed to create session: {e}")

        # Generate SRT captions
        try:
            # Generate SRT in session directory
            session_dir = Path(self.session_manager.sessions_dir) / session_id
            session_dir.mkdir(parents=True, exist_ok=True)

            srt_path = session_dir / "captions.srt"

            # Use caption_generator to create SRT
            logger.info(f"Generating captions with model: {model_name}")
            media_to_srt(media_path, str(srt_path), model_id="Oriserve/Whisper-Hindi2Hinglish-Prime")

            # Update session with caption path
            self.session_manager.update_session(
                session_id,
                captions_path=str(srt_path),
                status="transcribed",
                metadata={"media_type": media_type},
            )

            logger.info(f"✓ Caption session created: {session_id}")
            return session_id

        except Exception as e:
            # Update session status to error
            self.session_manager.update_session(session_id, status="error")
            raise PipelineError(f"Failed to generate captions: {e}")

    def apply_caption_style(
        self,
        session_id: str,
        preset_name: Optional[str] = None,
        style_overrides: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Apply caption style to a session.

        This method:
        1. Retrieves the session and preset
        2. Merges style overrides with preset defaults
        3. Updates session with caption_style

        Args:
            session_id: Session ID
            preset_name: Preset name (default: "reels_standard")
            style_overrides: Optional dictionary of style overrides

        Returns:
            True if style was applied successfully

        Raises:
            PipelineError: If session or preset not found
        """
        # Get session
        try:
            session = self.session_manager.get_session_or_raise(session_id)
        except SessionNotFoundError as e:
            raise PipelineError(f"Session not found: {session_id}") from e

        # Get preset (use default if not specified)
        if preset_name is None:
            preset_name = "reels_standard"

        try:
            preset = self.preset_manager.get_preset_or_raise(preset_name)
        except ValueError as e:
            raise PipelineError(f"Preset not found: {preset_name}") from e

        # Apply style overrides if provided
        if style_overrides:
            # Create updated TextStyle from overrides
            style_dict = preset.text_style.to_dict()
            style_dict.update(style_overrides)
            try:
                preset.text_style = TextStyle.from_dict(style_dict)
            except ValueError as e:
                raise PipelineError(f"Invalid style override: {e}") from e

        # Update session with style
        try:
            self.session_manager.update_session(
                session_id,
                caption_style=preset_name,
                metadata={
                    **session.metadata,
                    "text_style": preset.text_style.to_dict(),
                },
            )

            logger.info(f"✓ Applied style '{preset_name}' to session {session_id}")
            return True

        except Exception as e:
            raise PipelineError(f"Failed to apply style: {e}")

    def generate_caption_preview(
        self, session_id: str, fps: int = 1, max_frames: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Generate caption preview frames with timestamp and caption data.

        This method:
        1. Extracts frames from video at specified FPS
        2. Loads captions from SRT file
        3. Determines which caption (if any) should be displayed for each frame
        4. Returns list of frame data with timestamps and captions

        Args:
            session_id: Session ID
            fps: Frames per second to extract (default 1)
            max_frames: Maximum number of frames to extract (default 60)

        Returns:
            List of dictionaries with frame data:
                - timestamp: Frame timestamp in seconds
                - frame_path: Path to frame image
                - caption: Caption text (or None if no caption)

        Raises:
            PipelineError: If preview generation fails
        """
        # Get session
        try:
            session = self.session_manager.get_session_or_raise(session_id)
        except SessionNotFoundError as e:
            raise PipelineError(f"Session not found: {session_id}") from e

        # Check if video exists
        if not Path(session.video_path).exists():
            raise PipelineError(f"Video file not found: {session.video_path}")

        # Check if captions exist
        if not session.captions_path or not Path(session.captions_path).exists():
            raise PipelineError(f"Captions file not found: {session.captions_path}")

        # Create preview directory in session folder
        session_dir = Path(self.session_manager.sessions_dir) / session_id
        preview_dir = session_dir / "preview_frames"

        # Extract frames
        try:
            frame_files = extract_frames_at_fps(
                session.video_path, str(preview_dir), fps=fps, max_frames=max_frames
            )
        except Exception as e:
            raise PipelineError(f"Frame extraction failed: {e}") from e

        # Load captions
        try:
            captions = parse_srt_captions(session.captions_path)
        except Exception as e:
            raise PipelineError(f"Failed to parse captions: {e}") from e

        # Map frames to captions
        preview_data = []
        for idx, frame_path in enumerate(frame_files):
            timestamp = idx / fps  # Frame timestamp based on index and FPS

            # Find active caption at this timestamp
            active_caption = None
            for caption in captions:
                if caption.start_time <= timestamp <= caption.end_time:
                    active_caption = caption.text
                    break

            preview_data.append(
                {
                    "timestamp": timestamp,
                    "frame_path": frame_path,
                    "caption": active_caption,
                }
            )

        logger.info(f"✓ Generated preview for {len(preview_data)} frames")
        return preview_data

    def embed_captions_to_video(
        self, session_id: str, output_path: Optional[str] = None, burn: bool = True
    ) -> str:
        """
        Embed captions into video.

        This method:
        1. Generates ASS subtitle file from SRT with styling
        2. Uses FFmpeg to embed captions (burn or soft)
        3. Saves output video file
        4. Updates session status

        Args:
            session_id: Session ID
            output_path: Output video path (optional, auto-generated if None)
            burn: If True, burn captions into video; if False, add as soft subtitles

        Returns:
            Path to output video file

        Raises:
            PipelineError: If embedding fails
        """
        # Get session
        try:
            session = self.session_manager.get_session_or_raise(session_id)
        except SessionNotFoundError as e:
            raise PipelineError(f"Session not found: {session_id}") from e

        # Check required files
        if not Path(session.video_path).exists():
            raise PipelineError(f"Video file not found: {session.video_path}")

        if not session.captions_path or not Path(session.captions_path).exists():
            raise PipelineError(f"Captions file not found: {session.captions_path}")

        # Update session status
        self.session_manager.update_session(session_id, status="rendering")

        # Generate output path if not provided
        if output_path is None:
            video_path = Path(session.video_path)
            video_name = video_path.stem  # Get video name without extension
            
            # ALWAYS create output directory in ~/Videos/Video-Name/
            videos_dir = Path.home() / "Videos"
            output_dir = videos_dir / video_name
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate output paths
            output_path = str(output_dir / f"{video_name}_captioned.mp4")
            
            logger.info(f"Output directory: {output_dir}")
            logger.info(f"Output path: {output_path}")

        # Get text style from session metadata
        text_style = None
        if session.metadata and "text_style" in session.metadata:
            try:
                text_style = TextStyle.from_dict(session.metadata["text_style"])
            except ValueError:
                # Fall back to default preset
                text_style = self.preset_manager.get_default_preset().text_style
        else:
            # Use default preset
            text_style = self.preset_manager.get_default_preset().text_style

        # Get video resolution
        try:
            # Use ffprobe to get resolution
            command = [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height",
                "-of",
                "csv=s=x:p=0",
                session.video_path,
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            resolution = result.stdout.strip()
            if resolution:
                width, height = map(int, resolution.split("x"))
            else:
                # Default to 1080x1920 (9:16 vertical)
                width, height = 1080, 1920
        except Exception:
            # Default to 1080x1920 (9:16 vertical)
            width, height = 1080, 1920

        # ENHANCEMENT: Scale font size based on video resolution
        # Base resolution is 1080p (1920x1080 or 1080x1920 for vertical)
        # Scale font size proportionally for higher resolutions
        base_resolution = 1080  # Base height for font scaling
        if height > base_resolution:
            font_size_multiplier = height / base_resolution
            # Cap the multiplier to prevent excessively large fonts
            font_size_multiplier = min(font_size_multiplier, 1.5)
            # Apply scaling to text style
            original_font_size = text_style.font_size
            scaled_font_size = int(original_font_size * font_size_multiplier)
            text_style.font_size = scaled_font_size
            logger.info(
                f"Scaling font size from {original_font_size} "
                f"to {scaled_font_size} (multiplier: {font_size_multiplier:.2f})"
            )

        # Create session directory for temporary files
        session_dir = Path(self.session_manager.sessions_dir) / session_id
        ass_path = session_dir / "captions.ass"

        try:
            # Convert SRT to ASS with styling
            srt_to_ass(
                session.captions_path, str(ass_path), text_style, (width, height)
            )

            # Embed captions
            if burn:
                # Burn captions into video
                burn_captions_into_video(
                    session.video_path,
                    str(ass_path),
                    output_path,
                    font_dir=str(
                        self.font_manager.fonts_dir
                    ),  # FIX: Convert Path to str
                )
            else:
                # Soft subtitles (embed as track)
                # This would require different FFmpeg command
                # For now, we'll just burn as that's the primary use case
                logger.warning("Soft subtitles not yet implemented, burning instead")
                burn_captions_into_video(
                    session.video_path,
                    str(ass_path),
                    output_path,
                    font_dir=str(
                        self.font_manager.fonts_dir
                    ),  # FIX: Convert Path to str
                )

            # Update session status
            self.session_manager.update_session(
                session_id,
                status="complete",
                metadata={**session.metadata, "output_path": output_path},
            )

            logger.info(f"✓ Captions embedded successfully: {output_path}")
            # Generate additional outputs: SRT and WAV
            try:
                import shutil
                
                # Extract video name from output path
                output_path_obj = Path(output_path)
                video_name = output_path_obj.stem.replace("_captioned", "")
                output_dir = output_path_obj.parent
                
                # Copy SRT file to output directory
                srt_output = output_dir / f"{video_name}.srt"
                srt_source = Path(self.session_manager.sessions_dir) / session_id / "captions.srt"
                if srt_source.exists() and srt_source != srt_output:
                    shutil.copy2(srt_source, srt_output)
                    logger.info(f"✓ SRT file copied to: {srt_output}")
                
                # Extract WAV audio using FFmpeg
                wav_output = output_dir / f"{video_name}.wav"
                if not wav_output.exists():
                    wav_command = [
                        "ffmpeg",
                        "-i",
                        session.video_path,
                        "-vn",
                        "-acodec",
                        "pcm_s16le",
                        "-ar",
                        "16000",
                        "-ac",
                        "1",
                        "-y",
                        str(wav_output)
                    ]
                    subprocess.run(wav_command, capture_output=True, check=True)
                    logger.info(f"✓ WAV audio extracted to: {wav_output}")
                
                logger.info(f"✓ All outputs generated in: {output_dir}")
            except Exception as e:
                logger.warning(f"Failed to generate additional outputs: {e}")

            logger.info(f"✓ Captions embedded successfully: {output_path}")
            return output_path

        except Exception as e:
            self.session_manager.update_session(session_id, status="error")
            raise PipelineError(f"Failed to embed captions: {e}") from e

    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get session information.

        Args:
            session_id: Session ID

        Returns:
            Dictionary with session information

        Raises:
            PipelineError: If session not found
        """
        try:
            session = self.session_manager.get_session_or_raise(session_id)
            return session.to_dict()
        except SessionNotFoundError as e:
            raise PipelineError(f"Session not found: {session_id}") from e

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and its files.

        Args:
            session_id: Session ID

        Returns:
            True if deleted successfully

        Raises:
            PipelineError: If deletion fails
        """
        try:
            # Get session first to get paths
            session = self.session_manager.get_session(session_id)
            if session is None:
                return False

            # Delete session directory (including all generated files)
            session_dir = Path(self.session_manager.sessions_dir) / session_id
            if session_dir.exists():
                import shutil

                shutil.rmtree(session_dir)

            # Delete session metadata
            return self.session_manager.delete_session(session_id)

        except Exception as e:
            raise PipelineError(f"Failed to delete session: {e}") from e

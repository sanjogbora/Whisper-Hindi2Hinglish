"""
Flask API Server for Media to SRT Conversion and Video Caption Editing
Upload video or audio and get SRT file back
Phase 1: Session-based caption editing with style presets and video embedding

IMPORTANT: Run this server using the conda environment:
    conda activate whisper-hindi
    python web_server.py
"""

import argparse
import hashlib
import json
import logging
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
import uuid as uuid_lib

import torch
from flask import Flask, request, send_file, jsonify, render_template, redirect
from werkzeug.utils import secure_filename
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont

from logger import logger
from media_handler import get_media_type, validate_media_file
from utils import torch_dtype_from_str, get_device
from caption_generator import media_to_srt
from session_manager import SessionManager, SessionNotFoundError, SessionError
from caption_styling import PresetManager, FontManager
from video_caption_pipeline import VideoCaptionPipeline, PipelineError

app = Flask(__name__, template_folder="templates")
CORS(app)  # Enable CORS for all routes


# Custom Jinja filters
@app.template_filter("basename")
def basename_filter(path):
    """Extract the filename from a file path."""
    # FIX: Handle None and empty strings properly
    if not path:
        return ""
    try:
        return str(path).split("/").pop().split("\\").pop()
    except (AttributeError, IndexError):
        return str(path)


# Reduce logging verbosity for end users - only show important messages
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

# Configuration
UPLOAD_FOLDER = str(Path.home() / "Downloads")
ALLOWED_EXTENSIONS = {
    "mp4",
    "avi",
    "mov",
    "mkv",
    "webm",
    "flv",
    "wmv",
    "m4v",  # Video
    "mp3",
    "wav",
    "ogg",
    "m4a",
    "flac",
    "aac",
    "wma",
    "opus",  # Audio
}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

# Global model config
MODEL_CONFIG = {
    "model_id": "Oriserve/Whisper-Hindi2Hinglish-Prime",
    "device": "cuda",
    "dtype": torch.float16,
}

# Global pipeline instance (initialized at startup)
caption_pipeline: Optional[VideoCaptionPipeline] = None


def allowed_file(filename):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    """Enhanced landing page with system status"""
    return render_template("launcher.html")


@app.route("/upload-page")
def upload_page():
    """Original upload interface (for backwards compatibility)"""
    return render_template("upload.html")


@app.route("/api")
def api_info():
    """API documentation"""
    return jsonify(
        {
            "service": "Media to SRT Converter & Video Caption Editor",
            "description": "Upload Hindi-English mixed video or audio and get Roman English SRT subtitles or edit captions with styling",
            "endpoints": {
                "/upload": {
                    "method": "POST",
                    "description": "Upload media file (video or audio)",
                    "parameters": {
                        "media": "Media file (video: mp4, avi, mov, mkv, webm, flv, wmv, m4v | audio: mp3, wav, ogg, m4a, flac, aac, wma, opus)",
                    },
                    "returns": "SRT file download",
                },
                "/health": {"method": "GET", "description": "Check server health"},
                "/api/sessions": {
                    "method": "POST",
                    "description": "Create new caption session",
                    "parameters": {
                        "media_path": "Path to media file",
                    },
                    "returns": "Session information",
                },
                "/api/sessions": {"method": "GET", "description": "List all sessions"},
                "/api/sessions/<id>": {
                    "method": "GET",
                    "description": "Get session details",
                },
                "/api/sessions/<id>/style": {
                    "method": "PUT",
                    "description": "Apply caption style to session",
                },
                "/api/sessions/<id>/preview": {
                    "method": "GET",
                    "description": "Get caption preview frames",
                },
                "/api/sessions/<id>/embed": {
                    "method": "POST",
                    "description": "Embed captions into video",
                },
                "/api/presets": {
                    "method": "GET",
                    "description": "List available presets",
                },
                "/api/presets/<name>": {
                    "method": "GET",
                    "description": "Get preset details",
                },
                "/api/fonts": {"method": "GET", "description": "List available fonts"},
                "/api/sessions/<id>": {
                    "method": "DELETE",
                    "description": "Delete a session",
                },
                # Phase 2: Editor-specific endpoints
                "/editor": {
                    "method": "GET",
                    "description": "Serve the editor page",
                    "parameters": {
                        "session_id": "Optional: Redirect to /editor/{session_id} if provided",
                    },
                    "returns": "Rendered editor.html template",
                },
                "/editor/<session_id>": {
                    "method": "GET",
                    "description": "Serve editor page with specific session",
                    "parameters": {
                        "session_id": "The session ID to edit",
                    },
                    "returns": "Rendered editor.html template with session context",
                },
                "/editor/new": {
                    "method": "GET",
                    "description": "Redirect to create new session workflow",
                    "returns": "Redirects to /upload-page",
                },
                "/sessions": {
                    "method": "GET",
                    "description": "List all sessions for editor access",
                    "parameters": {
                        "status": "Optional: Filter sessions by status",
                        "search": "Optional: Search sessions by session ID",
                    },
                    "returns": "Rendered sessions.html template with session list",
                },
                "/api/editor/upload": {
                    "method": "POST",
                    "description": "Upload media and create session (editor workflow)",
                    "parameters": {
                        "video": "Video or audio file",
                    },
                    "returns": "Session ID and redirect URL to editor",
                },
            },
            "max_file_size": "500MB",
            "supported_formats": list(ALLOWED_EXTENSIONS),
        }
    )


@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "model": MODEL_CONFIG["model_id"]})


@app.route("/api/status")
def system_status():
    """Check system requirements status"""
    import subprocess
    import sys

    status = {
        "python": True,  # If we're running, Python is installed
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "ffmpeg": check_ffmpeg_installed(),
        "dependencies": check_dependencies(),
        "device": get_device_info(),
        "server": True,
    }
    return jsonify(status)


def check_ffmpeg_installed():
    """Check if FFmpeg is installed"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, check=True, timeout=5
        )
        return True
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return False


def check_dependencies():
    """Check if all required dependencies are installed"""
    required = ["flask", "torch", "transformers", "whisper_timestamped"]
    try:
        for module in required:
            __import__(module)
        return True
    except ImportError:
        return False


def is_safe_path(path_str: str, allowed_base_dirs: Optional[list] = None) -> bool:
    """
    Validate that a path is safe (no path traversal attempts).

    Args:
        path_str: Path string to validate
        allowed_base_dirs: List of allowed base directories (optional)

    Returns:
        True if path is safe, False otherwise
    """
    # FIX: Add path traversal validation
    try:
        path = Path(path_str).resolve()
        # Check for suspicious path components
        if ".." in str(path_str) or str(path_str).startswith("~"):
            return False
        # If base directories specified, ensure path is within them
        if allowed_base_dirs:
            for base_dir in allowed_base_dirs:
                try:
                    base = Path(base_dir).resolve()
                    if path.is_relative_to(base):
                        return True
                except (ValueError, OSError):
                    continue
            return False
        return True
    except (OSError, ValueError):
        return False


def is_valid_session_id(session_id: str) -> bool:
    """
    Validate that a session_id is a valid UUID.

    Args:
        session_id: Session ID string to validate

    Returns:
        True if valid UUID format, False otherwise
    """
    try:
        uuid_lib.UUID(session_id)
        return True
    except (ValueError, AttributeError):
        return False


def get_device_info():
    """Get device information for processing"""
    device = MODEL_CONFIG.get("device", "cpu")

    if device == "cuda":
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            return f"CUDA GPU ({gpu_name})"
        else:
            return "CPU (CUDA not available)"
    elif device == "mps":
        return "Apple Silicon (MPS)"
    else:
        return "CPU"


@app.route("/upload", methods=["POST"])
def upload_media():
    """
    Upload media (video or audio) and get SRT file
    """
    # Check if file is present (support both 'video' and 'media' for backward compatibility)
    if "video" not in request.files and "media" not in request.files:
        return jsonify({"error": "No media file provided"}), 400

    file = request.files.get("video") or request.files.get("media")

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify(
            {"error": f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}
        ), 400

    # Save uploaded file
    filename = secure_filename(file.filename)
    media_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(media_path)

    # Validate and detect media type
    is_valid, result = validate_media_file(media_path)
    if not is_valid:
        if os.path.exists(media_path):
            os.remove(media_path)
        return jsonify({"error": result}), 400

    media_type = result
    srt_path = None

    try:
        # Generate SRT file
        logger.info(f"Original filename: {file.filename}")
        logger.info(f"Secured filename: {filename}")
        logger.info(f"Processing {media_type}: {filename}")
        srt_filename = Path(filename).stem + ".srt"
        srt_path = os.path.join(app.config["UPLOAD_FOLDER"], srt_filename)
        logger.info(f"SRT filename: {srt_filename}")
        logger.info(f"SRT path: {srt_path}")

        media_to_srt(
            media_path,
            srt_path,
            MODEL_CONFIG["model_id"],  # Use "large" model
            MODEL_CONFIG["device"],
            MODEL_CONFIG["dtype"],
        )

        # Send SRT file
        return send_file(
            srt_path,
            as_attachment=True,
            download_name=srt_filename,
            mimetype="text/plain",
        )

    except Exception as e:
        logger.error(f"Error processing {media_type}: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        # Cleanup
        if os.path.exists(media_path):
            os.remove(media_path)
        if srt_path and os.path.exists(srt_path):
            # Give time for file to be sent before deletion
            pass


# =============================================================================
# Phase 1 API Endpoints - Caption Editing System
# =============================================================================


def generate_preview_image(session_id: str, timestamp: float):
    """
    Generate a preview image with caption overlay at a specific timestamp.

    Args:
        session_id: Session ID
        timestamp: Timestamp in seconds

    Returns:
        Path to the generated preview image

    Raises:
        PipelineError: If preview generation fails
    """
    # Get session
    session = caption_pipeline.session_manager.get_session_or_raise(session_id)

    # Check if video exists
    if not Path(session.video_path).exists():
        raise PipelineError(f"Video file not found: {session.video_path}")

    # Check if captions exist
    if not session.captions_path or not Path(session.captions_path).exists():
        raise PipelineError(f"Captions file not found: {session.captions_path}")

    # Create preview directory in session folder
    session_dir = Path(caption_pipeline.session_manager.sessions_dir) / session_id
    preview_dir = session_dir / "preview_frames"
    preview_dir.mkdir(parents=True, exist_ok=True)

    # Generate a unique filename for this preview
    import hashlib

    timestamp_str = f"{timestamp:.3f}"
    preview_hash = hashlib.md5(f"{session_id}_{timestamp_str}".encode()).hexdigest()[:8]
    preview_path = preview_dir / f"preview_{preview_hash}.jpg"

    # If preview already exists, return it
    if preview_path.exists():
        return str(preview_path)

    # Extract a single frame at the timestamp
    import tempfile

    temp_frame = preview_dir / f"temp_frame_{preview_hash}.jpg"

    # Use ffmpeg to extract frame at timestamp
    command = [
        "ffmpeg",
        "-ss",
        str(timestamp),
        "-i",
        session.video_path,
        "-vframes",
        "1",
        "-q:v",
        "2",
        "-y",
        str(temp_frame),
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        if not temp_frame.exists():
            raise PipelineError("Failed to extract frame")

        # Load captions to find active caption at timestamp
        from video_caption_pipeline import parse_srt_captions

        captions = parse_srt_captions(session.captions_path)

        # Find caption active at this timestamp
        active_caption = None
        for caption in captions:
            if caption.start_time <= timestamp <= caption.end_time:
                active_caption = caption
                break

        # If there's an active caption, burn it onto the frame
        if active_caption and session.metadata and "text_style" in session.metadata:
            # Open the frame
            img = Image.open(temp_frame)

            # Get style settings
            style = session.metadata["text_style"]
            font_family = style.get("font_family", "Arial")
            font_size = style.get("font_size", 36)
            font_color = style.get("font_color", "#FFFFFF")
            position_x = style.get("position_x", 50)
            position_y = style.get("position_y", 80)
            outline_enabled = style.get("outline_enabled", True)
            outline_width = style.get("outline_width", 2)

            # Convert color from hex to RGB
            font_color_rgb = tuple(
                int(font_color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)
            )
            outline_color = (0, 0, 0)  # Black outline

            # Try to load the font
            try:
                font_path = caption_pipeline.font_manager.get_font_path(font_family)
                font = ImageFont.truetype(font_path, font_size)
            except Exception:
                font = ImageFont.load_default()

            draw = ImageDraw.Draw(img)

            # Get text dimensions
            bbox = draw.textbbox((0, 0), active_caption.text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Calculate position (percentage of image dimensions)
            img_width, img_height = img.size
            x = int((position_x / 100) * img_width) - (text_width // 2)
            y = int((position_y / 100) * img_height)

            # Draw outline if enabled
            if outline_enabled:
                for offset_x in range(-outline_width, outline_width + 1):
                    for offset_y in range(-outline_width, outline_width + 1):
                        if offset_x != 0 or offset_y != 0:
                            draw.text(
                                (x + offset_x, y + offset_y),
                                active_caption.text,
                                font=font,
                                fill=outline_color,
                            )

            # Draw text
            draw.text((x, y), active_caption.text, font=font, fill=font_color_rgb)

            # Save the captioned frame
            img.save(preview_path, "JPEG", quality=95)
        else:
            # No caption at this timestamp, just copy the frame
            temp_frame.rename(preview_path)

        # Clean up temp frame
        if temp_frame.exists():
            temp_frame.unlink()

        logger.info(
            f"✓ Generated preview image at timestamp {timestamp}s: {preview_path}"
        )
        return str(preview_path)

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or "Unknown error"
        raise PipelineError(f"FFmpeg frame extraction failed: {error_msg}")
    except FileNotFoundError:
        raise PipelineError(
            "FFmpeg not found. Please install FFmpeg and ensure it's in your PATH."
        )
    except Exception as e:
        raise PipelineError(f"Unexpected error generating preview: {e}")


def update_captions_data(session_id: str, captions: list):
    """
    Update caption data for a session.

    Args:
        session_id: Session ID
        captions: List of caption dictionaries with index, start, end, text

    Returns:
        Number of captions updated

    Raises:
        PipelineError: If update fails
    """
    # Get session
    session = caption_pipeline.session_manager.get_session_or_raise(session_id)

    if not session.captions_path:
        raise PipelineError("Session has no captions file")

    # Convert caption data to SRT format
    def format_srt_time(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

    srt_content = []
    for cap in captions:
        srt_content.append(str(cap["index"]))
        srt_content.append(
            f"{format_srt_time(cap['start'])} --> {format_srt_time(cap['end'])}"
        )
        srt_content.append(cap["text"])
        srt_content.append("")  # Empty line between captions

    # Write to SRT file
    with open(session.captions_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_content))

    # Update timestamp
    session.update_timestamp()
    caption_pipeline.session_manager._save_session(session)

    logger.info(f"✓ Updated {len(captions)} captions for session {session_id}")
    return len(captions)


def get_render_progress(session_id: str):
    """
    Get rendering progress for a session.

    Args:
        session_id: Session ID

    Returns:
        Dictionary with render progress information

    Raises:
        PipelineError: If status check fails
    """
    # Get session
    session = caption_pipeline.session_manager.get_session_or_raise(session_id)

    # Check session status
    status = session.status

    # Default progress response
    progress_info = {
        "render_id": session_id,
        "status": status,
        "percent": 0,
        "current_frame": 0,
        "total_frames": 0,
        "eta_seconds": None,
        "output_url": None,
    }

    # If session has output video, mark as complete
    if session.metadata and "output_path" in session.metadata:
        output_path = session.metadata["output_path"]
        if Path(output_path).exists():
            progress_info["status"] = "complete"
            progress_info["percent"] = 100
            progress_info["output_url"] = f"/api/video/{session_id}/download"

    # If session is in rendering status, try to get more details
    elif status == "rendering":
        # Check if there's a progress file
        session_dir = Path(caption_pipeline.session_manager.sessions_dir) / session_id
        progress_file = session_dir / "render_progress.json"

        if progress_file.exists():
            import json

            try:
                with open(progress_file, "r") as f:
                    progress_data = json.load(f)
                    progress_info.update(progress_data)
            except Exception as e:
                logger.warning(f"Could not read progress file: {e}")

    elif status in ["created", "transcribed", "editing"]:
        progress_info["status"] = "queued"
        progress_info["percent"] = 0

    elif status == "error":
        progress_info["status"] = "error"
        progress_info["percent"] = 0

    return progress_info


def verify_pipeline_initialized():
    """Verify that the caption pipeline is initialized."""
    global caption_pipeline
    if caption_pipeline is None:
        return jsonify({"error": "Caption pipeline not initialized"}), 500
    return None


@app.route("/api/video/upload", methods=["POST"])
def upload_video():
    """
    Upload video and create caption session.

    Request (multipart/form-data):
        video: Video file

    Response JSON (201):
        {
            "success": true,
            "session_id": "uuid-string",
            "video_info": {
                "filename": "input.mp4",
                "duration": 120.5,
                "resolution": [1080, 1920],
                "fps": 60
            },
            "redirect_url": "/editor?session=uuid-string"
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # Check if file is present
    if "video" not in request.files and "media" not in request.files:
        return jsonify({"error": "No media file provided"}), 400

    file = request.files.get("video") or request.files.get("media")

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify(
            {"error": f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}
        ), 400

    # Save uploaded file
    filename = secure_filename(file.filename)
    media_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(media_path)

    # Validate and detect media type
    is_valid, result = validate_media_file(media_path)
    if not is_valid:
        if os.path.exists(media_path):
            os.remove(media_path)
        return jsonify({"error": result}), 400

    media_type = result
    logger.info(f"Video upload: {filename} ({media_type})")

    try:
        # Create session (uses "large" model by default)
        session_id = caption_pipeline.create_caption_session(media_path=media_path)

        # Get session info
        session = caption_pipeline.session_manager.get_session_or_raise(session_id)

        # Build video info response
        video_info = {
            "filename": filename,
            "path": media_path,
            "media_type": media_type,
        }

        # Add metadata if available
        if session.metadata:
            video_info.update(
                {
                    k: v
                    for k, v in session.metadata.items()
                    if k in ["duration", "resolution", "fps"]
                }
            )

        redirect_url = f"/editor?session={session_id}"

        logger.info(f"✓ Session created from upload: {session_id}")

        return (
            jsonify(
                {
                    "success": True,
                    "session_id": session_id,
                    "video_info": video_info,
                    "redirect_url": redirect_url,
                    "status": session.status,
                    "created_at": session.created_at,
                }
            ),
            201,
        )

    except PipelineError as e:
        logger.error(f"Pipeline error creating session: {e}")
        # Cleanup uploaded file on error
        if os.path.exists(media_path):
            os.remove(media_path)
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        logger.error(f"Unexpected error creating session: {e}")
        # Cleanup uploaded file on error
        if os.path.exists(media_path):
            os.remove(media_path)
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/sessions", methods=["POST"])
def create_session():
    """
    Create a new caption session (legacy endpoint).

    Request JSON:
        {
            "media_path": "/path/to/media.mp4"
        }

    Response JSON (201):
        {
            "session_id": "uuid-string",
            "status": "processing",
            "created_at": "2024-02-11T10:00:00Z"
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # Validate request
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    media_path = data.get("media_path")

    if not media_path:
        return jsonify({"error": "media_path is required"}), 400

    # Validate media file exists
    if not os.path.exists(media_path):
        return jsonify({"error": f"Media file not found: {media_path}"}), 404

    logger.info(f"Creating caption session for: {media_path}")

    try:
        # Create session using pipeline (uses "large" model)
        session_id = caption_pipeline.create_caption_session(media_path=media_path)

        # Get session info
        session = caption_pipeline.session_manager.get_session_or_raise(session_id)

        logger.info(f"✓ Session created: {session_id}")

        return (
            jsonify(
                {
                    "session_id": session_id,
                    "status": session.status,
                    "created_at": session.created_at,
                }
            ),
            201,
        )

    except PipelineError as e:
        logger.error(f"Pipeline error creating session: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error creating session: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/video", methods=["GET"])
def list_videos():
    """
    List all video sessions.

    Response JSON (200):
        {
            "sessions": [
                {
                    "session_id": "uuid-string",
                    "status": "complete",
                    "created_at": "2024-02-11T10:00:00Z"
                },
                ...
            ]
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    try:
        sessions = caption_pipeline.session_manager.list_sessions()
        return jsonify({"sessions": [s.to_dict() for s in sessions]}), 200

    except SessionError as e:
        logger.error(f"Error listing sessions: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error listing sessions: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/sessions", methods=["GET"])
def list_sessions():
    """
    List all sessions (legacy endpoint).

    Response JSON (200):
        {
            "sessions": [
                {
                    "session_id": "uuid-string",
                    "status": "complete",
                    "created_at": "2024-02-11T10:00:00Z"
                },
                ...
            ]
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    try:
        sessions = caption_pipeline.session_manager.list_sessions()
        return jsonify({"sessions": [s.to_dict() for s in sessions]}), 200

    except SessionError as e:
        logger.error(f"Error listing sessions: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error listing sessions: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/video/<session_id>", methods=["GET"])
def get_session(session_id):
    """
    Get session details.

    Response JSON (200):
        {
            "session_id": "uuid-string",
            "video_path": "/path/to/video.mp4",
            "status": "complete",
            "captions_path": "/path/to/captions.srt",
            "caption_style": "reels_standard",
            "metadata": {...},
            "created_at": "2024-02-11T10:00:00Z"
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    try:
        session = caption_pipeline.session_manager.get_session_or_raise(session_id)
        return jsonify(session.to_dict()), 200

    except SessionNotFoundError:
        return jsonify({"error": f"Session not found: {session_id}"}), 404
    except SessionError as e:
        logger.error(f"Error getting session: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error getting session: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/sessions/<session_id>", methods=["GET"])
def get_session_legacy(session_id):
    """
    Get session details (legacy endpoint).

    Response JSON (200):
        {
            "session_id": "uuid-string",
            "video_path": "/path/to/video.mp4",
            "status": "complete",
            "captions_path": "/path/to/captions.srt",
            "caption_style": "reels_standard",
            "metadata": {...},
            "created_at": "2024-02-11T10:00:00Z"
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    try:
        session = caption_pipeline.session_manager.get_session_or_raise(session_id)
        return jsonify(session.to_dict()), 200

    except SessionNotFoundError:
        return jsonify({"error": f"Session not found: {session_id}"}), 404
    except SessionError as e:
        logger.error(f"Error getting session: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error getting session: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/sessions/<session_id>/style", methods=["PUT"])
def apply_session_style(session_id):
    """
    Apply caption style to session (legacy endpoint).

    Request JSON:
        {
            "preset_name": "reels_standard",  # Optional
            "style_overrides": {
                "font_size": 40,
                "color": "#FF0000"
            }  # Optional
        }

    Response JSON (200):
        {
            "success": true,
            "message": "Style applied successfully"
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    preset_name = data.get("preset_name", "reels_standard")
    style_overrides = data.get("style_overrides")

    logger.info(f"Applying style '{preset_name}' to session: {session_id}")

    try:
        caption_pipeline.apply_caption_style(
            session_id=session_id,
            preset_name=preset_name,
            style_overrides=style_overrides,
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Style '{preset_name}' applied successfully",
                }
            ),
            200,
        )

    except PipelineError as e:
        logger.error(f"Pipeline error applying style: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error applying style: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/video/<session_id>/preview", methods=["GET"])
def get_video_preview(session_id):
    """
    Get caption preview frames.

    Query parameters:
        fps=1 (default)
        max_frames=60 (default)

    Response JSON (200):
        {
            "session_id": "uuid-string",
            "fps": 1,
            "frames": [
                {
                    "timestamp": 0.0,
                    "frame_path": "/sessions/uuid/preview_frames/frame_00001.jpg",
                    "caption": "Caption text"
                },
                ...
            ]
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # Get query parameters
    fps = request.args.get("fps", 1, type=int)
    max_frames = request.args.get("max_frames", 60, type=int)

    # Validate parameters
    if fps <= 0:
        return jsonify({"error": "fps must be positive"}), 400
    if max_frames <= 0:
        return jsonify({"error": "max_frames must be positive"}), 400

    logger.info(
        f"Generating preview for session: {session_id} (fps={fps}, max_frames={max_frames})"
    )

    try:
        preview_data = caption_pipeline.generate_caption_preview(
            session_id=session_id, fps=fps, max_frames=max_frames
        )

        return (
            jsonify(
                {
                    "session_id": session_id,
                    "fps": fps,
                    "frames": preview_data,
                }
            ),
            200,
        )

    except PipelineError as e:
        logger.error(f"Pipeline error generating preview: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error generating preview: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/sessions/<session_id>/preview", methods=["GET"])
def get_session_preview(session_id):
    """
    Get caption preview frames (legacy endpoint).

    Query parameters:
        fps=1 (default)
        max_frames=60 (default)

    Response JSON (200):
        {
            "session_id": "uuid-string",
            "fps": 1,
            "frames": [
                {
                    "timestamp": 0.0,
                    "frame_path": "/sessions/uuid/preview_frames/frame_00001.jpg",
                    "caption": "Caption text"
                },
                ...
            ]
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # Get query parameters
    fps = request.args.get("fps", 1, type=int)
    max_frames = request.args.get("max_frames", 60, type=int)

    # Validate parameters
    if fps <= 0:
        return jsonify({"error": "fps must be positive"}), 400
    if max_frames <= 0:
        return jsonify({"error": "max_frames must be positive"}), 400

    logger.info(
        f"Generating preview for session: {session_id} (fps={fps}, max_frames={max_frames})"
    )

    try:
        preview_data = caption_pipeline.generate_caption_preview(
            session_id=session_id, fps=fps, max_frames=max_frames
        )

        return (
            jsonify(
                {
                    "session_id": session_id,
                    "fps": fps,
                    "frames": preview_data,
                }
            ),
            200,
        )

    except PipelineError as e:
        logger.error(f"Pipeline error generating preview: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error generating preview: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/video/<session_id>/preview/frame", methods=["GET"])
def get_video_preview_frame(session_id):
    """
    Get a single captioned preview frame at a specific timestamp.

    Query parameters:
        t: Timestamp in seconds (float, required)

    Response:
        Binary image data (JPEG) with caption overlay
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # Get timestamp parameter
    timestamp = request.args.get("t", type=float)
    if timestamp is None:
        return jsonify({"error": "Timestamp parameter 't' is required"}), 400

    if timestamp < 0:
        return jsonify({"error": "Timestamp must be non-negative"}), 400

    logger.info(f"Generating preview frame for session: {session_id} at t={timestamp}s")

    try:
        # Generate preview image with caption overlay
        preview_path = generate_preview_image(session_id, timestamp)

        if not Path(preview_path).exists():
            return jsonify({"error": "Failed to generate preview frame"}), 500

        # Return the image
        return send_file(preview_path, mimetype="image/jpeg")

    except PipelineError as e:
        logger.error(f"Pipeline error generating preview frame: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error generating preview frame: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/sessions/<session_id>/embed", methods=["POST"])
def embed_session_captions(session_id):
    """
    Embed captions into video (legacy endpoint).

    Request JSON:
        {
            "output_path": "/path/to/output.mp4",  # Optional
            "burn": true  # Optional, default: true
        }

    Response JSON (200):
        {
            "session_id": "uuid-string",
            "output_path": "/path/to/output.mp4",
            "status": "complete"
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    output_path = data.get("output_path")
    burn = data.get("burn", True)

    logger.info(f"Embedding captions for session: {session_id} (burn={burn})")

    try:
        output = caption_pipeline.embed_captions_to_video(
            session_id=session_id, output_path=output_path, burn=burn
        )

        # Get updated session status
        session = caption_pipeline.session_manager.get_session_or_raise(session_id)

        return (
            jsonify(
                {
                    "session_id": session_id,
                    "output_path": output,
                    "status": session.status,
                }
            ),
            200,
        )

    except PipelineError as e:
        logger.error(f"Pipeline error embedding captions: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error embedding captions: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/video/<session_id>/style", methods=["GET"])
def get_video_style(session_id):
    """
    Get caption style for a video session.

    Response JSON (200):
        {
            "preset": "reels_standard",
            "font_family": "Roboto Bold",
            "font_size": 36,
            "font_color": "#FFFFFF",
            "position_x": 50,
            "position_y": 80
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # Validate session_id format
    if not is_valid_session_id(session_id):
        return jsonify({"error": "Invalid session ID format"}), 400

    try:
        session = caption_pipeline.session_manager.get_session_or_raise(session_id)

        # Get style from metadata
        style = {"preset": session.caption_style}
        if session.metadata and "text_style" in session.metadata:
            style.update(session.metadata["text_style"])

        return jsonify(style), 200

    except SessionNotFoundError:
        return jsonify({"error": f"Session not found: {session_id}"}), 404
    except Exception as e:
        logger.error(f"Error getting style: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/video/<session_id>/style", methods=["POST"])
def update_video_style(session_id):
    """
    Update caption style for a video session.

    Request JSON:
        {
            "style": {
                "preset": "custom",
                "font_family": "Roboto Bold",
                "font_size": 40,
                "font_color": "#FFFF00",
                "position_x": 50,
                "position_y": 85,
                "outline_enabled": true,
                "outline_width": 3
            }
        }

    Response JSON (200):
        {
            "success": true,
            "preview_url": "/api/video/preview-frame/{session_id}?t=5&style_hash=abc123"
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # Validate session_id format
    if not is_valid_session_id(session_id):
        return jsonify({"error": "Invalid session ID format"}), 400

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    style_data = data.get("style", {})

    logger.info(f"Updating style for session: {session_id}")

    try:
        # Get session
        session = caption_pipeline.session_manager.get_session_or_raise(session_id)

        # Update session style
        preset_name = style_data.get("preset", "custom")
        style_overrides = {k: v for k, v in style_data.items() if k != "preset"}

        caption_pipeline.apply_caption_style(
            session_id=session_id,
            preset_name=preset_name,
            style_overrides=style_overrides,
        )

        # Generate preview URL
        import hashlib

        style_hash = hashlib.md5(str(style_data).encode()).hexdigest()[:8]
        preview_url = (
            f"/api/video/{session_id}/preview/frame?t=5&style_hash={style_hash}"
        )

        return (
            jsonify({"success": True, "preview_url": preview_url}),
            200,
        )

    except PipelineError as e:
        logger.error(f"Pipeline error updating style: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error updating style: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/presets", methods=["GET"])
def list_presets():
    """
    List available presets.

    Response JSON (200):
        {
            "presets": [
                {
                    "name": "Reels Standard",
                    "description": "Optimized for Instagram Reels",
                    "id": "reels_standard",
                    "category": "social"
                },
                ...
            ]
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    try:
        presets = caption_pipeline.preset_manager.list_presets()

        return (
            jsonify(
                {
                    "presets": [
                        {
                            "id": preset_id,
                            "name": preset.name,
                            "description": preset.description,
                            "category": preset.category,
                            "target_aspect_ratio": preset.target_aspect_ratio,
                        }
                        for preset_id, preset in caption_pipeline.preset_manager._get_all_presets().items()
                    ]
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Unexpected error listing presets: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/presets/<preset_name>", methods=["GET"])
def get_preset(preset_name):
    """
    Get preset details.

    Response JSON (200):
        {
            "name": "reels_standard",
            "description": "Reels/Shorts preset",
            "text_style": {
                "font_family": "Roboto Bold",
                "font_size": 36,
                "color": "#FFFFFF",
                ...
            }
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    try:
        preset = caption_pipeline.preset_manager.get_preset_or_raise(preset_name)

        return jsonify(
            {
                "id": preset_name,
                "name": preset.name,
                "description": preset.description,
                "category": preset.category,
                "target_aspect_ratio": preset.target_aspect_ratio,
                "text_style": preset.text_style.to_dict(),
            }
        ), 200

    except ValueError:
        return jsonify({"error": f"Preset not found: {preset_name}"}), 404
    except Exception as e:
        logger.error(f"Unexpected error getting preset: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/fonts", methods=["GET"])
def list_fonts():
    """
    List available fonts.

    Response JSON (200):
        {
            "fonts": [
                {
                    "id": "roboto_bold",
                    "name": "Roboto Bold",
                    "file": "Roboto-Bold.ttf"
                },
                ...
            ]
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    try:
        fonts = caption_pipeline.font_manager.get_available_fonts()

        return jsonify({"fonts": fonts}), 200

    except OSError as e:
        logger.error(f"Error listing fonts: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error listing fonts: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/sessions/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    """
    Delete a session.

    Response JSON (200):
        {
            "success": true,
            "message": "Session deleted"
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # FIX: Validate session_id format
    if not is_valid_session_id(session_id):
        return jsonify({"error": "Invalid session ID format"}), 400

    logger.info(f"Deleting session: {session_id}")

    try:
        success = caption_pipeline.delete_session(session_id)

        if success:
            return (
                jsonify(
                    {
                        "success": True,
                        "message": f"Session {session_id} deleted successfully",
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Session {session_id} not found",
                    }
                ),
                404,
            )

    except PipelineError as e:
        logger.error(f"Pipeline error deleting session: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error deleting session: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# =============================================================================
# Additional Endpoints for Frontend Integration
# =============================================================================


@app.route("/api/sessions/<session_id>/captions", methods=["GET"])
def get_session_captions(session_id):
    """
    Get captions for a session (legacy endpoint, parsed from SRT file).

    Response JSON (200):
        {
            "session_id": "uuid-string",
            "captions": [
                {"index": 1, "start": 0.0, "end": 2.5, "text": "Caption text"},
                ...
            ],
            "style": {...}
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # FIX: Validate session_id format
    if not is_valid_session_id(session_id):
        return jsonify({"error": "Invalid session ID format"}), 400

    try:
        session = caption_pipeline.session_manager.get_session_or_raise(session_id)

        # Parse captions from SRT file
        from video_caption_pipeline import parse_srt_captions

        captions = []
        if session.captions_path and Path(session.captions_path).exists():
            captions = [c.to_dict() for c in parse_srt_captions(session.captions_path)]

        # Get style from metadata
        style = {}
        if session.metadata and "text_style" in session.metadata:
            style = session.metadata["text_style"]

        return jsonify(
            {"session_id": session_id, "captions": captions, "style": style}
        ), 200

    except SessionNotFoundError:
        return jsonify({"error": f"Session not found: {session_id}"}), 404
    except Exception as e:
        logger.error(f"Error getting captions: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/video/<session_id>/captions", methods=["GET"])
def get_video_captions(session_id):
    """
    Get captions for a video session.

    Response JSON (200):
        {
            "captions": [
                {
                    "index": 1,
                    "start": 0.2,
                    "end": 1.36,
                    "text": "Kal mainne kaha tha"
                },
                {
                    "index": 2,
                    "start": 1.36,
                    "end": 3.16,
                    "text": "wealth hustle se nahin"
                }
            ],
            "style": {
                "preset": "reels_standard",
                "font_family": "Roboto Bold",
                "font_size": 36,
                "font_color": "#FFFFFF",
                "position_x": 50,
                "position_y": 80
            }
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # Validate session_id format
    if not is_valid_session_id(session_id):
        return jsonify({"error": "Invalid session ID format"}), 400

    try:
        session = caption_pipeline.session_manager.get_session_or_raise(session_id)

        # Parse captions from SRT file
        from video_caption_pipeline import parse_srt_captions

        captions = []
        if session.captions_path and Path(session.captions_path).exists():
            captions = [c.to_dict() for c in parse_srt_captions(session.captions_path)]

        # Get style from metadata
        style = {}
        if session.metadata and "text_style" in session.metadata:
            style = session.metadata["text_style"]
            style["preset"] = session.caption_style

        return jsonify({"captions": captions, "style": style}), 200

    except SessionNotFoundError:
        return jsonify({"error": f"Session not found: {session_id}"}), 404
    except Exception as e:
        logger.error(f"Error getting captions: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/sessions/<session_id>/captions", methods=["PUT"])
def update_session_captions(session_id):
    """
    Update captions for a session (legacy endpoint, regenerates SRT file).

    Request JSON:
        {
            "captions": [
                {"index": 1, "start": 0.0, "end": 2.5, "text": "Caption text"},
                ...
            ]
        }

    Response JSON (200):
        {
            "success": true,
            "message": "Captions updated"
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # FIX: Validate session_id format
    if not is_valid_session_id(session_id):
        return jsonify({"error": "Invalid session ID format"}), 400

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    captions_data = data.get("captions", [])

    try:
        session = caption_pipeline.session_manager.get_session_or_raise(session_id)

        if not session.captions_path:
            return jsonify({"error": "Session has no captions file"}), 400

        # Convert caption data to SRT format
        def format_srt_time(seconds):
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            ms = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

        srt_content = []
        for cap in captions_data:
            srt_content.append(str(cap["index"]))
            srt_content.append(
                f"{format_srt_time(cap['start'])} --> {format_srt_time(cap['end'])}"
            )
            srt_content.append(cap["text"])
            srt_content.append("")  # Empty line between captions

        # Write to SRT file
        with open(session.captions_path, "w", encoding="utf-8") as f:
            f.write("\n".join(srt_content))

        # Update timestamp
        session.update_timestamp()
        caption_pipeline.session_manager._save_session(session)

        logger.info(f"✓ Updated {len(captions_data)} captions for session {session_id}")

        return jsonify(
            {"success": True, "message": f"Updated {len(captions_data)} captions"}
        ), 200

    except SessionNotFoundError:
        return jsonify({"error": f"Session not found: {session_id}"}), 404
    except Exception as e:
        logger.error(f"Error updating captions: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/video/<session_id>/captions", methods=["PUT"])
def update_video_captions(session_id):
    """
    Update captions for a video session.

    Request JSON:
        {
            "captions": [
                {
                    "index": 1,
                    "start": 0.2,
                    "end": 1.36,
                    "text": "Modified caption text"
                }
            ]
        }

    Response JSON (200):
        {
            "success": true,
            "updated_count": 1
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # Validate session_id format
    if not is_valid_session_id(session_id):
        return jsonify({"error": "Invalid session ID format"}), 400

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    captions_data = data.get("captions", [])

    try:
        # Use the helper function to update captions
        updated_count = update_captions_data(session_id, captions_data)

        return jsonify({"success": True, "updated_count": updated_count}), 200

    except SessionNotFoundError:
        return jsonify({"error": f"Session not found: {session_id}"}), 404
    except Exception as e:
        logger.error(f"Error updating captions: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/sessions/<session_id>/download", methods=["GET"])
def download_session_video(session_id):
    """
    Download the output video with embedded captions (legacy endpoint).

    Query parameters:
        path (optional): Output file path (uses session metadata if not provided)

    Returns:
        Video file download
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # FIX: Validate session_id format
    if not is_valid_session_id(session_id):
        return jsonify({"error": "Invalid session ID format"}), 400

    try:
        session = caption_pipeline.session_manager.get_session_or_raise(session_id)

        # Get output path from query or session metadata
        output_path = request.args.get("path")
        if not output_path and session.metadata and "output_path" in session.metadata:
            output_path = session.metadata["output_path"]

        if not output_path:
            return jsonify({"error": "No output video available for this session"}), 404

        if not Path(output_path).exists():
            return jsonify({"error": "Output video file not found"}), 404

        # Extract filename for download
        filename = Path(output_path).name

        return send_file(
            output_path,
            as_attachment=True,
            download_name=filename,
            mimetype="video/mp4",
        )

    except SessionNotFoundError:
        return jsonify({"error": f"Session not found: {session_id}"}), 404
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/video/<session_id>/render", methods=["POST"])
def render_video(session_id):
    """
    Render video with embedded captions.

    Request JSON:
        {
            "quality": "high" | "medium" | "low" (optional, default: "high")
        }

    Response JSON (200):
        {
            "success": true,
            "render_id": "render-uuid",
            "status": "queued",
            "estimated_time": 45
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # Validate session_id format
    if not is_valid_session_id(session_id):
        return jsonify({"error": "Invalid session ID format"}), 400

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    quality = data.get("quality", "high")

    logger.info(f"Rendering video for session: {session_id} (quality={quality})")

    try:
        session = caption_pipeline.session_manager.get_session_or_raise(session_id)

        # Start rendering in background
        output = caption_pipeline.embed_captions_to_video(
            session_id=session_id, burn=True
        )

        # Generate render ID (same as session_id for now)
        render_id = session_id

        # Estimate time based on video duration
        estimated_time = 30  # Default 30 seconds
        if session.metadata and "duration" in session.metadata:
            estimated_time = int(session.metadata["duration"] * 0.5)  # Rough estimate

        return (
            jsonify(
                {
                    "success": True,
                    "render_id": render_id,
                    "status": "queued",
                    "estimated_time": estimated_time,
                }
            ),
            200,
        )

    except PipelineError as e:
        logger.error(f"Pipeline error rendering video: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error rendering video: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/video/<session_id>/render/progress", methods=["GET"])
def get_render_progress_endpoint(session_id):
    """
    Get render progress for a video session.

    Response JSON (200):
        {
            "render_id": "render-uuid",
            "status": "rendering",  // queued, rendering, complete, error
            "percent": 65,
            "current_frame": 4500,
            "total_frames": 7200,
            "eta_seconds": 18,
            "output_url": null  // populated when complete
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # Validate session_id format
    if not is_valid_session_id(session_id):
        return jsonify({"error": "Invalid session ID format"}), 400

    try:
        # Use helper function to get progress
        progress_info = get_render_progress(session_id)

        return jsonify(progress_info), 200

    except SessionNotFoundError:
        return jsonify({"error": f"Session not found: {session_id}"}), 404
    except Exception as e:
        logger.error(f"Error getting render progress: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/video/<session_id>/download", methods=["GET"])
def download_rendered_video(session_id):
    """
    Download the rendered video with embedded captions.

    Response:
        Video file download with Content-Type: video/mp4
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # Validate session_id format
    if not is_valid_session_id(session_id):
        return jsonify({"error": "Invalid session ID format"}), 400

    try:
        session = caption_pipeline.session_manager.get_session_or_raise(session_id)

        # Get output path from session metadata
        output_path = None
        if session.metadata and "output_path" in session.metadata:
            output_path = session.metadata["output_path"]

        if not output_path:
            return jsonify(
                {"error": "No rendered video available for this session"}
            ), 404

        if not Path(output_path).exists():
            return jsonify({"error": "Rendered video file not found"}), 404

        # Extract filename for download
        filename = f"video_with_captions_{session_id}.mp4"

        return send_file(
            output_path,
            as_attachment=True,
            download_name=filename,
            mimetype="video/mp4",
        )

    except SessionNotFoundError:
        return jsonify({"error": f"Session not found: {session_id}"}), 404
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/sessions/<session_id>/video", methods=["GET"])
def serve_session_video(session_id):
    """
    Serve the original video file for a session (legacy endpoint).

    Returns:
        Video file stream for playback
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # FIX: Validate session_id format
    if not is_valid_session_id(session_id):
        return jsonify({"error": "Invalid session ID format"}), 400

    try:
        session = caption_pipeline.session_manager.get_session_or_raise(session_id)

        if not session.video_path:
            return jsonify({"error": "Session has no video file"}), 404

        if not Path(session.video_path).exists():
            return jsonify({"error": "Video file not found"}), 404

        # FIX: Add security check - ensure video path is safe
        if not is_safe_path(session.video_path, [app.config["UPLOAD_FOLDER"]]):
            logger.warning(
                f"Attempted to access unauthorized video path: {session.video_path}"
            )
            return jsonify({"error": "Unauthorized file access"}), 403

        filename = Path(session.video_path).name
        return send_file(session.video_path, mimetype="video/mp4", as_attachment=False)

    except SessionNotFoundError:
        return jsonify({"error": f"Session not found: {session_id}"}), 404
    except Exception as e:
        logger.error(f"Error serving video: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/video/<session_id>/preview/video", methods=["GET"])
def serve_video_preview_stream(session_id):
    """
    Serve the original video file for preview streaming.

    Returns:
        Video file stream for playback
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # Validate session_id format
    if not is_valid_session_id(session_id):
        return jsonify({"error": "Invalid session ID format"}), 400

    try:
        session = caption_pipeline.session_manager.get_session_or_raise(session_id)

        if not session.video_path:
            return jsonify({"error": "Session has no video file"}), 404

        if not Path(session.video_path).exists():
            return jsonify({"error": "Video file not found"}), 404

        # Add security check
        if not is_safe_path(session.video_path, [app.config["UPLOAD_FOLDER"]]):
            logger.warning(
                f"Attempted to access unauthorized video path: {session.video_path}"
            )
            return jsonify({"error": "Unauthorized file access"}), 403

        filename = Path(session.video_path).name
        return send_file(session.video_path, mimetype="video/mp4", as_attachment=False)

    except SessionNotFoundError:
        return jsonify({"error": f"Session not found: {session_id}"}), 404
    except Exception as e:
        logger.error(f"Error serving video: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/video/<session_id>/frames", methods=["GET"])
def get_video_frames(session_id):
    """
    Get list of preview frame URLs for a video session.

    Response JSON (200):
        {
            "frames": [
                {
                    "timestamp": 0,
                    "url": "/api/video/preview-frame/{session_id}?t=0",
                    "has_caption": true
                },
                ...
            ],
            "total_frames": 121,
            "video_url": "/api/video/preview/video/{session_id}"
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # Validate session_id format
    if not is_valid_session_id(session_id):
        return jsonify({"error": "Invalid session ID format"}), 400

    try:
        # Get preview data
        preview_data = caption_pipeline.generate_caption_preview(
            session_id=session_id, fps=1, max_frames=60
        )

        # Transform to expected format
        frames = []
        for frame in preview_data:
            frames.append(
                {
                    "timestamp": frame["timestamp"],
                    "url": f"/api/video/{session_id}/preview/frame?t={frame['timestamp']}",
                    "has_caption": frame["caption"] is not None,
                }
            )

        # Get total frames if available
        total_frames = len(frames)
        if session := caption_pipeline.session_manager.get_session(session_id):
            if session.metadata and "duration" in session.metadata:
                total_frames = int(session.metadata["duration"])

        return jsonify(
            {
                "frames": frames,
                "total_frames": total_frames,
                "video_url": f"/api/video/{session_id}/preview/video",
            }
        ), 200

    except SessionNotFoundError:
        return jsonify({"error": f"Session not found: {session_id}"}), 404
    except Exception as e:
        logger.error(f"Error getting frames: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/video/<session_id>", methods=["DELETE"])
def delete_video_session(session_id):
    """
    Delete a video session.

    Response JSON (200):
        {
            "success": true,
            "message": "Session deleted"
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # Validate session_id format
    if not is_valid_session_id(session_id):
        return jsonify({"error": "Invalid session ID format"}), 400

    logger.info(f"Deleting session: {session_id}")

    try:
        success = caption_pipeline.delete_session(session_id)

        if success:
            return (
                jsonify(
                    {
                        "success": True,
                        "message": f"Session {session_id} deleted successfully",
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Session {session_id} not found",
                    }
                ),
                404,
            )

    except PipelineError as e:
        logger.error(f"Pipeline error deleting session: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error deleting session: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/video/<session_id>/reset", methods=["POST"])
def reset_video_session(session_id):
    """
    Reset a video session to initial state.

    Response JSON (200):
        {
            "success": true,
            "message": "Session reset"
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # Validate session_id format
    if not is_valid_session_id(session_id):
        return jsonify({"error": "Invalid session ID format"}), 400

    logger.info(f"Resetting session: {session_id}")

    try:
        session = caption_pipeline.session_manager.get_session_or_raise(session_id)

        # Reset status and clear output
        session.status = "transcribed"
        if session.metadata:
            session.metadata.pop("output_path", None)

        session.update_timestamp()
        caption_pipeline.session_manager._save_session(session)

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Session {session_id} reset successfully",
                }
            ),
            200,
        )

    except SessionNotFoundError:
        return jsonify({"error": f"Session not found: {session_id}"}), 404
    except Exception as e:
        logger.error(f"Error resetting session: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/video/styles", methods=["GET"])
def list_video_styles():
    """
    List all available style presets.

    Response JSON (200):
        {
            "presets": [
                {
                    "id": "reels_standard",
                    "name": "Reels Standard",
                    "description": "Optimized for Instagram Reels",
                    "thumbnail": "/static/presets/reels_standard.jpg"
                },
                {
                    "id": "minimal_clean",
                    "name": "Minimal Clean",
                    "description": "Clean look with background",
                    "thumbnail": "/static/presets/minimal_clean.jpg"
                }
            ]
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    try:
        presets = caption_pipeline.preset_manager.list_presets()

        return (
            jsonify(
                {
                    "presets": [
                        {
                            "id": preset_id,
                            "name": preset.name,
                            "description": preset.description,
                            "thumbnail": f"/static/presets/{preset_id}.jpg",
                        }
                        for preset_id, preset in caption_pipeline.preset_manager._get_all_presets().items()
                    ]
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Unexpected error listing presets: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/styles/presets", methods=["GET"])
def list_style_presets():
    """
    List all available style presets (roadmap endpoint).

    Response JSON (200):
        {
            "presets": [
                {
                    "id": "reels_standard",
                    "name": "Reels Standard",
                    "description": "Optimized for Instagram Reels",
                    "thumbnail": "/static/presets/reels_standard.jpg"
                },
                {
                    "id": "minimal_clean",
                    "name": "Minimal Clean",
                    "description": "Clean look with background",
                    "thumbnail": "/static/presets/minimal_clean.jpg"
                }
            ]
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    try:
        presets = caption_pipeline.preset_manager.list_presets()

        return (
            jsonify(
                {
                    "presets": [
                        {
                            "id": preset_id,
                            "name": preset.name,
                            "description": preset.description,
                            "thumbnail": f"/static/presets/{preset_id}.jpg",
                        }
                        for preset_id, preset in caption_pipeline.preset_manager._get_all_presets().items()
                    ]
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Unexpected error listing presets: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/styles/presets/<preset_id>", methods=["GET"])
def get_style_preset(preset_id):
    """
    Get a specific style preset.

    Response JSON (200):
        {
            "id": "reels_standard",
            "name": "Reels Standard",
            "config": {
                "font_family": "Roboto Bold",
                "font_size": 36,
                "font_color": "#FFFFFF",
                "position_x": 50,
                "position_y": 80
            }
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    try:
        preset = caption_pipeline.preset_manager.get_preset_or_raise(preset_id)

        return jsonify(
            {
                "id": preset_id,
                "name": preset.name,
                "description": preset.description,
                "category": preset.category,
                "target_aspect_ratio": preset.target_aspect_ratio,
                "config": preset.text_style.to_dict(),
            }
        ), 200

    except ValueError:
        return jsonify({"error": f"Preset not found: {preset_id}"}), 404
    except Exception as e:
        logger.error(f"Unexpected error getting preset: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# =============================================================================
# End of Phase 1 API Endpoints
# =============================================================================


# =============================================================================
# Phase 2: Editor-Specific Routes
# =============================================================================


@app.route("/editor")
def editor_page():
    """
    Serve the editor page.

    Query parameters:
        session_id (optional): If provided, redirect to /editor/{session_id}

    Returns:
        Rendered editor.html template
    """
    session_id = request.args.get("session_id")

    if session_id:
        # Redirect to the specific session editor
        logger.info(f"Redirecting to editor with session: {session_id}")
        return redirect(f"/editor/{session_id}")

    # Show editor with empty state (prompt to create session)
    logger.info("Serving editor page without session (empty state)")
    return render_template("editor.html", session_id=None, error=None)


@app.route("/editor/<session_id>")
def editor_page_with_session(session_id):
    """
    Serve editor page with specific session.

    Args:
        session_id: The session ID to edit

    Returns:
        Rendered editor.html template with session_id context
        Or error page if session doesn't exist
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    logger.info(f"Serving editor page for session: {session_id}")

    try:
        # Validate session exists
        session = caption_pipeline.session_manager.get_session_or_raise(session_id)

        # Check if session has required data
        if not session.video_path:
            logger.warning(f"Session {session_id} exists but has no video_path")
            return render_template(
                "editor.html",
                session_id=session_id,
                error="Session exists but has no associated video file",
            )

        logger.info(f"✓ Session {session_id} found: status={session.status}")

        return render_template(
            "editor.html", session_id=session_id, error=None, session=session.to_dict()
        )

    except SessionNotFoundError:
        logger.warning(f"Session not found: {session_id}")
        return render_template(
            "editor.html",
            session_id=session_id,
            error=f"Session not found: {session_id}",
        ), 404

    except SessionError as e:
        logger.error(f"Error accessing session {session_id}: {e}")
        return render_template(
            "editor.html",
            session_id=session_id,
            error=f"Error accessing session: {str(e)}",
        ), 500

    except Exception as e:
        logger.error(f"Unexpected error loading session {session_id}: {e}")
        return render_template(
            "editor.html",
            session_id=session_id,
            error=f"Internal server error: {str(e)}",
        ), 500


@app.route("/editor/new")
def editor_new_session():
    """
    Redirect to create new session workflow.

    For now, redirects to upload page.
    Could be enhanced to show modal for selecting existing session.
    """
    logger.info("Redirecting to upload page for new session creation")
    return redirect("/upload-page")


@app.route("/sessions")
def sessions_list_page():
    """
    List all sessions for editor access.

    Query parameters:
        status (optional): Filter sessions by status
        search (optional): Search sessions by session ID

    Returns:
        Rendered sessions.html template with session list
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # Get filter parameters
    status_filter = request.args.get("status")
    search_query = request.args.get("search", "").lower().strip()

    logger.info(
        f"Serving sessions list (status_filter={status_filter}, search={search_query})"
    )

    try:
        # Get all sessions
        all_sessions = caption_pipeline.session_manager.list_sessions()

        # Apply filters
        filtered_sessions = []
        for session in all_sessions:
            # Filter by status if specified
            if status_filter and session.status != status_filter:
                continue

            # Filter by search query (session ID)
            if search_query and search_query not in session.session_id.lower():
                continue

            filtered_sessions.append(session)

        # Calculate statistics
        total_count = len(all_sessions)
        filtered_count = len(filtered_sessions)

        # Get status counts for filter buttons
        status_counts = {}
        for session in all_sessions:
            status_counts[session.status] = status_counts.get(session.status, 0) + 1

        logger.info(f"Displaying {filtered_count} of {total_count} sessions")

        return render_template(
            "sessions.html",
            sessions=[s.to_dict() for s in filtered_sessions],
            total_count=total_count,
            filtered_count=filtered_count,
            status_filter=status_filter,
            search_query=search_query,
            status_counts=status_counts,
        )

    except SessionError as e:
        logger.error(f"Error listing sessions: {e}")
        return render_template(
            "sessions.html", sessions=[], error=f"Error loading sessions: {str(e)}"
        ), 500

    except Exception as e:
        logger.error(f"Unexpected error listing sessions: {e}")
        return render_template(
            "sessions.html", sessions=[], error=f"Internal server error: {str(e)}"
        ), 500


@app.route("/api/editor/upload", methods=["POST"])
def editor_upload_media():
    """
    Upload media and create session (editor workflow).

    Request (multipart/form-data):
        video: Video or audio file
        model (optional): "prime" (default)

    Response JSON (201):
        {
            "success": true,
            "session_id": "uuid-string",
            "video_info": {
                "filename": "input.mp4",
                "duration": 120.5,
                "resolution": [1080, 1920]
            },
            "redirect_url": "/editor/{session_id}"
        }
    """
    # Verify pipeline is initialized
    error_response = verify_pipeline_initialized()
    if error_response:
        return error_response

    # Check if file is present
    if "video" not in request.files and "media" not in request.files:
        return jsonify({"error": "No media file provided"}), 400

    file = request.files.get("video") or request.files.get("media")

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify(
            {"error": f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}
        ), 400

    # Save uploaded file
    filename = secure_filename(file.filename)
    media_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(media_path)

    # Validate and detect media type
    is_valid, result = validate_media_file(media_path)
    if not is_valid:
        if os.path.exists(media_path):
            os.remove(media_path)
        return jsonify({"error": result}), 400

    media_type = result
    logger.info(f"Editor upload: {filename} ({media_type})")

    try:
        # Create session (uses "large" model)
        session_id = caption_pipeline.create_caption_session(media_path=media_path)

        # Get session info
        session = caption_pipeline.session_manager.get_session_or_raise(session_id)

        # Build video info response
        video_info = {
            "filename": filename,
            "path": media_path,
            "media_type": media_type,
        }

        # Add metadata if available
        if session.metadata:
            video_info.update(
                {
                    k: v
                    for k, v in session.metadata.items()
                    if k in ["duration", "resolution", "fps"]
                }
            )

        redirect_url = f"/editor/{session_id}"

        logger.info(f"✓ Session created for editor: {session_id}")

        return (
            jsonify(
                {
                    "success": True,
                    "session_id": session_id,
                    "video_info": video_info,
                    "redirect_url": redirect_url,
                    "status": session.status,
                    "created_at": session.created_at,
                }
            ),
            201,
        )

    except PipelineError as e:
        logger.error(f"Pipeline error creating session: {e}")
        # Cleanup uploaded file on error
        if os.path.exists(media_path):
            os.remove(media_path)
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        logger.error(f"Unexpected error creating session: {e}")
        # Cleanup uploaded file on error
        if os.path.exists(media_path):
            os.remove(media_path)
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# =============================================================================
# End of Phase 2 Editor Routes
# =============================================================================


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Media to SRT API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind")
    parser.add_argument(
        "--model-id",
        default="Oriserve/Whisper-Hindi2Hinglish-Prime",
        help="Whisper model size (default: large. Options: tiny, base, small, medium, large, large-v2, large-v3)",
    )
    parser.add_argument("--device", default="cuda", help="Device to run model on")
    parser.add_argument("--dtype", default="float16", help="Data type for model")

    args = parser.parse_args()

    # Detect available device with CPU fallback
    available_device = get_device(args.device)

    # Update global config
    MODEL_CONFIG["model_id"] = args.model_id
    MODEL_CONFIG["device"] = available_device
    MODEL_CONFIG["dtype"] = torch_dtype_from_str(args.dtype, available_device)

    logger.info(f"Starting API server on http://{args.host}:{args.port}")
    logger.info(f"Using model: {MODEL_CONFIG['model_id']}")
    logger.info(f"Device: {available_device}, dtype: {MODEL_CONFIG['dtype']}")

    # Create necessary directories
    os.makedirs("sessions", exist_ok=True)
    os.makedirs("fonts", exist_ok=True)
    os.makedirs("presets", exist_ok=True)

    # Initialize caption pipeline (Phase 1)
    caption_pipeline = None
    try:
        caption_pipeline = VideoCaptionPipeline(
            sessions_dir="sessions", font_dir="fonts"
        )
        logger.info("✓ Caption pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize caption pipeline: {e}")
        logger.warning("Phase 1 API endpoints will not be available")

    app.run(host=args.host, port=args.port, debug=False)

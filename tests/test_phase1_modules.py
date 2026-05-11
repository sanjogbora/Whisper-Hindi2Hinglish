"""
Comprehensive unit tests for Phase 1 modules:
- session_manager.py
- caption_styling.py
- video_caption_pipeline.py

Tests cover:
- Session management and persistence
- Caption styling and presets
- Video caption pipeline orchestration
- Helper functions (SRT parsing, frame extraction, ASS conversion)
"""

import json
import os
import tempfile
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch, call

import pytest

# Import modules under test
from caption_styling import (
    CaptionPreset,
    FontManager,
    PresetManager,
    TextStyle,
    DEFAULT_PRESETS,
    validate_alignment,
    validate_hex_color,
)
from session_manager import (
    Session,
    SessionError,
    SessionManager,
    SessionNotFoundError,
)
from video_caption_pipeline import (
    Caption,
    PipelineError,
    VideoCaptionPipeline,
    burn_captions_into_video,
    extract_frames_at_fps,
    parse_srt_captions,
    parse_srt_time,
    srt_to_ass,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_video_file(temp_dir):
    """Create a sample video file for testing."""
    video_path = Path(temp_dir) / "sample_video.mp4"
    video_path.write_bytes(b"fake video content")
    return str(video_path)


@pytest.fixture
def sample_audio_file(temp_dir):
    """Create a sample audio file for testing."""
    audio_path = Path(temp_dir) / "sample_audio.mp3"
    audio_path.write_bytes(b"fake audio content")
    return str(audio_path)


@pytest.fixture
def sample_srt_file(temp_dir):
    """Create a sample SRT file for testing."""
    srt_path = Path(temp_dir) / "sample_captions.srt"
    srt_content = """1
00:00:00,200 --> 00:00:01,360
Kal mainne kaha tha

2
00:00:01,360 --> 00:00:03,160
wealth hustle se nahin

3
00:00:03,160 --> 00:00:05,000
yeh hai business ka funda

4
00:00:05,000 --> 00:00:07,500
agar kisi ko samjh nahi aata
"""
    srt_path.write_text(srt_content, encoding="utf-8")
    return str(srt_path)


@pytest.fixture
def session_manager(temp_dir):
    """Create a SessionManager instance for testing."""
    sessions_dir = Path(temp_dir) / "sessions"
    return SessionManager(sessions_dir=str(sessions_dir))


@pytest.fixture
def preset_manager(temp_dir):
    """Create a PresetManager instance for testing."""
    presets_dir = Path(temp_dir) / "presets"
    return PresetManager(presets_dir=str(presets_dir))


@pytest.fixture
def font_manager(temp_dir):
    """Create a FontManager instance for testing."""
    fonts_dir = Path(temp_dir) / "fonts"
    return FontManager(fonts_dir=str(fonts_dir))


@pytest.fixture
def sample_session(session_manager, sample_video_file):
    """Create a sample session for testing."""
    session_id = session_manager.create_session(video_path=sample_video_file)
    return session_manager.get_session(session_id)


@pytest.fixture
def sample_text_style():
    """Create a sample TextStyle for testing."""
    return TextStyle(
        font_family="Roboto Bold",
        font_size=36,
        color="#FFFFFF",
        bold=True,
        italic=False,
        outline_color="#000000",
        outline_width=2,
        shadow=True,
        position_x=50,
        position_y=80,
        alignment="center",
    )


@pytest.fixture
def sample_preset(sample_text_style):
    """Create a sample CaptionPreset for testing."""
    return CaptionPreset(
        name="Test Preset",
        description="A test preset for unit testing",
        text_style=sample_text_style,
        target_aspect_ratio="9:16",
        category="test",
    )


# =============================================================================
# TestSessionManager - Tests for session_manager.py
# =============================================================================


class TestSessionManager:
    """Test suite for SessionManager class."""

    def test_session_manager_initialization(self, temp_dir):
        """Test that SessionManager initializes correctly and creates sessions directory."""
        sessions_dir = Path(temp_dir) / "test_sessions"
        manager = SessionManager(sessions_dir=str(sessions_dir))

        assert manager.sessions_dir == sessions_dir
        assert sessions_dir.exists()
        assert sessions_dir.is_dir()

    def test_create_session_with_video_only(self, session_manager, sample_video_file):
        """Test creating a session with only a video file."""
        session_id = session_manager.create_session(video_path=sample_video_file)

        # Verify session was created
        assert session_id is not None
        assert isinstance(session_id, str)

        # Verify session file exists
        session_file = session_manager._get_session_file_path(session_id)
        assert session_file.exists()

        # Verify session data
        session = session_manager.get_session(session_id)
        assert session.session_id == session_id
        assert session.video_path == sample_video_file
        assert session.audio_path is None
        assert session.status == "created"
        assert session.caption_style == "reels_standard"

    def test_create_session_with_video_and_audio(
        self, session_manager, sample_video_file, sample_audio_file
    ):
        """Test creating a session with both video and audio files."""
        session_id = session_manager.create_session(
            video_path=sample_video_file, audio_path=sample_audio_file
        )

        session = session_manager.get_session(session_id)
        assert session.video_path == sample_video_file
        assert session.audio_path == sample_audio_file

    def test_create_session_with_nonexistent_video(self, session_manager):
        """Test that creating a session with non-existent video raises error."""
        with pytest.raises(SessionError, match="Video file does not exist"):
            session_manager.create_session(video_path="/nonexistent/video.mp4")

    def test_create_session_with_nonexistent_audio(
        self, session_manager, sample_video_file
    ):
        """Test that creating a session with non-existent audio raises error."""
        with pytest.raises(SessionError, match="Audio file does not exist"):
            session_manager.create_session(
                video_path=sample_video_file, audio_path="/nonexistent/audio.mp3"
            )

    def test_get_existing_session(self, session_manager, sample_session):
        """Test retrieving an existing session."""
        session = session_manager.get_session(sample_session.session_id)

        assert session is not None
        assert session.session_id == sample_session.session_id
        assert isinstance(session, Session)

    def test_get_nonexistent_session_returns_none(self, session_manager):
        """Test that getting a non-existent session returns None."""
        session = session_manager.get_session("nonexistent-session-id")
        assert session is None

    def test_get_session_or_raise_success(self, session_manager, sample_session):
        """Test get_session_or_raise with existing session."""
        session = session_manager.get_session_or_raise(sample_session.session_id)
        assert session.session_id == sample_session.session_id

    def test_get_session_or_raise_not_found(self, session_manager):
        """Test that get_session_or_raise raises exception for non-existent session."""
        with pytest.raises(SessionNotFoundError):
            session_manager.get_session_or_raise("nonexistent-session-id")

    def test_update_session_fields(self, session_manager, sample_session):
        """Test updating session fields."""
        session_id = sample_session.session_id

        # Update single field
        success = session_manager.update_session(session_id, status="transcribed")
        assert success is True

        session = session_manager.get_session(session_id)
        assert session.status == "transcribed"

        # Update multiple fields
        success = session_manager.update_session(
            session_id, status="complete", captions_path="/path/to/captions.srt"
        )
        assert success is True

        session = session_manager.get_session(session_id)
        assert session.status == "complete"
        assert session.captions_path == "/path/to/captions.srt"

    def test_update_session_adds_to_metadata(self, session_manager, sample_session):
        """Test that updating unknown fields adds them to metadata."""
        session_id = sample_session.session_id

        session_manager.update_session(
            session_id, custom_field="custom_value", another_field=123
        )

        session = session_manager.get_session(session_id)
        assert session.metadata["custom_field"] == "custom_value"
        assert session.metadata["another_field"] == 123

    def test_delete_existing_session(self, session_manager, sample_session):
        """Test deleting an existing session."""
        session_id = sample_session.session_id

        # Verify session exists
        assert session_manager.get_session(session_id) is not None

        # Delete session
        success = session_manager.delete_session(session_id)
        assert success is True

        # Verify session is gone
        assert session_manager.get_session(session_id) is None

    def test_delete_nonexistent_session(self, session_manager):
        """Test deleting a non-existent session returns False."""
        success = session_manager.delete_session("nonexistent-session-id")
        assert success is False

    def test_list_sessions_empty(self, session_manager):
        """Test listing sessions when none exist."""
        sessions = session_manager.list_sessions()
        assert isinstance(sessions, list)
        assert len(sessions) == 0

    def test_list_sessions_with_data(self, session_manager, sample_video_file):
        """Test listing sessions with multiple sessions."""
        # Create multiple sessions
        session_ids = []
        for i in range(3):
            sid = session_manager.create_session(video_path=sample_video_file)
            session_ids.append(sid)

        # List sessions
        sessions = session_manager.list_sessions()
        assert len(sessions) == 3

        # Verify sessions are sorted by created_at (newest first)
        created_times = [s.created_at for s in sessions]
        assert created_times == sorted(created_times, reverse=True)

    def test_cleanup_old_sessions(self, session_manager, sample_video_file):
        """Test cleaning up expired sessions."""
        # Create an expired session
        session_id = session_manager.create_session(video_path=sample_video_file)

        # Manually set created_at to 25 hours ago
        session = session_manager.get_session(session_id)
        old_time = (datetime.now() - timedelta(hours=25)).isoformat()
        session.created_at = old_time
        session_manager._save_session(session)

        # Create a fresh session
        fresh_id = session_manager.create_session(video_path=sample_video_file)

        # Cleanup sessions older than 24 hours
        deleted_count = session_manager.cleanup_old_sessions(max_age_hours=24)
        assert deleted_count == 1

        # Verify expired session is deleted
        assert session_manager.get_session(session_id) is None
        assert session_manager.get_session(fresh_id) is not None

    def test_get_sessions_by_status(self, session_manager, sample_video_file):
        """Test filtering sessions by status."""
        # Create sessions with different statuses
        sid1 = session_manager.create_session(video_path=sample_video_file)
        sid2 = session_manager.create_session(video_path=sample_video_file)
        sid3 = session_manager.create_session(video_path=sample_video_file)

        # Update statuses
        session_manager.update_session(sid1, status="transcribed")
        session_manager.update_session(sid2, status="complete")
        session_manager.update_session(sid3, status="transcribed")

        # Get sessions by status
        transcribed = session_manager.get_sessions_by_status("transcribed")
        complete = session_manager.get_sessions_by_status("complete")

        assert len(transcribed) == 2
        assert len(complete) == 1
        assert complete[0].session_id == sid2

    def test_get_sessions_count(self, session_manager, sample_video_file):
        """Test getting the count of sessions."""
        assert session_manager.get_sessions_count() == 0

        session_manager.create_session(video_path=sample_video_file)
        session_manager.create_session(video_path=sample_video_file)
        session_manager.create_session(video_path=sample_video_file)

        assert session_manager.get_sessions_count() == 3


class TestSession:
    """Test suite for Session dataclass."""

    def test_session_to_dict_and_from_dict(self, sample_video_file):
        """Test Session serialization and deserialization."""
        session = Session(
            session_id="test-id",
            video_path=sample_video_file,
            audio_path="/path/to/audio.mp3",
            captions_path="/path/to/captions.srt",
            status="complete",
            caption_style="minimal_clean",
            metadata={"duration": 120.5, "resolution": "1080x1920"},
        )

        # Convert to dict
        session_dict = session.to_dict()
        assert isinstance(session_dict, dict)
        assert session_dict["session_id"] == "test-id"
        assert session_dict["status"] == "complete"

        # Convert back from dict
        restored_session = Session.from_dict(session_dict)
        assert restored_session.session_id == session.session_id
        assert restored_session.video_path == session.video_path
        assert restored_session.status == session.status
        assert restored_session.metadata == session.metadata

    def test_session_timestamp_updates(self, sample_video_file):
        """Test that update_timestamp updates the timestamp."""
        session = Session(
            session_id="test-id", video_path=sample_video_file, status="created"
        )

        old_updated_at = session.updated_at

        # Wait a tiny bit to ensure timestamp changes
        import time

        time.sleep(0.001)

        session.update_timestamp()

        assert session.updated_at != old_updated_at

    def test_session_is_expired(self, sample_video_file):
        """Test session expiration checking."""
        # Fresh session should not be expired
        session = Session(
            session_id="test-id", video_path=sample_video_file, status="created"
        )
        assert session.is_expired(max_age_hours=24) is False

        # Old session should be expired
        session.created_at = (datetime.now() - timedelta(hours=25)).isoformat()
        assert session.is_expired(max_age_hours=24) is True

    def test_session_is_expired_with_invalid_timestamp(self, sample_video_file):
        """Test that invalid timestamp is considered expired."""
        session = Session(
            session_id="test-id",
            video_path=sample_video_file,
            created_at="invalid-timestamp",
        )
        assert session.is_expired(max_age_hours=24) is True


# =============================================================================
# TestCaptionStyling - Tests for caption_styling.py
# =============================================================================


class TestCaptionStyling:
    """Test suite for caption styling components."""

    # ---------- TextStyle Tests ----------

    def test_text_style_creation_with_defaults(self):
        """Test creating TextStyle with default values."""
        style = TextStyle()

        assert style.font_family == "Roboto Bold"
        assert style.font_size == 36
        assert style.color == "#FFFFFF"
        assert style.bold is True
        assert style.italic is False
        assert style.outline_color == "#000000"
        assert style.outline_width == 2
        assert style.shadow is True
        assert style.position_x == 50
        assert style.position_y == 80
        assert style.alignment == "center"

    def test_text_style_creation_with_custom_values(self):
        """Test creating TextStyle with custom values."""
        style = TextStyle(
            font_family="Arial",
            font_size=40,
            color="#FFFF00",
            bold=False,
            italic=True,
            outline_color="#FF0000",
            outline_width=3,
            shadow=False,
            position_x=30,
            position_y=90,
            alignment="right",
        )

        assert style.font_family == "Arial"
        assert style.font_size == 40
        assert style.color == "#FFFF00"
        assert style.bold is False
        assert style.italic is True
        assert style.outline_width == 3
        assert style.shadow is False
        assert style.position_x == 30
        assert style.position_y == 90
        assert style.alignment == "right"

    def test_text_style_validation_invalid_color(self):
        """Test that TextStyle raises ValueError for invalid color."""
        with pytest.raises(ValueError, match="Invalid color format"):
            TextStyle(color="INVALID")

    def test_text_style_validation_invalid_outline_color(self):
        """Test that TextStyle raises ValueError for invalid outline color."""
        with pytest.raises(ValueError, match="Invalid outline color format"):
            TextStyle(outline_color="ZZZZZZ")

    def test_text_style_validation_invalid_alignment(self):
        """Test that TextStyle raises ValueError for invalid alignment."""
        with pytest.raises(ValueError, match="Invalid alignment"):
            TextStyle(alignment="invalid")

    def test_text_style_validation_position_x_out_of_range(self):
        """Test that TextStyle raises ValueError for position_x out of range."""
        with pytest.raises(ValueError, match="position_x must be between 0 and 100"):
            TextStyle(position_x=150)

    def test_text_style_validation_position_y_out_of_range(self):
        """Test that TextStyle raises ValueError for position_y out of range."""
        with pytest.raises(ValueError, match="position_y must be between 0 and 100"):
            TextStyle(position_y=-10)

    def test_text_style_validation_negative_font_size(self):
        """Test that TextStyle raises ValueError for negative font size."""
        with pytest.raises(ValueError, match="font_size must be positive"):
            TextStyle(font_size=-5)

    def test_text_style_validation_negative_outline_width(self):
        """Test that TextStyle raises ValueError for negative outline width."""
        with pytest.raises(ValueError, match="outline_width cannot be negative"):
            TextStyle(outline_width=-1)

    def test_text_style_to_dict_and_from_dict(self, sample_text_style):
        """Test TextStyle serialization and deserialization."""
        # Convert to dict
        style_dict = sample_text_style.to_dict()
        assert isinstance(style_dict, dict)
        assert style_dict["font_family"] == "Roboto Bold"
        assert style_dict["font_size"] == 36

        # Convert back from dict
        restored_style = TextStyle.from_dict(style_dict)
        assert restored_style.font_family == sample_text_style.font_family
        assert restored_style.font_size == sample_text_style.font_size
        assert restored_style.color == sample_text_style.color

    def test_text_style_to_ass_style(self, sample_text_style):
        """Test converting TextStyle to ASS format."""
        ass_style = sample_text_style.to_ass_style()

        assert isinstance(ass_style, str)
        assert "Fontname: Roboto Bold" in ass_style
        assert "Fontsize: 36" in ass_style
        assert "PrimaryColour:" in ass_style
        assert "OutlineColour:" in ass_style
        assert "Bold: 1" in ass_style
        assert "Italic: 0" in ass_style
        assert "Outline: 2" in ass_style
        assert "Alignment: 2" in ass_style

    def test_text_style_to_ass_style_with_custom_font(self, sample_text_style):
        """Test converting TextStyle to ASS with custom font name."""
        ass_style = sample_text_style.to_ass_style(font_name="CustomFont")
        assert "Fontname: CustomFont" in ass_style

    # ---------- CaptionPreset Tests ----------

    def test_caption_preset_creation(self, sample_preset):
        """Test creating a CaptionPreset."""
        assert sample_preset.name == "Test Preset"
        assert sample_preset.description == "A test preset for unit testing"
        assert sample_preset.target_aspect_ratio == "9:16"
        assert sample_preset.category == "test"
        assert isinstance(sample_preset.text_style, TextStyle)

    def test_caption_preset_to_dict_and_from_dict(self, sample_preset):
        """Test CaptionPreset serialization and deserialization."""
        # Convert to dict
        preset_dict = sample_preset.to_dict()
        assert isinstance(preset_dict, dict)
        assert preset_dict["name"] == "Test Preset"
        assert "text_style" in preset_dict

        # Convert back from dict
        restored_preset = CaptionPreset.from_dict(preset_dict)
        assert restored_preset.name == sample_preset.name
        assert restored_preset.description == sample_preset.description
        assert (
            restored_preset.text_style.font_family
            == sample_preset.text_style.font_family
        )

    # ---------- PresetManager Tests ----------

    def test_preset_manager_get_default_preset(self, preset_manager):
        """Test getting the default preset."""
        preset = preset_manager.get_default_preset()

        assert preset is not None
        assert preset.name == "Reels Standard"
        assert isinstance(preset, CaptionPreset)

    def test_preset_manager_get_preset_by_id(self, preset_manager):
        """Test getting a preset by ID."""
        preset = preset_manager.get_preset("reels_standard")
        assert preset is not None
        assert preset.name == "Reels Standard"

    def test_preset_manager_get_nonexistent_preset(self, preset_manager):
        """Test getting a non-existent preset returns None."""
        preset = preset_manager.get_preset("nonexistent_preset")
        assert preset is None

    def test_preset_manager_get_preset_or_raise_success(self, preset_manager):
        """Test get_preset_or_raise with existing preset."""
        preset = preset_manager.get_preset_or_raise("reels_standard")
        assert preset.name == "Reels Standard"

    def test_preset_manager_get_preset_or_raise_not_found(self, preset_manager):
        """Test that get_preset_or_raise raises exception for non-existent preset."""
        with pytest.raises(ValueError, match="Preset not found"):
            preset_manager.get_preset_or_raise("nonexistent_preset")

    def test_preset_manager_list_presets_all(self, preset_manager):
        """Test listing all presets."""
        presets = preset_manager.list_presets()

        assert isinstance(presets, list)
        assert len(presets) > 0
        assert all(isinstance(p, CaptionPreset) for p in presets)

    def test_preset_manager_list_presets_filtered_by_category(self, preset_manager):
        """Test listing presets filtered by category."""
        social_presets = preset_manager.list_presets(category="social")

        assert all(p.category == "social" for p in social_presets)

    def test_preset_manager_list_presets_filtered_by_aspect_ratio(self, preset_manager):
        """Test listing presets filtered by aspect ratio."""
        vertical_presets = preset_manager.list_presets(aspect_ratio="9:16")

        assert all(p.target_aspect_ratio in ("9:16", "any") for p in vertical_presets)

    def test_preset_manager_create_custom_preset(
        self, preset_manager, sample_text_style
    ):
        """Test creating a custom preset."""
        preset = preset_manager.create_preset(
            preset_id="my_custom_preset",
            name="My Custom Preset",
            description="A custom preset for testing",
            text_style=sample_text_style,
            target_aspect_ratio="16:9",
            category="custom",
        )

        assert preset.name == "My Custom Preset"
        assert preset.category == "custom"

        # Verify it can be retrieved
        retrieved = preset_manager.get_preset("my_custom_preset")
        assert retrieved is not None
        assert retrieved.name == "My Custom Preset"

    def test_preset_manager_create_preset_with_dict_style(self, preset_manager):
        """Test creating a preset with dictionary style."""
        style_dict = {
            "font_family": "Arial",
            "font_size": 40,
            "color": "#FFFF00",
            "bold": True,
            "italic": False,
            "outline_color": "#000000",
            "outline_width": 2,
            "shadow": True,
            "position_x": 50,
            "position_y": 80,
            "alignment": "center",
        }

        preset = preset_manager.create_preset(
            preset_id="dict_style_preset",
            name="Dict Style Preset",
            description="Preset created from dict",
            text_style=style_dict,
        )

        assert preset.text_style.font_family == "Arial"
        assert preset.text_style.font_size == 40

    def test_preset_manager_create_duplicate_preset(
        self, preset_manager, sample_text_style
    ):
        """Test that creating a duplicate preset raises error."""
        preset_id = "duplicate_preset"

        # Create first preset
        preset_manager.create_preset(
            preset_id=preset_id,
            name="First Preset",
            description="First preset",
            text_style=sample_text_style,
        )

        # Try to create duplicate
        with pytest.raises(ValueError, match="Preset already exists"):
            preset_manager.create_preset(
                preset_id=preset_id,
                name="Second Preset",
                description="Second preset",
                text_style=sample_text_style,
            )

    def test_preset_manager_delete_custom_preset(
        self, preset_manager, sample_text_style, temp_dir
    ):
        """Test deleting a custom preset."""
        # Create custom preset
        preset_id = "deletable_preset"
        preset_manager.create_preset(
            preset_id=preset_id,
            name="Deletable Preset",
            description="This can be deleted",
            text_style=sample_text_style,
        )

        # Verify it exists
        assert preset_manager.get_preset(preset_id) is not None

        # Delete it
        success = preset_manager.delete_preset(preset_id)
        assert success is True

        # Verify it's gone
        assert preset_manager.get_preset(preset_id) is None

    def test_preset_manager_protect_default_presets(self, preset_manager):
        """Test that default presets cannot be deleted."""
        with pytest.raises(ValueError, match="Cannot delete default preset"):
            preset_manager.delete_preset("reels_standard")

    def test_preset_manager_list_categories(self, preset_manager):
        """Test listing preset categories."""
        categories = preset_manager.list_categories()

        assert isinstance(categories, list)
        assert "social" in categories
        assert "minimal" in categories

    def test_preset_manager_get_presets_by_aspect_ratio(self, preset_manager):
        """Test getting presets for specific aspect ratio."""
        vertical_presets = preset_manager.get_presets_by_aspect_ratio("9:16")

        assert isinstance(vertical_presets, list)
        assert all(p.target_aspect_ratio in ("9:16", "any") for p in vertical_presets)

    # ---------- FontManager Tests ----------

    def test_font_manager_get_available_fonts_empty(self, font_manager):
        """Test getting available fonts when directory is empty."""
        fonts = font_manager.get_available_fonts()

        assert isinstance(fonts, list)
        assert len(fonts) == 0

    def test_font_manager_get_available_fonts_with_files(self, font_manager, temp_dir):
        """Test getting available fonts with font files."""
        # Create fake font files
        fonts_dir = Path(temp_dir) / "fonts"
        (fonts_dir / "Roboto-Bold.ttf").write_bytes(b"fake font")
        (fonts_dir / "Arial.ttf").write_bytes(b"fake font")
        (fonts_dir / "not_a_font.txt").write_bytes(b"text file")

        # Refresh cache
        font_manager.refresh_cache()

        fonts = font_manager.get_available_fonts()

        assert len(fonts) == 2
        font_names = [f["name"] for f in fonts]
        assert "Roboto-Bold" in font_names
        assert "Arial" in font_names

    def test_font_manager_get_font_by_id(self, font_manager, temp_dir):
        """Test getting font by ID."""
        fonts_dir = Path(temp_dir) / "fonts"
        (fonts_dir / "Test-Font.ttf").write_bytes(b"fake font")

        font_manager.refresh_cache()

        font = font_manager.get_font_by_id("test_font")
        assert font is not None
        assert font["name"] == "Test-Font"

    def test_font_manager_get_font_by_name(self, font_manager, temp_dir):
        """Test getting font by name."""
        fonts_dir = Path(temp_dir) / "fonts"
        (fonts_dir / "MyFont.ttf").write_bytes(b"fake font")

        font_manager.refresh_cache()

        font = font_manager.get_font_by_name("MyFont")
        assert font is not None
        assert font["id"] == "myfont"

    def test_font_manager_get_font_path(self, font_manager, temp_dir):
        """Test getting font file path."""
        fonts_dir = Path(temp_dir) / "fonts"
        font_file = fonts_dir / "PathFont.ttf"
        font_file.write_bytes(b"fake font")

        font_manager.refresh_cache()

        path = font_manager.get_font_path("PathFont")
        assert path is not None
        assert str(font_file) == path

    def test_font_manager_font_exists(self, font_manager, temp_dir):
        """Test checking if font exists."""
        fonts_dir = Path(temp_dir) / "fonts"
        (fonts_dir / "ExistsFont.ttf").write_bytes(b"fake font")

        font_manager.refresh_cache()

        assert font_manager.font_exists("ExistsFont") is True
        assert font_manager.font_exists("NonExistent") is False

    def test_font_manager_refresh_cache(self, font_manager):
        """Test refreshing font cache."""
        # Get fonts (should be empty)
        fonts = font_manager.get_available_fonts()
        assert len(fonts) == 0

        # Refresh
        font_manager.refresh_cache()
        assert font_manager._font_cache is None

        # Get again (cache should be rebuilt)
        fonts = font_manager.get_available_fonts()
        assert font_manager._font_cache is not None

    # ---------- Validation Functions Tests ----------

    def test_validate_hex_color_valid(self):
        """Test validating valid hex colors."""
        assert validate_hex_color("#FFFFFF") is True
        assert validate_hex_color("#000000") is True
        assert validate_hex_color("#FF0000") is True
        assert validate_hex_color("#00FF00") is True
        assert validate_hex_color("#0000FF") is True
        assert validate_hex_color("FFFFFF") is True  # Without #
        assert validate_hex_color("123abc") is True  # Lowercase

    def test_validate_hex_color_invalid(self):
        """Test validating invalid hex colors."""
        assert validate_hex_color("") is False
        assert validate_hex_color("#FFF") is False  # Too short
        assert validate_hex_color("#FFFFF") is False  # Too short
        assert validate_hex_color("#FFFFFFF") is False  # Too long
        assert validate_hex_color("#GGGGGG") is False  # Invalid hex
        assert validate_hex_color("notacolor") is False
        assert validate_hex_color(None) is False
        assert validate_hex_color(123) is False

    def test_validate_alignment_valid(self):
        """Test validating valid alignment values."""
        assert validate_alignment("left") is True
        assert validate_alignment("center") is True
        assert validate_alignment("right") is True

    def test_validate_alignment_invalid(self):
        """Test validating invalid alignment values."""
        assert validate_alignment("invalid") is False
        assert validate_alignment("justify") is False
        assert validate_alignment("") is False
        assert validate_alignment(None) is False


# =============================================================================
# TestVideoCaptionPipeline - Tests for video_caption_pipeline.py
# =============================================================================


class TestVideoCaptionPipeline:
    """Test suite for VideoCaptionPipeline class."""

    def test_pipeline_initialization(self, temp_dir):
        """Test that VideoCaptionPipeline initializes correctly."""
        sessions_dir = Path(temp_dir) / "sessions"
        fonts_dir = Path(temp_dir) / "fonts"

        pipeline = VideoCaptionPipeline(
            sessions_dir=str(sessions_dir), font_dir=str(fonts_dir)
        )

        assert pipeline.session_manager is not None
        assert pipeline.preset_manager is not None
        assert pipeline.font_manager is not None
        assert sessions_dir.exists()
        assert fonts_dir.exists()

    @patch("video_caption_pipeline.media_to_srt")
    @patch("video_caption_pipeline.get_media_type")
    def test_create_caption_session_with_video(
        self, mock_get_media_type, mock_media_to_srt, temp_dir, sample_video_file
    ):
        """Test creating a caption session from video file."""
        # Setup mocks
        mock_get_media_type.return_value = "video"

        # Mock SRT generation to actually create the file
        def create_srt(input_path, output_path, **kwargs):
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            Path(output_path).write_text(
                "1\n00:00:00,000 --> 00:00:01,000\nTest caption"
            )

        mock_media_to_srt.side_effect = create_srt

        sessions_dir = Path(temp_dir) / "sessions"
        pipeline = VideoCaptionPipeline(sessions_dir=str(sessions_dir))

        # Create session
        session_id = pipeline.create_caption_session(sample_video_file)

        # Verify session was created
        assert session_id is not None
        session = pipeline.session_manager.get_session(session_id)
        assert session is not None
        assert session.status == "transcribed"
        assert session.video_path == sample_video_file

        # Verify SRT file was created
        srt_path = Path(sessions_dir) / session_id / "captions.srt"
        assert srt_path.exists()

    @patch("video_caption_pipeline.media_to_srt")
    @patch("video_caption_pipeline.get_media_type")
    def test_create_caption_session_with_audio(
        self, mock_get_media_type, mock_media_to_srt, temp_dir, sample_audio_file
    ):
        """Test creating a caption session from audio file."""
        # Setup mocks
        mock_get_media_type.return_value = "audio"
        mock_media_to_srt.return_value = None

        sessions_dir = Path(temp_dir) / "sessions"
        pipeline = VideoCaptionPipeline(sessions_dir=str(sessions_dir))

        # For audio, we need to create a video path manually
        # since create_caption_session expects video_path
        session_id = pipeline.create_caption_session(sample_audio_file)

        # Verify session was created
        assert session_id is not None
        session = pipeline.session_manager.get_session(session_id)
        assert session.status == "transcribed"

    @patch("video_caption_pipeline.get_media_type")
    def test_create_caption_session_with_unsupported_format(
        self, mock_get_media_type, temp_dir, sample_video_file
    ):
        """Test that unsupported format raises error."""
        mock_get_media_type.return_value = "unknown"

        sessions_dir = Path(temp_dir) / "sessions"
        pipeline = VideoCaptionPipeline(sessions_dir=str(sessions_dir))

        with pytest.raises(PipelineError, match="Unsupported media format"):
            pipeline.create_caption_session(sample_video_file)

    def test_apply_caption_style_with_default_preset(
        self, temp_dir, sample_video_file, sample_srt_file
    ):
        """Test applying default caption style to a session."""
        sessions_dir = Path(temp_dir) / "sessions"
        pipeline = VideoCaptionPipeline(sessions_dir=str(sessions_dir))

        # Create session with captions
        session_id = pipeline.session_manager.create_session(
            video_path=sample_video_file
        )
        pipeline.session_manager.update_session(
            session_id, captions_path=sample_srt_file, status="transcribed"
        )

        # Apply default style
        success = pipeline.apply_caption_style(session_id)

        assert success is True
        session = pipeline.session_manager.get_session(session_id)
        assert session.caption_style == "reels_standard"

    def test_apply_caption_style_with_custom_overrides(
        self, temp_dir, sample_video_file, sample_srt_file
    ):
        """Test applying style with custom overrides."""
        sessions_dir = Path(temp_dir) / "sessions"
        pipeline = VideoCaptionPipeline(sessions_dir=str(sessions_dir))

        # Create session with captions
        session_id = pipeline.session_manager.create_session(
            video_path=sample_video_file
        )
        pipeline.session_manager.update_session(
            session_id, captions_path=sample_srt_file, status="transcribed"
        )

        # Apply style with overrides
        success = pipeline.apply_caption_style(
            session_id,
            preset_name="reels_standard",
            style_overrides={"font_size": 40, "color": "#FFFF00"},
        )

        assert success is True

        # Verify overrides were applied
        session = pipeline.session_manager.get_session(session_id)
        text_style = session.metadata.get("text_style", {})
        assert text_style.get("font_size") == 40
        assert text_style.get("color") == "#FFFF00"

    def test_apply_caption_style_with_invalid_override(
        self, temp_dir, sample_video_file, sample_srt_file
    ):
        """Test that invalid style override raises error."""
        sessions_dir = Path(temp_dir) / "sessions"
        pipeline = VideoCaptionPipeline(sessions_dir=str(sessions_dir))

        # Create session with captions
        session_id = pipeline.session_manager.create_session(
            video_path=sample_video_file
        )
        pipeline.session_manager.update_session(
            session_id, captions_path=sample_srt_file, status="transcribed"
        )

        # Try to apply invalid color
        with pytest.raises(PipelineError, match="Invalid style override"):
            pipeline.apply_caption_style(
                session_id,
                preset_name="reels_standard",
                style_overrides={"color": "INVALID"},
            )

    def test_apply_caption_style_nonexistent_session(self, temp_dir):
        """Test applying style to non-existent session."""
        sessions_dir = Path(temp_dir) / "sessions"
        pipeline = VideoCaptionPipeline(sessions_dir=str(sessions_dir))

        with pytest.raises(PipelineError, match="Session not found"):
            pipeline.apply_caption_style("nonexistent-session-id")

    def test_apply_caption_style_nonexistent_preset(
        self, temp_dir, sample_video_file, sample_srt_file
    ):
        """Test applying non-existent preset raises error."""
        sessions_dir = Path(temp_dir) / "sessions"
        pipeline = VideoCaptionPipeline(sessions_dir=str(sessions_dir))

        # Create session with captions
        session_id = pipeline.session_manager.create_session(
            video_path=sample_video_file
        )
        pipeline.session_manager.update_session(
            session_id, captions_path=sample_srt_file, status="transcribed"
        )

        # Try to apply non-existent preset
        with pytest.raises(PipelineError, match="Preset not found"):
            pipeline.apply_caption_style(session_id, preset_name="nonexistent_preset")

    def test_get_session_info(self, temp_dir, sample_video_file):
        """Test getting session information."""
        sessions_dir = Path(temp_dir) / "sessions"
        pipeline = VideoCaptionPipeline(sessions_dir=str(sessions_dir))

        # Create session
        session_id = pipeline.session_manager.create_session(
            video_path=sample_video_file
        )

        # Get session info
        info = pipeline.get_session_info(session_id)

        assert isinstance(info, dict)
        assert info["session_id"] == session_id
        assert info["video_path"] == sample_video_file
        assert info["status"] == "created"

    def test_get_session_info_nonexistent(self, temp_dir):
        """Test getting info for non-existent session."""
        sessions_dir = Path(temp_dir) / "sessions"
        pipeline = VideoCaptionPipeline(sessions_dir=str(sessions_dir))

        with pytest.raises(PipelineError, match="Session not found"):
            pipeline.get_session_info("nonexistent-session-id")

    def test_delete_session(self, temp_dir, sample_video_file):
        """Test deleting a session."""
        sessions_dir = Path(temp_dir) / "sessions"
        pipeline = VideoCaptionPipeline(sessions_dir=str(sessions_dir))

        # Create session
        session_id = pipeline.session_manager.create_session(
            video_path=sample_video_file
        )

        # Create some files in session directory
        session_dir = Path(sessions_dir) / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        (session_dir / "test_file.txt").write_text("test content")

        # Delete session
        success = pipeline.delete_session(session_id)

        assert success is True
        assert pipeline.session_manager.get_session(session_id) is None
        assert not session_dir.exists()

    def test_delete_session_nonexistent(self, temp_dir):
        """Test deleting non-existent session."""
        sessions_dir = Path(temp_dir) / "sessions"
        pipeline = VideoCaptionPipeline(sessions_dir=str(sessions_dir))

        success = pipeline.delete_session("nonexistent-session-id")
        assert success is False


# =============================================================================
# Test Helper Functions - Tests for utility functions
# =============================================================================


class TestHelperFunctions:
    """Test suite for helper functions in video_caption_pipeline."""

    # ---------- Caption Tests ----------

    def test_caption_creation(self):
        """Test creating a Caption object."""
        caption = Caption(index=1, start_time=0.2, end_time=1.36, text="Test caption")

        assert caption.index == 1
        assert caption.start_time == 0.2
        assert caption.end_time == 1.36
        assert caption.text == "Test caption"

    def test_caption_to_dict_and_from_dict(self):
        """Test Caption serialization and deserialization."""
        caption = Caption(index=1, start_time=0.2, end_time=1.36, text="Test caption")

        # Convert to dict
        caption_dict = caption.to_dict()
        assert caption_dict["index"] == 1
        assert caption_dict["start"] == 0.2
        assert caption_dict["end"] == 1.36
        assert caption_dict["text"] == "Test caption"

        # Convert back from dict
        restored_caption = Caption.from_dict(caption_dict)
        assert restored_caption.index == caption.index
        assert restored_caption.start_time == caption.start_time
        assert restored_caption.end_time == caption.end_time
        assert restored_caption.text == caption.text

    # ---------- SRT Parsing Tests ----------

    def test_parse_srt_time_valid(self):
        """Test parsing valid SRT timestamps."""
        assert parse_srt_time("00:00:00,200") == pytest.approx(0.2)
        assert parse_srt_time("00:00:01,360") == pytest.approx(1.36)
        assert parse_srt_time("00:01:00,000") == pytest.approx(60.0)
        assert parse_srt_time("01:00:00,000") == pytest.approx(3600.0)
        assert parse_srt_time("01:01:01,500") == pytest.approx(3661.5)

    def test_parse_srt_time_invalid(self):
        """Test parsing invalid SRT timestamps."""
        with pytest.raises(ValueError, match="Invalid SRT timestamp"):
            parse_srt_time("invalid")

        with pytest.raises(ValueError, match="Invalid SRT timestamp"):
            parse_srt_time("00:00:00")

    def test_parse_srt_captions_valid(self, sample_srt_file):
        """Test parsing a valid SRT file."""
        captions = parse_srt_captions(sample_srt_file)

        assert len(captions) == 4
        assert captions[0].index == 1
        assert captions[0].start_time == pytest.approx(0.2)
        assert captions[0].end_time == pytest.approx(1.36)
        assert captions[0].text == "Kal mainne kaha tha"

        assert captions[1].index == 2
        assert captions[1].text == "wealth hustle se nahin"

    def test_parse_srt_captions_multiline_text(self, temp_dir):
        """Test parsing SRT with multiline caption text."""
        srt_path = Path(temp_dir) / "multiline.srt"
        srt_content = """1
00:00:00,000 --> 00:00:02,000
First line
Second line
Third line

2
00:00:02,000 --> 00:00:04,000
Single line caption
"""
        srt_path.write_text(srt_content, encoding="utf-8")

        captions = parse_srt_captions(str(srt_path))

        assert len(captions) == 2
        assert captions[0].text == "First line\nSecond line\nThird line"
        assert captions[1].text == "Single line caption"

    def test_parse_srt_captions_empty_file(self, temp_dir):
        """Test parsing an empty SRT file."""
        srt_path = Path(temp_dir) / "empty.srt"
        srt_path.write_text("", encoding="utf-8")

        captions = parse_srt_captions(str(srt_path))

        assert len(captions) == 0

    def test_parse_srt_captions_invalid_blocks(self, temp_dir):
        """Test parsing SRT with invalid blocks (should skip them)."""
        srt_path = Path(temp_dir) / "invalid.srt"
        srt_content = """invalid block without proper format

1
00:00:00,000 --> 00:00:01,000
Valid caption

invalid
another invalid
"""
        srt_path.write_text(srt_content, encoding="utf-8")

        captions = parse_srt_captions(str(srt_path))

        # Should only parse the valid caption
        assert len(captions) == 1
        assert captions[0].text == "Valid caption"

    # ---------- Frame Extraction Tests ----------

    @patch("video_caption_pipeline.subprocess.run")
    @patch("video_caption_pipeline.get_media_duration")
    def test_extract_frames_at_fps_success(
        self, mock_duration, mock_subprocess, temp_dir, sample_video_file
    ):
        """Test successful frame extraction."""
        # Setup mocks
        mock_duration.return_value = 10.0  # 10 second video
        mock_subprocess.return_value = MagicMock(stderr="")

        # Create fake frame files
        output_dir = Path(temp_dir) / "frames"
        output_dir.mkdir(parents=True, exist_ok=True)
        for i in range(10):
            (output_dir / f"frame_{i:05d}.jpg").write_bytes(b"fake frame")

        # Extract frames
        frames = extract_frames_at_fps(
            sample_video_file, str(output_dir), fps=1, width=160
        )

        assert len(frames) == 10
        assert all(Path(f).exists() for f in frames)

        # Verify ffmpeg command was called
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert "ffmpeg" in call_args
        assert sample_video_file in call_args
        # The vf parameter is a combined string
        vf_arg = next(arg for arg in call_args if "fps=" in arg)
        assert "fps=1" in vf_arg
        assert "scale=160:-1" in vf_arg

    @patch("video_caption_pipeline.get_media_duration")
    def test_extract_frames_at_fps_invalid_duration(
        self, mock_duration, temp_dir, sample_video_file
    ):
        """Test frame extraction with invalid duration."""
        mock_duration.return_value = 0.0

        with pytest.raises(PipelineError, match="Could not determine video duration"):
            extract_frames_at_fps(sample_video_file, str(temp_dir))

    @patch("video_caption_pipeline.subprocess.run")
    @patch("video_caption_pipeline.get_media_duration")
    def test_extract_frames_at_fps_max_frames_limit(
        self, mock_duration, mock_subprocess, temp_dir, sample_video_file
    ):
        """Test frame extraction with max_frames limit."""
        # Setup mocks
        mock_duration.return_value = 100.0  # 100 second video
        mock_subprocess.return_value = MagicMock(stderr="")

        output_dir = Path(temp_dir) / "frames"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create fake frame files for the expected output
        for i in range(60):
            (output_dir / f"frame_{i:05d}.jpg").write_bytes(b"fake frame")

        # Extract with max_frames limit
        frames = extract_frames_at_fps(
            sample_video_file, str(output_dir), fps=1, max_frames=60
        )

        # Should adjust FPS to get 60 frames
        # Expected FPS: 60 / 100 = 0.6 fps
        call_args = mock_subprocess.call_args[0][0]
        vf_arg = next(arg for arg in call_args if "fps=" in arg)
        assert "fps=0.6" in vf_arg

    @patch("video_caption_pipeline.subprocess.run", side_effect=FileNotFoundError)
    @patch("video_caption_pipeline.get_media_duration")
    def test_extract_frames_at_fps_ffmpeg_not_found(
        self, mock_duration, temp_dir, sample_video_file
    ):
        """Test frame extraction when FFmpeg is not found."""
        mock_duration.return_value = 10.0

        with pytest.raises(PipelineError, match="FFmpeg not found"):
            extract_frames_at_fps(sample_video_file, str(temp_dir))

    # ---------- SRT to ASS Conversion Tests ----------

    def test_srt_to_ass_conversion(self, sample_srt_file, temp_dir, sample_text_style):
        """Test converting SRT to ASS format."""
        ass_path = Path(temp_dir) / "output.ass"

        srt_to_ass(
            sample_srt_file,
            str(ass_path),
            sample_text_style,
            video_resolution=(1080, 1920),
        )

        # Verify ASS file was created
        assert ass_path.exists()

        # Verify ASS content
        ass_content = ass_path.read_text(encoding="utf-8")
        assert "[Script Info]" in ass_content
        assert "[V4+ Styles]" in ass_content
        assert "[Events]" in ass_content
        assert "PlayResX: 1080" in ass_content
        assert "PlayResY: 1920" in ass_content
        assert "Fontname: Roboto Bold" in ass_content
        assert "Fontsize: 36" in ass_content
        assert "Dialogue:" in ass_content

    def test_srt_to_ass_empty_srt(self, temp_dir, sample_text_style):
        """Test converting empty SRT to ASS."""
        empty_srt = Path(temp_dir) / "empty.srt"
        empty_srt.write_text("", encoding="utf-8")
        ass_path = Path(temp_dir) / "output.ass"

        with pytest.raises(PipelineError, match="No captions found"):
            srt_to_ass(str(empty_srt), str(ass_path), sample_text_style)

    def test_srt_to_ass_escapes_special_chars(self, temp_dir, sample_text_style):
        """Test that SRT to ASS properly escapes special characters."""
        srt_path = Path(temp_dir) / "special.srt"
        srt_content = """1
00:00:00,000 --> 00:00:01,000
Text with {braces} and \\backslashes
"""
        srt_path.write_text(srt_content, encoding="utf-8")
        ass_path = Path(temp_dir) / "output.ass"

        srt_to_ass(str(srt_path), str(ass_path), sample_text_style)

        ass_content = ass_path.read_text(encoding="utf-8")
        # Special characters should be escaped
        assert "\\{" in ass_content
        assert "\\}" in ass_content
        assert "\\\\" in ass_content

    # ---------- Caption Burning Tests ----------

    @patch("video_caption_pipeline.subprocess.Popen")
    def test_burn_captions_into_video_success(
        self, mock_popen, temp_dir, sample_video_file, sample_srt_file
    ):
        """Test burning captions into video."""
        output_path = Path(temp_dir) / "output.mp4"
        font_dir = Path(temp_dir) / "fonts"
        font_dir.mkdir(parents=True, exist_ok=True)

        # Setup mock process that creates output file when wait is called
        def create_output_on_wait():
            output_path.write_bytes(b"fake video with captions")
            return 0

        mock_process = MagicMock()
        mock_process.wait.side_effect = create_output_on_wait
        mock_process.stdout = iter([])
        mock_popen.return_value = mock_process

        # Burn captions
        burn_captions_into_video(
            sample_video_file, sample_srt_file, str(output_path), font_dir=str(font_dir)
        )

        # Verify ffmpeg command
        call_args = mock_popen.call_args[0][0]
        assert "ffmpeg" in call_args
        assert sample_video_file in call_args
        # Check that the ass filter is in the command
        vf_arg = next(arg for arg in call_args if "ass=" in arg)
        assert str(sample_srt_file) in vf_arg
        assert "libx264" in call_args
        assert str(output_path) in call_args

    @patch("video_caption_pipeline.subprocess.Popen")
    def test_burn_captions_with_progress_callback(
        self, mock_popen, temp_dir, sample_video_file, sample_srt_file
    ):
        """Test burning captions with progress callback."""
        output_path = Path(temp_dir) / "output.mp4"
        font_dir = Path(temp_dir) / "fonts"
        font_dir.mkdir(parents=True, exist_ok=True)

        # Setup mock process with progress output
        mock_process = MagicMock()
        mock_process.wait.return_value = 0
        mock_process.stdout = iter(
            [
                "Duration: 00:00:10.00",
                "time=00:00:05.00",
                "time=00:00:10.00",
            ]
        )

        # Create output file when wait is called
        def create_output_on_wait():
            output_path.write_bytes(b"fake video with captions")
            return 0

        mock_process.wait.side_effect = create_output_on_wait
        mock_popen.return_value = mock_process

        # Track progress calls
        progress_values = []

        def progress_callback(progress):
            progress_values.append(progress)

        # Burn captions
        burn_captions_into_video(
            sample_video_file,
            sample_srt_file,
            str(output_path),
            font_dir=str(font_dir),
            progress_callback=progress_callback,
        )

        # Verify progress was reported
        assert len(progress_values) > 0
        # Use approximate comparison for floating point
        assert any(pytest.approx(50.0) == p for p in progress_values)  # 5/10 = 50%
        assert any(pytest.approx(100.0) == p for p in progress_values)  # 10/10 = 100%

    @patch("video_caption_pipeline.subprocess.Popen")
    def test_burn_captions_with_ffmpeg_error(
        self, mock_popen, temp_dir, sample_video_file, sample_srt_file
    ):
        """Test burning captions when FFmpeg fails."""
        # Setup mock process with error
        mock_process = MagicMock()
        mock_process.wait.return_value = 1  # Non-zero exit code
        mock_process.stdout = iter([])
        mock_popen.return_value = mock_process

        output_path = Path(temp_dir) / "output.mp4"
        font_dir = Path(temp_dir) / "fonts"
        font_dir.mkdir(parents=True, exist_ok=True)

        with pytest.raises(PipelineError, match="FFmpeg exited with code 1"):
            burn_captions_into_video(
                sample_video_file,
                sample_srt_file,
                str(output_path),
                font_dir=str(font_dir),
            )

    @patch("video_caption_pipeline.subprocess.Popen", side_effect=FileNotFoundError)
    def test_burn_captions_ffmpeg_not_found(
        self, temp_dir, sample_video_file, sample_srt_file
    ):
        """Test burning captions when FFmpeg is not found."""
        output_path = Path(temp_dir) / "output.mp4"

        with pytest.raises(PipelineError, match="FFmpeg not found"):
            burn_captions_into_video(
                sample_video_file, sample_srt_file, str(output_path)
            )


# =============================================================================
# Run Tests
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

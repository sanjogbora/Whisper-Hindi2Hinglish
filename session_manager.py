"""
Session Manager - Manages caption editing sessions with persistence

This module provides session management functionality for the video caption editor,
including session creation, retrieval, updates, deletion, and cleanup of old sessions.
"""

__all__ = [
    "Session",
    "SessionManager",
    "SessionNotFoundError",
    "SessionError",
]

import json
import logging
import os
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure module logger
logger = logging.getLogger(__name__)


class SessionError(Exception):
    """Base exception for session-related errors."""

    pass


class SessionNotFoundError(SessionError):
    """Raised when a session cannot be found."""

    pass


def is_valid_uuid(uuid_str: str) -> bool:
    """
    Validate that a string is a valid UUID format.

    Args:
        uuid_str: String to validate

    Returns:
        True if valid UUID format, False otherwise
    """
    try:
        uuid.UUID(uuid_str)
        return True
    except (ValueError, AttributeError):
        return False


@dataclass
class Session:
    """
    Represents a single caption editing session.

    Attributes:
        session_id: Unique identifier for the session (UUID)
        video_path: Path to the uploaded video file
        audio_path: Optional path to extracted audio file
        captions_path: Path to generated SRT captions file
        status: Current session status (created, transcribed, editing, rendering, complete, error)
        created_at: ISO format timestamp of session creation
        updated_at: ISO format timestamp of last update
        caption_style: Name or ID of the caption style preset being used
        metadata: Optional dictionary for additional session data (duration, resolution, etc.)
    """

    session_id: str
    video_path: str
    audio_path: Optional[str] = None
    captions_path: Optional[str] = None
    status: str = "created"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    caption_style: str = "reels_standard"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create Session instance from dictionary."""
        return cls(**data)

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time."""
        self.updated_at = datetime.now().isoformat()

    def is_expired(self, max_age_hours: int = 24) -> bool:
        """
        Check if the session has expired based on its creation time.

        Args:
            max_age_hours: Maximum age in hours before considering a session expired

        Returns:
            True if session is expired, False otherwise
        """
        try:
            created_at = datetime.fromisoformat(self.created_at)
            expiry_time = created_at + timedelta(hours=max_age_hours)
            return datetime.now() > expiry_time
        except (ValueError, TypeError):
            # If we can't parse the timestamp, consider it expired
            return True


class SessionManager:
    """
    Manages caption editing sessions with persistent storage.

    Sessions are stored as JSON files in the specified sessions directory.
    Each session file is named after the session ID.

    Example:
        >>> manager = SessionManager(sessions_dir="sessions")
        >>> session_id = manager.create_session("/path/to/video.mp4")
        >>> session = manager.get_session(session_id)
        >>> print(session.status)
    """

    def __init__(self, sessions_dir: str = "sessions"):
        """
        Initialize the SessionManager.

        Args:
            sessions_dir: Directory path where session files will be stored

        Raises:
            SessionError: If the sessions directory cannot be created or accessed
        """
        self.sessions_dir = Path(sessions_dir)

        try:
            self.sessions_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise SessionError(
                f"Failed to create sessions directory at {self.sessions_dir}: {e}"
            )

    def _get_session_file_path(self, session_id: str) -> Path:
        """
        Get the file path for a session's JSON file.

        Args:
            session_id: The session ID

        Returns:
            Path object for the session file
        """
        return self.sessions_dir / f"{session_id}.json"

    def create_session(self, video_path: str, audio_path: Optional[str] = None) -> str:
        """
        Create a new editing session.

        Args:
            video_path: Path to the uploaded video file
            audio_path: Optional path to extracted audio file

        Returns:
            The newly created session ID (UUID string)

        Raises:
            SessionError: If the video path doesn't exist or session creation fails
        """
        # Validate video path exists
        if not Path(video_path).exists():
            raise SessionError(f"Video file does not exist: {video_path}")

        # Validate audio path if provided
        if audio_path and not Path(audio_path).exists():
            raise SessionError(f"Audio file does not exist: {audio_path}")

        # Generate unique session ID
        session_id = str(uuid.uuid4())

        # Create new session
        session = Session(
            session_id=session_id,
            video_path=video_path,
            audio_path=audio_path,
            status="created",
        )

        # Save session to disk
        self._save_session(session)

        return session_id

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Retrieve a session by ID.

        Args:
            session_id: The session ID to retrieve

        Returns:
            Session object if found, None otherwise

        Raises:
            SessionError: If the session file cannot be read or parsed
        """
        session_file = self._get_session_file_path(session_id)

        if not session_file.exists():
            return None

        try:
            with open(session_file, "r", encoding="utf-8") as f:
                session_data = json.load(f)
            return Session.from_dict(session_data)
        except json.JSONDecodeError as e:
            raise SessionError(f"Failed to parse session file for {session_id}: {e}")
        except Exception as e:
            raise SessionError(f"Failed to read session file for {session_id}: {e}")

    def get_session_or_raise(self, session_id: str) -> Session:
        """
        Retrieve a session by ID, raising an exception if not found.

        Args:
            session_id: The session ID to retrieve

        Returns:
            Session object

        Raises:
            SessionNotFoundError: If the session does not exist
            SessionError: If the session file cannot be read or parsed
        """
        session = self.get_session(session_id)
        if session is None:
            raise SessionNotFoundError(f"Session not found: {session_id}")
        return session

    def update_session(self, session_id: str, **kwargs) -> bool:
        """
        Update session fields.

        Args:
            session_id: The session ID to update
            **kwargs: Field names and values to update (e.g., status="complete")

        Returns:
            True if update was successful, False otherwise

        Raises:
            SessionNotFoundError: If the session does not exist
            SessionError: If the update fails
        """
        session = self.get_session_or_raise(session_id)

        # Update specified fields
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
            else:
                # Add to metadata if it's not a direct field
                # FIX: Ensure metadata is initialized before use
                if session.metadata is None:
                    session.metadata = {}
                session.metadata[key] = value

        # Update timestamp
        session.update_timestamp()

        # Save updated session
        self._save_session(session)

        return True

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and its metadata file.

        Note: This does not delete the actual video/audio/caption files.
        Those should be cleaned up separately if needed.

        Args:
            session_id: The session ID to delete

        Returns:
            True if deletion was successful, False if session didn't exist

        Raises:
            SessionError: If deletion fails for reasons other than non-existence
        """
        session_file = self._get_session_file_path(session_id)

        if not session_file.exists():
            return False

        try:
            session_file.unlink()
            return True
        except OSError as e:
            raise SessionError(f"Failed to delete session {session_id}: {e}")

    def list_sessions(self) -> List[Session]:
        """
        List all existing sessions.

        Returns:
            List of Session objects, sorted by creation time (newest first)

        Raises:
            SessionError: If listing sessions fails
        """
        sessions = []

        try:
            for session_file in self.sessions_dir.glob("*.json"):
                try:
                    with open(session_file, "r", encoding="utf-8") as f:
                        session_data = json.load(f)
                    sessions.append(Session.from_dict(session_data))
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    # FIX: Use logger instead of print
                    logger.warning(
                        f"Skipping corrupted session file {session_file.name}: {e}"
                    )
                    continue
        except OSError as e:
            raise SessionError(f"Failed to list sessions: {e}")

        # Sort by created_at (newest first)
        sessions.sort(key=lambda s: s.created_at, reverse=True)

        return sessions

    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Remove expired sessions based on their creation time.

        Args:
            max_age_hours: Maximum age in hours before considering a session expired

        Returns:
            Number of sessions cleaned up

        Raises:
            SessionError: If cleanup fails
        """
        sessions = self.list_sessions()
        deleted_count = 0

        for session in sessions:
            if session.is_expired(max_age_hours):
                try:
                    self.delete_session(session.session_id)
                    deleted_count += 1
                except SessionError as e:
                    # FIX: Use logger instead of print
                    logger.warning(
                        f"Failed to delete expired session {session.session_id}: {e}"
                    )
                    continue

        return deleted_count

    def get_sessions_by_status(self, status: str) -> List[Session]:
        """
        Get all sessions with a specific status.

        Args:
            status: The status to filter by (e.g., "created", "transcribed", "rendering")

        Returns:
            List of Session objects with the specified status
        """
        all_sessions = self.list_sessions()
        return [s for s in all_sessions if s.status == status]

    def _save_session(self, session: Session) -> None:
        """
        Save a session to disk.

        Args:
            session: The Session object to save

        Raises:
            SessionError: If saving fails
        """
        session_file = self._get_session_file_path(session.session_id)

        try:
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
        except (OSError, TypeError) as e:
            raise SessionError(f"Failed to save session {session.session_id}: {e}")

    def get_sessions_count(self) -> int:
        """
        Get the total number of sessions.

        Returns:
            Number of session files
        """
        return len(list(self.sessions_dir.glob("*.json")))

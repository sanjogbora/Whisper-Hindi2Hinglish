"""
Tests for audio to SRT conversion
Tests the caption_generator module with various audio file formats
"""

import os
import tempfile
import pytest
from pathlib import Path

from caption_generator import media_to_srt, format_timestamp, group_words_for_subtitles
from media_handler import get_media_type, validate_media_file, get_media_duration


class TestMediaTypeDetection:
    """Test media type detection for various file formats"""

    def test_detect_audio_mp3(self):
        """Test detection of MP3 audio files"""
        media_type = get_media_type("test_audio.mp3")
        assert media_type == "audio"

    def test_detect_audio_wav(self):
        """Test detection of WAV audio files"""
        media_type = get_media_type("test_audio.wav")
        assert media_type == "audio"

    def test_detect_audio_m4a(self):
        """Test detection of M4A audio files"""
        media_type = get_media_type("test_audio.m4a")
        assert media_type == "audio"

    def test_detect_audio_ogg(self):
        """Test detection of OGG audio files"""
        media_type = get_media_type("test_audio.ogg")
        assert media_type == "audio"

    def test_detect_audio_flac(self):
        """Test detection of FLAC audio files"""
        media_type = get_media_type("test_audio.flac")
        assert media_type == "audio"

    def test_detect_audio_aac(self):
        """Test detection of AAC audio files"""
        media_type = get_media_type("test_audio.aac")
        assert media_type == "audio"

    def test_detect_video_mp4(self):
        """Test detection of MP4 video files"""
        media_type = get_media_type("test_video.mp4")
        assert media_type == "video"

    def test_detect_unknown_format(self):
        """Test detection of unknown file formats"""
        media_type = get_media_type("test.xyz")
        assert media_type == "unknown"


class TestMediaValidation:
    """Test media file validation"""

    def test_validate_nonexistent_file(self):
        """Test validation of non-existent file"""
        is_valid, result = validate_media_file("/nonexistent/file.mp3")
        assert is_valid is False
        assert "not found" in result.lower()

    def test_validate_unsupported_format(self):
        """Test validation of unsupported file format"""
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            temp_file = f.name
        try:
            is_valid, result = validate_media_file(temp_file)
            assert is_valid is False
            assert "unsupported" in result.lower()
        finally:
            os.remove(temp_file)


class TestTimestampFormatting:
    """Test SRT timestamp formatting"""

    def test_format_timestamp_seconds(self):
        """Test formatting of seconds-only timestamp"""
        result = format_timestamp(45.0)
        assert result == "00:00:45,000"

    def test_format_timestamp_minutes(self):
        """Test formatting of minutes timestamp"""
        result = format_timestamp(125.5)
        assert result == "00:02:05,500"

    def test_format_timestamp_hours(self):
        """Test formatting of hours timestamp"""
        result = format_timestamp(3661.123)
        assert result == "01:01:01,123"

    def test_format_timestamp_zero(self):
        """Test formatting of zero timestamp"""
        result = format_timestamp(0.0)
        assert result == "00:00:00,000"


class TestWordGrouping:
    """Test word grouping for subtitles"""

    def test_group_words_simple(self):
        """Test basic word grouping"""
        segments = [
            {
                "words": [
                    {"text": "Hello", "start": 0.0, "end": 0.5},
                    {"text": "world", "start": 0.5, "end": 1.0},
                    {"text": "this", "start": 1.0, "end": 1.5},
                    {"text": "is", "start": 1.5, "end": 1.8},
                    {"text": "test", "start": 1.8, "end": 2.2},
                ]
            }
        ]
        subtitles = group_words_for_subtitles(segments, max_words=2, max_chars=42)
        assert len(subtitles) > 0
        assert subtitles[0][0] == "Hello world"

    def test_group_words_with_pause(self):
        """Test word grouping with long pauses"""
        segments = [
            {
                "words": [
                    {"text": "Hello", "start": 0.0, "end": 0.5},
                    {"text": "world", "start": 0.5, "end": 1.0},
                    {"text": "this", "start": 2.0, "end": 2.5},  # 1 second pause
                ]
            }
        ]
        subtitles = group_words_for_subtitles(segments, max_words=3, max_pause_gap=0.5)
        assert len(subtitles) >= 2  # Should break at pause

    def test_group_words_character_limit(self):
        """Test word grouping with character limit"""
        segments = [
            {
                "words": [
                    {"text": "very", "start": 0.0, "end": 0.3},
                    {"text": "long", "start": 0.3, "end": 0.6},
                    {"text": "word", "start": 0.6, "end": 0.9},
                    {"text": "here", "start": 0.9, "end": 1.2},
                ]
            }
        ]
        subtitles = group_words_for_subtitles(segments, max_words=10, max_chars=10)
        # Should break due to character limit
        assert all(len(sub[0]) <= 10 for sub in subtitles)

    def test_group_words_fallback_segment(self):
        """Test word grouping fallback for segment-level data"""
        segments = [{"text": "Hello world this is a test", "start": 0.0, "end": 2.0}]
        subtitles = group_words_for_subtitles(segments, max_words=3, max_chars=42)
        assert len(subtitles) > 0
        assert subtitles[0][0] == "Hello world this is a test"


class TestAudioProcessing:
    """Test audio file processing"""

    @pytest.mark.skipif(
        not os.environ.get("RUN_INTEGRATION_TESTS"), reason="Integration test"
    )
    def test_media_to_srt_with_audio(self):
        """Test full audio to SRT conversion (requires test audio file)"""
        # This test requires a real audio file
        # Set RUN_INTEGRATION_TESTS=1 to run
        test_audio = os.path.join(
            os.path.dirname(__file__), "fixtures", "test_audio.mp3"
        )

        if not os.path.exists(test_audio):
            pytest.skip(f"Test audio file not found: {test_audio}")

        with tempfile.NamedTemporaryFile(suffix=".srt", delete=False) as f:
            output_srt = f.name

        try:
            result = media_to_srt(
                test_audio, output_srt, model_id="large", device="cpu"
            )
            assert os.path.exists(result)
            assert os.path.getsize(result) > 0

            # Verify SRT format
            with open(result, "r", encoding="utf-8") as f:
                content = f.read()
                assert "-->" in content  # SRT timestamp format
        finally:
            if os.path.exists(output_srt):
                os.remove(output_srt)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

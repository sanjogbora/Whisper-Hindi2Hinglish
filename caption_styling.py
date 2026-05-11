"""
Caption Styling - Manages caption presets and style configurations

This module provides classes for managing caption styling, including:
- TextStyle: Dataclass for text styling properties
- CaptionPreset: Dataclass for preset definitions
- FontManager: Manages available fonts
- PresetManager: Manages caption style presets

The module includes default presets optimized for social media formats
like Instagram Reels, TikTok, and YouTube Shorts.
"""

__all__ = [
    "TextStyle",
    "CaptionPreset",
    "FontManager",
    "PresetManager",
    "DEFAULT_PRESETS",
    "validate_hex_color",
    "validate_alignment",
]

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Configure module logger
logger = logging.getLogger(__name__)


# Default presets dictionary - includes all built-in presets
DEFAULT_PRESETS: Dict[str, Dict[str, Any]] = {
    "reels_standard": {
        "name": "Reels Standard",
        "description": "Optimized for Instagram Reels and TikTok",
        "text_style": {
            "font_family": "Fira Sans Compressed Medium",
            "font_size": 36,
            "color": "#FFFFFF",
            "bold": True,
            "italic": False,
            "outline_color": "#000000",
            "outline_width": 15,
            "shadow": True,
            "position_x": 50,
            "position_y": 50,
            "alignment": "center",
        },
        "target_aspect_ratio": "9:16",
        "category": "social",
    },
    "shorts_safe": {
        "name": "YouTube Shorts Safe",
        "description": "Safe area for YouTube interface elements",
        "text_style": {
            "font_family": "Fira Sans Compressed Medium",
            "font_size": 32,
            "color": "#FFFFFF",
            "bold": True,
            "italic": False,
            "outline_color": "#000000",
            "outline_width": 15,
            "shadow": True,
            "position_x": 50,
            "position_y": 50,
            "alignment": "center",
        },
        "target_aspect_ratio": "9:16",
        "category": "social",
    },
    "minimal_clean": {
        "name": "Minimal Clean",
        "description": "Clean look with subtle text shadow for readability",
        "text_style": {
            "font_family": "Fira Sans Compressed Medium",
            "font_size": 32,
            "color": "#FFFFFF",
            "bold": False,
            "italic": False,
            "outline_color": "#000000",
            "outline_width": 15,  # FIX: Add outline for visibility
            "shadow": True,  # FIX: Enable shadow for contrast
            "position_x": 50,
            "position_y": 50,
            "alignment": "center",
        },
        "target_aspect_ratio": "any",
        "category": "minimal",
    },
    "bold_impact": {
        "name": "Bold Impact",
        "description": "High contrast for maximum readability",
        "text_style": {
            "font_family": "Fira Sans Compressed Medium",
            "font_size": 40,
            "color": "#FFFFFF",
            "bold": True,
            "italic": False,
            "outline_color": "#000000",
            "outline_width": 15,
            "shadow": True,
            "position_x": 50,
            "position_y": 50,
            "alignment": "center",
        },
        "target_aspect_ratio": "any",
        "category": "impact",
    },
    "cinematic": {
        "name": "Cinematic",
        "description": "Elegant style for cinematic content",
        "text_style": {
            "font_family": "Fira Sans Compressed Medium",
            "font_size": 34,
            "color": "#FFFFFF",  # Changed from Beige to White
            "bold": False,
            "italic": True,
            "outline_color": "#000000",
            "outline_width": 15,  # FIX: Increased from 1 to 2 for better visibility
            "shadow": True,
            "position_x": 50,
            "position_y": 50,
            "alignment": "center",
        },
        "target_aspect_ratio": "any",
        "category": "cinematic",
    },
}


def validate_hex_color(color: str) -> bool:
    """
    Validate that a string is a valid hex color code.

    Args:
        color: The color string to validate

    Returns:
        True if valid hex color, False otherwise
    """
    if not color or not isinstance(color, str):
        return False
    # Remove # if present
    color = color.lstrip("#")
    # Check if it's 6 hex characters
    return len(color) == 6 and all(c.lower() in "0123456789abcdef" for c in color)


def validate_alignment(alignment: str) -> bool:
    """
    Validate that a string is a valid alignment value.

    Args:
        alignment: The alignment string to validate

    Returns:
        True if valid alignment, False otherwise
    """
    return alignment in {"left", "center", "right"}


@dataclass
class TextStyle:
    """
    Represents text styling properties for captions.

    Attributes:
        font_family: Name of the font family (e.g., "Roboto Bold")
        font_size: Font size in pixels
        color: Text color as hex string (e.g., "#FFFFFF")
        bold: Whether text should be bold
        italic: Whether text should be italic
        outline_color: Outline color as hex string
        outline_width: Outline width in pixels (0 for no outline)
        shadow: Whether to apply text shadow
        position_x: Horizontal position as percentage (0-100)
        position_y: Vertical position as percentage (0-100)
        alignment: Text alignment ('left', 'center', 'right')
    """

    font_family: str = "Fira Sans Compressed Medium"
    font_size: int = 36
    color: str = "#FFFFFF"
    bold: bool = True
    italic: bool = False
    outline_color: str = "#000000"
    outline_width: int = 15
    shadow: bool = True
    position_x: int = 50
    position_y: int = 50
    alignment: str = "center"

    def __post_init__(self):
        """Validate style parameters after initialization."""
        if not validate_hex_color(self.color):
            raise ValueError(f"Invalid color format: {self.color}")
        if not validate_hex_color(self.outline_color):
            raise ValueError(f"Invalid outline color format: {self.outline_color}")
        if not validate_alignment(self.alignment):
            raise ValueError(f"Invalid alignment: {self.alignment}")
        if not 0 <= self.position_x <= 100:
            raise ValueError(f"position_x must be between 0 and 100: {self.position_x}")
        if not 0 <= self.position_y <= 100:
            raise ValueError(f"position_y must be between 0 and 100: {self.position_y}")
        if self.font_size <= 0:
            raise ValueError(f"font_size must be positive: {self.font_size}")
        if self.outline_width < 0:
            raise ValueError(f"outline_width cannot be negative: {self.outline_width}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert TextStyle to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TextStyle":
        """Create TextStyle from dictionary."""
        return cls(**data)

    def to_ass_style(self, font_name: Optional[str] = None) -> str:
        """
        Convert to ASS subtitle style format.

        Returns comma-separated values in the exact order specified by ASS Format:
        Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour,
        BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing,
        Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding

        Args:
            font_name: Override font family name for ASS format

        Returns:
            ASS style configuration string with comma-separated values
        """
        font = font_name or self.font_family

        # Convert hex color to ASS format (BGR with alpha)
        # ASS uses &HAABBGGRR format where AA is alpha
        def hex_to_ass(hex_color: str) -> str:
            hex_color = hex_color.lstrip("#")
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return f"&H00{b:02X}{g:02X}{r:02X}"

        # Convert alignment to ASS value
        # ASS: 1=bottom-left, 2=bottom-center, 3=bottom-right
        #      4=middle-left, 5=middle-center, 6=middle-right
        #      7=top-left, 8=top-center, 9=top-right
        # We'll map to bottom row (1, 2, 3) for captions
        alignment_map = {"left": 4, "center": 5, "right": 6}
        ass_alignment = alignment_map.get(self.alignment, 5)

        primary_color = hex_to_ass(self.color)
        outline_color = hex_to_ass(self.outline_color)
        secondary_color = "&H00FFFFFF"  # Default white
        back_color = "&HFF000000"  # Black background box

        # Calculate margins based on alignment
        # Adjust left/right margins to prevent text from going off-screen
        margin_l = 100 if self.alignment == "right" else 10
        margin_r = 100 if self.alignment == "left" else 10

        # Return comma-separated values in the exact order of ASS Format declaration
        # NO field names - only values, separated by commas
        return ",".join(
            [
                "Default",  # Name (style name)
                font,  # Fontname
                str(self.font_size),  # Fontsize
                primary_color,  # PrimaryColour
                secondary_color,  # SecondaryColour
                outline_color,  # OutlineColour
                back_color,  # BackColour (black background box)
                str(1 if self.bold else 0),  # Bold
                str(1 if self.italic else 0),  # Italic
                "0",  # Underline
                "0",  # StrikeOut
                "100",  # ScaleX
                "100",  # ScaleY
                "0",  # Spacing
                "0",  # Angle
                "3",  # BorderStyle (3=opaque box background for black rectangular box)
                str(self.outline_width),  # Outline
                str(2 if self.shadow else 0),  # Shadow
                str(ass_alignment),  # Alignment
                str(margin_l),  # MarginL
                str(margin_r),  # MarginR
                "10",  # MarginV
                "1",  # Encoding (1=Western European)
            ]
        )


@dataclass
class CaptionPreset:
    """
    Represents a caption style preset.

    Attributes:
        name: Human-readable name of the preset
        description: Description of when to use this preset
        text_style: TextStyle object containing styling properties
        target_aspect_ratio: Target aspect ratio (e.g., "9:16", "16:9", "any")
        category: Category for grouping (e.g., "social", "minimal", "cinematic")
    """

    name: str
    description: str
    text_style: TextStyle
    target_aspect_ratio: str = "9:16"
    category: str = "social"

    def to_dict(self) -> Dict[str, Any]:
        """Convert CaptionPreset to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "text_style": self.text_style.to_dict(),
            "target_aspect_ratio": self.target_aspect_ratio,
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CaptionPreset":
        """Create CaptionPreset from dictionary."""
        text_style_data = data.get("text_style", {})
        text_style = (
            TextStyle.from_dict(text_style_data)
            if isinstance(text_style_data, dict)
            else text_style_data
        )
        return cls(
            name=data["name"],
            description=data["description"],
            text_style=text_style,
            target_aspect_ratio=data.get("target_aspect_ratio", "9:16"),
            category=data.get("category", "social"),
        )


class FontManager:
    """
    Manages available fonts for caption rendering.

    This class handles font discovery, validation, and preview generation.
    Fonts are expected to be stored in a fonts/ directory.
    """

    def __init__(self, fonts_dir: str = "fonts"):
        """
        Initialize the FontManager.

        Args:
            fonts_dir: Directory containing font files
        """
        self.fonts_dir = Path(fonts_dir)
        # FIX: Add error handling for directory creation
        try:
            self.fonts_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.warning(f"Failed to create fonts directory {fonts_dir}: {e}")
        self._font_cache: Optional[List[Dict[str, str]]] = None

    def get_available_fonts(self) -> List[Dict[str, str]]:
        """
        Get list of available fonts.

        Returns:
            List of font dictionaries with 'id', 'name', and 'file' keys

        Raises:
            OSError: If fonts directory cannot be accessed
        """
        if self._font_cache is not None:
            return self._font_cache

        fonts = []

        # Common font file extensions
        font_extensions = {".ttf", ".otf", ".woff", ".woff2"}

        try:
            for font_file in self.fonts_dir.iterdir():
                if font_file.suffix.lower() in font_extensions:
                    # Create a simple ID from filename
                    font_id = font_file.stem.lower().replace(" ", "_").replace("-", "_")

                    fonts.append(
                        {
                            "id": font_id,
                            "name": font_file.stem,
                            "file": font_file.name,
                            "path": str(font_file),
                        }
                    )
        except OSError as e:
            raise OSError(f"Failed to access fonts directory: {e}")

        self._font_cache = fonts
        return fonts

    def get_font_by_id(self, font_id: str) -> Optional[Dict[str, str]]:
        """
        Get font information by ID.

        Args:
            font_id: The font ID to look up

        Returns:
            Font dictionary if found, None otherwise
        """
        fonts = self.get_available_fonts()
        for font in fonts:
            if font["id"] == font_id:
                return font
        return None

    def get_font_by_name(self, font_name: str) -> Optional[Dict[str, str]]:
        """
        Get font information by name.

        Args:
            font_name: The font name to look up

        Returns:
            Font dictionary if found, None otherwise
        """
        fonts = self.get_available_fonts()
        for font in fonts:
            if font["name"].lower() == font_name.lower():
                return font
        return None

    def get_font_path(self, font_name: str) -> Optional[str]:
        """
        Get the full file path for a font by name.

        Args:
            font_name: The font name

        Returns:
            Full path to font file if found, None otherwise
        """
        font = self.get_font_by_name(font_name)
        return font["path"] if font else None

    def font_exists(self, font_name: str) -> bool:
        """
        Check if a font exists in the fonts directory.

        Args:
            font_name: The font name to check

        Returns:
            True if font exists, False otherwise
        """
        return self.get_font_by_name(font_name) is not None

    def get_font_preview(
        self, font_name: str, text: str = "AaBbCc123"
    ) -> Dict[str, Any]:
        """
        Get information needed for generating a font preview.

        Note: Actual preview image generation would require PIL/Pillow.
        This returns the metadata needed to create a preview.

        Args:
            font_name: The font name
            text: Sample text for preview

        Returns:
            Dictionary with font info and sample text

        Raises:
            ValueError: If font doesn't exist
        """
        font = self.get_font_by_name(font_name)
        if not font:
            raise ValueError(f"Font not found: {font_name}")

        return {
            "font": font,
            "sample_text": text,
            "font_path": font["path"],
        }

    def refresh_cache(self) -> None:
        """Refresh the font cache to pick up new fonts."""
        self._font_cache = None


class PresetManager:
    """
    Manages caption style presets.

    This class handles loading, saving, and managing caption presets.
    Presets can be loaded from the DEFAULT_PRESETS dictionary or
    from custom JSON files.
    """

    def __init__(self, presets_dir: str = "presets"):
        """
        Initialize the PresetManager.

        Args:
            presets_dir: Directory for custom preset JSON files
        """
        self.presets_dir = Path(presets_dir)
        self.presets_dir.mkdir(exist_ok=True)
        self._preset_cache: Optional[Dict[str, CaptionPreset]] = None

    def _load_default_presets(self) -> Dict[str, CaptionPreset]:
        """Load all default presets from DEFAULT_PRESETS dictionary."""
        presets = {}
        for preset_id, preset_data in DEFAULT_PRESETS.items():
            try:
                presets[preset_id] = CaptionPreset.from_dict(preset_data)
            except (KeyError, ValueError) as e:
                # FIX: Use logger instead of print
                logger.warning(f"Failed to load default preset {preset_id}: {e}")
                continue
        return presets

    def _load_custom_presets(self) -> Dict[str, CaptionPreset]:
        """Load custom presets from JSON files in presets directory."""
        presets = {}

        for preset_file in self.presets_dir.glob("*.json"):
            try:
                with open(preset_file, "r", encoding="utf-8") as f:
                    preset_data = json.load(f)
                preset_id = preset_file.stem
                presets[preset_id] = CaptionPreset.from_dict(preset_data)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # FIX: Use logger instead of print
                logger.warning(f"Failed to load custom preset {preset_file.name}: {e}")
                continue

        return presets

    def _get_all_presets(self) -> Dict[str, CaptionPreset]:
        """Get all presets (default + custom) with caching."""
        if self._preset_cache is not None:
            return self._preset_cache

        presets = {}
        presets.update(self._load_default_presets())
        presets.update(self._load_custom_presets())

        self._preset_cache = presets
        return presets

    def get_preset(self, preset_id: str) -> Optional[CaptionPreset]:
        """
        Get a preset by ID.

        Args:
            preset_id: The preset ID to retrieve

        Returns:
            CaptionPreset object if found, None otherwise
        """
        presets = self._get_all_presets()
        return presets.get(preset_id)

    def get_preset_or_raise(self, preset_id: str) -> CaptionPreset:
        """
        Get a preset by ID, raising an exception if not found.

        Args:
            preset_id: The preset ID to retrieve

        Returns:
            CaptionPreset object

        Raises:
            ValueError: If preset is not found
        """
        preset = self.get_preset(preset_id)
        if preset is None:
            raise ValueError(f"Preset not found: {preset_id}")
        return preset

    def list_presets(
        self, category: Optional[str] = None, aspect_ratio: Optional[str] = None
    ) -> List[CaptionPreset]:
        """
        List all available presets, optionally filtered.

        Args:
            category: Optional category filter (e.g., "social", "minimal")
            aspect_ratio: Optional aspect ratio filter (e.g., "9:16", "16:9")

        Returns:
            List of CaptionPreset objects
        """
        presets = list(self._get_all_presets().values())

        # Apply filters
        if category:
            presets = [p for p in presets if p.category == category]
        if aspect_ratio:
            presets = [
                p for p in presets if p.target_aspect_ratio in (aspect_ratio, "any")
            ]

        # Sort by name
        presets.sort(key=lambda p: p.name)

        return presets

    def get_default_preset(self) -> CaptionPreset:
        """
        Get the default preset (Reels/Shorts).

        Returns:
            CaptionPreset object for reels_standard preset
        """
        return self.get_preset_or_raise("reels_standard")

    def create_preset(
        self,
        preset_id: str,
        name: str,
        description: str,
        text_style: Union[TextStyle, Dict[str, Any]],
        target_aspect_ratio: str = "9:16",
        category: str = "custom",
        save_to_file: bool = True,
    ) -> CaptionPreset:
        """
        Create a new custom preset.

        Args:
            preset_id: Unique ID for the preset
            name: Human-readable name
            description: Description of the preset
            text_style: TextStyle object or dictionary
            target_aspect_ratio: Target aspect ratio
            category: Category for grouping
            save_to_file: Whether to save as JSON file

        Returns:
            The created CaptionPreset object

        Raises:
            ValueError: If preset ID already exists
        """
        # Check if preset already exists
        if preset_id in self._get_all_presets():
            raise ValueError(f"Preset already exists: {preset_id}")

        # Convert dict to TextStyle if needed
        if isinstance(text_style, dict):
            text_style = TextStyle.from_dict(text_style)

        # Create preset
        preset = CaptionPreset(
            name=name,
            description=description,
            text_style=text_style,
            target_aspect_ratio=target_aspect_ratio,
            category=category,
        )

        # Add to cache
        if self._preset_cache is None:
            self._preset_cache = {}
        self._preset_cache[preset_id] = preset

        # Save to file if requested
        if save_to_file:
            self._save_preset_file(preset_id, preset)

        return preset

    def delete_preset(self, preset_id: str) -> bool:
        """
        Delete a custom preset.

        Note: Default presets cannot be deleted.

        Args:
            preset_id: The preset ID to delete

        Returns:
            True if deleted, False if preset doesn't exist or is a default preset

        Raises:
            ValueError: If trying to delete a default preset
        """
        # Check if it's a default preset
        if preset_id in DEFAULT_PRESETS:
            raise ValueError(f"Cannot delete default preset: {preset_id}")

        # Remove from cache
        if self._preset_cache and preset_id in self._preset_cache:
            del self._preset_cache[preset_id]

        # Delete file if exists
        preset_file = self.presets_dir / f"{preset_id}.json"
        if preset_file.exists():
            try:
                preset_file.unlink()
            except OSError as e:
                print(f"Warning: Failed to delete preset file {preset_file}: {e}")
                return False

        return True

    def _save_preset_file(self, preset_id: str, preset: CaptionPreset) -> None:
        """
        Save a preset to a JSON file.

        Args:
            preset_id: The preset ID
            preset: The CaptionPreset object to save

        Raises:
            OSError: If file cannot be written
        """
        preset_file = self.presets_dir / f"{preset_id}.json"
        try:
            with open(preset_file, "w", encoding="utf-8") as f:
                json.dump(preset.to_dict(), f, indent=2, ensure_ascii=False)
        except OSError as e:
            raise OSError(f"Failed to save preset file {preset_file}: {e}")

    def refresh_cache(self) -> None:
        """Refresh the preset cache to pick up new presets."""
        self._preset_cache = None

    def list_categories(self) -> List[str]:
        """
        Get list of all available categories.

        Returns:
            List of category names
        """
        categories = set()
        for preset in self.list_presets():
            categories.add(preset.category)
        return sorted(list(categories))

    def get_presets_by_aspect_ratio(self, aspect_ratio: str) -> List[CaptionPreset]:
        """
        Get presets optimized for a specific aspect ratio.

        Args:
            aspect_ratio: The aspect ratio (e.g., "9:16", "16:9")

        Returns:
            List of CaptionPreset objects for that aspect ratio
        """
        return self.list_presets(aspect_ratio=aspect_ratio)


# Convenience function for quick preset access
def get_reels_shorts_preset() -> CaptionPreset:
    """
    Get the Reels/Shorts default preset quickly.

    Returns:
        CaptionPreset optimized for 9:16 vertical videos
    """
    manager = PresetManager()
    return manager.get_default_preset()

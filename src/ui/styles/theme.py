"""
Centralized theme system for Imajin Image Processor

This module defines all design tokens including colors, typography, spacing,
border radius, animation durations, and shadow definitions to ensure
consistent styling throughout the application.
"""


class Theme:
    """Centralized color palette and design tokens"""

    # Color Palette (PRESERVED - DO NOT MODIFY)
    BG_PRIMARY = '#F3F0FF'      # 60% - Light purple (background)
    BG_SECONDARY = '#E0D7FF'    # 30% - Medium purple (UI elements)
    ACCENT = '#CBE67C'          # 10% - Lime green (highlights)
    TEXT = '#352E52'            # Dark purple (text)

    # Semantic Colors (derived from palette)
    SUCCESS = '#CBE67C'         # Same as accent - green for success
    WARNING = '#FFA500'         # Orange for warnings
    ERROR = '#FF4444'           # Red for errors
    INFO = '#6C5CE7'            # Purple for info

    # Neutral Colors
    WHITE = '#FFFFFF'
    BLACK = '#000000'
    DISABLED_BG = '#CCCCCC'
    DISABLED_TEXT = '#666666'
    DISABLED_BORDER = '#999999'

    # Typography
    FONT_FAMILY = 'VCR OSD Mono'
    FONT_SIZE_SMALL = 9
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_LARGE = 14
    FONT_SIZE_TITLE = 16

    # Spacing (in pixels)
    SPACING_XS = 5
    SPACING_SM = 10
    SPACING_MD = 15
    SPACING_LG = 20
    SPACING_XL = 30

    # Border Radius (in pixels)
    RADIUS_SM = 3
    RADIUS_MD = 5
    RADIUS_LG = 8
    RADIUS_ROUND = 9  # For circular elements

    # Border Width
    BORDER_THIN = 2
    BORDER_THICK = 3

    # Animation Durations (in milliseconds)
    ANIMATION_FAST = 150
    ANIMATION_NORMAL = 300
    ANIMATION_SLOW = 500

    # Shadow Definitions (RGBA format)
    SHADOW_LIGHT = 'rgba(53, 46, 82, 0.1)'
    SHADOW_MEDIUM = 'rgba(53, 46, 82, 0.15)'
    SHADOW_HEAVY = 'rgba(53, 46, 82, 0.25)'

    # Shadow Offset and Blur
    SHADOW_OFFSET_X = 0
    SHADOW_OFFSET_Y = 2
    SHADOW_BLUR = 15

    # Gradient Colors (for progress bar and effects)
    ACCENT_LIGHT = '#D4F08C'    # Lighter shade of accent

    # Opacity Values
    OPACITY_FULL = 1.0
    OPACITY_HIGH = 0.9
    OPACITY_MEDIUM = 0.7
    OPACITY_LOW = 0.5
    OPACITY_VERY_LOW = 0.3

    # Component Sizes
    BUTTON_PADDING_H = 16  # Horizontal padding
    BUTTON_PADDING_V = 8   # Vertical padding
    ICON_SIZE = 18
    CHECKBOX_SIZE = 18
    SLIDER_HANDLE_SIZE = 18
    PROGRESS_BAR_HEIGHT = 30
    TOAST_WIDTH = 300
    TOAST_HEIGHT = 60

    # Z-Index for layering
    Z_INDEX_BASE = 0
    Z_INDEX_DROPDOWN = 1000
    Z_INDEX_DIALOG = 2000
    Z_INDEX_TOAST = 3000
    Z_INDEX_TOOLTIP = 4000

    @classmethod
    def get_qfont(cls, size=None, bold=False):
        """
        Get a QFont instance with theme settings

        Args:
            size: Font size (defaults to FONT_SIZE_NORMAL)
            bold: Whether to make the font bold

        Returns:
            QFont instance
        """
        from PyQt6.QtGui import QFont

        if size is None:
            size = cls.FONT_SIZE_NORMAL

        font = QFont(cls.FONT_FAMILY, size)
        if bold:
            font.setBold(True)
        return font

    @classmethod
    def rgba_to_hex(cls, r, g, b, a=1.0):
        """
        Convert RGBA values to hex color string

        Args:
            r, g, b: RGB values (0-255)
            a: Alpha value (0-1)

        Returns:
            Hex color string
        """
        if a < 1.0:
            # Include alpha in hex
            alpha_hex = format(int(a * 255), '02x')
            return f"#{format(r, '02x')}{format(g, '02x')}{format(b, '02x')}{alpha_hex}"
        return f"#{format(r, '02x')}{format(g, '02x')}{format(b, '02x')}"

    @classmethod
    def lighten_color(cls, color, factor=0.2):
        """
        Lighten a hex color by a factor

        Args:
            color: Hex color string (e.g., '#F3F0FF')
            factor: Amount to lighten (0-1)

        Returns:
            Lightened hex color string
        """
        # Remove # if present
        color = color.lstrip('#')

        # Convert to RGB
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)

        # Lighten
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))

        return f"#{format(r, '02x')}{format(g, '02x')}{format(b, '02x')}"

    @classmethod
    def darken_color(cls, color, factor=0.2):
        """
        Darken a hex color by a factor

        Args:
            color: Hex color string (e.g., '#F3F0FF')
            factor: Amount to darken (0-1)

        Returns:
            Darkened hex color string
        """
        # Remove # if present
        color = color.lstrip('#')

        # Convert to RGB
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)

        # Darken
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))

        return f"#{format(r, '02x')}{format(g, '02x')}{format(b, '02x')}"

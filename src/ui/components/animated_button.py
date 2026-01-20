"""
AnimatedButton - Button with hover and click animations for Imajin Image Processor

Features:
- Hover scale animation
- Click bounce effect
- Icon support via QtAwesome
- Loading state with spinner
- Smooth color transitions
"""

from PyQt6.QtWidgets import QPushButton, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon
from ui.styles.theme import Theme
import qtawesome as qta


class AnimatedButton(QPushButton):
    """
    Custom button with smooth animations

    Features:
    - Hover: Scale to 1.05x with color transition
    - Click: Scale to 0.95x then spring back
    - Icons: Support for QtAwesome icons
    - Loading: Animated spinner state
    """

    def __init__(self, text="", icon_name=None, parent=None):
        """
        Initialize the animated button

        Args:
            text: Button text
            icon_name: QtAwesome icon name (e.g., 'fa5s.folder-plus')
            parent: Parent widget
        """
        super().__init__(text, parent)

        self.icon_name = icon_name
        self.is_loading = False
        self.original_geometry = None
        self.hover_animation = None
        self.click_animation = None

        # Set icon if provided
        if icon_name:
            self._set_icon(icon_name)

        # Apply styling
        self._apply_style()

        # Set cursor
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Store original size for animations
        self.updateGeometry()

    def _set_icon(self, icon_name):
        """Set button icon from QtAwesome"""
        try:
            icon = qta.icon(icon_name, color=Theme.TEXT)
            self.setIcon(icon)
            self.setIconSize(QSize(Theme.ICON_SIZE, Theme.ICON_SIZE))
        except Exception as e:
            print(f"Warning: Could not load icon '{icon_name}': {e}")

    def _apply_style(self):
        """Apply stylesheet to the button"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.BG_SECONDARY};
                color: {Theme.TEXT};
                border: {Theme.BORDER_THIN}px solid {Theme.TEXT};
                border-radius: {Theme.RADIUS_MD}px;
                padding: {Theme.BUTTON_PADDING_V}px {Theme.BUTTON_PADDING_H}px;
                font-family: '{Theme.FONT_FAMILY}';
                font-weight: bold;
                font-size: {Theme.FONT_SIZE_NORMAL}px;
            }}

            QPushButton:hover {{
                background-color: {Theme.ACCENT};
                color: {Theme.TEXT};
            }}

            QPushButton:pressed {{
                background-color: {Theme.TEXT};
                color: {Theme.BG_PRIMARY};
            }}

            QPushButton:disabled {{
                background-color: {Theme.DISABLED_BG};
                color: {Theme.DISABLED_TEXT};
                border: {Theme.BORDER_THIN}px solid {Theme.DISABLED_BORDER};
            }}
        """)

    def enterEvent(self, event):
        """Handle mouse enter - scale up animation"""
        super().enterEvent(event)

        if self.isEnabled() and not self.is_loading:
            # Stop any existing animation
            if self.hover_animation and self.hover_animation.state() == QPropertyAnimation.State.Running:
                self.hover_animation.stop()

            # Store original geometry if not already stored
            if self.original_geometry is None:
                self.original_geometry = self.geometry()

            # Calculate scaled geometry
            original = self.original_geometry
            scale_factor = 1.05
            scaled_width = int(original.width() * scale_factor)
            scaled_height = int(original.height() * scale_factor)
            scaled_x = original.x() - (scaled_width - original.width()) // 2
            scaled_y = original.y() - (scaled_height - original.height()) // 2

            scaled_geo = self.geometry()
            scaled_geo.setRect(scaled_x, scaled_y, scaled_width, scaled_height)

            # Create animation
            self.hover_animation = QPropertyAnimation(self, b"geometry")
            self.hover_animation.setDuration(Theme.ANIMATION_FAST)
            self.hover_animation.setStartValue(self.geometry())
            self.hover_animation.setEndValue(scaled_geo)
            self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.hover_animation.start()

    def leaveEvent(self, event):
        """Handle mouse leave - scale back to original"""
        super().leaveEvent(event)

        if self.isEnabled() and not self.is_loading and self.original_geometry:
            # Stop any existing animation
            if self.hover_animation and self.hover_animation.state() == QPropertyAnimation.State.Running:
                self.hover_animation.stop()

            # Animate back to original size
            self.hover_animation = QPropertyAnimation(self, b"geometry")
            self.hover_animation.setDuration(Theme.ANIMATION_FAST)
            self.hover_animation.setStartValue(self.geometry())
            self.hover_animation.setEndValue(self.original_geometry)
            self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.hover_animation.start()

    def mousePressEvent(self, event):
        """Handle mouse press - quick scale down"""
        if self.isEnabled() and not self.is_loading:
            # Quick scale down animation
            if self.original_geometry:
                scale_factor = 0.95
                original = self.original_geometry
                scaled_width = int(original.width() * scale_factor)
                scaled_height = int(original.height() * scale_factor)
                scaled_x = original.x() + (original.width() - scaled_width) // 2
                scaled_y = original.y() + (original.height() - scaled_height) // 2

                scaled_geo = self.geometry()
                scaled_geo.setRect(scaled_x, scaled_y, scaled_width, scaled_height)

                self.click_animation = QPropertyAnimation(self, b"geometry")
                self.click_animation.setDuration(100)
                self.click_animation.setStartValue(self.geometry())
                self.click_animation.setEndValue(scaled_geo)
                self.click_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
                self.click_animation.start()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release - bounce back"""
        if self.isEnabled() and not self.is_loading and self.original_geometry:
            # Bounce back to hover size (1.05x)
            scale_factor = 1.05
            original = self.original_geometry
            scaled_width = int(original.width() * scale_factor)
            scaled_height = int(original.height() * scale_factor)
            scaled_x = original.x() - (scaled_width - original.width()) // 2
            scaled_y = original.y() - (scaled_height - original.height()) // 2

            scaled_geo = self.geometry()
            scaled_geo.setRect(scaled_x, scaled_y, scaled_width, scaled_height)

            self.click_animation = QPropertyAnimation(self, b"geometry")
            self.click_animation.setDuration(Theme.ANIMATION_FAST)
            self.click_animation.setStartValue(self.geometry())
            self.click_animation.setEndValue(scaled_geo)
            self.click_animation.setEasingCurve(QEasingCurve.Type.OutBack)
            self.click_animation.start()

        super().mouseReleaseEvent(event)

    def set_loading(self, loading):
        """
        Set button loading state with spinner icon

        Args:
            loading: True to show loading spinner, False to restore original icon
        """
        self.is_loading = loading

        if loading:
            # Show loading spinner
            try:
                spinner_icon = qta.icon('fa5s.spinner', color=Theme.TEXT, animation=qta.Spin(self))
                self.setIcon(spinner_icon)
                self.setEnabled(False)
            except Exception as e:
                print(f"Warning: Could not create spinner icon: {e}")
                self.setText(f"{self.text()} ...")
        else:
            # Restore original icon
            if self.icon_name:
                self._set_icon(self.icon_name)
            else:
                self.setIcon(QIcon())  # Clear icon
            self.setEnabled(True)

    def set_icon(self, icon_name):
        """
        Update button icon

        Args:
            icon_name: QtAwesome icon name
        """
        self.icon_name = icon_name
        if not self.is_loading:
            self._set_icon(icon_name)

    def resizeEvent(self, event):
        """Update original geometry when button is resized"""
        super().resizeEvent(event)
        if not self.hover_animation or self.hover_animation.state() != QPropertyAnimation.State.Running:
            self.original_geometry = self.geometry()


class PrimaryButton(AnimatedButton):
    """Styled primary action button with accent color"""

    def __init__(self, text="", icon_name=None, parent=None):
        super().__init__(text, icon_name, parent)
        self._apply_primary_style()

    def _apply_primary_style(self):
        """Apply primary button styling"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.ACCENT};
                color: {Theme.TEXT};
                border: {Theme.BORDER_THICK}px solid {Theme.TEXT};
                border-radius: {Theme.RADIUS_MD}px;
                padding: {Theme.BUTTON_PADDING_V + 4}px {Theme.BUTTON_PADDING_H + 4}px;
                font-family: '{Theme.FONT_FAMILY}';
                font-weight: bold;
                font-size: {Theme.FONT_SIZE_LARGE}px;
            }}

            QPushButton:hover {{
                background-color: {Theme.TEXT};
                color: {Theme.ACCENT};
            }}

            QPushButton:pressed {{
                background-color: {Theme.TEXT};
                color: {Theme.ACCENT};
            }}

            QPushButton:disabled {{
                background-color: {Theme.DISABLED_BG};
                color: {Theme.DISABLED_TEXT};
                border: {Theme.BORDER_THIN}px solid {Theme.DISABLED_BORDER};
            }}
        """)


class DangerButton(AnimatedButton):
    """Styled danger/cancel button with red accent"""

    def __init__(self, text="", icon_name=None, parent=None):
        super().__init__(text, icon_name, parent)
        self._apply_danger_style()

    def _apply_danger_style(self):
        """Apply danger button styling"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.ERROR};
                color: {Theme.WHITE};
                border: {Theme.BORDER_THIN}px solid {Theme.TEXT};
                border-radius: {Theme.RADIUS_MD}px;
                padding: {Theme.BUTTON_PADDING_V}px {Theme.BUTTON_PADDING_H}px;
                font-family: '{Theme.FONT_FAMILY}';
                font-weight: bold;
                font-size: {Theme.FONT_SIZE_NORMAL}px;
            }}

            QPushButton:hover {{
                background-color: {Theme.darken_color(Theme.ERROR, 0.2)};
                color: {Theme.WHITE};
            }}

            QPushButton:pressed {{
                background-color: {Theme.TEXT};
                color: {Theme.ERROR};
            }}

            QPushButton:disabled {{
                background-color: {Theme.DISABLED_BG};
                color: {Theme.DISABLED_TEXT};
                border: {Theme.BORDER_THIN}px solid {Theme.DISABLED_BORDER};
            }}
        """)

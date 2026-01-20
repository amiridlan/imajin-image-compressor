"""
CardWidget - Material Design style card container for Imajin Image Processor

This widget replaces QGroupBox with a modern card design featuring shadows,
rounded corners, and optional collapsible content.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from ui.styles.theme import Theme
from ui.styles.animations import smooth_height_change


class CardWidget(QWidget):
    """
    Material Design elevated card with shadow effects

    Features:
    - Drop shadow for depth
    - Rounded corners
    - Optional collapsible header
    - Animated expand/collapse
    """

    collapsed = pyqtSignal(bool)  # Emitted when collapsed state changes

    def __init__(self, title="", collapsible=False, parent=None):
        """
        Initialize the card widget

        Args:
            title: Optional title text for header
            collapsible: Whether the card can be collapsed
            parent: Parent widget
        """
        super().__init__(parent)
        self.collapsible = collapsible
        self.expanded = True
        self.title_text = title

        # Create shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(Theme.SHADOW_BLUR)
        shadow.setColor(QColor(53, 46, 82, 40))  # Dark purple with alpha
        shadow.setOffset(Theme.SHADOW_OFFSET_X, Theme.SHADOW_OFFSET_Y)
        self.setGraphicsEffect(shadow)

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(Theme.SPACING_MD, Theme.SPACING_MD,
                                            Theme.SPACING_MD, Theme.SPACING_MD)
        self.main_layout.setSpacing(Theme.SPACING_SM)

        # Create header if title provided
        if title:
            self.header_widget = self._create_header(title)
            self.main_layout.addWidget(self.header_widget)

        # Content container
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(Theme.SPACING_MD)
        self.main_layout.addWidget(self.content_widget)

        # Apply styling
        self._apply_style()

        # Store original content height for animations
        self.content_max_height = 1000  # Large enough for most content

    def _create_header(self, title):
        """Create the header widget with title and optional collapse button"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, Theme.SPACING_SM)
        header_layout.setSpacing(Theme.SPACING_SM)

        # Title label
        title_label = QLabel(title)
        title_label.setFont(Theme.get_qfont(Theme.FONT_SIZE_LARGE, bold=True))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT};
                background-color: transparent;
                border: none;
            }}
        """)
        header_layout.addWidget(title_label)

        # Spacer
        header_layout.addStretch()

        # Collapse button if collapsible
        if self.collapsible:
            self.collapse_button = QPushButton("▼")
            self.collapse_button.setFixedSize(24, 24)
            self.collapse_button.clicked.connect(self.toggle_collapse)
            self.collapse_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {Theme.TEXT};
                    border: none;
                    font-size: {Theme.FONT_SIZE_LARGE}px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {Theme.ACCENT};
                }}
            """)
            header_layout.addWidget(self.collapse_button)

        return header

    def _apply_style(self):
        """Apply stylesheet to the card"""
        self.setStyleSheet(f"""
            CardWidget {{
                background-color: {Theme.BG_SECONDARY};
                border: {Theme.BORDER_THIN}px solid {Theme.TEXT};
                border-radius: {Theme.RADIUS_LG}px;
                font-family: '{Theme.FONT_FAMILY}';
            }}
        """)

    def toggle_collapse(self):
        """Toggle the collapsed state of the card"""
        if self.expanded:
            # Collapse
            target_height = 0
            if self.collapsible:
                self.collapse_button.setText("▶")
        else:
            # Expand
            target_height = self.content_max_height
            if self.collapsible:
                self.collapse_button.setText("▼")

        # Animate the height change
        smooth_height_change(self.content_widget, target_height, Theme.ANIMATION_NORMAL)

        self.expanded = not self.expanded
        self.collapsed.emit(not self.expanded)

    def add_widget(self, widget):
        """
        Add a widget to the card content area

        Args:
            widget: QWidget to add
        """
        self.content_layout.addWidget(widget)

    def add_layout(self, layout):
        """
        Add a layout to the card content area

        Args:
            layout: QLayout to add
        """
        self.content_layout.addLayout(layout)

    def set_title(self, title):
        """
        Update the card title

        Args:
            title: New title text
        """
        if hasattr(self, 'header_widget'):
            # Find and update the title label
            title_label = self.header_widget.findChild(QLabel)
            if title_label:
                title_label.setText(title)

    def clear_content(self):
        """Remove all widgets from the content area"""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Recursively clear sublayouts
                while item.layout().count():
                    subitem = item.layout().takeAt(0)
                    if subitem.widget():
                        subitem.widget().deleteLater()

    def set_content_max_height(self, height):
        """
        Set the maximum height for content (used for collapse animation)

        Args:
            height: Maximum height in pixels
        """
        self.content_max_height = height
        self.content_widget.setMaximumHeight(height if self.expanded else 0)

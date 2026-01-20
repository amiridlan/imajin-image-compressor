"""
QualityPresetsWidget - Slider with preset buttons for Imajin Image Processor

Provides an enhanced quality slider with Web/Balanced/High preset buttons
and smooth animated transitions between values.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, QButtonGroup
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from ui.styles.theme import Theme


class QualityPresetsWidget(QWidget):
    """
    Quality slider with preset buttons

    Presets:
    - Web: 75% (optimized for web)
    - Balanced: 85% (best balance)
    - High: 95% (maximum quality)
    - Custom: User-adjusted value
    """

    value_changed = pyqtSignal(int)  # Emitted when quality value changes

    PRESET_WEB = 75
    PRESET_BALANCED = 85
    PRESET_HIGH = 95

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_preset = "Balanced"  # Default preset
        self.slider_animation = None

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(Theme.SPACING_SM)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header with label and value
        header_layout = QHBoxLayout()
        header_layout.setSpacing(Theme.SPACING_SM)

        self.label = QLabel("Compression Quality:")
        self.label.setFont(Theme.get_qfont(Theme.FONT_SIZE_NORMAL, bold=False))
        self.label.setStyleSheet(f"color: {Theme.TEXT}; background: transparent;")

        self.value_label = QLabel("85%")
        self.value_label.setFont(Theme.get_qfont(Theme.FONT_SIZE_NORMAL, bold=True))
        self.value_label.setStyleSheet(f"color: {Theme.TEXT}; background: transparent;")

        header_layout.addWidget(self.label)
        header_layout.addStretch()
        header_layout.addWidget(self.value_label)

        main_layout.addLayout(header_layout)

        # Preset buttons
        presets_layout = QHBoxLayout()
        presets_layout.setSpacing(Theme.SPACING_SM)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        # Create preset buttons
        self.web_button = self._create_preset_button("Web: 75", self.PRESET_WEB,
                                                      "Optimized for web - smaller files, good quality")
        self.balanced_button = self._create_preset_button("Balanced: 85", self.PRESET_BALANCED,
                                                          "Best balance of quality and file size")
        self.high_button = self._create_preset_button("High: 95", self.PRESET_HIGH,
                                                       "Maximum quality - minimal compression")
        self.custom_button = self._create_preset_button("Custom", None,
                                                        "User-adjusted quality value")

        self.button_group.addButton(self.web_button, 0)
        self.button_group.addButton(self.balanced_button, 1)
        self.button_group.addButton(self.high_button, 2)
        self.button_group.addButton(self.custom_button, 3)

        presets_layout.addWidget(self.web_button)
        presets_layout.addWidget(self.balanced_button)
        presets_layout.addWidget(self.high_button)
        presets_layout.addWidget(self.custom_button)
        presets_layout.addStretch()

        main_layout.addLayout(presets_layout)

        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(100)
        self.slider.setValue(self.PRESET_BALANCED)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.slider.setToolTip("Drag to set custom compression quality (1-100)")

        self._apply_slider_style()

        main_layout.addWidget(self.slider)

        # Set default preset as checked
        self.balanced_button.setChecked(True)

    def _create_preset_button(self, text, value, tooltip):
        """Create a preset button"""
        button = QPushButton(text)
        button.setCheckable(True)
        button.setToolTip(tooltip)
        button.setCursor(Qt.CursorShape.PointingHandCursor)

        if value is not None:
            button.clicked.connect(lambda: self._on_preset_clicked(value, text.split(':')[0]))
        else:
            # Custom button - just visual, doesn't change value
            button.clicked.connect(lambda: self._on_custom_clicked())

        self._apply_preset_button_style(button)

        return button

    def _apply_preset_button_style(self, button):
        """Apply styling to preset button"""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.BG_SECONDARY};
                color: {Theme.TEXT};
                border: {Theme.BORDER_THIN}px solid {Theme.TEXT};
                border-radius: {Theme.RADIUS_LG}px;
                padding: {Theme.SPACING_XS}px {Theme.SPACING_SM}px;
                font-family: '{Theme.FONT_FAMILY}';
                font-size: {Theme.FONT_SIZE_SMALL}px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background-color: {Theme.lighten_color(Theme.ACCENT, 0.3)};
            }}

            QPushButton:checked {{
                background-color: {Theme.ACCENT};
                color: {Theme.TEXT};
                border: {Theme.BORDER_THIN}px solid {Theme.TEXT};
            }}

            QPushButton:disabled {{
                background-color: {Theme.DISABLED_BG};
                color: {Theme.DISABLED_TEXT};
            }}
        """)

    def _apply_slider_style(self):
        """Apply styling to slider"""
        self.slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {Theme.BG_SECONDARY};
                height: 8px;
                border-radius: 4px;
                border: 1px solid {Theme.TEXT};
            }}

            QSlider::handle:horizontal {{
                background: {Theme.ACCENT};
                border: {Theme.BORDER_THIN}px solid {Theme.TEXT};
                width: {Theme.SLIDER_HANDLE_SIZE}px;
                height: {Theme.SLIDER_HANDLE_SIZE}px;
                margin: -7px 0;
                border-radius: {Theme.RADIUS_ROUND}px;
            }}

            QSlider::handle:horizontal:hover {{
                background: {Theme.TEXT};
                border: {Theme.BORDER_THIN}px solid {Theme.ACCENT};
            }}

            QSlider::sub-page:horizontal {{
                background: {Theme.ACCENT};
                border-radius: 4px;
            }}
        """)

    def _on_preset_clicked(self, value, preset_name):
        """Handle preset button click"""
        self.current_preset = preset_name

        # Animate slider to preset value
        self._animate_slider_to(value)

    def _on_custom_clicked(self):
        """Handle custom button click"""
        self.current_preset = "Custom"
        # Just update the UI, don't change slider value

    def _on_slider_changed(self, value):
        """Handle slider value change"""
        # Update value label
        self.value_label.setText(f"{value}%")

        # Check if value matches a preset
        if value == self.PRESET_WEB:
            self.current_preset = "Web"
            self.web_button.setChecked(True)
        elif value == self.PRESET_BALANCED:
            self.current_preset = "Balanced"
            self.balanced_button.setChecked(True)
        elif value == self.PRESET_HIGH:
            self.current_preset = "High"
            self.high_button.setChecked(True)
        else:
            self.current_preset = "Custom"
            self.custom_button.setChecked(True)

        # Emit signal
        self.value_changed.emit(value)

    def _animate_slider_to(self, target_value):
        """Animate slider to target value"""
        # Stop any existing animation
        if self.slider_animation and self.slider_animation.state() == QPropertyAnimation.State.Running:
            self.slider_animation.stop()

        # Create animation
        self.slider_animation = QPropertyAnimation(self.slider, b"value")
        self.slider_animation.setDuration(Theme.ANIMATION_NORMAL)
        self.slider_animation.setStartValue(self.slider.value())
        self.slider_animation.setEndValue(target_value)
        self.slider_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.slider_animation.start()

    def get_value(self):
        """Get current quality value"""
        return self.slider.value()

    def set_value(self, value):
        """Set quality value"""
        self.slider.setValue(value)

    def get_preset(self):
        """Get current preset name"""
        return self.current_preset

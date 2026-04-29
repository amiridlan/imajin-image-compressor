from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QSizePolicy, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QColor
import qtawesome as qta
from ui.styles.theme import Theme

_RADIUS       = 16
_BORDER_IDLE  = 'rgba(255, 45, 120, 90)'
_BORDER_HOVER = Theme.ACCENT
_SHADOW_IDLE  = QColor(255, 45, 120, 80)
_SHADOW_HOVER = QColor(255, 45, 120, 180)
_BLUR_IDLE    = 14
_BLUR_HOVER   = 28
_OFFSET_IDLE  = 4
_OFFSET_HOVER = 8


class FeatureCard(QWidget):
    clicked = pyqtSignal()

    def __init__(self, icon_name, title, description, parent=None):
        super().__init__(parent)
        self.icon_name = icon_name
        self._hovered = False
        self._animation = None

        self.setFixedSize(280, 320)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # Required so mouseMoveEvent fires without a button held
        self.setMouseTracking(True)

        self._setup_shadow()
        self._build_ui(icon_name, title, description)
        self._apply_style(hovered=False)

    # ------------------------------------------------------------------
    # Shadow
    # ------------------------------------------------------------------

    def _setup_shadow(self):
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(_BLUR_IDLE)
        self._shadow.setOffset(0, _OFFSET_IDLE)
        self._shadow.setColor(_SHADOW_IDLE)
        self.setGraphicsEffect(self._shadow)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self, icon_name, title, description):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)
        layout.setContentsMargins(28, 32, 28, 28)

        icon_container = QWidget()
        icon_container.setFixedSize(72, 72)
        icon_container.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(255, 45, 120, 30);
                border-radius: 18px;
                border: 1px solid rgba(255, 45, 120, 60);
            }}
        """)
        icon_inner = QHBoxLayout(icon_container)
        icon_inner.setContentsMargins(12, 12, 12, 12)

        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("background: transparent; border: none;")
        self._update_icon(color=Theme.ACCENT)
        icon_inner.addWidget(self.icon_label)

        icon_row = QHBoxLayout()
        icon_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_row.addWidget(icon_container)

        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT};
                font-family: '{Theme.FONT_DISPLAY}';
                font-size: 19px;
                font-weight: bold;
                background: transparent;
                border: none;
            }}
        """)

        self.desc_label = QLabel(description)
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_MUTED};
                font-family: '{Theme.FONT_FAMILY}';
                font-size: 14px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)

        layout.addLayout(icon_row)
        layout.addWidget(self.title_label)
        layout.addWidget(self.desc_label)

    def _update_icon(self, color):
        try:
            icon = qta.icon(self.icon_name, color=color)
            self.icon_label.setPixmap(icon.pixmap(44, 44))
        except Exception:
            self.icon_label.setText("?")

    # ------------------------------------------------------------------
    # Style & animation
    # ------------------------------------------------------------------

    def _animate_glow(self, expand):
        if self._animation and self._animation.state() == QPropertyAnimation.State.Running:
            self._animation.stop()
        anim = QPropertyAnimation(self._shadow, b"blurRadius")
        anim.setDuration(200)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setStartValue(self._shadow.blurRadius())
        anim.setEndValue(_BLUR_HOVER if expand else _BLUR_IDLE)
        anim.start()
        self._animation = anim

    def _apply_style(self, hovered):
        if hovered:
            border = _BORDER_HOVER
            bw     = 2
            self._shadow.setColor(_SHADOW_HOVER)
            self._shadow.setOffset(0, _OFFSET_HOVER)
        else:
            border = _BORDER_IDLE
            bw     = 1
            self._shadow.setColor(_SHADOW_IDLE)
            self._shadow.setOffset(0, _OFFSET_IDLE)

        self.setStyleSheet(f"""
            FeatureCard {{
                background-color: {Theme.BG_SECONDARY};
                border: {bw}px solid {border};
                border-radius: {_RADIUS}px;
            }}
        """)
        self._update_icon(color=Theme.ACCENT)

    def _set_hover(self, on: bool):
        """Central hover toggle — guards against spurious state changes."""
        if on == self._hovered:
            return
        self._hovered = on
        self._apply_style(hovered=on)
        self._animate_glow(expand=on)

    # ------------------------------------------------------------------
    # Event handling — all gated on self.rect() to exclude shadow area
    # ------------------------------------------------------------------

    def _in_card(self, pos) -> bool:
        """True only when pos is inside the visible card rect (not shadow)."""
        return self.rect().contains(pos)

    def enterEvent(self, event):
        if self._in_card(event.position().toPoint()):
            self._set_hover(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._set_hover(False)
        super().leaveEvent(event)

    def mouseMoveEvent(self, event):
        # Tracks crossing the visible edge while inside the shadow hit area
        self._set_hover(self._in_card(event.pos()))
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if not self._in_card(event.pos()):
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.setStyleSheet(f"""
                FeatureCard {{
                    background-color: {Theme.ACCENT};
                    border: 2px solid {Theme.ACCENT};
                    border-radius: {_RADIUS}px;
                }}
            """)
            self._update_icon(color=Theme.BG_PRIMARY)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if not self._in_card(event.pos()):
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self._apply_style(hovered=True)
            self.clicked.emit()
        super().mouseReleaseEvent(event)

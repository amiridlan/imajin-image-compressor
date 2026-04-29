import webbrowser
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QSizePolicy, QApplication,
                              QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from ui.styles.theme import Theme

_STATUS_COLOR = {
    'malicious': Theme.ERROR,
    'safe':      Theme.SUCCESS_TEXT,
    'unknown':   Theme.WARNING,
}

_STATUS_LABEL = {
    'malicious': '⚠  MALICIOUS',
    'safe':      '✓  SAFE',
    'unknown':   '?  UNKNOWN',
}


class QrResultDialog(QDialog):
    def __init__(self, result: dict, parent=None):
        super().__init__(parent)
        self._result = result
        self.setWindowTitle("QR Code Details")
        self.setMinimumWidth(480)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.BG_PRIMARY};
                color: {Theme.TEXT};
                font-family: '{Theme.FONT_FAMILY}';
            }}
            QLabel {{
                background-color: transparent;
                color: {Theme.TEXT};
                font-family: '{Theme.FONT_FAMILY}';
            }}
            QPushButton {{
                background-color: {Theme.BG_SECONDARY};
                color: {Theme.TEXT};
                border: 2px solid {Theme.TEXT};
                border-radius: {Theme.RADIUS_MD}px;
                padding: {Theme.BUTTON_PADDING_V}px {Theme.BUTTON_PADDING_H}px;
                font-family: '{Theme.FONT_FAMILY}';
                font-weight: bold;
                font-size: {Theme.FONT_SIZE_NORMAL}px;
            }}
            QPushButton:hover {{
                background-color: {Theme.ACCENT};
            }}
            QPushButton:pressed {{
                background-color: {Theme.TEXT};
                color: {Theme.BG_PRIMARY};
            }}
        """)

        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(24, 24, 24, 20)

        # Title row
        safety = self._result['safety']
        status = safety['status']
        color = _STATUS_COLOR.get(status, Theme.TEXT)
        status_text = _STATUS_LABEL.get(status, '? UNKNOWN')

        status_lbl = QLabel(status_text)
        status_lbl.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 18px;
                font-weight: bold;
                font-family: '{Theme.FONT_FAMILY}';
                background: transparent;
            }}
        """)
        root.addWidget(status_lbl)

        divider = QFrame()
        divider.setFixedHeight(2)
        divider.setStyleSheet(f"background-color: {Theme.BG_SECONDARY}; border: none;")
        root.addWidget(divider)

        # QR content
        root.addWidget(self._row("Content", self._result['data'], monospace=True, wrap=True))
        root.addWidget(self._row("Source",  safety['source']))
        root.addWidget(self._row("Detail",  safety['detail'], wrap=True))

        if self._result.get('page'):
            root.addWidget(self._row("Page", str(self._result['page'])))

        root.addSpacing(4)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        from core.qr.malware_checker import is_url
        if is_url(self._result['data']):
            open_btn = QPushButton("Open URL")
            open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            open_btn.clicked.connect(self._open_url)
            btn_row.addWidget(open_btn)

        copy_btn = QPushButton("Copy")
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.clicked.connect(self._copy)
        btn_row.addWidget(copy_btn)

        btn_row.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)

        root.addLayout(btn_row)

    def _row(self, label: str, value: str, monospace=False, wrap=False):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        lbl = QLabel(label.upper())
        lbl.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT};
                font-size: 8px;
                font-weight: bold;
                font-family: '{Theme.FONT_FAMILY}';
                background: {Theme.ACCENT};
                border: none;
                padding: 1px 5px;
                border-radius: 2px;
            }}
        """)
        lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        val = QLabel(value)
        val.setWordWrap(wrap)
        val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        font_family = 'Consolas' if monospace else Theme.FONT_FAMILY
        val.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT};
                font-size: {Theme.FONT_SIZE_NORMAL}px;
                font-family: '{font_family}';
                background: transparent;
                padding: 4px 0;
            }}
        """)

        layout.addWidget(lbl)
        layout.addWidget(val)
        return container

    def _open_url(self):
        url = self._result['data']
        status = self._result['safety']['status']

        if status == 'malicious':
            reply = QMessageBox.warning(
                self,
                "Warning — Malicious URL",
                f"This URL has been flagged as malicious by {self._result['safety']['source']}.\n\n"
                f"Opening it may be dangerous.\n\nAre you sure you want to proceed?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        webbrowser.open(url)

    def _copy(self):
        QApplication.clipboard().setText(self._result['data'])


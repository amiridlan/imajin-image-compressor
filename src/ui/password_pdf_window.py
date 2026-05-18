from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QSizePolicy, QButtonGroup, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from ui.styles.theme import Theme
import qtawesome as qta


class _Worker(QThread):
    done    = pyqtSignal(str)
    error   = pyqtSignal(str)

    def __init__(self, mode, src, dest, password):
        super().__init__()
        self.mode = mode
        self.src = src
        self.dest = dest
        self.password = password

    def run(self):
        try:
            from core.pdf.password_pdf import add_password, remove_password
            if self.mode == 'add':
                add_password(self.src, self.dest, self.password)
            else:
                remove_password(self.src, self.dest, self.password)
            self.done.emit(self.dest)
        except ValueError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Unexpected error: {e}")


class PasswordPdfWindow(QWidget):
    def __init__(self, on_back=None, parent=None):
        super().__init__(parent)
        self._on_back = on_back
        self._src = ""
        self._worker = None
        self._mode = "add"
        self.setAcceptDrops(True)
        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_header())

        body = QWidget()
        body.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        body_layout = QVBoxLayout(body)
        body_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body_layout.setContentsMargins(60, 48, 60, 48)
        body_layout.setSpacing(24)

        # Mode toggle
        toggle_row = QHBoxLayout()
        toggle_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        toggle_row.setSpacing(0)

        self._btn_add = self._toggle_btn("Add Password", active=True)
        self._btn_remove = self._toggle_btn("Remove Password", active=False)
        self._btn_add.clicked.connect(lambda: self._set_mode("add"))
        self._btn_remove.clicked.connect(lambda: self._set_mode("remove"))

        toggle_row.addWidget(self._btn_add)
        toggle_row.addWidget(self._btn_remove)
        body_layout.addLayout(toggle_row)

        # Drop zone
        body_layout.addWidget(self._build_drop_zone())

        # Password field
        pw_label = QLabel("Password")
        pw_label.setStyleSheet(f"color: {Theme.TEXT}; font-family: '{Theme.FONT_FAMILY}'; font-size: 14px; background: transparent;")
        body_layout.addWidget(pw_label)

        self._pw_field = QLineEdit()
        self._pw_field.setEchoMode(QLineEdit.EchoMode.Password)
        self._pw_field.setPlaceholderText("Enter password…")
        self._pw_field.setFixedHeight(40)
        body_layout.addWidget(self._pw_field)

        # Confirm password (add mode only)
        self._confirm_label = QLabel("Confirm Password")
        self._confirm_label.setStyleSheet(f"color: {Theme.TEXT}; font-family: '{Theme.FONT_FAMILY}'; font-size: 14px; background: transparent;")
        self._confirm_field = QLineEdit()
        self._confirm_field.setEchoMode(QLineEdit.EchoMode.Password)
        self._confirm_field.setPlaceholderText("Re-enter password…")
        self._confirm_field.setFixedHeight(40)
        body_layout.addWidget(self._confirm_label)
        body_layout.addWidget(self._confirm_field)

        # Status label
        self._status = QLabel("")
        self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status.setWordWrap(True)
        self._status.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-family: '{Theme.FONT_FAMILY}'; font-size: 14px; background: transparent;")
        body_layout.addWidget(self._status)

        # Action button
        self._run_btn = QPushButton("Apply")
        self._run_btn.setFixedHeight(44)
        self._run_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.ACCENT};
                color: {Theme.TEXT};
                border: none;
                border-radius: {Theme.RADIUS_MD}px;
                font-family: '{Theme.FONT_FAMILY}';
                font-weight: bold;
                font-size: 15px;
            }}
            QPushButton:hover {{ background-color: {Theme.ACCENT_LIGHT}; }}
            QPushButton:disabled {{ background-color: {Theme.DISABLED_BG}; color: {Theme.DISABLED_TEXT}; }}
        """)
        self._run_btn.clicked.connect(self._run)
        body_layout.addWidget(self._run_btn)

        root.addWidget(body)

    def _build_header(self):
        header = QWidget()
        header.setObjectName("headerBar")
        header.setFixedHeight(48)
        header.setStyleSheet(f"""
            QWidget#headerBar {{
                background-color: {Theme.BG_SECONDARY};
                border-bottom: 2px solid {Theme.ACCENT};
            }}
        """)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(12, 0, 16, 0)

        back_btn = QPushButton()
        back_btn.setIcon(qta.icon('fa5s.arrow-left', color=Theme.TEXT))
        back_btn.setFixedSize(36, 36)
        back_btn.setStyleSheet("border: none; background: transparent;")
        back_btn.clicked.connect(self._go_back)

        title = QLabel("Password PDF")
        title.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT};
                font-size: {Theme.FONT_SIZE_TITLE}px;
                font-weight: bold;
                font-family: '{Theme.FONT_DISPLAY}';
                background: transparent;
            }}
        """)

        layout.addWidget(back_btn)
        layout.addSpacing(8)
        layout.addWidget(title)
        layout.addStretch()
        return header

    def _toggle_btn(self, text, active):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(active)
        btn.setFixedHeight(38)
        btn.setMinimumWidth(160)
        self._refresh_toggle_style(btn, active)
        return btn

    def _refresh_toggle_style(self, btn, active):
        if active:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Theme.ACCENT};
                    color: {Theme.TEXT};
                    border: 2px solid {Theme.ACCENT};
                    border-radius: 0px;
                    font-family: '{Theme.FONT_FAMILY}';
                    font-weight: bold;
                    font-size: 14px;
                    padding: 0 20px;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Theme.BG_SECONDARY};
                    color: {Theme.TEXT_MUTED};
                    border: 2px solid {Theme.BG_SECONDARY};
                    border-radius: 0px;
                    font-family: '{Theme.FONT_FAMILY}';
                    font-size: 14px;
                    padding: 0 20px;
                }}
                QPushButton:hover {{ color: {Theme.TEXT}; border-color: {Theme.ACCENT}; }}
            """)

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def _set_mode(self, mode):
        self._mode = mode
        self._refresh_toggle_style(self._btn_add, mode == "add")
        self._refresh_toggle_style(self._btn_remove, mode == "remove")
        show_confirm = mode == "add"
        self._confirm_label.setVisible(show_confirm)
        self._confirm_field.setVisible(show_confirm)
        self._pw_field.setPlaceholderText(
            "Enter new password…" if mode == "add" else "Enter current password…"
        )
        self._status.setText("")

    def _build_drop_zone(self):
        frame = QFrame()
        frame.setFixedHeight(72)
        frame.setStyleSheet(f"""
            QFrame {{
                border: 2px dashed {Theme.TEXT};
                border-radius: {Theme.RADIUS_LG}px;
                background-color: transparent;
            }}
        """)
        row = QHBoxLayout(frame)
        row.setContentsMargins(16, 0, 16, 0)
        row.setSpacing(12)

        self._file_label = QLabel("⬇  DROP PDF HERE")
        self._file_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_MUTED};
                font-size: 14px;
                font-weight: bold;
                font-family: '{Theme.FONT_FAMILY}';
                background: transparent;
                border: none;
            }}
        """)

        or_lbl = QLabel("or")
        or_lbl.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-family: '{Theme.FONT_FAMILY}'; background: transparent; border: none;")

        browse_btn = QPushButton("Browse PDF")
        browse_btn.setFixedWidth(110)
        browse_btn.clicked.connect(self._browse_file)

        row.addStretch()
        row.addWidget(self._file_label)
        row.addWidget(or_lbl)
        row.addWidget(browse_btn)
        row.addStretch()
        return frame

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if path:
            self._load_file(path)

    def _load_file(self, path):
        self._src = path
        self._file_label.setText(f"  {path.split('/')[-1].split(chr(92))[-1]}")
        self._file_label.setStyleSheet(self._file_label.styleSheet().replace(
            Theme.TEXT_MUTED, Theme.TEXT))
        self._status.setText("")

    # Drag & drop
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        paths = [u.toLocalFile() for u in event.mimeData().urls()
                 if u.toLocalFile().lower().endswith('.pdf')]
        if paths:
            self._load_file(paths[0])

    def _run(self):
        if not self._src:
            self._set_status("Please select a PDF file.", error=True)
            return
        pw = self._pw_field.text()
        if not pw:
            self._set_status("Please enter a password.", error=True)
            return
        if self._mode == "add" and pw != self._confirm_field.text():
            self._set_status("Passwords do not match.", error=True)
            return

        from core.pdf.password_pdf import suggested_output
        dest = suggested_output(self._src, self._mode)

        self._run_btn.setEnabled(False)
        self._set_status("Working…", error=False)

        self._worker = _Worker(self._mode, self._src, dest, pw)
        self._worker.done.connect(self._on_done)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_done(self, dest):
        self._run_btn.setEnabled(True)
        action = "protected" if self._mode == "add" else "unlocked"
        self._set_status(f"Saved: {dest}", error=False, success=True)

    def _on_error(self, msg):
        self._run_btn.setEnabled(True)
        self._set_status(msg, error=True)

    def _set_status(self, msg, error=False, success=False):
        color = Theme.ERROR if error else (Theme.SUCCESS if success else Theme.TEXT_MUTED)
        self._status.setStyleSheet(f"color: {color}; font-family: '{Theme.FONT_FAMILY}'; font-size: 14px; background: transparent;")
        self._status.setText(msg)

    def _go_back(self):
        if self._on_back:
            self._on_back()

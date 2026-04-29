import json
import os

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFileDialog, QListWidget, QListWidgetItem,
                              QFrame, QSizePolicy, QProgressBar, QMessageBox,
                              QStackedWidget, QLineEdit, QScrollArea,
                              QPushButton, QApplication)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QColor, QPixmap

from ui.components.animated_button import AnimatedButton, PrimaryButton, DangerButton
from ui.styles.theme import Theme
from utils.file_utils import format_file_size, filter_files_by_ext

_ACCEPTED = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.tif', '.pdf')

_STATUS_COLOR = {
    'malicious': Theme.ERROR,
    'safe':      Theme.SUCCESS,
    'unknown':   Theme.WARNING,
}
_STATUS_ICON = {
    'malicious': '⚠',
    'safe':      '✓',
    'unknown':   '?',
}

CONFIG_FILE = 'config.json'


class QrScannerWindow(QWidget):
    def __init__(self, on_back=None, parent=None):
        super().__init__(parent)
        self.on_back = on_back

        # state
        self._scan_worker  = None
        self._camera_worker = None
        self._results: list = []
        self._current_file  = None
        self._camera_running = False
        self._next_result_index = 1   # running index for camera results

        self._init_ui()
        self._load_settings()
        self.setAcceptDrops(True)

        # Pre-load URLhaus in background
        QTimer.singleShot(500, self._preload_blocklist)

    # ==================================================================
    # UI construction
    # ==================================================================

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self._build_header())

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setSpacing(0)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.addWidget(self._build_left_panel(), 52)
        body_layout.addWidget(self._build_right_panel(), 48)
        root.addWidget(body, 1)

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------

    def _build_header(self):
        header = QWidget()
        header.setObjectName("headerBar")
        header.setFixedHeight(48)
        header.setStyleSheet(
            f"QWidget#headerBar {{ background-color: {Theme.TEXT}; border: none; }}"
        )
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 0, 16, 0)

        if self.on_back:
            back_btn = AnimatedButton("← BACK")
            back_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {Theme.BG_SECONDARY};
                    border: 1px solid {Theme.BG_SECONDARY};
                    border-radius: {Theme.RADIUS_SM}px;
                    padding: 4px 12px;
                    font-family: '{Theme.FONT_FAMILY}';
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {Theme.BG_SECONDARY};
                    color: {Theme.TEXT};
                }}
            """)
            back_btn.clicked.connect(self._safe_back)
            layout.addWidget(back_btn)
            layout.addSpacing(12)

        title = QLabel("QR SCANNER")
        title.setStyleSheet(f"""
            QLabel {{
                color: {Theme.ACCENT};
                font-size: {Theme.FONT_SIZE_TITLE}px;
                font-weight: bold;
                font-family: '{Theme.FONT_DISPLAY}';
                background-color: transparent;
            }}
        """)

        self.status_label = QLabel("READY_")
        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.BG_SECONDARY};
                font-size: 13px;
                font-family: '{Theme.FONT_DISPLAY}';
                background-color: transparent;
            }}
        """)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.status_label)
        return header

    # ------------------------------------------------------------------
    # Left panel — mode toggle + Camera / Upload pages
    # ------------------------------------------------------------------

    def _build_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 8, 16)

        layout.addWidget(self._build_mode_toggle())
        layout.addSpacing(2)

        # Stacked: 0 = camera page, 1 = upload page
        self.mode_stack = QStackedWidget()
        self.mode_stack.addWidget(self._build_camera_page())
        self.mode_stack.addWidget(self._build_upload_page())
        self.mode_stack.setCurrentIndex(0)
        layout.addWidget(self.mode_stack, 1)

        return panel

    def _build_mode_toggle(self):
        container = QWidget()
        container.setStyleSheet("QWidget { background-color: transparent; }")
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        def _style(active):
            if active:
                return f"""
                    QPushButton {{
                        background-color: {Theme.ACCENT};
                        color: {Theme.TEXT};
                        border: 2px solid {Theme.TEXT};
                        padding: 7px 22px;
                        font-family: '{Theme.FONT_FAMILY}';
                        font-weight: bold;
                        font-size: 15px;
                    }}
                """
            return f"""
                QPushButton {{
                    background-color: {Theme.BG_SECONDARY};
                    color: {Theme.TEXT};
                    border: 2px solid {Theme.TEXT};
                    padding: 7px 22px;
                    font-family: '{Theme.FONT_FAMILY}';
                    font-weight: bold;
                    font-size: 15px;
                }}
                QPushButton:hover {{ background-color: {Theme.BG_PRIMARY}; }}
            """

        self.btn_camera = AnimatedButton("📷  Camera")
        self.btn_camera.setStyleSheet(
            _style(True) + f"QPushButton {{ border-top-left-radius: {Theme.RADIUS_MD}px; border-bottom-left-radius: {Theme.RADIUS_MD}px; }}"
        )
        self.btn_camera.clicked.connect(lambda: self._set_mode(0))

        self.btn_upload = AnimatedButton("📂  Upload")
        self.btn_upload.setStyleSheet(
            _style(False) + f"QPushButton {{ border-top-right-radius: {Theme.RADIUS_MD}px; border-bottom-right-radius: {Theme.RADIUS_MD}px; }}"
        )
        self.btn_upload.clicked.connect(lambda: self._set_mode(1))

        self._mode_active_style   = _style(True)
        self._mode_inactive_style = _style(False)

        row.addWidget(self.btn_camera)
        row.addWidget(self.btn_upload)
        row.addStretch()
        return container

    def _set_mode(self, index):
        if index == 0 and self.mode_stack.currentIndex() == 1:
            self._stop_camera()   # safety
        if index == 1 and self._camera_running:
            self._stop_camera()

        self.mode_stack.setCurrentIndex(index)

        active   = self._mode_active_style
        inactive = self._mode_inactive_style
        left_r   = f"border-top-left-radius: {Theme.RADIUS_MD}px; border-bottom-left-radius: {Theme.RADIUS_MD}px;"
        right_r  = f"border-top-right-radius: {Theme.RADIUS_MD}px; border-bottom-right-radius: {Theme.RADIUS_MD}px;"

        if index == 0:
            self.btn_camera.setStyleSheet(active  + f"QPushButton {{ {left_r}  }}")
            self.btn_upload.setStyleSheet(inactive + f"QPushButton {{ {right_r} }}")
        else:
            self.btn_camera.setStyleSheet(inactive + f"QPushButton {{ {left_r}  }}")
            self.btn_upload.setStyleSheet(active   + f"QPushButton {{ {right_r} }}")

    # ------------------------------------------------------------------
    # Camera page
    # ------------------------------------------------------------------

    def _build_camera_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        # Viewfinder
        self.viewfinder = QLabel()
        self.viewfinder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.viewfinder.setMinimumHeight(260)
        self.viewfinder.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.viewfinder.setStyleSheet(f"""
            QLabel {{
                background-color: {Theme.TEXT};
                border: 2px solid {Theme.TEXT};
                border-radius: {Theme.RADIUS_LG}px;
                color: {Theme.BG_SECONDARY};
                font-family: '{Theme.FONT_FAMILY}';
                font-size: 15px;
            }}
        """)
        self.viewfinder.setText("Camera not started")
        layout.addWidget(self.viewfinder, 1)

        # Camera controls row
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(8)

        self.start_camera_btn = PrimaryButton("▶  Start Camera", icon_name=None)
        self.start_camera_btn.setMinimumHeight(40)
        self.start_camera_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.start_camera_btn.clicked.connect(self._toggle_camera)

        self.clear_camera_btn = AnimatedButton("Clear", icon_name="fa5s.broom")
        self.clear_camera_btn.clicked.connect(self._clear_results)

        ctrl_row.addWidget(self.start_camera_btn, 1)
        ctrl_row.addWidget(self.clear_camera_btn)
        layout.addLayout(ctrl_row)

        # Device index
        dev_row = QHBoxLayout()
        dev_lbl = QLabel("Camera index:")
        dev_lbl.setStyleSheet(f"QLabel {{ color: {Theme.TEXT}; font-size: 13px; font-family: '{Theme.FONT_FAMILY}'; background: transparent; }}")
        self.camera_index_input = QLineEdit("0")
        self.camera_index_input.setFixedWidth(48)
        self.camera_index_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Theme.INPUT_BG};
                color: {Theme.TEXT};
                border: 2px solid {Theme.BG_SECONDARY};
                border-radius: {Theme.RADIUS_SM}px;
                padding: 3px 6px;
                font-family: '{Theme.FONT_FAMILY}';
                font-size: 13px;
            }}
        """)
        self.camera_index_input.textChanged.connect(self._save_settings)
        dev_row.addWidget(dev_lbl)
        dev_row.addWidget(self.camera_index_input)
        dev_row.addStretch()
        layout.addLayout(dev_row)

        return page

    def _toggle_camera(self):
        if self._camera_running:
            self._stop_camera()
        else:
            self._start_camera()

    def _start_camera(self):
        from core.qr.camera_worker import CameraWorker
        try:
            idx = int(self.camera_index_input.text())
        except ValueError:
            idx = 0

        vt_key = self.vt_key_input.text().strip()

        self._camera_worker = CameraWorker(device_index=idx, virustotal_key=vt_key)
        self._camera_worker.frame_ready.connect(self._on_frame)
        self._camera_worker.qr_detected.connect(self._on_camera_qr)
        self._camera_worker.camera_error.connect(self._on_camera_error)
        self._camera_worker.start()

        self._camera_running = True
        self._next_result_index = self.results_list.count() + 1
        self.start_camera_btn.setText("■  Stop Camera")
        self.status_label.setText("CAMERA ACTIVE_")

    def _stop_camera(self):
        if self._camera_worker:
            self._camera_worker.stop()
            self._camera_worker.wait(2000)
            self._camera_worker = None
        self._camera_running = False
        self.start_camera_btn.setText("▶  Start Camera")
        self.viewfinder.setText("Camera not started")
        self.viewfinder.setPixmap(QPixmap())
        self.status_label.setText("CAMERA STOPPED_")

    def _on_frame(self, qt_image):
        pixmap = QPixmap.fromImage(qt_image)
        scaled = pixmap.scaled(
            self.viewfinder.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.viewfinder.setPixmap(scaled)

    def _on_camera_qr(self, codes: list):
        self.empty_label.setVisible(False)
        for code in codes:
            code['index'] = self._next_result_index
            self._next_result_index += 1
            self._results.append(code)
            self._add_result_item(code)

        count = self.results_list.count()
        self.status_label.setText(f"{count} QR CODE{'S' if count > 1 else ''} FOUND_")

    def _on_camera_error(self, msg: str):
        self._stop_camera()
        QMessageBox.warning(self, "Camera Error", msg)

    # ------------------------------------------------------------------
    # Upload page
    # ------------------------------------------------------------------

    def _build_upload_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._build_drop_zone())
        layout.addWidget(self._build_file_info())

        layout.addSpacing(4)
        layout.addWidget(self._section_label("// BLOCKLIST STATUS //"))
        self.blocklist_label = QLabel("Checking…")
        self.blocklist_label.setStyleSheet(f"QLabel {{ color: {Theme.TEXT}; font-size: 13px; font-family: '{Theme.FONT_FAMILY}'; background: transparent; padding: 2px 0; }}")
        layout.addWidget(self.blocklist_label)

        layout.addStretch()

        self.scan_btn = PrimaryButton("SCAN FOR QR CODES", icon_name="fa5s.search")
        self.scan_btn.setMinimumHeight(46)
        self.scan_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.scan_btn.clicked.connect(self._start_scan)
        self.scan_btn.setEnabled(False)
        layout.addWidget(self.scan_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        return page

    def _build_drop_zone(self):
        frame = QFrame()
        frame.setFixedHeight(110)
        frame.setStyleSheet(f"""
            QFrame {{
                border: 2px dashed {Theme.TEXT};
                border-radius: {Theme.RADIUS_LG}px;
                background-color: transparent;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)

        drop_label = QLabel("⬇  DROP IMAGE OR PDF HERE")
        drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT};
                font-size: 14px;
                font-weight: bold;
                font-family: '{Theme.FONT_FAMILY}';
                background-color: transparent;
                border: none;
            }}
        """)

        or_label = QLabel("or")
        or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        or_label.setStyleSheet(f"QLabel {{ color: {Theme.TEXT}; font-size: 15px; font-family: '{Theme.FONT_FAMILY}'; background: transparent; border: none; }}")

        browse_btn = AnimatedButton("Browse File", icon_name="fa5s.folder-open")
        browse_btn.clicked.connect(self._browse_file)

        layout.addWidget(drop_label)
        layout.addWidget(or_label)
        layout.addWidget(browse_btn, 0, Qt.AlignmentFlag.AlignCenter)
        return frame

    def _build_file_info(self):
        self.file_info_label = QLabel("No file selected")
        self.file_info_label.setStyleSheet(f"QLabel {{ color: {Theme.TEXT}; font-size: 13px; font-family: '{Theme.FONT_FAMILY}'; background: transparent; padding: 3px 0; }}")
        return self.file_info_label

    # ------------------------------------------------------------------
    # Right panel — results + settings
    # ------------------------------------------------------------------

    def _build_right_panel(self):
        panel = QWidget()
        panel.setObjectName("rightPanel")

        layout = QVBoxLayout(panel)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 16, 16, 16)

        layout.addWidget(self._section_label("// DETECTED QR CODES //"))

        self.results_list = QListWidget()
        self.results_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {Theme.INPUT_BG};
                color: {Theme.TEXT};
                border: 2px solid {Theme.BG_SECONDARY};
                border-radius: {Theme.RADIUS_MD}px;
                font-family: '{Theme.FONT_FAMILY}';
                font-size: 15px;
            }}
            QListWidget::item {{
                padding: 7px 10px;
                border-bottom: 1px solid {Theme.BG_PRIMARY};
            }}
            QListWidget::item:selected {{
                background-color: {Theme.BG_SECONDARY};
                color: {Theme.TEXT};
            }}
            QListWidget::item:hover {{ background-color: {Theme.BG_PRIMARY}; }}
        """)
        self.results_list.itemDoubleClicked.connect(self._open_result_dialog)
        layout.addWidget(self.results_list, 1)

        self.empty_label = QLabel("No QR codes detected yet.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(f"QLabel {{ color: {Theme.TEXT}; font-family: '{Theme.FONT_FAMILY}'; font-size: 15px; background: transparent; }}")
        layout.addWidget(self.empty_label)

        # Divider
        div = QFrame()
        div.setFixedHeight(2)
        div.setStyleSheet(f"background-color: {Theme.TEXT}; border: none;")
        layout.addWidget(div)

        layout.addWidget(self._section_label("// SETTINGS //"))
        layout.addLayout(self._build_vt_row())

        return panel

    def _build_vt_row(self):
        row = QVBoxLayout()
        row.setSpacing(4)

        lbl = QLabel("VirusTotal API Key (optional):")
        lbl.setStyleSheet(f"QLabel {{ color: {Theme.TEXT}; font-size: 13px; font-family: '{Theme.FONT_FAMILY}'; background: transparent; }}")

        self.vt_key_input = QLineEdit()
        self.vt_key_input.setPlaceholderText("Paste your VirusTotal API key for live scanning…")
        self.vt_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.vt_key_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Theme.INPUT_BG};
                color: {Theme.TEXT};
                border: 2px solid {Theme.BG_SECONDARY};
                border-radius: {Theme.RADIUS_SM}px;
                padding: 5px;
                font-family: '{Theme.FONT_FAMILY}';
                font-size: 13px;
            }}
            QLineEdit:focus {{ border: 2px solid {Theme.ACCENT}; }}
        """)
        self.vt_key_input.textChanged.connect(self._save_settings)

        row.addWidget(lbl)
        row.addWidget(self.vt_key_input)
        return row

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _section_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT};
                font-size: 13px;
                font-weight: bold;
                font-family: '{Theme.FONT_FAMILY}';
                background-color: {Theme.ACCENT};
                border: none;
                padding: 2px 6px;
                border-radius: {Theme.RADIUS_SM}px;
            }}
        """)
        lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        return lbl

    # ------------------------------------------------------------------
    # Drag & drop
    # ------------------------------------------------------------------

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        paths = [u.toLocalFile() for u in event.mimeData().urls()]
        valid = filter_files_by_ext(paths, _ACCEPTED)
        if valid:
            self._set_mode(1)
            self._set_file(valid[0])

    # ------------------------------------------------------------------
    # File selection (upload mode)
    # ------------------------------------------------------------------

    def _browse_file(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter(
            "Images & PDFs (*.jpg *.jpeg *.png *.bmp *.webp *.tiff *.tif *.pdf)"
        )
        if dialog.exec():
            self._set_file(dialog.selectedFiles()[0])

    def _set_file(self, path):
        self._current_file = path
        name = os.path.basename(path)
        size = format_file_size(os.path.getsize(path))
        self.file_info_label.setText(f"  {name}  ({size})")
        self.scan_btn.setEnabled(True)
        self._clear_results()
        self.status_label.setText("FILE LOADED_")

    # ------------------------------------------------------------------
    # Blocklist preload
    # ------------------------------------------------------------------

    def _preload_blocklist(self):
        try:
            from core.qr.urlhaus_list import get_blocklist, cache_size
            get_blocklist()
            n = cache_size()
            self.blocklist_label.setText(f"URLhaus: {n:,} threats loaded")
        except Exception:
            self.blocklist_label.setText("URLhaus: unavailable (offline?)")

    # ------------------------------------------------------------------
    # Upload scan
    # ------------------------------------------------------------------

    def _start_scan(self):
        if not self._current_file or (self._scan_worker and self._scan_worker.isRunning()):
            return

        from core.qr.scan_worker import QrScanWorker
        vt_key = self.vt_key_input.text().strip()
        self._scan_worker = QrScanWorker(self._current_file, virustotal_key=vt_key)
        self._scan_worker.scan_completed.connect(self._on_scan_completed)
        self._scan_worker.scan_failed.connect(self._on_scan_failed)
        self._scan_worker.status_update.connect(self.status_label.setText)

        self._clear_results()
        self.scan_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self._scan_worker.start()

    def _clear_results(self):
        self.results_list.clear()
        self._results = []
        self._next_result_index = 1
        self.empty_label.setVisible(True)
        self.empty_label.setText("No QR codes detected yet.")

    def _on_scan_completed(self, results):
        self.progress_bar.setVisible(False)
        self.scan_btn.setEnabled(True)
        self._results = results

        if not results:
            self.status_label.setText("NO QR CODES FOUND_")
            self.empty_label.setText("No QR codes found in this file.")
            return

        self.empty_label.setVisible(False)
        for r in results:
            self._add_result_item(r)
        count = len(results)
        self.status_label.setText(f"{count} QR CODE{'S' if count > 1 else ''} FOUND_")

    def _on_scan_failed(self, error):
        self.progress_bar.setVisible(False)
        self.scan_btn.setEnabled(True)
        self.status_label.setText("SCAN FAILED_")
        QMessageBox.critical(self, "Scan Failed", f"Could not scan file:\n\n{error}")

    # ------------------------------------------------------------------
    # Result list
    # ------------------------------------------------------------------

    def _add_result_item(self, result):
        status = result['safety']['status']
        icon   = _STATUS_ICON.get(status, '?')
        color  = _STATUS_COLOR.get(status, Theme.TEXT)

        data      = result['data']
        page_info = f"  [p.{result['page']}]" if result.get('page') else ''
        short     = data[:52] + '…' if len(data) > 52 else data
        label_txt = f"{result['index']}.  {icon}  {short}{page_info}"

        # Custom row widget: colored label + copy button
        row = QWidget()
        row.setStyleSheet("QWidget { background: transparent; }")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(10, 6, 8, 6)
        row_layout.setSpacing(8)

        lbl = QLabel(label_txt)
        lbl.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-family: '{Theme.FONT_FAMILY}';
                font-size: {Theme.FONT_SIZE_NORMAL}px;
                background: transparent;
                border: none;
            }}
        """)
        lbl.setWordWrap(False)

        copy_btn = QPushButton("COPY")
        copy_btn.setFixedSize(58, 26)
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.TEXT_MUTED};
                border: 1px solid {Theme.BG_SECONDARY};
                border-radius: 4px;
                font-family: '{Theme.FONT_FAMILY}';
                font-size: 10px;
                font-weight: bold;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {Theme.ACCENT};
                color: {Theme.BG_PRIMARY};
                border-color: {Theme.ACCENT};
            }}
            QPushButton:pressed {{
                background-color: {Theme.TEXT};
                color: {Theme.BG_PRIMARY};
            }}
        """)
        copy_btn.clicked.connect(lambda _, d=data: (
            QApplication.clipboard().setText(d),
            copy_btn.setText("✓"),
            QTimer.singleShot(1200, lambda: copy_btn.setText("COPY"))
        ))

        row_layout.addWidget(lbl, 1)
        row_layout.addWidget(copy_btn, 0)

        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, result)
        item.setSizeHint(QSize(0, 42))
        self.results_list.addItem(item)
        self.results_list.setItemWidget(item, row)

    # ------------------------------------------------------------------
    # Result dialog
    # ------------------------------------------------------------------

    def _open_result_dialog(self, item):
        result = item.data(Qt.ItemDataRole.UserRole)
        if result is None:
            return
        from ui.dialogs.qr_result_dialog import QrResultDialog
        QrResultDialog(result, parent=self).exec()

    # ------------------------------------------------------------------
    # Settings persistence
    # ------------------------------------------------------------------

    def _load_settings(self):
        if not os.path.exists(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, 'r') as f:
                cfg = json.load(f)
            self.vt_key_input.setText(cfg.get('virustotal_api_key', ''))
            self.camera_index_input.setText(str(cfg.get('camera_device_index', 0)))
        except Exception:
            pass

    def _save_settings(self):
        try:
            cfg = {}
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    cfg = json.load(f)
            cfg['virustotal_api_key'] = self.vt_key_input.text()
            try:
                cfg['camera_device_index'] = int(self.camera_index_input.text())
            except ValueError:
                cfg['camera_device_index'] = 0
            with open(CONFIG_FILE, 'w') as f:
                json.dump(cfg, f, indent=4)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Safe back — stop camera first
    # ------------------------------------------------------------------

    def _safe_back(self):
        if self._camera_running:
            self._stop_camera()
        if self.on_back:
            self.on_back()

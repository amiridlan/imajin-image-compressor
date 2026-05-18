from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog, QSizePolicy,
    QAbstractItemView, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap, QDragEnterEvent, QDropEvent
from ui.styles.theme import Theme
import qtawesome as qta


class _ThumbnailLoader(QThread):
    page_ready = pyqtSignal(int, QPixmap)  # original_index, pixmap

    def __init__(self, src, page_count):
        super().__init__()
        self.src = src
        self.page_count = page_count

    def run(self):
        from core.pdf.organize_pdf import render_page_thumbnail
        for i in range(self.page_count):
            pix = render_page_thumbnail(self.src, i, max_size=140)
            self.page_ready.emit(i, pix)


class _SaveWorker(QThread):
    done  = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, src, dest, order, rotations):
        super().__init__()
        self.src = src
        self.dest = dest
        self.order = order
        self.rotations = rotations

    def run(self):
        try:
            from core.pdf.organize_pdf import save_reordered
            save_reordered(self.src, self.dest, self.order, self.rotations)
            self.done.emit(self.dest)
        except Exception as e:
            self.error.emit(str(e))


class OrganizePdfWindow(QWidget):
    def __init__(self, on_back=None, parent=None):
        super().__init__(parent)
        self._on_back = on_back
        self._src = ""
        self._page_count = 0
        self._rotations = {}     # orig_idx → extra rotation (0/90/180/270)
        self._thumb_loader = None
        self._save_worker = None
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
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(24, 24, 24, 24)
        body_layout.setSpacing(16)

        # Drop zone
        body_layout.addWidget(self._build_drop_zone())

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        toolbar.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self._rotate_l_btn = self._tool_btn('fa5s.undo-alt', "Rotate CCW")
        self._rotate_r_btn = self._tool_btn('fa5s.redo-alt', "Rotate CW")
        self._del_btn      = self._tool_btn('fa5s.trash-alt', "Delete Page")
        self._up_btn       = self._tool_btn('fa5s.arrow-up', "Move Up")
        self._down_btn     = self._tool_btn('fa5s.arrow-down', "Move Down")

        self._rotate_l_btn.clicked.connect(lambda: self._rotate_selected(-90))
        self._rotate_r_btn.clicked.connect(lambda: self._rotate_selected(90))
        self._del_btn.clicked.connect(self._delete_selected)
        self._up_btn.clicked.connect(lambda: self._move_selected(-1))
        self._down_btn.clicked.connect(lambda: self._move_selected(1))

        for btn in (self._rotate_l_btn, self._rotate_r_btn,
                    self._del_btn, self._up_btn, self._down_btn):
            toolbar.addWidget(btn)
            btn.setEnabled(False)

        toolbar.addStretch()
        self._page_count_label = QLabel("")
        self._page_count_label.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-family: '{Theme.FONT_FAMILY}'; font-size: 13px; background: transparent;")
        toolbar.addWidget(self._page_count_label)
        body_layout.addLayout(toolbar)

        # Page list (icon view for thumbnails)
        self._list = QListWidget()
        self._list.setViewMode(QListWidget.ViewMode.IconMode)
        self._list.setIconSize(QSize(140, 180))
        self._list.setGridSize(QSize(160, 220))
        self._list.setMovement(QListWidget.Movement.Snap)
        self._list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self._list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self._list.setStyleSheet(f"""
            QListWidget {{
                background-color: {Theme.INPUT_BG};
                border: 2px solid {Theme.BG_SECONDARY};
                border-radius: {Theme.RADIUS_MD}px;
            }}
            QListWidget::item {{
                color: {Theme.TEXT};
                font-family: '{Theme.FONT_FAMILY}';
                font-size: 12px;
                padding: 4px;
                border: 1px solid transparent;
            }}
            QListWidget::item:selected {{
                background-color: {Theme.BG_SECONDARY};
                border: 1px solid {Theme.ACCENT};
                border-radius: 4px;
            }}
        """)
        self._list.currentRowChanged.connect(self._on_selection_changed)
        body_layout.addWidget(self._list, 1)

        # Status + save
        bottom = QHBoxLayout()
        self._status = QLabel("")
        self._status.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-family: '{Theme.FONT_FAMILY}'; font-size: 13px; background: transparent;")
        self._save_btn = QPushButton("Save Organized PDF")
        self._save_btn.setFixedHeight(40)
        self._save_btn.setEnabled(False)
        self._save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.ACCENT};
                color: {Theme.TEXT};
                border: none;
                border-radius: {Theme.RADIUS_MD}px;
                font-family: '{Theme.FONT_FAMILY}';
                font-weight: bold;
                font-size: 14px;
                padding: 0 24px;
            }}
            QPushButton:hover {{ background-color: {Theme.ACCENT_LIGHT}; }}
            QPushButton:disabled {{ background-color: {Theme.DISABLED_BG}; color: {Theme.DISABLED_TEXT}; }}
        """)
        self._save_btn.clicked.connect(self._save)
        bottom.addWidget(self._status, 1)
        bottom.addWidget(self._save_btn)
        body_layout.addLayout(bottom)

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

        title = QLabel("Organize PDF")
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

    def _tool_btn(self, icon_name, tooltip):
        btn = QPushButton()
        btn.setIcon(qta.icon(icon_name, color=Theme.TEXT))
        btn.setFixedSize(36, 36)
        btn.setToolTip(tooltip)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {Theme.BG_SECONDARY};
                border: 1px solid rgba(240,230,255,30);
                border-radius: 6px;
            }}
            QPushButton:hover {{ border-color: {Theme.ACCENT}; }}
            QPushButton:disabled {{ opacity: 0.4; }}
        """)
        return btn

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

        open_btn = QPushButton("Open PDF")
        open_btn.setFixedWidth(110)
        open_btn.clicked.connect(self._open_file)

        row.addStretch()
        row.addWidget(self._file_label)
        row.addWidget(or_lbl)
        row.addWidget(open_btn)
        row.addStretch()
        return frame

    # ------------------------------------------------------------------
    # File loading
    # ------------------------------------------------------------------

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if path:
            self._load_file(path)

    def _load_file(self, path):
        self._src = path
        name = path.split('/')[-1].split('\\')[-1]
        self._file_label.setText(f"  {name}")
        self._file_label.setStyleSheet(self._file_label.styleSheet().replace(
            Theme.TEXT_MUTED, Theme.TEXT))
        self._rotations.clear()
        self._list.clear()
        self._save_btn.setEnabled(False)
        self._set_status("Loading pages…")

        from pypdf import PdfReader
        self._page_count = len(PdfReader(path).pages)
        self._page_count_label.setText(f"{self._page_count} pages")

        # Load thumbnails in background
        self._thumb_loader = _ThumbnailLoader(path, self._page_count)
        self._thumb_loader.page_ready.connect(self._add_thumbnail)
        self._thumb_loader.finished.connect(self._thumbnails_done)
        self._thumb_loader.start()

    # Drag & drop
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        paths = [u.toLocalFile() for u in event.mimeData().urls()
                 if u.toLocalFile().lower().endswith('.pdf')]
        if paths:
            self._load_file(paths[0])

    def _add_thumbnail(self, orig_idx, pixmap):
        item = QListWidgetItem(QIcon(pixmap), f"Page {orig_idx + 1}")
        item.setData(Qt.ItemDataRole.UserRole, orig_idx)
        item.setSizeHint(QSize(160, 220))
        self._list.addItem(item)

    def _thumbnails_done(self):
        self._set_status("")
        self._save_btn.setEnabled(True)
        for btn in (self._rotate_l_btn, self._rotate_r_btn,
                    self._del_btn, self._up_btn, self._down_btn):
            btn.setEnabled(True)

    # ------------------------------------------------------------------
    # Page operations
    # ------------------------------------------------------------------

    def _current_row(self):
        return self._list.currentRow()

    def _on_selection_changed(self, row):
        pass

    def _rotate_selected(self, delta):
        row = self._current_row()
        if row < 0:
            return
        item = self._list.item(row)
        orig_idx = item.data(Qt.ItemDataRole.UserRole)
        current = self._rotations.get(orig_idx, 0)
        self._rotations[orig_idx] = (current + delta) % 360

        # Re-render thumbnail with rotation applied
        from core.pdf.organize_pdf import render_page_thumbnail
        from PyQt6.QtGui import QTransform
        pix = render_page_thumbnail(self._src, orig_idx, max_size=140)
        transform = QTransform().rotate(self._rotations[orig_idx])
        item.setIcon(QIcon(pix.transformed(transform)))

    def _delete_selected(self):
        row = self._current_row()
        if row < 0:
            return
        self._list.takeItem(row)
        remaining = self._list.count()
        self._page_count_label.setText(f"{remaining} pages")
        if remaining == 0:
            self._save_btn.setEnabled(False)

    def _move_selected(self, delta):
        row = self._current_row()
        new_row = row + delta
        if new_row < 0 or new_row >= self._list.count():
            return
        item = self._list.takeItem(row)
        self._list.insertItem(new_row, item)
        self._list.setCurrentRow(new_row)

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def _save(self):
        if self._list.count() == 0:
            self._set_status("No pages to save.", error=True)
            return

        order = [self._list.item(i).data(Qt.ItemDataRole.UserRole)
                 for i in range(self._list.count())]

        from core.pdf.organize_pdf import suggested_output
        dest, _ = QFileDialog.getSaveFileName(
            self, "Save As", suggested_output(self._src), "PDF Files (*.pdf)")
        if not dest:
            return

        self._save_btn.setEnabled(False)
        self._set_status("Saving…")
        self._save_worker = _SaveWorker(self._src, dest, order, self._rotations)
        self._save_worker.done.connect(lambda p: self._set_status(f"Saved: {p}", success=True))
        self._save_worker.done.connect(lambda: self._save_btn.setEnabled(True))
        self._save_worker.error.connect(lambda m: self._set_status(m, error=True))
        self._save_worker.error.connect(lambda: self._save_btn.setEnabled(True))
        self._save_worker.start()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _set_status(self, msg, error=False, success=False):
        color = Theme.ERROR if error else (Theme.SUCCESS if success else Theme.TEXT_MUTED)
        self._status.setStyleSheet(f"color: {color}; font-family: '{Theme.FONT_FAMILY}'; font-size: 13px; background: transparent;")
        self._status.setText(msg)

    def _go_back(self):
        if self._thumb_loader and self._thumb_loader.isRunning():
            self._thumb_loader.quit()
        if self._on_back:
            self._on_back()

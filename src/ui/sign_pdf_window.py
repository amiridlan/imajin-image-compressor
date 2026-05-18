from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QSizePolicy, QSpinBox, QFrame, QSplitter,
    QTabWidget, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint, QRect, QSize
from PyQt6.QtGui import (
    QPainter, QPen, QPixmap, QColor, QCursor, QImage,
    QDragEnterEvent, QDropEvent
)
from ui.styles.theme import Theme
import qtawesome as qta


# ──────────────────────────────────────────────────────────────────────
# Signature draw pad
# ──────────────────────────────────────────────────────────────────────

class SignaturePad(QWidget):
    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(420, 160)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self._canvas = QPixmap(420, 160)
        self._canvas.fill(QColor(Theme.INPUT_BG))
        self._last = None
        self._drawing = False
        self._pen_color = QColor(Theme.TEXT)

    def paintEvent(self, _):
        p = QPainter(self)
        p.drawPixmap(0, 0, self._canvas)
        # Border
        p.setPen(QPen(QColor(Theme.BG_SECONDARY), 2))
        p.drawRect(self.rect().adjusted(1, 1, -1, -1))

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drawing = True
            self._last = e.position().toPoint()

    def mouseMoveEvent(self, e):
        if self._drawing and self._last:
            cur = e.position().toPoint()
            p = QPainter(self._canvas)
            pen = QPen(self._pen_color, 2, Qt.PenStyle.SolidLine,
                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            p.setPen(pen)
            p.drawLine(self._last, cur)
            p.end()
            self._last = cur
            self.update()
            self.changed.emit()

    def mouseReleaseEvent(self, e):
        self._drawing = False
        self._last = None

    def clear(self):
        self._canvas.fill(QColor(Theme.INPUT_BG))
        self.update()
        self.changed.emit()

    def get_pixmap(self):
        """Return canvas with transparent background where the bg color was."""
        result = QPixmap(self._canvas.size())
        result.fill(Qt.GlobalColor.transparent)
        p = QPainter(result)
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        p.drawPixmap(0, 0, self._canvas)
        p.end()

        # Make INPUT_BG pixels transparent
        img = result.toImage().convertToFormat(QImage.Format.Format_ARGB32)
        bg = QColor(Theme.INPUT_BG)
        bg_rgb = (bg.red(), bg.green(), bg.blue())
        for y in range(img.height()):
            for x in range(img.width()):
                c = QColor(img.pixel(x, y))
                if (c.red(), c.green(), c.blue()) == bg_rgb:
                    img.setPixelColor(x, y, QColor(0, 0, 0, 0))
        return QPixmap.fromImage(img)

    def is_empty(self):
        img = self._canvas.toImage()
        bg = QColor(Theme.INPUT_BG).rgb()
        for y in range(img.height()):
            for x in range(img.width()):
                if img.pixel(x, y) != bg:
                    return False
        return True


# ──────────────────────────────────────────────────────────────────────
# Page preview with draggable/resizable signature overlay
# ──────────────────────────────────────────────────────────────────────

class PagePreview(QWidget):
    """Shows a PDF page and lets the user drag-place a signature rectangle."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 500)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._page_pix  = None    # QPixmap of the rendered page
        self._sig_pix   = None    # QPixmap of the signature
        self._scale     = 1.0     # px per PDF point
        self._page_rect = QRect() # where the page is drawn inside the widget

        # Signature placement in page pixels
        self._sig_rect  = QRect(40, 40, 200, 80)
        self._dragging  = False
        self._drag_off  = QPoint()
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def set_page(self, pixmap, scale):
        self._page_pix = pixmap
        self._scale = scale
        self._center_page()
        self.update()

    def set_signature(self, pixmap):
        self._sig_pix = pixmap
        self.update()

    def _center_page(self):
        if not self._page_pix:
            return
        pw, ph = self._page_pix.width(), self._page_pix.height()
        x = (self.width() - pw) // 2
        y = (self.height() - ph) // 2
        self._page_rect = QRect(max(0, x), max(0, y), pw, ph)

    def resizeEvent(self, _):
        self._center_page()

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(Theme.BG_PRIMARY))

        if self._page_pix:
            p.drawPixmap(self._page_rect, self._page_pix)

            if self._sig_pix:
                r = self._sig_rect.translated(self._page_rect.topLeft())
                p.drawPixmap(r, self._sig_pix.scaled(
                    r.size(), Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation))
                # Dashed selection border
                pen = QPen(QColor(Theme.ACCENT), 1, Qt.PenStyle.DashLine)
                p.setPen(pen)
                p.drawRect(r)

    # Drag the signature box
    def mousePressEvent(self, e):
        if not self._sig_pix or not self._page_pix:
            return
        r = self._sig_rect.translated(self._page_rect.topLeft())
        if r.contains(e.position().toPoint()):
            self._dragging = True
            self._drag_off = e.position().toPoint() - r.topLeft()
            self.setCursor(Qt.CursorShape.SizeAllCursor)

    def mouseMoveEvent(self, e):
        if not self._dragging:
            return
        new_tl = e.position().toPoint() - self._drag_off - self._page_rect.topLeft()
        # Clamp inside page
        pw, ph = self._page_pix.width(), self._page_pix.height()
        nx = max(0, min(new_tl.x(), pw - self._sig_rect.width()))
        ny = max(0, min(new_tl.y(), ph - self._sig_rect.height()))
        self._sig_rect.moveTo(nx, ny)
        self.update()

    def mouseReleaseEvent(self, e):
        self._dragging = False
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def get_sig_rect_pts(self):
        """Return (x, y, w, h) in PDF points."""
        s = self._scale
        return (self._sig_rect.x() / s, self._sig_rect.y() / s,
                self._sig_rect.width() / s, self._sig_rect.height() / s)

    def set_sig_size_px(self, w, h):
        self._sig_rect.setSize(QSize(w, h))
        self.update()


# ──────────────────────────────────────────────────────────────────────
# Background save worker
# ──────────────────────────────────────────────────────────────────────

class _SaveWorker(QThread):
    done  = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, src, dest, page_idx, sig_pix, x, y, w, h):
        super().__init__()
        self.src = src
        self.dest = dest
        self.page_idx = page_idx
        self.sig_pix = sig_pix
        self.x, self.y, self.w, self.h = x, y, w, h

    def run(self):
        try:
            from core.pdf.sign_pdf import embed_signature
            embed_signature(self.src, self.dest, self.page_idx,
                            self.sig_pix, self.x, self.y, self.w, self.h)
            self.done.emit(self.dest)
        except Exception as e:
            self.error.emit(str(e))


# ──────────────────────────────────────────────────────────────────────
# Main window
# ──────────────────────────────────────────────────────────────────────

class SignPdfWindow(QWidget):
    def __init__(self, on_back=None, parent=None):
        super().__init__(parent)
        self._on_back    = on_back
        self._src        = ""
        self._page_count = 0
        self._page_scale = 1.0
        self._sig_pixmap = None   # final QPixmap to embed
        self._worker     = None
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

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: rgba(240,230,255,20); width: 2px; }")

        # ── Left panel: signature source + page selector ──
        left = QWidget()
        left.setMinimumWidth(440)
        left.setMaximumWidth(500)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(20, 20, 16, 20)
        left_layout.setSpacing(16)

        # Drop zone
        left_layout.addWidget(self._build_drop_zone())

        # Page selector
        page_row = QHBoxLayout()
        page_row.addWidget(QLabel("Sign page:"))
        self._page_spin = QSpinBox()
        self._page_spin.setMinimum(1)
        self._page_spin.setMaximum(1)
        self._page_spin.setFixedWidth(70)
        self._page_spin.setEnabled(False)
        self._page_spin.valueChanged.connect(self._load_page_preview)
        self._total_label = QLabel("of —")
        self._total_label.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-size: 13px; background: transparent;")
        page_row.addWidget(self._page_spin)
        page_row.addWidget(self._total_label)
        page_row.addStretch()
        left_layout.addLayout(page_row)

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"background: rgba(240,230,255,30); border: none;")
        left_layout.addWidget(divider)

        # Signature source tabs
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 2px solid {Theme.BG_SECONDARY};
                border-radius: {Theme.RADIUS_MD}px;
                background: {Theme.INPUT_BG};
            }}
            QTabBar::tab {{
                background: {Theme.BG_SECONDARY};
                color: {Theme.TEXT_MUTED};
                font-family: '{Theme.FONT_FAMILY}';
                font-size: 13px;
                padding: 6px 18px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background: {Theme.ACCENT};
                color: {Theme.TEXT};
            }}
        """)

        # Draw tab
        draw_tab = QWidget()
        draw_layout = QVBoxLayout(draw_tab)
        draw_layout.setContentsMargins(12, 12, 12, 12)
        draw_layout.setSpacing(10)

        lbl_draw = QLabel("Draw your signature below:")
        lbl_draw.setStyleSheet(f"color: {Theme.TEXT}; font-family: '{Theme.FONT_FAMILY}'; font-size: 13px; background: transparent;")
        draw_layout.addWidget(lbl_draw)

        self._pad = SignaturePad()
        draw_layout.addWidget(self._pad)

        clear_btn = QPushButton("Clear")
        clear_btn.setFixedWidth(80)
        clear_btn.clicked.connect(self._pad.clear)
        draw_layout.addWidget(clear_btn, 0, Qt.AlignmentFlag.AlignRight)
        draw_layout.addStretch()

        # Upload tab
        upload_tab = QWidget()
        upload_layout = QVBoxLayout(upload_tab)
        upload_layout.setContentsMargins(12, 12, 12, 12)
        upload_layout.setSpacing(10)

        lbl_up = QLabel("Upload a signature image (PNG/JPG):")
        lbl_up.setStyleSheet(f"color: {Theme.TEXT}; font-family: '{Theme.FONT_FAMILY}'; font-size: 13px; background: transparent;")
        upload_layout.addWidget(lbl_up)

        self._sig_preview = QLabel("No image loaded")
        self._sig_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sig_preview.setFixedHeight(120)
        self._sig_preview.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_MUTED};
                font-family: '{Theme.FONT_FAMILY}';
                font-size: 13px;
                background: {Theme.BG_PRIMARY};
                border: 1px dashed rgba(240,230,255,40);
                border-radius: 6px;
            }}
        """)
        upload_layout.addWidget(self._sig_preview)

        upload_btn = QPushButton("Browse Image…")
        upload_btn.clicked.connect(self._browse_sig_image)
        upload_layout.addWidget(upload_btn)
        upload_layout.addStretch()

        self._tabs.addTab(draw_tab, "Draw")
        self._tabs.addTab(upload_tab, "Upload Image")
        left_layout.addWidget(self._tabs, 1)

        # Signature size hint
        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Sig width (pt):"))
        self._sig_w_spin = QSpinBox()
        self._sig_w_spin.setRange(20, 400)
        self._sig_w_spin.setValue(180)
        self._sig_w_spin.setFixedWidth(70)
        size_row.addWidget(self._sig_w_spin)
        size_row.addSpacing(12)
        size_row.addWidget(QLabel("height (pt):"))
        self._sig_h_spin = QSpinBox()
        self._sig_h_spin.setRange(10, 200)
        self._sig_h_spin.setValue(60)
        self._sig_h_spin.setFixedWidth(70)
        size_row.addWidget(self._sig_h_spin)
        size_row.addStretch()
        left_layout.addLayout(size_row)

        # Apply + status
        self._apply_btn = QPushButton("Place Signature on Preview")
        self._apply_btn.setFixedHeight(40)
        self._apply_btn.setEnabled(False)
        self._apply_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Theme.BG_SECONDARY};
                color: {Theme.TEXT};
                border: 2px solid {Theme.ACCENT};
                border-radius: {Theme.RADIUS_MD}px;
                font-family: '{Theme.FONT_FAMILY}';
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{ background: {Theme.ACCENT}; }}
            QPushButton:disabled {{ border-color: {Theme.DISABLED_BORDER}; color: {Theme.DISABLED_TEXT}; }}
        """)
        self._apply_btn.clicked.connect(self._place_signature)
        left_layout.addWidget(self._apply_btn)

        self._save_btn = QPushButton("Save Signed PDF")
        self._save_btn.setFixedHeight(44)
        self._save_btn.setEnabled(False)
        self._save_btn.setStyleSheet(f"""
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
        self._save_btn.clicked.connect(self._save)
        left_layout.addWidget(self._save_btn)

        self._status = QLabel("")
        self._status.setWordWrap(True)
        self._status.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-family: '{Theme.FONT_FAMILY}'; font-size: 13px; background: transparent;")
        left_layout.addWidget(self._status)

        # ── Right panel: page preview ──
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 20, 20, 20)
        right_layout.setSpacing(8)

        preview_label = QLabel("Page Preview  ·  drag signature to position")
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_label.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-family: '{Theme.FONT_FAMILY}'; font-size: 12px; background: transparent;")
        right_layout.addWidget(preview_label)

        self._preview = PagePreview()
        right_layout.addWidget(self._preview, 1)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        root.addWidget(splitter, 1)

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
        title = QLabel("Sign PDF")
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

    # ------------------------------------------------------------------
    # File handling
    # ------------------------------------------------------------------

    def _build_drop_zone(self):
        frame = QFrame()
        frame.setFixedHeight(64)
        frame.setStyleSheet(f"""
            QFrame {{
                border: 2px dashed {Theme.TEXT};
                border-radius: {Theme.RADIUS_LG}px;
                background-color: transparent;
            }}
        """)
        row = QHBoxLayout(frame)
        row.setContentsMargins(12, 0, 12, 0)
        row.setSpacing(10)

        self._file_label = QLabel("⬇  DROP PDF HERE")
        self._file_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_MUTED};
                font-size: 13px;
                font-weight: bold;
                font-family: '{Theme.FONT_FAMILY}';
                background: transparent;
                border: none;
            }}
        """)

        or_lbl = QLabel("or")
        or_lbl.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-family: '{Theme.FONT_FAMILY}'; background: transparent; border: none;")

        browse_btn = QPushButton("Open PDF")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self._browse_pdf)

        row.addStretch()
        row.addWidget(self._file_label)
        row.addWidget(or_lbl)
        row.addWidget(browse_btn)
        row.addStretch()
        return frame

    def _browse_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if path:
            self._load_pdf(path)

    def _load_pdf(self, path):
        self._src = path
        name = path.split('/')[-1].split('\\')[-1]
        self._file_label.setText(f"  {name}")
        self._file_label.setStyleSheet(self._file_label.styleSheet().replace(
            Theme.TEXT_MUTED, Theme.TEXT))
        from core.pdf.sign_pdf import page_count
        self._page_count = page_count(path)
        self._page_spin.setMaximum(self._page_count)
        self._page_spin.setValue(1)
        self._page_spin.setEnabled(True)
        self._total_label.setText(f"of {self._page_count}")
        self._apply_btn.setEnabled(True)
        self._load_page_preview(1)

    def _load_page_preview(self, page_num):
        if not self._src:
            return
        from core.pdf.sign_pdf import render_page_preview
        pix, pw, ph, scale = render_page_preview(self._src, page_num - 1, max_size=560)
        self._page_scale = scale
        self._preview.set_page(pix, scale)
        self._set_status("")

    def _browse_sig_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Signature Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)")
        if path:
            self._load_sig_image(path)

    def _load_sig_image(self, path):
        pix = QPixmap(path)
        if pix.isNull():
            self._set_status("Could not load image.", error=True)
            return
        self._sig_preview.setPixmap(
            pix.scaled(360, 110, Qt.AspectRatioMode.KeepAspectRatio,
                       Qt.TransformationMode.SmoothTransformation))
        self._uploaded_sig = pix

    _IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.bmp', '.webp'}

    # Drag & drop — PDFs load as the document; images load as signature
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            ext = '.' + path.rsplit('.', 1)[-1].lower() if '.' in path else ''
            if path.lower().endswith('.pdf'):
                self._load_pdf(path)
                break
            elif ext in self._IMAGE_EXTS:
                self._tabs.setCurrentIndex(1)   # switch to Upload Image tab
                self._load_sig_image(path)
                break

    # ------------------------------------------------------------------
    # Signature placement
    # ------------------------------------------------------------------

    def _get_sig_pixmap(self):
        if self._tabs.currentIndex() == 0:
            if self._pad.is_empty():
                return None, "Draw a signature first."
            return self._pad.get_pixmap(), None
        else:
            if not hasattr(self, '_uploaded_sig'):
                return None, "Upload a signature image first."
            return self._uploaded_sig, None

    def _place_signature(self):
        if not self._src:
            self._set_status("Open a PDF first.", error=True)
            return
        pix, err = self._get_sig_pixmap()
        if err:
            self._set_status(err, error=True)
            return

        self._sig_pixmap = pix
        w_pt = self._sig_w_spin.value()
        h_pt = self._sig_h_spin.value()
        w_px = int(w_pt * self._page_scale)
        h_px = int(h_pt * self._page_scale)
        self._preview.set_sig_size_px(w_px, h_px)
        self._preview.set_signature(pix)
        self._save_btn.setEnabled(True)
        self._set_status("Drag the signature to your desired position, then click Save.")

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def _save(self):
        if not self._sig_pixmap:
            self._set_status("Place a signature first.", error=True)
            return

        from core.pdf.sign_pdf import suggested_output
        dest, _ = QFileDialog.getSaveFileName(
            self, "Save Signed PDF", suggested_output(self._src), "PDF Files (*.pdf)")
        if not dest:
            return

        x, y, w, h = self._preview.get_sig_rect_pts()
        page_idx = self._page_spin.value() - 1

        self._save_btn.setEnabled(False)
        self._set_status("Saving…")

        self._worker = _SaveWorker(self._src, dest, page_idx, self._sig_pixmap, x, y, w, h)
        self._worker.done.connect(lambda p: self._set_status(f"Saved: {p}", success=True))
        self._worker.done.connect(lambda: self._save_btn.setEnabled(True))
        self._worker.error.connect(lambda m: self._set_status(m, error=True))
        self._worker.error.connect(lambda: self._save_btn.setEnabled(True))
        self._worker.start()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _set_status(self, msg, error=False, success=False):
        color = Theme.ERROR if error else (Theme.SUCCESS if success else Theme.TEXT_MUTED)
        self._status.setStyleSheet(f"color: {color}; font-family: '{Theme.FONT_FAMILY}'; font-size: 13px; background: transparent;")
        self._status.setText(msg)

    def _go_back(self):
        if self._on_back:
            self._on_back()

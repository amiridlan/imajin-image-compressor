import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QStackedWidget, QSizePolicy, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QFontDatabase
from ui.components.feature_card import FeatureCard
from ui.styles.theme import Theme
import qtawesome as qta


class HubWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Imajin — Multi-Purpose Toolkit")
        self.setMinimumSize(QSize(1100, 720))
        self.resize(1200, 800)
        self._set_window_icon()

        self._load_fonts()
        self._apply_global_style()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.hub_page = self._build_hub_page()
        self.stack.addWidget(self.hub_page)

        # Feature windows are imported lazily to avoid circular imports
        # and to prevent heavy modules (easyocr, opencv) loading at startup.
        self._image_window    = None
        self._pdf_window      = None
        self._qr_window       = None
        self._password_window = None
        self._organize_window = None
        self._sign_window     = None

    # ------------------------------------------------------------------
    # Fonts & global style (shared with feature windows)
    # ------------------------------------------------------------------

    def _set_window_icon(self):
        try:
            icon = qta.icon('fa5s.tools', color=Theme.ACCENT)
            self.setWindowIcon(icon)
        except Exception:
            pass

    def _load_fonts(self):
        fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 '..', 'assets', 'fonts')
        for fname in ('Outfit-Variable.ttf',
                      'DMSans-Variable.ttf'):
            path = os.path.normpath(os.path.join(fonts_dir, fname))
            if os.path.exists(path):
                QFontDatabase.addApplicationFont(path)

    def _apply_global_style(self):
        _base_font = QFont(Theme.FONT_FAMILY, Theme.FONT_SIZE_NORMAL)
        _base_font.setWeight(QFont.Weight.DemiBold)
        self.setFont(_base_font)
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {Theme.BG_PRIMARY};
                color: {Theme.TEXT};
                font-family: '{Theme.FONT_FAMILY}';
                font-weight: 600;
            }}
            QLabel {{
                color: {Theme.TEXT};
                font-family: '{Theme.FONT_FAMILY}';
                font-weight: 600;
                background-color: transparent;
            }}
            QCheckBox {{
                color: {Theme.TEXT};
                font-family: '{Theme.FONT_FAMILY}';
                font-weight: 600;
                spacing: 8px;
                background-color: transparent;
            }}
            QCheckBox::indicator {{
                width: 18px; height: 18px;
                border: 2px solid {Theme.TEXT};
                border-radius: 3px;
                background-color: {Theme.INPUT_BG};
            }}
            QCheckBox::indicator:checked {{
                background-color: {Theme.ACCENT};
                border: 2px solid {Theme.TEXT};
            }}
            QPushButton {{
                background-color: {Theme.BG_SECONDARY};
                color: {Theme.TEXT};
                border: 2px solid {Theme.TEXT};
                border-radius: {Theme.RADIUS_MD}px;
                padding: {Theme.BUTTON_PADDING_V}px {Theme.BUTTON_PADDING_H}px;
                font-family: '{Theme.FONT_FAMILY}';
                font-weight: bold;
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
                border: 2px solid {Theme.DISABLED_BORDER};
            }}
            QLineEdit {{
                background-color: {Theme.INPUT_BG};
                color: {Theme.TEXT};
                border: 2px solid {Theme.BG_SECONDARY};
                border-radius: {Theme.RADIUS_SM}px;
                padding: 5px;
                font-family: '{Theme.FONT_FAMILY}';
                font-weight: 600;
            }}
            QLineEdit:focus {{
                border: 2px solid {Theme.ACCENT};
            }}
            QListWidget {{
                background-color: {Theme.INPUT_BG};
                color: {Theme.TEXT};
                border: 2px solid {Theme.BG_SECONDARY};
                border-radius: {Theme.RADIUS_MD}px;
                font-family: '{Theme.FONT_FAMILY}';
                font-weight: 600;
            }}
            QListWidget::item {{
                padding: 4px 8px;
                border-left: 3px solid transparent;
            }}
            QListWidget::item:selected {{
                background-color: {Theme.BG_SECONDARY};
                color: {Theme.TEXT};
                border-left: 3px solid {Theme.ACCENT};
            }}
            QListWidget::item:hover {{
                background-color: {Theme.BG_SECONDARY};
                border-left: 3px solid {Theme.ACCENT};
            }}
            QComboBox {{
                background-color: {Theme.INPUT_BG};
                color: {Theme.TEXT};
                border: 2px solid {Theme.BG_SECONDARY};
                border-radius: {Theme.RADIUS_SM}px;
                padding: 5px;
                font-family: '{Theme.FONT_FAMILY}';
            }}
            QComboBox:hover {{ border: 2px solid {Theme.ACCENT}; }}
            QComboBox::drop-down {{ border: none; width: 30px; }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {Theme.TEXT};
                margin-right: 5px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {Theme.BG_SECONDARY};
                color: {Theme.TEXT};
                selection-background-color: {Theme.ACCENT};
                border: 2px solid {Theme.ACCENT};
                font-family: '{Theme.FONT_FAMILY}';
            }}
            QSlider::groove:horizontal {{
                background: {Theme.BG_SECONDARY};
                height: 8px;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {Theme.ACCENT};
                border: 2px solid {Theme.TEXT};
                width: 18px; height: 18px;
                margin: -7px 0;
                border-radius: 9px;
            }}
            QSlider::handle:horizontal:hover {{ background: {Theme.TEXT}; }}
            QProgressBar {{
                background-color: {Theme.BG_SECONDARY};
                border: 2px solid {Theme.TEXT};
                border-radius: {Theme.RADIUS_MD}px;
                text-align: center;
                color: {Theme.TEXT};
                font-family: '{Theme.FONT_FAMILY}';
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {Theme.ACCENT};
                border-radius: 3px;
            }}
            QMessageBox {{
                background-color: {Theme.BG_PRIMARY};
                color: {Theme.TEXT};
                font-family: '{Theme.FONT_FAMILY}';
            }}
            QMessageBox QPushButton {{ min-width: 80px; }}
            #rightPanel {{
                background-color: {Theme.BG_SECONDARY};
                border-left: 2px solid {Theme.TEXT};
            }}
            #rightPanel QWidget {{ background-color: {Theme.BG_SECONDARY}; }}
            #rightPanel QLabel {{ background-color: transparent; }}
            #rightPanel QCheckBox {{ background-color: transparent; }}
            #rightPanel QLineEdit {{ background-color: {Theme.INPUT_BG}; }}
            #rightPanel QComboBox {{ background-color: {Theme.INPUT_BG}; }}
            #rightPanel QTextEdit {{ background-color: {Theme.INPUT_BG}; }}
        """)

    # ------------------------------------------------------------------
    # Hub page
    # ------------------------------------------------------------------

    def _build_hub_page(self):
        page = QWidget()
        root = QVBoxLayout(page)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        root.addWidget(self._build_header())
        root.addWidget(self._build_cards_area(), 1)

        return page

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
        layout.setContentsMargins(16, 0, 16, 0)

        title = QLabel("IMAJIN")
        title.setStyleSheet(f"""
            QLabel {{
                color: {Theme.ACCENT};
                font-size: {Theme.FONT_SIZE_TITLE}px;
                font-weight: bold;
                font-family: '{Theme.FONT_DISPLAY}';
                background-color: transparent;
            }}
        """)

        version = QLabel("v2.0")
        version.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_MUTED};
                font-size: 13px;
                font-family: '{Theme.FONT_DISPLAY}';
                background-color: transparent;
            }}
        """)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(version)
        return header

    def _build_cards_area(self):
        from PyQt6.QtWidgets import QFrame, QScrollArea
        area = QWidget()
        area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        scroll.setWidget(inner)

        outer = QVBoxLayout(inner)
        outer.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        outer.setSpacing(0)
        outer.setContentsMargins(40, 48, 40, 40)

        # Hero
        hero = QLabel("Imajin Toolkit")
        hero.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT};
                font-family: '{Theme.FONT_DISPLAY}';
                font-size: 40px;
                font-weight: bold;
                background: transparent;
                letter-spacing: 2px;
            }}
        """)
        outer.addWidget(hero)

        tagline = QLabel("Image & media tools  ·  PDF signing, organizing, and conversion  ·  QR threat detection")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_MUTED};
                font-family: '{Theme.FONT_FAMILY}';
                font-size: 14px;
                background: transparent;
                padding-top: 6px;
                padding-bottom: 28px;
            }}
        """)
        outer.addWidget(tagline)

        divider = QFrame()
        divider.setFixedHeight(3)
        divider.setFixedWidth(420)
        divider.setStyleSheet(f"background-color: {Theme.ACCENT}; border: none; border-radius: 2px;")
        outer.addWidget(divider, 0, Qt.AlignmentFlag.AlignCenter)
        outer.addSpacing(36)

        # ── Media group ──────────────────────────────────────────────────
        outer.addWidget(self._section_label("MEDIA"))
        outer.addSpacing(14)

        media_row = QHBoxLayout()
        media_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        media_row.setSpacing(40)

        image_card = FeatureCard('fa5s.images', 'Image Converter',
                                 'Compress & convert\nJPG / PNG → WebP / AVIF')
        image_card.clicked.connect(self._open_image_converter)

        qr_card = FeatureCard('fa5s.qrcode', 'QR Scanner',
                              'Scan & check URLs for threats\nCamera or file upload')
        qr_card.clicked.connect(self._open_qr_scanner)

        media_row.addWidget(image_card)
        media_row.addWidget(qr_card)
        outer.addLayout(media_row)
        outer.addSpacing(36)

        # ── Documents group ──────────────────────────────────────────────
        outer.addWidget(self._section_label("DOCUMENTS"))
        outer.addSpacing(14)

        docs_row = QHBoxLayout()
        docs_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        docs_row.setSpacing(28)

        _DS = (220, 270)   # Documents card size

        pdf_card = FeatureCard('fa5s.file-word', 'PDF ↔ Word',
                               'Convert with OCR\nPDF → Word · Word → PDF',
                               size=_DS)
        pdf_card.clicked.connect(self._open_pdf_converter)

        sign_card = FeatureCard('fa5s.signature', 'Sign PDF',
                                'Add a handwritten or\nimage signature to any page',
                                size=_DS)
        sign_card.clicked.connect(self._open_sign_pdf)

        organize_card = FeatureCard('fa5s.th-large', 'Organize PDF',
                                    'Reorder, rotate & delete\npages visually',
                                    size=_DS)
        organize_card.clicked.connect(self._open_organize_pdf)

        password_card = FeatureCard('fa5s.lock', 'Password PDF',
                                    'Add or remove\npassword protection',
                                    size=_DS)
        password_card.clicked.connect(self._open_password_pdf)

        docs_row.addWidget(pdf_card)
        docs_row.addWidget(sign_card)
        docs_row.addWidget(organize_card)
        docs_row.addWidget(password_card)
        outer.addLayout(docs_row)
        outer.addSpacing(28)

        hint = QLabel("Click any card to open the tool")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_MUTED};
                font-family: '{Theme.FONT_FAMILY}';
                font-size: 13px;
                background: transparent;
            }}
        """)
        outer.addWidget(hint)

        # Wrap scroll area
        wrap_layout = QVBoxLayout(area)
        wrap_layout.setContentsMargins(0, 0, 0, 0)
        wrap_layout.addWidget(scroll)
        return area

    def _section_label(self, text):
        from PyQt6.QtWidgets import QFrame
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)

        line_l = QFrame()
        line_l.setFixedHeight(1)
        line_l.setStyleSheet(f"background: rgba(240,230,255,40); border: none;")
        line_l.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        lbl = QLabel(text)
        lbl.setStyleSheet(f"""
            QLabel {{
                color: {Theme.ACCENT};
                font-family: '{Theme.FONT_DISPLAY}';
                font-size: 12px;
                font-weight: bold;
                letter-spacing: 3px;
                background: transparent;
            }}
        """)

        line_r = QFrame()
        line_r.setFixedHeight(1)
        line_r.setStyleSheet(f"background: rgba(240,230,255,40); border: none;")
        line_r.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        row.addWidget(line_l)
        row.addWidget(lbl)
        row.addWidget(line_r)
        return container

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _switch_to(self, widget):
        self.stack.setCurrentWidget(widget)
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(Theme.ANIMATION_NORMAL)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.finished.connect(lambda: widget.setGraphicsEffect(None))
        anim.start()
        # Keep reference so it isn't GC'd mid-animation
        widget._fade_anim = anim

    def _show_hub(self):
        self._switch_to(self.hub_page)

    def _open_image_converter(self):
        if self._image_window is None:
            from ui.image_converter_window import ImageConverterWindow
            self._image_window = ImageConverterWindow(on_back=self._show_hub)
            self.stack.addWidget(self._image_window)
        self._switch_to(self._image_window)

    def _open_pdf_converter(self):
        if self._pdf_window is None:
            from ui.pdf_converter_window import PdfConverterWindow
            self._pdf_window = PdfConverterWindow(on_back=self._show_hub)
            self.stack.addWidget(self._pdf_window)
        self._switch_to(self._pdf_window)

    def _open_qr_scanner(self):
        if self._qr_window is None:
            from ui.qr_scanner_window import QrScannerWindow
            self._qr_window = QrScannerWindow(on_back=self._show_hub)
            self.stack.addWidget(self._qr_window)
        self._switch_to(self._qr_window)

    def _open_password_pdf(self):
        if self._password_window is None:
            from ui.password_pdf_window import PasswordPdfWindow
            self._password_window = PasswordPdfWindow(on_back=self._show_hub)
            self.stack.addWidget(self._password_window)
        self._switch_to(self._password_window)

    def _open_organize_pdf(self):
        if self._organize_window is None:
            from ui.organize_pdf_window import OrganizePdfWindow
            self._organize_window = OrganizePdfWindow(on_back=self._show_hub)
            self.stack.addWidget(self._organize_window)
        self._switch_to(self._organize_window)

    def _open_sign_pdf(self):
        if self._sign_window is None:
            from ui.sign_pdf_window import SignPdfWindow
            self._sign_window = SignPdfWindow(on_back=self._show_hub)
            self.stack.addWidget(self._sign_window)
        self._switch_to(self._sign_window)

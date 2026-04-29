import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFileDialog, QLineEdit, QCheckBox, QProgressBar,
                              QMessageBox, QFrame, QSizePolicy, QListWidget,
                              QListWidgetItem, QButtonGroup, QPushButton)
from PyQt6.QtCore import Qt
from ui.components.animated_button import AnimatedButton, PrimaryButton, DangerButton
from ui.components.processing_log import ProcessingLog
from ui.styles.theme import Theme
from utils.file_utils import format_file_size, filter_files_by_ext, ensure_dir


class PdfConverterWindow(QWidget):
    def __init__(self, on_back=None, parent=None):
        super().__init__(parent)
        self.on_back = on_back
        self.direction = 'pdf_to_word'   # 'pdf_to_word' | 'word_to_pdf'
        self.worker = None
        self.default_output = './output'
        self.config_file = 'config.json'

        self._init_ui()
        self._load_output_setting()
        self.setAcceptDrops(True)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self._build_header())
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setSpacing(0)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.addWidget(self._build_left_panel(), 55)
        body_layout.addWidget(self._build_right_panel(), 45)
        root.addWidget(body, 1)

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

    def _build_header(self):
        header = QWidget()
        header.setObjectName("headerBar")
        header.setFixedHeight(48)
        header.setStyleSheet(f"QWidget#headerBar {{ background-color: {Theme.TEXT}; border: none; }}")
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
            back_btn.clicked.connect(self.on_back)
            layout.addWidget(back_btn)
            layout.addSpacing(12)

        title = QLabel("PDF ↔ WORD CONVERTER")
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
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
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

    def _build_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 8, 16)

        layout.addWidget(self._build_direction_toggle())
        layout.addSpacing(4)
        layout.addWidget(self._build_drop_zone())
        layout.addWidget(self._build_list_toolbar())

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        layout.addWidget(self.file_list, 1)

        return panel

    def _build_direction_toggle(self):
        container = QWidget()
        container.setStyleSheet("QWidget { background-color: transparent; }")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        btn_style_active = f"""
            QPushButton {{
                background-color: {Theme.ACCENT};
                color: {Theme.TEXT};
                border: 2px solid {Theme.TEXT};
                border-radius: 0px;
                padding: 8px 20px;
                font-family: '{Theme.FONT_FAMILY}';
                font-weight: bold;
                font-size: 15px;
            }}
        """
        btn_style_inactive = f"""
            QPushButton {{
                background-color: {Theme.BG_SECONDARY};
                color: {Theme.TEXT};
                border: 2px solid {Theme.TEXT};
                border-radius: 0px;
                padding: 8px 20px;
                font-family: '{Theme.FONT_FAMILY}';
                font-weight: bold;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background-color: {Theme.BG_PRIMARY};
            }}
        """

        self.btn_pdf_to_word = QPushButton("PDF → Word")
        self.btn_pdf_to_word.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pdf_to_word.setStyleSheet(btn_style_active)
        self.btn_pdf_to_word.setCheckable(True)
        self.btn_pdf_to_word.setChecked(True)

        self.btn_word_to_pdf = QPushButton("Word → PDF")
        self.btn_word_to_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_word_to_pdf.setStyleSheet(btn_style_inactive)
        self.btn_word_to_pdf.setCheckable(True)

        self._btn_active_style = btn_style_active
        self._btn_inactive_style = btn_style_inactive

        self.btn_pdf_to_word.clicked.connect(lambda: self._set_direction('pdf_to_word'))
        self.btn_word_to_pdf.clicked.connect(lambda: self._set_direction('word_to_pdf'))

        # Round left edge of first, right edge of last
        self.btn_pdf_to_word.setStyleSheet(btn_style_active.replace(
            "border-radius: 0px", f"border-top-left-radius: {Theme.RADIUS_MD}px; border-bottom-left-radius: {Theme.RADIUS_MD}px; border-radius: 0px"
        ))
        self.btn_word_to_pdf.setStyleSheet(btn_style_inactive.replace(
            "border-radius: 0px", f"border-top-right-radius: {Theme.RADIUS_MD}px; border-bottom-right-radius: {Theme.RADIUS_MD}px; border-radius: 0px"
        ))

        layout.addWidget(self.btn_pdf_to_word)
        layout.addWidget(self.btn_word_to_pdf)
        layout.addStretch()
        return container

    def _set_direction(self, direction):
        self.direction = direction
        self.file_list.clear()
        self._update_status()

        if direction == 'word_to_pdf':
            from core.pdf.word_to_pdf import is_word_available
            if not is_word_available():
                QMessageBox.warning(
                    self, "Microsoft Word Not Found",
                    "Word → PDF conversion requires Microsoft Word to be installed on this machine.\n\n"
                    "You can still use PDF → Word conversion without Word."
                )

        active = f"""
            QPushButton {{
                background-color: {Theme.ACCENT};
                color: {Theme.TEXT};
                border: 2px solid {Theme.TEXT};
                padding: 8px 20px;
                font-family: '{Theme.FONT_FAMILY}';
                font-weight: bold;
                font-size: 15px;
            }}
        """
        inactive = f"""
            QPushButton {{
                background-color: {Theme.BG_SECONDARY};
                color: {Theme.TEXT};
                border: 2px solid {Theme.TEXT};
                padding: 8px 20px;
                font-family: '{Theme.FONT_FAMILY}';
                font-weight: bold;
                font-size: 15px;
            }}
            QPushButton:hover {{ background-color: {Theme.BG_PRIMARY}; }}
        """

        if direction == 'pdf_to_word':
            self.btn_pdf_to_word.setStyleSheet(active + f"QPushButton {{ border-top-left-radius: {Theme.RADIUS_MD}px; border-bottom-left-radius: {Theme.RADIUS_MD}px; }}")
            self.btn_word_to_pdf.setStyleSheet(inactive + f"QPushButton {{ border-top-right-radius: {Theme.RADIUS_MD}px; border-bottom-right-radius: {Theme.RADIUS_MD}px; }}")
            self.drop_label.setText("⬇  DROP PDF FILES HERE")
            self.ocr_checkbox.setVisible(True)
        else:
            self.btn_word_to_pdf.setStyleSheet(active + f"QPushButton {{ border-top-right-radius: {Theme.RADIUS_MD}px; border-bottom-right-radius: {Theme.RADIUS_MD}px; }}")
            self.btn_pdf_to_word.setStyleSheet(inactive + f"QPushButton {{ border-top-left-radius: {Theme.RADIUS_MD}px; border-bottom-left-radius: {Theme.RADIUS_MD}px; }}")
            self.drop_label.setText("⬇  DROP WORD FILES HERE")
            self.ocr_checkbox.setVisible(False)

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
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        self.drop_label = QLabel("⬇  DROP PDF FILES HERE")
        self.drop_label.setStyleSheet(f"""
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
        or_label.setStyleSheet(f"QLabel {{ color: {Theme.TEXT}; font-size: 15px; font-family: '{Theme.FONT_FAMILY}'; background-color: transparent; border: none; }}")

        self.add_button = AnimatedButton("+ ADD FILES", icon_name="fa5s.folder-plus")
        self.add_button.clicked.connect(self._add_files)

        layout.addStretch()
        layout.addWidget(self.drop_label)
        layout.addWidget(or_label)
        layout.addWidget(self.add_button)
        layout.addStretch()
        return frame

    def _build_list_toolbar(self):
        toolbar = QWidget()
        toolbar.setStyleSheet("QWidget { background-color: transparent; }")
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(8)

        self.file_count_label = QLabel("FILES (0)")
        self.file_count_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT};
                font-size: 15px;
                font-weight: bold;
                font-family: '{Theme.FONT_FAMILY}';
                background-color: transparent;
                border: none;
            }}
        """)

        remove_btn = AnimatedButton("remove", icon_name="fa5s.trash-alt")
        remove_btn.clicked.connect(self._remove_selected)

        clear_btn = AnimatedButton("clear all", icon_name="fa5s.broom")
        clear_btn.clicked.connect(self._clear_all)

        layout.addWidget(self.file_count_label)
        layout.addStretch()
        layout.addWidget(remove_btn)
        layout.addWidget(clear_btn)
        return toolbar

    def _build_right_panel(self):
        panel = QWidget()
        panel.setObjectName("rightPanel")
        layout = QVBoxLayout(panel)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 16, 16, 16)

        layout.addWidget(self._section_label("// OUTPUT //"))

        output_row = QHBoxLayout()
        self.output_input = QLineEdit()
        self.output_input.setText(self.default_output)
        self.output_input.setPlaceholderText("Select output folder...")

        browse_btn = AnimatedButton("browse", icon_name="fa5s.folder-open")
        browse_btn.clicked.connect(self._browse_output)

        output_row.addWidget(self.output_input, 1)
        output_row.addWidget(browse_btn)
        layout.addLayout(output_row)

        layout.addSpacing(8)
        layout.addWidget(self._section_label("// OPTIONS //"))

        self.ocr_checkbox = QCheckBox("Use OCR (for scanned PDFs)")
        self.ocr_checkbox.setChecked(False)
        self.ocr_checkbox.setToolTip(
            "Enable OCR via EasyOCR for PDFs that contain scanned images instead of text.\n"
            "First use downloads a ~100 MB language model."
        )
        layout.addWidget(self.ocr_checkbox)

        layout.addSpacing(8)
        divider = QFrame()
        divider.setFixedHeight(2)
        divider.setStyleSheet(f"background-color: {Theme.TEXT}; border: none;")
        layout.addWidget(divider)
        layout.addSpacing(8)
        layout.addStretch()

        layout.addWidget(self._section_label("// PROCESSING //"))

        self.convert_button = PrimaryButton("CONVERT ALL", icon_name="fa5s.sync-alt")
        self.convert_button.setMinimumHeight(48)
        self.convert_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.convert_button.clicked.connect(self._start_conversion)
        layout.addWidget(self.convert_button)

        self.cancel_button = DangerButton("CANCEL", icon_name="fa5s.stop-circle")
        self.cancel_button.clicked.connect(self._cancel)
        self.cancel_button.setVisible(False)
        layout.addWidget(self.cancel_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.log = ProcessingLog()
        self.log.setVisible(False)
        layout.addWidget(self.log)

        return panel

    # ------------------------------------------------------------------
    # Drag & drop
    # ------------------------------------------------------------------

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        paths = [u.toLocalFile() for u in event.mimeData().urls()]
        self._add_files_to_list(paths)

    # ------------------------------------------------------------------
    # File management
    # ------------------------------------------------------------------

    def _accepted_extensions(self):
        return ('.pdf',) if self.direction == 'pdf_to_word' else ('.docx', '.doc')

    def _add_files(self):
        if self.direction == 'pdf_to_word':
            name_filter = "PDF Files (*.pdf)"
        else:
            name_filter = "Word Documents (*.docx *.doc)"

        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setNameFilter(name_filter)
        if dialog.exec():
            self._add_files_to_list(dialog.selectedFiles())

    def _add_files_to_list(self, paths):
        valid = filter_files_by_ext(paths, self._accepted_extensions())
        skipped = len(paths) - len(valid)
        if skipped:
            self.status_label.setText(f"SKIPPED {skipped} UNSUPPORTED_")

        existing = {
            self.file_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.file_list.count())
        }
        for path in valid:
            if path in existing:
                continue
            name = os.path.basename(path)
            size = format_file_size(os.path.getsize(path))
            item = QListWidgetItem(f"{name}  ({size})")
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.file_list.addItem(item)

        self._update_status()

    def _remove_selected(self):
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))
        self._update_status()

    def _clear_all(self):
        self.file_list.clear()
        self._update_status()

    def _update_status(self):
        count = self.file_list.count()
        self.file_count_label.setText(f"FILES ({count})")
        self.status_label.setText("READY_" if count == 0 else f"{count} FILE{'S' if count > 1 else ''} LOADED_")

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def _browse_output(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        current = self.output_input.text()
        if current and os.path.exists(current):
            dialog.setDirectory(current)
        if dialog.exec():
            self.output_input.setText(dialog.selectedFiles()[0])
            self._save_output_setting()

    def _load_output_setting(self):
        import json
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file) as f:
                    cfg = json.load(f)
                self.output_input.setText(cfg.get('output_folder', self.default_output))
            except Exception:
                pass

    def _save_output_setting(self):
        import json
        try:
            cfg = {}
            if os.path.exists(self.config_file):
                with open(self.config_file) as f:
                    cfg = json.load(f)
            cfg['output_folder'] = self.output_input.text()
            with open(self.config_file, 'w') as f:
                json.dump(cfg, f, indent=4)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Conversion
    # ------------------------------------------------------------------

    def _start_conversion(self):
        output_dir = self.output_input.text().strip()
        if not output_dir:
            QMessageBox.warning(self, "No Output Folder", "Please select an output folder.")
            return

        files = [
            self.file_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.file_list.count())
        ]
        if not files:
            QMessageBox.warning(self, "No Files", "Please add at least one file to convert.")
            return

        try:
            ensure_dir(output_dir)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not create output folder:\n{e}")
            return

        from core.pdf.pdf_worker import PdfWorker
        self.worker = PdfWorker(
            files=files,
            output_dir=output_dir,
            direction=self.direction,
            use_ocr=self.ocr_checkbox.isChecked(),
        )
        self.worker.file_started.connect(self._on_file_started)
        self.worker.file_completed.connect(self._on_file_completed)
        self.worker.progress_updated.connect(self._on_progress)
        self.worker.all_completed.connect(self._on_all_completed)
        self.worker.status_update.connect(self.status_label.setText)

        self.convert_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.cancel_button.setVisible(True)
        self.cancel_button.setEnabled(True)
        self.log.clear_log()
        self.log.setVisible(True)

        self.worker.start()

    def _cancel(self):
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, "Cancel", "Cancel conversion?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.worker.cancel()
                self.status_label.setText("CANCELLING...")
                self.cancel_button.setEnabled(False)

    def _on_file_started(self, filename):
        short = filename[:20] + "..." if len(filename) > 20 else filename
        self.status_label.setText(f"CONVERTING: {short}_")

    def _on_file_completed(self, success, filename, message):
        self.log.add_entry(success, filename, message)

    def _on_progress(self, value):
        self.progress_bar.setValue(value)

    def _on_all_completed(self, successful, failed, errors):
        self.convert_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.cancel_button.setVisible(False)

        msg = f"Conversion complete!\n\nSuccessful: {successful}\nFailed: {failed}"
        if errors:
            msg += "\n\nErrors:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                msg += f"\n... and {len(errors) - 5} more"

        if failed:
            # Surface a specific tip if Word is missing
            word_missing = any("Microsoft Word" in e or "Word.Application" in e for e in errors)
            if word_missing:
                QMessageBox.critical(
                    self, "Microsoft Word Required",
                    "Word → PDF conversion requires Microsoft Word to be installed.\n\n"
                    "Please install Microsoft Word and try again.\n\n"
                    "Alternatively, use a free tool like LibreOffice to export your .docx as PDF "
                    "before using the PDF → Word feature in reverse."
                )
            else:
                QMessageBox.warning(self, "Conversion Complete", msg)
        else:
            QMessageBox.information(self, "Conversion Complete", msg)

        self.status_label.setText(f"{successful} CONVERTED_")
        self.worker = None

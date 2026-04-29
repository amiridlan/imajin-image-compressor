import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QListWidget, QListWidgetItem, QLabel,
                              QFileDialog, QLineEdit, QCheckBox,
                              QProgressBar, QMessageBox, QComboBox,
                              QFrame, QSizePolicy)
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QFont
from core.compressor import validate_quality
from core.converter import get_supported_formats
from core.worker import ImageProcessorWorker
from core.conflict_checker import check_conflicts
from ui.components.animated_button import AnimatedButton, PrimaryButton, DangerButton
from ui.components.quality_presets import QualityPresetsWidget
from ui.components.processing_log import ProcessingLog
from ui.dialogs.conflict_dialog import ConflictDialog
from ui.styles.theme import Theme


class ImageConverterWindow(QWidget):
    def __init__(self, on_back=None, parent=None):
        super().__init__(parent)
        self.on_back = on_back

        self.supported_formats = ('.jpg', '.jpeg', '.png')
        self.default_output_folder = './output'
        self.config_file = 'config.json'
        self.worker = None

        self._init_ui()
        self._load_settings()
        self.setAcceptDrops(True)

    # ------------------------------------------------------------------
    # UI construction
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
        label = QLabel(text)
        label.setStyleSheet(f"""
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
        label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        return label

    def _build_header(self):
        header = QWidget()
        header.setObjectName("headerBar")
        header.setFixedHeight(48)
        header.setStyleSheet(f"""
            QWidget#headerBar {{
                background-color: {Theme.TEXT};
                border: none;
            }}
        """)
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

        title = QLabel("IMAGE CONVERTER")
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

        layout.addWidget(self._build_drop_zone())
        layout.addWidget(self._build_list_toolbar())

        self.image_list = QListWidget()
        self.image_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        layout.addWidget(self.image_list, 1)

        return panel

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

        drop_label = QLabel("⬇  DROP IMAGES HERE")
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
        or_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT};
                font-size: 15px;
                font-family: '{Theme.FONT_FAMILY}';
                background-color: transparent;
                border: none;
            }}
        """)

        self.add_button = AnimatedButton("+ ADD FILES", icon_name="fa5s.folder-plus")
        self.add_button.clicked.connect(self._add_images)

        layout.addStretch()
        layout.addWidget(drop_label)
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

        self.remove_button = AnimatedButton("remove", icon_name="fa5s.trash-alt")
        self.remove_button.clicked.connect(self._remove_selected)

        self.clear_button = AnimatedButton("clear all", icon_name="fa5s.broom")
        self.clear_button.clicked.connect(self._clear_all)

        layout.addWidget(self.file_count_label)
        layout.addStretch()
        layout.addWidget(self.remove_button)
        layout.addWidget(self.clear_button)
        return toolbar

    def _build_right_panel(self):
        panel = QWidget()
        panel.setObjectName("rightPanel")

        layout = QVBoxLayout(panel)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 16, 16, 16)

        layout.addWidget(self._section_label("// OUTPUT //"))

        output_row = QHBoxLayout()
        self.output_folder_input = QLineEdit()
        self.output_folder_input.setText(self.default_output_folder)
        self.output_folder_input.setPlaceholderText("Select output folder...")

        self.browse_button = AnimatedButton("browse", icon_name="fa5s.folder-open")
        self.browse_button.clicked.connect(self._browse_output_folder)

        output_row.addWidget(self.output_folder_input, 1)
        output_row.addWidget(self.browse_button)
        layout.addLayout(output_row)

        format_row = QHBoxLayout()
        format_label = QLabel("FORMAT:")
        self.format_selector = QComboBox()
        self.format_selector.addItems(get_supported_formats())
        self.format_selector.view().setStyleSheet(f"""
            QAbstractItemView {{
                background-color: {Theme.BG_SECONDARY};
                color: {Theme.TEXT};
                border: 2px solid {Theme.TEXT};
                selection-background-color: {Theme.BG_SECONDARY};
                selection-color: {Theme.TEXT};
                font-family: '{Theme.FONT_FAMILY}';
                padding: 2px;
                outline: none;
            }}
        """)

        format_row.addWidget(format_label)
        format_row.addWidget(self.format_selector, 1)
        layout.addLayout(format_row)

        layout.addSpacing(8)
        layout.addWidget(self._section_label("// QUALITY //"))
        self.quality_presets = QualityPresetsWidget()
        layout.addWidget(self.quality_presets)

        layout.addSpacing(8)
        layout.addWidget(self._section_label("// OPTIONS //"))
        self.remove_metadata_checkbox = QCheckBox("Strip EXIF metadata")
        self.remove_metadata_checkbox.setChecked(False)
        self.remove_metadata_checkbox.stateChanged.connect(self._save_settings)
        layout.addWidget(self.remove_metadata_checkbox)

        layout.addSpacing(8)
        divider = QFrame()
        divider.setFixedHeight(2)
        divider.setStyleSheet(f"background-color: {Theme.TEXT}; border: none;")
        layout.addWidget(divider)
        layout.addSpacing(8)
        layout.addStretch()

        layout.addWidget(self._section_label("// PROCESSING //"))

        self.process_button = PrimaryButton("START PROCESSING", icon_name="fa5s.play-circle")
        self.process_button.setMinimumHeight(48)
        self.process_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.process_button.clicked.connect(self._start_processing)
        layout.addWidget(self.process_button)

        self.cancel_button = DangerButton("CANCEL", icon_name="fa5s.stop-circle")
        self.cancel_button.clicked.connect(self._cancel_processing)
        self.cancel_button.setVisible(False)
        layout.addWidget(self.cancel_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.processing_log = ProcessingLog()
        self.processing_log.setVisible(False)
        layout.addWidget(self.processing_log)

        return panel

    # ------------------------------------------------------------------
    # Drag & drop
    # ------------------------------------------------------------------

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self._add_files_to_list(self._validate_files(files))

    # ------------------------------------------------------------------
    # File management
    # ------------------------------------------------------------------

    def _validate_files(self, files):
        valid, invalid = [], 0
        for f in files:
            if os.path.isfile(f) and f.lower().endswith(self.supported_formats):
                valid.append(f)
            else:
                invalid += 1
        if invalid:
            self.status_label.setText(f"SKIPPED {invalid} UNSUPPORTED_")
        return valid

    def _add_files_to_list(self, file_paths):
        existing = {
            self.image_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.image_list.count())
        }
        for path in file_paths:
            if path in existing:
                continue
            name = os.path.basename(path)
            size_mb = os.path.getsize(path) / (1024 * 1024)
            item = QListWidgetItem(f"{name} ({size_mb:.2f} MB)")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.image_list.addItem(item)
        self._update_status()

    def _add_images(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setNameFilter("Images (*.jpg *.jpeg *.png)")
        if dialog.exec():
            self._add_files_to_list(self._validate_files(dialog.selectedFiles()))

    def _remove_selected(self):
        for item in self.image_list.selectedItems():
            self.image_list.takeItem(self.image_list.row(item))
        self._update_status()

    def _clear_all(self):
        self.image_list.clear()
        self._update_status()

    def _update_status(self):
        count = self.image_list.count()
        self.file_count_label.setText(f"FILES ({count})")
        if count == 0:
            self.status_label.setText("READY_")
        else:
            self.status_label.setText(f"{count} FILE{'S' if count > 1 else ''} LOADED_")

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def _browse_output_folder(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        current = self.output_folder_input.text()
        if current and os.path.exists(current):
            dialog.setDirectory(current)
        if dialog.exec():
            self.output_folder_input.setText(dialog.selectedFiles()[0])
            self._save_settings()

    def _load_settings(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    cfg = json.load(f)
                self.output_folder_input.setText(cfg.get('output_folder', self.default_output_folder))
                self.remove_metadata_checkbox.setChecked(cfg.get('remove_metadata', False))
            except Exception:
                pass

    def _save_settings(self):
        try:
            cfg = {
                'output_folder': self.output_folder_input.text(),
                'remove_metadata': self.remove_metadata_checkbox.isChecked(),
            }
            with open(self.config_file, 'w') as f:
                json.dump(cfg, f, indent=4)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Processing
    # ------------------------------------------------------------------

    def _start_processing(self):
        output_folder = self.output_folder_input.text()
        if not output_folder:
            QMessageBox.warning(self, "No Output Folder", "Please select an output folder.")
            return

        if not os.path.exists(output_folder):
            try:
                os.makedirs(output_folder)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create output folder: {e}")
                return

        images = [
            self.image_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.image_list.count())
            if self.image_list.item(i).checkState() == Qt.CheckState.Checked
        ]

        if not images:
            QMessageBox.warning(self, "No Images Selected", "Please check at least one image.")
            return

        quality = validate_quality(self.quality_presets.get_value())
        remove_metadata = self.remove_metadata_checkbox.isChecked()
        selected_format = self.format_selector.currentText()

        self.process_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.cancel_button.setVisible(True)
        self.cancel_button.setEnabled(True)
        self.processing_log.clear_log()
        self.processing_log.setVisible(True)

        self.worker = ImageProcessorWorker(
            images, output_folder, quality, remove_metadata, selected_format
        )
        self.worker.progress_updated.connect(self._on_progress)
        self.worker.file_started.connect(self._on_file_started)
        self.worker.file_completed.connect(self._on_file_completed)
        self.worker.all_completed.connect(self._on_all_completed)
        self.worker.start()

    def _cancel_processing(self):
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, "Cancel", "Cancel processing?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.worker.cancel()
                self.status_label.setText("CANCELLING...")
                self.cancel_button.setEnabled(False)

    def _on_progress(self, value):
        self.progress_bar.setValue(value)

    def _on_file_started(self, filename):
        short = filename[:18] + "..." if len(filename) > 18 else filename
        self.status_label.setText(f"PROCESSING: {short}_")

    def _on_file_completed(self, success, filename, message, stats=None):
        self.processing_log.add_entry(success, filename, message, stats)

    def _on_all_completed(self, successful, failed, errors):
        self.process_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.cancel_button.setVisible(False)

        msg = f"Processing complete!\n\nSuccessfully processed: {successful}\nFailed: {failed}"
        if errors:
            msg += "\n\nErrors:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                msg += f"\n... and {len(errors) - 5} more"

        if failed:
            QMessageBox.warning(self, "Processing Complete", msg)
        else:
            QMessageBox.information(self, "Processing Complete", msg)

        self.status_label.setText(f"{successful} PROCESSED_")
        self.worker = None

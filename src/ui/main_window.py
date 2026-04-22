import os
import json
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QListWidget, QListWidgetItem, QLabel,
                              QFileDialog, QLineEdit, QCheckBox,
                              QProgressBar, QMessageBox, QComboBox,
                              QFrame, QSizePolicy)
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QFont, QFontDatabase
from core.compressor import validate_quality
from core.converter import get_supported_formats
from core.worker import ImageProcessorWorker
from core.conflict_checker import check_conflicts
from ui.components.animated_button import AnimatedButton, PrimaryButton, DangerButton
from ui.components.quality_presets import QualityPresetsWidget
from ui.components.processing_log import ProcessingLog
from ui.dialogs.conflict_dialog import ConflictDialog
from ui.styles.theme import Theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Imajin")
        self.setMinimumSize(QSize(920, 640))

        self.supported_formats = ('.jpg', '.jpeg', '.png')
        self.default_output_folder = './output'
        self.config_file = 'config.json'
        self.worker = None

        self._load_fonts()
        self.apply_global_style()
        self.init_ui()
        self.load_settings()
        self.setAcceptDrops(True)

    def _load_fonts(self):
        fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 '..', 'assets', 'fonts')
        for fname in ('SpaceGrotesk-Regular.ttf',
                      'SpaceGrotesk-Medium.ttf',
                      'SpaceGrotesk-Bold.ttf'):
            path = os.path.normpath(os.path.join(fonts_dir, fname))
            if os.path.exists(path):
                QFontDatabase.addApplicationFont(path)

    def apply_global_style(self):
        font = QFont("Space Grotesk", 10)
        self.setFont(font)

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {Theme.BG_PRIMARY};
                color: {Theme.TEXT};
                font-family: 'Space Grotesk';
            }}

            QWidget {{
                background-color: {Theme.BG_PRIMARY};
                color: {Theme.TEXT};
                font-family: 'Space Grotesk';
            }}

            QLabel {{
                color: {Theme.TEXT};
                font-family: 'Space Grotesk';
                background-color: transparent;
            }}

            QCheckBox {{
                color: {Theme.TEXT};
                font-family: 'Space Grotesk';
                spacing: 8px;
                background-color: transparent;
            }}

            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {Theme.TEXT};
                border-radius: 3px;
                background-color: white;
            }}

            QCheckBox::indicator:checked {{
                background-color: {Theme.ACCENT};
                border: 2px solid {Theme.TEXT};
            }}

            QPushButton {{
                background-color: {Theme.BG_SECONDARY};
                color: {Theme.TEXT};
                border: 2px solid {Theme.TEXT};
                border-radius: 5px;
                padding: 8px 16px;
                font-family: 'Space Grotesk';
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
                background-color: #cccccc;
                color: #666666;
                border: 2px solid #999999;
            }}

            QLineEdit {{
                background-color: white;
                color: {Theme.TEXT};
                border: 2px solid {Theme.BG_SECONDARY};
                border-radius: 3px;
                padding: 5px;
                font-family: 'Space Grotesk';
            }}

            QLineEdit:focus {{
                border: 2px solid {Theme.ACCENT};
            }}

            QListWidget {{
                background-color: white;
                color: {Theme.TEXT};
                border: 2px solid {Theme.BG_SECONDARY};
                border-radius: 5px;
                font-family: 'Space Grotesk';
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
                background-color: {Theme.BG_PRIMARY};
                border-left: 3px solid {Theme.ACCENT};
            }}

            QComboBox {{
                background-color: white;
                color: {Theme.TEXT};
                border: 2px solid {Theme.BG_SECONDARY};
                border-radius: 3px;
                padding: 5px;
                font-family: 'Space Grotesk';
            }}

            QComboBox:hover {{
                border: 2px solid {Theme.ACCENT};
            }}

            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}

            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {Theme.TEXT};
                margin-right: 5px;
            }}

            QComboBox QAbstractItemView {{
                background-color: white;
                color: {Theme.TEXT};
                selection-background-color: {Theme.BG_SECONDARY};
                border: 2px solid {Theme.TEXT};
                font-family: 'Space Grotesk';
            }}

            QSlider::groove:horizontal {{
                background: {Theme.BG_SECONDARY};
                height: 8px;
                border-radius: 4px;
            }}

            QSlider::handle:horizontal {{
                background: {Theme.ACCENT};
                border: 2px solid {Theme.TEXT};
                width: 18px;
                height: 18px;
                margin: -7px 0;
                border-radius: 9px;
            }}

            QSlider::handle:horizontal:hover {{
                background: {Theme.TEXT};
            }}

            QProgressBar {{
                background-color: {Theme.BG_SECONDARY};
                border: 2px solid {Theme.TEXT};
                border-radius: 5px;
                text-align: center;
                color: {Theme.TEXT};
                font-family: 'Space Grotesk';
                font-weight: bold;
            }}

            QProgressBar::chunk {{
                background-color: {Theme.ACCENT};
                border-radius: 3px;
            }}

            QMessageBox {{
                background-color: {Theme.BG_PRIMARY};
                color: {Theme.TEXT};
                font-family: 'Space Grotesk';
            }}

            QMessageBox QPushButton {{
                min-width: 80px;
            }}

            /* Right panel and all its QWidget descendants */
            #rightPanel {{
                background-color: {Theme.BG_SECONDARY};
                border-left: 2px solid {Theme.TEXT};
            }}

            #rightPanel QWidget {{
                background-color: {Theme.BG_SECONDARY};
            }}

            /* Override specific widgets that need non-secondary backgrounds */
            #rightPanel QLabel {{
                background-color: transparent;
            }}

            #rightPanel QCheckBox {{
                background-color: transparent;
            }}

            #rightPanel QLineEdit {{
                background-color: white;
            }}

            #rightPanel QComboBox {{
                background-color: white;
            }}

            #rightPanel QTextEdit {{
                background-color: white;
            }}
        """)

    def _section_label(self, text):
        label = QLabel(text)
        label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT};
                font-size: 9px;
                font-weight: bold;
                font-family: 'Space Grotesk';
                background-color: {Theme.ACCENT};
                border: none;
                padding: 2px 6px;
                border-radius: 3px;
            }}
        """)
        label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        return label

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setSpacing(0)
        root_layout.setContentsMargins(0, 0, 0, 0)

        root_layout.addWidget(self._build_header())

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setSpacing(0)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.addWidget(self._build_left_panel(), 55)
        body_layout.addWidget(self._build_right_panel(), 45)
        root_layout.addWidget(body, 1)

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

        title = QLabel("IMAJIN IMAGE PROCESSOR")
        title.setStyleSheet(f"""
            QLabel {{
                color: {Theme.ACCENT};
                font-size: 16px;
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
                font-size: 9px;
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
        self.image_list.setToolTip("List of images to process. Check/uncheck items to include/exclude them.")
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
                font-size: 12px;
                font-weight: bold;
                font-family: 'Space Grotesk';
                background-color: transparent;
                border: none;
            }}
        """)

        or_label = QLabel("or")
        or_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT};
                font-size: 10px;
                font-family: 'Space Grotesk';
                background-color: transparent;
                border: none;
            }}
        """)

        self.add_button = AnimatedButton("+ ADD FILES", icon_name="fa5s.folder-plus")
        self.add_button.clicked.connect(self.add_images)
        self.add_button.setToolTip("Select images from your computer (Ctrl+O)")

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
                font-size: 10px;
                font-weight: bold;
                font-family: 'Space Grotesk';
                background-color: transparent;
                border: none;
            }}
        """)

        self.remove_button = AnimatedButton("remove", icon_name="fa5s.trash-alt")
        self.remove_button.clicked.connect(self.remove_selected)
        self.remove_button.setToolTip("Remove selected images (Delete)")

        self.clear_button = AnimatedButton("clear all", icon_name="fa5s.broom")
        self.clear_button.clicked.connect(self.clear_all)
        self.clear_button.setToolTip("Clear all images (Ctrl+Shift+C)")

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

        # // OUTPUT //
        layout.addWidget(self._section_label("// OUTPUT //"))

        output_row = QHBoxLayout()
        self.output_folder_input = QLineEdit()
        self.output_folder_input.setText(self.default_output_folder)
        self.output_folder_input.setPlaceholderText("Select output folder...")
        self.output_folder_input.setToolTip("Folder where processed images will be saved")

        self.browse_button = AnimatedButton("browse", icon_name="fa5s.folder-open")
        self.browse_button.clicked.connect(self.browse_output_folder)
        self.browse_button.setToolTip("Select output folder")

        output_row.addWidget(self.output_folder_input, 1)
        output_row.addWidget(self.browse_button)
        layout.addLayout(output_row)

        format_row = QHBoxLayout()
        format_label = QLabel("FORMAT:")
        self.format_selector = QComboBox()
        self.format_selector.addItems(get_supported_formats())
        self.format_selector.setCurrentIndex(0)
        self.format_selector.currentIndexChanged.connect(self.on_format_changed)
        self.format_selector.setToolTip("Choose output format: Keep Original, WebP, or AVIF")
        self.format_selector.view().setStyleSheet(f"""
            QAbstractItemView {{
                background-color: white;
                color: {Theme.TEXT};
                border: 2px solid {Theme.TEXT};
                selection-background-color: {Theme.BG_SECONDARY};
                selection-color: {Theme.TEXT};
                font-family: 'Space Grotesk';
                padding: 2px;
                outline: none;
            }}
        """)

        format_row.addWidget(format_label)
        format_row.addWidget(self.format_selector, 1)
        layout.addLayout(format_row)

        layout.addSpacing(8)

        # // QUALITY //
        layout.addWidget(self._section_label("// QUALITY //"))
        self.quality_presets = QualityPresetsWidget()
        layout.addWidget(self.quality_presets)

        layout.addSpacing(8)

        # // OPTIONS //
        layout.addWidget(self._section_label("// OPTIONS //"))
        self.remove_metadata_checkbox = QCheckBox("Strip EXIF metadata")
        self.remove_metadata_checkbox.setChecked(False)
        self.remove_metadata_checkbox.stateChanged.connect(self.save_settings)
        self.remove_metadata_checkbox.setToolTip("Remove EXIF metadata (camera info, GPS, etc.) from images")
        layout.addWidget(self.remove_metadata_checkbox)

        layout.addSpacing(8)
        divider = QFrame()
        divider.setFixedHeight(2)
        divider.setStyleSheet(f"background-color: {Theme.TEXT}; border: none;")
        layout.addWidget(divider)
        layout.addSpacing(8)

        layout.addStretch()

        # // PROCESSING //
        layout.addWidget(self._section_label("// PROCESSING //"))

        self.process_button = PrimaryButton("START PROCESSING", icon_name="fa5s.play-circle")
        self.process_button.setMinimumHeight(48)
        self.process_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.process_button.clicked.connect(self.start_processing)
        self.process_button.setToolTip("Process all checked images (F5)")
        layout.addWidget(self.process_button)

        self.cancel_button = DangerButton("CANCEL", icon_name="fa5s.stop-circle")
        self.cancel_button.clicked.connect(self.cancel_processing)
        self.cancel_button.setToolTip("Cancel processing (Escape)")
        self.cancel_button.setVisible(False)
        layout.addWidget(self.cancel_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setToolTip("Processing progress")
        layout.addWidget(self.progress_bar)

        self.processing_log = ProcessingLog()
        self.processing_log.setVisible(False)
        layout.addWidget(self.processing_log)

        return panel

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        valid_files = self.validate_files(files)
        self.add_files_to_list(valid_files)

    def validate_files(self, files):
        valid_files = []
        invalid_count = 0

        for file_path in files:
            if os.path.isfile(file_path):
                if file_path.lower().endswith(self.supported_formats):
                    valid_files.append(file_path)
                else:
                    invalid_count += 1

        if invalid_count > 0:
            self.status_label.setText(
                f"SKIPPED {invalid_count} UNSUPPORTED_"
            )

        return valid_files

    def add_files_to_list(self, file_paths):
        for file_path in file_paths:
            if not self.file_exists_in_list(file_path):
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                file_size_mb = file_size / (1024 * 1024)

                item = QListWidgetItem(f"{file_name} ({file_size_mb:.2f} MB)")
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Checked)
                item.setData(Qt.ItemDataRole.UserRole, file_path)

                self.image_list.addItem(item)

        self.update_status()

    def file_exists_in_list(self, file_path):
        for i in range(self.image_list.count()):
            item = self.image_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == file_path:
                return True
        return False

    def add_images(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Images (*.jpg *.jpeg *.png)")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            valid_files = self.validate_files(selected_files)
            self.add_files_to_list(valid_files)

    def remove_selected(self):
        selected_items = self.image_list.selectedItems()

        if not selected_items:
            self.status_label.setText("NO ITEMS SELECTED_")
            return

        for item in selected_items:
            self.image_list.takeItem(self.image_list.row(item))

        self.update_status()

    def clear_all(self):
        self.image_list.clear()
        self.update_status()

    def update_status(self):
        count = self.image_list.count()
        if count == 0:
            self.status_label.setText("READY_")
            self.file_count_label.setText("FILES (0)")
        elif count == 1:
            self.status_label.setText("1 FILE LOADED_")
            self.file_count_label.setText("FILES (1)")
        else:
            self.status_label.setText(f"{count} FILES LOADED_")
            self.file_count_label.setText(f"FILES ({count})")

    def browse_output_folder(self):
        folder_dialog = QFileDialog(self)
        folder_dialog.setFileMode(QFileDialog.FileMode.Directory)

        current_folder = self.output_folder_input.text()
        if current_folder and os.path.exists(current_folder):
            folder_dialog.setDirectory(current_folder)

        if folder_dialog.exec():
            selected_folder = folder_dialog.selectedFiles()[0]
            self.output_folder_input.setText(selected_folder)
            self.save_settings()

    def load_settings(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.output_folder_input.setText(
                        config.get('output_folder', self.default_output_folder)
                    )
                    self.remove_metadata_checkbox.setChecked(
                        config.get('remove_metadata', False)
                    )
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save_settings(self):
        try:
            config = {
                'output_folder': self.output_folder_input.text(),
                'remove_metadata': self.remove_metadata_checkbox.isChecked()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def on_format_changed(self):
        pass

    def start_processing(self):
        output_folder = self.output_folder_input.text()

        if not output_folder:
            QMessageBox.warning(self, "No Output Folder",
                                "Please select an output folder.")
            return

        if not os.path.exists(output_folder):
            try:
                os.makedirs(output_folder)
            except Exception as e:
                QMessageBox.critical(self, "Error",
                                     f"Could not create output folder: {str(e)}")
                return

        images_to_process = []
        for i in range(self.image_list.count()):
            item = self.image_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                file_path = item.data(Qt.ItemDataRole.UserRole)
                images_to_process.append(file_path)

        if not images_to_process:
            QMessageBox.warning(self, "No Images Selected",
                                "Please check at least one image to process.")
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
            images_to_process,
            output_folder,
            quality,
            remove_metadata,
            selected_format
        )

        self.worker.progress_updated.connect(self.on_progress_updated)
        self.worker.file_started.connect(self.on_file_started)
        self.worker.file_completed.connect(self.on_file_completed)
        self.worker.all_completed.connect(self.on_all_completed)

        self.worker.start()

    def on_progress_updated(self, progress):
        self.progress_bar.setValue(progress)

    def cancel_processing(self):
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Cancel Processing",
                "Are you sure you want to cancel processing?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.worker.cancel()
                self.status_label.setText("CANCELLING...")
                self.cancel_button.setEnabled(False)

    def on_file_started(self, filename):
        truncated = filename[:18] + "..." if len(filename) > 18 else filename
        self.status_label.setText(f"PROCESSING: {truncated}_")

    def on_file_completed(self, success, filename, message, stats=None):
        self.processing_log.add_entry(success, filename, message, stats)

    def on_all_completed(self, successful, failed, errors):
        self.process_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.cancel_button.setVisible(False)

        result_message = "Processing complete!\n\n"
        result_message += f"Successfully processed: {successful}\n"
        result_message += f"Failed: {failed}\n"

        if errors:
            result_message += "\nErrors:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                result_message += f"\n... and {len(errors) - 5} more errors"

        if failed > 0:
            QMessageBox.warning(self, "Processing Complete", result_message)
        else:
            QMessageBox.information(self, "Processing Complete", result_message)

        self.status_label.setText(f"{successful} PROCESSED_")
        self.worker = None

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Processing in Progress",
                "Image processing is still in progress. Do you want to cancel and exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.worker.cancel()
                self.worker.wait()
                self.save_settings()
                event.accept()
            else:
                event.ignore()
        else:
            self.save_settings()
            event.accept()

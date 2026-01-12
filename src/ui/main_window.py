import os
import json
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QListWidget, QListWidgetItem, QLabel,
                              QFileDialog, QLineEdit, QCheckBox, QGroupBox,
                              QSlider, QProgressBar, QMessageBox, QComboBox)
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QFont
from core.compressor import validate_quality
from core.converter import get_supported_formats
from core.worker import ImageProcessorWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Processor")
        self.setMinimumSize(QSize(800, 600))

        # Color palette
        self.colors = {
            'bg_primary': '#F3F0FF',    # 60% - Light purple (background)
            'bg_secondary': '#E0D7FF',   # 30% - Medium purple (UI elements)
            'accent': '#CBE67C',         # 10% - Lime green (highlights)
            'text': '#352E52'            # Dark purple (text)
        }

        # Supported image formats
        self.supported_formats = ('.jpg', '.jpeg', '.png')

        # Default settings
        self.default_output_folder = './output'
        self.config_file = 'config.json'

        # Worker thread
        self.worker = None

        # Apply global styling
        self.apply_global_style()

        # Initialize UI
        self.init_ui()

        # Load saved settings
        self.load_settings()

        # Enable drag and drop
        self.setAcceptDrops(True)

    def apply_global_style(self):
        """Apply global styling with VCR OSD Mono font and color palette"""
        # Set global font
        font = QFont("VCR OSD Mono", 10)
        self.setFont(font)

        # Apply global stylesheet
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['bg_primary']};
                color: {self.colors['text']};
                font-family: 'VCR OSD Mono';
            }}

            QWidget {{
                background-color: {self.colors['bg_primary']};
                color: {self.colors['text']};
                font-family: 'VCR OSD Mono';
            }}

            QLabel {{
                color: {self.colors['text']};
                font-family: 'VCR OSD Mono';
            }}

            QPushButton {{
                background-color: {self.colors['bg_secondary']};
                color: {self.colors['text']};
                border: 2px solid {self.colors['text']};
                border-radius: 5px;
                padding: 8px 16px;
                font-family: 'VCR OSD Mono';
                font-weight: bold;
            }}

            QPushButton:hover {{
                background-color: {self.colors['accent']};
                color: {self.colors['text']};
            }}

            QPushButton:pressed {{
                background-color: {self.colors['text']};
                color: {self.colors['bg_primary']};
            }}

            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
                border: 2px solid #999999;
            }}

            QLineEdit {{
                background-color: white;
                color: {self.colors['text']};
                border: 2px solid {self.colors['bg_secondary']};
                border-radius: 3px;
                padding: 5px;
                font-family: 'VCR OSD Mono';
            }}

            QLineEdit:focus {{
                border: 2px solid {self.colors['accent']};
            }}

            QListWidget {{
                background-color: white;
                color: {self.colors['text']};
                border: 2px solid {self.colors['bg_secondary']};
                border-radius: 5px;
                font-family: 'VCR OSD Mono';
            }}

            QListWidget::item:selected {{
                background-color: {self.colors['bg_secondary']};
                color: {self.colors['text']};
            }}

            QListWidget::item:hover {{
                background-color: {self.colors['bg_primary']};
            }}

            QGroupBox {{
                background-color: {self.colors['bg_secondary']};
                border: 2px solid {self.colors['text']};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                font-family: 'VCR OSD Mono';
                font-weight: bold;
            }}

            QGroupBox::title {{
                color: {self.colors['text']};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}

            QCheckBox {{
                color: {self.colors['text']};
                font-family: 'VCR OSD Mono';
                spacing: 8px;
            }}

            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {self.colors['text']};
                border-radius: 3px;
                background-color: white;
            }}

            QCheckBox::indicator:checked {{
                background-color: {self.colors['accent']};
                border: 2px solid {self.colors['text']};
            }}

            QComboBox {{
                background-color: white;
                color: {self.colors['text']};
                border: 2px solid {self.colors['bg_secondary']};
                border-radius: 3px;
                padding: 5px;
                font-family: 'VCR OSD Mono';
            }}

            QComboBox:hover {{
                border: 2px solid {self.colors['accent']};
            }}

            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}

            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {self.colors['text']};
                margin-right: 5px;
            }}

            QComboBox QAbstractItemView {{
                background-color: white;
                color: {self.colors['text']};
                selection-background-color: {self.colors['bg_secondary']};
                border: 2px solid {self.colors['text']};
                font-family: 'VCR OSD Mono';
            }}

            QSlider::groove:horizontal {{
                background: {self.colors['bg_secondary']};
                height: 8px;
                border-radius: 4px;
            }}

            QSlider::handle:horizontal {{
                background: {self.colors['accent']};
                border: 2px solid {self.colors['text']};
                width: 18px;
                height: 18px;
                margin: -7px 0;
                border-radius: 9px;
            }}

            QSlider::handle:horizontal:hover {{
                background: {self.colors['text']};
            }}

            QProgressBar {{
                background-color: {self.colors['bg_secondary']};
                border: 2px solid {self.colors['text']};
                border-radius: 5px;
                text-align: center;
                color: {self.colors['text']};
                font-family: 'VCR OSD Mono';
                font-weight: bold;
            }}

            QProgressBar::chunk {{
                background-color: {self.colors['accent']};
                border-radius: 3px;
            }}

            QMessageBox {{
                background-color: {self.colors['bg_primary']};
                color: {self.colors['text']};
                font-family: 'VCR OSD Mono';
            }}

            QMessageBox QPushButton {{
                min-width: 80px;
            }}
        """)

    def init_ui(self):
        """Initialize the user interface"""
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Title label
        title_label = QLabel("Drop images here or click 'Add Images'")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            font-size: 16px;
            padding: 20px;
            background-color: {self.colors['bg_secondary']};
            border: 2px solid {self.colors['text']};
            border-radius: 5px;
            color: {self.colors['text']};
            font-weight: bold;
        """)
        main_layout.addWidget(title_label)

        # Image list widget with checkboxes
        self.image_list = QListWidget()
        self.image_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.image_list.setToolTip("List of images to process. Check/uncheck items to include/exclude them.")
        main_layout.addWidget(self.image_list)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Add Images button
        self.add_button = QPushButton("Add Images")
        self.add_button.clicked.connect(self.add_images)
        self.add_button.setToolTip("Select images from your computer to add to the list")
        button_layout.addWidget(self.add_button)

        # Remove Selected button
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_selected)
        self.remove_button.setToolTip("Remove the selected images from the list")
        button_layout.addWidget(self.remove_button)

        # Clear All button
        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self.clear_all)
        self.clear_button.setToolTip("Remove all images from the list")
        button_layout.addWidget(self.clear_button)

        main_layout.addLayout(button_layout)

        # Settings section
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(15)

        # Output folder section
        output_folder_layout = QHBoxLayout()
        output_folder_label = QLabel("Output Folder:")
        self.output_folder_input = QLineEdit()
        self.output_folder_input.setText(self.default_output_folder)
        self.output_folder_input.setPlaceholderText("Select output folder...")
        self.output_folder_input.setToolTip("Folder where processed images will be saved")

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_output_folder)
        self.browse_button.setToolTip("Select a folder for saving processed images")

        output_folder_layout.addWidget(output_folder_label)
        output_folder_layout.addWidget(self.output_folder_input)
        output_folder_layout.addWidget(self.browse_button)

        settings_layout.addLayout(output_folder_layout)

        # Metadata removal checkbox
        self.remove_metadata_checkbox = QCheckBox("Remove metadata (EXIF)")
        self.remove_metadata_checkbox.setChecked(False)
        self.remove_metadata_checkbox.stateChanged.connect(self.save_settings)
        self.remove_metadata_checkbox.setToolTip("Remove EXIF metadata (camera info, GPS, etc.) from images")
        settings_layout.addWidget(self.remove_metadata_checkbox)

        # Format selector
        format_layout = QHBoxLayout()
        format_label = QLabel("Output Format:")
        self.format_selector = QComboBox()
        self.format_selector.addItems(get_supported_formats())
        self.format_selector.setCurrentIndex(0)  # Default to "Keep Original"
        self.format_selector.currentIndexChanged.connect(self.on_format_changed)
        self.format_selector.setToolTip("Choose output format: Keep Original, WebP (smaller), or AVIF (smallest)")

        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_selector)
        format_layout.addStretch()

        settings_layout.addLayout(format_layout)

        # Compression quality slider
        quality_layout = QHBoxLayout()
        quality_label_text = QLabel("Compression Quality:")
        self.quality_value_label = QLabel("85%")
        self.quality_value_label.setStyleSheet("font-weight: bold;")

        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setMinimum(1)
        self.quality_slider.setMaximum(100)
        self.quality_slider.setValue(85)
        self.quality_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.quality_slider.setTickInterval(10)
        self.quality_slider.valueChanged.connect(self.update_quality_label)
        self.quality_slider.setToolTip("Set compression quality (1-100). Higher = better quality, larger file size")

        quality_layout.addWidget(quality_label_text)
        quality_layout.addWidget(self.quality_slider)
        quality_layout.addWidget(self.quality_value_label)

        settings_layout.addLayout(quality_layout)

        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        # Processing section
        processing_layout = QVBoxLayout()
        processing_layout.setSpacing(10)

        # Start Processing button
        self.process_button = QPushButton("Start Processing")
        self.process_button.clicked.connect(self.start_processing)
        self.process_button.setToolTip("Process all checked images with the selected settings")
        self.process_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['accent']};
                color: {self.colors['text']};
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border: 3px solid {self.colors['text']};
                border-radius: 5px;
                font-family: 'VCR OSD Mono';
            }}
            QPushButton:hover {{
                background-color: {self.colors['text']};
                color: {self.colors['accent']};
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
                border: 2px solid #999999;
            }}
        """)
        processing_layout.addWidget(self.process_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setToolTip("Processing progress")
        processing_layout.addWidget(self.progress_bar)

        main_layout.addLayout(processing_layout)

        # Status label
        self.status_label = QLabel("No images loaded")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("padding: 10px;")
        main_layout.addWidget(self.status_label)

    def dragEnterEvent(self, event):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle drop event"""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        valid_files = self.validate_files(files)
        self.add_files_to_list(valid_files)

    def validate_files(self, files):
        """Validate file formats and return only supported image files"""
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
                f"Added {len(valid_files)} images, skipped {invalid_count} unsupported files"
            )

        return valid_files

    def add_files_to_list(self, file_paths):
        """Add validated files to the list widget"""
        for file_path in file_paths:
            # Check if file already exists in list
            if not self.file_exists_in_list(file_path):
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                file_size_mb = file_size / (1024 * 1024)  # Convert to MB

                # Create list item with checkbox
                item = QListWidgetItem(f"{file_name} ({file_size_mb:.2f} MB)")
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Checked)
                item.setData(Qt.ItemDataRole.UserRole, file_path)  # Store full path

                self.image_list.addItem(item)

        self.update_status()

    def file_exists_in_list(self, file_path):
        """Check if a file already exists in the list"""
        for i in range(self.image_list.count()):
            item = self.image_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == file_path:
                return True
        return False

    def add_images(self):
        """Open file dialog to select images"""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Images (*.jpg *.jpeg *.png)")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            valid_files = self.validate_files(selected_files)
            self.add_files_to_list(valid_files)

    def remove_selected(self):
        """Remove selected items from the list"""
        selected_items = self.image_list.selectedItems()

        if not selected_items:
            self.status_label.setText("No items selected")
            return

        for item in selected_items:
            self.image_list.takeItem(self.image_list.row(item))

        self.update_status()

    def clear_all(self):
        """Clear all items from the list"""
        self.image_list.clear()
        self.update_status()

    def update_status(self):
        """Update the status label with current image count"""
        count = self.image_list.count()
        if count == 0:
            self.status_label.setText("No images loaded")
        elif count == 1:
            self.status_label.setText("1 image loaded")
        else:
            self.status_label.setText(f"{count} images loaded")

    def browse_output_folder(self):
        """Open folder dialog to select output directory"""
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
        """Load settings from config file"""
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
        """Save settings to config file"""
        try:
            config = {
                'output_folder': self.output_folder_input.text(),
                'remove_metadata': self.remove_metadata_checkbox.isChecked()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def update_quality_label(self):
        """Update the quality label when slider value changes"""
        quality = self.quality_slider.value()
        self.quality_value_label.setText(f"{quality}%")

    def on_format_changed(self):
        """Handle format selector change"""
        selected_format = self.format_selector.currentText()
        # You could add logic here to show/hide certain options based on format
        # For example, different quality settings for different formats
        pass

    def start_processing(self):
        """Start processing selected images using worker thread"""
        # Get output folder
        output_folder = self.output_folder_input.text()

        # Validate output folder
        if not output_folder:
            QMessageBox.warning(self, "No Output Folder",
                              "Please select an output folder.")
            return

        # Create output folder if it doesn't exist
        if not os.path.exists(output_folder):
            try:
                os.makedirs(output_folder)
            except Exception as e:
                QMessageBox.critical(self, "Error",
                                   f"Could not create output folder: {str(e)}")
                return

        # Get checked images
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

        # Get settings
        quality = validate_quality(self.quality_slider.value())
        remove_metadata = self.remove_metadata_checkbox.isChecked()
        selected_format = self.format_selector.currentText()

        # Disable UI during processing
        self.process_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Create and configure worker thread
        self.worker = ImageProcessorWorker(
            images_to_process,
            output_folder,
            quality,
            remove_metadata,
            selected_format
        )

        # Connect signals
        self.worker.progress_updated.connect(self.on_progress_updated)
        self.worker.file_started.connect(self.on_file_started)
        self.worker.file_completed.connect(self.on_file_completed)
        self.worker.all_completed.connect(self.on_all_completed)

        # Start the worker thread
        self.worker.start()

    def on_progress_updated(self, progress):
        """Handle progress update signal from worker"""
        self.progress_bar.setValue(progress)

    def on_file_started(self, filename):
        """Handle file started signal from worker"""
        self.status_label.setText(f"Processing: {filename}")

    def on_file_completed(self, success, filename, message):
        """Handle file completed signal from worker"""
        # You could add per-file logging here if needed
        pass

    def on_all_completed(self, successful, failed, errors):
        """Handle all completed signal from worker"""
        # Re-enable UI
        self.process_button.setEnabled(True)
        self.progress_bar.setVisible(False)

        # Show completion message
        result_message = f"Processing complete!\n\n"
        result_message += f"Successfully processed: {successful}\n"
        result_message += f"Failed: {failed}\n"

        if errors:
            result_message += f"\nErrors:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                result_message += f"\n... and {len(errors) - 5} more errors"

        if failed > 0:
            QMessageBox.warning(self, "Processing Complete", result_message)
        else:
            QMessageBox.information(self, "Processing Complete", result_message)

        self.status_label.setText(f"{successful} images processed successfully")

        # Clean up worker
        self.worker = None

    def closeEvent(self, event):
        """Save settings when window is closed and handle active processing"""
        # Check if worker is still processing
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Processing in Progress",
                "Image processing is still in progress. Do you want to cancel and exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Cancel the worker
                self.worker.cancel()
                self.worker.wait()  # Wait for thread to finish
                self.save_settings()
                event.accept()
            else:
                event.ignore()
        else:
            self.save_settings()
            event.accept()

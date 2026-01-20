import os
from PyQt6.QtCore import QThread, pyqtSignal
from core.compressor import compress_image, validate_quality
from core.converter import convert_image


class ImageProcessorWorker(QThread):
    """
    Worker thread for processing images in the background.
    Emits signals to update the UI during processing.
    """

    # Signals
    progress_updated = pyqtSignal(int)  # Progress percentage
    file_started = pyqtSignal(str)  # Current file being processed
    file_completed = pyqtSignal(bool, str, str)  # (success, filename, message)
    all_completed = pyqtSignal(int, int, list)  # (successful, failed, errors)

    def __init__(self, images, output_folder, quality, remove_metadata, output_format):
        """
        Initialize the worker thread.

        Args:
            images: List of image file paths to process
            output_folder: Output directory path
            quality: Compression/conversion quality (1-100)
            remove_metadata: Whether to remove EXIF metadata
            output_format: Output format ('Keep Original', 'WebP', 'AVIF')
        """
        super().__init__()
        self.images = images
        self.output_folder = output_folder
        self.quality = validate_quality(quality)
        self.remove_metadata = remove_metadata
        self.output_format = output_format
        self.is_cancelled = False

    def run(self):
        """
        Execute the image processing in the background thread.
        """
        total_images = len(self.images)
        successful = 0
        failed = 0
        errors = []

        for idx, input_path in enumerate(self.images):
            # Check if processing was cancelled
            if self.is_cancelled:
                break

            # Get filename
            file_name = os.path.basename(input_path)

            # Emit signal that we're starting this file
            self.file_started.emit(file_name)

            # Generate output filename
            output_path = os.path.join(self.output_folder, file_name)

            # Process based on selected format
            try:
                if self.output_format == "Keep Original":
                    # Compress while keeping original format
                    success, message, reduction = compress_image(
                        input_path, output_path, self.quality, self.remove_metadata
                    )
                elif self.output_format in ["WebP", "AVIF"]:
                    # Convert to selected format
                    success, message, reduction = convert_image(
                        input_path, output_path, self.output_format,
                        self.quality, self.remove_metadata
                    )
                else:
                    success = False
                    message = f"Unsupported format: {self.output_format}"
                    reduction = 0.0

                # Track results
                if success:
                    successful += 1
                else:
                    failed += 1
                    errors.append(f"{file_name}: {message}")

                # Emit completion signal for this file
                self.file_completed.emit(success, file_name, message)

            except Exception as e:
                # Handle unexpected errors
                failed += 1
                error_msg = f"Unexpected error: {str(e)}"
                errors.append(f"{file_name}: {error_msg}")
                self.file_completed.emit(False, file_name, error_msg)

            # Update progress
            progress = int(((idx + 1) / total_images) * 100)
            self.progress_updated.emit(progress)

        # Emit completion signal with final statistics
        self.all_completed.emit(successful, failed, errors)

    def cancel(self):
        """
        Request cancellation of the processing.
        """
        self.is_cancelled = True

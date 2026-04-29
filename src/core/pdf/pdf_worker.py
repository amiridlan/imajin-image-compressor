import os
from PyQt6.QtCore import QThread, pyqtSignal
from utils.file_utils import safe_output_path, ensure_dir


class PdfWorker(QThread):
    """Background thread for PDF ↔ Word conversions."""

    file_started = pyqtSignal(str)
    file_completed = pyqtSignal(bool, str, str)   # success, filename, message
    progress_updated = pyqtSignal(int)             # 0-100
    all_completed = pyqtSignal(int, int, list)     # successful, failed, errors
    status_update = pyqtSignal(str)                # free-form status text

    def __init__(self, files, output_dir, direction, use_ocr=False, ocr_language='en'):
        """
        Args:
            files:       list of absolute file paths
            output_dir:  destination folder
            direction:   'pdf_to_word' | 'word_to_pdf'
            use_ocr:     apply OCR on scanned PDFs (pdf_to_word only)
            ocr_language: easyocr language code
        """
        super().__init__()
        self.files = files
        self.output_dir = output_dir
        self.direction = direction
        self.use_ocr = use_ocr
        self.ocr_language = ocr_language
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        ensure_dir(self.output_dir)
        total = len(self.files)
        successful, failed, errors = 0, 0, []

        for idx, src_path in enumerate(self.files):
            if self._cancelled:
                break

            filename = os.path.basename(src_path)
            self.file_started.emit(filename)

            try:
                result = self._convert(src_path)
            except Exception as e:
                result = {'success': False, 'output_path': None, 'error': str(e)}

            if result['success']:
                successful += 1
                out_name = os.path.basename(result['output_path'])
                self.file_completed.emit(True, filename, f"→ {out_name}")
            else:
                failed += 1
                err = result.get('error', 'Unknown error')
                errors.append(f"{filename}: {err}")
                self.file_completed.emit(False, filename, err)

            self.progress_updated.emit(int((idx + 1) / total * 100))

        self.all_completed.emit(successful, failed, errors)

    def _convert(self, src_path):
        filename = os.path.basename(src_path)
        base, _ = os.path.splitext(filename)

        if self.direction == 'pdf_to_word':
            out_name = base + '.docx'
            out_path = safe_output_path(self.output_dir, out_name)
            from core.pdf.pdf_to_word import convert_pdf_to_word, _is_scanned
            if self.use_ocr and _is_scanned(src_path):
                self.status_update.emit("OCR MODEL LOADING...")
            return convert_pdf_to_word(src_path, out_path,
                                       use_ocr=self.use_ocr,
                                       ocr_language=self.ocr_language)
        else:
            out_name = base + '.pdf'
            out_path = safe_output_path(self.output_dir, out_name)
            from core.pdf.word_to_pdf import convert_word_to_pdf
            return convert_word_to_pdf(src_path, out_path)

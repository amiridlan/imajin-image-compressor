import os
from pdf2docx import Converter


def convert_pdf_to_word(pdf_path, output_path, use_ocr=False, ocr_language='en'):
    """
    Convert a PDF to .docx.

    For digital PDFs:  pdf2docx handles layout, tables, images natively.
    For scanned PDFs:  when use_ocr=True, easyocr extracts text first,
                       then we write it into a plain docx.

    Returns:
        dict with keys: success (bool), output_path (str), error (str or None)
    """
    try:
        if use_ocr and _is_scanned(pdf_path):
            return _ocr_convert(pdf_path, output_path, ocr_language)
        return _direct_convert(pdf_path, output_path)
    except Exception as e:
        return {'success': False, 'output_path': None, 'error': str(e)}


def _direct_convert(pdf_path, output_path):
    try:
        cv = Converter(pdf_path)
        cv.convert(output_path)
        cv.close()
    except Exception as e:
        msg = str(e)
        if 'password' in msg.lower() or 'encrypt' in msg.lower():
            raise ValueError("This PDF is password-protected. Please unlock it first.")
        raise ValueError(f"PDF conversion failed — the file may be corrupted.\n\nDetails: {msg}")
    return {'success': True, 'output_path': output_path, 'error': None}


def _is_scanned(pdf_path):
    """Return True if PDF has no extractable text (likely a scanned image)."""
    try:
        import pdfminer.high_level as pdfminer
        text = pdfminer.extract_text(pdf_path)
        return not text or len(text.strip()) < 20
    except Exception:
        return False


def _ocr_convert(pdf_path, output_path, language):
    from pdf2image import convert_from_path
    from docx import Document

    try:
        images = convert_from_path(pdf_path, dpi=200)
    except Exception as e:
        raise ValueError(f"Could not read PDF for OCR — file may be corrupted.\n\nDetails: {e}")

    try:
        import easyocr
        reader = easyocr.Reader([language], gpu=False, verbose=False)
    except Exception as e:
        raise ValueError(
            "OCR model could not be loaded.\n"
            "This usually means the model download failed or there is insufficient disk space.\n\n"
            f"Details: {e}"
        )

    doc = Document()
    for page_num, img in enumerate(images, start=1):
        if page_num > 1:
            doc.add_page_break()
        try:
            results = reader.readtext(img, detail=0, paragraph=True)
        except Exception:
            results = []
        for line in results:
            doc.add_paragraph(line)

    doc.save(output_path)
    return {'success': True, 'output_path': output_path, 'error': None}

import os
from PIL import Image
from pyzbar.pyzbar import decode, ZBarSymbol


def scan_image(pil_image):
    """
    Detect all QR codes in a PIL Image.

    Returns list of dicts:
        data  - decoded string
        rect  - namedtuple(left, top, width, height) in pixels
        page  - None (set by callers that know the page number)
    """
    codes = decode(pil_image, symbols=[ZBarSymbol.QRCODE])
    results = []
    for code in codes:
        try:
            data = code.data.decode('utf-8')
        except UnicodeDecodeError:
            data = code.data.decode('latin-1', errors='replace')
        results.append({'data': data, 'rect': code.rect, 'page': None})
    return results


def sort_qr_codes(codes):
    """
    Sort QR codes in natural reading order: top-to-bottom, left-to-right.

    Codes whose vertical centres are within 60 px of each other are treated
    as the same row, then sorted left-to-right within the row.
    """
    if not codes:
        return codes

    ROW_THRESHOLD = 60

    def row_key(c):
        centre_y = c['rect'].top + c['rect'].height // 2
        return centre_y // ROW_THRESHOLD

    return sorted(codes, key=lambda c: (row_key(c), c['rect'].left))


def scan_file(file_path):
    """
    Scan an image or PDF file for QR codes.

    Returns sorted list of dicts (same structure as scan_image, with 'page'
    set to 1-based page number for PDFs, or None for images).

    Raises:
        ValueError  – unsupported file extension
        Exception   – propagated from pyzbar / pdf2image
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        codes = _scan_pdf(file_path)
    elif ext in ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.tif'):
        codes = _scan_image_file(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return sort_qr_codes(codes)


def _scan_image_file(path):
    try:
        img = Image.open(path).convert('RGB')
    except Exception:
        raise ValueError(
            f"Could not open image file.\n"
            "The file may be corrupted or in an unsupported format."
        )
    codes = scan_image(img)
    for c in codes:
        c['page'] = None
    return codes


def _scan_pdf(path):
    try:
        from pdf2image import convert_from_path
        images = convert_from_path(path, dpi=150)
    except Exception as e:
        raise ValueError(
            f"Could not read PDF pages.\n"
            "The file may be corrupted, password-protected, or malformed.\n\n"
            f"Details: {e}"
        )
    all_codes = []
    for page_num, img in enumerate(images, start=1):
        codes = scan_image(img.convert('RGB'))
        for c in codes:
            c['page'] = page_num
        all_codes.extend(codes)
    return all_codes

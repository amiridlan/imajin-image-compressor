from pathlib import Path
from pypdf import PdfReader, PdfWriter


def render_page_thumbnail(src: str, page_index: int, max_size: int = 160):
    """Return a QPixmap of the given page (caller must import Qt)."""
    import fitz
    from PyQt6.QtGui import QPixmap, QImage

    doc = fitz.open(src)
    page = doc[page_index]
    # Scale so longest side ≤ max_size
    scale = max_size / max(page.rect.width, page.rect.height)
    mat = fitz.Matrix(scale, scale)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
    doc.close()
    return QPixmap.fromImage(img)


def save_reordered(src: str, dest: str, order: list[int], rotations: dict[int, int]) -> None:
    """
    order     — list of original 0-based page indices in desired output order
    rotations — map of original page index → additional clockwise rotation (0/90/180/270)
    """
    reader = PdfReader(src)
    writer = PdfWriter()
    for orig_idx in order:
        page = reader.pages[orig_idx]
        rot = rotations.get(orig_idx, 0)
        if rot:
            page.rotate(rot)
        writer.add_page(page)
    with open(dest, "wb") as f:
        writer.write(f)


def suggested_output(src: str) -> str:
    p = Path(src)
    return str(p.parent / (p.stem + "_organized" + p.suffix))

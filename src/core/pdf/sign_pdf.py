from pathlib import Path
from PIL import Image
import io


def render_page_preview(src: str, page_index: int, max_size: int = 600):
    """Return (QPixmap, page_w_pt, page_h_pt) for the placement preview."""
    import fitz
    from PyQt6.QtGui import QPixmap, QImage

    doc = fitz.open(src)
    page = doc[page_index]
    pw, ph = page.rect.width, page.rect.height
    scale = max_size / max(pw, ph)
    mat = fitz.Matrix(scale, scale)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
    doc.close()
    return QPixmap.fromImage(img), pw, ph, scale


def embed_signature(
    src: str,
    dest: str,
    page_index: int,
    sig_pixmap,          # QPixmap of the signature (transparent bg preferred)
    x_pt: float,         # top-left x in PDF points
    y_pt: float,         # top-left y in PDF points
    w_pt: float,         # width in PDF points
    h_pt: float,         # height in PDF points
) -> None:
    import fitz

    # Convert QPixmap → PNG bytes
    from PyQt6.QtCore import QBuffer, QIODevice
    buf = QBuffer()
    buf.open(QIODevice.OpenModeFlag.WriteOnly)
    sig_pixmap.save(buf, "PNG")
    png_bytes = bytes(buf.data())
    buf.close()

    doc = fitz.open(src)
    page = doc[page_index]
    rect = fitz.Rect(x_pt, y_pt, x_pt + w_pt, y_pt + h_pt)
    page.insert_image(rect, stream=png_bytes)
    doc.save(dest)
    doc.close()


def page_count(src: str) -> int:
    import fitz
    doc = fitz.open(src)
    n = doc.page_count
    doc.close()
    return n


def suggested_output(src: str) -> str:
    p = Path(src)
    return str(p.parent / (p.stem + "_signed" + p.suffix))

from pathlib import Path
from pypdf import PdfReader, PdfWriter


def add_password(src: str, dest: str, password: str) -> None:
    reader = PdfReader(src)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(password, algorithm="AES-256")
    with open(dest, "wb") as f:
        writer.write(f)


def remove_password(src: str, dest: str, password: str) -> None:
    reader = PdfReader(src)
    if reader.is_encrypted:
        result = reader.decrypt(password)
        if result == 0:
            raise ValueError("Incorrect password")
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    with open(dest, "wb") as f:
        writer.write(f)


def suggested_output(src: str, mode: str) -> str:
    p = Path(src)
    suffix = "_protected" if mode == "add" else "_unlocked"
    return str(p.parent / (p.stem + suffix + p.suffix))

# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_data_files

datas = []
binaries = []
hiddenimports = ['PIL._tkinter_finder', 'pillow_avif', 'fitz', 'pymupdf']

# --- Pillow AVIF plugin ---
tmp = collect_all('pillow_avif')
datas += tmp[0]; binaries += tmp[1]; hiddenimports += tmp[2]

# --- QtAwesome (icon font data files) ---
tmp = collect_all('qtawesome')
datas += tmp[0]; binaries += tmp[1]; hiddenimports += tmp[2]

# --- pdf2docx ---
tmp = collect_all('pdf2docx')
datas += tmp[0]; binaries += tmp[1]; hiddenimports += tmp[2]

# --- python-docx ---
tmp = collect_all('docx')
datas += tmp[0]; binaries += tmp[1]; hiddenimports += tmp[2]

# --- easyocr (torch models download at runtime to ~/.EasyOCR) ---
tmp = collect_all('easyocr')
datas += tmp[0]; binaries += tmp[1]; hiddenimports += tmp[2]

# --- pyzbar + native libzbar DLL ---
tmp = collect_all('pyzbar')
datas += tmp[0]; binaries += tmp[1]; hiddenimports += tmp[2]

# --- OpenCV ---
tmp = collect_all('cv2')
datas += tmp[0]; binaries += tmp[1]; hiddenimports += tmp[2]

# --- PyMuPDF ---
tmp = collect_all('fitz')
datas += tmp[0]; binaries += tmp[1]; hiddenimports += tmp[2]

# --- Audiowide + Exo 2 fonts ---
datas += [('src/assets/fonts', 'assets/fonts')]

# --- Additional hidden imports ---
hiddenimports += [
    # PDF stack
    'pdf2docx', 'pdfminer', 'pdfminer.high_level', 'pdfminer.six',
    'docx2pdf', 'docx', 'docx.shared', 'docx.enum.text',
    # OCR
    'easyocr', 'torch', 'torchvision',
    # Image / QR
    'cv2', 'pyzbar', 'pyzbar.pyzbar', 'pdf2image',
    # Auto-updater
    'core.updater', 'version',
    # App modules (in case auto-discovery misses them)
    'core.qr.scanner', 'core.qr.malware_checker',
    'core.qr.urlhaus_list', 'core.qr.scan_worker', 'core.qr.camera_worker',
    'core.pdf.pdf_to_word', 'core.pdf.word_to_pdf', 'core.pdf.pdf_worker',
    'core.pdf.password_pdf', 'core.pdf.organize_pdf', 'core.pdf.sign_pdf',
    'utils.file_utils',
    # UI modules
    'ui.hub_window', 'ui.image_converter_window',
    'ui.pdf_converter_window', 'ui.qr_scanner_window',
    'ui.password_pdf_window', 'ui.organize_pdf_window', 'ui.sign_pdf_window',
    'ui.dialogs.qr_result_dialog', 'ui.components.feature_card',
    # Windows COM (Word → PDF)
    'win32com', 'win32com.client', 'pythoncom',
    # Network
    'requests', 'urllib3', 'certifi',
    # Qt
    'PyQt6.QtMultimedia',
]

a = Analysis(
    ['src\\main.py'],
    pathex=['src'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Imajin',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

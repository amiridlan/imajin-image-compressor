# Imajin v2.0 — Multi-Purpose Toolkit

A Windows desktop application built with PyQt6, styled with a **Synthwave Drive** dark theme (hot pink / deep purple). Six tools in one hub — image conversion, PDF utilities, and QR threat scanning.

## Features

### MEDIA

#### Image Converter
- Compress JPG / PNG with adjustable quality (1–100)
- Convert to **WebP** or **AVIF** for smaller files
- Drag-and-drop or multi-file picker
- Optional EXIF metadata removal
- Background processing — UI stays responsive

#### QR Scanner
- **Camera mode** — live viewfinder with real-time bounding boxes around detected codes
- **Upload mode** — scan images or multi-page PDFs for embedded QR codes
- **Threat detection** — checks URLs against the URLhaus malware blocklist (cached, updated every 24 h)
- **VirusTotal** — optional live URL scan with your own API key
- Multi-code support: all detected codes listed with SAFE / MALICIOUS / UNKNOWN badges
- Copy button per result; double-click for full details and one-click URL open

### DOCUMENTS

#### PDF ↔ Word Converter
- **PDF → Word** — preserves layout, tables, and images via `pdf2docx`
- **Scanned PDF → Word** — OCR fallback via `easyocr` (auto-detected)
- **Word → PDF** — one-click export via Microsoft Word COM automation
- Drag-and-drop file loading; progress log with per-file status

#### Sign PDF
- **Draw** a freehand signature on a built-in canvas
- **Upload** an image file (PNG / JPG / BMP / WebP) as the signature
- Preview the target page and **drag** the signature to any position
- Adjust signature width and height (in PDF points) before placing
- Saves as `filename_signed.pdf`

#### Organize PDF
- Visual thumbnail grid — see every page at a glance
- **Reorder** pages by drag-and-drop within the grid, or use Move Up / Move Down buttons
- **Rotate** individual pages clockwise or counter-clockwise
- **Delete** unwanted pages
- Saves as `filename_organized.pdf`

#### Password PDF
- **Add password** — AES-256 encryption with confirmation field
- **Remove password** — decrypt with the current password
- Instant error feedback for wrong passwords
- Saves as `filename_protected.pdf` or `filename_unlocked.pdf`

---

## Requirements

- Python 3.11+
- Microsoft Word (for Word → PDF conversion only)
- Poppler for Windows (for scanning QR codes inside PDF files)

## Installation

```bash
pip install -r requirements.txt
python src/main.py
```

### Poppler (PDF QR scanning)

1. Download the latest Poppler for Windows from [github.com/oschwartz10612/poppler-windows/releases](https://github.com/oschwartz10612/poppler-windows/releases)
2. Extract and add the `bin/` folder to your system `PATH`
3. Restart the application

## Dependencies

| Package | Purpose |
|---------|---------|
| PyQt6 >= 6.6.0 | GUI framework |
| Pillow >= 10.0.0 | Image processing |
| pillow-avif-plugin >= 1.4.0 | AVIF format support |
| qtawesome >= 1.2.3 | FontAwesome icons |
| opencv-python >= 4.8.0 | Camera capture & frame processing |
| pyzbar >= 0.1.9 | QR code detection |
| pdf2image >= 1.16.0 | PDF page rendering for QR scanning |
| requests >= 2.31.0 | URLhaus feed download |
| pdf2docx >= 0.5.6 | PDF → Word conversion |
| pdfminer.six >= 20221105 | Scanned PDF detection |
| easyocr >= 1.7.0 | OCR for scanned PDFs |
| docx2pdf >= 0.1.8 | Word → PDF via COM |
| pypdf >= 4.0.0 | PDF password encryption / decryption, page reordering |
| pymupdf >= 1.23.0 | PDF page thumbnail rendering, signature image embedding |

## Usage

### Hub screen

Launch the app. The hub is divided into two groups:

- **MEDIA** — Image Converter, QR Scanner
- **DOCUMENTS** — PDF ↔ Word, Sign PDF, Organize PDF, Password PDF

Click any card to open that tool. Click **← Back** inside any tool to return to the hub. All tools support drag-and-drop file loading.

### Image Converter

1. Drag images into the drop zone or click **Add Images**
2. Choose output folder, format (WebP / AVIF), and quality
3. Click **Start Processing**

### PDF ↔ Word

1. Select direction: **PDF → Word** or **Word → PDF**
2. Drag files into the drop zone or click **Add Files**
3. Choose output folder
4. Enable **Use OCR** if converting scanned/image PDFs (first run downloads the OCR model, ~100 MB)
5. Click **Convert**

> Word → PDF requires Microsoft Word to be installed.

### Sign PDF

1. Drag a PDF into the drop zone or click **Open PDF**
2. Choose a page using the page spinner
3. **Draw tab** — draw your signature with the mouse on the canvas, then click **Clear** to redo
4. **Upload Image tab** — drag an image file onto the window (or browse) to use as the signature
5. Adjust signature width and height (PDF points)
6. Click **Place Signature on Preview** — the signature appears on the page preview
7. Drag the signature box to reposition it
8. Click **Save Signed PDF**

### Organize PDF

1. Drag a PDF into the drop zone or click **Open PDF** — page thumbnails load automatically
2. Select a page thumbnail and use the toolbar to:
   - **↺ / ↻** — rotate counter-clockwise / clockwise
   - **🗑** — delete the page
   - **↑ / ↓** — move the page up or down
   - Drag thumbnails directly to reorder
3. Click **Save Organized PDF**

### Password PDF

**Add password**
1. Drag a PDF into the drop zone or click **Browse PDF**
2. Select **Add Password**
3. Enter and confirm the new password
4. Click **Apply** — saved as `filename_protected.pdf`

**Remove password**
1. Drag a PDF into the drop zone or click **Browse PDF**
2. Select **Remove Password**
3. Enter the current password
4. Click **Apply** — saved as `filename_unlocked.pdf`

### QR Scanner

**Camera**
1. Click **Start Camera** (grant webcam access if prompted)
2. Hold a QR code in front of the camera — bounding boxes appear automatically
3. Detected codes appear in the results panel with a threat status badge

**Upload**
1. Switch to **Upload** tab
2. Drag an image or PDF onto the window, or click to browse
3. Click **Scan**

**VirusTotal (optional)**
- Paste your VirusTotal API key in the Settings panel to enable live URL scanning beyond the offline blocklist

## Building the Executable

```cmd
pyinstaller Imajin.spec
```

The standalone `.exe` is written to `dist/Imajin.exe`.

> easyocr downloads its model at first use (~100 MB). This happens inside the packaged exe the first time OCR is requested.

## Project Structure

```
imajin/
├── src/
│   ├── main.py
│   ├── assets/
│   │   └── fonts/                  # Outfit & DM Sans variable fonts
│   ├── ui/
│   │   ├── hub_window.py           # Main window, navigation, MEDIA/DOCUMENTS groups
│   │   ├── image_converter_window.py
│   │   ├── pdf_converter_window.py
│   │   ├── qr_scanner_window.py
│   │   ├── sign_pdf_window.py      # Draw pad + page preview + signature placement
│   │   ├── organize_pdf_window.py  # Thumbnail grid, drag-to-reorder, rotate, delete
│   │   ├── password_pdf_window.py  # Add / remove AES-256 password
│   │   ├── components/
│   │   │   └── feature_card.py     # Clickable hub cards (supports custom size)
│   │   ├── dialogs/
│   │   │   └── qr_result_dialog.py
│   │   └── styles/
│   │       └── theme.py            # All design tokens
│   ├── core/
│   │   ├── image/                  # Image compression & conversion
│   │   ├── pdf/
│   │   │   ├── pdf_to_word.py
│   │   │   ├── word_to_pdf.py
│   │   │   ├── pdf_worker.py
│   │   │   ├── sign_pdf.py         # pymupdf page preview & image embed
│   │   │   ├── organize_pdf.py     # pypdf page reorder/rotate + thumbnails
│   │   │   └── password_pdf.py     # pypdf encrypt / decrypt
│   │   └── qr/
│   │       ├── scanner.py          # QR detection & sorting
│   │       ├── malware_checker.py  # URLhaus + VirusTotal
│   │       ├── urlhaus_list.py     # Threat feed cache
│   │       ├── scan_worker.py      # Background scan thread
│   │       └── camera_worker.py    # Live camera thread
│   └── utils/
│       ├── file_utils.py
│       └── metadata.py
├── Imajin.spec                     # PyInstaller build spec
├── requirements.txt
└── README.md
```

## Troubleshooting

**AVIF format not available**
```bash
pip install pillow-avif-plugin
```

**Camera not detected**
- Check webcam permissions in Windows Settings > Privacy > Camera
- Try a different camera index (default is 0) in the QR Scanner settings panel

**OCR first run is slow**
- easyocr downloads its English model (~100 MB) on first use — this is expected

**Word → PDF fails**
- Microsoft Word must be installed and licensed
- If Word is installed but still fails, try running the app as Administrator

**QR codes in PDFs not detected**
- Poppler must be installed and its `bin/` folder must be on the system PATH

**Sign PDF — signature not visible after saving**
- Ensure the signature canvas is not empty (Draw tab) or a valid image is loaded (Upload tab)
- Click **Place Signature on Preview** before clicking Save

**Password PDF — "Incorrect password" error**
- The PDF is encrypted with a different password than entered
- Some PDFs use owner-only restrictions; try the user password instead

# Imajin v2.0 — Multi-Purpose Toolkit

A Windows desktop application built with PyQt6. Convert images, transform PDFs, and scan QR codes for malware — all from a single hub.

## Features

### Image Converter
- Compress JPG / PNG with adjustable quality (1–100)
- Convert to **WebP** or **AVIF** for smaller files
- Drag-and-drop or multi-file picker
- Optional EXIF metadata removal
- Background processing — UI stays responsive

### PDF ↔ Word Converter
- **PDF → Word** — preserves layout, tables, and images via `pdf2docx`
- **Scanned PDF → Word** — OCR fallback via `easyocr` (auto-detected)
- **Word → PDF** — one-click export via Microsoft Word COM automation
- Progress log with per-file status

### QR Scanner
- **Camera mode** — live viewfinder with real-time bounding boxes around detected codes
- **Upload mode** — scan images or multi-page PDFs for embedded QR codes
- **Threat detection** — checks URLs against the URLhaus malware blocklist (cached, updated every 24 h)
- **VirusTotal** — optional live URL scan with your own API key
- Multi-code support: all detected codes listed with SAFE / MALICIOUS / UNKNOWN badges
- Double-click any result for full details and one-click URL open

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
| qtawesome >= 1.3.0 | FontAwesome icons |
| opencv-python >= 4.8.0 | Camera capture & frame processing |
| pyzbar >= 0.1.9 | QR code detection |
| pdf2image >= 1.16.0 | PDF page rendering for QR scanning |
| requests >= 2.31.0 | URLhaus feed download |
| pdf2docx >= 0.5.6 | PDF → Word conversion |
| pdfminer.six >= 20221105 | Scanned PDF detection |
| easyocr >= 1.7.0 | OCR for scanned PDFs |
| docx2pdf >= 0.1.8 | Word → PDF via COM |
| python-docx >= 1.1.0 | DOCX document creation |

## Usage

### Hub screen

Launch the app and click any feature card to open that tool. Click **Back** inside any tool to return to the hub.

### Image Converter

1. Drag images into the drop zone or click **Add Images**
2. Choose output folder, format, and quality
3. Click **Start Processing**

### PDF ↔ Word

1. Select direction: **PDF → Word** or **Word → PDF**
2. Drop files into the list
3. Choose output folder
4. Enable **Use OCR** if converting scanned/image PDFs (first run downloads the OCR model, ~100 MB)
5. Click **Convert**

> Word → PDF requires Microsoft Word to be installed.

### QR Scanner

**Camera**
1. Click **Start Camera** (grant webcam access if prompted)
2. Hold a QR code in front of the camera — bounding boxes appear automatically
3. Detected codes appear in the results panel with a threat status badge

**Upload**
1. Switch to **Upload** tab
2. Drop an image or PDF into the zone
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
│   │   └── fonts/                  # Space Grotesk font files
│   ├── ui/
│   │   ├── hub_window.py           # Main window & navigation
│   │   ├── image_converter_window.py
│   │   ├── pdf_converter_window.py
│   │   ├── qr_scanner_window.py
│   │   ├── components/
│   │   │   └── feature_card.py     # Clickable hub cards
│   │   ├── dialogs/
│   │   │   └── qr_result_dialog.py
│   │   └── styles/
│   │       └── theme.py            # Design tokens
│   ├── core/
│   │   ├── image/                  # Image compression & conversion
│   │   ├── pdf/
│   │   │   ├── pdf_to_word.py
│   │   │   ├── word_to_pdf.py
│   │   │   └── pdf_worker.py
│   │   └── qr/
│   │       ├── scanner.py          # QR detection & sorting
│   │       ├── malware_checker.py  # URLhaus + VirusTotal
│   │       ├── urlhaus_list.py     # Threat feed cache
│   │       ├── scan_worker.py      # Background scan thread
│   │       └── camera_worker.py   # Live camera thread
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

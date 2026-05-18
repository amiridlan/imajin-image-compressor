# CLAUDE.md — Imajin v2.0

## What this project is

Imajin is a **Windows desktop application** built with PyQt6. It is a multi-tool hub that exposes three features — image compression/conversion, PDF↔Word conversion, and QR code scanning with threat detection — through a shared hub home screen. It ships as a standalone `.exe` via PyInstaller.

**Entry point:** `src/main.py` → `HubWindow`

---

## Project structure

```
src/
├── main.py                         # Entry point
├── assets/fonts/                   # Outfit-Variable.ttf, DMSans-Variable.ttf
├── ui/
│   ├── hub_window.py               # Root QMainWindow, QStackedWidget nav, global stylesheet
│   │                               # Hub groups: MEDIA (Image, QR) / DOCUMENTS (PDF tools)
│   ├── image_converter_window.py   # Image Converter feature window
│   ├── pdf_converter_window.py     # PDF ↔ Word feature window
│   ├── qr_scanner_window.py        # QR Scanner feature window
│   ├── password_pdf_window.py      # Add / remove PDF password
│   ├── organize_pdf_window.py      # Visual page reorder / rotate / delete
│   ├── sign_pdf_window.py          # Draw or upload signature, place on page
│   ├── components/
│   │   ├── feature_card.py         # Clickable hub cards (shadow-gated hit area)
│   │   │                           # Accepts size=(w,h) — Media=280×320, Docs=220×270
│   │   ├── animated_button.py
│   │   ├── processing_log.py
│   │   └── quality_presets.py
│   ├── dialogs/
│   │   ├── qr_result_dialog.py     # QR detail dialog (full data + open URL)
│   │   └── conflict_dialog.py
│   └── styles/
│       ├── theme.py                # ALL design tokens — edit only here
│       └── animations.py
├── core/
│   ├── worker.py                   # Image processing QThread
│   ├── compressor.py
│   ├── converter.py
│   ├── conflict_checker.py
│   ├── pdf/
│   │   ├── pdf_to_word.py          # pdf2docx + easyocr OCR fallback
│   │   ├── word_to_pdf.py          # docx2pdf via Word COM
│   │   ├── pdf_worker.py           # PDF conversion QThread worker
│   │   ├── password_pdf.py         # pypdf encrypt / decrypt
│   │   ├── organize_pdf.py         # pymupdf thumbnails + pypdf page reorder
│   │   └── sign_pdf.py             # pymupdf page preview + image embed
│   └── qr/
│       ├── scanner.py              # pyzbar decode + result sorting
│       ├── malware_checker.py      # URLhaus + VirusTotal
│       ├── urlhaus_list.py         # Threat feed cache (24 h TTL)
│       ├── scan_worker.py          # Upload-mode scan QThread
│       └── camera_worker.py        # Live camera QThread (OpenCV)
└── utils/
    ├── file_utils.py
    └── metadata.py
```

---

## Theme system

**Single source of truth: `src/ui/styles/theme.py`**

Never hardcode colors or font names anywhere else. Always reference `Theme.*` constants.

### Synthwave Drive palette

| Token | Value | Role |
|---|---|---|
| `BG_PRIMARY` | `#0D0221` | 60 % — page / window background |
| `BG_SECONDARY` | `#1A0533` | 30 % — panels, cards, header bar |
| `ACCENT` | `#FF2D78` | 10 % — interactive elements, borders on hover |
| `TEXT` | `#F0E6FF` | Body text, borders |
| `TEXT_MUTED` | `#9B7BB8` | Hints, secondary labels |
| `INPUT_BG` | `#0F0428` | Input field background |

### Fonts

| Token | Value | Use |
|---|---|---|
| `FONT_DISPLAY` | `'Outfit'` | Headings, titles, card labels |
| `FONT_FAMILY` | `'DM Sans 14pt'` | **All body text** |

> **Critical quirk:** The DM Sans variable font (`DMSans-Variable.ttf`) registers in Qt as `'DM Sans 14pt'`, **not** `'DM Sans'`. Using `'DM Sans'` renders only the thin-weight stub. Always use `Theme.FONT_FAMILY` — never write `'DM Sans'` directly.

The global stylesheet is applied once in `HubWindow._apply_global_style()` and cascades to all child widgets. Feature windows inherit it automatically via `QStackedWidget`.

---

## Navigation

`HubWindow` owns a `QStackedWidget`. Feature windows are created lazily on first open and added to the stack — they are never destroyed until the app closes.

```
hub_page  ← always index 0
image_window  ← added on first click
pdf_window
qr_window
```

Transitions use `QGraphicsOpacityEffect` + `QPropertyAnimation` on `b"opacity"`.

> **Important:** After the fade animation completes, `widget.setGraphicsEffect(None)` **must** be called. Leaving an opacity effect on a parent widget causes `QPainter not active` errors when child widgets with their own `QGraphicsEffect` (e.g. `FeatureCard` shadow) try to paint.

---

## FeatureCard hit-area behaviour

`FeatureCard` uses `QGraphicsDropShadowEffect`. Qt extends the widget's bounding rect by `blurRadius` pixels in every direction for event dispatch — so without a guard, hover/click events fire outside the visible card.

The fix lives in `feature_card.py`:

- `setMouseTracking(True)` — lets `mouseMoveEvent` fire without a button held.
- `_in_card(pos)` — `return self.rect().contains(pos)` — gates all event handlers to the literal 280 × 320 card rect.
- `_set_hover(on)` — idempotency guard prevents redundant style repaints.

Do not remove or bypass these guards.

---

## Background processing

All heavy work runs in `QThread` subclasses. Never block the main thread.

| Worker | File | Signals |
|---|---|---|
| Image compression | `core/worker.py` | `progress`, `file_done`, `finished` |
| PDF conversion | `core/pdf/pdf_worker.py` | `progress`, `file_done`, `finished`, `error` |
| PDF password | `ui/password_pdf_window._Worker` | `done`, `error` |
| PDF organize save | `ui/organize_pdf_window._SaveWorker` | `done`, `error` |
| PDF thumbnail load | `ui/organize_pdf_window._ThumbnailLoader` | `page_ready` |
| PDF sign save | `ui/sign_pdf_window._SaveWorker` | `done`, `error` |
| QR upload scan | `core/qr/scan_worker.py` | `result_found`, `finished`, `error` |
| Camera feed | `core/qr/camera_worker.py` | `frame_ready`, `code_detected` |

---

## Build

```cmd
pyinstaller Imajin.spec
# output: dist/Imajin.exe
```

The spec bundles `src/assets/fonts/` and the URLhaus cache. easyocr downloads its model (~100 MB) at first OCR use — this happens inside the packaged exe.

---

## Key dependencies and why they exist

| Package | Why |
|---|---|
| `pillow-avif-plugin` | AVIF encode support (Pillow alone can't write AVIF) |
| `easyocr` | OCR for scanned/image PDFs — auto-detected, not always triggered |
| `docx2pdf` | Word COM automation — requires Microsoft Word installed |
| `pdf2image` + Poppler | Render PDF pages to images for QR scanning |
| `pyzbar` | QR/barcode decode from image arrays |
| `qtawesome` | FontAwesome 5 icons via `qta.icon()` |
| `pypdf` | PDF password encryption/decryption, page reordering and rotation |
| `pymupdf` (fitz) | PDF page thumbnail rendering, signature image embedding |

---

## Hub layout

The hub is split into two labeled sections:
- **MEDIA** — Image Converter, QR Scanner — cards at `size=(280, 320)`
- **DOCUMENTS** — PDF↔Word, Sign PDF, Organize PDF, Password PDF — cards at `size=(220, 270)`

`FeatureCard` accepts a `size=(w, h)` parameter (defaults to `(280, 320)`). Always pass the appropriate size when adding a new card.

Section headers are rendered by `HubWindow._section_label(text)` — a `QLabel` flanked by two thin `QFrame` dividers.

---

## Known constraints

- **Word → PDF** requires Microsoft Word installed and licensed on the machine.
- **PDF QR scanning** requires Poppler for Windows on the system `PATH`.
- The app is **Windows-only** (Word COM, PyInstaller spec, `.exe` distribution).
- `easyocr` first run downloads a ~100 MB English model — inform users.
- **Sign PDF** — `SignaturePad.get_pixmap()` walks every pixel to make the background transparent; this is fast for the 420×160 canvas but do not scale the canvas up without revisiting that loop.

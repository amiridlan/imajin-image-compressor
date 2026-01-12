# Image Processor - Project Plan

# Project Name - Imajin

## Tech Stack

- Python 3.11+, PyQt6, Pillow, PyInstaller
- Structure: src/{main.py, ui/, core/, utils/}, tests/, requirements.txt

## Features

1. Compress images (bulk, adjustable quality 1-100)
2. Convert JPG/PNG → WebP/AVIF (quality control)
3. Drag-drop + manual file selection
4. Custom output destination
5. Optional metadata (EXIF) removal

---

## Sprint 1: Foundation (Week 1)

**Goal**: Installable app with empty window

**Tasks**:

- Create folder structure: `src/{main.py, ui/main_window.py, core/, utils/}`
- Add `requirements.txt`: `PyQt6>=6.6.0`, `Pillow>=10.0.0`
- Create `main.py`: PyQt6 app entry point with 800x600 window titled "Image Processor"
- Create `install.sh`/`install.bat`: `pip install -r requirements.txt`
- Add `README.md` with install instructions

**Deliverable**: User runs install script → launches empty window

---

## Sprint 2: UI & File Selection (Week 2)

**Goal**: Drag-drop images, see list with checkboxes

**Tasks**:

- `main_window.py`: Add drag-drop area (accept .jpg, .jpeg, .png)
- Add QListWidget with checkboxes showing filename + size
- Add "Add Images" button (QFileDialog multi-select)
- Add "Clear All" and "Remove Selected" buttons
- Validate file formats on drop/select

**Deliverable**: Functional image list management

---

## Sprint 3: Settings UI (Week 3)

**Goal**: Configure output folder and metadata option

**Tasks**:

- Add "Output Folder" section with QLineEdit + browse button (QFileDialog)
- Default output: `./output`
- Add QCheckBox: "Remove metadata (EXIF)" (default unchecked)
- Optional: Save settings to JSON config file

**Deliverable**: Output and metadata settings functional

---

## Sprint 4: Compression (Week 4)

**Goal**: Compress images with quality control

**Tasks**:

- Create `core/compressor.py`: Use `PIL.Image.save(quality=X)` preserving format
- Create `utils/metadata.py`: Strip EXIF via `image.save()` without `exif` param
- Add QSlider (0-100, default 85) with label: "Compression Quality: X%"
- Add "Start Processing" button → call compressor for selected images
- Add QProgressBar
- Apply metadata removal if checkbox enabled

**Deliverable**: Working compression + metadata removal

---

## Sprint 5: Format Conversion (Week 5)

**Goal**: Convert to WebP/AVIF with quality control

**Tasks**:

- Create `core/converter.py`:
  - JPG/PNG → WebP: `image.save('file.webp', quality=X)`
  - JPG/PNG → AVIF: `image.save('file.avif', quality=X)` (needs `pillow-avif-plugin`)
- Add format selector: QComboBox ["Keep Original", "WebP", "AVIF"]
- Add separate quality slider for conversions
- Update `core/processor.py` to route compress vs convert
- Handle errors (unsupported formats)

**Deliverable**: WebP/AVIF conversion working

---

## Sprint 6: Batch Processing (Week 6)

**Goal**: Real-time progress for bulk operations

**Tasks**:

- Implement QThread for background processing (keep UI responsive)
- Update QProgressBar per file: `current/total * 100`
- Show QLabel: "Processing: filename.jpg"
- Add completion QMessageBox: "Processed X files, Y errors"
- Log errors to list

**Deliverable**: Smooth bulk processing with feedback

---

## Sprint 7: Polish & Package (Week 7)

**Goal**: Production-ready executable

**Tasks**:

- Add app icon, improve layout/spacing, add tooltips
- Test: various formats, large files, edge cases (no output folder, corrupted files)
- Create executable: `pyinstaller --onefile --windowed main.py`
- Test on clean machines
- Update README with screenshots, usage guide

**Deliverable**: Distributable .exe/.app + documentation

---

## Key Implementation Notes

### Compression (Sprint 4)

```python
# core/compressor.py
from PIL import Image
def compress(input_path, output_path, quality, remove_metadata):
    img = Image.open(input_path)
    save_kwargs = {'quality': quality, 'optimize': True}
    if remove_metadata:
        img.save(output_path, **save_kwargs)
    else:
        img.save(output_path, exif=img.getexif(), **save_kwargs)
```

### Conversion (Sprint 5)

```python
# core/converter.py
def convert(input_path, output_path, format, quality):
    img = Image.open(input_path).convert('RGB')
    img.save(output_path, format=format, quality=quality)
```

### Drag-Drop (Sprint 2)

```python
# ui/main_window.py
def dragEnterEvent(self, event):
    if event.mimeData().hasUrls():
        event.acceptProposedAction()

def dropEvent(self, event):
    files = [u.toLocalFile() for u in event.mimeData().urls()]
    valid = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png'))]
    self.add_images(valid)
```

---

## Timeline

7 weeks total | User can install by Sprint 1 | Core features by Sprint 5

**Next Step**: Type "next" to start Sprint 1 development

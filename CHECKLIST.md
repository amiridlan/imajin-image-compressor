# Imajin - Sprint Checklist

## Project Overview

**Name**: Imajin
**Purpose**: Image processing application with compression and format conversion
**Tech Stack**: Python 3.11+, PyQt6, Pillow, PyInstaller
**Timeline**: 7 weeks

---

## Sprint 1: Foundation ✓ Week 1

**Goal**: Installable app with empty window

- [ ] Create folder structure: `src/{main.py, ui/main_window.py, core/, utils/}`
- [ ] Add `requirements.txt` with PyQt6>=6.6.0 and Pillow>=10.0.0
- [ ] Create `main.py` with PyQt6 app entry point (800x600 window, title "Image Processor")
- [ ] Create `install.sh` for Linux/Mac
- [ ] Create `install.bat` for Windows
- [ ] Add `README.md` with installation instructions
- [ ] **Test**: User runs install script → launches empty window

---

## Sprint 2: UI & File Selection ✓ Week 2

**Goal**: Drag-drop images, see list with checkboxes

- [ ] Implement drag-drop area in `main_window.py` (accept .jpg, .jpeg, .png)
- [ ] Add QListWidget with checkboxes showing filename + size
- [ ] Add "Add Images" button with QFileDialog multi-select
- [ ] Add "Clear All" button
- [ ] Add "Remove Selected" button
- [ ] Implement file format validation on drop/select
- [ ] **Test**: Drag-drop works, manual selection works, list displays correctly

---

## Sprint 3: Settings UI ✓ Week 3

**Goal**: Configure output folder and metadata option

- [ ] Add "Output Folder" section with QLineEdit
- [ ] Add browse button with QFileDialog for output folder
- [ ] Set default output to `./output`
- [ ] Add QCheckBox: "Remove metadata (EXIF)" (default unchecked)
- [ ] (Optional) Implement settings persistence to JSON config file
- [ ] **Test**: Output folder selection works, metadata checkbox toggles

---

## Sprint 4: Compression ✓ Week 4

**Goal**: Compress images with quality control

- [ ] Create `core/compressor.py` with PIL.Image.save(quality=X)
- [ ] Implement format preservation during compression
- [ ] Create `utils/metadata.py` for EXIF stripping
- [ ] Add QSlider (0-100, default 85) for compression quality
- [ ] Add quality label display: "Compression Quality: X%"
- [ ] Add "Start Processing" button
- [ ] Wire button to compressor for selected images
- [ ] Add QProgressBar for processing feedback
- [ ] Implement metadata removal when checkbox enabled
- [ ] **Test**: Compression works at various quality levels, metadata removal works

---

## Sprint 5: Format Conversion ✓ Week 5

**Goal**: Convert to WebP/AVIF with quality control

- [ ] Create `core/converter.py`
- [ ] Implement JPG/PNG → WebP conversion with quality control
- [ ] Implement JPG/PNG → AVIF conversion (requires pillow-avif-plugin)
- [ ] Add format selector QComboBox ["Keep Original", "WebP", "AVIF"]
- [ ] Add separate quality slider for conversions
- [ ] Update/create `core/processor.py` to route compress vs convert operations
- [ ] Implement error handling for unsupported formats
- [ ] **Test**: WebP conversion works, AVIF conversion works, quality control effective

---

## Sprint 6: Batch Processing ✓ Week 6

**Goal**: Real-time progress for bulk operations

- [ ] Implement QThread for background processing
- [ ] Ensure UI remains responsive during processing
- [ ] Update QProgressBar per file: current/total \* 100
- [ ] Add QLabel showing: "Processing: filename.jpg"
- [ ] Create completion QMessageBox: "Processed X files, Y errors"
- [ ] Implement error logging to list/file
- [ ] **Test**: Bulk processing 10+ images, UI stays responsive, progress accurate

---

## Sprint 7: Polish & Package ✓ Week 7

**Goal**: Production-ready executable

- [ ] Add application icon
- [ ] Improve UI layout and spacing
- [ ] Add tooltips to all controls
- [ ] Test various image formats (JPG, PNG, etc.)
- [ ] Test large files (10MB+)
- [ ] Test edge cases: no output folder, corrupted files, no permissions
- [ ] Create executable with PyInstaller: `pyinstaller --onefile --windowed main.py`
- [ ] Test executable on clean Windows machine
- [ ] Test executable on clean Mac machine (if applicable)
- [ ] Test executable on clean Linux machine (if applicable)
- [ ] Update README.md with screenshots
- [ ] Update README.md with detailed usage guide
- [ ] **Test**: Executable runs without Python installation, all features work

---

## Key Files to Create

### Core Structure

- `src/main.py` - Application entry point
- `src/ui/main_window.py` - Main UI window
- `src/core/compressor.py` - Image compression logic
- `src/core/converter.py` - Format conversion logic
- `src/core/processor.py` - Processing coordinator
- `src/utils/metadata.py` - EXIF metadata handling

### Configuration & Documentation

- `requirements.txt` - Python dependencies
- `install.sh` - Linux/Mac installation script
- `install.bat` - Windows installation script
- `README.md` - User documentation
- (Optional) `config.json` - Settings persistence

---

## Progress Tracking

**Current Sprint**: Sprint 1
**Overall Progress**: 0/7 Sprints Complete

### Notes

- Use this checklist to track progress throughout the 7-week development cycle
- Mark items complete as you finish them
- Update Current Sprint as you progress
- Add any blockers or notes below each sprint as needed

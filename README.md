# Imajin - Image Processor

An image processing Python application for compressing and converting images with drag-and-drop interface.

## Features

- **Bulk Image Compression** - Compress multiple images with adjustable quality (1-100)
- **Format Conversion** - Convert JPG/PNG to WebP or AVIF formats
- **Drag-and-Drop Interface** - Simply drag images into the window
- **Metadata Removal** - Optionally remove EXIF data (camera info, GPS, etc.)

## Requirements

- Python 3.11 or higher
- PyQt6 >= 6.6.0
- Pillow >= 10.0.0
- pillow-avif-plugin >= 1.4.0 (for AVIF support)

## Installation

### Windows

1. Run the installation script:

   ```cmd
   install.bat
   ```

2. Launch the application:
   ```cmd
   python src/main.py
   ```

### Linux/Mac

1. Make the install script executable and run it:

   ```bash
   chmod +x install.sh
   ./install.sh
   ```

2. Launch the application:
   ```bash
   python src/main.py
   ```

### Manual Installation

If you prefer to install manually:

```bash
pip install -r requirements.txt
python src/main.py
```

## Usage Guide

### Quick Start

1. **Add Images**

   - Drag and drop images directly into the window, OR
   - Click "Add Images" button to select files

2. **Configure Settings**

   - **Output Folder**: Choose where to save processed images (default: `./output`)
   - **Output Format**: Select format
     - `Keep Original`: Compress while maintaining format (JPG stays JPG)
     - `WebP`: Convert to WebP format (smaller files, wide support)
     - `AVIF`: Convert to AVIF format (smallest files, newer format)
   - **Compression Quality**: Adjust slider (1-100)
     - Lower values = smaller files, lower quality
     - Higher values = better quality, larger files
     - Recommended: 85% for good balance
   - **Remove Metadata**: Check to strip EXIF data from images

3. **Process Images**
   - Check/uncheck images in the list to include/exclude them
   - Click "Start Processing"
   - Monitor progress in real-time
   - View completion summary

### Detailed Features

#### Image List Management

- **Add Images**: Select multiple images at once using Ctrl+Click or Shift+Click
- **Remove Selected**: Highlight images and click to remove them from the list
- **Clear All**: Remove all images from the list
- **Checkboxes**: Only checked images will be processed

#### Format Conversion

- **WebP**: Modern format with excellent compression, supported by all major browsers
- **AVIF**: Next-generation format with superior compression, growing browser support
- **Keep Original**: Maintains original format (JPG/PNG) while compressing

#### Compression Quality

- **100%**: Maximum quality, minimal compression
- **85%** (Recommended): Excellent quality with good file size reduction
- **70%**: Good quality for web use
- **50%**: Acceptable quality, significant size reduction
- **<50%**: Noticeable quality loss, maximum compression

#### Metadata (EXIF) Removal

EXIF data includes:

- Camera make and model
- Photo settings (ISO, aperture, shutter speed)
- Date and time taken
- GPS location (if available)
- Copyright information

Enable "Remove metadata" to:

- Reduce file size slightly
- Protect privacy (removes GPS data)
- Remove identifying camera information

### Tips & Best Practices

1. **Format Choice**:
   - Use **WebP** for web publishing (wide compatibility)
   - Use **AVIF** for maximum compression (newest browsers)
   - Use **Keep Original** when format compatibility is critical
2. **Quality Settings**:
   - Photos for web: 80-85%
   - Professional use: 90-95%
   - Archive/storage: 70-80%

### Troubleshooting

**AVIF option not showing?**

- Install the AVIF plugin: `pip install pillow-avif-plugin`
- Restart the application

**Images not processing?**

- Check that images are checked in the list
- Verify output folder path is valid
- Ensure sufficient disk space

**Slow processing?**

- Normal for large images or many files
- UI remains responsive - you can minimize the window
- Processing happens in background thread

**Error messages?**

- Check file permissions
- Ensure images aren't corrupted
- Verify format is supported (JPG, JPEG, PNG)

## Building Executable (.exe)

### Windows

```cmd
build.bat
```

### Linux/Mac

```bash
chmod +x build.sh
./build.sh
```

The executable will be created in the `dist/` folder.

## Project Structure

```
imajin/
├── src/
│   ├── main.py              # Application entry point
│   ├── ui/
│   │   └── main_window.py   # Main UI window
│   ├── core/
│   │   ├── compressor.py    # Image compression logic
│   │   ├── converter.py     # Format conversion logic
│   │   └── worker.py        # Background processing thread
│   └── utils/
│       └── metadata.py      # EXIF metadata handling
├── requirements.txt         # Python dependencies
├── install.sh              # Linux/Mac installation script
├── install.bat             # Windows installation script
├── build.sh                # Linux/Mac build script
├── build.bat               # Windows build script
├── DEVELOPMENT_PLAN.md     # Development roadmap
├── CHECKLIST.md            # Sprint checklist
└── README.md               # This file
```

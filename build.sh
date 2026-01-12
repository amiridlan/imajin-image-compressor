#!/bin/bash

echo "Building Imajin executable with PyInstaller..."
echo ""

# Check if PyInstaller is installed
python3 -c "import PyInstaller" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "PyInstaller not found. Installing..."
    pip3 install pyinstaller
fi

# Build the executable
echo ""
echo "Building executable..."
pyinstaller --onefile --windowed --name Imajin --clean \
    --paths=src \
    --hidden-import=PIL._tkinter_finder \
    --hidden-import=pillow_avif \
    --collect-all pillow_avif \
    src/main.py

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "Build complete!"
    echo "Executable location: dist/Imajin"
    echo "========================================"
else
    echo ""
    echo "Build failed. Please check the error messages above."
    exit 1
fi

@echo off
echo Building Imajin executable with PyInstaller...
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Build the executable
echo.
echo Building executable...
pyinstaller --onefile --windowed --name Imajin --clean ^
    --paths=src ^
    --hidden-import=PIL._tkinter_finder ^
    --hidden-import=pillow_avif ^
    --collect-all pillow_avif ^
    src/main.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Build complete!
    echo Executable location: dist\Imajin.exe
    echo ========================================
) else (
    echo.
    echo Build failed. Please check the error messages above.
    exit /b 1
)

pause

@echo off
echo Installing Imajin dependencies...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo Installation completed successfully!
    echo To run the application, use: python src/main.py
) else (
    echo Installation failed. Please check the error messages above.
    exit /b 1
)

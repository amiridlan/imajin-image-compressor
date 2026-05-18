@echo off
echo ============================================================
echo  Imajin — Build Script
echo ============================================================
echo.

REM ── 1. Dependencies ─────────────────────────────────────────
echo [1/3] Installing dependencies...
pip install -r requirements.txt pyinstaller
if %errorlevel% neq 0 (
    echo ERROR: pip install failed.
    pause & exit /b 1
)

REM ── 2. PyInstaller ──────────────────────────────────────────
echo.
echo [2/3] Building exe with PyInstaller...
pyinstaller Imajin.spec --clean
if %errorlevel% neq 0 (
    echo ERROR: PyInstaller build failed.
    pause & exit /b 1
)

REM ── 3. Inno Setup installer ─────────────────────────────────
echo.
echo [3/3] Compiling installer with Inno Setup...
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (
    echo WARNING: Inno Setup not found at %ISCC%.
    echo          Install from https://jrsoftware.org/isinfo.php or skip this step.
    echo          Exe is still available at dist\Imajin.exe
    goto done
)
%ISCC% Imajin.iss
if %errorlevel% neq 0 (
    echo ERROR: Inno Setup compilation failed.
    pause & exit /b 1
)

:done
echo.
echo ============================================================
echo  Build complete!
echo    Exe:       dist\Imajin.exe
echo    Installer: installer\ImajinSetup.exe  (if Inno Setup ran)
echo ============================================================
pause

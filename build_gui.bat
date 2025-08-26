@echo off
echo ========================================
echo GUI Screenshot Monitor Build Script
echo ========================================
echo.

REM Activate Python virtual environment if exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Install required packages
echo.
echo Installing required packages...
call pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Error: Package installation failed
    pause
    exit /b 1
)

REM Clean existing build files
echo.
echo Cleaning up existing build files...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.spec del *.spec

REM Build with PyInstaller
echo.
echo Building executable file...

REM Check for encrypted credentials
if exist credentials.enc (
    echo Building with encrypted credentials...
    call venv\Scripts\pyinstaller.exe --onefile --windowed ^
        --name "ScreenshotMonitor" ^
        --add-data "credentials.enc;." ^
        --hidden-import "credential_manager" ^
        auto_screenshot_gui.py
) else (
    REM Check for service account file
    if exist service-account-key.json (
        echo Building with service account key...
        call venv\Scripts\pyinstaller.exe --onefile --windowed ^
            --name "ScreenshotMonitor" ^
            --add-data "service-account-key.json;." ^
            auto_screenshot_gui.py
    ) else (
        echo.
        echo Warning: Authentication file not found
        echo Either service-account-key.json or credentials.enc is required
        pause
        exit /b 1
    )
)

if errorlevel 1 (
    echo.
    echo Error: Build failed
    pause
    exit /b 1
)

REM Build success
echo.
echo ========================================
echo Build Complete!
echo.
echo Generated files:
echo - dist\ScreenshotMonitor.exe
echo.
echo Usage:
echo 1. Run ScreenshotMonitor.exe
echo 2. Enter password (same as encryption password)
echo 3. Control recording in main window
echo.
echo Distribution notes:
echo - Distribute ScreenshotMonitor.exe only
echo - Do not distribute service-account-key.json
echo - Share password through secure channel
echo ========================================
echo.
pause
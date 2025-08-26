@echo off
echo ========================================
echo Secure Auto Screenshot Tool Build Script
echo (For distribution with encrypted credentials)
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
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Error: Package installation failed
    pause
    exit /b 1
)

REM Check for encrypted credentials
if not exist credentials.enc (
    echo.
    echo ========================================
    echo Warning: credentials.enc not found
    echo.
    echo Please run the following steps:
    echo 1. Run encrypt_credentials.bat
    echo 2. Select password encryption (for employee distribution)
    echo 3. Set distribution password
    echo ========================================
    echo.
    pause
    exit /b 1
)

REM Clean existing build files
echo.
echo Cleaning up existing build files...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.spec del *.spec

REM Build with PyInstaller (include encrypted file)
echo.
echo Building executable with encrypted credentials...
pyinstaller --onefile --windowed ^
    --name "AutoScreenshotTool" ^
    --add-data "credentials.enc;." ^
    --hidden-import "credential_manager" ^
    --icon=NONE ^
    auto_screenshot_gdrive.py

if errorlevel 1 (
    echo.
    echo Error: Build failed
    pause
    exit /b 1
)

REM Create distribution batch file
echo.
echo Creating distribution launch script...
echo @echo off > dist\run_with_password.bat
echo echo Starting Auto Screenshot Tool >> dist\run_with_password.bat
echo set /p SCREENSHOT_PASSWORD=Enter password:  >> dist\run_with_password.bat
echo AutoScreenshotTool.exe >> dist\run_with_password.bat

REM Build success
echo.
echo ========================================
echo Build Complete!
echo.
echo Generated files:
echo - dist\AutoScreenshotTool.exe (executable)
echo - dist\run_with_password.bat (password input launch script)
echo.
echo Distribution to employees:
echo ========================================
echo.
echo [Option 1: Password input on launch]
echo 1. Distribute these files:
echo    - AutoScreenshotTool.exe
echo    - run_with_password.bat
echo.
echo 2. Employees run run_with_password.bat
echo 3. Enter password to launch
echo.
echo [Option 2: Environment variable]
echo 1. Distribute AutoScreenshotTool.exe only
echo 2. Set SCREENSHOT_PASSWORD environment variable on each PC
echo 3. Run AutoScreenshotTool.exe directly
echo.
echo [IMPORTANT]
echo - DO NOT distribute service-account-key.json
echo - credentials.enc is included in the executable
echo - Notify password through secure method
echo ========================================
echo.
pause
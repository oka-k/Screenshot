@echo off
echo ========================================
echo GUI Screenshot Monitor - Employee Distribution Preparation
echo ========================================
echo.
echo This script will:
echo 1. Encrypt Google service account credentials
echo 2. Build executable with encrypted data
echo 3. Create distribution files
echo.

REM Check for service account file
if not exist service-account-key.json (
    echo.
    echo Error: service-account-key.json not found
    echo Please place the service account key file in current directory
    pause
    exit /b 1
)

REM Activate Python virtual environment if exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Install required packages
echo.
echo Installing required packages...
call pip install -r requirements.txt
call pip install cryptography
if errorlevel 1 (
    echo.
    echo Error: Package installation failed
    pause
    exit /b 1
)

REM Encrypt credentials
echo.
echo ========================================
echo STEP 1: Encrypt Credentials
echo ========================================
echo.
echo You need to set a password to protect the credentials.
echo Employees will use this password to run the tool.
echo.

call python -c "from credential_manager import CredentialManager; import getpass; cm = CredentialManager(); p1 = getpass.getpass('Enter password: '); p2 = getpass.getpass('Confirm password: '); exit(1) if p1 != p2 else cm.encrypt_credentials('service-account-key.json', p1) or print('\nCredentials encrypted successfully!')"

if errorlevel 1 (
    echo.
    echo Error: Password mismatch or encryption failed
    pause
    exit /b 1
)

REM Clean existing build files
echo.
echo ========================================
echo STEP 2: Building Application
echo ========================================
echo.
echo Cleaning up existing build files...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.spec del *.spec

REM Build with PyInstaller (include encrypted file)
echo.
echo Building executable with encrypted credentials...
call venv\Scripts\pyinstaller.exe --onefile --windowed ^
    --name "ScreenshotMonitor" ^
    --add-data "credentials.enc;." ^
    --hidden-import "credential_manager" ^
    --icon=NONE ^
    auto_screenshot_gui.py

if errorlevel 1 (
    echo.
    echo Error: Build failed
    pause
    exit /b 1
)

REM Create distribution batch file
echo.
echo Creating distribution launch script...
echo @echo off > dist\run_monitor.bat
echo echo Starting Screenshot Monitor >> dist\run_monitor.bat
echo set /p SCREENSHOT_PASSWORD=Enter password:  >> dist\run_monitor.bat
echo ScreenshotMonitor.exe >> dist\run_monitor.bat

REM Build success
echo.
echo ========================================
echo Build Complete!
echo.
echo Generated files in dist\ folder:
echo - ScreenshotMonitor.exe (main executable)
echo - run_monitor.bat (password input helper)
echo.
echo ========================================
echo DISTRIBUTION INSTRUCTIONS
echo ========================================
echo.
echo For each employee:
echo.
echo 1. Copy these files to employee PC:
echo    - ScreenshotMonitor.exe
echo    - run_monitor.bat (optional)
echo.
echo 2. Share the password securely (in person/phone)
echo.
echo 3. Employee runs the tool:
echo    Option A: Double-click run_monitor.bat
echo    Option B: Run ScreenshotMonitor.exe directly
echo.
echo 4. First login:
echo    - Enter the password you set during encryption
echo    - Main window appears
echo    - Click "Start" to begin monitoring
echo.
echo IMPORTANT SECURITY NOTES:
echo - NEVER share service-account-key.json
echo - credentials.enc is embedded in the exe
echo - Password protects both GUI and Google credentials
echo ========================================
echo.
pause
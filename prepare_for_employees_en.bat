@echo off
echo ========================================
echo Employee Distribution File Preparation Tool
echo ========================================
echo.
echo This tool should be run by administrators.
echo Prepares encrypted credentials for employee distribution.
echo.

REM Check service-account-key.json
if not exist service-account-key.json (
    echo Error: service-account-key.json not found
    echo Please place the Google service account key file
    pause
    exit /b 1
)

REM Check existing encrypted file
if exist credentials.enc (
    echo.
    echo Existing encrypted file credentials.enc found.
    set /p OVERWRITE="Overwrite? (y/n): "
    if /i not "%OVERWRITE%"=="y" (
        echo Process cancelled
        pause
        exit /b 0
    )
)

echo.
echo ========================================
echo Step 1: Encrypt Credentials
echo ========================================
echo.
echo Set a common password for all employees.
echo You will need to notify employees of this password separately.
echo.

REM Execute encryption with Python script
python -c "from credential_manager import CredentialManager; import getpass; cm = CredentialManager(); cm.encrypt_credentials('service-account-key.json', use_machine_binding=False)"

if errorlevel 1 (
    echo.
    echo Error: Encryption failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Step 2: Execute Build
echo ========================================
echo.
echo Encryption complete. Now executing build.
echo.
pause

call build_secure_en.bat

echo.
echo ========================================
echo Distribution Preparation Complete
echo ========================================
echo.
echo Files to distribute to employees:
echo   1. dist\AutoScreenshotTool.exe
echo   2. dist\run_with_password.bat (optional)
echo.
echo Instructions for employees:
echo   - Run run_with_password.bat
echo   - Enter the notified password
echo   - Or set SCREENSHOT_PASSWORD environment variable
echo.
echo [SECURITY NOTES]
echo   - NEVER distribute service-account-key.json
echo   - Notify password through secure method
echo   - Recommend deleting service-account-key.json after distribution
echo ========================================
echo.
pause
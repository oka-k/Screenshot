@echo off
echo ========================================
echo 自動スクリーンショットツール ビルドスクリプト
echo (Googleドライブ連携版)
echo ========================================
echo.

REM Python仮想環境がある場合はアクティベート
if exist venv\Scripts\activate.bat (
    echo 仮想環境をアクティベートしています...
    call venv\Scripts\activate.bat
)

REM 必要なパッケージのインストール
echo.
echo 必要なパッケージをインストールしています...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo エラー: パッケージのインストールに失敗しました
    pause
    exit /b 1
)

REM サービスアカウントキーファイルの確認
if not exist service-account-key.json (
    echo.
    echo ========================================
    echo 警告: service-account-key.json が見つかりません
    echo.
    echo Googleドライブ連携を使用するには、以下の手順でファイルを配置してください:
    echo 1. Google Cloud ConsoleでサービスアカウントのJSONキーを取得
    echo 2. このフォルダに service-account-key.json として保存
    echo ========================================
    echo.
    echo 続行しますか？ (Y/N)
    set /p CONTINUE=
    if /i not "%CONTINUE%"=="Y" (
        echo ビルドを中止しました
        pause
        exit /b 0
    )
)

REM 既存のビルドファイルを削除
echo.
echo 既存のビルドファイルをクリーンアップしています...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.spec del *.spec

REM PyInstallerでビルド
echo.
echo 実行ファイルをビルドしています...
if exist service-account-key.json (
    echo サービスアカウントキーファイルを含めてビルドします...
    pyinstaller --onefile --windowed --name "AutoScreenshotTool" --add-data "service-account-key.json;." --icon=NONE auto_screenshot_gdrive.py
) else (
    echo サービスアカウントキーファイルなしでビルドします...
    pyinstaller --onefile --windowed --name "AutoScreenshotTool" --icon=NONE auto_screenshot_gdrive.py
)

if errorlevel 1 (
    echo.
    echo エラー: ビルドに失敗しました
    pause
    exit /b 1
)

REM ビルド成功
echo.
echo ========================================
echo ビルド完了！
echo.
echo 実行ファイル: dist\AutoScreenshotTool.exe
echo.
echo 使用方法:
echo 1. auto_screenshot_gdrive.py の設定を編集:
echo    - INTERVAL_MINUTES: スクリーンショット撮影間隔（分）
echo    - GDRIVE_FOLDER_ID: アップロード先のGoogleドライブフォルダID
echo.
echo 2. service-account-key.json を同じフォルダに配置
echo.
echo 3. 再度 build.bat を実行してビルド
echo.
echo 4. dist\AutoScreenshotTool.exe を配布・実行
echo ========================================
echo.
pause
@echo off
echo ========================================
echo セキュア版 自動スクリーンショットツール ビルドスクリプト
echo (暗号化認証情報を含む配布用)
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

REM 暗号化された認証情報の確認
if not exist credentials.enc (
    echo.
    echo ========================================
    echo 警告: credentials.enc が見つかりません
    echo.
    echo 先に以下の手順を実行してください:
    echo 1. encrypt_credentials.bat を実行
    echo 2. パスワード暗号化を選択（従業員配布用）
    echo 3. 配布用パスワードを設定
    echo ========================================
    echo.
    pause
    exit /b 1
)

REM 既存のビルドファイルを削除
echo.
echo 既存のビルドファイルをクリーンアップしています...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.spec del *.spec

REM PyInstallerでビルド（暗号化ファイルを含める）
echo.
echo 実行ファイルをビルドしています（暗号化認証情報を含む）...
pyinstaller --onefile --windowed ^
    --name "AutoScreenshotTool" ^
    --add-data "credentials.enc;." ^
    --hidden-import "credential_manager" ^
    --icon=NONE ^
    auto_screenshot_gdrive.py

if errorlevel 1 (
    echo.
    echo エラー: ビルドに失敗しました
    pause
    exit /b 1
)

REM 配布用バッチファイルを作成
echo.
echo 配布用起動スクリプトを作成しています...
echo @echo off > dist\run_with_password.bat
echo echo 自動スクリーンショットツールを起動します >> dist\run_with_password.bat
echo set /p SCREENSHOT_PASSWORD=パスワードを入力してください:  >> dist\run_with_password.bat
echo AutoScreenshotTool.exe >> dist\run_with_password.bat

REM ビルド成功
echo.
echo ========================================
echo ビルド完了！
echo.
echo 生成されたファイル:
echo - dist\AutoScreenshotTool.exe （実行ファイル）
echo - dist\run_with_password.bat （パスワード入力用起動スクリプト）
echo.
echo 従業員への配布方法:
echo ========================================
echo.
echo 【オプション1: 起動時パスワード入力】
echo 1. 以下のファイルを配布:
echo    - AutoScreenshotTool.exe
echo    - run_with_password.bat
echo.
echo 2. 従業員は run_with_password.bat を実行
echo 3. パスワードを入力して起動
echo.
echo 【オプション2: 環境変数設定】
echo 1. AutoScreenshotTool.exe のみ配布
echo 2. 各PCで環境変数 SCREENSHOT_PASSWORD を設定
echo 3. AutoScreenshotTool.exe を直接実行
echo.
echo 【重要】
echo - service-account-key.json は配布しません
echo - credentials.enc は実行ファイルに含まれています
echo - パスワードは安全な方法で従業員に通知してください
echo ========================================
echo.
pause
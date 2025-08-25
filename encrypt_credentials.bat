@echo off
echo ========================================
echo 認証情報暗号化ツール
echo ========================================
echo.

REM Pythonがインストールされているか確認
python --version >nul 2>&1
if errorlevel 1 (
    echo エラー: Pythonがインストールされていません
    pause
    exit /b 1
)

REM cryptographyパッケージがインストールされているか確認
echo 必要なパッケージを確認しています...
pip show cryptography >nul 2>&1
if errorlevel 1 (
    echo cryptographyパッケージをインストールしています...
    pip install cryptography
)

REM service-account-key.jsonが存在するか確認
if not exist service-account-key.json (
    echo.
    echo エラー: service-account-key.json が見つかりません
    echo このファイルをこのフォルダに配置してから実行してください
    pause
    exit /b 1
)

echo.
echo ========================================
echo 認証情報を暗号化します
echo.
echo 暗号化方式を選択してください:
echo 1. マシン紐付け暗号化（推奨）
echo    - このPCでのみ自動的に復号化可能
echo    - パスワード入力不要
echo.
echo 2. パスワード暗号化
echo    - パスワードがあればどのPCでも復号化可能
echo    - 実行時にパスワード入力が必要
echo ========================================
echo.

set /p CHOICE=選択 (1 または 2): 

if "%CHOICE%"=="1" (
    echo.
    echo マシン紐付け暗号化を実行します...
    python credential_manager.py encrypt service-account-key.json
) else if "%CHOICE%"=="2" (
    echo.
    echo パスワード暗号化を実行します...
    echo 注意: パスワードは画面に表示されません
    python -c "from credential_manager import CredentialManager; cm = CredentialManager(); cm.encrypt_credentials('service-account-key.json', use_machine_binding=False)"
) else (
    echo.
    echo 無効な選択です
    pause
    exit /b 1
)

if errorlevel 1 (
    echo.
    echo エラー: 暗号化に失敗しました
    pause
    exit /b 1
)

echo.
echo ========================================
echo 暗号化が完了しました！
echo.
echo 生成されたファイル:
echo - credentials.enc (暗号化された認証情報)
echo.
echo 注意事項:
echo - credentials.enc を安全に保管してください
echo - service-account-key.json は削除することを推奨します
echo - .gitignore に含まれているため、誤ってコミットされることはありません
echo ========================================
echo.
pause
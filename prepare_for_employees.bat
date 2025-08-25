@echo off
echo ========================================
echo 従業員配布用ファイル準備ツール
echo ========================================
echo.
echo このツールは管理者が実行してください。
echo 従業員に配布する暗号化済み認証情報を準備します。
echo.

REM service-account-key.jsonの確認
if not exist service-account-key.json (
    echo エラー: service-account-key.json が見つかりません
    echo Googleサービスアカウントのキーファイルを配置してください
    pause
    exit /b 1
)

REM 既存の暗号化ファイルがある場合は確認
if exist credentials.enc (
    echo.
    echo 既存の暗号化ファイル (credentials.enc) が見つかりました。
    set /p OVERWRITE=上書きしますか？ (y/n): 
    if /i not "%OVERWRITE%"=="y" (
        echo 処理を中止しました
        pause
        exit /b 0
    )
)

echo.
echo ========================================
echo ステップ1: 認証情報の暗号化
echo ========================================
echo.
echo 従業員全員が使用する共通パスワードを設定します。
echo このパスワードは従業員に別途通知する必要があります。
echo.

REM Pythonスクリプトで暗号化を実行
python -c "from credential_manager import CredentialManager; import getpass; cm = CredentialManager(); cm.encrypt_credentials('service-account-key.json', use_machine_binding=False)"

if errorlevel 1 (
    echo.
    echo エラー: 暗号化に失敗しました
    pause
    exit /b 1
)

echo.
echo ========================================
echo ステップ2: ビルド実行
echo ========================================
echo.
echo 暗号化が完了しました。次にビルドを実行します。
echo.
pause

call build_secure.bat

echo.
echo ========================================
echo 配布準備完了
echo ========================================
echo.
echo 従業員に配布するファイル:
echo   1. dist\AutoScreenshotTool.exe
echo   2. dist\run_with_password.bat (オプション)
echo.
echo 従業員への指示:
echo   - run_with_password.bat を実行
echo   - 通知されたパスワードを入力
echo   - または環境変数 SCREENSHOT_PASSWORD を設定
echo.
echo 【セキュリティ注意事項】
echo   - service-account-key.json は絶対に配布しない
echo   - パスワードは安全な方法で通知する
echo   - 配布後は service-account-key.json を削除推奨
echo ========================================
echo.
pause
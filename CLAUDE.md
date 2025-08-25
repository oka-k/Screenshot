# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

自動スクリーンショットアップローダーツールの開発プロジェクトです。Windowsバックグラウンドで動作し、定期的にスクリーンショットを撮影してクラウドサービス（SlackまたはGoogleドライブ）にアップロードします。

## 開発環境

- **言語**: Python 3.9以上（`zoneinfo`標準ライブラリを使用）
- **配布形式**: PyInstallerで単一の.exeファイルとして配布

## 必要なライブラリ

```bash
pip install Pillow schedule pyautogui
# Slack連携の場合
pip install requests
# Googleドライブ連携の場合
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## ビルドコマンド

### 基本ビルド（Slack連携）
```bash
pyinstaller --onefile --windowed --name "AutoScreenshotTool.exe" your_script_name.py
```

### Googleドライブ連携の場合
```bash
pyinstaller --onefile --windowed --name "AutoScreenshotTool.exe" --add-data "your-key-file.json;." your_script_name.py
```

## アーキテクチャ

### ファイル命名規則
- 基本形式: `YYYYMMDD-ユーザー名.png`（JST時刻）
- 重複時: `YYYYMMDD-ユーザー名_HHMMSS.png`

### 主要機能
1. **定期実行**: `schedule`ライブラリでN分間隔のスクリーンショット撮影
2. **スクリーンショット**: `pyautogui.screenshot()`でプライマリスクリーンを撮影
3. **外部連携**:
   - Slack: `files.upload` APIを使用（Bot Tokenで認証）
   - Googleドライブ: Drive API v3（サービスアカウント認証）

### 設定定数の管理
スクリプト内で以下の定数を定義（コンパイル前に設定）:
- `INTERVAL_MINUTES`: 撮影間隔
- `SLACK_BOT_TOKEN`, `SLACK_CHANNEL_ID`: Slack連携用
- `SERVICE_ACCOUNT_FILE`, `GDRIVE_FOLDER_ID`: Googleドライブ連携用

## 重要な実装ポイント
- バックグラウンド実行（`--windowed`オプション必須）
- JST時刻の使用（`ZoneInfo("Asia/Tokyo")`）
- 一時ファイルの適切な削除処理
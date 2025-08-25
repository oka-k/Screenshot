#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動スクリーンショットアップローダー (Googleドライブ連携版)
定期的にスクリーンショットを撮影し、Googleドライブにアップロードします。
"""

import os
import sys
import time
import traceback
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import tempfile

import schedule
import pyautogui
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# ===== 設定定数 =====
# 撮影間隔（分）
INTERVAL_MINUTES = 5

# Googleドライブ連携用設定
SERVICE_ACCOUNT_FILE = 'service-account-key.json'  # サービスアカウントのJSONキーファイル名
GDRIVE_FOLDER_ID = '1aQz0NVrKuKre-I3GkF8Mnua2snZyaH66'  # アップロード先のGoogleドライブフォルダID

# Google Drive APIのスコープ
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# ログファイルのパス（デバッグ用）
LOG_FILE = 'auto_screenshot.log'


def log_message(message):
    """ログメッセージを記録する"""
    timestamp = datetime.now(ZoneInfo("Asia/Tokyo")).strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception:
        pass  # ログ書き込みエラーは無視


def get_drive_service():
    """Google Drive APIのサービスオブジェクトを取得"""
    try:
        # サービスアカウントファイルのパスを取得
        if getattr(sys, 'frozen', False):
            # PyInstallerでビルドされた実行ファイルの場合
            base_path = sys._MEIPASS
        else:
            # 通常のPythonスクリプトの場合
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        key_file_path = os.path.join(base_path, SERVICE_ACCOUNT_FILE)
        
        if not os.path.exists(key_file_path):
            log_message(f"エラー: サービスアカウントファイルが見つかりません: {key_file_path}")
            return None
        
        # 認証情報を作成
        credentials = service_account.Credentials.from_service_account_file(
            key_file_path,
            scopes=SCOPES
        )
        
        # Drive APIサービスを構築
        service = build('drive', 'v3', credentials=credentials)
        log_message("Google Drive APIサービスの初期化に成功しました")
        return service
        
    except Exception as e:
        log_message(f"Google Drive APIサービスの初期化エラー: {str(e)}")
        return None


def upload_to_gdrive(local_file_path, file_name, service):
    """Googleドライブにファイルをアップロード"""
    try:
        file_metadata = {
            'name': file_name,
            'parents': [GDRIVE_FOLDER_ID]
        }
        
        media = MediaFileUpload(
            local_file_path,
            mimetype='image/png',
            resumable=True
        )
        
        # ファイルをアップロード
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name'
        ).execute()
        
        log_message(f"アップロード成功: {file_name} (ID: {file.get('id')})")
        return True
        
    except HttpError as e:
        if e.resp.status == 404:
            log_message(f"エラー: 指定されたフォルダIDが見つかりません: {GDRIVE_FOLDER_ID}")
        else:
            log_message(f"Googleドライブアップロードエラー (HTTP {e.resp.status}): {str(e)}")
        return False
    except Exception as e:
        log_message(f"Googleドライブアップロードエラー: {str(e)}")
        return False


def take_and_upload_screenshot():
    """スクリーンショットを撮影してGoogleドライブにアップロード"""
    service = None
    temp_file_path = None
    
    try:
        # Google Drive APIサービスを取得
        service = get_drive_service()
        if not service:
            log_message("Google Drive APIサービスの取得に失敗しました")
            return
        
        # ファイル名の生成
        username = os.getlogin()
        jst_now = datetime.now(ZoneInfo("Asia/Tokyo"))
        date_str = jst_now.strftime('%Y%m%d')
        base_name = f"{date_str}-{username}"
        
        # 重複チェック用のタイムスタンプ付きファイル名
        # Googleドライブでは同名ファイルも保存可能だが、識別しやすくするため時刻を付与
        timestamp_suffix = jst_now.strftime('%H%M%S')
        file_name = f"{base_name}_{timestamp_suffix}.png"
        
        # 一時ディレクトリにファイルを保存
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, file_name)
        
        # スクリーンショット撮影
        log_message(f"スクリーンショット撮影開始: {file_name}")
        screenshot = pyautogui.screenshot()
        screenshot.save(temp_file_path)
        log_message(f"スクリーンショット保存完了: {temp_file_path}")
        
        # Googleドライブにアップロード
        if upload_to_gdrive(temp_file_path, file_name, service):
            log_message(f"処理完了: {file_name}")
        else:
            log_message(f"アップロード失敗: {file_name}")
        
    except Exception as e:
        log_message(f"エラー発生: {str(e)}")
        log_message(f"トレースバック: {traceback.format_exc()}")
    
    finally:
        # 一時ファイルを削除
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                log_message(f"一時ファイル削除: {temp_file_path}")
            except Exception as e:
                log_message(f"一時ファイル削除エラー: {str(e)}")


def main():
    """メイン処理"""
    log_message("=" * 50)
    log_message("自動スクリーンショットアップローダー起動")
    log_message(f"撮影間隔: {INTERVAL_MINUTES}分")
    log_message(f"Googleドライブフォルダ ID: {GDRIVE_FOLDER_ID}")
    
    # 設定の検証
    if GDRIVE_FOLDER_ID == 'YOUR_FOLDER_ID_HERE':
        log_message("エラー: GoogleドライブフォルダIDが設定されていません")
        log_message("GDRIVE_FOLDER_IDを正しい値に設定してください")
        sys.exit(1)
    
    # 初回実行
    log_message("初回スクリーンショット撮影を開始します...")
    take_and_upload_screenshot()
    
    # スケジュール設定
    schedule.every(INTERVAL_MINUTES).minutes.do(take_and_upload_screenshot)
    log_message(f"スケジューラー設定完了: {INTERVAL_MINUTES}分ごとに実行")
    
    # メインループ
    log_message("メインループ開始")
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            log_message("キーボード割り込みを検出。プログラムを終了します。")
            break
        except Exception as e:
            log_message(f"メインループエラー: {str(e)}")
            time.sleep(60)  # エラー時は60秒待機


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log_message(f"プログラム終了エラー: {str(e)}")
        log_message(f"トレースバック: {traceback.format_exc()}")
        sys.exit(1)
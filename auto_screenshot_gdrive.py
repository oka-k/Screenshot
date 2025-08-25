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
GDRIVE_FOLDER_ID = '1j8QhcrXodnMm6C7y9yJVnwqbHEREu-iO'  # アップロード先のGoogleドライブフォルダID

# Google Drive APIのスコープ
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# ログファイルのパス（デバッグ用）
LOG_FILE = 'auto_screenshot.log'


# ログローテーション設定
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
MAX_LOG_FILES = 5  # 最大5世代保持


def rotate_log_if_needed():
    """ログファイルのサイズをチェックし、必要に応じてローテーション"""
    try:
        if not os.path.exists(LOG_FILE):
            return
        
        # ファイルサイズをチェック
        file_size = os.path.getsize(LOG_FILE)
        if file_size < MAX_LOG_SIZE:
            return
        
        # ローテーション実行
        # 古いログファイルを削除
        oldest_log = f"{LOG_FILE}.{MAX_LOG_FILES}"
        if os.path.exists(oldest_log):
            os.remove(oldest_log)
        
        # 既存のログファイルを順番にリネーム
        for i in range(MAX_LOG_FILES - 1, 0, -1):
            old_name = f"{LOG_FILE}.{i}"
            new_name = f"{LOG_FILE}.{i + 1}"
            if os.path.exists(old_name):
                os.rename(old_name, new_name)
        
        # 現在のログファイルをローテーション
        os.rename(LOG_FILE, f"{LOG_FILE}.1")
        
        # 新しいログファイルを作成
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            jst_now = datetime.now(ZoneInfo("Asia/Tokyo"))
            f.write(f"[{jst_now.strftime('%Y-%m-%d %H:%M:%S')}] ログファイルをローテーションしました\n")
            f.write(f"[{jst_now.strftime('%Y-%m-%d %H:%M:%S')}] 前のログは {LOG_FILE}.1 に保存されています\n")
            
    except Exception as e:
        # ローテーションエラーは無視（ログ記録自体は続行）
        pass

def log_message(message):
    """ログメッセージを記録する（ローテーション機能付き）"""
    timestamp = datetime.now(ZoneInfo("Asia/Tokyo")).strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    
    try:
        # ログファイルのローテーションチェック
        rotate_log_if_needed()
        
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception:
        pass  # ログ書き込みエラーは無視  # ログ書き込みエラーは無視


def get_drive_service():
    """Google Drive APIのサービスオブジェクトを取得"""
    try:
        # 暗号化された認証情報を使用
        from credential_manager import CredentialManager
        
        # 暗号化マネージャーを初期化
        cred_manager = CredentialManager()
        
        try:
            # 環境変数からパスワードを取得（従業員配布用）
            import os
            password = os.environ.get('SCREENSHOT_PASSWORD')
            
            if not password and cred_manager.encrypted_file_path.exists():
                # パスワードが環境変数にない場合、プロンプトで入力
                import getpass
                password = getpass.getpass("認証パスワードを入力してください: ")
            
            # 暗号化された認証情報を復号化
            if password:
                credentials_dict = cred_manager.get_credentials_for_gdrive(password=password)
            else:
                # パスワードがない場合はマシン紐付けまたは通常の認証
                credentials_dict = cred_manager.get_credentials_for_gdrive()
            
            # 認証情報を作成
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict,
                scopes=SCOPES
            )
            
            # Drive APIサービスを構築
            service = build('drive', 'v3', credentials=credentials)
            log_message("Google Drive APIサービスの初期化に成功しました")
            return service
            
        except FileNotFoundError:
            # 暗号化ファイルが見つからない場合、従来の方法を試す
            log_message("暗号化された認証情報が見つかりません。通常のJSONファイルを探します...")
            
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
            log_message("Google Drive APIサービスの初期化に成功しました（通常認証使用）")
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
        
        # スクリーンショット撮影（全画面を1枚に）
        log_message(f"スクリーンショット撮影開始: {file_name}")
        
        try:
            # mssを使用して全モニターを含む仮想画面を撮影
            import mss
            from PIL import Image
            
            with mss.mss() as sct:
                # monitors[0]は全モニターを含む仮想画面
                monitor = sct.monitors[0]
                screenshot = sct.grab(monitor)
                # PIL Imageに変換
                img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
                img.save(temp_file_path)
                log_message(f"全画面スクリーンショット保存完了: {temp_file_path}")
                
        except (ImportError, Exception) as e:
            # mssが使用できない場合は通常の方法（プライマリモニターのみ）
            log_message("全画面撮影に失敗。プライマリモニターのみ撮影します。")
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
    # 起動時に古いログファイルをクリーンアップ
    cleanup_old_logs()
    
    log_message("=" * 50)
    log_message("自動スクリーンショットアップローダー起動")
    log_message(f"撮影間隔: {INTERVAL_MINUTES}分")
    log_message(f"Googleドライブフォルダ ID: {GDRIVE_FOLDER_ID}")
    log_message(f"ログローテーション: {MAX_LOG_SIZE / 1024 / 1024:.1f}MB, 最大{MAX_LOG_FILES}世代保持")
    
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

def cleanup_old_logs():
    """起動時に古いログファイルをクリーンアップ"""
    try:
        log_dir = os.path.dirname(os.path.abspath(LOG_FILE))
        log_base = os.path.basename(LOG_FILE)
        
        # ログファイルのリストを取得
        log_files = []
        for file in os.listdir(log_dir):
            if file.startswith(log_base) and file != log_base:
                # auto_screenshot.log.1, auto_screenshot.log.2 など
                try:
                    parts = file.split('.')
                    if len(parts) == 3 and parts[-1].isdigit():
                        log_files.append((file, int(parts[-1])))
                except:
                    pass
        
        # 番号順にソート
        log_files.sort(key=lambda x: x[1])
        
        # MAX_LOG_FILESを超える古いファイルを削除
        for file, num in log_files:
            if num > MAX_LOG_FILES:
                try:
                    os.remove(os.path.join(log_dir, file))
                    print(f"古いログファイルを削除: {file}")
                except:
                    pass
                    
    except Exception:
        pass


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log_message(f"プログラム終了エラー: {str(e)}")
        log_message(f"トレースバック: {traceback.format_exc()}")
        sys.exit(1)
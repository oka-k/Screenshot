#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動スクリーンショットツール GUI版
パスワード認証と撮影制御機能を提供
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import os
import sys
import json
import tempfile
import traceback
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

# 既存のスクリーンショット機能をインポート
import pyautogui
from PIL import Image
import schedule

# Google Drive関連
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# mss対応（マルチモニター）
try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False

# 暗号化された認証情報の復号化対応
try:
    from credential_manager import CredentialManager
    CREDENTIAL_MANAGER_AVAILABLE = True
except ImportError:
    CREDENTIAL_MANAGER_AVAILABLE = False

# ========== 設定（ハードコード） ==========
INTERVAL_MINUTES = 5
SERVICE_ACCOUNT_FILE = 'service-account-key.json'
GDRIVE_FOLDER_ID = '1j8QhcrXodnMm6C7y9yJVnwqbHEREu-iO'
SCOPES = ['https://www.googleapis.com/auth/drive.file']
LOG_FILE = 'auto_screenshot.log'
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
MAX_LOG_FILES = 5

# パスワードはcredential_managerで暗号化時に設定されたものを使用
# GUIログイン時のパスワードと認証情報復号化のパスワードは同じ

# ========== ログ機能 ==========
def rotate_log_if_needed():
    """ログファイルのローテーション"""
    if os.path.exists(LOG_FILE):
        if os.path.getsize(LOG_FILE) > MAX_LOG_SIZE:
            for i in range(MAX_LOG_FILES - 1, 0, -1):
                old_log = f"{LOG_FILE}.{i}"
                new_log = f"{LOG_FILE}.{i+1}"
                if os.path.exists(old_log):
                    if i + 1 >= MAX_LOG_FILES:
                        os.remove(old_log)
                    else:
                        os.rename(old_log, new_log)
            os.rename(LOG_FILE, f"{LOG_FILE}.1")

def log_message(message):
    """ログメッセージを記録"""
    rotate_log_if_needed()
    timestamp = datetime.now(ZoneInfo("Asia/Tokyo")).strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"ログ書き込みエラー: {str(e)}")

# ========== Google Drive関連 ==========
def get_drive_service():
    """Google Drive APIサービスを取得"""
    try:
        # 暗号化された認証情報がある場合
        if CREDENTIAL_MANAGER_AVAILABLE and os.path.exists('credentials.enc'):
            password = os.environ.get('SCREENSHOT_PASSWORD')
            if password:
                cm = CredentialManager()
                # get_credentials_for_gdriveメソッドを使用
                key_data = cm.get_credentials_for_gdrive(password=password)
                if key_data:
                    credentials = service_account.Credentials.from_service_account_info(
                        key_data,  # すでにdict形式
                        scopes=SCOPES
                    )
                    return build('drive', 'v3', credentials=credentials)
        
        # 通常のサービスアカウントファイル
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        key_file_path = os.path.join(base_path, SERVICE_ACCOUNT_FILE)
        
        if not os.path.exists(key_file_path):
            log_message(f"エラー: サービスアカウントファイルが見つかりません: {key_file_path}")
            return None
        
        credentials = service_account.Credentials.from_service_account_file(
            key_file_path,
            scopes=SCOPES
        )
        
        return build('drive', 'v3', credentials=credentials)
        
    except Exception as e:
        log_message(f"Google Drive API初期化エラー: {str(e)}")
        return None

def upload_to_gdrive(file_path, file_name, service):
    """Google Driveにファイルをアップロード"""
    try:
        file_metadata = {
            'name': file_name,
            'parents': [GDRIVE_FOLDER_ID]
        }
        
        media = MediaFileUpload(file_path, mimetype='image/png', resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        log_message(f"アップロード成功: {file_name} (File ID: {file.get('id')})")
        return True
        
    except HttpError as error:
        if error.resp.status == 404:
            log_message(f"エラー: 指定されたフォルダIDが見つかりません: {GDRIVE_FOLDER_ID}")
        else:
            log_message(f"アップロードエラー: {error}")
        return False
    except Exception as e:
        log_message(f"アップロードエラー: {str(e)}")
        return False

def take_and_upload_screenshot():
    """スクリーンショットを撮影してGoogle Driveにアップロード"""
    service = None
    temp_file_path = None
    
    try:
        service = get_drive_service()
        if not service:
            log_message("Google Drive APIサービスの取得に失敗しました")
            return
        
        # ファイル名の生成
        username = os.getlogin()
        jst_now = datetime.now(ZoneInfo("Asia/Tokyo"))
        date_str = jst_now.strftime('%Y%m%d')
        timestamp_suffix = jst_now.strftime('%H%M%S')
        file_name = f"{date_str}-{username}_{timestamp_suffix}.png"
        
        # 一時ディレクトリにファイルを保存
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, file_name)
        
        # スクリーンショット撮影
        log_message(f"スクリーンショット撮影開始: {file_name}")
        
        try:
            if not MSS_AVAILABLE:
                raise ImportError("mss not available")
            
            with mss.mss() as sct:
                monitor = sct.monitors[0]
                screenshot = sct.grab(monitor)
                img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
                img.save(temp_file_path)
                log_message(f"全画面スクリーンショット保存完了: {temp_file_path}")
                
        except (ImportError, Exception) as e:
            log_message("全画面撮影に失敗。プライマリモニターのみ撮影します。")
            screenshot = pyautogui.screenshot()
            screenshot.save(temp_file_path)
            log_message(f"スクリーンショット保存完了: {temp_file_path}")
        
        # Google Driveにアップロード
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

# ========== GUI クラス ==========
class ScreenshotApp:
    def __init__(self):
        self.root = None
        self.is_recording = False
        self.screenshot_thread = None
        self.stop_event = threading.Event()
        
        # パスワード認証画面を表示
        self.show_login()
    
    def show_login(self):
        """パスワード認証画面"""
        self.login_window = tk.Tk()
        self.login_window.title("Screenshot Tool - Login")
        self.login_window.resizable(False, False)
        
        # パスワード入力フィールド
        frame = ttk.Frame(self.login_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Password:", font=('', 11)).pack(pady=(20, 10))
        
        self.password_entry = ttk.Entry(frame, show="*", width=30, font=('', 11))
        self.password_entry.pack(pady=10)
        self.password_entry.focus()
        
        # Enterキーでログイン
        self.password_entry.bind('<Return>', lambda e: self.verify_password())
        
        ttk.Button(frame, text="OK", width=15, command=self.verify_password).pack(pady=15)
        
        # ウィンドウ閉じるボタンでアプリ終了
        self.login_window.protocol("WM_DELETE_WINDOW", self.quit_app)
        
        # ウィンドウサイズを自動調整してから中央配置
        self.login_window.update_idletasks()
        self.login_window.geometry("")  # 自動サイズ調整
        self.login_window.update_idletasks()
        
        # 中央配置
        width = self.login_window.winfo_reqwidth()
        height = self.login_window.winfo_reqheight()
        x = (self.login_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.login_window.winfo_screenheight() // 2) - (height // 2)
        self.login_window.geometry(f'+{x}+{y}')
        
        self.login_window.mainloop()
    
    def verify_password(self):
        """パスワード検証"""
        input_password = self.password_entry.get()
        
        # 環境変数に保存（credential_manager用）
        os.environ['SCREENSHOT_PASSWORD'] = input_password
        
        # 暗号化された認証情報で検証
        if CREDENTIAL_MANAGER_AVAILABLE and os.path.exists('credentials.enc'):
            try:
                cm = CredentialManager()
                # get_credentials_for_gdriveメソッドを使用（パスワード引数対応）
                key_data = cm.get_credentials_for_gdrive(password=input_password)
                if key_data:
                    # パスワードが正しい場合
                    self.login_window.destroy()
                    self.show_main_window()
                    return
            except Exception as e:
                log_message(f"パスワード検証エラー: {str(e)}")
        
        # パスワードが間違っている場合
        messagebox.showerror("Error", "Incorrect password")
        self.password_entry.delete(0, tk.END)
        self.password_entry.focus()
    
    def show_main_window(self):
        """メイン画面を表示"""
        self.root = tk.Tk()
        self.root.title("Screenshot Monitor")
        self.root.resizable(False, False)
        
        # メインフレーム
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 状態表示ラベル
        self.status_label = ttk.Label(frame, text="状態: 停止中", font=('', 14, 'bold'))
        self.status_label.pack(pady=(30, 20))
        
        # 制御ボタン
        self.control_button = ttk.Button(frame, text="開始", width=20, 
                                        command=self.toggle_recording,
                                        style='Large.TButton')
        self.control_button.pack(pady=20)
        
        # ボタンスタイルの設定
        style = ttk.Style()
        style.configure('Large.TButton', font=('', 12))
        
        # ウィンドウ閉じるボタンの動作を設定
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # ウィンドウサイズを自動調整してから中央配置
        self.root.update_idletasks()
        self.root.geometry("")  # 自動サイズ調整
        self.root.update_idletasks()
        
        # 中央配置
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
        
        # 初期化完了ログ
        log_message("=== Screenshot Monitor GUI 起動 ===")
        log_message(f"撮影間隔: {INTERVAL_MINUTES}分")
        log_message(f"Google DriveフォルダID: {GDRIVE_FOLDER_ID}")
        
        self.root.mainloop()
    
    def toggle_recording(self):
        """撮影のオン/オフ切り替え"""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        """撮影開始"""
        self.is_recording = True
        self.status_label.config(text="状態: 撮影中")
        self.control_button.config(text="停止")
        
        log_message("撮影開始")
        
        # スクリーンショットスレッドを開始
        self.stop_event.clear()
        self.screenshot_thread = threading.Thread(target=self.screenshot_loop, daemon=True)
        self.screenshot_thread.start()
    
    def stop_recording(self):
        """撮影停止"""
        self.is_recording = False
        self.status_label.config(text="状態: 停止中")
        self.control_button.config(text="開始")
        
        log_message("撮影停止")
        
        # スレッドを停止
        self.stop_event.set()
    
    def screenshot_loop(self):
        """スクリーンショット撮影ループ（別スレッド）"""
        # 最初のスクリーンショットをすぐに撮影
        if not self.stop_event.is_set():
            take_and_upload_screenshot()
        
        # 定期実行
        while not self.stop_event.is_set():
            # INTERVAL_MINUTES分待機（1秒ごとにチェック）
            for _ in range(INTERVAL_MINUTES * 60):
                if self.stop_event.is_set():
                    break
                time.sleep(1)
            
            # 撮影実行
            if not self.stop_event.is_set():
                take_and_upload_screenshot()
    
    def on_close(self):
        """ウィンドウを閉じる時の処理"""
        if messagebox.askyesno("確認", "アプリケーションを終了しますか？"):
            self.quit_app()
    
    def quit_app(self):
        """アプリケーション終了"""
        log_message("=== Screenshot Monitor GUI 終了 ===")
        self.stop_event.set()
        
        try:
            if hasattr(self, 'root') and self.root:
                self.root.quit()
                self.root.destroy()
        except:
            pass
        
        try:
            if hasattr(self, 'login_window') and self.login_window:
                self.login_window.quit()
                self.login_window.destroy()
        except:
            pass
        
        sys.exit(0)

def main():
    """メイン関数"""
    try:
        app = ScreenshotApp()
    except Exception as e:
        log_message(f"起動エラー: {str(e)}")
        log_message(f"トレースバック: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
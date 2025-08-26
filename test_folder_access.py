#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Googleドライブフォルダのアクセス権限診断スクリプト
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 設定
SERVICE_ACCOUNT_FILE = 'service-account-key.json'
GDRIVE_FOLDER_ID = '1j8QhcrXodnMm6C7y9yJVnwqbHEREu-iO'

def test_folder_access():
    """フォルダへのアクセスをテスト"""
    try:
        # サービスアカウントで認証
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        # Drive APIサービスを構築
        service = build('drive', 'v3', credentials=credentials)
        
        print(f"サービスアカウント: {credentials.service_account_email}")
        print(f"フォルダID: {GDRIVE_FOLDER_ID}")
        print("-" * 50)
        
        # フォルダ情報を取得
        try:
            folder = service.files().get(fileId=GDRIVE_FOLDER_ID, fields='id,name,permissions').execute()
            print(f"✓ フォルダ名: {folder.get('name', '不明')}")
            print(f"✓ フォルダID: {folder.get('id')}")
            
            # 権限情報を表示
            permissions = folder.get('permissions', [])
            if permissions:
                print("\n権限情報:")
                for perm in permissions:
                    print(f"  - {perm}")
            else:
                print("\n権限情報が取得できませんでした。")
                
        except Exception as e:
            print(f"✗ フォルダにアクセスできません: {e}")
            print("\n解決方法:")
            print("1. Googleドライブでフォルダを開く")
            print("2. 共有ボタンをクリック")
            print(f"3. '{credentials.service_account_email}' を追加")
            print("4. '編集者' 権限を付与")
            
        # ファイル一覧を取得してみる
        print("\n" + "-" * 50)
        print("フォルダ内のファイル一覧を取得中...")
        try:
            results = service.files().list(
                q=f"'{GDRIVE_FOLDER_ID}' in parents",
                pageSize=5,
                fields="files(id, name)"
            ).execute()
            
            files = results.get('files', [])
            if files:
                print(f"✓ {len(files)}個のファイルが見つかりました:")
                for file in files:
                    print(f"  - {file['name']}")
            else:
                print("✓ フォルダは空です")
                
        except Exception as e:
            print(f"✗ ファイル一覧を取得できません: {e}")
            
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    test_folder_access()
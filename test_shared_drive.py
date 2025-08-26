#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共有ドライブとマイドライブの診断スクリプト
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 設定
SERVICE_ACCOUNT_FILE = 'service-account-key.json'
GDRIVE_FOLDER_ID = '1j8QhcrXodnMm6C7y9yJVnwqbHEREu-iO'

def test_drive_access():
    """ドライブへのアクセスをテスト"""
    try:
        # サービスアカウントで認証
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        # Drive APIサービスを構築
        service = build('drive', 'v3', credentials=credentials)
        
        print(f"サービスアカウント: {credentials.service_account_email}")
        print(f"対象フォルダID: {GDRIVE_FOLDER_ID}")
        print("=" * 60)
        
        # 1. マイドライブのフォルダとして試す
        print("\n1. マイドライブのフォルダとしてアクセス:")
        print("-" * 40)
        try:
            folder = service.files().get(
                fileId=GDRIVE_FOLDER_ID,
                fields='id,name,mimeType,parents',
                supportsAllDrives=False
            ).execute()
            print(f"✓ フォルダ名: {folder.get('name')}")
            print(f"✓ タイプ: {folder.get('mimeType')}")
            print(f"✓ 親フォルダ: {folder.get('parents', [])}")
        except Exception as e:
            print(f"✗ マイドライブとしてアクセス失敗: {str(e)[:100]}")
        
        # 2. 共有ドライブのフォルダとして試す
        print("\n2. 共有ドライブのフォルダとしてアクセス:")
        print("-" * 40)
        try:
            folder = service.files().get(
                fileId=GDRIVE_FOLDER_ID,
                fields='id,name,mimeType,parents,driveId',
                supportsAllDrives=True
            ).execute()
            print(f"✓ フォルダ名: {folder.get('name')}")
            print(f"✓ タイプ: {folder.get('mimeType')}")
            print(f"✓ ドライブID: {folder.get('driveId', 'なし（マイドライブ）')}")
            print(f"✓ 親フォルダ: {folder.get('parents', [])}")
        except Exception as e:
            print(f"✗ 共有ドライブとしてアクセス失敗: {str(e)[:100]}")
        
        # 3. 共有されているアイテムを検索
        print("\n3. 共有されているフォルダを検索:")
        print("-" * 40)
        try:
            results = service.files().list(
                q="sharedWithMe=true and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            ).execute()
            
            folders = results.get('files', [])
            if folders:
                print(f"共有されているフォルダ ({len(folders)}個):")
                for folder in folders[:5]:  # 最初の5個だけ表示
                    print(f"  - {folder['name']} (ID: {folder['id']})")
                    if folder['id'] == GDRIVE_FOLDER_ID:
                        print(f"    ★ 目的のフォルダが見つかりました！")
            else:
                print("共有されているフォルダはありません")
        except Exception as e:
            print(f"✗ 共有フォルダの検索失敗: {e}")
        
        # 4. すべてのドライブを表示
        print("\n4. アクセス可能な共有ドライブ:")
        print("-" * 40)
        try:
            results = service.drives().list(
                pageSize=10
            ).execute()
            
            drives = results.get('drives', [])
            if drives:
                print(f"共有ドライブ ({len(drives)}個):")
                for drive in drives:
                    print(f"  - {drive['name']} (ID: {drive['id']})")
            else:
                print("アクセス可能な共有ドライブはありません")
        except Exception as e:
            print(f"✗ 共有ドライブの一覧取得失敗: {e}")
            
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    test_drive_access()
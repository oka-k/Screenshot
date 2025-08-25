#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Drive API認証のテスト
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# 親ディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import auto_screenshot_gdrive as main_module
from credential_manager import CredentialManager


def test_service_account_auth():
    """サービスアカウント認証のテスト"""
    print("=== Google Drive API認証テスト ===")
    
    # 1. サービスアカウントファイルの存在確認
    print("\n1. サービスアカウントファイルの確認...")
    
    service_account_path = Path(main_module.SERVICE_ACCOUNT_FILE)
    credentials_enc_path = Path('credentials.enc')
    
    has_json = service_account_path.exists()
    has_encrypted = credentials_enc_path.exists()
    
    print(f"  service-account-key.json: {'✓ 存在' if has_json else '✗ 存在しない'}")
    print(f"  credentials.enc: {'✓ 存在' if has_encrypted else '✗ 存在しない'}")
    
    if not has_json and not has_encrypted:
        print("⚠️  認証情報が見つかりません。実際のテストはスキップします。")
        print("   service-account-key.json または credentials.enc が必要です。")
        return False
    
    # 2. 認証情報の読み込みテスト
    print("\n2. 認証情報の読み込みテスト...")
    
    try:
        # CredentialManagerを使用して認証情報を取得
        cred_manager = CredentialManager()
        
        if has_encrypted:
            # 暗号化ファイルがある場合
            print("  暗号化された認証情報を読み込み中...")
            try:
                # 環境変数またはマシン紐付けで復号化を試みる
                credentials_dict = cred_manager.get_credentials_for_gdrive()
                print("✓ 暗号化された認証情報の読み込み成功")
            except Exception as e:
                print(f"⚠️  暗号化ファイルの復号化に失敗: {str(e)}")
                if has_json:
                    print("  通常のJSONファイルから読み込みます...")
                    with open(service_account_path, 'r') as f:
                        credentials_dict = json.load(f)
                    print("✓ JSONファイルの読み込み成功")
                else:
                    raise
        else:
            # JSONファイルのみの場合
            with open(service_account_path, 'r') as f:
                credentials_dict = json.load(f)
            print("✓ JSONファイルの読み込み成功")
        
        # 必須フィールドの確認
        required_fields = [
            'type', 'project_id', 'private_key_id', 
            'private_key', 'client_email', 'client_id'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in credentials_dict:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ 必須フィールドが不足: {missing_fields}")
            return False
        
        print("✓ 認証情報の形式が正しい")
        print(f"  プロジェクトID: {credentials_dict['project_id']}")
        print(f"  サービスアカウント: {credentials_dict['client_email']}")
        
    except Exception as e:
        print(f"❌ 認証情報の読み込みエラー: {str(e)}")
        return False
    
    # 3. Google Drive APIサービスの初期化テスト
    print("\n3. Google Drive APIサービスの初期化テスト...")
    
    try:
        service = main_module.get_drive_service()
        
        if service is None:
            print("❌ サービスの初期化に失敗")
            return False
        
        print("✓ Google Drive APIサービスの初期化成功")
        
        # 4. API接続テスト（About情報の取得）
        print("\n4. API接続テスト...")
        try:
            # Drive APIのabout().get()でサービスアカウント情報を取得
            about = service.about().get(fields="user").execute()
            user_info = about.get('user', {})
            
            print("✓ Google Drive APIへの接続成功")
            print(f"  接続ユーザー: {user_info.get('emailAddress', 'Unknown')}")
            
        except Exception as e:
            error_msg = str(e)
            
            if "accessNotConfigured" in error_msg:
                print("⚠️  Google Drive APIが有効化されていません")
                print("   Google Cloud Consoleで有効化してください")
            elif "storageQuotaExceeded" in error_msg:
                print("⚠️  サービスアカウントにはストレージがありません")
                print("   共有ドライブを使用するか、通常のGoogleアカウントに切り替えてください")
            elif "invalid_grant" in error_msg:
                print("❌ 認証エラー: 無効な認証情報")
            else:
                print(f"⚠️  API接続エラー: {error_msg[:100]}")
            
            return False
        
    except Exception as e:
        print(f"❌ サービス初期化エラー: {str(e)}")
        return False
    
    print("\n=== API認証テスト成功 ===")
    return True


def test_folder_access():
    """Googleドライブフォルダへのアクセステスト"""
    print("\n=== フォルダアクセステスト ===")
    
    # フォルダIDの確認
    folder_id = main_module.GDRIVE_FOLDER_ID
    
    if folder_id == 'YOUR_FOLDER_ID_HERE':
        print("⚠️  フォルダIDが設定されていません")
        return False
    
    print(f"フォルダID: {folder_id}")
    
    try:
        service = main_module.get_drive_service()
        if not service:
            print("❌ サービスの初期化に失敗")
            return False
        
        # フォルダの情報を取得
        print("\nフォルダ情報を取得中...")
        try:
            folder = service.files().get(
                fileId=folder_id,
                fields="id, name, mimeType, permissions"
            ).execute()
            
            print(f"✓ フォルダアクセス成功")
            print(f"  フォルダ名: {folder.get('name', 'Unknown')}")
            
            # 権限の確認
            permissions = folder.get('permissions', [])
            print(f"  権限数: {len(permissions)}")
            
            for perm in permissions:
                email = perm.get('emailAddress', 'Unknown')
                role = perm.get('role', 'Unknown')
                print(f"    - {email}: {role}")
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "notFound" in error_msg:
                print(f"❌ フォルダが見つかりません: {folder_id}")
                print("   フォルダIDが正しいか確認してください")
            elif "403" in error_msg or "insufficientPermissions" in error_msg:
                print(f"❌ フォルダへのアクセス権限がありません")
                print("   サービスアカウントにフォルダを共有してください")
            else:
                print(f"❌ フォルダアクセスエラー: {error_msg[:100]}")
            return False
            
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("Google Drive API認証テスト")
    print("="*60)
    
    # 認証テスト
    auth_success = test_service_account_auth()
    
    # フォルダアクセステスト
    if auth_success:
        folder_success = test_folder_access()
    else:
        print("\n⚠️  認証テストが失敗したため、フォルダテストはスキップします")
        folder_success = False
    
    # 結果サマリー
    print("\n" + "="*60)
    print("テスト結果")
    print("="*60)
    print(f"API認証: {'✅ 成功' if auth_success else '❌ 失敗'}")
    print(f"フォルダアクセス: {'✅ 成功' if folder_success else '❌ 失敗'}")
    
    if auth_success and folder_success:
        print("\n✅ すべてのAPI認証テスト完了")
    else:
        print("\n⚠️  一部のテストが失敗しました")
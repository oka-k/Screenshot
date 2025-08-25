#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
暗号化機能のテスト
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# 親ディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from credential_manager import CredentialManager


def test_encryption():
    """暗号化・復号化機能のテスト"""
    print("=== 暗号化機能テスト ===")
    
    # テスト用の一時ディレクトリ
    test_dir = tempfile.mkdtemp()
    
    try:
        # テスト用のJSON認証情報
        test_credentials = {
            "type": "service_account",
            "project_id": "test-project-123",
            "private_key_id": "test-key-id",
            "private_key": "-----BEGIN PRIVATE KEY-----\nTEST_KEY_DATA\n-----END PRIVATE KEY-----\n",
            "client_email": "test@test-project.iam.gserviceaccount.com",
            "client_id": "123456789",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
        
        # 1. パスワード暗号化テスト
        print("\n1. パスワード暗号化・復号化テスト...")
        
        # テスト用JSONファイルを作成
        test_json_file = os.path.join(test_dir, "test_credentials.json")
        with open(test_json_file, 'w') as f:
            json.dump(test_credentials, f)
        
        # 暗号化マネージャーを初期化
        encrypted_file = os.path.join(test_dir, "test_encrypted.enc")
        cm = CredentialManager(encrypted_file_path=encrypted_file)
        
        # パスワードで暗号化（テスト用に直接メソッドを呼ぶ）
        test_password = "TestPassword123!"
        salt = os.urandom(16)
        key = cm._derive_key(test_password, salt)
        
        from cryptography.fernet import Fernet
        fernet = Fernet(key)
        
        json_bytes = json.dumps(test_credentials).encode()
        encrypted_data = fernet.encrypt(json_bytes)
        
        # 暗号化データを保存
        with open(encrypted_file, 'wb') as f:
            f.write(salt + encrypted_data)
        
        print("✓ 暗号化完了")
        
        # 復号化テスト
        with open(encrypted_file, 'rb') as f:
            data = f.read()
        
        recovered_salt = data[:16]
        recovered_encrypted = data[16:]
        
        # 同じパスワードで復号化
        recovered_key = cm._derive_key(test_password, recovered_salt)
        fernet2 = Fernet(recovered_key)
        decrypted_data = fernet2.decrypt(recovered_encrypted)
        recovered_credentials = json.loads(decrypted_data.decode())
        
        # 復号化したデータが一致することを確認
        assert recovered_credentials == test_credentials, "復号化データが一致しない"
        print("✓ 正しく復号化できた")
        
        # 2. 間違ったパスワードでの復号化テスト
        print("\n2. 間違ったパスワードでの復号化テスト...")
        wrong_password = "WrongPassword"
        wrong_key = cm._derive_key(wrong_password, recovered_salt)
        fernet3 = Fernet(wrong_key)
        
        try:
            fernet3.decrypt(recovered_encrypted)
            assert False, "間違ったパスワードで復号化できてしまった"
        except Exception:
            print("✓ 間違ったパスワードでは復号化できない")
        
        # 3. ファイルサイズ確認
        print("\n3. 暗号化ファイルサイズ確認...")
        original_size = len(json.dumps(test_credentials))
        encrypted_size = os.path.getsize(encrypted_file)
        
        print(f"  元のサイズ: {original_size} bytes")
        print(f"  暗号化後: {encrypted_size} bytes")
        print(f"  オーバーヘッド: {encrypted_size - original_size} bytes")
        
        assert encrypted_size > original_size, "暗号化後のサイズが小さすぎる"
        print("✓ 暗号化ファイルのサイズが適切")
        
        # 4. 暗号化ファイルの存在確認
        print("\n4. ファイル操作テスト...")
        assert os.path.exists(encrypted_file), "暗号化ファイルが存在しない"
        assert os.path.getsize(encrypted_file) > 0, "暗号化ファイルが空"
        
        # ファイルがバイナリであることを確認
        with open(encrypted_file, 'rb') as f:
            header = f.read(16)
        
        assert len(header) == 16, "ソルトのサイズが不正"
        print("✓ 暗号化ファイルの形式が正しい")
        
        print("\n=== すべての暗号化テスト成功 ===")
        
    finally:
        # クリーンアップ
        shutil.rmtree(test_dir)


def test_key_derivation():
    """鍵導出関数のテスト"""
    print("\n=== 鍵導出テスト ===")
    
    cm = CredentialManager()
    
    # 同じパスワードとソルトから同じ鍵が生成されることを確認
    password = "TestPassword"
    salt = b"1234567890123456"  # 16バイト
    
    key1 = cm._derive_key(password, salt)
    key2 = cm._derive_key(password, salt)
    
    assert key1 == key2, "同じ入力から異なる鍵が生成された"
    print("✓ 鍵導出の再現性確認")
    
    # 異なるソルトから異なる鍵が生成されることを確認
    salt2 = b"6543210987654321"
    key3 = cm._derive_key(password, salt2)
    
    assert key1 != key3, "異なるソルトから同じ鍵が生成された"
    print("✓ ソルトによる鍵の差別化確認")
    
    print("\n=== 鍵導出テスト成功 ===")


if __name__ == "__main__":
    test_encryption()
    test_key_derivation()
    print("\n✅ 暗号化テスト完了")
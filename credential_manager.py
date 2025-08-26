#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
認証情報暗号化管理モジュール
サービスアカウントキーを暗号化して安全に管理します。
"""

import os
import json
import base64
import getpass
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CredentialManager:
    """認証情報の暗号化・復号化を管理するクラス"""
    
    def __init__(self, encrypted_file_path='credentials.enc'):
        """
        初期化
        
        Args:
            encrypted_file_path: 暗号化された認証情報ファイルのパス
        """
        self.encrypted_file_path = Path(encrypted_file_path)
        self.key_file_path = Path('.key')  # 暗号化キーを保存するファイル
        
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        パスワードから暗号化キーを生成
        
        Args:
            password: ユーザーが入力したパスワード
            salt: ソルト（ランダムなバイト列）
            
        Returns:
            暗号化キー
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _get_machine_id(self) -> str:
        """
        マシン固有のIDを生成（Windowsの場合）
        
        Returns:
            マシンID
        """
        import platform
        import subprocess
        
        machine_info = []
        
        # コンピューター名
        machine_info.append(platform.node())
        
        # プロセッサ情報
        machine_info.append(platform.processor())
        
        # WindowsのマシンID取得
        try:
            # wmic csproduct get UUID コマンドでUUIDを取得
            result = subprocess.run(
                ['wmic', 'csproduct', 'get', 'UUID'],
                capture_output=True,
                text=True,
                shell=True
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    machine_info.append(lines[1].strip())
        except Exception:
            pass
        
        # 情報を結合してハッシュ化
        combined = ''.join(machine_info)
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def encrypt_credentials(self, json_file_path: str, password: str = None, use_machine_binding: bool = None):
        """
        JSONファイルを暗号化
        
        Args:
            json_file_path: 元のJSONファイルパス
            password: 暗号化用パスワード（Noneの場合は対話的に入力）
            use_machine_binding: マシンに紐付けた暗号化を行うか（passwordより優先）
        """
        # JSONファイルを読み込み
        with open(json_file_path, 'r', encoding='utf-8') as f:
            credentials = json.load(f)
        
        # ソルトを生成
        salt = os.urandom(16)
        
        # 暗号化キーを生成
        if use_machine_binding is None:
            # 引数で明示的に指定されていない場合、passwordの有無で判断
            use_machine_binding = (password is None)
        
        if use_machine_binding:
            # マシンIDを使用した自動暗号化
            machine_id = self._get_machine_id()
            key = self._derive_key(machine_id, salt)
        else:
            # パスワードベースの暗号化
            if password is None:
                password = getpass.getpass("暗号化パスワードを入力してください: ")
                confirm = getpass.getpass("パスワードを再入力してください: ")
                
                if password != confirm:
                    raise ValueError("パスワードが一致しません")
            
            key = self._derive_key(password, salt)
        
        # Fernetインスタンスを作成
        fernet = Fernet(key)
        
        # JSONデータを暗号化
        json_bytes = json.dumps(credentials).encode()
        encrypted_data = fernet.encrypt(json_bytes)
        
        # 暗号化データとソルトを保存
        with open(self.encrypted_file_path, 'wb') as f:
            f.write(salt + encrypted_data)
        
        print(f"認証情報を暗号化しました: {self.encrypted_file_path}")
        
        # 元のJSONファイルを削除するか確認
        response = input(f"元のファイル {json_file_path} を削除しますか？ (y/n): ")
        if response.lower() == 'y':
            os.remove(json_file_path)
            print(f"{json_file_path} を削除しました")
    
    def decrypt_credentials(self, use_machine_binding: bool = True) -> dict:
        """
        暗号化された認証情報を復号化
        
        Args:
            use_machine_binding: マシン紐付けの復号化を使用するか
            
        Returns:
            復号化されたJSON辞書
        """
        if not self.encrypted_file_path.exists():
            raise FileNotFoundError(f"暗号化ファイルが見つかりません: {self.encrypted_file_path}")
        
        # 暗号化データを読み込み
        with open(self.encrypted_file_path, 'rb') as f:
            data = f.read()
        
        # ソルトと暗号化データを分離
        salt = data[:16]
        encrypted_data = data[16:]
        
        # 暗号化キーを生成
        if use_machine_binding:
            # マシンIDを使用した自動復号化
            machine_id = self._get_machine_id()
            key = self._derive_key(machine_id, salt)
        else:
            # パスワードベースの復号化
            password = getpass.getpass("復号化パスワードを入力してください: ")
            key = self._derive_key(password, salt)
        
        # 復号化
        try:
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)
            credentials = json.loads(decrypted_data.decode())
            return credentials
        except Exception as e:
            raise ValueError(f"復号化に失敗しました: {str(e)}")
    
    def get_credentials_for_gdrive(self, password: str = None) -> dict:
        """
        Googleドライブ用の認証情報を取得（パスワード指定で復号化）
        
        Args:
            password: 復号化用パスワード（Noneの場合はマシン紐付け）
            
        Returns:
            認証情報の辞書
        """
        try:
            # まず暗号化ファイルから復号化を試みる
            if self.encrypted_file_path.exists():
                if password:
                    # パスワードが指定されている場合
                    with open(self.encrypted_file_path, 'rb') as f:
                        data = f.read()
                    salt = data[:16]
                    encrypted_data = data[16:]
                    key = self._derive_key(password, salt)
                    fernet = Fernet(key)
                    decrypted_data = fernet.decrypt(encrypted_data)
                    return json.loads(decrypted_data.decode())
                else:
                    # マシン紐付け暗号化の場合
                    return self.decrypt_credentials(use_machine_binding=True)
            
            # 暗号化ファイルがない場合、通常のJSONファイルを探す
            json_path = Path('service-account-key.json')
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            raise FileNotFoundError("認証情報ファイルが見つかりません")
            
        except Exception as e:
            raise Exception(f"認証情報の取得に失敗しました: {str(e)}")


def main():
    """CLIツールとして実行"""
    import sys
    
    manager = CredentialManager()
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python credential_manager.py encrypt <json_file>  - JSONファイルを暗号化")
        print("  python credential_manager.py decrypt              - 暗号化ファイルを復号化して表示")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'encrypt':
        if len(sys.argv) < 3:
            print("エラー: JSONファイルパスを指定してください")
            sys.exit(1)
        
        json_file = sys.argv[2]
        if not os.path.exists(json_file):
            print(f"エラー: ファイルが見つかりません: {json_file}")
            sys.exit(1)
        
        # マシン紐付け暗号化を使用
        manager.encrypt_credentials(json_file, use_machine_binding=True)
        
    elif command == 'decrypt':
        try:
            credentials = manager.decrypt_credentials(use_machine_binding=True)
            print("復号化成功:")
            print(json.dumps(credentials, indent=2))
        except Exception as e:
            print(f"復号化失敗: {str(e)}")
            sys.exit(1)
    
    else:
        print(f"不明なコマンド: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ログローテーション機能のテスト
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 親ディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# テスト対象のモジュールをインポート
import auto_screenshot_gdrive as main_module


def test_log_rotation():
    """ログローテーション機能のテスト"""
    print("=== ログローテーション機能テスト ===")
    
    # テスト用の一時ディレクトリを作成
    test_dir = tempfile.mkdtemp()
    original_log_file = main_module.LOG_FILE
    
    try:
        # ログファイルパスを一時ディレクトリに変更
        test_log_file = os.path.join(test_dir, "test.log")
        main_module.LOG_FILE = test_log_file
        
        # 1. 小さいログファイルではローテーションしない
        print("\n1. 小さいファイルのテスト...")
        with open(test_log_file, 'w') as f:
            f.write("Test log entry\n" * 10)
        
        main_module.rotate_log_if_needed()
        
        # ローテーションされていないことを確認
        assert os.path.exists(test_log_file), "ログファイルが存在しない"
        assert not os.path.exists(f"{test_log_file}.1"), "不要なローテーションが発生"
        print("✓ 小さいファイルはローテーションされない")
        
        # 2. 大きいログファイルはローテーションする
        print("\n2. 大きいファイルのテスト...")
        # 10MB以上のファイルを作成
        large_content = "X" * (11 * 1024 * 1024)  # 11MB
        with open(test_log_file, 'w') as f:
            f.write(large_content)
        
        original_size = os.path.getsize(test_log_file)
        main_module.rotate_log_if_needed()
        
        # ローテーションされたことを確認
        assert os.path.exists(test_log_file), "新しいログファイルが作成されていない"
        assert os.path.exists(f"{test_log_file}.1"), "ローテーションファイルが作成されていない"
        assert os.path.getsize(test_log_file) < original_size, "ログファイルがリセットされていない"
        print("✓ 大きいファイルは正しくローテーションされる")
        
        # 3. 複数世代のローテーション
        print("\n3. 複数世代のローテーションテスト...")
        for i in range(1, 4):
            # 既存のローテーションファイルを作成
            with open(f"{test_log_file}.{i}", 'w') as f:
                f.write(f"Rotation {i}\n")
        
        # 新たにローテーション
        with open(test_log_file, 'w') as f:
            f.write("X" * (11 * 1024 * 1024))
        
        main_module.rotate_log_if_needed()
        
        # ファイルが正しくシフトされたことを確認
        assert os.path.exists(f"{test_log_file}.1"), ".1ファイルが存在する"
        assert os.path.exists(f"{test_log_file}.2"), ".2ファイルが存在する"
        assert os.path.exists(f"{test_log_file}.3"), ".3ファイルが存在する"
        assert os.path.exists(f"{test_log_file}.4"), ".4ファイルが存在する"
        print("✓ 複数世代のローテーションが正しく動作")
        
        # 4. 古いログファイルのクリーンアップ
        print("\n4. 古いログのクリーンアップテスト...")
        # MAX_LOG_FILES以上のファイルを作成
        for i in range(1, 8):
            with open(f"{test_log_file}.{i}", 'w') as f:
                f.write(f"Old log {i}\n")
        
        main_module.cleanup_old_logs()
        
        # 5世代以上は削除されることを確認
        for i in range(1, 6):
            assert os.path.exists(f"{test_log_file}.{i}"), f".{i}ファイルは保持される"
        assert not os.path.exists(f"{test_log_file}.6"), ".6ファイルは削除される"
        assert not os.path.exists(f"{test_log_file}.7"), ".7ファイルは削除される"
        print("✓ 古いログファイルが正しくクリーンアップされる")
        
        print("\n=== すべてのログローテーションテスト成功 ===")
        
    finally:
        # クリーンアップ
        main_module.LOG_FILE = original_log_file
        shutil.rmtree(test_dir)


if __name__ == "__main__":
    test_log_rotation()
    print("\n✅ ログローテーションテスト完了")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
すべてのテストを実行するスクリプト
"""

import sys
import os
import traceback

# 親ディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_test(test_name, test_function):
    """個別テストを実行"""
    print(f"\n{'='*60}")
    print(f"実行中: {test_name}")
    print('='*60)
    
    try:
        test_function()
        print(f"✅ {test_name} - 成功")
        return True
    except Exception as e:
        print(f"❌ {test_name} - 失敗")
        print(f"エラー: {str(e)}")
        traceback.print_exc()
        return False


def main():
    """すべてのテストを実行"""
    print("="*60)
    print("自動スクリーンショットツール - 総合テスト")
    print("="*60)
    
    # テストモジュールをインポート
    import test_log_rotation
    import test_screenshot
    import test_encryption
    import test_api_auth
    import test_upload
    
    # テストリスト
    tests = [
        ("ログローテーション機能", test_log_rotation.test_log_rotation),
        ("スクリーンショット撮影", test_screenshot.test_screenshot_capture),
        ("暗号化機能", test_encryption.test_encryption),
        ("鍵導出機能", test_encryption.test_key_derivation),
        ("API認証", test_api_auth.test_service_account_auth),
        ("フォルダアクセス", test_api_auth.test_folder_access),
        ("基本アップロード", test_upload.test_upload_basic),
        ("複数ファイルアップロード", test_upload.test_upload_multiple),
        ("大容量ファイルアップロード", test_upload.test_large_file_upload),
    ]
    
    # 結果を記録
    results = []
    
    # 各テストを実行
    for test_name, test_func in tests:
        success = run_test(test_name, test_func)
        results.append((test_name, success))
    
    # 結果サマリー
    print("\n" + "="*60)
    print("テスト結果サマリー")
    print("="*60)
    
    success_count = 0
    fail_count = 0
    
    for test_name, success in results:
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"{test_name:30} : {status}")
        if success:
            success_count += 1
        else:
            fail_count += 1
    
    print("-"*60)
    print(f"合計: {len(results)} テスト")
    print(f"成功: {success_count} テスト")
    print(f"失敗: {fail_count} テスト")
    
    if fail_count == 0:
        print("\n🎉 すべてのテストが成功しました！")
        return 0
    else:
        print(f"\n⚠️ {fail_count} 個のテストが失敗しました")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
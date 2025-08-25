#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
スクリーンショット機能のテスト
"""

import os
import sys
import tempfile
from PIL import Image

# 親ディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_screenshot_capture():
    """スクリーンショット撮影機能のテスト"""
    print("=== スクリーンショット撮影テスト ===")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 1. pyautoguiでの撮影テスト（プライマリモニター）
        print("\n1. プライマリモニター撮影テスト...")
        import pyautogui
        
        screenshot = pyautogui.screenshot()
        test_file = os.path.join(temp_dir, "test_primary.png")
        screenshot.save(test_file)
        
        assert os.path.exists(test_file), "スクリーンショットファイルが作成されていない"
        
        # 画像の検証
        img = Image.open(test_file)
        width, height = img.size
        assert width > 0 and height > 0, "画像サイズが無効"
        print(f"✓ プライマリモニター撮影成功: {width}x{height}")
        
        # 2. mssでの全画面撮影テスト
        print("\n2. 全画面撮影テスト（mss使用）...")
        try:
            import mss
            
            with mss.mss() as sct:
                monitors = sct.monitors
                print(f"  検出されたモニター数: {len(monitors) - 1}")
                
                # 全画面（monitors[0]）を撮影
                monitor = monitors[0]
                screenshot = sct.grab(monitor)
                
                # PIL Imageに変換
                img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
                test_file_all = os.path.join(temp_dir, "test_all.png")
                img.save(test_file_all)
                
                assert os.path.exists(test_file_all), "全画面スクリーンショットが作成されていない"
                
                img_all = Image.open(test_file_all)
                width_all, height_all = img_all.size
                assert width_all > 0 and height_all > 0, "全画面画像サイズが無効"
                
                # 全画面は通常プライマリモニターより大きいか同じ
                assert width_all >= width, "全画面の幅が不正"
                print(f"✓ 全画面撮影成功: {width_all}x{height_all}")
                
                # 各モニターの情報を表示
                for i in range(1, min(len(monitors), 4)):  # 最大3モニターまで表示
                    m = monitors[i]
                    print(f"  モニター{i}: {m['width']}x{m['height']} at ({m['left']}, {m['top']})")
                    
        except ImportError:
            print("⚠ mssがインストールされていないため、全画面テストをスキップ")
        
        # 3. ファイル名生成テスト
        print("\n3. ファイル名生成テスト...")
        from datetime import datetime
        from zoneinfo import ZoneInfo
        
        username = os.getlogin()
        jst_now = datetime.now(ZoneInfo("Asia/Tokyo"))
        date_str = jst_now.strftime('%Y%m%d')
        timestamp = jst_now.strftime('%H%M%S')
        
        filename = f"{date_str}-{username}_{timestamp}.png"
        print(f"✓ ファイル名生成成功: {filename}")
        
        assert date_str in filename, "日付が含まれていない"
        assert username in filename, "ユーザー名が含まれていない"
        assert filename.endswith('.png'), "拡張子が正しくない"
        
        print("\n=== すべてのスクリーンショットテスト成功 ===")
        
    finally:
        # クリーンアップ
        import shutil
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_screenshot_capture()
    print("\n✅ スクリーンショットテスト完了")
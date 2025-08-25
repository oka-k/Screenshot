#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Googleドライブアップロード機能のテスト
"""

import os
import sys
import tempfile
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageFont

# 親ディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import auto_screenshot_gdrive as main_module


def create_test_image(width=800, height=600, text="TEST IMAGE"):
    """テスト用の画像を生成"""
    # 画像を作成
    img = Image.new('RGB', (width, height), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # テキストを描画
    try:
        # フォントサイズを設定（システムフォントを使用）
        font_size = 48
        # Windowsのデフォルトフォントを試す
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # フォントが見つからない場合はデフォルトフォント
            font = ImageFont.load_default()
    except:
        font = None
    
    # 中央にテキストを配置
    text_color = 'darkblue'
    if font:
        # テキストサイズを取得
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        # デフォルトフォントの場合の概算
        text_width = len(text) * 10
        text_height = 20
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), text, fill=text_color, font=font)
    
    # タイムスタンプを追加
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    draw.text((10, height - 30), timestamp, fill='gray')
    
    # 枠線を追加
    draw.rectangle([(0, 0), (width-1, height-1)], outline='darkblue', width=3)
    
    return img


def test_upload_basic():
    """基本的なアップロードテスト"""
    print("=== 基本アップロードテスト ===")
    
    # Google Drive APIサービスを取得
    print("\n1. APIサービスの初期化...")
    service = main_module.get_drive_service()
    
    if not service:
        print("❌ APIサービスの初期化に失敗")
        print("   認証情報を確認してください")
        return False
    
    print("✓ APIサービスの初期化成功")
    
    # テスト画像を作成
    print("\n2. テスト画像の作成...")
    temp_dir = tempfile.mkdtemp()
    
    try:
        # ファイル名を生成
        username = os.getlogin()
        jst_now = datetime.now(ZoneInfo("Asia/Tokyo"))
        date_str = jst_now.strftime('%Y%m%d')
        timestamp = jst_now.strftime('%H%M%S')
        
        test_filename = f"TEST_{date_str}_{username}_{timestamp}.png"
        test_filepath = os.path.join(temp_dir, test_filename)
        
        # テスト画像を作成して保存
        test_img = create_test_image(
            text=f"Upload Test - {username}"
        )
        test_img.save(test_filepath)
        
        file_size = os.path.getsize(test_filepath)
        print(f"✓ テスト画像作成完了: {test_filename}")
        print(f"  サイズ: {file_size:,} bytes")
        
        # アップロードテスト
        print("\n3. Googleドライブへのアップロード...")
        
        start_time = time.time()
        success = main_module.upload_to_gdrive(
            test_filepath, 
            test_filename, 
            service
        )
        upload_time = time.time() - start_time
        
        if success:
            print(f"✓ アップロード成功")
            print(f"  所要時間: {upload_time:.2f}秒")
            print(f"  速度: {file_size / upload_time / 1024:.1f} KB/s")
            return True
        else:
            print("❌ アップロード失敗")
            
            # エラーログを確認
            if os.path.exists(main_module.LOG_FILE):
                with open(main_module.LOG_FILE, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    recent_errors = [l for l in lines[-10:] if 'エラー' in l or 'error' in l.lower()]
                    if recent_errors:
                        print("\n最近のエラーログ:")
                        for error in recent_errors:
                            print(f"  {error.strip()}")
            
            return False
            
    except Exception as e:
        print(f"❌ テスト中にエラー: {str(e)}")
        return False
        
    finally:
        # クリーンアップ
        import shutil
        shutil.rmtree(temp_dir)


def test_upload_multiple():
    """複数ファイルの連続アップロードテスト"""
    print("\n=== 複数ファイル連続アップロードテスト ===")
    
    service = main_module.get_drive_service()
    if not service:
        print("❌ APIサービスの初期化に失敗")
        return False
    
    temp_dir = tempfile.mkdtemp()
    success_count = 0
    
    try:
        # 3つのテスト画像を作成してアップロード
        num_files = 3
        print(f"\n{num_files}個のファイルをアップロードします...")
        
        for i in range(num_files):
            # ユニークなファイル名を生成
            username = os.getlogin()
            jst_now = datetime.now(ZoneInfo("Asia/Tokyo"))
            date_str = jst_now.strftime('%Y%m%d')
            timestamp = jst_now.strftime('%H%M%S')
            
            filename = f"TEST_MULTI_{i+1}_{date_str}_{timestamp}.png"
            filepath = os.path.join(temp_dir, filename)
            
            # 異なるサイズの画像を作成
            width = 640 + (i * 160)
            height = 480 + (i * 120)
            
            img = create_test_image(
                width=width,
                height=height,
                text=f"Multi Test {i+1}/{num_files}"
            )
            img.save(filepath)
            
            print(f"\nファイル {i+1}/{num_files}: {filename}")
            print(f"  サイズ: {width}x{height}")
            
            # アップロード
            if main_module.upload_to_gdrive(filepath, filename, service):
                print(f"  ✓ アップロード成功")
                success_count += 1
            else:
                print(f"  ❌ アップロード失敗")
            
            # 少し待機（API制限対策）
            if i < num_files - 1:
                time.sleep(1)
        
        print(f"\n結果: {success_count}/{num_files} ファイルのアップロード成功")
        return success_count == num_files
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return False
        
    finally:
        import shutil
        shutil.rmtree(temp_dir)


def test_large_file_upload():
    """大きいファイルのアップロードテスト"""
    print("\n=== 大容量ファイルアップロードテスト ===")
    
    service = main_module.get_drive_service()
    if not service:
        print("❌ APIサービスの初期化に失敗")
        return False
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 大きめの画像を作成（Full HD相当）
        print("\n大容量画像の作成中...")
        large_width = 1920
        large_height = 1080
        
        username = os.getlogin()
        jst_now = datetime.now(ZoneInfo("Asia/Tokyo"))
        date_str = jst_now.strftime('%Y%m%d')
        timestamp = jst_now.strftime('%H%M%S')
        
        filename = f"TEST_LARGE_{date_str}_{timestamp}.png"
        filepath = os.path.join(temp_dir, filename)
        
        # グラデーション付きの複雑な画像を作成
        img = Image.new('RGB', (large_width, large_height))
        draw = ImageDraw.Draw(img)
        
        # グラデーション背景
        for y in range(large_height):
            color_value = int(255 * (y / large_height))
            color = (color_value, 100, 255 - color_value)
            draw.line([(0, y), (large_width, y)], fill=color)
        
        # パターンを追加
        for x in range(0, large_width, 50):
            for y in range(0, large_height, 50):
                draw.ellipse([(x, y), (x+30, y+30)], 
                           outline='white', width=2)
        
        # テキストを追加
        draw.text((large_width//2 - 100, large_height//2), 
                 "LARGE FILE TEST", fill='white')
        
        img.save(filepath, optimize=False, quality=95)
        
        file_size = os.path.getsize(filepath)
        print(f"✓ 大容量画像作成完了")
        print(f"  解像度: {large_width}x{large_height}")
        print(f"  ファイルサイズ: {file_size / 1024 / 1024:.2f} MB")
        
        # アップロード
        print("\nアップロード中...")
        start_time = time.time()
        
        success = main_module.upload_to_gdrive(filepath, filename, service)
        
        upload_time = time.time() - start_time
        
        if success:
            print(f"✓ 大容量ファイルのアップロード成功")
            print(f"  所要時間: {upload_time:.2f}秒")
            print(f"  転送速度: {file_size / upload_time / 1024 / 1024:.2f} MB/s")
            return True
        else:
            print("❌ 大容量ファイルのアップロード失敗")
            return False
            
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return False
        
    finally:
        import shutil
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    print("="*60)
    print("Googleドライブアップロードテスト")
    print("="*60)
    
    results = []
    
    # 基本アップロードテスト
    basic_success = test_upload_basic()
    results.append(("基本アップロード", basic_success))
    
    if basic_success:
        # 複数ファイルテスト
        multi_success = test_upload_multiple()
        results.append(("複数ファイル連続", multi_success))
        
        # 大容量ファイルテスト
        large_success = test_large_file_upload()
        results.append(("大容量ファイル", large_success))
    else:
        print("\n⚠️  基本アップロードが失敗したため、他のテストはスキップします")
    
    # 結果サマリー
    print("\n" + "="*60)
    print("アップロードテスト結果")
    print("="*60)
    
    for test_name, success in results:
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"{test_name:20} : {status}")
    
    all_success = all(s for _, s in results)
    if all_success:
        print("\n✅ すべてのアップロードテスト完了")
    else:
        print("\n⚠️  一部のテストが失敗しました")
        print("\n考えられる原因:")
        print("  1. サービスアカウントにストレージ容量がない")
        print("  2. フォルダへの書き込み権限がない")
        print("  3. ネットワーク接続の問題")
        print("  4. API制限に達している")
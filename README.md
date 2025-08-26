# 自動スクリーンショットアップローダー

## 概要
Windowsバックグラウンドで動作し、定期的にスクリーンショットを撮影してGoogleドライブに自動アップロードするツールです。従業員の作業状況を可視化し、リモートワーク環境での業務管理を支援します。

## 主な機能
- **自動スクリーンショット撮影**: 指定間隔（デフォルト5分）で自動撮影
- **マルチモニター対応**: 全モニターを1枚の画像に結合
- **Googleドライブ自動アップロード**: サービスアカウント認証で安全にアップロード
- **暗号化認証情報**: APIキーを暗号化して配布（従業員に生のキーを渡さない）
- **GUI制御画面**: 撮影の開始/停止を簡単に制御
- **パスワード保護**: 初回起動時のパスワード認証
- **ログローテーション**: ログファイルの自動管理（10MB、5世代）

## システム要件
- Windows 10/11
- Python 3.9以上（開発環境のみ）
- インターネット接続

## GUI版の新機能
### 3つのシンプルな機能
1. **撮影のオン/オフ切り替え** - ボタン1つで制御
2. **撮影状態の表示** - 現在の状態を明確に表示
3. **パスワード認証** - 初回起動時の安全な認証

## セットアップ（管理者向け）

### 1. 必要なファイルの準備
```
ScreenShot/
├── auto_screenshot_gui.py        # GUI版メインプログラム（NEW）
├── auto_screenshot_gdrive.py     # CLI版メインプログラム
├── credential_manager.py         # 暗号化管理モジュール
├── service-account-key.json      # Googleサービスアカウントキー（要取得）
└── requirements.txt              # 依存パッケージリスト
```

### 2. Googleサービスアカウントの設定
1. Google Cloud Consoleでプロジェクトを作成
2. Google Drive APIを有効化
3. サービスアカウントを作成してキーをダウンロード
4. `service-account-key.json`として保存
5. 共有ドライブの特定フォルダにアクセス権限を付与

### 3. 設定の変更
`auto_screenshot_gui.py`の定数を編集（ハードコード）：
```python
INTERVAL_MINUTES = 5  # スクリーンショット間隔
GDRIVE_FOLDER_ID = "your-folder-id"  # アップロード先フォルダID
```

### 4. 従業員配布用ファイルの作成

#### GUI版の場合（推奨）
```batch
# GUI版の配布準備
prepare_gui_for_employees.bat
```

#### CLI版の場合
```batch
# CLI版の配布準備
prepare_for_employees_en.bat
```

両方とも：
1. パスワードを設定（従業員に通知する共通パスワード）
2. 自動的に暗号化とビルドが実行される
3. `dist/`フォルダに配布用ファイルが生成される

## 従業員への配布

### 配布ファイル（GUI版）
```
dist/
└── ScreenshotMonitor.exe    # GUI版実行ファイル（認証情報埋め込み済み）
```

### 従業員の実行方法（GUI版）

#### 使い方
1. `ScreenshotMonitor.exe`をダブルクリック
2. パスワード入力画面で管理者から通知されたパスワードを入力
   （ビルド時に設定したパスワード = GUIログインパスワード = 認証情報復号化パスワード）
3. メイン画面が表示される
4. 「開始」ボタンで撮影開始、「停止」ボタンで一時停止

## ファイル構成

### 開発環境
```
ScreenShot/
├── auto_screenshot_gui.py        # GUI版メインプログラム
├── auto_screenshot_gdrive.py     # CLI版メインプログラム
├── credential_manager.py         # 暗号化管理
├── service-account-key.json      # 認証情報（機密）
├── credentials.enc               # 暗号化済み認証情報
├── requirements.txt              # 依存パッケージ
├── GUI設計書.md                  # GUI仕様書
├── prepare_gui_for_employees.bat # GUI版配布準備
├── build_gui.bat                # GUI版ビルド
├── prepare_for_employees_en.bat  # CLI版配布準備
├── build_secure_en.bat          # CLI版セキュアビルド
├── test/                        # テストスイート
│   ├── test_screenshot.py       # スクリーンショットテスト
│   ├── test_encryption.py       # 暗号化テスト
│   ├── test_log_rotation.py     # ログローテーションテスト
│   ├── test_api_auth.py        # API認証テスト
│   ├── test_upload.py          # アップロードテスト
│   └── run_all_tests.py        # 統合テスト実行
├── README.md                    # このファイル
├── README_Encryption.md         # 暗号化詳細ガイド
├── README_GoogleDrive.md        # Google Drive設定ガイド
├── CLAUDE.md                   # AI開発支援用
├── 設計書.md                    # 技術設計書
└── .gitignore                  # Git除外設定
```

### 実行時生成ファイル
```
├── auto_screenshot.log          # 実行ログ
├── auto_screenshot.log.1-5      # ローテーション済みログ
└── temp/                       # 一時ファイル（自動削除）
```

## 技術仕様

### スクリーンショット
- **ライブラリ**: mss（高速、マルチモニター対応）
- **形式**: PNG（可逆圧縮）
- **命名規則**: `YYYYMMDD-ユーザー名_HHMMSS.png`（JST時刻）

### GUI
- **フレームワーク**: tkinter（Python標準）
- **画面**: パスワード入力画面 → メイン制御画面
- **制御**: 撮影開始/停止のトグル

### 暗号化
- **アルゴリズム**: Fernet（AES-128）
- **鍵導出**: PBKDF2-SHA256（100,000回反復）
- **ソルト**: 16バイトランダム値

### ログ管理
- **最大サイズ**: 10MB
- **世代数**: 5世代
- **形式**: `[YYYY-MM-DD HH:MM:SS] メッセージ`

### Google Drive連携
- **API**: Google Drive API v3
- **認証**: サービスアカウント
- **アップロード先**: 共有ドライブの指定フォルダ

## トラブルシューティング

### よくある問題

#### 起動しない
- Windows Defenderの警告が出る場合は、「詳細情報」→「実行」を選択
- または、Windowsセキュリティの除外リストに追加

#### パスワードエラー
- 暗号化時に設定したパスワードと同じものを入力
- 大文字小文字を区別します

#### アップロードエラー
- インターネット接続を確認
- `auto_screenshot.log`でエラー詳細を確認

#### 「指定されたフォルダIDが見つかりません」エラー
- **原因**: 共有ドライブへのアクセス権限不足
- **解決方法**: 
  1. サービスアカウントが共有ドライブのメンバーになっているか確認
  2. GUI版の場合、`supportsAllDrives=True`パラメータが設定されているか確認
  3. フォルダIDが正しいことを確認（共有ドライブのフォルダIDを使用）
- **コード確認箇所**: `upload_to_gdrive`関数内の`files().create()`メソッドに`supportsAllDrives=True`が必要

### ログファイルの確認
```
[2024-01-25 10:30:00] スクリーンショット撮影開始
[2024-01-25 10:30:01] アップロード成功: 20240125-user.png
```

## セキュリティ

### 保護される情報
- Googleサービスアカウント認証情報
- APIアクセストークン
- アップロード先フォルダID

### セキュリティ対策
- 認証情報の暗号化（AES-128）
- パスワード保護による配布
- GUI起動時のパスワード認証
- .gitignoreによる機密情報の除外
- ログファイルへの機密情報非記録

## 開発者向け

### 必要パッケージのインストール
```bash
pip install -r requirements.txt
```

### テストの実行
```bash
# 全テスト実行
python test/run_all_tests.py

# 個別テスト
python test/test_screenshot.py
python test/test_encryption.py
```

### ビルド
```bash
# GUI版の暗号化済み配布用ビルド
prepare_gui_for_employees.bat

# GUI版の開発用ビルド
build_gui.bat

# CLI版の暗号化済み配布用ビルド
prepare_for_employees_en.bat

# CLI版の開発用ビルド
build_secure_en.bat
```

## ライセンス
内部使用専用ツール

## サポート
社内システム管理者まで連絡してください。

## 更新履歴
- v3.1: GUI版の共有ドライブアクセス問題を修正（supportsAllDrivesパラメータ追加）
- v3.0: GUI版追加、撮影制御機能実装
- v2.1: PyInstaller実行ファイル内の埋め込みcredentials.encパス解決を修正
- v2.0: マルチモニター対応、ログローテーション実装
- v1.5: パスワード暗号化方式に統一
- v1.0: 初回リリース
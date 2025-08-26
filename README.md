# 自動スクリーンショットアップローダー

## 概要
Windowsバックグラウンドで動作し、定期的にスクリーンショットを撮影してGoogleドライブに自動アップロードするツールです。従業員の作業状況を可視化し、リモートワーク環境での業務管理を支援します。

## 主な機能
- **自動スクリーンショット撮影**: 指定間隔（デフォルト5分）で自動撮影
- **マルチモニター対応**: 全モニターを1枚の画像に結合
- **Googleドライブ自動アップロード**: サービスアカウント認証で安全にアップロード
- **暗号化認証情報**: APIキーを暗号化して配布（従業員に生のキーを渡さない）
- **ログローテーション**: ログファイルの自動管理（10MB、5世代）
- **バックグラウンド動作**: ウィンドウを表示せずに静かに実行

## システム要件
- Windows 10/11
- Python 3.9以上（開発環境のみ）
- インターネット接続

## セットアップ（管理者向け）

### 1. 必要なファイルの準備
```
ScreenShot/
├── auto_screenshot_gdrive.py     # メインプログラム
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
`auto_screenshot_gdrive.py`の定数を編集：
```python
INTERVAL_MINUTES = 5  # スクリーンショット間隔
GDRIVE_FOLDER_ID = "your-folder-id"  # アップロード先フォルダID
```

### 4. 従業員配布用ファイルの作成
```batch
# 一括準備スクリプトを実行（英語版）
prepare_for_employees_en.bat
```
1. パスワードを設定（従業員に通知する共通パスワード）
2. 自動的に暗号化とビルドが実行される
3. `dist/`フォルダに配布用ファイルが生成される

## 従業員への配布

### 配布ファイル
```
dist/
├── AutoScreenshotTool.exe    # 実行ファイル（credentials.enc埋め込み済み）
└── run_with_password.bat     # パスワード入力補助スクリプト
```

**重要**: `credentials.enc`は.exe内に埋め込まれているため、別途配布する必要はありません。

### 従業員の実行方法

#### 方法1: 簡単な起動（推奨）
1. `run_with_password.bat`をダブルクリック
2. 管理者から通知されたパスワードを入力
3. 自動的にツールが起動

#### 方法2: 環境変数設定（上級者向け）
1. 環境変数`SCREENSHOT_PASSWORD`にパスワードを設定
2. `AutoScreenshotTool.exe`を直接実行

#### 方法3: 直接実行
1. `AutoScreenshotTool.exe`をダブルクリック
2. コマンドプロンプトでパスワード入力

## ファイル構成

### 開発環境
```
ScreenShot/
├── auto_screenshot_gdrive.py     # メインプログラム
├── credential_manager.py         # 暗号化管理
├── service-account-key.json      # 認証情報（機密）
├── credentials.enc               # 暗号化済み認証情報
├── requirements.txt              # 依存パッケージ
├── prepare_for_employees_en.bat  # 配布準備スクリプト（英語版）
├── build_secure_en.bat          # セキュアビルド（英語版）
├── test/                        # テストスイート
│   ├── test_screenshot.py       # スクリーンショットテスト
│   ├── test_encryption.py       # 暗号化テスト
│   ├── test_log_rotation.py     # ログローテーションテスト
│   ├── test_api_auth.py        # API認証テスト
│   ├── test_upload.py          # アップロードテスト
│   └── run_all_tests.py        # 統合テスト実行
├── README.md                    # このファイル
├── README_Encryption.md         # 暗号化詳細ガイド
├── CLAUDE.md                   # AI開発支援用
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
- **命名規則**: `YYYYMMDD-ユーザー名.png`（JST時刻）
- **重複時**: `YYYYMMDD-ユーザー名_HHMMSS.png`

### 暗号化
- **アルゴリズム**: Fernet（AES-128）
- **鍵導出**: PBKDF2-SHA256（100,000回反復）
- **ソルト**: 16バイトランダム値

### ログ管理
- **最大サイズ**: 10MB
- **世代数**: 5世代
- **形式**: `[YYYY-MM-DD HH:MM:SS] レベル - メッセージ`

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
- 正しいパスワードを入力しているか確認
- 大文字小文字を区別します

#### アップロードエラー
- インターネット接続を確認
- `auto_screenshot.log`でエラー詳細を確認

### ログファイルの確認
```
[2024-01-25 10:30:00] INFO - スクリーンショット撮影開始
[2024-01-25 10:30:01] INFO - アップロード成功: 20240125-user.png
```

## セキュリティ

### 保護される情報
- Googleサービスアカウント認証情報
- APIアクセストークン
- アップロード先フォルダID

### セキュリティ対策
- 認証情報の暗号化（AES-128）
- パスワード保護による配布
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
# 暗号化済み配布用ビルド
build_secure_en.bat

# 開発用ビルド（暗号化なし）
pyinstaller --onefile --windowed --name "AutoScreenshotTool" auto_screenshot_gdrive.py
```

## ライセンス
内部使用専用ツール

## サポート
社内システム管理者まで連絡してください。

## 更新履歴
- v2.1: PyInstaller実行ファイル内の埋め込みcredentials.encパス解決を修正
- v2.0: マルチモニター対応、ログローテーション実装
- v1.5: パスワード暗号化方式に統一
- v1.0: 初回リリース
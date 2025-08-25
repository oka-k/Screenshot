# 自動スクリーンショットアップローダー (Googleドライブ連携版)

## 概要
このツールは、Windows PCで定期的にスクリーンショットを撮影し、自動的にGoogleドライブにアップロードするバックグラウンドアプリケーションです。

## セットアップ手順

### 1. Google Cloud Consoleでの準備

#### 1.1 プロジェクトの作成
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成（または既存のプロジェクトを選択）

#### 1.2 Google Drive APIの有効化
1. 左側メニューから「APIとサービス」→「ライブラリ」を選択
2. 「Google Drive API」を検索
3. 「有効にする」ボタンをクリック

#### 1.3 サービスアカウントの作成
1. 左側メニューから「APIとサービス」→「認証情報」を選択
2. 「+ 認証情報を作成」→「サービスアカウント」を選択
3. サービスアカウント名を入力（例：`screenshot-uploader`）
4. 「作成して続行」をクリック
5. ロールは「基本」→「編集者」または「Google Drive」→「ドライブファイルのアップロード」を選択
6. 「完了」をクリック

#### 1.4 サービスアカウントキーの取得
1. 作成したサービスアカウントをクリック
2. 「キー」タブを選択
3. 「鍵を追加」→「新しい鍵を作成」
4. 「JSON」を選択して「作成」
5. JSONファイルがダウンロードされる（重要：このファイルは再ダウンロードできません）

### 2. Googleドライブのフォルダ準備

#### 2.1 アップロード先フォルダの作成
1. [Google Drive](https://drive.google.com)にアクセス
2. スクリーンショット保存用のフォルダを作成（例：「Screenshots」）

#### 2.2 フォルダIDの取得
1. 作成したフォルダを開く
2. URLから以下の形式でフォルダIDを確認：
   ```
   https://drive.google.com/drive/folders/[ここがフォルダID]
   ```
   例：`1234567890abcdefghijklmnopqrstuv`

#### 2.3 サービスアカウントとフォルダの共有
1. フォルダを右クリック→「共有」を選択
2. サービスアカウントのメールアドレスを入力
   （形式：`サービスアカウント名@プロジェクトID.iam.gserviceaccount.com`）
3. 「編集者」権限を付与
4. 「送信」をクリック

### 3. アプリケーションの設定

#### 3.1 ファイルの配置
1. ダウンロードしたJSONキーファイルを `service-account-key.json` にリネーム
2. プロジェクトフォルダに配置

#### 3.2 設定の編集
`auto_screenshot_gdrive.py` を開いて以下を編集：

```python
# 撮影間隔（分）
INTERVAL_MINUTES = 5  # 必要に応じて変更

# Googleドライブ連携用設定
SERVICE_ACCOUNT_FILE = 'service-account-key.json'  # JSONファイル名
GDRIVE_FOLDER_ID = 'YOUR_FOLDER_ID_HERE'  # 取得したフォルダIDに置き換え
```

### 4. ビルドと実行

#### 4.1 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

#### 4.2 実行ファイルのビルド
```bash
build.bat
```
または手動で：
```bash
pyinstaller --onefile --windowed --name "AutoScreenshotTool" --add-data "service-account-key.json;." auto_screenshot_gdrive.py
```

#### 4.3 実行
- `dist\AutoScreenshotTool.exe` を実行
- バックグラウンドで動作開始
- `auto_screenshot.log` でログを確認可能

## 配布時の注意事項

### 従業員への配布方法
1. 以下のファイルをセットで配布：
   - `AutoScreenshotTool.exe`（ビルド済み実行ファイル）
   - 設定済みの `service-account-key.json`（機密情報として取り扱い）

2. **重要**: サービスアカウントキーは事前に実行ファイルに埋め込むか、安全な方法で配布

### セキュリティに関する注意
- `service-account-key.json` は機密情報です
- GitHubなどのパブリックリポジトリにアップロードしないでください
- `.gitignore` に追加することを推奨：
  ```
  service-account-key.json
  *.log
  dist/
  build/
  *.spec
  ```

## トラブルシューティング

### よくある問題と解決方法

#### 1. 「サービスアカウントファイルが見つかりません」エラー
- `service-account-key.json` がexeファイルと同じディレクトリにあることを確認
- ファイル名が正確であることを確認

#### 2. 「指定されたフォルダIDが見つかりません」エラー
- フォルダIDが正しいことを確認
- サービスアカウントがフォルダに対して編集権限を持っていることを確認

#### 3. アップロードが失敗する
- インターネット接続を確認
- プロキシ設定が必要な場合は、システム環境変数で設定

#### 4. スクリーンショットが撮影されない
- ウイルス対策ソフトがブロックしていないか確認
- Windows Defenderの例外設定に追加

### ログファイルの確認
問題が発生した場合は、`auto_screenshot.log` を確認してください。
このファイルには詳細なエラーメッセージが記録されています。

## システム要件
- Windows 10/11
- Python 3.9以上（開発時）
- インターネット接続（Googleドライブへのアクセス用）

## ライセンス
社内利用専用ツール
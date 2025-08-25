# テストスイート

## 概要
自動スクリーンショットツールの各機能をテストするためのテストコード集です。

## テストファイル

### 1. test_log_rotation.py
**ログローテーション機能のテスト**
- 小さいファイルはローテーションしない
- 10MB以上のファイルは自動ローテーション
- 複数世代の管理（最大5世代）
- 古いログファイルの自動削除

### 2. test_screenshot.py
**スクリーンショット撮影機能のテスト**
- プライマリモニターの撮影
- 全モニターを1枚に結合した撮影（mss使用）
- ファイル名生成の検証
- 画像サイズとフォーマットの確認

### 3. test_encryption.py
**暗号化機能のテスト**
- パスワードベースの暗号化・復号化
- 間違ったパスワードでのアクセス拒否
- 暗号化ファイルのサイズとフォーマット検証
- 鍵導出関数の再現性と一意性

## テストの実行方法

### すべてのテストを実行
```bash
cd test
python run_all_tests.py
```

### 個別テストの実行
```bash
# ログローテーションのみ
python test_log_rotation.py

# スクリーンショットのみ
python test_screenshot.py

# 暗号化のみ
python test_encryption.py
```

## 必要な環境

### 必須パッケージ
```bash
pip install -r ../requirements.txt
```

### Python バージョン
- Python 3.9以上（zoneinfoモジュール使用）

## テスト結果の見方

### 成功時
```
✅ テスト名 - 成功
```

### 失敗時
```
❌ テスト名 - 失敗
エラー: エラーメッセージ
```

## 注意事項

1. **スクリーンショットテスト**
   - 実際に画面を撮影するため、実行環境にディスプレイが必要
   - リモート環境では失敗する可能性あり

2. **ログローテーションテスト**
   - 一時的に大きなファイル（約11MB）を作成
   - テスト後は自動的にクリーンアップ

3. **暗号化テスト**
   - 一時ディレクトリに暗号化ファイルを作成
   - テスト後は自動的に削除

## トラブルシューティング

### ImportError が発生する場合
```bash
# 親ディレクトリから実行
cd ..
python -m test.run_all_tests
```

### mss関連のエラー
```bash
pip install mss
```

### tzdata関連のエラー
```bash
pip install tzdata
```

## 継続的インテグレーション（CI）での使用

GitHub ActionsやJenkinsなどのCIツールで使用する場合：

```yaml
# .github/workflows/test.yml の例
- name: Run tests
  run: |
    pip install -r requirements.txt
    python test/run_all_tests.py
```

## 開発者向け情報

新しいテストを追加する場合：

1. `test_機能名.py` ファイルを作成
2. テスト関数を実装
3. `run_all_tests.py` にインポートと登録を追加

```python
# run_all_tests.py に追加
import test_new_feature

tests = [
    # 既存のテスト...
    ("新機能", test_new_feature.test_function),
]
```
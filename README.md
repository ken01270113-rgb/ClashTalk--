# 討論SNSアプリ

「討論」をテーマにしたSNS型Webアプリケーションです。ユーザーは様々な議題について賛成・反対に分かれ、自分の意見を投稿し、他者と議論することができます。

## 概要

このプロジェクトはDjangoとSQLiteを使用して構築されており、将来的なPostgreSQLへの移行やログイン機能の追加を見据えた拡張性の高い設計になっています。
モダンで直感的なUI（ダークモード対応）を備え、スマートフォンやPCのどちらからでも快適に利用できるレスポンシブデザインを採用しています。

## 主な機能

- **討論の作成**: タイトル、説明、カテゴリー、賛成/反対のカスタム名称を設定して新しい討論を作成できます。
- **意見の投稿**: 賛成または反対の立場を選んで意見を投稿できます（匿名投稿も可能）。
- **コメント機能**: 他のユーザーの投稿に対してコメント（返信）を付けることができます。
- **いいね機能**: 共感した投稿に「いいね」をつけることができます（セッションベースで重複防止）。
- **ランキング機能**: 投稿数、いいね数、コメント数を総合したスコアに基づいて人気討論をランキング表示します。
- **検索・カテゴリー**: キーワード検索やカテゴリーによる絞り込みが可能です。
- **ダークモード対応**: 画面右上の🌙/☀️ボタンでテーマを切り替えられます。

## 技術スタック

- **バックエンド**: Python 3.11, Django 5.0
- **データベース**: SQLite3（開発用、将来のPostgreSQL移行を想定した設計）
- **フロントエンド**: HTML5, CSS3, Vanilla JavaScript
- **デザイン**: カスタムCSS（モダンUI、レスポンシブ、ダークモード対応）

## セットアップと実行方法

### 前提条件
- Python 3.10以上
- pip (Pythonパッケージマネージャー)

### 1. リポジトリのクローンと移動
```bash
git clone <repository-url>
cd toron_project
```

### 2. 必要なパッケージのインストール
```bash
pip install -r requirements.txt
```
※ `requirements.txt` がない場合は以下のコマンドを実行してください。
```bash
pip install django django-crispy-forms pillow
```

### 3. マイグレーションの実行
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 初期データの投入（オプション）
カテゴリーやサンプルの討論データを投入する場合は以下のコマンドを実行します。
```bash
python manage.py seed_data
```

### 5. 開発サーバーの起動
```bash
python manage.py runserver
```

ブラウザで `http://localhost:8000` または `http://127.0.0.1:8000` にアクセスするとアプリを利用できます。

## ディレクトリ構成

```text
toron_project/
├── manage.py               # Django管理スクリプト
├── README.md               # このファイル
├── toron_project/          # プロジェクト設定ディレクトリ
│   ├── settings.py         # 全体設定（DB, インストールアプリ等）
│   ├── urls.py             # プロジェクト全体のURLルーティング
│   └── ...
├── core/                   # 共通機能用アプリ（将来拡張用）
├── debates/                # 討論機能メインアプリ
│   ├── models.py           # データモデル（Debate, Post, Comment, Like, Category）
│   ├── views.py            # ビュー関数（ビジネスロジック）
│   ├── urls.py             # アプリ内URLルーティング
│   ├── forms.py            # フォーム定義
│   ├── admin.py            # 管理画面設定
│   └── management/         # カスタムコマンド（seed_data等）
├── static/                 # 静的ファイル（CSS, JS, 画像）
│   ├── css/
│   │   └── main.css        # メインスタイルシート
│   └── js/
│   │   └── main.js         # メインJavaScript
└── templates/              # HTMLテンプレート
    ├── base.html           # 共通レイアウト
    └── debates/            # 討論機能用テンプレート
        ├── home.html       # ホーム画面
        ├── detail.html     # 討論詳細画面
        ├── create.html     # 討論作成画面
        └── ...
```

## セキュリティ対策

Djangoの標準機能を利用して以下のセキュリティ対策を実施しています。
- **XSS対策**: テンプレートエンジンによる自動エスケープ
- **CSRF対策**: フォーム送信時のCSRFトークン検証 (`{% csrf_token %}`)
- **SQLインジェクション対策**: Django ORM/クエリビルダの使用による自動パラメータ化

## 将来の拡張性について

このプロジェクトは以下の機能追加を容易に行えるよう設計されています。

1. **ログイン機能・ユーザー認証**: `User` モデルとの連携（現在はセッションベース）
2. **PostgreSQLへの移行**: `settings.py` の `DATABASES` 設定を変更するだけで移行可能
3. **AI機能の統合**: 各ビュー関数内でAI API（OpenAI等）を呼び出して要約やモデレーションを追加可能
4. **管理者機能**: 既にDjango Admin (`/admin/`) が設定されており、モデレーションが可能

## ライセンス

This project is licensed under the MIT License.

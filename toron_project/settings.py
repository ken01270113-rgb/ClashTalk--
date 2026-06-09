"""
討論SNS - Django設定ファイル
将来的なPostgreSQL移行・スケールアップを考慮した設計
"""

import os
from pathlib import Path

# プロジェクトのベースディレクトリ
BASE_DIR = Path(__file__).resolve().parent.parent

# セキュリティキー（本番環境では環境変数から取得すること）
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-toron-sns-dev-key-change-in-production-xyz123'
)

# デバッグモード（本番環境ではFalseに設定）
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')

# CSRF信頼済みオリジン（プロキシ経由のアクセスに対応）
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'DJANGO_CSRF_TRUSTED_ORIGINS',
    'http://localhost:8000,http://127.0.0.1:8000'
).split(',')
# 開発環境ではワイルドカード対応
if DEBUG:
    CSRF_TRUSTED_ORIGINS += [
        'https://*.manus.computer',
        'https://*.sg1.manus.computer',
    ]

# インストール済みアプリ
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 独自アプリ
    'debates.apps.DebatesConfig',
    'core.apps.CoreConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'toron_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # カスタムコンテキストプロセッサ（カテゴリー等のグローバル情報）
                'debates.context_processors.global_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'toron_project.wsgi.application'

# データベース設定（SQLite / 将来的にPostgreSQLへ移行可能な設計）
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DB_NAME', str(BASE_DIR / 'db.sqlite3')),
    }
}

# パスワードバリデーション
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 国際化設定
LANGUAGE_CODE = 'ja'
TIME_ZONE = 'Asia/Tokyo'
USE_I18N = True
USE_TZ = True

# 静的ファイル設定
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# メディアファイル設定
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# デフォルトの主キーフィールド
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# セッション設定
SESSION_COOKIE_AGE = 86400 * 30  # 30日
SESSION_SAVE_EVERY_REQUEST = True

# セキュリティ設定（本番環境用）
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# ページネーション設定
DEBATES_PER_PAGE = 10
POSTS_PER_PAGE = 20
COMMENTS_PER_PAGE = 20

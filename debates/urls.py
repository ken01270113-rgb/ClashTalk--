"""
討論SNS - URLパターン定義
"""

from django.urls import path
from . import views

app_name = 'debates'

urlpatterns = [
    # ホーム
    path('', views.home, name='home'),
    # 討論作成
    path('create/', views.debate_create, name='create'),
    # 討論詳細
    path('<int:pk>/', views.debate_detail, name='detail'),
    # 投稿作成（AJAX対応）
    path('<int:debate_pk>/post/', views.post_create, name='post_create'),
    # コメント作成（AJAX対応）
    path('post/<int:post_pk>/comment/', views.comment_create, name='comment_create'),
    # いいねトグル（AJAX専用）
    path('post/<int:post_pk>/like/', views.like_toggle, name='like_toggle'),
    # カテゴリー別一覧
    path('category/<slug:slug>/', views.category_debates, name='category'),
    # 検索
    path('search/', views.search, name='search'),
    # ランキング
    path('ranking/', views.ranking, name='ranking'),
]

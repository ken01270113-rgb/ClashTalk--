"""
討論SNS - グローバルコンテキストプロセッサ
全テンプレートで使用するデータを提供する
"""

from .models import Category


def global_context(request):
    """全テンプレートに渡すグローバルコンテキスト"""
    categories = Category.objects.all().order_by('order', 'name')
    return {
        'global_categories': categories,
    }

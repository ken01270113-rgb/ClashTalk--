"""
討論SNS - データモデル定義
将来的なログイン機能・フォロー・通知・タグ機能の追加を考慮した設計
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class Category(models.Model):
    """カテゴリーモデル"""
    name = models.CharField('カテゴリー名', max_length=50, unique=True)
    slug = models.SlugField('スラッグ', max_length=50, unique=True)
    icon = models.CharField('アイコン（絵文字）', max_length=10, default='💬')
    description = models.TextField('説明', blank=True)
    order = models.PositiveIntegerField('表示順', default=0)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)

    class Meta:
        verbose_name = 'カテゴリー'
        verbose_name_plural = 'カテゴリー'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('debates:category', kwargs={'slug': self.slug})


class Debate(models.Model):
    """討論モデル"""
    title = models.CharField('タイトル', max_length=200)
    description = models.TextField('説明')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='debates',
        verbose_name='カテゴリー'
    )
    pro_label = models.CharField('賛成側名称', max_length=50, default='賛成')
    con_label = models.CharField('反対側名称', max_length=50, default='反対')
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='debates',
        verbose_name='作成者'
    )
    session_key = models.CharField('セッションキー', max_length=40, blank=True)
    author_name = models.CharField('投稿者名', max_length=50, default='匿名')
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    is_active = models.BooleanField('公開中', default=True)

    class Meta:
        verbose_name = '討論'
        verbose_name_plural = '討論'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('debates:detail', kwargs={'pk': self.pk})

    @property
    def pro_posts(self):
        return self.posts.filter(side='pro', is_active=True)

    @property
    def con_posts(self):
        return self.posts.filter(side='con', is_active=True)

    @property
    def total_posts(self):
        return self.posts.filter(is_active=True).count()

    @property
    def total_likes(self):
        return Like.objects.filter(post__debate=self).count()

    @property
    def total_comments(self):
        return Comment.objects.filter(post__debate=self, is_active=True).count()

    @property
    def popularity_score(self):
        return self.total_posts + self.total_likes * 2 + self.total_comments * 1.5


class Post(models.Model):
    """投稿モデル（賛成・反対の意見）"""
    SIDE_CHOICES = [
        ('pro', '賛成'),
        ('con', '反対'),
    ]

    debate = models.ForeignKey(
        Debate,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='討論'
    )
    content = models.TextField('内容', max_length=1000)
    side = models.CharField('立場', max_length=3, choices=SIDE_CHOICES)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='投稿者'
    )
    session_key = models.CharField('セッションキー', max_length=40, blank=True)
    author_name = models.CharField('投稿者名', max_length=50, default='匿名')
    created_at = models.DateTimeField('投稿日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    is_active = models.BooleanField('公開中', default=True)

    class Meta:
        verbose_name = '投稿'
        verbose_name_plural = '投稿'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['debate', 'side']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f'{self.debate.title} - {self.get_side_display()} - {self.content[:30]}'

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.filter(parent=None, is_active=True).count()

    @property
    def all_comments_count(self):
        return self.comments.filter(is_active=True).count()


class Comment(models.Model):
    """コメントモデル（ツリー構造対応）"""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='投稿'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='親コメント'
    )
    content = models.TextField('内容', max_length=500)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comments',
        verbose_name='投稿者'
    )
    session_key = models.CharField('セッションキー', max_length=40, blank=True)
    author_name = models.CharField('投稿者名', max_length=50, default='匿名')
    created_at = models.DateTimeField('投稿日時', auto_now_add=True)
    is_active = models.BooleanField('公開中', default=True)

    class Meta:
        verbose_name = 'コメント'
        verbose_name_plural = 'コメント'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'parent']),
        ]

    def __str__(self):
        return f'コメント: {self.content[:30]}'


class Like(models.Model):
    """いいねモデル（セッションベース）"""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='投稿'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='likes',
        verbose_name='ユーザー'
    )
    session_key = models.CharField('セッションキー', max_length=40)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)

    class Meta:
        verbose_name = 'いいね'
        verbose_name_plural = 'いいね'
        unique_together = [['post', 'session_key']]
        indexes = [
            models.Index(fields=['post', 'session_key']),
        ]

    def __str__(self):
        return f'{self.post} へのいいね'

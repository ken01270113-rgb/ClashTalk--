"""
討論SNS - Django管理画面設定
"""

from django.contrib import admin
from .models import Category, Debate, Post, Comment, Like


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'slug', 'order', 'debate_count']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def debate_count(self, obj):
        return obj.debates.filter(is_active=True).count()
    debate_count.short_description = '討論数'


class PostInline(admin.TabularInline):
    model = Post
    extra = 0
    fields = ['side', 'content', 'author_name', 'is_active']


@admin.register(Debate)
class DebateAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author_name', 'total_posts_count', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'author_name']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PostInline]

    def total_posts_count(self, obj):
        return obj.total_posts
    total_posts_count.short_description = '投稿数'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['debate', 'side', 'author_name', 'get_likes_count', 'is_active', 'created_at']
    list_filter = ['side', 'is_active', 'created_at']
    search_fields = ['content', 'author_name', 'debate__title']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']

    def get_likes_count(self, obj):
        return obj.likes_count
    get_likes_count.short_description = 'いいね数'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author_name', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['content', 'author_name']
    list_editable = ['is_active']
    readonly_fields = ['created_at']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['post', 'session_key', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at']

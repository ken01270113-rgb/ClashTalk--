"""
討論SNS - ビュー定義
ホーム・討論詳細・作成・投稿・コメント・いいね・検索機能を実装
"""

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator

from .models import Category, Debate, Post, Comment, Like
from .forms import DebateCreateForm, PostCreateForm, CommentCreateForm, SearchForm


def get_or_create_session_key(request):
    """セッションキーを取得または作成する"""
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def home(request):
    """ホーム画面ビュー"""
    search_form = SearchForm(request.GET)
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')
    sort = request.GET.get('sort', 'new')

    debates = Debate.objects.filter(is_active=True).select_related('category')

    selected_category = None
    if category_slug:
        try:
            selected_category = Category.objects.get(slug=category_slug)
            debates = debates.filter(category=selected_category)
        except Category.DoesNotExist:
            pass

    if query:
        debates = debates.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    debates = apply_sort(debates, sort)

    paginator = Paginator(debates, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    latest_debates = Debate.objects.filter(is_active=True).select_related('category').order_by('-created_at')[:8]
    popular_debates = get_popular_debates(10)
    categories = Category.objects.all().order_by('order', 'name')

    context = {
        'page_obj': page_obj,
        'latest_debates': latest_debates,
        'popular_debates': popular_debates,
        'categories': categories,
        'selected_category': selected_category,
        'search_form': search_form,
        'query': query,
        'sort': sort,
    }
    return render(request, 'debates/home.html', context)


def get_popular_debates(limit=10):
    """人気討論を取得する"""
    debates = list(Debate.objects.filter(is_active=True).select_related('category'))
    scored = []
    for d in debates:
        score = d.total_posts + d.total_likes * 2 + d.total_comments * 1.5
        scored.append((score, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:limit]]


def apply_sort(debates, sort):
    """並び替えを適用する"""
    if sort == 'popular':
        return debates.annotate(post_count=Count('posts')).order_by('-post_count', '-created_at')
    elif sort == 'comments':
        return debates.annotate(
            comment_count=Count('posts__comments')
        ).order_by('-comment_count', '-created_at')
    elif sort == 'likes':
        return debates.annotate(
            like_count=Count('posts__likes')
        ).order_by('-like_count', '-created_at')
    else:
        return debates.order_by('-created_at')


def debate_detail(request, pk):
    """討論詳細画面ビュー"""
    debate = get_object_or_404(Debate, pk=pk, is_active=True)
    session_key = get_or_create_session_key(request)

    post_form = PostCreateForm()
    sort = request.GET.get('sort', 'new')

    pro_posts = debate.posts.filter(side='pro', is_active=True).prefetch_related('likes', 'comments')
    con_posts = debate.posts.filter(side='con', is_active=True).prefetch_related('likes', 'comments')

    if sort == 'likes':
        pro_posts = pro_posts.annotate(like_count=Count('likes')).order_by('-like_count', '-created_at')
        con_posts = con_posts.annotate(like_count=Count('likes')).order_by('-like_count', '-created_at')
    else:
        pro_posts = pro_posts.order_by('-created_at')
        con_posts = con_posts.order_by('-created_at')

    liked_post_ids = set(
        Like.objects.filter(session_key=session_key).values_list('post_id', flat=True)
    )

    pro_posts_with_comments = []
    for post in pro_posts:
        root_comments = post.comments.filter(parent=None, is_active=True).prefetch_related('replies')
        pro_posts_with_comments.append({
            'post': post,
            'root_comments': root_comments,
            'comment_form': CommentCreateForm(),
            'liked': post.pk in liked_post_ids,
        })

    con_posts_with_comments = []
    for post in con_posts:
        root_comments = post.comments.filter(parent=None, is_active=True).prefetch_related('replies')
        con_posts_with_comments.append({
            'post': post,
            'root_comments': root_comments,
            'comment_form': CommentCreateForm(),
            'liked': post.pk in liked_post_ids,
        })

    related_debates = []
    if debate.category:
        related_debates = Debate.objects.filter(
            category=debate.category,
            is_active=True
        ).exclude(pk=pk).order_by('-created_at')[:5]

    context = {
        'debate': debate,
        'post_form': post_form,
        'pro_posts_with_comments': pro_posts_with_comments,
        'con_posts_with_comments': con_posts_with_comments,
        'related_debates': related_debates,
        'sort': sort,
        'pro_count': pro_posts.count(),
        'con_count': con_posts.count(),
        'liked_post_ids': list(liked_post_ids),
    }
    return render(request, 'debates/detail.html', context)


def debate_create(request):
    """討論作成ビュー"""
    if request.method == 'POST':
        form = DebateCreateForm(request.POST)
        if form.is_valid():
            debate = form.save(commit=False)
            debate.session_key = get_or_create_session_key(request)
            debate.author_name = request.POST.get('author_name', '匿名').strip() or '匿名'
            if not debate.pro_label:
                debate.pro_label = '賛成'
            if not debate.con_label:
                debate.con_label = '反対'
            debate.save()
            messages.success(request, f'討論「{debate.title}」を作成しました！')
            return redirect('debates:detail', pk=debate.pk)
        else:
            messages.error(request, '入力内容に誤りがあります。確認してください。')
    else:
        form = DebateCreateForm()

    categories = Category.objects.all().order_by('order', 'name')
    context = {
        'form': form,
        'categories': categories,
    }
    return render(request, 'debates/create.html', context)


@require_POST
def post_create(request, debate_pk):
    """投稿作成ビュー（AJAX対応）"""
    debate = get_object_or_404(Debate, pk=debate_pk, is_active=True)
    form = PostCreateForm(request.POST)

    if form.is_valid():
        post = form.save(commit=False)
        post.debate = debate
        post.session_key = get_or_create_session_key(request)
        post.author_name = request.POST.get('author_name', '匿名').strip() or '匿名'
        post.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'post': {
                    'id': post.pk,
                    'content': post.content,
                    'side': post.side,
                    'author_name': post.author_name,
                    'created_at': post.created_at.strftime('%Y年%m月%d日 %H:%M'),
                    'likes_count': 0,
                }
            })
        messages.success(request, '意見を投稿しました！')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        messages.error(request, '投稿に失敗しました。入力内容を確認してください。')

    return redirect('debates:detail', pk=debate_pk)


@require_POST
def comment_create(request, post_pk):
    """コメント作成ビュー（AJAX対応）"""
    post = get_object_or_404(Post, pk=post_pk, is_active=True)
    form = CommentCreateForm(request.POST)
    parent_id = request.POST.get('parent_id')

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.session_key = get_or_create_session_key(request)
        comment.author_name = request.POST.get('author_name', '匿名').strip() or '匿名'

        if parent_id:
            try:
                parent_comment = Comment.objects.get(pk=parent_id, post=post, is_active=True)
                comment.parent = parent_comment
            except Comment.DoesNotExist:
                pass

        comment.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'comment': {
                    'id': comment.pk,
                    'content': comment.content,
                    'author_name': comment.author_name,
                    'created_at': comment.created_at.strftime('%Y年%m月%d日 %H:%M'),
                    'parent_id': comment.parent_id,
                }
            })
        messages.success(request, 'コメントを投稿しました！')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        messages.error(request, 'コメントの投稿に失敗しました。')

    return redirect('debates:detail', pk=post.debate_id)


@require_POST
def like_toggle(request, post_pk):
    """いいねのトグル（AJAX専用）"""
    post = get_object_or_404(Post, pk=post_pk, is_active=True)
    session_key = get_or_create_session_key(request)

    like, created = Like.objects.get_or_create(
        post=post,
        session_key=session_key,
    )

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        'success': True,
        'liked': liked,
        'likes_count': post.likes_count,
    })


def category_debates(request, slug):
    """カテゴリー別討論一覧ビュー"""
    category = get_object_or_404(Category, slug=slug)
    sort = request.GET.get('sort', 'new')
    debates = Debate.objects.filter(category=category, is_active=True).select_related('category')
    debates = apply_sort(debates, sort)

    paginator = Paginator(debates, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj,
        'sort': sort,
    }
    return render(request, 'debates/category.html', context)


def search(request):
    """検索ビュー"""
    form = SearchForm(request.GET)
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')
    sort = request.GET.get('sort', 'new')

    debates = Debate.objects.filter(is_active=True).select_related('category')

    selected_category = None
    if category_slug:
        try:
            selected_category = Category.objects.get(slug=category_slug)
            debates = debates.filter(category=selected_category)
        except Category.DoesNotExist:
            pass

    if query:
        debates = debates.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    debates = apply_sort(debates, sort)

    paginator = Paginator(debates, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'page_obj': page_obj,
        'query': query,
        'selected_category': selected_category,
        'sort': sort,
        'result_count': paginator.count,
    }
    return render(request, 'debates/search.html', context)


def ranking(request):
    """ランキングビュー"""
    popular_debates = get_popular_debates(10)
    context = {
        'popular_debates': popular_debates,
    }
    return render(request, 'debates/ranking.html', context)

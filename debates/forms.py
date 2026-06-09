"""
討論SNS - フォーム定義
入力バリデーションとセキュリティを考慮した設計
"""

from django import forms
from .models import Debate, Post, Comment


class DebateCreateForm(forms.ModelForm):
    """討論作成フォーム"""

    class Meta:
        model = Debate
        fields = ['title', 'description', 'category', 'pro_label', 'con_label']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例：制服は必要か',
                'maxlength': 200,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '討論の背景や詳細を入力してください',
                'rows': 4,
                'maxlength': 2000,
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'pro_label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例：必要（省略可）',
                'maxlength': 50,
            }),
            'con_label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例：不要（省略可）',
                'maxlength': 50,
            }),
        }
        labels = {
            'title': 'タイトル',
            'description': '説明',
            'category': 'カテゴリー',
            'pro_label': '賛成側の名称',
            'con_label': '反対側の名称',
        }
        help_texts = {
            'title': '討論のテーマを簡潔に入力してください（最大200文字）',
            'description': '討論の背景や詳細を入力してください',
            'pro_label': '省略した場合は「賛成」と表示されます',
            'con_label': '省略した場合は「反対」と表示されます',
        }

    def clean_title(self):
        """タイトルのバリデーション"""
        title = self.cleaned_data.get('title', '').strip()
        if len(title) < 2:
            raise forms.ValidationError('タイトルは2文字以上で入力してください。')
        return title

    def clean_description(self):
        """説明のバリデーション"""
        description = self.cleaned_data.get('description', '').strip()
        if len(description) < 10:
            raise forms.ValidationError('説明は10文字以上で入力してください。')
        return description


class PostCreateForm(forms.ModelForm):
    """投稿フォーム"""
    SIDE_CHOICES = [
        ('pro', '👍 賛成'),
        ('con', '👎 反対'),
    ]

    side = forms.ChoiceField(
        choices=SIDE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'side-radio'}),
        label='立場を選択',
    )

    class Meta:
        model = Post
        fields = ['content', 'side']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'あなたの意見を書いてください',
                'rows': 3,
                'maxlength': 1000,
            }),
        }
        labels = {
            'content': '意見',
        }

    def clean_content(self):
        """投稿内容のバリデーション"""
        content = self.cleaned_data.get('content', '').strip()
        if len(content) < 5:
            raise forms.ValidationError('意見は5文字以上で入力してください。')
        return content


class CommentCreateForm(forms.ModelForm):
    """コメントフォーム"""

    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control comment-input',
                'placeholder': 'コメントを入力してください',
                'rows': 2,
                'maxlength': 500,
            }),
        }
        labels = {
            'content': 'コメント',
        }

    def clean_content(self):
        """コメント内容のバリデーション"""
        content = self.cleaned_data.get('content', '').strip()
        if len(content) < 2:
            raise forms.ValidationError('コメントは2文字以上で入力してください。')
        return content


class SearchForm(forms.Form):
    """検索フォーム"""
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'search-input',
            'placeholder': '討論を検索...',
            'autocomplete': 'off',
        }),
        label='キーワード',
    )
    category = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ('new', '新着順'),
            ('popular', '人気順'),
            ('comments', 'コメント数順'),
            ('likes', 'いいね順'),
        ],
        initial='new',
        widget=forms.Select(attrs={'class': 'sort-select'}),
        label='並び替え',
    )

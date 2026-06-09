"""
討論SNS - 初期データ投入コマンド
python manage.py seed_data で実行
"""

from django.core.management.base import BaseCommand
from debates.models import Category, Debate, Post, Comment, Like


CATEGORIES = [
    {'name': '政治', 'slug': 'politics', 'icon': '🏛️', 'order': 1},
    {'name': '教育', 'slug': 'education', 'icon': '📚', 'order': 2},
    {'name': 'スポーツ', 'slug': 'sports', 'icon': '⚽', 'order': 3},
    {'name': '科学', 'slug': 'science', 'icon': '🔬', 'order': 4},
    {'name': 'AI', 'slug': 'ai', 'icon': '🤖', 'order': 5},
    {'name': 'ゲーム', 'slug': 'game', 'icon': '🎮', 'order': 6},
    {'name': 'アニメ', 'slug': 'anime', 'icon': '🎌', 'order': 7},
    {'name': '日常', 'slug': 'daily', 'icon': '☀️', 'order': 8},
    {'name': 'その他', 'slug': 'other', 'icon': '💬', 'order': 9},
]

DEBATES_DATA = [
    {
        'title': '制服は必要か',
        'description': '学校における制服の必要性について議論しましょう。制服が生徒の学習意欲や規律に与える影響、個性の表現との兼ね合いなど、様々な観点から考えてみてください。',
        'category_slug': 'education',
        'pro_label': '必要',
        'con_label': '不要',
        'posts': [
            {'side': 'pro', 'content': '制服は学校への帰属意識を高め、経済的格差を見えにくくする効果があります。毎朝服を選ぶ時間が省けるのも大きなメリットです。', 'author_name': '教育者A'},
            {'side': 'pro', 'content': '制服があることで、学校の外でも生徒としての自覚が生まれ、問題行動の抑制につながると思います。', 'author_name': '保護者B'},
            {'side': 'con', 'content': '個性を表現する自由は重要です。服装の自由化は自己表現力を育て、社会に出てからの判断力にもつながります。', 'author_name': '学生C'},
            {'side': 'con', 'content': '制服の購入費用は決して安くありません。経済的負担を考えると、私服の方が合理的ではないでしょうか。', 'author_name': '保護者D'},
        ]
    },
    {
        'title': 'AIは人間の仕事を奪うか',
        'description': '人工知能の急速な発展により、多くの職業が自動化されると言われています。AIは本当に人間の仕事を奪うのか、それとも新たな雇用を生み出すのか議論しましょう。',
        'category_slug': 'ai',
        'pro_label': '奪う',
        'con_label': '奪わない',
        'posts': [
            {'side': 'pro', 'content': '既に多くの工場でロボットが人間の代わりに働いています。AIの進化でホワイトカラーの仕事も置き換えられるのは時間の問題です。', 'author_name': '経済学者X'},
            {'side': 'pro', 'content': 'ChatGPTなどのAIはライティング、コーディング、デザインなど多くの分野で人間を超えつつあります。雇用への影響は避けられません。', 'author_name': 'エンジニアY'},
            {'side': 'con', 'content': '産業革命でも同じ議論がありましたが、新技術は新たな雇用を生み出しました。AIも同様に新しい職業を創出するでしょう。', 'author_name': '歴史家Z'},
            {'side': 'con', 'content': 'AIが得意なのはパターン認識です。創造性・共感・倫理的判断が必要な仕事はまだまだ人間にしかできません。', 'author_name': '哲学者W'},
        ]
    },
    {
        'title': 'プロ野球とJリーグ、どちらが面白いか',
        'description': '日本の二大プロスポーツ、野球とサッカー。どちらがより面白く、応援しがいがあるか議論しましょう。',
        'category_slug': 'sports',
        'pro_label': 'プロ野球',
        'con_label': 'Jリーグ',
        'posts': [
            {'side': 'pro', 'content': '野球は戦略の奥深さが魅力です。投手と打者の心理戦、守備のシフト、サインプレーなど見どころが満載です。', 'author_name': '野球ファン'},
            {'side': 'con', 'content': 'サッカーは90分間ずっと動き続ける躍動感があります。世界中でプレーされているスポーツの普遍的な魅力があります。', 'author_name': 'サッカーファン'},
        ]
    },
    {
        'title': '週4日勤務制は導入すべきか',
        'description': '一部の企業や国で試験導入されている週4日勤務制。生産性向上やワークライフバランスの観点から、日本でも導入すべきか議論しましょう。',
        'category_slug': 'daily',
        'pro_label': '導入すべき',
        'con_label': '不要',
        'posts': [
            {'side': 'pro', 'content': 'アイスランドやマイクロソフトの実験では生産性が向上したという結果が出ています。休息が創造性と集中力を高めます。', 'author_name': '人事担当者'},
            {'side': 'pro', 'content': '週4日勤務で子育てや介護との両立がしやすくなります。少子化対策としても有効ではないでしょうか。', 'author_name': '子育て中の親'},
            {'side': 'con', 'content': '業種によっては週4日では業務が回りません。サービス業や医療など、休めない仕事もあります。', 'author_name': '経営者'},
        ]
    },
    {
        'title': 'ゲームは子どもに悪影響か',
        'description': 'ビデオゲームが子どもの発達に与える影響について議論しましょう。暴力性や依存性の問題と、認知能力向上や社会性育成の効果、どちらが大きいでしょうか。',
        'category_slug': 'game',
        'pro_label': '悪影響あり',
        'con_label': '悪影響なし',
        'posts': [
            {'side': 'pro', 'content': '長時間のゲームは睡眠不足や視力低下を招きます。また、暴力的なゲームが攻撃性を高めるという研究もあります。', 'author_name': '小児科医'},
            {'side': 'con', 'content': 'ゲームは問題解決能力や空間認識能力を鍛えます。マインクラフトのような創造的なゲームは教育にも活用されています。', 'author_name': 'ゲーム研究者'},
            {'side': 'con', 'content': 'オンラインゲームを通じて世界中の人とコミュニケーションを取り、友人を作ることができます。社会性の育成に役立ちます。', 'author_name': 'ゲーマー'},
        ]
    },
]


class Command(BaseCommand):
    help = '初期データを投入します'

    def handle(self, *args, **options):
        self.stdout.write('カテゴリーを作成中...')
        category_map = {}
        for cat_data in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'icon': cat_data['icon'],
                    'order': cat_data['order'],
                }
            )
            category_map[cat_data['slug']] = cat
            if created:
                self.stdout.write(f'  カテゴリー作成: {cat.name}')

        self.stdout.write('討論データを作成中...')
        for debate_data in DEBATES_DATA:
            if Debate.objects.filter(title=debate_data['title']).exists():
                self.stdout.write(f'  スキップ（既存）: {debate_data["title"]}')
                continue

            category = category_map.get(debate_data['category_slug'])
            debate = Debate.objects.create(
                title=debate_data['title'],
                description=debate_data['description'],
                category=category,
                pro_label=debate_data['pro_label'],
                con_label=debate_data['con_label'],
                session_key='seed_data',
                author_name='管理者',
            )

            for post_data in debate_data.get('posts', []):
                Post.objects.create(
                    debate=debate,
                    content=post_data['content'],
                    side=post_data['side'],
                    session_key='seed_data',
                    author_name=post_data['author_name'],
                )

            self.stdout.write(f'  討論作成: {debate.title}')

        self.stdout.write(self.style.SUCCESS('初期データの投入が完了しました！'))

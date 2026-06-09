/**
 * 討論SNS - メインJavaScript
 * いいね・コメント・ダークモード・アニメーション等の実装
 */

'use strict';

// ===================================================
// DOMContentLoaded 後に初期化
// ===================================================
document.addEventListener('DOMContentLoaded', function () {
  initTheme();
  initHamburgerMenu();
  initLikeButtons();
  initCommentForms();
  initCommentToggles();
  initCharCounters();
  initMessages();
  initSideSelector();
  initSearchForm();
  initAnimations();
});

// ===================================================
// ダークモード切替
// ===================================================
function initTheme() {
  const toggle = document.getElementById('theme-toggle');
  if (!toggle) return;

  const saved = localStorage.getItem('theme') || 'light';
  applyTheme(saved);

  toggle.addEventListener('click', function () {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    localStorage.setItem('theme', next);
  });
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  const toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    toggle.title = theme === 'dark' ? 'ライトモードに切替' : 'ダークモードに切替';
  }
}

// ===================================================
// ハンバーガーメニュー
// ===================================================
function initHamburgerMenu() {
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobile-menu');
  if (!hamburger || !mobileMenu) return;

  hamburger.addEventListener('click', function () {
    hamburger.classList.toggle('active');
    mobileMenu.classList.toggle('open');
  });

  // メニュー外クリックで閉じる
  document.addEventListener('click', function (e) {
    if (!hamburger.contains(e.target) && !mobileMenu.contains(e.target)) {
      hamburger.classList.remove('active');
      mobileMenu.classList.remove('open');
    }
  });
}

// ===================================================
// いいねボタン（AJAX）
// ===================================================
function initLikeButtons() {
  document.addEventListener('click', function (e) {
    const btn = e.target.closest('.like-btn');
    if (!btn) return;

    const postId = btn.dataset.postId;
    if (!postId) return;

    // 連打防止
    if (btn.disabled) return;
    btn.disabled = true;

    const csrfToken = getCsrfToken();
    const url = `/post/${postId}/like/`;

    fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json',
      },
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          // いいね状態を更新
          btn.classList.toggle('liked', data.liked);
          const countEl = btn.querySelector('.like-count');
          if (countEl) {
            countEl.textContent = data.likes_count;
          }
          // アニメーション
          btn.classList.add('animate-pulse');
          setTimeout(() => btn.classList.remove('animate-pulse'), 300);
        }
      })
      .catch(err => {
        console.error('いいねエラー:', err);
      })
      .finally(() => {
        btn.disabled = false;
      });
  });
}

// ===================================================
// コメントフォーム（AJAX）
// ===================================================
function initCommentForms() {
  document.addEventListener('submit', function (e) {
    const form = e.target.closest('.comment-form-ajax');
    if (!form) return;

    e.preventDefault();

    const postId = form.dataset.postId;
    const textarea = form.querySelector('textarea');
    const content = textarea ? textarea.value.trim() : '';

    if (!content) {
      showToast('コメントを入力してください。', 'error');
      return;
    }

    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.disabled = true;

    const formData = new FormData(form);
    const csrfToken = getCsrfToken();

    fetch(`/post/${postId}/comment/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: formData,
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          const comment = data.comment;
          const commentList = form.closest('.comments-section').querySelector('.comment-list');

          if (commentList) {
            const newComment = createCommentElement(comment);
            if (comment.parent_id) {
              // 返信の場合は親コメントの下に追加
              const parentItem = commentList.querySelector(`[data-comment-id="${comment.parent_id}"]`);
              if (parentItem) {
                parentItem.insertAdjacentElement('afterend', newComment);
              } else {
                commentList.appendChild(newComment);
              }
            } else {
              commentList.appendChild(newComment);
            }
          }

          // フォームをリセット
          if (textarea) textarea.value = '';
          // 返信フォームを閉じる
          const replyContainer = form.closest('.reply-form-container');
          if (replyContainer) replyContainer.remove();

          showToast('コメントを投稿しました！', 'success');
        } else {
          showToast('コメントの投稿に失敗しました。', 'error');
        }
      })
      .catch(err => {
        console.error('コメントエラー:', err);
        showToast('エラーが発生しました。', 'error');
      })
      .finally(() => {
        if (submitBtn) submitBtn.disabled = false;
      });
  });
}

function createCommentElement(comment) {
  const li = document.createElement('li');
  li.className = `comment-item${comment.parent_id ? ' reply' : ''}`;
  li.dataset.commentId = comment.id;
  li.innerHTML = `
    <div class="comment-header">
      <span class="comment-author">${escapeHtml(comment.author_name)}</span>
      <span class="comment-time">${comment.created_at}</span>
    </div>
    <p class="comment-content">${escapeHtml(comment.content)}</p>
    ${!comment.parent_id ? `<button class="comment-reply-btn" data-comment-id="${comment.id}">返信する</button>` : ''}
  `;
  return li;
}

// ===================================================
// コメント表示/非表示トグル
// ===================================================
function initCommentToggles() {
  document.addEventListener('click', function (e) {
    // コメントトグルボタン
    const toggleBtn = e.target.closest('.comment-toggle-btn');
    if (toggleBtn) {
      const postId = toggleBtn.dataset.postId;
      const section = document.getElementById(`comments-${postId}`);
      if (section) {
        section.classList.toggle('open');
        const countEl = toggleBtn.querySelector('.comment-toggle-count');
        const isOpen = section.classList.contains('open');
        toggleBtn.setAttribute('aria-expanded', isOpen);
      }
      return;
    }

    // 返信ボタン
    const replyBtn = e.target.closest('.comment-reply-btn');
    if (replyBtn) {
      const commentId = replyBtn.dataset.commentId;
      const postId = replyBtn.closest('.comments-section').dataset.postId;
      const existingForm = document.getElementById(`reply-form-${commentId}`);

      if (existingForm) {
        existingForm.remove();
        return;
      }

      const replyForm = document.createElement('div');
      replyForm.id = `reply-form-${commentId}`;
      replyForm.className = 'reply-form-container';
      replyForm.innerHTML = `
        <form class="comment-form comment-form-ajax mt-2" data-post-id="${postId}">
          <input type="hidden" name="parent_id" value="${commentId}">
          <input type="hidden" name="csrfmiddlewaretoken" value="${getCsrfToken()}">
          <textarea name="content" placeholder="返信を入力..." rows="2" maxlength="500"></textarea>
          <button type="submit" class="btn btn-sm btn-primary">返信</button>
        </form>
      `;
      replyBtn.closest('.comment-item').insertAdjacentElement('afterend', replyForm);
      replyForm.querySelector('textarea').focus();
      return;
    }
  });
}

// ===================================================
// 文字数カウンター
// ===================================================
function initCharCounters() {
  document.querySelectorAll('[data-max-length]').forEach(function (el) {
    const maxLength = parseInt(el.dataset.maxLength);
    const counterId = el.dataset.counterId;
    const counter = counterId ? document.getElementById(counterId) : null;

    if (!counter) return;

    function update() {
      const remaining = maxLength - el.value.length;
      counter.textContent = `${el.value.length} / ${maxLength}`;
      counter.className = 'char-counter';
      if (remaining < 50) counter.classList.add('warning');
      if (remaining < 10) counter.classList.add('danger');
    }

    el.addEventListener('input', update);
    update();
  });
}

// ===================================================
// メッセージ自動消去
// ===================================================
function initMessages() {
  const messages = document.querySelectorAll('.message-alert');
  messages.forEach(function (msg, i) {
    setTimeout(function () {
      msg.style.opacity = '0';
      msg.style.transform = 'translateX(20px)';
      msg.style.transition = 'all 0.3s ease';
      setTimeout(() => msg.remove(), 300);
    }, 4000 + i * 500);

    msg.addEventListener('click', function () {
      msg.style.opacity = '0';
      setTimeout(() => msg.remove(), 300);
    });
  });
}

// ===================================================
// 賛成/反対セレクター
// ===================================================
function initSideSelector() {
  const radios = document.querySelectorAll('.side-option input[type="radio"]');
  radios.forEach(function (radio) {
    radio.addEventListener('change', function () {
      // 選択状態のビジュアル更新はCSSで処理
      updatePostFormStyle(this.value);
    });
  });
}

function updatePostFormStyle(side) {
  const textarea = document.querySelector('.post-textarea');
  if (!textarea) return;

  textarea.className = 'post-textarea';
  if (side === 'pro') {
    textarea.style.borderColor = 'var(--pro-color)';
  } else if (side === 'con') {
    textarea.style.borderColor = 'var(--con-color)';
  } else {
    textarea.style.borderColor = '';
  }
}

// ===================================================
// 検索フォーム
// ===================================================
function initSearchForm() {
  // Enterキーで検索
  const searchInputs = document.querySelectorAll('.search-bar input, .mobile-search input');
  searchInputs.forEach(function (input) {
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        const q = input.value.trim();
        if (q) {
          window.location.href = `/search/?q=${encodeURIComponent(q)}`;
        }
      }
    });
  });

  // 検索ボタン
  const searchBtns = document.querySelectorAll('.search-bar button');
  searchBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const input = btn.closest('.search-bar').querySelector('input');
      if (input && input.value.trim()) {
        window.location.href = `/search/?q=${encodeURIComponent(input.value.trim())}`;
      }
    });
  });
}

// ===================================================
// スクロールアニメーション
// ===================================================
function initAnimations() {
  if (!window.IntersectionObserver) return;

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.debate-card, .post-card').forEach(function (el) {
    el.style.opacity = '0';
    el.style.transform = 'translateY(10px)';
    el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
    observer.observe(el);
  });
}

// ===================================================
// 投稿フォーム（AJAX）
// ===================================================
function initPostForm() {
  const form = document.getElementById('post-form');
  if (!form) return;

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    const debateId = form.dataset.debateId;
    const submitBtn = form.querySelector('button[type="submit"]');
    const content = form.querySelector('[name="content"]').value.trim();
    const side = form.querySelector('[name="side"]:checked');

    if (!content) {
      showToast('意見を入力してください。', 'error');
      return;
    }

    if (!side) {
      showToast('賛成・反対を選択してください。', 'error');
      return;
    }

    if (submitBtn) submitBtn.disabled = true;

    const formData = new FormData(form);

    fetch(`/${debateId}/post/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCsrfToken(),
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: formData,
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          const post = data.post;
          addPostToColumn(post);
          form.reset();
          updateScoreBar();
          showToast('意見を投稿しました！', 'success');
        } else {
          const errors = data.errors;
          let msg = '入力内容を確認してください。';
          if (errors && errors.content) msg = errors.content[0];
          showToast(msg, 'error');
        }
      })
      .catch(err => {
        console.error('投稿エラー:', err);
        showToast('エラーが発生しました。', 'error');
      })
      .finally(() => {
        if (submitBtn) submitBtn.disabled = false;
      });
  });
}

function addPostToColumn(post) {
  const column = document.getElementById(`column-${post.side}`);
  if (!column) return;

  const postEl = document.createElement('div');
  postEl.className = `post-card ${post.side}`;
  postEl.dataset.postId = post.id;
  postEl.innerHTML = `
    <div class="post-author">
      <div class="post-avatar ${post.side}">${post.author_name.charAt(0)}</div>
      <span class="post-author-name">${escapeHtml(post.author_name)}</span>
      <span class="post-time">${post.created_at}</span>
    </div>
    <p class="post-content">${escapeHtml(post.content)}</p>
    <div class="post-actions">
      <button class="like-btn" data-post-id="${post.id}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
        </svg>
        <span class="like-count">0</span>
      </button>
      <button class="comment-toggle-btn" data-post-id="${post.id}">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        <span class="comment-toggle-count">0</span>件のコメント
      </button>
    </div>
    <div class="comments-section" id="comments-${post.id}" data-post-id="${post.id}">
      <ul class="comment-list"></ul>
      <form class="comment-form comment-form-ajax" data-post-id="${post.id}">
        <input type="hidden" name="csrfmiddlewaretoken" value="${getCsrfToken()}">
        <textarea name="content" placeholder="コメントを入力..." rows="2" maxlength="500"></textarea>
        <button type="submit">送信</button>
      </form>
    </div>
  `;

  column.insertBefore(postEl, column.firstChild);

  // カウントを更新
  const countEl = column.querySelector('.column-count');
  if (countEl) {
    countEl.textContent = parseInt(countEl.textContent || 0) + 1;
  }
}

function updateScoreBar() {
  const proColumn = document.getElementById('column-pro');
  const conColumn = document.getElementById('column-con');
  if (!proColumn || !conColumn) return;

  const proCount = proColumn.querySelectorAll('.post-card').length;
  const conCount = conColumn.querySelectorAll('.post-card').length;
  const total = proCount + conCount;

  const proCountEl = document.querySelector('.pro-count');
  const conCountEl = document.querySelector('.con-count');
  const barFill = document.querySelector('.score-bar-fill');

  if (proCountEl) proCountEl.textContent = proCount;
  if (conCountEl) conCountEl.textContent = conCount;
  if (barFill && total > 0) {
    barFill.style.width = `${(proCount / total) * 100}%`;
  }
}

// ===================================================
// ユーティリティ関数
// ===================================================

/**
 * CSRFトークンを取得する
 */
function getCsrfToken() {
  const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
  if (cookie) return cookie.split('=')[1].trim();
  const meta = document.querySelector('meta[name="csrf-token"]');
  if (meta) return meta.content;
  const input = document.querySelector('[name="csrfmiddlewaretoken"]');
  if (input) return input.value;
  return '';
}

/**
 * HTMLエスケープ
 */
function escapeHtml(str) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

/**
 * トースト通知を表示する
 */
function showToast(message, type = 'info') {
  const container = document.getElementById('messages-container') ||
    (() => {
      const c = document.createElement('div');
      c.id = 'messages-container';
      c.className = 'messages-container';
      document.body.appendChild(c);
      return c;
    })();

  const alert = document.createElement('div');
  alert.className = `message-alert ${type}`;
  alert.textContent = message;
  container.appendChild(alert);

  setTimeout(() => {
    alert.style.opacity = '0';
    alert.style.transform = 'translateX(20px)';
    alert.style.transition = 'all 0.3s ease';
    setTimeout(() => alert.remove(), 300);
  }, 3000);

  alert.addEventListener('click', () => alert.remove());
}

// 投稿フォームの初期化（討論詳細ページ用）
document.addEventListener('DOMContentLoaded', function () {
  initPostForm();
});

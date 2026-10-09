(() => {
  const $ = (id) => document.getElementById(id);
  const log = $('log');
  const scroller = $('scroller');
  const questionBox = $('question');
  const TOKEN_KEY = 'ragdoc.token';
  const DOCS_PREFIX = /^docs\/([a-z-]+)\/docs\//;
  const MODES = { dense: 'dense(벡터 검색)', hybrid: 'hybrid(벡터 + 키워드)', rerank: 'rerank(재정렬)' };
  const stampFormat = new Intl.DateTimeFormat('ko-KR', { month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  const EXAMPLES = [
    '존재하지 않는 항목을 요청하면 404 오류를 어떻게 반환하나요?',
    '한 번의 요청으로 여러 파일을 업로드하려면 어떻게 하나요?',
    "What's the difference between def and async def for an endpoint?",
  ];

  let token = null;
  try { token = sessionStorage.getItem(TOKEN_KEY); } catch (e) { /* storage blocked: stay logged out */ }
  let busy = false;
  let queuedQuestion = null;

  class ApiError extends Error {
    constructor(status, detail) {
      super(detail || 'HTTP ' + status);
      this.status = status;
      this.detail = detail;
    }
  }

  async function api(path, options = {}) {
    const headers = { ...(options.headers || {}) };
    if (token) headers.Authorization = 'Bearer ' + token;
    let res;
    try {
      res = await fetch(path, { ...options, headers });
    } catch (e) {
      throw new ApiError(0, '서버에 연결할 수 없어요. docker compose로 서버가 켜져 있는지 확인해 주세요.');
    }
    if (!res.ok) {
      let detail = '';
      let fields = [];
      try {
        const body = await res.json();
        if (typeof body.detail === 'string') detail = body.detail;
        // A 422 lists each rejected field; its last loc entry is the field name.
        if (Array.isArray(body.detail)) fields = body.detail.map((d) => (d.loc || []).at(-1));
      } catch (e) { /* non-JSON error body */ }
      const err = new ApiError(res.status, detail);
      err.fields = fields;
      throw err;
    }
    return res.json();
  }

  function errorText(err, context) {
    if (err.status === 0) return err.message;
    if (context === 'login' && err.status === 401) return '이메일이나 비밀번호가 맞지 않아요.';
    if (context === 'register' && err.status === 409) return '이미 가입된 이메일이에요. 로그인을 눌러 주세요.';
    if (err.status === 422) {
      if (context === 'ask') return '질문은 2000자 이내로 입력해 주세요.';
      if ((err.fields || []).includes('password')) {
        return '비밀번호는 8자 이상, 72바이트(한글은 24자) 이하로 정해 주세요.';
      }
      return '이메일 형식을 확인해 주세요.';
    }
    if (context === 'ask' && err.status >= 500) {
      return `답변을 만들지 못했어요 (HTTP ${err.status}). Ollama가 켜져 있는지 확인한 뒤 다시 보내 주세요.`;
    }
    return `요청이 실패했어요 (HTTP ${err.status}${err.detail ? ', ' + err.detail : ''}).`;
  }

  function setToken(value) {
    token = value;
    try {
      if (value) sessionStorage.setItem(TOKEN_KEY, value);
      else sessionStorage.removeItem(TOKEN_KEY);
    } catch (e) { /* storage blocked: token lives in memory only */ }
  }

  /* ---------- rendering ---------- */

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }

  function renderProse(s) {
    s = s.trim();
    if (!s) return '';
    return s.split(/\n{2,}/).map((para) => {
      const html = escapeHtml(para)
        .replace(/`([^`\n]+)`/g, '<code>$1</code>')
        .replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
      return '<p>' + html + '</p>';
    }).join('');
  }

  // Answers are markdown-ish: prose plus ``` code fences. Everything is escaped
  // before any tag is added, so model output can never inject markup.
  function renderAnswer(text) {
    const fence = /```[\w-]*\n?([\s\S]*?)(?:```|$)/g;
    const parts = [];
    let last = 0;
    let match;
    while ((match = fence.exec(text)) !== null) {
      parts.push(renderProse(text.slice(last, match.index)));
      parts.push('<pre><code>' + escapeHtml(match[1].replace(/\n$/, '')) + '</code></pre>');
      last = fence.lastIndex;
    }
    parts.push(renderProse(text.slice(last)));
    return parts.join('');
  }

  function docLanguage(sourcePath) {
    const match = sourcePath.match(DOCS_PREFIX);
    return match ? match[1] : 'en';
  }

  function docUrl(sourcePath) {
    const language = docLanguage(sourcePath);
    let page = sourcePath.replace(DOCS_PREFIX, '');
    page = page.endsWith('index.md') ? page.slice(0, -'index.md'.length) : page.replace(/\.md$/, '/');
    return 'https://fastapi.tiangolo.com/' + (language === 'en' ? '' : language + '/') + page;
  }

  function docLabel(sourcePath) {
    const origin = docLanguage(sourcePath) === 'en' ? '영어 원문' : '한국어 번역';
    return origin + ', ' + sourcePath.replace(DOCS_PREFIX, '');
  }

  function renderSources(citations) {
    const box = el('div', 'sources');
    box.appendChild(el('h2', null, '참고한 문서'));
    const list = el('ol');
    const seen = new Set();
    for (const c of citations) {
      const key = c.source_path + '|' + (c.heading_path || '');
      if (seen.has(key)) continue;
      seen.add(key);
      const link = el('a');
      link.href = docUrl(c.source_path);
      link.target = '_blank';
      link.rel = 'noopener';
      const title = c.heading_path
        ? c.heading_path.replace(/`/g, '').split(' > ').join(' › ')
        : c.source_path.replace(DOCS_PREFIX, '').replace(/\.md$/, '');
      link.append(el('span', 'crumb', title), el('span', 'path', docLabel(c.source_path)));
      const item = el('li');
      item.appendChild(link);
      list.appendChild(item);
    }
    box.appendChild(list);
    return box;
  }

  function seconds(ms) {
    const s = ms / 1000;
    return (s < 1 ? s.toFixed(2) : s.toFixed(1)) + '초';
  }

  function renderTiming(t) {
    const total = t.total || t.embedding + t.retrieval + t.generation;
    const steps = [
      ['질문 분석', t.embedding, 'seg-embed'],
      ['문서 검색', t.retrieval, 'seg-search'],
      ['답변 작성', t.generation, 'seg-gen'],
    ];
    const wrap = el('div', 'timing');
    wrap.appendChild(el('div', null, seconds(total) + ' 걸림'));
    const bar = el('div', 'timing-bar');
    bar.setAttribute('aria-hidden', 'true');
    const legend = el('div', 'legend');
    for (const [label, ms, cls] of steps) {
      const seg = el('span', cls);
      seg.style.flexBasis = (total ? (ms / total) * 100 : 0) + '%';
      bar.appendChild(seg);
      const entry = el('span');
      entry.append(el('i', cls), label + ' ' + seconds(ms));
      legend.appendChild(entry);
    }
    wrap.append(bar, legend);
    return wrap;
  }

  function renderResult(container, data) {
    container.replaceChildren();
    const answer = el('div', 'answer');
    answer.innerHTML = renderAnswer(data.answer);
    container.appendChild(answer);
    if (data.citations && data.citations.length) {
      container.appendChild(renderSources(data.citations));
    } else {
      container.appendChild(el('p', 'no-sources', '근거로 표시된 문서가 없는 답변이에요.'));
    }
    if (data.latency_ms) container.appendChild(renderTiming(data.latency_ms));
  }

  function addUser(text) {
    log.appendChild(el('div', 'msg-user', text));
  }

  function historyNodes(item) {
    const bot = el('div', 'msg-bot');
    const d = item.detail;
    renderResult(bot, {
      answer: item.answer,
      citations: d ? d.retrieved_chunks.filter((c) => c.cited) : [],
      latency_ms: d && d.generation_latency_ms != null ? {
        embedding: d.embedding_latency_ms || 0,
        retrieval: d.retrieval_latency_ms || 0,
        generation: d.generation_latency_ms || 0,
        total: item.total_latency_ms || 0,
      } : null,
    });
    return [el('div', 'stamp', stampFormat.format(new Date(item.created_at))), el('div', 'msg-user', item.question), bot];
  }

  function scrollToEnd() {
    scroller.scrollTop = scroller.scrollHeight;
  }

  function renderWelcome() {
    const wrap = el('div', 'msg-bot');
    const box = el('div', 'answer');
    box.appendChild(el('p', null, 'FastAPI 공식 문서(영어 원문 154개, 한국어 번역 123개)에서 질문과 같은 언어의 문서를 찾아, 찾은 내용만으로 답해요. 답변 아래에 근거로 쓴 문서가 나오고, 누르면 원문으로 이동해요.'));
    box.appendChild(el('p', null, '이런 질문부터 해 보세요.'));
    const examples = el('div', 'examples');
    for (const q of EXAMPLES) {
      const button = el('button', 'example', q);
      button.type = 'button';
      button.addEventListener('click', () => {
        if (token) {
          ask(q);
        } else {
          queuedQuestion = q;
          showLoginMessage('로그인하면 이 질문을 바로 보낼게요.');
          $('email').focus();
        }
      });
      examples.appendChild(button);
    }
    box.appendChild(examples);
    wrap.appendChild(box);
    log.appendChild(wrap);
  }

  function addPending() {
    const wrap = el('div', 'msg-bot');
    const row = el('div', 'pending');
    const label = el('span');
    row.append(el('span', 'pulse'), label);
    wrap.appendChild(row);
    log.appendChild(wrap);
    const started = performance.now();
    const tick = () => {
      label.textContent = '문서를 찾고 답변을 쓰는 중이에요 ' + Math.floor((performance.now() - started) / 1000) + '초';
    };
    tick();
    const timer = setInterval(tick, 500);
    scrollToEnd();
    return { wrap, stop: () => clearInterval(timer) };
  }

  /* ---------- actions ---------- */

  async function ask(raw) {
    const question = raw.trim();
    if (!question || busy) return;
    busy = true;
    $('ask-button').disabled = true;
    log.querySelector('.examples')?.closest('.msg-bot')?.remove();
    addUser(question);
    questionBox.value = '';
    autoGrow();
    const pending = addPending();
    try {
      const data = await api('/query/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, top_k: 5 }),
      });
      pending.stop();
      renderResult(pending.wrap, data);
    } catch (err) {
      pending.stop();
      if (err.status === 401) {
        queuedQuestion = question;
        logout('로그인이 만료됐어요. 다시 로그인하면 방금 질문을 이어서 보낼게요.');
      } else {
        pending.wrap.replaceChildren(el('p', 'failed', errorText(err, 'ask')));
      }
    } finally {
      busy = false;
      $('ask-button').disabled = false;
      scrollToEnd();
    }
  }

  async function loadHistory() {
    let items;
    try {
      items = await api('/logs?limit=10');
    } catch (err) {
      items = [];
    }
    if (!items.length) {
      if (!log.children.length) renderWelcome();
      return;
    }
    const details = await Promise.all(items.map((item) => api('/logs/' + item.id).catch(() => null)));
    items.forEach((item, i) => { item.detail = details[i]; });
    // Prepend instead of replacing: a question sent while the history was still
    // loading is already on screen and must stay below it.
    log.prepend(...items.reverse().flatMap(historyNodes));
    scrollToEnd();
  }

  async function enterChat() {
    $('login-form').hidden = true;
    $('login-msg').hidden = true;
    $('ask-form').hidden = false;
    $('ask-hint').hidden = false;
    $('who').hidden = false;
    log.replaceChildren();
    try {
      const me = await api('/auth/me');
      $('who-email').textContent = me.email;
    } catch (err) {
      if (err.status === 401) {
        logout('로그인이 만료됐어요. 다시 로그인해 주세요.');
        return;
      }
    }
    await loadHistory();
    questionBox.focus();
    if (queuedQuestion) {
      const q = queuedQuestion;
      queuedQuestion = null;
      ask(q);
    }
  }

  function showLoginMessage(text, failed = false) {
    const msg = $('login-msg');
    msg.hidden = false;
    msg.textContent = text;
    msg.classList.toggle('failed', failed);
  }

  function logout(message) {
    setToken(null);
    $('who').hidden = true;
    $('ask-form').hidden = true;
    $('ask-hint').hidden = true;
    $('login-form').hidden = false;
    showLoginMessage(message || '로그아웃했어요. 다시 질문하려면 로그인하세요.');
    log.replaceChildren();
    renderWelcome();
  }

  async function authenticate(kind) {
    const email = $('email').value.trim();
    const password = $('password').value;
    const buttons = $('login-form').querySelectorAll('button');
    buttons.forEach((b) => { b.disabled = true; });
    showLoginMessage(kind === 'register' ? '계정을 만드는 중이에요.' : '로그인하는 중이에요.');
    try {
      if (kind === 'register') {
        await api('/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        });
      }
      const tokens = await api('/auth/login', {
        method: 'POST',
        body: new URLSearchParams({ username: email, password }),
      });
      setToken(tokens.access_token);
      $('password').value = '';
      await enterChat();
    } catch (err) {
      showLoginMessage(errorText(err, kind), true);
    } finally {
      buttons.forEach((b) => { b.disabled = false; });
    }
  }

  async function loadStatus() {
    try {
      const h = await api('/health');
      const mode = MODES[h.retrieval_mode] || h.retrieval_mode || '알 수 없음';
      $('status').textContent = `검색 방식 ${mode}, 답변 모델 ${h.generation_model || '알 수 없음'}`
        + (h.db === 'ok' ? '' : ', DB 연결 오류');
    } catch (err) {
      $('status').textContent = '서버에 연결할 수 없어요';
    }
  }

  function autoGrow() {
    questionBox.style.height = 'auto';
    questionBox.style.height = Math.min(questionBox.scrollHeight, 160) + 'px';
  }

  /* ---------- wiring ---------- */

  $('login-form').addEventListener('submit', (e) => {
    e.preventDefault();
    authenticate('login');
  });
  $('register').addEventListener('click', () => {
    if ($('login-form').reportValidity()) authenticate('register');
  });
  $('logout').addEventListener('click', () => logout());
  $('ask-form').addEventListener('submit', (e) => {
    e.preventDefault();
    ask(questionBox.value);
  });
  questionBox.addEventListener('keydown', (e) => {
    // While a Korean IME is still composing a syllable, Enter only confirms it. Browsers
    // flag that with isComposing, and some (Safari) only with keyCode 229.
    if (e.isComposing || e.keyCode === 229) return;
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      ask(questionBox.value);
    }
  });
  questionBox.addEventListener('input', autoGrow);

  loadStatus();
  if (token) {
    enterChat();
  } else {
    renderWelcome();
  }
})();

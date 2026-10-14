// [파일 역할] 채팅 화면(app/web/index.html)의 동작 전부. 로그인·가입, 질문 보내기, 답변·근거 문서·걸린 시간
// 그리기, 최근 질문 불러오기, 서버 상태 표시를 맡는다. 원래 index.html의 인라인 script였고, CSP(같은 출처
// 파일만 실행)를 지키려고 내용 그대로 이 파일로 옮겼다.
// [설계]
// - 빌드 도구 없는 순수 JavaScript. 전역 변수를 만들지 않도록 전체를 즉시 실행 함수로 감싼다.
// - 서버 API(/auth/*, /query/ask, /logs, /health)만 부른다. 다른 클라이언트와 같은 API라 화면이 API 사용
//   예시도 된다.
// - 보안: 모델 출력과 사용자 입력은 textContent로 넣거나, HTML이 필요하면 먼저 이스케이프한 뒤에 태그를
//   붙인다(renderAnswer). 접근 토큰은 sessionStorage에 둬 탭을 닫으면 사라진다.
// [흐름] 시작 → 서버 상태 표시 → 저장된 토큰이 있으면 대화 화면(최근 질문 10개), 없으면 환영 화면과 로그인
// 폼.

(() => {
  // $: id로 요소를 찾는 짧은 도우미. log는 대화가 쌓이는 곳, scroller는 스크롤되는 main, questionBox는 질문
  // 입력칸이다.
  const $ = (id) => document.getElementById(id);
  const log = $('log');
  const scroller = $('scroller');
  const questionBox = $('question');
  // TOKEN_KEY: sessionStorage에 접근 토큰을 저장할 키.
  // DOCS_PREFIX: 'docs/<언어>/docs/' 경로 앞부분. 문서 언어를 알아내고 공식 문서 URL로 바꾸는 데 쓴다.
  // MODES: /health의 retrieval_mode 값을 상태 줄에 보일 한국어 설명으로 바꾸는 표.
  // stampFormat: 불러온 이전 질문 위에 찍을 날짜·시각 형식.
  // EXAMPLES: 첫 화면의 예시 질문(한국어 두 개, 영어 한 개). 누르면 바로 보내진다.
  const TOKEN_KEY = 'ragdoc.token';
  const DOCS_PREFIX = /^docs\/([a-z-]+)\/docs\//;
  const MODES = { dense: 'dense(벡터 검색)', hybrid: 'hybrid(벡터 + 키워드)', rerank: 'rerank(재정렬)' };
  const stampFormat = new Intl.DateTimeFormat('ko-KR', { month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  const EXAMPLES = [
    '존재하지 않는 항목을 요청하면 404 오류를 어떻게 반환하나요?',
    '한 번의 요청으로 여러 파일을 업로드하려면 어떻게 하나요?',
    "What's the difference between def and async def for an endpoint?",
  ];

  // 페이지를 새로 고쳐도 같은 탭이면 로그인이 유지되도록 sessionStorage에서 토큰을 읽는다. 브라우저 설정으로
  // 저장소가 막혀 있으면 예외가 나므로 잡고 로그아웃 상태로 시작한다.
  // busy: 답변을 기다리는 중이면 새 질문을 막는 표시. queuedQuestion: 로그인 전에 누른 예시 질문이나 토큰
  // 만료로 못 보낸 질문을 로그인 뒤 이어 보내려고 잠시 담아 둔다.
  let token = null;
  try { token = sessionStorage.getItem(TOKEN_KEY); } catch (e) { /* 저장소가 막힘: 로그아웃 상태로 둔다 */ }
  let busy = false;
  let queuedQuestion = null;

  // API 오류: HTTP 상태 코드와 서버의 detail 문구를 함께 담는다. status 0은 서버에 아예 닿지 못한 경우다.
  class ApiError extends Error {
    constructor(status, detail) {
      super(detail || 'HTTP ' + status);
      this.status = status;
      this.detail = detail;
    }
  }

  // 모든 API 호출의 공통 함수. 토큰이 있으면 Authorization: Bearer 헤더를 붙이고, 성공하면 JSON 본문을,
  // 실패하면 ApiError를 던진다.
  // 네트워크 오류(fetch 자체 실패)는 서버가 꺼진 경우로 보고 안내 문구를 담는다. 실패 응답에서는 detail이
  // 문자열이면 그대로 쓰고, 422처럼 목록이면 어떤 필드가 거부됐는지(loc의 마지막 값)와 거부 이유(type, 예:
  // string_too_long)를 모아 둔다.
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
      let types = [];
      try {
        const body = await res.json();
        if (typeof body.detail === 'string') detail = body.detail;
        // 422는 거부된 필드를 하나씩 나열하고, 각 항목의 loc 마지막 값이 필드 이름이다.
        if (Array.isArray(body.detail)) {
          fields = body.detail.map((d) => (d.loc || []).at(-1));
          types = body.detail.map((d) => d.type);
        }
      } catch (e) { /* 오류 본문이 JSON이 아님 */ }
      const err = new ApiError(res.status, detail);
      err.fields = fields;
      err.types = types;
      throw err;
    }
    return res.json();
  }

  // 오류를 상황별 한국어 안내로 바꾼다. context는 login, register, ask 중 하나다.
  // - 422: 질문이면 거부 이유로 나눈다. 너무 길면(string_too_long, 2000자 초과) 길이 안내, 그 밖에는 서버가
  //   저장할 수 없는 문자(NUL 같은 제어 문자, 짝이 없는 서로게이트) 안내다. 예전에는 이유와 상관없이 늘 길이
  //   안내였다. 가입이면 거부된 필드가 password인지로 비밀번호 규칙(8자 이상, 72바이트 이하)과 이메일 형식
  //   오류를 구분한다. 서버의 비밀번호 규칙(app/schemas/auth.py)과 같은 숫자다.
  // - 질문의 5xx는 대개 생성 단계(Ollama) 문제라 Ollama 확인을 권한다.
  function errorText(err, context) {
    if (err.status === 0) return err.message;
    if (context === 'login' && err.status === 401) return '이메일이나 비밀번호가 맞지 않아요.';
    if (context === 'register' && err.status === 409) return '이미 가입된 이메일이에요. 로그인을 눌러 주세요.';
    if (err.status === 422) {
      if (context === 'ask') {
        if ((err.types || []).includes('string_too_long')) return '질문은 2000자 이내로 입력해 주세요.';
        return '질문에 보낼 수 없는 문자(NUL 같은 제어 문자)가 들어 있어요. 그 부분을 지우고 다시 보내 주세요.';
      }
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

  // 토큰을 메모리와 sessionStorage에 함께 저장하거나 지운다. 저장소가 막혀 있으면 메모리에만 둔다(새로 고치면
  // 로그아웃).
  function setToken(value) {
    token = value;
    try {
      if (value) sessionStorage.setItem(TOKEN_KEY, value);
      else sessionStorage.removeItem(TOKEN_KEY);
    } catch (e) { /* 저장소가 막힘: 토큰은 메모리에만 남는다 */ }
  }

  /* ---------- 화면 그리기 ---------- */

  // 요소를 만드는 도우미. 글은 textContent로 넣으므로 HTML로 해석되지 않는다.
  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  // HTML 특수 문자 다섯 개를 엔티티로 바꾼다. innerHTML에 넣는 글은 반드시 이 함수를 먼저 거친다.
  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }

  // 코드 블록 밖의 글을 HTML로 바꾼다. 빈 줄로 문단을 나누고, 이스케이프한 뒤에 인라인 코드(백틱)와 굵게(별표
  // 두 개)만 태그로 바꾸고, 줄바꿈은 br로 바꾼다. 마크다운 전체를 지원하지 않고 답변에 자주 나오는 것만
  // 처리한다.
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

  // 답변은 마크다운 비슷한 형식이다: 설명 글과 ``` 코드 펜스. 태그를 하나라도 붙이기 전에 모든 글을 먼저
  // 이스케이프하므로, 모델 출력이 마크업을 끼워 넣을 수 없다. 닫히지 않은 펜스는 답의 끝까지를 코드로 본다.
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

  // 문서 경로에서 언어를 꺼낸다(형식이 다르면 영어로 본다).
  function docLanguage(sourcePath) {
    const match = sourcePath.match(DOCS_PREFIX);
    return match ? match[1] : 'en';
  }

  // 저장소 경로를 공식 문서 사이트 주소로 바꾼다. 예: docs/ko/docs/tutorial/body.md →
  // https://fastapi.tiangolo.com/ko/tutorial/body/. index.md는 폴더 주소가 되고, 영어는 언어 경로를 붙이지
  // 않는다.
  function docUrl(sourcePath) {
    const language = docLanguage(sourcePath);
    let page = sourcePath.replace(DOCS_PREFIX, '');
    page = page.endsWith('index.md') ? page.slice(0, -'index.md'.length) : page.replace(/\.md$/, '/');
    return 'https://fastapi.tiangolo.com/' + (language === 'en' ? '' : language + '/') + page;
  }

  // 근거 문서 아래에 작게 보일 표시: '영어 원문' 또는 '한국어 번역'과 문서 안 경로.
  function docLabel(sourcePath) {
    const origin = docLanguage(sourcePath) === 'en' ? '영어 원문' : '한국어 번역';
    return origin + ', ' + sourcePath.replace(DOCS_PREFIX, '');
  }

  // 인용 목록을 '참고한 문서' 상자로 그린다. 같은 문서의 같은 절을 여러 청크가 가리키면 한 번만 보인다.
  // 링크는 새 탭으로 열고 rel=noopener로 새 탭이 원래 페이지에 접근하지 못하게 한다. 제목은 헤딩 경로(백틱
  // 빼고 ' › '로 이음), 없으면 파일 경로다.
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

  // 밀리초를 '0.12초', '3.4초'처럼 읽기 쉬운 글로 바꾼다(1초 미만은 소수 둘째 자리).
  function seconds(ms) {
    const s = ms / 1000;
    return (s < 1 ? s.toFixed(2) : s.toFixed(1)) + '초';
  }

  // 응답의 latency_ms로 단계별 걸린 시간 막대를 그린다. 세 단계(질문 분석=임베딩, 문서 검색, 답변
  // 작성=생성)의 비율만큼 칸 너비(flexBasis)를 정한다. 너비는 element.style로 스크립트가 넣으므로 CSP의 style
  // 속성 금지에 걸리지 않는다. 막대는 장식이라 aria-hidden으로 숨기고, 같은 정보를 범례 글로 보여 준다.
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

  // 답변 하나를 그린다: 답 본문(renderAnswer로 안전하게 만든 HTML), 근거 문서(없으면 안내 문구), 걸린 시간.
  // 기다림 표시가 있던 자리를 비우고 다시 채운다.
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

  // 내 질문 말풍선. textContent라 질문에 HTML이 있어도 글자로만 보인다.
  function addUser(text) {
    log.appendChild(el('div', 'msg-user', text));
  }

  // 불러온 이전 질문 하나를 날짜, 질문, 답변 노드로 되살린다. 인용은 상세 기록의 retrieved_chunks 중 cited인
  // 것으로 만든다(이 기록에는 헤딩 경로가 없어 제목은 파일 경로로 나온다). 상세를 못 받았거나 지연 기록이
  // 없으면 그 부분은 빼고 그린다.
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

  // 대화 영역을 맨 아래로 내린다.
  function scrollToEnd() {
    scroller.scrollTop = scroller.scrollHeight;
  }

  // 첫 화면 안내와 예시 질문 버튼. 로그인돼 있으면 누르는 즉시 보내고, 아니면 질문을 담아 두고 로그인을
  // 안내한 뒤 이메일 칸으로 초점을 옮긴다.
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

  // 답변을 기다리는 동안 깜빡이는 점과 경과 초를 보여 준다. 0.5초마다 글을 갱신하고, 돌려준 stop으로 타이머를
  // 멈춘다. wrap은 나중에 답변으로 바뀔 자리다.
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

  /* ---------- 사용자 동작 ---------- */

  // 질문을 보낸다. 앞뒤 공백을 지운 빈 질문이나, 이전 답변을 기다리는 중이면 무시한다. 첫 화면의 예시 상자를
  // 지우고, 내 말풍선과 기다림 표시를 붙인 뒤 /query/ask를 부른다(top_k 5).
  // - 성공: 기다림 자리에 답변을 그린다.
  // - 401: 토큰이 만료됐으므로 질문을 담아 두고 로그아웃한다. 다시 로그인하면 enterChat이 이어 보낸다(갱신
  //   토큰은 쓰지 않는다).
  // - 그 밖의 오류: 기다림 자리에 오류 문구를 보인다.
  // finally에서 busy를 풀어 다음 질문을 받는다.
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

  // 로그인 뒤 내 최근 질문 10개를 불러온다. 목록(/logs?limit=10)은 요약만 주므로 각 항목의 상세(/logs/{id})를
  // 동시에 받아 인용과 걸린 시간을 채운다. 상세 하나가 실패해도 나머지는 그린다. 기록이 없고 화면이 비어
  // 있으면 환영 화면을 보인다. 목록은 최신순이라 뒤집어서 오래된 것이 위에 오게 한다.
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
    // 바꿔 넣지 않고 앞에 붙인다: 기록을 불러오는 동안 보낸 질문은 이미 화면에 있고, 그 질문은 기록 아래에
    // 남아 있어야 한다.
    log.prepend(...items.reverse().flatMap(historyNodes));
    scrollToEnd();
  }

  // 대화 화면으로 바꾼다: 로그인 폼을 숨기고 질문 폼을 보인 뒤, 화면을 비우고 /auth/me로 이메일을 표시한다.
  // 토큰이 만료돼 401이면 로그아웃한다. 화면을 여기서(불러오기 전에) 비우므로, 불러오는 동안 보낸 새 질문이
  // 나중에 지워지지 않는다. 그다음 이전 질문을 불러오고, 담아 둔 질문이 있으면 보낸다.
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

  // 로그인 폼 아래 안내 문구를 보인다. failed면 오류 색으로 표시한다.
  function showLoginMessage(text, failed = false) {
    const msg = $('login-msg');
    msg.hidden = false;
    msg.textContent = text;
    msg.classList.toggle('failed', failed);
  }

  // 토큰을 지우고 로그인 화면으로 돌아간다. 서버에는 아무것도 보내지 않는다(JWT라 서버에 세션이 없다). 대화
  // 화면을 비우고 환영 화면을 다시 그린다.
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

  // 로그인 또는 가입. 처리하는 동안 버튼을 잠근다. 가입이면 /auth/register(JSON) 뒤 이어서 로그인한다.
  // 로그인은 OAuth2 password 흐름 규약대로 폼 형식(URLSearchParams)으로 username=이메일, password를 보낸다.
  // 받은 접근 토큰을 저장하고 비밀번호 칸을 비운 뒤 대화 화면으로 들어간다.
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

  // 상단 상태 줄: /health로 검색 방식과 답변 모델을 보이고, DB 연결이 안 되면 그것도 알린다.
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

  // 질문 칸 높이를 내용에 맞춰 늘린다(최대 160px, CSS의 max-height 10rem과 같은 크기). 높이를 auto로 되돌린
  // 뒤 scrollHeight를 재야 줄어드는 경우도 맞게 계산된다.
  function autoGrow() {
    questionBox.style.height = 'auto';
    questionBox.style.height = Math.min(questionBox.scrollHeight, 160) + 'px';
  }

  /* ---------- 이벤트 연결 ---------- */

  // 이벤트 연결. 로그인 폼 제출은 페이지 이동을 막고 로그인한다. 계정 만들기는 submit 버튼이 아니라서
  // reportValidity로 브라우저 기본 검사(필수 입력, 이메일 형식)를 직접 돌린 뒤 가입한다.
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
  // Enter는 보내기, Shift+Enter는 줄바꿈. 한글 입력기 조합 중의 Enter는 무시한다.
  questionBox.addEventListener('keydown', (e) => {
    // 한글 입력기가 아직 음절을 조합하는 중이면 Enter는 그 글자를 확정할 뿐이다. 브라우저는 이를
    // isComposing으로 알려 주고, 일부 브라우저(Safari)는 keyCode 229로만 알려 준다.
    if (e.isComposing || e.keyCode === 229) return;
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      ask(questionBox.value);
    }
  });
  questionBox.addEventListener('input', autoGrow);

  // 시작: 서버 상태를 띄우고, 같은 탭에 저장된 토큰이 있으면 바로 대화 화면으로, 없으면 환영 화면을 보인다.
  loadStatus();
  if (token) {
    enterChat();
  } else {
    renderWelcome();
  }
})();

"""스키마로 강제한 구조화 인용이 붙은 답변 생성.

서로 바꿔 끼울 수 있는 두 제공자를 한 인터페이스 뒤에 둔다:
- Anthropic: `tool_choice`로 `cite_answer` 도구 호출을 강제한다.
- Ollama: Ollama의 `format`(제약 디코딩)으로 같은 JSON 스키마를 강제한다.

둘 다 자유 텍스트를 파싱하지 않고도 스키마에 맞는 인용을 보장하므로, `/query/ask`는 어느 쪽이 연결돼
있는지 신경 쓸 필요가 없다.
"""

# [파일 역할] 검색된 청크를 근거로 LLM 답변과 인용(근거 청크 번호)을 만드는 생성 단계. 로컬 Ollama와 Claude
# API 두 제공자를 같은 인터페이스(GenerationService.answer) 뒤에 둔다.
# [설계 이유]
# - 인용을 자유 텍스트에서 파싱하지 않고 JSON 스키마로 강제한다(README '인용을 스키마로 강제'). Claude는
#   tool_choice로 도구 호출을, Ollama는 format(제약 디코딩)으로 스키마를 따르게 한다.
# - Ollama 경로만 호출을 두 번으로 나눈다. 로컬 7B 모델이 제약 디코딩 중 문자열 안의 따옴표를 이스케이프하지
#   못해 코드가 든 답이 잘렸기 때문에, 답변은 자유 텍스트로 받고 인용(숫자 목록)만 따로 스키마로 받는다.
# - 한국어 질문에만 한국어 답변 규칙을 붙이고, 한국어 답에 한자·가나가 섞이면 한 번 다시 만드는 언어 가드를
#   둔다(v8, v13).
# - 생성기를 쓸 수 없을 때(연결 실패·시간 초과·모델 없음)는 GenerationUnavailableError(code)로 바꿔 올린다.
#   /query/ask는 이것을 503 + Retry-After로 응답하고(app/main.py), 채팅 화면은 code마다 다른 안내를 보인다.
# [연결] /query/ask(app/routers/query.py)가 get_generation_service 결과를 의존성으로 받아 answer를 부른다.
# 평가(eval/run_answer_eval.py)도 같은 생성기를 strict_citations=False로 만들어 쓰고, 프롬프트 상수를 가져다
# 토큰 수를 센다. 판정 호출(eval/judge.py, eval/run_judge.py)은 이 파일의 공유 SSL 컨텍스트를 함께 쓴다.

from __future__ import annotations

import json
import re
import ssl
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import cache, lru_cache

# httpx: Ollama REST API(/api/chat)를 비동기로 부른다. AsyncAnthropic: Claude Messages API 비동기 클라이언트.
# API*Error: Claude SDK 예외(연결 실패·시간 초과·HTTP 상태 오류)를 생성기 장애로 바꿀 때 가른다.
# RetrievedChunk: 검색 결과 청크(본문·헤딩)를 프롬프트로 만들 때 쓴다.
import httpx
from anthropic import APIConnectionError, APIError, APIStatusError, APITimeoutError, AsyncAnthropic

from app.config import get_settings
from app.services.language import Language
from app.services.retrieval import RetrievedChunk

# 두 제공자가 공유하는 기본 지시: 주어진 번호 붙은 문맥만 근거로 답하고, 근거가 부족하면 추측하지 말고
# 모른다고 하라. 환각을 줄이려는 RAG의 기본 규칙이다. 영어 프롬프트 문장은 테스트로 고정돼 있다(v8에서
# 프롬프트 한 줄 때문에 영어 정확도가 떨어진 일이 있었다).
BASE_RULES = (
    "You are a documentation assistant answering questions about FastAPI using ONLY the "
    "numbered context passages provided below. Rules:\n"
    "1. Answer only using information present in the context passages.\n"
    "2. If the passages do not contain enough information to answer, say you don't know "
    "instead of guessing.\n"
)

# Claude용: cite_answer 도구를 반드시 호출하고 citations에 실제로 쓴 청크 번호를 넣으라는 규칙을 더한다.
ANTHROPIC_SYSTEM_PROMPT = BASE_RULES + (
    "3. Always call the cite_answer tool. In `citations`, list the chunk_number of every "
    "passage you actually relied on to construct the answer.\n"
)

# Ollama 답변 호출용: JSON이나 머리말 없이 답 글만 쓰라는 규칙을 더한다(인용은 다음 호출에서 따로 받는다).
OLLAMA_ANSWER_PROMPT = BASE_RULES + (
    "3. Reply with the answer text only — no JSON, no preamble.\n"
)

# 한국어 질문에만 붙이는 규칙. 처음에는 "질문과 같은 언어로 답하라"는 일반 규칙(예시로 한국어를 들었음)을
# 썼는데, 로컬 7B 모델이 영어 질문에도 한국어로 답해 영어 답변 정확도가 4.60에서 4.19로 떨어졌다.
KOREAN_ANSWER_RULE = (
    "4. Write the answer in Korean. Keep code, API names and identifiers exactly as they "
    "appear in the passages.\n"
)


# 한국어 질문이면 기본 프롬프트 뒤에 한국어 답변 규칙을 붙이고, 영어면 원래 프롬프트를 그대로 쓴다.
def system_prompt_for(prompt: str, language: Language) -> str:
    return prompt + KOREAN_ANSWER_RULE if language == "ko" else prompt


# 언어 가드(docs/experiments.md v13. v13 채택 때부터 Settings.language_guard로 기본으로 켜져 있고,
# LANGUAGE_GUARD=false로 끈다): 코드 밖에 가나나 한자가 있는 한국어 답은 KOREAN_ANSWER_RULE 대신 이 규칙을
# 넣어 한 번 더 생성한다. 문서는 이 문자들을 전혀 쓰지 않으므로, 답에 나왔다면 모델이 일본어나 중국어로 샌
# 것이다(v10~v12에서 7B 모델의 답에서 이런 경우를 봤다).
KOREAN_RETRY_RULE = (
    "4. Write the entire answer in Korean only (한국어로만 답하세요). Do not switch to Chinese "
    "or Japanese: no Chinese characters and no Japanese kana outside code. Keep code, API "
    "names and identifiers exactly as they appear in the passages.\n"
)

# 가나(U+3040~U+30FF)와 한자(U+4E00~U+9FFF) 범위. 평가 스크립트(eval/run_answer_eval.py,
# eval/generator_arms.py)도 섞인 답을 셀 때 이 정규식을 가져다 쓴다.
# _FENCED_CODE_RE·_INLINE_CODE_RE: 펜스 코드 블록과 인라인 코드. 코드 안의 한자(예: 예제 문자열)는 언어 섞임이
# 아니므로 가드 판단에서 뺀다.
KANA_HAN_RE = re.compile(r"[぀-ヿ一-鿿]")
# 닫히지 않은 펜스는 답의 끝까지를 코드로 본다.
_FENCED_CODE_RE = re.compile(r"```.*?(?:```|\Z)", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


# 답에서 코드 부분을 공백으로 바꿔 지우고 설명 글만 남긴다. 펜스 블록을 먼저 지운 뒤 인라인 코드를 지운다.
def prose_outside_code(text: str) -> str:
    return _INLINE_CODE_RE.sub(" ", _FENCED_CODE_RE.sub(" ", text))


# 한국어 질문의 답에서 코드 밖에 가나·한자가 하나라도 있으면 다시 만들어야 한다고 본다. 영어 질문에는 언제나
# False.
def needs_language_retry(answer: str, language: Language) -> bool:
    return language == "ko" and bool(KANA_HAN_RE.search(prose_outside_code(answer)))


# --- 거절(답할 근거가 없다는 답) 분류 (docs/experiments.md v15) ---
# 답이 '주어진 문서 구절에 그 내용이 없다/모른다'는 거절인지 정규식으로 가른다. 쓰임은 두 가지다.
# 1) 평가 지표: 문서에 답이 없는 질문에서 시스템이 모른다고 하는 비율(거절률)을 센다(eval/refusal.py).
# 2) 설정 EMPTY_CITATIONS_ON_REFUSAL: 거절 답에는 인용을 붙이지 않는다. 지금 인용 스키마(minItems 1)는 거절한
#    답에도 인용을 하나 이상 강제해, 화면에 '근거'가 붙은 거절이 나온다.
# 왜 첫 문장만 보나: 저장된 답을 보면 거절은 거의 늘 첫 문장에서 한다("I don't know.", "제공된 문맥에는 …에
# 대한 정보가 포함되어 있지 않습니다."). 첫 문장에서 답한 뒤 뒤쪽에서 일부만 모른다고 하는 답(부분 답)이나,
# '함께 받을 수 없습니다'처럼 '없다'가 답의 내용인 문장을 거절로 잘못 세지 않으려고 첫 문장과 '정보·내용이
# 없다' 같은 꼴로 좁혔다. 그래도 정규식이라 틀릴 수 있으므로, 평가는 이 분류와 함께 판정 모델 점수를 보고한다.
# 2026-10-18 보강(docs/experiments.md v15 규칙 변경, I4 test 전): dev 답에서 놓친 거절 꼴 두 가지를 더했다.
# A.X가 영어로 쓰는 "You don't know."와, 한국어 "…정보는 제공되지 않았습니다", "…정보를 제공하지 않습니다"처럼
# '제공·설명·언급되지(하지) 않'는다는 꼴이다. 저장된 답 약 500개에 대 보면 새로 걸리는 답은 모두 거절이었다.
_REFUSAL_PATTERNS: dict[str, re.Pattern] = {
    "en": re.compile(
        r"\b(?:(?:i|you) (?:do not|don't) know"
        r"|(?:do|does|did) not (?:contain|include|mention|cover|provide|specify|say|describe|explain|address)"
        r"|(?:don't|doesn't|didn't) "
        r"(?:contain|include|mention|cover|provide|specify|say|describe|explain|address)"
        r"|no (?:information|details|mention|explanation)"
        r"|not (?:mentioned|covered|provided|specified|described|explained|addressed|found|available) in"
        r"|(?:cannot|can't|unable to) (?:answer|find|determine|tell)"
        r"|(?:not enough|insufficient) (?:information|context|detail))",
        re.IGNORECASE,
    ),
    "ko": re.compile(
        r"(?:모르겠|모릅니다|알 수 없"
        r"|(?:정보|내용|언급|설명|방법|자료|답)(?:이|가|은|는|도)?\s?(?:없|부족)"
        r"|(?:나와|언급되어|포함되어|제공되어|설명되어|나타나|기술되어|다뤄지|다루어지|명시되어|소개되어)\s?있지\s?않"
        r"|다루지\s?않|찾을 수 없|(?:답|답변|확인)(?:하기|할 수)\s?(?:없|어렵)"
        r"|(?:제공|설명|언급|포함|기술|명시|소개|안내)(?:되|하)지\s?않)"
    ),
}
# 첫 문장의 끝: 마침표·물음표·느낌표 뒤 공백, 또는 줄바꿈. 300자를 넘으면 거기서 자른다(한 문장이 아주 길게
# 이어지는 답에서 뒤쪽의 부분 거절을 잡지 않으려고).
_SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s|\n")
FIRST_SENTENCE_MAX_CHARS = 300


# 답의 첫 문장(코드 블록을 지우고 앞뒤 공백을 뗀 뒤)을 돌려준다.
def first_sentence(answer: str) -> str:
    text = prose_outside_code(answer).strip()
    match = _SENTENCE_END_RE.search(text)
    sentence = text[: match.start()] if match else text
    return sentence[:FIRST_SENTENCE_MAX_CHARS]


# 거절 답이면 True. 질문 언어의 패턴으로 첫 문장만 본다(영어 질문은 영어 패턴, 한국어 질문은 한국어 패턴).
def is_refusal_answer(answer: str, language: Language) -> bool:
    pattern = _REFUSAL_PATTERNS["ko" if language == "ko" else "en"]
    return bool(pattern.search(first_sentence(answer)))


# 설정 REFUSE_WITHOUT_CONTEXT가 켜져 있고 검색된 청크가 0개일 때 LLM 대신 돌려주는 고정 거절문(질문 언어별).
# 근거가 하나도 없으면 모델은 지식으로 답을 지어낼 수밖에 없으므로 부르지 않는다. 사용자에게 보이는 문장이라
# 짧고 분명하게 쓰고, 위 거절 분류기에 걸리는지 테스트로 고정한다(tests/test_generation.py).
NO_CONTEXT_REFUSAL: dict[str, str] = {
    "en": "I don't know: the documentation passages I found do not cover this question.",
    "ko": "모르겠습니다. 찾은 문서 구절에는 이 질문에 대한 내용이 없습니다.",
}

# Ollama 두 번째 호출(인용 추출)용 지시: 질문·번호 붙은 문맥·이미 쓴 답을 보고 답이 실제로 기댄 [N] 번호를
# 돌려준다.
OLLAMA_CITATION_PROMPT = (
    "Given a question, numbered context passages, and an answer that was written from them, "
    "report which passages the answer actually relied on. Return their [N] numbers."
)

# 인용 호출의 출력 스키마: chunk_number 정수를 담은 객체 배열, 최소 1개. Ollama format에 넘겨 제약 디코딩으로
# 이 모양만 나오게 한다. 숫자만 있으므로 따옴표 이스케이프 문제가 생기지 않는다.
CITATIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "citations": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {"chunk_number": {"type": "integer"}},
                "required": ["chunk_number"],
            },
        }
    },
    "required": ["citations"],
}


# 인용 호출을 답변 대화에 이어 붙이는 모드(설정 CITATION_MODE=followup, docs/experiments.md v15 후보)에서 쓰는
# 마지막 사용자 메시지와 출력 스키마.
# - 왜: 따로 부르는 인용 호출(separate)은 다른 system 프롬프트로 시작해 질문·문맥 약 1,600토큰을 처음부터 다시
#   읽는다. 답변 호출과 같은 system·user 메시지 뒤에 모델이 쓴 답과 이 질문을 이어 붙이면, 앞부분이 Ollama의
#   프롬프트 캐시와 같아 다시 읽지 않아도 된다.
# - 출력도 객체 배열({"chunk_number": N}) 대신 정수 배열로 줄여 출력 토큰을 줄인다. 숫자만이라 따옴표 문제는
#   여전히 없다. 아래 문장은 모델에게 그대로 가는 글이라 영어 원문을 유지한다.
CITATION_FOLLOWUP_PROMPT = (
    "Which of the numbered context passages did your answer above rely on? "
    "Reply with their [N] numbers."
)
COMPACT_CITATIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "citations": {"type": "array", "minItems": 1, "items": {"type": "integer"}},
    },
    "required": ["citations"],
}


# 인용 응답이 스키마를 어기는 이유를 문자열로 돌려준다(맞으면 None). bool은 파이썬에서 int의 하위 타입이라
# 따로 걸러 낸다. 앱 동작에는 영향이 없고, 평가가 스키마를 지킨 응답 수를 세는 데 쓴다(eval/answer_report.py).
# compact=True면 이어 붙이기 모드의 정수 배열 스키마(COMPACT_CITATIONS_SCHEMA)로 본다.
def citation_schema_error(reply: str, compact: bool = False) -> str | None:
    """인용 응답이 CITATIONS_SCHEMA(또는 compact면 COMPACT_CITATIONS_SCHEMA)를 어기는 이유. 맞으면 None.

    기록용일 뿐이다(답변 평가가 스키마를 지킨 응답 수를 센다). 앱은 응답을 늘 하던 대로 파싱한다.
    """
    try:
        parsed = json.loads(reply)
    except ValueError:
        return "not JSON"
    if not isinstance(parsed, dict) or not isinstance(parsed.get("citations"), list):
        return "no citations array"
    if not parsed["citations"]:
        return "empty citations array"
    for item in parsed["citations"]:
        if compact:
            number = item
        else:
            number = item.get("chunk_number") if isinstance(item, dict) else None
        if not isinstance(number, int) or isinstance(number, bool):
            return "citation number is not an integer" if compact else "chunk_number is not an integer"
    return None


# 인용 응답에서 [N] 번호 목록을 꺼낸다. 형식이 틀리면 예외(ValueError·KeyError·TypeError·AttributeError)를
# 낸다.
# - 기본(separate): {"chunk_number": N} 객체 배열. 예전 코드와 똑같이 파싱한다(citations 키가 없으면 빈 목록).
# - compact(followup): 정수 배열. 제약 디코딩이 스키마를 지키게 하지만, 정수가 아닌 값(bool 포함)이 오면
#   TypeError로 거른다.
def parse_citations(reply: str, compact: bool = False) -> list[int]:
    parsed = json.loads(reply)
    if not compact:
        return [c["chunk_number"] for c in parsed.get("citations", [])]
    numbers = parsed["citations"]
    if any(not isinstance(n, int) or isinstance(n, bool) for n in numbers):
        raise TypeError("citation numbers must be integers")
    return list(numbers)


# Claude 도구 입력 스키마: 답 글(answer)과 인용 배열(citations)을 한 번에 받는다.
ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string", "description": "The answer to the user's question."},
        "citations": {
            "type": "array",
            # minItems로 스키마 제약 디코딩이 인용을 최소 하나는 내게 한다. 그러지 않으면 작은 로컬 모델은
            # 빈 배열로 스키마를 만족시켜 버린다.
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "chunk_number": {
                        "type": "integer",
                        "description": "The [N] label of a context passage that was used.",
                    }
                },
                "required": ["chunk_number"],
            },
        },
    },
    "required": ["answer", "citations"],
}

# Claude에게 주는 도구 정의. tool_choice로 이 도구를 강제하면 응답이 항상 ANSWER_SCHEMA 모양의 도구 입력으로
# 온다.
CITE_ANSWER_TOOL = {
    "name": "cite_answer",
    "description": "Return the answer to the user's question along with the passages used.",
    "input_schema": ANSWER_SCHEMA,
}


# --- 생성기 호출 경로: 공유 SSL 컨텍스트와 생성기 장애 ---

# Ollama 호출(생성, 판정, 상태 읽기)이 함께 쓰는 SSL 컨텍스트를 프로세스당 한 번만 만든다.
# - 왜: httpx는 클라이언트(기본 transport)를 만들 때마다 기본 SSL 컨텍스트를 새로 만들며 certifi CA 번들을
#   동기로 읽는다. 이 모듈은 호출마다 클라이언트를 열므로 그 일이 호출마다 일어났고, Windows 호스트에서 호출당
#   CPU 약 0.3초(부하 때는 그 이상)가 들면서 그동안 이벤트 루프 전체가 멈췄다. 기록된 호스트 생성·인용·판정
#   시간에도 이 비용이 들어 있다(docs/experiments.md '기타 관찰'). Ollama 기본 주소는 http라 이 컨텍스트는
#   쓰이지도 않는다. 미리 만든 컨텍스트를 verify=로 넘기면 클라이언트 생성은 1ms 안쪽이다.
# - 클라이언트 대신 컨텍스트만 공유하는 이유: AsyncClient(연결 풀)는 만든 이벤트 루프에 묶여, 테스트마다 새
#   루프를 쓰는 pytest나 asyncio.run을 여러 번 부르는 평가 스크립트 사이에서 공유하면 문제가 되고 닫는 처리도
#   따로 필요하다. 반면 keep-alive로 아끼는 localhost 연결은 1ms 안팎이다. SSL 컨텍스트는 이벤트 루프와
#   상관없이 여러 연결이 함께 써도 된다.
# - verify=False는 쓰지 않는다. OLLAMA_BASE_URL을 https로 둔 배포에서 인증서 검증이 꺼지기 때문이다.
#   httpx.create_ssl_context()는 클라이언트 기본값과 같은 검증 컨텍스트(certifi 번들,
#   SSL_CERT_FILE·SSL_CERT_DIR 환경 변수가 있으면 그것)를 만든다.
# 주의: 처음 부를 때의 환경 변수로 정해져 프로세스가 끝날 때까지 바뀌지 않는다. 모든 호출이 같은 객체를 쓰므로
# 읽기만 하고 고치지 않는다(예: load_cert_chain을 부르면 모든 호출에 퍼진다).
@cache
def ollama_ssl_context() -> ssl.SSLContext:
    """Ollama 호출이 함께 쓰는 검증용 SSL 컨텍스트. 처음 부를 때 한 번 만든다."""
    return httpx.create_ssl_context()


# 생성기 장애 code와 503 응답의 detail.message. 생성기(LLM 서버)를 쓸 수 없어 답을 못 만든 경우를 셋으로
# 나눈다. app/main.py가 503 JSON {"detail": {"code", "message"}}와 Retry-After 헤더로 바꾸고, 채팅
# 화면(app/web/static/chat.js)은 code마다 다른 안내를 보인다(tests/test_web.py가 code 목록이 화면에 모두
# 있는지 확인). 문구는 API 응답으로 그대로 나가는 글이라 다른 API 오류 문구처럼 영어로 둔다.
# - generator_unavailable: 연결 실패, 생성기의 5xx(Ollama 모델 실행기 중단, Claude 과부하 529 등)
# - generator_timeout: 한 호출의 제한 시간(Ollama는 180초)을 넘김
# - generator_model_missing: 설정한 모델이 서버에 없음(Ollama 404). README 설치 절대로 A.X 모델을 직접
#   만들어야 해서, 모델 태그를 아직 만들지 않은 것이 가장 흔한 첫 실패다.
GENERATOR_ERROR_MESSAGES: dict[str, str] = {
    "generator_unavailable": "The answer generator could not be reached or failed. Try again later.",
    "generator_timeout": "The answer generator did not respond in time. Try again later.",
    "generator_model_missing": "The configured generation model is not available on the generator server.",
}

# 503 응답의 Retry-After(초). 다시 띄운 Ollama가 모델을 올리고 첫 답을 내기까지 README '화면'의 첫 질문에서
# 15.8초가 걸렸으므로 그보다 넉넉한 30초로 둔다. 잰 회복 시간이 아니라, 클라이언트가 곧바로 되풀이해 보내지
# 않게 하는 안내값이다.
GENERATION_RETRY_AFTER_SECONDS = 30

# 업스트림 오류 본문을 원인 요약(upstream)에 넣을 때의 최대 글자 수. Ollama 오류 본문은 {"error": "..."} 한
# 줄이라 충분하고, 예상 밖의 큰 본문(HTML 오류 페이지 등)이 로그를 채우지 않게 자른다.
UPSTREAM_TEXT_LIMIT = 300


class GenerationUnavailableError(RuntimeError):
    """생성기(LLM 서버)를 쓸 수 없어 답을 만들지 못했다. /query/ask는 이것을 503으로 응답한다.

    code: GENERATOR_ERROR_MESSAGES의 키. 다른 값이면 ValueError를 낸다(응답 계약 밖의 code를 막으려고).
    upstream: 원인 요약(업스트림 HTTP 상태와 오류 본문 앞부분, 또는 예외 이름과 문구). 서버 로그와 예외
        문구(평가 스크립트의 트레이스백)에만 쓰고 HTTP 응답에는 싣지 않는다.
    retry_after: 503 응답의 Retry-After(초).
    원래 예외는 `raise ... from`으로 __cause__에 남긴다.
    """

    def __init__(
        self, code: str, *, upstream: str = "", retry_after: int = GENERATION_RETRY_AFTER_SECONDS
    ) -> None:
        if code not in GENERATOR_ERROR_MESSAGES:
            raise ValueError(f"unknown generator error code {code!r}")
        super().__init__(f"{code}: {upstream}" if upstream else code)
        self.code = code
        self.upstream = upstream
        self.retry_after = retry_after

    # 503 응답의 detail.message(영어 고정 문구).
    @property
    def message(self) -> str:
        return GENERATOR_ERROR_MESSAGES[self.code]


# Ollama 호출의 httpx 예외를 생성기 장애로 바꾼다. 장애로 보지 않을 예외면 None을 돌려줘 호출한 쪽이 원래
# 예외를 그대로 올리게 한다.
# - 시간 초과(TimeoutException: 연결·읽기·쓰기·풀 대기) → generator_timeout
# - HTTP 404 → generator_model_missing (Ollama /api/chat은 모델 태그가 없으면 404와 "model ... not found")
# - HTTP 5xx → generator_unavailable
# - 404가 아닌 4xx → None. 요청 본문이나 think 설정처럼 이쪽 요청의 문제라, 503 뒤에 숨기지 않고 500과
#   트레이스백으로 드러나게 한다.
# - 그 밖의 전송 오류(ConnectError 등, Ollama가 꺼졌거나 주소가 틀림) → generator_unavailable
def _ollama_unavailable(exc: httpx.HTTPError) -> GenerationUnavailableError | None:
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        upstream = f"Ollama HTTP {status}: {exc.response.text[:UPSTREAM_TEXT_LIMIT]}"
        if status == 404:
            return GenerationUnavailableError("generator_model_missing", upstream=upstream)
        if status >= 500:
            return GenerationUnavailableError("generator_unavailable", upstream=upstream)
        return None
    upstream = f"{type(exc).__name__}: {exc}"
    if isinstance(exc, httpx.TimeoutException):
        return GenerationUnavailableError("generator_timeout", upstream=upstream)
    return GenerationUnavailableError("generator_unavailable", upstream=upstream)


# Claude SDK 예외를 생성기 장애로 바꾼다(Ollama와 같은 code). 장애로 보지 않을 예외면 None.
# - APITimeoutError → generator_timeout. APIConnectionError의 하위 클래스라 먼저 본다.
# - APIConnectionError → generator_unavailable
# - HTTP 404 → generator_model_missing (모델 이름이 없음), HTTP 5xx(529 과부하 포함) → generator_unavailable
# - 나머지(400 잘못된 요청, 401 키 오류, 403, 413, 422, 429 한도 초과, 응답 검증 오류) → None. 우리
#   요청·설정의 문제를 503으로 숨기지 않으려고 넓게 묶지 않는다. SDK는 연결 오류·429·5xx를 스스로 몇 번 다시
#   시도한 뒤에 예외를 내므로, 여기 오는 것은 재시도가 다 실패한 경우다.
def _claude_unavailable(exc: APIError) -> GenerationUnavailableError | None:
    upstream = f"{type(exc).__name__}: {str(exc)[:UPSTREAM_TEXT_LIMIT]}"
    if isinstance(exc, APITimeoutError):
        return GenerationUnavailableError("generator_timeout", upstream=upstream)
    if isinstance(exc, APIConnectionError):
        return GenerationUnavailableError("generator_unavailable", upstream=upstream)
    if isinstance(exc, APIStatusError):
        if exc.status_code == 404:
            return GenerationUnavailableError("generator_model_missing", upstream=upstream)
        if exc.status_code >= 500:
            return GenerationUnavailableError("generator_unavailable", upstream=upstream)
    return None


# 생성 결과. answer는 답 글, cited_chunk_numbers는 1부터 시작하는 [N] 번호 목록, 토큰 수와 모델 이름은 질문
# 기록(query_logs)에 저장된다.
@dataclass
class GenerationResult:
    answer: str
    cited_chunk_numbers: list[int]
    input_tokens: int
    output_tokens: int
    model_name: str
    # 답변 평가가 기록하는 제공자별 세부 정보(호출마다의 토큰 수, 멈춘 이유, 언어 가드). 앱은 읽지 않는다.
    diagnostics: dict = field(default_factory=dict)


# 검색된 청크를 '[번호] (헤딩 경로)' + 본문 형태로 이어 붙인 문맥 블록. 번호는 1부터이고, 모델이 돌려준 인용
# 번호를 다시 청크로 바꿀 때 이 순서를 쓴다.
def _build_context_block(chunks: list[RetrievedChunk]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        heading = chunk.heading_path or "(no heading)"
        parts.append(f"[{i}] ({heading})\n{chunk.content}")
    return "\n\n".join(parts)


# 사용자 메시지: 문맥 블록을 먼저, 질문을 마지막에 둔다.
def _build_user_message(question: str, chunks: list[RetrievedChunk]) -> str:
    return f"Context passages:\n\n{_build_context_block(chunks)}\n\nQuestion: {question}"


# 생성기 공통 인터페이스. 라우터는 이 타입만 알고, 어느 제공자인지는 설정이 정한다. 테스트는 이것을 상속한
# 가짜 생성기를 끼운다(tests/conftest.py).
class GenerationService(ABC):
    @abstractmethod
    async def answer(
        self, question: str, chunks: list[RetrievedChunk], language: Language = "en"
    ) -> GenerationResult: ...


# Claude API 생성기. 한 번의 호출로 답과 인용을 함께 받는다. README에 적힌 대로 코드와 단위 테스트만 있고 실제
# API로는 돌려 보지 않았다(크레딧 없음).
class AnthropicGenerationService(GenerationService):
    # refuse_without_context·empty_citations_on_refusal은 Ollama 생성기와 같은 v15 설정이다(기본 꺼짐). 이
    # 경로는 인용을 답과 한 번에 받으므로, 거절 답이면 받은 인용을 비우기만 한다.
    def __init__(
        self,
        api_key: str,
        model_name: str,
        *,
        refuse_without_context: bool = False,
        empty_citations_on_refusal: bool = False,
    ) -> None:
        self._client = AsyncAnthropic(api_key=api_key)
        self._model_name = model_name
        self._refuse_without_context = refuse_without_context
        self._empty_citations_on_refusal = empty_citations_on_refusal

    async def answer(
        self, question: str, chunks: list[RetrievedChunk], language: Language = "en"
    ) -> GenerationResult:
        if self._refuse_without_context and not chunks:
            return GenerationResult(
                answer=NO_CONTEXT_REFUSAL["ko" if language == "ko" else "en"],
                cited_chunk_numbers=[],
                input_tokens=0,
                output_tokens=0,
                model_name=self._model_name,
                diagnostics={"refused_without_context": True},
            )
        # tool_choice로 cite_answer 도구를 강제해, 모델이 자유 텍스트 대신 스키마에 맞는 도구 입력을 내게
        # 한다. 출력은 최대 1024토큰. 연결 실패·시간 초과·404·5xx는 GenerationUnavailableError로 바꾸고(503),
        # 나머지 SDK 오류는 그대로 올린다(_claude_unavailable).
        try:
            response = await self._client.messages.create(
                model=self._model_name,
                max_tokens=1024,
                system=system_prompt_for(ANTHROPIC_SYSTEM_PROMPT, language),
                tools=[CITE_ANSWER_TOOL],
                tool_choice={"type": "tool", "name": "cite_answer"},
                messages=[{"role": "user", "content": _build_user_message(question, chunks)}],
            )
        except APIError as exc:
            unavailable = _claude_unavailable(exc)
            if unavailable is None:
                raise
            raise unavailable from exc

        # 응답 내용 중 도구 호출 블록을 찾아 그 입력(answer, citations)을 꺼낸다.
        tool_use_block = next(block for block in response.content if block.type == "tool_use")
        tool_input = tool_use_block.input
        cited = [c["chunk_number"] for c in tool_input.get("citations", [])]
        if self._empty_citations_on_refusal and is_refusal_answer(tool_input["answer"], language):
            cited = []

        return GenerationResult(
            answer=tool_input["answer"],
            cited_chunk_numbers=cited,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            model_name=self._model_name,
        )


class OllamaGenerationService(GenerationService):
    """로컬 생성. 호출을 두 번으로 나눈다.

    7B 모델은 JSON 스키마 제약 디코딩 중에 문자열 값 안의 따옴표를 믿을 만하게 이스케이프하지 못해, 코드가
    든 답이 첫 `"`에서 잘린다. 답 글은 자유 텍스트로 생성하고, 인용은 숫자만 담는 스키마로 두 번째 호출에서
    뽑으면 이 문제를 아예 피한다.

    v13에서 더한 옵션(docs/experiments.md). 모두 기본값에서는 아무 영향이 없다:
    - `think`: 값이 있으면 Ollama의 `think` 필드로 보낸다(False면 qwen3.5 같은 모델이 기본으로 하는 추론을
      끈다). None이면 필드를 보내지 않는다.
    - `language_guard`: 코드 밖에 가나나 한자가 있는 한국어 답을 KOREAN_RETRY_RULE로 한 번 더 생성한다.
      인용은 최종 답을 기준으로 받는다.
    - `strict_citations=False`(답변 평가용): 스키마를 어긴 인용 응답에서 예외를 내는 대신 기록해, 한 번의
      실행에서 그런 응답 수를 셀 수 있게 한다.

    v15 후보(docs/experiments.md v15). 셋 다 기본값은 지금 동작이다:
    - `citation_mode="followup"`: 인용 호출을 답변 대화에 이어 붙이고 정수 배열 스키마로 받는다("separate"는
      예전처럼 다른 system 프롬프트로 따로 부른다).
    - `refuse_without_context=True`: 검색된 청크가 0개면 LLM을 부르지 않고 NO_CONTEXT_REFUSAL을 돌려준다.
    - `empty_citations_on_refusal=True`: 거절로 분류된 답(is_refusal_answer)은 인용 호출 없이 인용을 비운다.
    """

    # CONTEXT_TOKENS: 요청마다 num_ctx로 문맥 크기를 8192로 지정한다. MAX_OUTPUT_TOKENS: 답 길이
    # 상한(num_predict 1024). 문맥 8192 중 1024는 답에 쓰이는 셈이다(docs/experiments.md v11의 계산).
    # Ollama 기본 문맥은 4096토큰인데, 검색된 문맥만으로도 거의 찰 수 있어 답을 쓸 자리가 남지 않는다.
    CONTEXT_TOKENS = 8192
    MAX_OUTPUT_TOKENS = 1024

    # base_url: Ollama 서버 주소, model_name: Ollama 모델 태그, timeout: 한 호출의 제한 시간(초, 기본 180).
    # 나머지 세 옵션은 위 docstring 참고. 앱은 설정의 think·language_guard를 넘기고, 평가는
    # strict_citations=False를 더한다.
    def __init__(
        self,
        base_url: str,
        model_name: str,
        timeout: float = 180.0,
        *,
        think: bool | None = None,
        language_guard: bool = False,
        strict_citations: bool = True,
        citation_mode: str = "separate",
        refuse_without_context: bool = False,
        empty_citations_on_refusal: bool = False,
    ) -> None:
        if citation_mode not in ("separate", "followup"):
            raise ValueError(f"unknown citation_mode {citation_mode!r}")
        self._base_url = base_url.rstrip("/")
        self._model_name = model_name
        self._timeout = timeout
        self._think = think
        self._language_guard = language_guard
        self._strict_citations = strict_citations
        self._citation_mode = citation_mode
        self._refuse_without_context = refuse_without_context
        self._empty_citations_on_refusal = empty_citations_on_refusal

    # Ollama /api/chat를 한 번 부른다(스트리밍 없이 완성된 응답 하나).
    # - temperature 0: 같은 입력에 최대한 같은 답이 나오게 해 평가를 반복할 수 있게 한다(docs/experiments.md
    #   v13에 따르면 그래도 실행마다 완전히 같지는 않았다).
    # - response_schema가 있으면 format으로 넘겨 제약 디코딩을 켠다(인용 호출만).
    # - think는 설정됐을 때만 보낸다. 값이 없으면 v13 이전과 똑같은 요청이 된다.
    # 호출마다 클라이언트를 새로 열되, 인증서 번들은 프로세스에서 한 번만 읽는다(공유 SSL 컨텍스트
    # ollama_ssl_context. 호출마다 읽던 때는 Windows 호스트에서 호출당 CPU 약 0.3초였다). 요청 본문은
    # 그대로다. HTTP 오류는 raise_for_status로 예외가 되고, 생성기 장애(연결 실패·시간 초과·404·5xx)는
    # GenerationUnavailableError로 바꿔 올린다(_ollama_unavailable). 404가 아닌 4xx는 원래 예외 그대로다.
    async def _chat(self, messages: list[dict], response_schema: dict | None) -> dict:
        payload = {
            "model": self._model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0,
                "num_ctx": self.CONTEXT_TOKENS,
                "num_predict": self.MAX_OUTPUT_TOKENS,
            },
        }
        if response_schema is not None:
            payload["format"] = response_schema
        if self._think is not None:
            payload["think"] = self._think

        try:
            async with httpx.AsyncClient(timeout=self._timeout, verify=ollama_ssl_context()) as client:
                response = await client.post(f"{self._base_url}/api/chat", json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            unavailable = _ollama_unavailable(exc)
            if unavailable is None:
                raise
            raise unavailable from exc

    # _chat에 호출별 진단을 더한다: 실제로 읽은 프롬프트 토큰 수(prompt_eval_count), 출력 토큰 수(eval_count),
    # 끝난 이유(done_reason, length면 1024토큰에서 잘린 것), 추론 출력 길이, 걸린 시간(ms). 앱은 쓰지 않고
    # 평가가 문항별로 기록한다.
    async def _timed_chat(self, messages: list[dict], response_schema: dict | None) -> tuple[dict, dict]:
        start = time.perf_counter()
        data = await self._chat(messages, response_schema)
        message = data.get("message") or {}
        stats = {
            "prompt_eval_count": data.get("prompt_eval_count"),
            "eval_count": data.get("eval_count"),
            "done_reason": data.get("done_reason"),
            "thinking_chars": len(message.get("thinking") or ""),
            "ms": (time.perf_counter() - start) * 1000,
        }
        return data, stats

    # 답변 호출 메시지: 시스템 메시지(규칙) + 사용자 메시지(문맥 + 질문).
    def _answer_messages(self, question: str, chunks: list[RetrievedChunk], rule_set: str) -> list[dict]:
        return [
            {"role": "system", "content": rule_set},
            {"role": "user", "content": _build_user_message(question, chunks)},
        ]

    async def answer(
        self, question: str, chunks: list[RetrievedChunk], language: Language = "en"
    ) -> GenerationResult:
        # 0) 청크 0개 거절(REFUSE_WITHOUT_CONTEXT, 기본 꺼짐): 근거가 하나도 없으면 LLM을 부르지 않는다.
        #    토큰은 쓰지 않았으므로 0이다.
        if self._refuse_without_context and not chunks:
            return GenerationResult(
                answer=NO_CONTEXT_REFUSAL["ko" if language == "ko" else "en"],
                cited_chunk_numbers=[],
                input_tokens=0,
                output_tokens=0,
                model_name=self._model_name,
                diagnostics={
                    "think": self._think,
                    "guard_applied": False,
                    "refused_without_context": True,
                    "citation_mode": self._citation_mode,
                    "citation_call": None,
                    "citation_schema_error": None,
                    "citation_skipped": "no_context",
                },
            )

        context_block = _build_context_block(chunks)

        # 1) 답변 호출: 스키마 없이 자유 텍스트로 받는다. 그래서 코드 속 따옴표가 있어도 잘리지 않는다.
        # final_messages·final_raw는 최종 답을 만든 요청과 모델이 보낸 원문으로, 이어 붙이기 인용 호출이 쓴다.
        final_messages = self._answer_messages(
            question, chunks, system_prompt_for(OLLAMA_ANSWER_PROMPT, language)
        )
        answer_data, answer_stats = await self._timed_chat(final_messages, response_schema=None)
        final_raw = answer_data["message"]["content"]
        answer_text = final_raw.strip()
        answer_calls = [answer_stats]
        replies = [answer_data]
        diagnostics: dict = {
            "think": self._think,
            "guard_applied": False,
            "citation_mode": self._citation_mode,
        }

        # 2) 언어 가드(설정 LANGUAGE_GUARD, v13 채택 뒤 기본 켬): 한국어 답의 설명 글에 한자·가나가 있으면
        #    한국어 규칙을 더 강하게 쓴 KOREAN_RETRY_RULE로 한 번만 다시 만든다. 다시 만든 답을 최종 답으로
        #    쓰고, 가드 전 답과 재시도 시간은 진단에 남긴다. v13 채택 측정에서 A.X-4.0-Light는 한국어 155문항
        #    동안 가드가 한 번도 걸리지 않았다(docs/experiments.md v13).
        if self._language_guard and needs_language_retry(answer_text, language):
            final_messages = self._answer_messages(
                question, chunks, OLLAMA_ANSWER_PROMPT + KOREAN_RETRY_RULE
            )
            retry_data, retry_stats = await self._timed_chat(final_messages, response_schema=None)
            diagnostics.update(
                guard_applied=True, unguarded_answer=answer_text, guard_retry_ms=retry_stats["ms"]
            )
            final_raw = retry_data["message"]["content"]
            answer_text = final_raw.strip()
            answer_calls.append(retry_stats)
            replies.append(retry_data)

        diagnostics.update(
            answer_calls=answer_calls,
            think_tag_in_answer=any(
                "<think>" in r["message"]["content"] or "</think>" in r["message"]["content"]
                for r in replies
            ),
        )

        # 3) 거절 답의 인용 비우기(EMPTY_CITATIONS_ON_REFUSAL, 기본 꺼짐): 최종 답이 거절이면 인용 호출을 하지
        #    않는다. 기댄 구절이 없다는 답에 '근거'를 붙이지 않으려는 것이다.
        if self._empty_citations_on_refusal and is_refusal_answer(answer_text, language):
            diagnostics.update(citation_call=None, citation_schema_error=None, citation_skipped="refusal")
            return GenerationResult(
                answer=answer_text,
                cited_chunk_numbers=[],
                input_tokens=sum(c.get("prompt_eval_count", 0) for c in replies),
                output_tokens=sum(c.get("eval_count", 0) for c in replies),
                model_name=self._model_name,
                diagnostics=diagnostics,
            )

        # 4) 인용 호출. 답이 기댄 청크 번호만 스키마로 받는다.
        # - separate(기본): 다른 system 프롬프트로 질문·문맥·최종 답을 다시 보여 주고 CITATIONS_SCHEMA로
        #   받는다.
        # - followup(v15 후보): 최종 답을 만든 대화(같은 system·user) 뒤에 모델이 보낸 답 원문과 짧은 질문을
        #   붙이고 정수 배열 스키마로 받는다. 원문(final_raw)을 그대로 넣어야 토큰이 생성 때와 같아 캐시를 더
        #   길게 다시 쓸 수 있다.
        compact = self._citation_mode == "followup"
        if compact:
            citation_messages = [
                *final_messages,
                {"role": "assistant", "content": final_raw},
                {"role": "user", "content": CITATION_FOLLOWUP_PROMPT},
            ]
            schema = COMPACT_CITATIONS_SCHEMA
        else:
            citation_messages = [
                {"role": "system", "content": OLLAMA_CITATION_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Question: {question}\n\n"
                        f"Context passages:\n\n{context_block}\n\n"
                        f"Answer that was written:\n{answer_text}"
                    ),
                },
            ]
            schema = CITATIONS_SCHEMA
        citation_data, citation_stats = await self._timed_chat(citation_messages, response_schema=schema)
        # 인용 응답 파싱. 스키마 위반 이유는 기록용으로 먼저 계산해 둔다. 앱(strict_citations=True)은 JSON이
        # 깨졌으면 예외를 그대로 올리고, 평가는 빈 인용으로 계속 진행한다.
        reply = citation_data["message"]["content"]
        schema_error = citation_schema_error(reply, compact=compact)
        try:
            cited = parse_citations(reply, compact=compact)
        except (ValueError, KeyError, TypeError, AttributeError):
            if self._strict_citations:
                raise
            cited = []

        # 평가가 볼 진단: 인용 호출 통계와 스키마 위반 이유. 스키마를 어긴 경우에만 원래 인용 응답을 함께
        # 남긴다.
        diagnostics.update(citation_call=citation_stats, citation_schema_error=schema_error)
        if schema_error is not None:
            diagnostics["citation_reply"] = reply

        # 토큰 수는 이 질문에 쓴 모든 호출(답변, 가드 재시도, 인용)의 합이다. 값이 없는 응답은 0으로 센다.
        calls = [*replies, citation_data]
        return GenerationResult(
            answer=answer_text,
            cited_chunk_numbers=cited,
            input_tokens=sum(c.get("prompt_eval_count", 0) for c in calls),
            output_tokens=sum(c.get("eval_count", 0) for c in calls),
            model_name=self._model_name,
            diagnostics=diagnostics,
        )


# 설정에 맞는 생성기를 프로세스당 하나 만든다. GENERATION_PROVIDER=ollama(기본)면 Ollama 생성기에
# 모델·think·언어 가드 설정을 넘기고, 아니면 Claude 생성기를 만든다. app/dependencies.py의 get_generator가
# 이것을 돌려준다.
@lru_cache
def get_generation_service() -> GenerationService:
    settings = get_settings()
    if settings.generation_provider == "ollama":
        return OllamaGenerationService(
            settings.ollama_base_url,
            settings.ollama_model_name,
            think=settings.ollama_think,
            language_guard=settings.language_guard,
            citation_mode=settings.citation_mode,
            refuse_without_context=settings.refuse_without_context,
            empty_citations_on_refusal=settings.empty_citations_on_refusal,
        )
    return AnthropicGenerationService(
        settings.anthropic_api_key,
        settings.claude_model_name,
        refuse_without_context=settings.refuse_without_context,
        empty_citations_on_refusal=settings.empty_citations_on_refusal,
    )

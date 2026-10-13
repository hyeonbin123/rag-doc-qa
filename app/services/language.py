"""Question language detection, used to pick which docs translation to search."""

# [파일 역할] 질문이 영어인지 한국어인지 판별하고, 앱이 지원하는 문서 언어 목록을 정의한다.
# [왜 필요한가] 영어 원문과 한국어 번역은 서로 다른 임베딩 모델로 벡터를 만들었기 때문에(docs/experiments.md
# v8), 질문도 같은 언어의 모델로 임베딩하고 같은 언어의 청크에서만 찾아야 한다. 그 출발점이 질문 언어
# 판별이다.
# [연결] /query/ask(language=auto일 때), retrieval.retrieve(언어가 없을 때), 평가
# 스크립트(eval/run_retrieval_eval.py, eval/run_answer_eval.py)가 detect_language를 쓴다.
# SUPPORTED_LANGUAGES는 시작 시 모델 미리 올리기(app/main.py), 적재 언어(app/services/ingestion.py), 벡터
# SQL의 언어 검사(app/services/retrieval.py)가 쓴다.

import re
from typing import Literal

# Language: 언어 코드 타입. Literal이라 오타 난 언어 코드는 타입 검사에서 걸린다. 값은 문서 경로
# docs/<언어>/docs/와 chunks.language 열의 값과 같다.
# SUPPORTED_LANGUAGES: 적재·검색·모델 로딩을 하는 언어 목록(순서 고정 튜플).
Language = Literal["en", "ko"]
SUPPORTED_LANGUAGES: tuple[Language, ...] = ("en", "ko")

# 한글 문자 범위 세 가지: 한글 자모(U+1100~U+11FF), 호환용 자모(U+3130~U+318F, 'ㅋㅋ'처럼 자모만 쓴 글자),
# 완성형 음절(U+AC00~U+D7A3). 하나라도 있으면 한국어로 본다.
_HANGUL_RE = re.compile(r"[ᄀ-ᇿ㄰-㆏가-힣]")


# 규칙 기반 판별이라 모델 없이 즉시 끝난다. 이 서비스의 언어가 영어·한국어 둘뿐이라 '한글이 있느냐'만으로
# 충분하다. README '알려진 한계'에 적힌 대로 한글이 한 글자라도 있으면 한국어이며, 판별이 틀리면 API 요청의
# language로 직접 지정할 수 있다.
def detect_language(text: str) -> Language:
    """Korean if the text contains any Hangul, otherwise English.

    Korean questions usually mix in English API names ("HTTPException으로 404를
    반환하려면?"), so a single Hangul character is enough to call it Korean.
    """
    return "ko" if _HANGUL_RE.search(text) else "en"

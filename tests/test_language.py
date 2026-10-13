# [테스트 묶음] 한국어 지원(v8)의 언어별 규칙을 고정하는 단위 테스트: 질문 언어 판별, 적재할 번역 경로 고르기,
# 모델별 임베딩 접두사, 언어별 임베딩·재정렬 모델 설정, 한국어 질문에만 붙는 답변 언어 규칙.
# [왜 중요한가] 영어와 한국어는 서로 다른 임베딩 모델과 벡터 인덱스를 쓰므로, 언어 판별이나 모델 선택이
# 어긋나면 다른 벡터 공간끼리 비교하게 된다(README 설계 판단 '언어별 임베딩 모델과 인덱스').

import pytest

# 테스트 대상: 설정의 언어별 모델 선택, 임베딩 접두사 표, 답변 시스템 프롬프트, 적재 경로 선택, 언어 판별.
from app.config import get_settings
from app.services.embedding import prefixes_for
from app.services.generation import OLLAMA_ANSWER_PROMPT, system_prompt_for
from app.services.ingestion import select_doc_paths
from app.services.language import detect_language


# API 이름 같은 영어가 섞여도 한글이 한 글자라도 있으면 한국어 질문이다(README 알려진 한계에 적힌 판별 규칙).
def test_detect_language_treats_mixed_korean_as_korean():
    assert detect_language("HTTPException으로 404를 반환하려면?") == "ko"


# 한글이 없으면 영어로 본다.
def test_detect_language_defaults_to_english():
    assert detect_language("How do I return a 404 with HTTPException?") == "en"


# GitHub 트리에서 요청한 언어(en, ko)의 Markdown 파일만 고르고, 번역 안내 페이지·다른 언어(ja)·폴더·이미지는
# 빼는지 확인한다.
def test_select_doc_paths_keeps_requested_translations_and_skips_the_banner():
    tree = [
        {"type": "blob", "path": "docs/en/docs/tutorial/body.md"},
        {"type": "blob", "path": "docs/ko/docs/tutorial/body.md"},
        {"type": "blob", "path": "docs/ko/docs/translation-banner.md"},
        {"type": "blob", "path": "docs/ja/docs/tutorial/body.md"},
        {"type": "tree", "path": "docs/ko/docs/tutorial"},
        {"type": "blob", "path": "docs/ko/docs/img/logo.png"},
    ]

    assert select_doc_paths(tree, ("en", "ko")) == [
        ("docs/en/docs/tutorial/body.md", "en"),
        ("docs/ko/docs/tutorial/body.md", "ko"),
    ]


# 모델마다 접두사가 다르다: E5는 'query: '/'passage: ', BGE는 문서 쪽 접두사가 없다. 질문과 문서에 다른
# 접두사를 붙여야 하는 비대칭 모델이라 표로 관리한다.
def test_embedding_prefixes_differ_by_model_family():
    assert prefixes_for("intfloat/multilingual-e5-small") == ("query: ", "passage: ")
    assert prefixes_for("BAAI/bge-small-en-v1.5")[1] == ""


# 언어별 임베딩 모델 조회가 영어는 EMBEDDING_MODEL_NAME, 한국어는 EMBEDDING_MODEL_NAME_KO 설정을 따르는지
# 확인한다.
def test_each_language_has_its_own_embedding_model():
    settings = get_settings()
    assert settings.embedding_model_for("en") == settings.embedding_model_name
    assert settings.embedding_model_for("ko") == settings.embedding_model_name_ko


# 재정렬 모델도 언어별 설정을 따른다. 영어 전용 재정렬 모델은 한국어에서 재정렬을 안 한 것보다도 낮았기
# 때문이다(docs/experiments.md v9).
def test_each_language_has_its_own_reranker_model():
    settings = get_settings()
    assert settings.reranker_model_for("en") == settings.reranker_model_name
    assert settings.reranker_model_for("ko") == settings.reranker_model_name_ko


# 영어 프롬프트는 원래 문장 그대로이고 'Korean'이라는 말이 없어야 하며, 한국어 질문에만 한국어 규칙이 붙어야
# 한다. 모든 질문에 언어 규칙을 넣었더니 로컬 7B가 영어 질문에도 한국어로 답해 영어 정확도가 4.60 → 4.19로
# 떨어졌다(docs/experiments.md v8).
def test_only_korean_questions_get_a_language_rule_in_the_prompt():
    # The English prompt must stay byte-for-byte the original: a general language
    # rule made the local model answer English questions in Korean.
    assert system_prompt_for(OLLAMA_ANSWER_PROMPT, "en") == OLLAMA_ANSWER_PROMPT
    assert "Korean" not in OLLAMA_ANSWER_PROMPT
    assert "Korean" in system_prompt_for(OLLAMA_ANSWER_PROMPT, "ko")


# 표에 없는 모델은 접두사를 추측하지 않고 바로 ValueError로 실패해야 한다. 틀린 접두사는 조용히 검색 품질만
# 떨어뜨리기 때문이다.
def test_unknown_embedding_model_fails_loudly():
    with pytest.raises(ValueError):
        prefixes_for("some/unknown-model")

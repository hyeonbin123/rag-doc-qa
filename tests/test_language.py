import pytest

from app.config import get_settings
from app.services.embedding import prefixes_for
from app.services.generation import OLLAMA_ANSWER_PROMPT, system_prompt_for
from app.services.ingestion import select_doc_paths
from app.services.language import detect_language


def test_detect_language_treats_mixed_korean_as_korean():
    assert detect_language("HTTPException으로 404를 반환하려면?") == "ko"


def test_detect_language_defaults_to_english():
    assert detect_language("How do I return a 404 with HTTPException?") == "en"


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


def test_embedding_prefixes_differ_by_model_family():
    assert prefixes_for("intfloat/multilingual-e5-small") == ("query: ", "passage: ")
    assert prefixes_for("BAAI/bge-small-en-v1.5")[1] == ""


def test_each_language_has_its_own_embedding_model():
    settings = get_settings()
    assert settings.embedding_model_for("en") == settings.embedding_model_name
    assert settings.embedding_model_for("ko") == settings.embedding_model_name_ko


def test_only_korean_questions_get_a_language_rule_in_the_prompt():
    # The English prompt must stay byte-for-byte the original: a general language
    # rule made the local model answer English questions in Korean.
    assert system_prompt_for(OLLAMA_ANSWER_PROMPT, "en") == OLLAMA_ANSWER_PROMPT
    assert "Korean" not in OLLAMA_ANSWER_PROMPT
    assert "Korean" in system_prompt_for(OLLAMA_ANSWER_PROMPT, "ko")


def test_unknown_embedding_model_fails_loudly():
    with pytest.raises(ValueError):
        prefixes_for("some/unknown-model")

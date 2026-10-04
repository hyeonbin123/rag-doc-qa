"""The question-first Korean pool and its fixed split (docs/experiments.md v12)."""

import json
import re

from app.services.language import detect_language
from eval import build_pool3_sets
from eval.common import load_dataset

HANGUL_KANA_HAN = re.compile(r"[가-힣぀-ヿ一-鿿]")


def test_committed_sets_are_exactly_what_the_seeded_split_produces():
    for name, records in build_pool3_sets.build().items():
        path = build_pool3_sets.EVAL_DIR / f"{name}.jsonl"
        committed = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        assert committed == records, name


def test_the_three_sets_are_disjoint_and_cover_every_kept_question():
    labels = build_pool3_sets.load_labels()
    kept = {r["id"] for r in labels if "dropped" not in r}
    sets = {name: {r["id"] for r in records} for name, records in build_pool3_sets.build().items()}

    assert sets["qa_dev2_ko"].isdisjoint(sets["qa_test3a_ko"])
    assert sets["qa_dev2_ko"].isdisjoint(sets["qa_test3b_ko"])
    assert sets["qa_test3a_ko"].isdisjoint(sets["qa_test3b_ko"])
    assert set().union(*sets.values()) == kept
    assert [len(s) for s in sets.values()] == [40, 40, 40]


def test_the_sets_load_as_eval_questions_with_the_pool_wording():
    pool = build_pool3_sets.POOL_PATH.read_text(encoding="utf-8").splitlines()
    for name in build_pool3_sets.SET_NAMES:
        for q in load_dataset(build_pool3_sets.EVAL_DIR / f"{name}.jsonl"):
            assert q.question == pool[int(q.id[1:]) - 1]  # the question as written, unedited
            assert q.expected_source_paths and q.reference_answer


def test_the_english_test3b_is_the_korean_one_translated_item_for_item():
    # docs/experiments.md v13: the same 40 items, the same keywords, each expected page's
    # English original; only the question and reference answer are translated.
    ko = load_dataset(build_pool3_sets.EVAL_DIR / "qa_test3b_ko.jsonl")
    en = load_dataset(build_pool3_sets.EVAL_DIR / "qa_test3b_en.jsonl")

    assert [q.id for q in en] == [q.id for q in ko]
    for k, e in zip(ko, en, strict=True):
        assert e.expected_source_paths == [
            p.replace("docs/ko/docs/", "docs/en/docs/", 1) for p in k.expected_source_paths
        ]
        assert all(p.startswith("docs/en/docs/") for p in e.expected_source_paths)
        assert e.must_include_keywords == k.must_include_keywords
        assert detect_language(e.question) == "en", e.id
        assert not HANGUL_KANA_HAN.search(e.question + e.reference_answer), e.id

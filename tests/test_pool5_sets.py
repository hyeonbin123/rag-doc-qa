"""질문 풀 5(near-miss 답 없는 질문)의 라벨·분할과 거절 보고의 유형 열을 검증한다.

출처와 절차는 eval/pool5_provenance.md.
"""

# [테스트 묶음] 질문 풀 5(문서를 보지 않은 에이전트가 언어별로 따로 쓴 near-miss 60 + 인접 주제
# 10)의 라벨과 고정 분할(언어별 답 없음 dev 10 / test 나머지, 답 있는 질문은 거절 과잉 확인용
# dev), 그리고 eval/refusal.py가 거절 수를 질문 유형(near_miss / adjacent)별로 나눠 보고하는지를
# 검사한다. DB 없이 커밋된 파일만 읽는다.
# [왜 중요한가] 답 없는 test 셋은 한 번만 쓴다. 파일을 손으로 고치거나 셋이 겹치면 그 규칙이
# 깨진다. 질문은 라벨 전에 커밋한 문장 그대로여야 하고(라벨을 붙인 쪽이 고치지 않았는지),
# '답 없음'에는 무엇을 찾아봤는지가 남아 있어야 하며(없음을 보이는 근거), '답 있음'의 정답 경로는
# 실제로 적재되는 277개 문서 안에 있어야 검색 지표가 성립한다. 앞의 풀(3·4)과 같은 문장이
# 섞이면 이미 쓴 질문을 새 test로 다시 여는 셈이므로 문장 중복도 막는다.

import json
import os
import re
from pathlib import Path

import pytest

from app.services.ingestion import select_doc_paths
from app.services.language import detect_language
from eval import build_pool5_sets, refusal
from eval.common import load_dataset

HANGUL = re.compile(r"[가-힣]")
# 문장 중복을 볼 앞의 질문 풀 파일들(한 줄에 한 문항, 모두 400문항).
EARLIER_POOL_FILES = (
    "question_pool3_ko.txt",
    "question_pool4_ko.txt",
    "question_pool4_ko_adjacent.txt",
    "question_pool4_en.txt",
    "question_pool4_en_adjacent.txt",
)


# 공백 차이와 대소문자를 무시한 문장 비교 키.
def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


# 커밋된 여섯 셋이 고정 seed로 다시 나눈 결과와 완전히 같은지.
def test_committed_sets_are_exactly_what_the_seeded_split_produces():
    for name, records in build_pool5_sets.build().items():
        path = build_pool5_sets.EVAL_DIR / f"{name}.jsonl"
        committed = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        assert committed == records, name


# 셋끼리 겹치지 않고, 합치면 빼지 않은 문항 전부이며, 크기·종류·유형 비율이 규칙대로인지. 답 없는
# dev의 인접 주제 문항 수는 그 언어 답 없음 전체에서의 비율을 dev 크기에 맞춘 값(round)이어야
# 한다(유형으로 층화한 분할).
def test_sets_are_disjoint_cover_every_kept_label_and_have_the_registered_sizes():
    labels = {r["id"]: r for r in build_pool5_sets.load_labels() if "dropped" not in r}
    sets = {name: {r["id"] for r in records} for name, records in build_pool5_sets.build().items()}
    assert sorted(sets) == sorted(
        f"qa_pool5_{stem}_{language}"
        for stem in ("na_dev", "na_test", "ans_dev")
        for language in ("ko", "en")
    )
    names = list(sets)
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            assert sets[a].isdisjoint(sets[b]), (a, b)
    assert set().union(*sets.values()) == set(labels)
    for language in ("ko", "en"):
        na_dev = sets[f"qa_pool5_na_dev_{language}"]
        na_test = sets[f"qa_pool5_na_test_{language}"]
        ans_dev = sets[f"qa_pool5_ans_dev_{language}"]
        assert len(na_dev) == build_pool5_sets.DEV_UNANSWERABLE
        assert len(na_test) >= build_pool5_sets.MIN_TEST_UNANSWERABLE
        assert all(labels[i]["answerable"] is False for i in na_dev | na_test)
        assert all(labels[i]["answerable"] is True for i in ans_dev)
        kinds = [labels[i]["kind"] for i in na_dev | na_test]
        dev_adjacent = round(build_pool5_sets.DEV_UNANSWERABLE * kinds.count("adjacent") / len(kinds))
        assert sum(labels[i]["kind"] == "adjacent" for i in na_dev) == dev_adjacent


# 질문 파일은 언어마다 near-miss 60(`k5n01`~, `e5n01`~)과 인접 주제 10(`k5a01`~, `e5a01`~)이고,
# 라벨은 모든 문항에 질문 파일과 같은 순서로 하나씩 있으며 질문 문장·유형이 질문 파일과 같다.
def test_every_question_is_labelled_once_and_verbatim():
    questions = build_pool5_sets.load_questions()
    labels = build_pool5_sets.load_labels()
    for language, prefix in (("ko", "k5"), ("en", "e5")):
        ids = [q["id"] for q in questions if q["language"] == language]
        near_miss = [f"{prefix}n{i:02d}" for i in range(1, 61)]
        adjacent = [f"{prefix}a{i:02d}" for i in range(1, 11)]
        assert ids == near_miss + adjacent
    assert len(questions) == 140
    assert [r["id"] for r in labels] == [q["id"] for q in questions]
    for q, r in zip(questions, labels, strict=True):
        assert r["question"] == q["question"], q["id"]
        assert r["kind"] == q["kind"], q["id"]
        assert q["kind"] == ("adjacent" if q["id"][2] == "a" else "near_miss"), q["id"]


# 라벨 확인(build_pool5_sets.label_problems)이 커밋된 라벨에서 문제를 하나도 찾지 않는다: 답
# 없음은 찾아본 말 세 가지 이상과 결과가 있고 정답 경로·앵커가 비어 있음, 답 있음은 정답 경로가
# 277개 문서 안이고 앵커가 그 경로의 것, 한국어 질문은 번역이 있으면 한국어 경로, 뺀 문항은 이유가
# 있음.
def test_labels_pass_the_label_check():
    assert build_pool5_sets.label_problems() == []


# 확인이 규칙을 어긴 라벨을 실제로 잡아내는지(검사 자체의 검증). 정상 라벨 두 개에서 한 곳씩
# 망가뜨린다.
def test_label_check_catches_broken_labels():
    questions = [
        {"id": "k5n01", "language": "ko", "kind": "near_miss", "question": "질문 하나"},
        {"id": "e5a01", "language": "en", "kind": "adjacent", "question": "Question two?"},
    ]
    corpus = ["docs/en/docs/a.md", "docs/en/docs/only-en.md", "docs/ko/docs/a.md"]
    good_answerable = {
        "id": "k5n01",
        "question": "질문 하나",
        "kind": "near_miss",
        "answerable": True,
        "expected_source_paths": ["docs/ko/docs/a.md"],
        "evidence": ["docs/ko/docs/a.md#intro"],
        "reference_answer": "요약",
        "must_include_keywords": ["a"],
        "english_only_page": False,
        "not_in_docs_evidence": None,
        "notes": None,
    }
    good_unanswerable = {
        "id": "e5a01",
        "question": "Question two?",
        "kind": "adjacent",
        "answerable": False,
        "expected_source_paths": [],
        "evidence": [],
        "reference_answer": "The docs do not cover this.",
        "must_include_keywords": [],
        "english_only_page": False,
        "not_in_docs_evidence": {"searched": ["x", "y", "z"], "finding": "no page"},
        "notes": None,
    }

    def problems(answerable_changes: dict, unanswerable_changes: dict) -> list[str]:
        labels = [
            {**good_answerable, **answerable_changes},
            {**good_unanswerable, **unanswerable_changes},
        ]
        return build_pool5_sets.label_problems(labels=labels, questions=questions, corpus=corpus)

    en_page = {"expected_source_paths": ["docs/en/docs/a.md"], "evidence": ["docs/en/docs/a.md#intro"]}
    en_only = {
        "expected_source_paths": ["docs/en/docs/only-en.md"],
        "evidence": ["docs/en/docs/only-en.md#x"],
    }
    assert problems({}, {}) == []
    assert problems({"expected_source_paths": ["docs/ko/docs/missing.md"]}, {})  # 277개 문서 밖
    assert problems(en_page, {})  # 한국어 번역이 있는데 영어 경로
    assert problems({"evidence": ["docs/ko/docs/other.md#intro"]}, {})  # 앵커가 정답 경로 밖
    assert problems({"evidence": []}, {})
    assert problems({"must_include_keywords": []}, {})
    assert problems({"reference_answer": " "}, {})
    assert problems({"question": "고친 질문"}, {})
    assert problems({"kind": "adjacent"}, {})
    assert problems(en_only, {})  # 영어 전용 페이지인데 english_only_page가 False
    assert problems({**en_only, "english_only_page": True}, {}) == []
    two_terms = {"not_in_docs_evidence": {"searched": ["x", "y", "x"], "finding": "no page"}}
    assert problems({}, two_terms)  # 서로 다른 말이 두 가지뿐
    assert problems({}, {"not_in_docs_evidence": {"searched": ["x", "y", "z"], "finding": ""}})
    assert problems({}, {"not_in_docs_evidence": None})
    assert problems({}, {"expected_source_paths": ["docs/en/docs/a.md"]})
    assert problems({}, {"answerable": None})
    assert problems({}, {"dropped": ""})  # 빼면서 이유가 없음
    assert problems({}, {"dropped": "boundary disagreement"}) == []
    one_label = [good_answerable]  # 질문 하나에 라벨이 없음
    assert build_pool5_sets.label_problems(labels=one_label, questions=questions, corpus=corpus)


# 커밋한 코퍼스 목록은 측정 스냅숏(FastAPI 커밋 50113da)의 277개 문서이고, 앱의 적재 선택
# 규칙(select_doc_paths: docs/<언어>/docs/ 아래 .md, 번역 안내 배너 제외)이 고르는 모양과 같다.
def test_corpus_list_is_the_277_page_snapshot():
    paths = build_pool5_sets.load_corpus_paths()
    assert len(paths) == len(set(paths)) == 277
    assert paths == sorted(paths)
    assert sum(p.startswith("docs/en/docs/") for p in paths) == 154
    assert sum(p.startswith("docs/ko/docs/") for p in paths) == 123
    tree = [{"path": p, "type": "blob"} for p in paths]
    tree += [
        {"path": "docs/ko/docs/translation-banner.md", "type": "blob"},
        {"path": "docs/ko/mkdocs.yml", "type": "blob"},
        {"path": "docs/en/docs/tutorial", "type": "tree"},
    ]
    assert [path for path, _ in select_doc_paths(tree, ("en", "ko"))] == paths


# 풀 안에 같은 문장이 두 번 없고, 질문 풀 3·4의 어떤 문장과도 같지 않다(공백·대소문자 무시).
def test_no_question_repeats_within_pool5_or_from_pool3_and_pool4():
    pool5 = [_normalized(q["question"]) for q in build_pool5_sets.load_questions()]
    assert len(pool5) == len(set(pool5))
    earlier: set[str] = set()
    for name in EARLIER_POOL_FILES:
        lines = (build_pool5_sets.EVAL_DIR / name).read_text(encoding="utf-8").splitlines()
        earlier |= {_normalized(line) for line in lines if line.strip()}
    assert len(earlier) == 400
    assert not set(pool5) & earlier


# 답 있는 셋은 정답 페이지가 있고 답 없는 셋은 비어 있으며, 모든 셋에 참고 답안이 있다. 영어 셋
# 질문에는 한글이 없어 영어로, 한국어 셋 질문은 한국어로 판별된다(앱이 언어별 모델·청크를 고르는
# 기준).
def test_set_contents_match_their_kind_and_language():
    for name in build_pool5_sets.build():
        language = name.rsplit("_", 1)[1]
        unanswerable = name.startswith("qa_pool5_na_")
        for q in load_dataset(build_pool5_sets.EVAL_DIR / f"{name}.jsonl"):
            assert q.reference_answer
            assert bool(q.expected_source_paths) is not unanswerable, q.id
            assert detect_language(q.question) == language, q.id
            if language == "en":
                assert not HANGUL.search(q.question), q.id
            for path in q.expected_source_paths:
                assert path.startswith(f"docs/{language}/docs/") or path.startswith("docs/en/docs/")


# 거절 보고의 유형 열은 문항 id로 정한다: 질문 풀 5의 near-miss(`k5n01`)·인접 주제(`k5a01`),
# 질문 풀 4의 인접 주제(`k4a01`)가 각자의 유형이고, 그 밖의 id는 other.
def test_question_kind_reads_the_pool_ids():
    for q in build_pool5_sets.load_questions():
        assert refusal.question_kind(q["id"]) == q["kind"], q["id"]
    assert refusal.question_kind("k4a07") == "adjacent"
    assert refusal.question_kind("e4a30") == "adjacent"
    assert refusal.question_kind("k4001") == "other"
    assert refusal.question_kind("e4110") == "other"
    assert refusal.question_kind("q12") == "other"


# dev·test 명령의 거절 보고가 by_kind(--by-kind)이면 언어별 합계(기존 열)는 그대로 두고 유형별 문항
# 수·거절 수를 함께 낸다. 기본(끔)은 유형 열이 없는 v15 I4 모양 그대로다(커밋된 결정 기록과 같아야 함).
def test_refusal_reports_count_refusals_by_kind():
    def pair(item_id: str, answer: str) -> tuple:
        record = {
            "id": item_id,
            "dataset": "d",
            "language": "en",
            "answer": answer,
            "refusal": refusal.is_refusal_answer(answer, "en"),
            "cited_chunk_numbers": [],
        }
        return ("d", item_id), (record, None)

    na = dict(
        [
            pair("e5n01", "I don't know."),
            pair("e5n02", "The default is 42."),
            pair("e5a01", "I don't know."),
        ]
    )
    ans = dict([pair("e5n03", "Use Query."), pair("e5n04", "I don't know.")])
    dev = refusal.dev_command(ans, na, by_kind=True)["languages"]["en"]
    assert dev["unanswerable_refusals"] == 2
    assert dev["unanswerable_by_kind"] == {
        "adjacent": {"n": 1, "refusals": 1},
        "near_miss": {"n": 2, "refusals": 1},
    }
    assert dev["answerable_by_kind"] == {"near_miss": {"n": 2, "refusals": 1}}
    plain_dev = refusal.dev_command(ans, na)["languages"]["en"]
    assert {key: value for key, value in dev.items() if not key.endswith("_by_kind")} == plain_dev

    cand = dict([pair("e5n02", "I don't know.")])
    result = refusal.test_command({}, na, cand, {}, {}, [], c_adopted=False, by_kind=True)
    assert result["refusals_by_language"]["en"] == {"base": 2, "cand": 3, "n": 3}
    assert result["refusals_by_kind"] == {
        "en": {
            "adjacent": {"base": 1, "cand": 1, "n": 1},
            "near_miss": {"base": 1, "cand": 2, "n": 2},
        }
    }
    plain = refusal.test_command({}, na, cand, {}, {}, [], c_adopted=False)
    assert "refusals_by_kind" not in plain
    assert {key: value for key, value in result.items() if key != "refusals_by_kind"} == plain


# 라벨의 근거 앵커가 실제 문서에 `{ #앵커 }`로 있는지, 커밋한 코퍼스 목록이 체크아웃의 문서
# 목록과 같은지까지 본다. FastAPI 저장소를 커밋 50113da로 체크아웃한 경로를
# FASTAPI_DOCS_CHECKOUT에 줄 때만 돈다(CI에는 체크아웃이 없음).
@pytest.mark.skipif(
    not os.environ.get("FASTAPI_DOCS_CHECKOUT"),
    reason="FASTAPI_DOCS_CHECKOUT(FastAPI 커밋 50113da 체크아웃 경로)이 없으면 문서 본문을 볼 수 없음",
)
def test_label_anchors_exist_in_the_docs_checkout():
    docs = Path(os.environ["FASTAPI_DOCS_CHECKOUT"])
    assert build_pool5_sets.label_problems(docs_dir=docs) == []

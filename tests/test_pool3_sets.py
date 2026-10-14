"""질문을 먼저 쓴 한국어 질문 풀과 그 고정 분할을 검증한다(docs/experiments.md v12)."""

# [테스트 묶음] 질문 풀 3(문서를 보지 않고 쓴 한국어 질문 120개)과 그 고정 분할(qa_dev2_ko / qa_test3a_ko /
# qa_test3b_ko), 그리고 test3b의 영어판(qa_test3b_en)을 검사한다. DB 없이 커밋된 파일만 읽는다.
# [왜 중요한가] 튜닝용 셋과 테스트셋은 용도가 정해져 있다(dev2는 고르기, test3a는 v12 채택 판정 한 번,
# test3b는 다음 단계용으로 아껴 둠). 파일을 손으로 고치거나 셋끼리 문항이 겹치면 '테스트셋은 한 번만 쓴다'는
# 측정 규칙이 깨진다(docs/experiments.md v12, eval/pool3_provenance.md).

import json
import re

# 영어판 질문이 영어로 판별되는지 볼 언어 판별, 분할 스크립트, 데이터셋 로더.
from app.services.language import detect_language
from eval import build_pool3_sets
from eval.common import load_dataset

# 한글·가나·한자 중 하나라도 있으면 걸리는 정규식. 영어판에 원문 글자가 남지 않았는지 볼 때 쓴다.
HANGUL_KANA_HAN = re.compile(r"[가-힣぀-ヿ一-鿿]")


# 커밋된 세 셋 파일이 고정 seed(20261004)로 다시 나눈 결과와 완전히 같은지 확인한다. 파일을 손으로 고치면
# 여기서 걸린다.
def test_committed_sets_are_exactly_what_the_seeded_split_produces():
    for name, records in build_pool3_sets.build().items():
        path = build_pool3_sets.EVAL_DIR / f"{name}.jsonl"
        committed = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        assert committed == records, name


# 세 셋이 서로 겹치지 않고, 합치면 빼지 않은 문항 전부이며, 각각 40문항인지 확인한다.
def test_the_three_sets_are_disjoint_and_cover_every_kept_question():
    labels = build_pool3_sets.load_labels()
    kept = {r["id"] for r in labels if "dropped" not in r}
    sets = {name: {r["id"] for r in records} for name, records in build_pool3_sets.build().items()}

    assert sets["qa_dev2_ko"].isdisjoint(sets["qa_test3a_ko"])
    assert sets["qa_dev2_ko"].isdisjoint(sets["qa_test3b_ko"])
    assert sets["qa_test3a_ko"].isdisjoint(sets["qa_test3b_ko"])
    assert set().union(*sets.values()) == kept
    assert [len(s) for s in sets.values()] == [40, 40, 40]


# 셋의 질문 문장이 풀 파일에 쓴 그대로(고치지 않음)이고, 모든 문항에 정답 경로와 참고 답안이 있으며, 평가
# 스크립트의 로더로 읽히는지 확인한다. id의 숫자가 풀 파일의 줄 번호다.
def test_the_sets_load_as_eval_questions_with_the_pool_wording():
    pool = build_pool3_sets.POOL_PATH.read_text(encoding="utf-8").splitlines()
    for name in build_pool3_sets.SET_NAMES:
        for q in load_dataset(build_pool3_sets.EVAL_DIR / f"{name}.jsonl"):
            assert q.question == pool[int(q.id[1:]) - 1]  # 손대지 않은, 쓴 그대로의 질문
            assert q.expected_source_paths and q.reference_answer


# 영어판 test3b가 한국어판을 문항 단위로 옮긴 것인지 확인한다: 같은 id·순서, 정답 경로는 같은 페이지의 영어
# 원문, 키워드는 그대로, 질문은 영어로 판별되고 질문·참고 답안에 한글·가나·한자가 없다. v13 채택 단계에서 영어
# 정확도를 같은 문항으로 재는 데 쓴 셋이다.
def test_the_english_test3b_is_the_korean_one_translated_item_for_item():
    # docs/experiments.md v13: 같은 40문항, 같은 키워드, 정답 페이지는 각각의 영어 원문이다. 질문과 참고
    # 답안만 번역했다.
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

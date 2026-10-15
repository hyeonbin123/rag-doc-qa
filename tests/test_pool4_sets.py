"""질문 풀 4와 그 고정 분할을 검증한다(docs/experiments.md v15, eval/pool4_provenance.md)."""

# [테스트 묶음] 질문 풀 4(문서를 보지 않은 에이전트가 쓴 한국어·영어 각 110문항 + 인접 주제 각 30문항)의
# 라벨과 고정 분할(언어별 답 있음 dev 40 / test 70, 답 없음 dev 10 / test 20)을 검사한다. DB 없이 커밋된
# 파일만 읽는다.
# [왜 중요한가] test 셋은 한 번만 쓴다. 파일을 손으로 고치거나 셋이 겹치면 그 규칙이 깨진다. 질문 문장은 받은
# 그대로여야 하고(라벨을 붙인 쪽이 질문을 고치지 않았는지), 답 없는 질문에는 정답 페이지가 없어야 한다.

import json
import re

from app.services.language import detect_language
from eval import build_pool4_sets
from eval.common import load_dataset

HANGUL = re.compile(r"[가-힣]")


# 커밋된 여덟 셋이 고정 seed로 다시 나눈 결과와 완전히 같은지.
def test_committed_sets_are_exactly_what_the_seeded_split_produces():
    for name, records in build_pool4_sets.build().items():
        path = build_pool4_sets.EVAL_DIR / f"{name}.jsonl"
        committed = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        assert committed == records, name


# 셋끼리 겹치지 않고, 합치면 빼지 않은 문항 전부이며, 크기가 규칙대로인지.
def test_sets_are_disjoint_cover_every_label_and_have_the_registered_sizes():
    labels = [r for r in build_pool4_sets.load_labels() if "dropped" not in r]
    sets = {name: {r["id"] for r in records} for name, records in build_pool4_sets.build().items()}
    names = list(sets)
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            assert sets[a].isdisjoint(sets[b]), (a, b)
    assert set().union(*sets.values()) == {r["id"] for r in labels}
    for language in ("ko", "en"):
        assert len(sets[f"qa_pool4_dev_{language}"]) == 40
        assert len(sets[f"qa_pool4_na_dev_{language}"]) == 10
        assert len(sets[f"qa_pool4_test_{language}"]) >= 60
        assert len(sets[f"qa_pool4_na_test_{language}"]) >= 10


# 질문 문장은 풀 파일의 그 줄과 같다(고치지 않음). 280문항 모두 라벨이 있다.
def test_every_label_carries_the_pool_question_verbatim():
    pools = {
        prefix: path.read_text(encoding="utf-8").splitlines()
        for prefix, path in build_pool4_sets.POOL_FILES.items()
    }
    labels = build_pool4_sets.load_labels()
    assert len(labels) == sum(len(lines) for lines in pools.values()) == 280
    for r in labels:
        prefix, line = build_pool4_sets.pool_line(r["id"])
        assert r["question"] == pools[prefix][line - 1], r["id"]


# 답 있는 셋은 정답 페이지와 참고 답안이 있고, 답 없는 셋은 정답 페이지가 비어 있다. 영어 셋 질문에는 한글이
# 없어 영어로, 한국어 셋 질문은 한국어로 판별된다(앱이 언어별 모델·청크를 고르는 기준).
def test_set_contents_match_their_kind_and_language():
    for name in build_pool4_sets.build():
        language = name.rsplit("_", 1)[1]
        unanswerable = name.startswith("qa_pool4_na_")
        for q in load_dataset(build_pool4_sets.EVAL_DIR / f"{name}.jsonl"):
            assert q.reference_answer
            assert bool(q.expected_source_paths) is not unanswerable, q.id
            assert detect_language(q.question) == language, q.id
            if language == "en":
                assert not HANGUL.search(q.question), q.id
            for path in q.expected_source_paths:
                assert path.startswith(f"docs/{language}/docs/") or path.startswith("docs/en/docs/")

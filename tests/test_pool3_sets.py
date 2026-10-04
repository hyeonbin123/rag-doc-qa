"""The question-first Korean pool and its fixed split (docs/experiments.md v12)."""

import json

from eval import build_pool3_sets
from eval.common import load_dataset


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

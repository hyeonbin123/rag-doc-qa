"""Split the question-first Korean pool into its tuning and test sets.

Usage:
    python -m eval.build_pool3_sets

eval/question_pool3_ko.txt holds 120 Korean questions written before looking at the docs
or this repository; eval/pool3_labels.jsonl holds their labels (expected pages, the
sections that answer them, a reference answer, keywords), written afterwards from the docs.
See eval/pool3_provenance.md. The kept questions are shuffled with a fixed seed and cut
into three disjoint sets, each used for one purpose only:

- qa_dev2_ko: tuning, together with qa_dev_ko (docs/experiments.md v12 picks with it)
- qa_test3a_ko: the v12 test, run once on the picked setting
- qa_test3b_ko: held back for a later step; v12 does not open it
"""

from __future__ import annotations

import json
import random
from pathlib import Path

EVAL_DIR = Path(__file__).parent
POOL_PATH = EVAL_DIR / "question_pool3_ko.txt"
LABELS_PATH = EVAL_DIR / "pool3_labels.jsonl"
SEED = 20261004
SET_NAMES = ("qa_dev2_ko", "qa_test3a_ko", "qa_test3b_ko")
SET_SIZE = 40
EVAL_FIELDS = ("id", "question", "expected_source_paths", "reference_answer", "must_include_keywords")


def load_labels() -> list[dict]:
    with open(LABELS_PATH, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def build() -> dict[str, list[dict]]:
    kept = [r for r in load_labels() if "dropped" not in r]
    order = list(range(len(kept)))
    random.Random(SEED).shuffle(order)
    sets = {}
    for i, name in enumerate(SET_NAMES):
        chosen = sorted(order[i * SET_SIZE : (i + 1) * SET_SIZE])  # pool order within a set
        sets[name] = [{field: kept[j][field] for field in EVAL_FIELDS} for j in chosen]
    if sum(len(s) for s in sets.values()) != len(kept):
        raise ValueError(f"{len(kept)} kept questions do not fill {len(SET_NAMES)} sets of {SET_SIZE}")
    return sets


def main() -> None:
    for name, records in build().items():
        path = EVAL_DIR / f"{name}.jsonl"
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"{path.name}: {len(records)} questions")


if __name__ == "__main__":
    main()

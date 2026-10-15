"""질문 풀 4를 언어별 튜닝용 셋과 테스트셋으로 나눈다(docs/experiments.md v15).

사용법:
    python -m eval.build_pool4_sets

eval/question_pool4_*.txt의 질문(문서를 보지 않은 에이전트가 씀)과 eval/pool4_labels.jsonl의 라벨(그 뒤
문서를 보고 붙임)로, 답이 있는 질문과 답이 없는 질문을 언어별로 따로 섞어 자른다. 출처는
eval/pool4_provenance.md.

- qa_pool4_dev_<언어> (답 있음 40): 튜닝용. v15 I4의 바닥값·거절 후보를 고른다
- qa_pool4_test_<언어> (답 있음 나머지 70): 다음 단계용으로 아껴 둔다. v15에서는 열지 않는다
- qa_pool4_na_dev_<언어> (답 없음 10): 튜닝용
- qa_pool4_na_test_<언어> (답 없음 나머지 20): v15 I4의 test(한 번)
"""

# [파일 역할] 질문 풀 4(한국어·영어 각 110 + 인접 주제 30)를 고정 seed로 섞어 여덟 셋으로 나누고 eval/에
# JSONL로 쓴다. 답 유무는 질문을 쓴 쪽의 의도가 아니라 라벨(answerable)로 가른다.
# [왜 이렇게 나누나] v15 I4는 답 없는 질문의 거절을 처음 재는 단계라 답 없는 질문을 dev/test로 나눈다. 답 있는
# test 셋은 v15에서 열지 않고 다음 검색·생성 결정(영어 임베딩, 한국어 hybrid 등)에 남긴다. 그래서 v15 I4의 답
# 있는 질문 쪽 확인은 이미 쓴 테스트셋으로 한다(docs/experiments.md v15).
# [검증] tests/test_pool4_sets.py가 커밋된 셋이 이 스크립트를 다시 돌린 결과와 같은지, 셋끼리 겹치지 않는지
# 확인한다.

from __future__ import annotations

import json
import random
from pathlib import Path

# SEED: 분할에 쓰는 고정 seed(날짜 형태). DEV_ANSWERABLE·DEV_UNANSWERABLE: 언어별 튜닝용 셋의 크기. 나머지는
# 모두 테스트셋으로 간다.
EVAL_DIR = Path(__file__).parent
LABELS_PATH = EVAL_DIR / "pool4_labels.jsonl"
POOL_FILES = {
    "k4": EVAL_DIR / "question_pool4_ko.txt",
    "k4a": EVAL_DIR / "question_pool4_ko_adjacent.txt",
    "e4": EVAL_DIR / "question_pool4_en.txt",
    "e4a": EVAL_DIR / "question_pool4_en_adjacent.txt",
}
SEED = 20261015
DEV_ANSWERABLE = 40
DEV_UNANSWERABLE = 10
LANGUAGES = ("ko", "en")
EVAL_FIELDS = ("id", "question", "expected_source_paths", "reference_answer", "must_include_keywords")


# 문항 id의 언어: k로 시작하면 한국어, e로 시작하면 영어.
def language_of(item_id: str) -> str:
    return "ko" if item_id.startswith("k") else "en"


# id → 풀 파일에서의 줄 번호(1부터)와 그 파일. k4001 → (k4, 1), k4a07 → (k4a, 7).
def pool_line(item_id: str) -> tuple[str, int]:
    prefix = item_id[:3] if item_id[2] == "a" else item_id[:2]
    return prefix, int(item_id[len(prefix) :])


def load_labels() -> list[dict]:
    with open(LABELS_PATH, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# 분할 본체. 언어마다 '답 있음'과 '답 없음'(dropped 제외)을 따로 seed로 섞어 앞에서 dev 크기만큼 자르고
# 나머지를 test로 둔다. 셋 안에서는 id 순서로 정렬한다(읽기 쉽고 diff가 안정적이다). 무작위 순서는
# 언어·종류마다 같은 Random 객체를 이어서 쓰므로, 처리 순서(LANGUAGES, 답 있음 → 답 없음)도 분할의 일부다.
def build() -> dict[str, list[dict]]:
    labels = [r for r in load_labels() if "dropped" not in r]
    rng = random.Random(SEED)
    sets: dict[str, list[dict]] = {}
    for language in LANGUAGES:
        for answerable, dev_size, stem in (
            (True, DEV_ANSWERABLE, "qa_pool4"),
            (False, DEV_UNANSWERABLE, "qa_pool4_na"),
        ):
            group = sorted(
                (r for r in labels if language_of(r["id"]) == language and r["answerable"] is answerable),
                key=lambda r: r["id"],
            )
            rng.shuffle(group)
            dev, test = group[:dev_size], group[dev_size:]
            for split, items in (("dev", dev), ("test", test)):
                sets[f"{stem}_{split}_{language}"] = [
                    {field: r[field] for field in EVAL_FIELDS} for r in sorted(items, key=lambda r: r["id"])
                ]
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

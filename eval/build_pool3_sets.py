"""질문을 먼저 쓴 한국어 질문 풀을 튜닝용 셋과 테스트셋으로 나눈다.

사용법:
    python -m eval.build_pool3_sets

eval/question_pool3_ko.txt에는 문서나 이 저장소를 보기 전에 쓴 한국어 질문 120개가 있고,
eval/pool3_labels.jsonl에는 그 뒤에 문서를 보고 단 라벨(정답 페이지, 답이 되는 절, 참고 답안, 키워드)이
있다. eval/pool3_provenance.md 참고. 남긴 질문을 고정 seed로 섞어 서로 겹치지 않는 세 셋으로 자르고, 각
셋은 한 가지 목적에만 쓴다:

- qa_dev2_ko: 튜닝용. qa_dev_ko와 함께 쓴다(docs/experiments.md v12가 이 셋으로 설정을 고른다)
- qa_test3a_ko: v12 테스트. 고른 설정 하나로 한 번만 돌린다
- qa_test3b_ko: 다음 단계용으로 아껴 둔다. v12에서는 열어 보지 않는다
"""

# [파일 역할] 문서를 보기 전에 쓴 한국어 질문 120개(질문 풀 3)를 고정 seed로 섞어 40문항씩 세 셋으로 나누고
# eval/에 JSONL로 쓴다.
# [왜 필요한가] 튜닝용 셋과 테스트셋을 미리, 재현 가능하게 나눠 두어야 '파라미터는 튜닝용 셋에서만 고르고
# 테스트셋은 고른 설정 하나에 한 번만 쓴다'는 측정 원칙(docs/experiments.md 평가 방식)을 지킬 수 있다. 문서를
# 보며 쓴 기존 셋은 질문과 본문의 단어가 겹치기 쉬운 편향이 있어 v12에서 새 풀을 만들었다.
# [검증] tests/test_pool3_sets.py가 커밋된 세 파일이 이 스크립트를 다시 돌린 결과와 같은지, 셋끼리 겹치지
# 않는지 확인한다.

from __future__ import annotations

import json
import random
from pathlib import Path

# SEED: 분할에 쓰는 고정 난수 seed(날짜 형태 20261004). 같은 seed면 언제 돌려도 같은 분할이 나온다.
# SET_NAMES·SET_SIZE: 세 셋의 이름과 크기(40 × 3 = 120).
# EVAL_FIELDS: 라벨 파일의 여러 필드 중 평가 질문셋(EvalQuestion)에 들어갈 필드만 고른다.
EVAL_DIR = Path(__file__).parent
POOL_PATH = EVAL_DIR / "question_pool3_ko.txt"
LABELS_PATH = EVAL_DIR / "pool3_labels.jsonl"
SEED = 20261004
SET_NAMES = ("qa_dev2_ko", "qa_test3a_ko", "qa_test3b_ko")
SET_SIZE = 40
EVAL_FIELDS = ("id", "question", "expected_source_paths", "reference_answer", "must_include_keywords")


# 라벨 파일(eval/pool3_labels.jsonl)을 읽는다. 문항마다 정답 페이지, 근거 절, 참고 답안, 키워드가 있고, 뺀
# 문항에는 dropped 필드가 붙는다.
def load_labels() -> list[dict]:
    with open(LABELS_PATH, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# 분할 본체. 빼지 않은 문항의 위치 목록을 seed로 섞은 뒤 앞에서부터 40개씩 잘라 세 셋에 준다. 각 셋 안에서는
# 다시 정렬해 풀 순서를 유지한다(파일을 읽기 쉽고 diff가 안정적이다). 남는 문항이 있거나 모자라면 분할이 맞지
# 않는 것이므로 오류를 낸다.
def build() -> dict[str, list[dict]]:
    kept = [r for r in load_labels() if "dropped" not in r]
    order = list(range(len(kept)))
    random.Random(SEED).shuffle(order)
    sets = {}
    for i, name in enumerate(SET_NAMES):
        chosen = sorted(order[i * SET_SIZE : (i + 1) * SET_SIZE])  # 셋 안에서는 풀 순서대로
        sets[name] = [{field: kept[j][field] for field in EVAL_FIELDS} for j in chosen]
    if sum(len(s) for s in sets.values()) != len(kept):
        raise ValueError(f"{len(kept)} kept questions do not fill {len(SET_NAMES)} sets of {SET_SIZE}")
    return sets


# 세 셋을 eval/<이름>.jsonl로 쓴다(한국어 그대로, 줄 끝 LF).
def main() -> None:
    for name, records in build().items():
        path = EVAL_DIR / f"{name}.jsonl"
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"{path.name}: {len(records)} questions")


if __name__ == "__main__":
    main()

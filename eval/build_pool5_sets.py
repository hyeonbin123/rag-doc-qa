"""질문 풀 5(near-miss 답 없는 질문)를 언어별 셋으로 나누고 라벨을 확인한다.

사용법:
    # 여섯 셋을 eval/에 쓴다
    python -m eval.build_pool5_sets

    # 라벨 확인(커밋된 파일만): 문제가 있으면 한 줄씩 출력하고 종료 코드 1
    python -m eval.build_pool5_sets --check

    # 라벨 확인 + 근거 앵커·코퍼스 목록을 문서 본문과 대조
    python -m eval.build_pool5_sets --check --docs <FastAPI 저장소를 커밋 50113da로 체크아웃한 폴더>

eval/pool5_questions.jsonl의 질문(문서를 보지 않은 에이전트가 언어별로 따로 씀)과 eval/pool5_labels.jsonl의
라벨(질문 커밋 뒤 문서를 grep·읽기로 붙임)로 셋을 만든다. 출처와 절차는 eval/pool5_provenance.md.

- qa_pool5_na_dev_<언어> (답 없음 10): 튜닝용
- qa_pool5_na_test_<언어> (답 없음 나머지): 다음 거절 결정의 test. 한 번만 쓴다
- qa_pool5_ans_dev_<언어> (답 있음 전부): near-miss로 썼지만 문서에 답이 있던 질문. 거절 과잉을 보는 dev
"""

# [파일 역할] 질문 풀 5(언어별 near-miss 60 + 인접 주제 10)를 고정 seed로 섞어 여섯 셋으로 나눠 eval/에
# JSONL로 쓰고, 라벨이 규칙을 지키는지 확인한다. 답 유무는 질문을 쓴 쪽의 의도(kind)가 아니라 라벨
# (answerable)로 가른다. 질문 풀 4의 분할(eval/build_pool4_sets.py)과 같은 방식이고 두 가지가 다르다.
#   1. 답 없는 질문을 유형(kind: near_miss / adjacent)으로 층화해 자른다. 거절률을 유형별로 보고하므로
#      (eval/refusal.py의 유형 열) dev와 test의 유형 비율이 같아야 dev에서 고른 설정이 test에서 같은
#      조건으로 재진다.
#   2. 답 있는 질문은 test 없이 모두 dev(ans_dev)다. 이 풀의 목적은 답 없는 질문의 거절이고, 답 있는
#      near-miss는 거절 과잉(답할 수 있는데 모른다고 함)을 살피는 보조 셋이기 때문이다.
# [라벨 확인] label_problems가 라벨 스키마(답 없음은 찾아본 말 세 가지 이상과 결과, 답 있음은 정답 경로가
# 277개 문서 안이고 근거 앵커가 그 경로의 것 등)를 본다. --docs를 주면 근거 앵커가 실제 문서에 있는지와
# 커밋한 코퍼스 목록(eval/corpus_paths_50113da.txt)이 체크아웃의 문서 목록과 같은지까지 본다.
# [검증] tests/test_pool5_sets.py가 커밋된 셋이 이 스크립트를 다시 돌린 결과와 같은지, 셋끼리 겹치지
# 않는지, 라벨 확인이 문제를 찾지 않는지 확인한다.

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

# QUESTIONS_PATH: 질문 파일(라벨 전에 커밋). LABELS_PATH: 라벨 파일(질문 파일과 같은 순서, 문항마다 한 줄).
# CORPUS_PATHS_PATH: 측정 스냅숏(FastAPI 커밋 50113da)에서 앱이 적재하는 277개 문서 경로 목록. 문서 본문
# 없이도(CI) 정답 경로가 코퍼스 안인지 확인하려고 커밋해 둔다.
EVAL_DIR = Path(__file__).parent
QUESTIONS_PATH = EVAL_DIR / "pool5_questions.jsonl"
LABELS_PATH = EVAL_DIR / "pool5_labels.jsonl"
CORPUS_PATHS_PATH = EVAL_DIR / "corpus_paths_50113da.txt"
# SEED: 분할에 쓰는 고정 seed(날짜 형태). DEV_UNANSWERABLE: 언어별 답 없는 튜닝용 셋의 크기(나머지는
# 모두 test). MIN_TEST_UNANSWERABLE: 언어별 답 없는 test의 목표 하한(dev 10 + test 30 = 언어별 40).
# MIN_SEARCH_TERMS: '답 없음' 라벨이 남겨야 하는 서로 다른 검색어 수의 하한.
SEED = 20261030
DEV_UNANSWERABLE = 10
MIN_TEST_UNANSWERABLE = 30
MIN_SEARCH_TERMS = 3
LANGUAGES = ("ko", "en")
KINDS = ("near_miss", "adjacent")
EVAL_FIELDS = ("id", "question", "expected_source_paths", "reference_answer", "must_include_keywords")


# 문항 id의 언어: k로 시작하면 한국어, e로 시작하면 영어(k5n01, e5a03).
def language_of(item_id: str) -> str:
    return "ko" if item_id.startswith("k") else "en"


def _read_jsonl(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_questions() -> list[dict]:
    return _read_jsonl(QUESTIONS_PATH)


def load_labels() -> list[dict]:
    return _read_jsonl(LABELS_PATH)


# 커밋한 코퍼스 목록(정렬된 277개 경로).
def load_corpus_paths() -> list[str]:
    return CORPUS_PATHS_PATH.read_text(encoding="utf-8").split()


# 분할 본체. 언어마다 '답 없음'(dropped 제외)을 유형별로 따로 seed로 섞어 앞에서 dev 몫만큼 자르고 나머지를
# test로 둔다. dev의 인접 주제 몫은 round(DEV_UNANSWERABLE × 인접 주제 수 / 답 없음 수)이고(파이썬 round는
# .5에서 짝수 쪽), 나머지가 near-miss 몫이다. 답 있음은 전부 ans_dev. 셋 안에서는 id 순서로 정렬한다(읽기
# 쉽고 diff가 안정적이다). 같은 Random 객체를 언어·유형 순서(LANGUAGES, KINDS)대로 이어 쓰므로 그 처리
# 순서도 분할의 일부다.
def build() -> dict[str, list[dict]]:
    labels = [r for r in load_labels() if "dropped" not in r]
    rng = random.Random(SEED)
    sets: dict[str, list[dict]] = {}
    for language in LANGUAGES:
        rows = sorted((r for r in labels if language_of(r["id"]) == language), key=lambda r: r["id"])
        unanswerable = {
            kind: [r for r in rows if r["answerable"] is False and r["kind"] == kind] for kind in KINDS
        }
        total = sum(len(group) for group in unanswerable.values())
        dev_adjacent = round(DEV_UNANSWERABLE * len(unanswerable["adjacent"]) / total) if total else 0
        dev_sizes = {"near_miss": DEV_UNANSWERABLE - dev_adjacent, "adjacent": dev_adjacent}
        dev: list[dict] = []
        test: list[dict] = []
        for kind in KINDS:
            group = unanswerable[kind]
            rng.shuffle(group)
            dev += group[: dev_sizes[kind]]
            test += group[dev_sizes[kind] :]
        answerable = [r for r in rows if r["answerable"] is True]
        for stem, items in (
            ("qa_pool5_na_dev", dev),
            ("qa_pool5_na_test", test),
            ("qa_pool5_ans_dev", answerable),
        ):
            sets[f"{stem}_{language}"] = [
                {field: r[field] for field in EVAL_FIELDS} for r in sorted(items, key=lambda r: r["id"])
            ]
    return sets


# 영어 문서 경로에 대응하는 한국어 번역 경로(docs/en/docs/x.md → docs/ko/docs/x.md).
def _korean_page(path: str) -> str:
    return "docs/ko/docs/" + path.removeprefix("docs/en/docs/")


# 빼지 않은 라벨 한 줄의 규칙 위반 목록. 질문 풀 4의 라벨 규칙(eval/pool4_provenance.md '라벨')을 기계로
# 확인할 수 있는 만큼 옮긴 것이다.
# - 답 있음: 정답 경로가 코퍼스 안, 영어 질문은 영어 경로만, 한국어 질문은 번역이 있으면 한국어 경로,
#   english_only_page는 한국어 질문이 영어 경로를 쓸 때만 True, 근거 앵커는 정답 경로의 것, 핵심어 있음,
#   not_in_docs_evidence 없음
# - 답 없음: 정답 경로·앵커·핵심어가 비어 있음, not_in_docs_evidence가 {"searched": [...], "finding": "..."}
#   이고 서로 다른 검색어가 MIN_SEARCH_TERMS개 이상, finding이 비어 있지 않음
# - 둘 다: 참고 답안이 비어 있지 않음, answerable은 True/False 중 하나
def _record_problems(r: dict, language: str, corpus: set[str]) -> list[str]:
    out: list[str] = []
    paths = r.get("expected_source_paths") or []
    evidence = r.get("evidence") or []
    keywords = r.get("must_include_keywords") or []
    if not str(r.get("reference_answer") or "").strip():
        out.append("empty reference_answer")
    if r.get("answerable") is True:
        if not paths:
            out.append("answerable without expected_source_paths")
        for path in paths:
            if path not in corpus:
                out.append(f"{path} is not one of the corpus documents")
            elif language == "en" and not path.startswith("docs/en/docs/"):
                out.append(f"{path}: an English question must cite English pages")
            elif language == "ko" and path.startswith("docs/en/docs/") and _korean_page(path) in corpus:
                out.append(f"{path}: a Korean translation exists, cite it instead")
        english_only = language == "ko" and any(path.startswith("docs/en/docs/") for path in paths)
        if bool(r.get("english_only_page")) is not english_only:
            out.append("english_only_page does not match the cited pages")
        if not evidence:
            out.append("answerable without evidence anchors")
        for item in evidence:
            path, _, anchor = item.partition("#")
            if path not in paths or not anchor:
                out.append(f"evidence {item} is not an anchor of a cited page")
        if not keywords:
            out.append("answerable without must_include_keywords")
        if r.get("not_in_docs_evidence") is not None:
            out.append("answerable with not_in_docs_evidence")
    elif r.get("answerable") is False:
        if paths or evidence or keywords:
            out.append("unanswerable with pages, anchors or keywords")
        if r.get("english_only_page"):
            out.append("unanswerable with english_only_page")
        record = r.get("not_in_docs_evidence")
        if not isinstance(record, dict):
            out.append('not_in_docs_evidence must be {"searched": [...], "finding": "..."}')
            record = {}
        searched = {str(term).strip() for term in record.get("searched") or [] if str(term).strip()}
        if len(searched) < MIN_SEARCH_TERMS:
            out.append(f"only {len(searched)} distinct search terms (need {MIN_SEARCH_TERMS})")
        if not str(record.get("finding") or "").strip():
            out.append("empty not_in_docs_evidence finding")
    else:
        out.append("answerable must be true or false")
    return out


# 체크아웃 본문과의 대조: 코퍼스 목록이 체크아웃에서 앱의 적재 규칙(select_doc_paths)으로 고른 문서 목록과
# 같은지, 답 있는 라벨의 근거 앵커가 그 파일에 '{ #앵커 }'로 있는지. 앱 모듈은 이때만 불러온다(셋 만들기와
# 기본 확인은 앱 설정 없이 돈다).
def _docs_problems(labels: list[dict], corpus: set[str], docs_dir: Path) -> list[str]:
    from app.services.ingestion import select_doc_paths

    tree = [{"path": p.relative_to(docs_dir).as_posix(), "type": "blob"} for p in docs_dir.rglob("*.md")]
    listed = sorted(path for path, _ in select_doc_paths(tree, LANGUAGES))
    out: list[str] = []
    if listed != sorted(corpus):
        out.append(f"corpus list differs from the checkout ({len(corpus)} listed, {len(listed)} in checkout)")
    for r in labels:
        if "dropped" in r or r.get("answerable") is not True:
            continue
        for item in r.get("evidence") or []:
            path, _, anchor = item.partition("#")
            file = docs_dir / path
            if not file.is_file():
                out.append(f"{r['id']}: {path} is missing in the checkout")
            elif not re.search(r"\{\s*#" + re.escape(anchor) + r"\s*\}", file.read_text(encoding="utf-8")):
                out.append(f"{r['id']}: anchor #{anchor} missing in {path}")
    return out


# 라벨 확인. 인자를 주지 않으면 커밋된 질문·라벨·코퍼스 목록을 읽는다(테스트는 작은 가짜 입력을 넘겨 확인
# 자체를 검증한다). 반환: 문제 설명 문자열 목록(비어 있으면 통과).
# - 라벨은 질문 파일의 모든 문항에 같은 순서로 하나씩 있어야 하고, 질문 문장·유형이 질문 파일과 같아야 한다
# - 뺀 문항('dropped' 키)은 이유만 확인하고 나머지 규칙은 보지 않는다
def label_problems(
    labels: list[dict] | None = None,
    questions: list[dict] | None = None,
    corpus: list[str] | None = None,
    docs_dir: Path | None = None,
) -> list[str]:
    labels = load_labels() if labels is None else labels
    questions = load_questions() if questions is None else questions
    corpus_set = set(load_corpus_paths() if corpus is None else corpus)
    problems: list[str] = []
    if [r.get("id") for r in labels] != [q["id"] for q in questions]:
        problems.append("labels do not cover every question exactly once, in question-file order")
    by_id = {q["id"]: q for q in questions}
    for r in labels:
        item_id = r.get("id")
        question = by_id.get(item_id)
        if question is None:
            problems.append(f"{item_id}: no such question")
            continue
        if r.get("question") != question["question"]:
            problems.append(f"{item_id}: question text differs from the question file")
        if r.get("kind") != question["kind"]:
            problems.append(f"{item_id}: kind differs from the question file")
        if "dropped" in r:
            if not str(r["dropped"] or "").strip():
                problems.append(f"{item_id}: dropped without a reason")
            continue
        problems += [f"{item_id}: {p}" for p in _record_problems(r, question["language"], corpus_set)]
    if docs_dir is not None:
        problems += _docs_problems(labels, corpus_set, Path(docs_dir))
    return problems


# 언어·유형별 라벨 결과 수(답 있음 / 답 없음 / 뺌). --check가 출력하고 출처 문서의 표가 이 값이다.
def summary() -> dict[str, dict[str, int]]:
    counts: dict[str, Counter] = {}
    for r in load_labels():
        outcome = "dropped" if "dropped" in r else ("answerable" if r["answerable"] else "unanswerable")
        counts.setdefault(f"{language_of(r['id'])}/{r['kind']}", Counter())[outcome] += 1
    return {key: dict(sorted(counter.items())) for key, counter in sorted(counts.items())}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "질문 풀 5를 언어별 셋(답 없음 dev/test, 답 있음 dev)으로 나눠 eval/에 쓰거나(기본), "
            "--check로 라벨이 규칙을 지키는지 확인한다."
        ),
        epilog=(
            "셋 파일은 tests/test_pool5_sets.py가 이 스크립트의 결과와 같은지 확인하므로 손으로 고치지 "
            "않는다. 라벨 규칙과 분할 이유는 eval/pool5_provenance.md."
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="셋을 쓰지 않고 라벨만 확인한다. 문제가 있으면 한 줄씩 출력하고 종료 코드 1",
    )
    parser.add_argument(
        "--docs",
        type=Path,
        help=(
            "FastAPI 저장소를 커밋 50113da로 체크아웃한 폴더(--check와 함께). 근거 앵커가 그 파일에 "
            "'{ #앵커 }'로 있는지와 커밋한 코퍼스 목록이 체크아웃의 문서 목록과 같은지도 본다"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.docs is not None and not args.check:
        parser.error("--docs는 --check와 함께 쓴다")
    if args.check:
        problems = label_problems(docs_dir=args.docs)
        for problem in problems:
            print(problem)
        print(json.dumps(summary(), ensure_ascii=False))
        print(f"{len(problems)} problems")
        return 1 if problems else 0
    for name, records in build().items():
        path = EVAL_DIR / f"{name}.jsonl"
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"{path.name}: {len(records)} questions")
    return 0


if __name__ == "__main__":
    sys.exit(main())

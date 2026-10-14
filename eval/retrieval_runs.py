"""저장된 검색 평가 기록(eval/runs/<tag>.retrieval.jsonl)의 분석.

사용법:
    python -m eval.retrieval_runs floors eval/runs/<tag>.retrieval.jsonl
    python -m eval.retrieval_runs compare eval/runs/<a>.retrieval.jsonl eval/runs/<b>.retrieval.jsonl

floors: --score-floor 0으로 돌린 실행에서, 후보 바닥값마다의 지표와 v12 규칙이 고르는 바닥값(모든 질문이
결과 5개를 유지하는 가장 높은 값).
compare: 두 실행의 같은 질문들을 비교한다. 예: HNSW 대 정확 탐색, 또는 두 모델.
"""

# [파일 역할] eval/run_retrieval_eval.py가 남긴 문항별 검색 기록(eval/runs/<tag>.retrieval.jsonl)을 다시 읽어,
# 검색을 다시 돌리지 않고 두 가지 분석 리포트를 만든다.
# [왜 필요한가] v12 한국어 임베딩 비교의 '선택' 절차가 이 두 분석을 요구했다(docs/experiments.md v12). (1)
# floors: 후보 모델마다 점수 바닥값(score floor)을 품질이 아니라 '모든 문항이 5개 결과를 유지하는가'로만
# 정한다. (2) compare: 계획대로 돈 실행과 --exact(정확 탐색) 실행의 상위 10개가 같은지, 또는 두 모델 실행의
# 문항별 순위 변화를 본다.
# [흐름] main이 하위 명령(floors/compare)을 고르고 → 기록을 읽어 metrics·pick_floor·compare로 계산 → 마크다운
# 리포트를 eval/reports/에 쓴다.
# [연결] tests/test_retrieval_eval.py가 metrics·pick_floor를 검증한다.

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

# page_key: 'docs/ko/docs/x.md'와 'docs/en/docs/x.md'를 같은 페이지 'x.md'로 묶는 앱 함수. v12부터 Hit를 번역
# 언어와 상관없이 페이지 단위로 세므로 앱과 같은 정의를 쓴다.
# eval.common: JSON/JSONL 읽기와 리포트 쓰기를 다른 평가 스크립트와 공유한다.
from app.services.retrieval import page_key
from eval.common import read_json, read_jsonl, write_report

# 바닥값 후보. 규칙상 지금 값 0.3에서 시작해 0.05씩 낮춰 0까지 본다(docs/experiments.md v12 선택 1번). 높은
# 값부터 시도하므로 순서가 중요하다.
FLOOR_GRID = (0.3, 0.25, 0.2, 0.15, 0.1, 0.05, 0.0)
KEEP = 5  # 답변 파이프라인은 상위 5개를 생성기에 넘긴다


# 한 문항의 결과 중 바닥값 이상인 것만 남긴다(앱이 바닥값 아래 결과를 버리는 것과 같은 효과).
def _kept(record: dict, floor: float) -> list[dict]:
    return [r for r in record["results"] if r["score"] >= floor]


# 남은 결과 순위마다 정답 페이지인지(True/False)와 남은 개수를 돌려준다. 정답 경로도 결과 경로도 page_key로
# 바꿔 비교하므로 영어 원문 청크가 나와도 같은 페이지면 맞음으로 센다.
def ranked_pages_hit(record: dict, floor: float) -> tuple[list[bool], int]:
    """남은 순위마다 그 페이지가 정답 페이지인지, 그리고 몇 개가 남았는지."""
    expected = {page_key(p) for p in record["expected_source_paths"]}
    kept = _kept(record, floor)
    return [page_key(r["source_path"]) in expected for r in kept], len(kept)


# 문항 목록의 Hit@3/5/10, MRR, short(결과가 KEEP개 미만인 문항 수)를 계산한다. floor를 주면 그 바닥값으로 잘라
# 냈을 때의 값을 기록에서 다시 계산한다.
# MRR은 처음 맞은 순위의 역수 평균이고, 상위 결과 안에 정답이 없으면 0으로 센다.
def metrics(records: list[dict], floor: float = 0.0) -> dict:
    n = len(records)
    totals = {"hit@3": 0, "hit@5": 0, "hit@10": 0, "mrr": 0.0, "short": 0}
    for record in records:
        hits, kept = ranked_pages_hit(record, floor)
        for k in (3, 5, 10):
            totals[f"hit@{k}"] += any(hits[:k])
        # 처음으로 정답 페이지가 나온 순위(1부터). 없으면 None이라 역수 대신 0을 더한다.
        first = next((rank for rank, hit in enumerate(hits, start=1) if hit), None)
        totals["mrr"] += 1 / first if first else 0.0
        totals["short"] += kept < KEEP
    return {
        "n": n,
        "hit@3": totals["hit@3"] / n,
        "hit@5": totals["hit@5"] / n,
        "hit@10": totals["hit@10"] / n,
        "mrr": totals["mrr"] / n,
        "short": totals["short"],
    }


# 규칙이 고르는 바닥값: 모든 문항이 KEEP(5)개를 남기는 가장 높은 값. 원래 결과가 5개 미만인 문항은 가진 개수를
# 모두 남기면 통과로 본다.
# 왜 5개인가: 답변 파이프라인이 상위 5개를 생성기에 넘기므로, 바닥값 때문에 생성 컨텍스트가 줄어들지 않는
# 선에서만 값을 정하려는 것이다. 어느 값에서도 만족하지 않으면 0.0.
def pick_floor(records: list[dict], grid: tuple[float, ...] = FLOOR_GRID) -> float:
    """모든 질문이 KEEP개 결과(또는 원래 가진 결과 전부)를 남기는 가장 높은 바닥값."""
    for floor in grid:
        if all(len(_kept(r, floor)) >= min(KEEP, len(r["results"])) for r in records):
            return floor
    return 0.0


# 같은 질문을 같은 순서로 담은 두 실행을 문항별로 비교한다. 상위 `top`개 청크 id가 달라진 문항, 역순위(1/첫
# 정답 순위)가 오른·내린 문항, 두 실행의 MRR·Hit@5를 돌려준다.
# 주의: 서로 다른 DB(다른 모델로 적재한 복제 DB)끼리는 청크 id가 달라 'same_ranking'이 0으로 나오며 의미가
# 없다(docs/experiments.md v12 dev 결과). 그때는 역순위 변화만 본다.
def compare(a: list[dict], b: list[dict], top: int = 10) -> dict:
    by_id = {r["id"]: r for r in b}
    # 다른 질문셋이나 순서가 다른 실행을 실수로 비교하지 않도록 문항 id 목록이 완전히 같을 때만 진행한다.
    if [r["id"] for r in a] != [r["id"] for r in b]:
        raise ValueError("the two runs do not hold the same questions in the same order")
    changed, ups, downs = [], [], []
    for ra in a:
        rb = by_id[ra["id"]]
        ids_a = [r["chunk_id"] for r in ra["results"][:top]]
        ids_b = [r["chunk_id"] for r in rb["results"][:top]]
        if ids_a != ids_b:
            changed.append(ra["id"])
        # 문항 하나만 넣은 metrics의 MRR이 곧 그 문항의 역순위다. 같은 계산을 재사용해 정의가 어긋나지 않게
        # 한다.
        rr_a, rr_b = metrics([ra])["mrr"], metrics([rb])["mrr"]
        if rr_b > rr_a:
            ups.append(ra["id"])
        elif rr_b < rr_a:
            downs.append(ra["id"])
    ma, mb = metrics(a), metrics(b)
    return {
        "n": len(a),
        "same_ranking": len(a) - len(changed),
        "changed_ids": changed,
        "rr_up": ups,
        "rr_down": downs,
        "mrr_a": ma["mrr"],
        "mrr_b": mb["mrr"],
        "hit5_a": ma["hit@5"],
        "hit5_b": mb["hit@5"],
    }


# 문항별 검색 기록 JSONL을 읽는 얇은 도우미.
def _records(path: Path) -> list[dict]:
    return read_jsonl(path)


# floors 명령의 리포트: 바닥값 후보마다 short 수와 지표를 표로 만들고 규칙이 고른 값을 적는다.
# 바닥값을 0으로 돌린 실행이어야 모든 후보 바닥값을 기록에서 다시 계산할 수 있으므로, 다른 바닥값으로 돈
# 기록이면 SystemExit로 멈춘다. 옆의 .retrieval.meta.json에서 태그·DB·모델을 가져와 리포트 머리에 적는다.
def _floors_report(path: Path) -> str:
    records = _records(path)
    meta = read_json(path.with_name(path.name.replace(".retrieval.jsonl", ".retrieval.meta.json")))
    floors_used = {r["score_floor"] for r in records}
    if floors_used != {0.0}:
        raise SystemExit(f"{path} was not run with --score-floor 0 (floors {floors_used})")
    lines = [
        f"# Score floors ({path.name})",
        "",
        f"- run: {meta.get('tag')}, database {meta.get('database')}, "
        f"models {meta.get('embedding_models')}",
        f"- questions: {len(records)}; 'short' = questions keeping fewer than {KEEP} results",
        "",
        "| floor | short | Hit@3 | Hit@5 | Hit@10 | MRR |",
        "|---|---|---|---|---|---|",
    ]
    for floor in FLOOR_GRID:
        m = metrics(records, floor)
        lines.append(
            f"| {floor} | {m['short']} | {m['hit@3']:.3f} | {m['hit@5']:.3f} "
            f"| {m['hit@10']:.3f} | {m['mrr']:.3f} |"
        )
    lines += ["", f"rule pick (highest floor with no short question): **{pick_floor(records)}**"]
    return "\n".join(lines)


# compare 명령의 리포트: 같은 상위 청크 수, 순위가 바뀐 문항, MRR·Hit@5 변화, 역순위가 오른·내린 문항을
# 목록으로 적는다.
def _compare_report(path_a: Path, path_b: Path, top: int) -> str:
    diff = compare(_records(path_a), _records(path_b), top)
    return "\n".join(
        [
            f"# Retrieval runs compared: {path_a.name} vs {path_b.name}",
            "",
            f"- questions: {diff['n']}; same top-{top} chunk ids: {diff['same_ranking']}",
            f"- ranking changed: {', '.join(diff['changed_ids']) or 'none'}",
            f"- MRR a {diff['mrr_a']:.3f} -> b {diff['mrr_b']:.3f}; "
            f"Hit@5 a {diff['hit5_a']:.3f} -> b {diff['hit5_b']:.3f}",
            f"- reciprocal rank up in b: {', '.join(diff['rr_up']) or 'none'}",
            f"- reciprocal rank down in b: {', '.join(diff['rr_down']) or 'none'}",
        ]
    )


# 명령행 진입점. floors/compare 하위 명령을 받아 리포트를 만들고, 파일 이름에 입력 태그와 UTC 시각을 붙여
# eval/reports/에 저장한 뒤 화면에도 출력한다.
def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    floors = sub.add_parser("floors")
    floors.add_argument("run", type=Path)
    cmp = sub.add_parser("compare")
    cmp.add_argument("a", type=Path)
    cmp.add_argument("b", type=Path)
    cmp.add_argument("--top", type=int, default=10)
    args = parser.parse_args(argv)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    if args.command == "floors":
        report = _floors_report(args.run)
        name = f"retrieval_floors_{args.run.name.removesuffix('.retrieval.jsonl')}_{timestamp}.md"
    else:
        report = _compare_report(args.a, args.b, args.top)
        tag_a, tag_b = (p.name.removesuffix(".retrieval.jsonl") for p in (args.a, args.b))
        stem = f"{tag_a}_vs_{tag_b}"
        name = f"retrieval_compare_{stem}_{timestamp}.md"
    path = write_report(name, report)
    print(report)
    print(f"\nwritten to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

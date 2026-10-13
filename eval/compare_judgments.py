"""Compare judgment runs item by item, and summarize judge-prompt truncation.

pair: matches two groups of eval/runs/*.judge.jsonl files by dataset and question id.
Per dataset (and pooled) it reports both sums, the mean per-item difference (b - a) with
a paired bootstrap 90% interval, how many items went up / down, and how many stored
answers differ. Used for one judge against another on the same answers (J1 vs J0), and
for two generation passes under one judge (the generation-to-generation noise).

truncation: per file, how many judge prompts came back cut (prompt_eval_count short of
the tokenizer count by more than the tolerance), how many were longer than the context
before sending, and how far Ollama's count and the tokenizer's differ on prompts that
were not cut (the counter's calibration).

Usage:
    python -m eval.compare_judgments pair --title "J1 - J0, pass A" --tag v11_j1_vs_j0_A
        --a eval/runs/v11_A_*.J0.judge.jsonl --b eval/runs/v11_A_*.J1.judge.jsonl
        [--split-by-truncation a]
    python -m eval.compare_judgments truncation --tag v11_truncation_J0 --ctx 4096
        eval/runs/v11_*.J0.judge.jsonl
"""

# [파일 역할] 판정 기록(eval/runs/*.judge.jsonl)을 문항 단위로 비교하는 분석 도구. 두 하위 명령이 있다.
# - pair: 두 판정 묶음을 셋·문항 id로 짝지어 합계, 문항별 차이의 평균과 대응표본 bootstrap 90% 구간,
#   오른·내린·같은 문항 수, 답이 달라진 문항 수를 표로 낸다.
# - truncation: 파일마다 판정 프롬프트가 잘린 수, 보내기 전에 이미 문맥보다 길었던 수, 잘리지 않은
#   프롬프트에서 Ollama 토큰 수와 토크나이저 수의 차이를 낸다.
# [왜 필요한가] v11에서 판정 설정(문맥 크기)이나 순서만 바꿔도 점수가 움직인다는 것을
# 확인했다(docs/experiments.md v11). 그래서 평균 하나만 보지 않고 같은 문항끼리 짝지어 차이와 그 불확실성
# 구간을 본다. 30~43문항 규모에서는 문항 하나의 변화로도 평균이 움직이므로 오른·내린 문항 수를 함께 본다.
# [연결] README '평가' 절의 compare_judgments 명령. 리포트는 eval/reports/judge_compare_*,
# judge_truncation_*로 남는다.

from __future__ import annotations

import argparse
import random
import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

# display_path: 리포트에 저장소 기준 경로를 쓴다. TRUNCATION_TOLERANCE: 잘림 판정 기준을 판정 모듈과 같은
# 값으로 쓴다.
from eval.answer_report import display_path
from eval.common import read_jsonl, write_report
from eval.judge import TRUNCATION_TOLERANCE

# bootstrap 다시 뽑기 횟수, 고정 seed(같은 입력이면 같은 구간이 나오게), 신뢰 수준 90%. METRICS: 비교하는 판정
# 항목(정확도, 충실도, 환각 여부).
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 20261003
CONFIDENCE = 0.90
METRICS = ("correctness_score", "faithfulness_score", "hallucinated")


# 문항별 차이(b - a)의 평균과 백분위 bootstrap 구간. 차이 목록에서 같은 개수를 복원 추출해 평균을 내는 일을
# 10,000번 반복하고, 정렬한 평균들의 5%·95% 위치 값을 구간으로 쓴다. 문항을 짝지은 채로 뽑으므로(대응표본)
# 문항 난이도 차이가 구간에 섞이지 않는다. 구간이 0을 포함하지 않으면 그 방향의 차이가 노이즈만으로 보기
# 어렵다는 뜻으로 읽는다.
def paired_bootstrap_ci(
    diffs: list[float],
    n_resamples: int = BOOTSTRAP_RESAMPLES,
    confidence: float = CONFIDENCE,
    seed: int = BOOTSTRAP_SEED,
) -> tuple[float, float, float]:
    """Mean of the per-item differences and its percentile bootstrap interval."""
    n = len(diffs)
    mean = sum(diffs) / n
    rng = random.Random(seed)
    means = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(n_resamples))
    low = means[int((1 - confidence) / 2 * n_resamples)]
    high = means[int((1 + confidence) / 2 * n_resamples) - 1]
    return mean, low, high


# 한 지표에 대해 양쪽 모두 점수가 있는 문항들의 짝. diffs는 b - a, up/down/same은 오른·내린·같은 문항 수,
# sum_a/sum_b는 양쪽 합계다.
@dataclass
class Paired:
    ids: list[str]
    a: list[float]
    b: list[float]

    @property
    def diffs(self) -> list[float]:
        return [y - x for x, y in zip(self.a, self.b, strict=True)]

    @property
    def up(self) -> int:
        return sum(1 for d in self.diffs if d > 0)

    @property
    def down(self) -> int:
        return sum(1 for d in self.diffs if d < 0)

    @property
    def same(self) -> int:
        return sum(1 for d in self.diffs if d == 0)

    @property
    def sum_a(self) -> float:
        return sum(self.a)

    @property
    def sum_b(self) -> float:
        return sum(self.b)


# 판정 기록에서 지표 값을 숫자로 꺼낸다. hallucinated 같은 bool은 int로 바꿔 1/0으로 센다. 값이 없으면 None(그
# 문항은 이 지표에서 빠진다).
def _value(row: dict, metric: str) -> float | None:
    value = row.get(metric)
    return None if value is None else int(value)  # booleans count as 0/1


# 두 판정 기록을 문항 id로 짝짓는다. 양쪽 문항 집합이 다르면 잘못된 파일끼리 비교하는 것이므로 오류를 낸다.
# 검색 결과가 없었거나 판정 오류로 한쪽이라도 점수가 없는 문항은 그 지표에서 뺀다.
def pair_metric(a_rows: list[dict], b_rows: list[dict], metric: str) -> Paired:
    """Items scored on both sides, in a's order; the two sides must hold the same items."""
    b_by_id = {r["id"]: r for r in b_rows}
    a_ids = [r["id"] for r in a_rows]
    mismatch = set(a_ids) ^ set(b_by_id)
    if mismatch:
        raise ValueError(f"the two runs hold different items: {', '.join(sorted(mismatch))}")
    ids, a_values, b_values = [], [], []
    for row in a_rows:
        x, y = _value(row, metric), _value(b_by_id[row["id"]], metric)
        if x is not None and y is not None:
            ids.append(row["id"])
            a_values.append(x)
            b_values.append(y)
    return Paired(ids, a_values, b_values)


# 두 쪽에서 판정한 답 자체가 다른 문항 수(답 SHA-1 비교). 같은 답을 다른 판정으로 잰 비교라면 0이어야 하고,
# 생성을 두 번 한 비교라면 생성 노이즈의 크기가 된다.
def answers_changed(a_rows: list[dict], b_rows: list[dict]) -> int:
    b_by_id = {r["id"]: r for r in b_rows}
    return sum(1 for r in a_rows if r.get("answer_sha1") != b_by_id[r["id"]].get("answer_sha1"))


# 여러 판정 파일의 행을 질문셋 이름별로 묶고 셋 안의 원래 순서(dataset_index)로 정렬한다. 셋 이름이 없는 옛
# 기록은 파일 이름으로 묶는다.
def _by_dataset(paths: list[Path]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for path in paths:
        for row in read_jsonl(path):
            groups[row.get("dataset") or path.name].append(row)
    for rows in groups.values():
        rows.sort(key=lambda r: r.get("dataset_index") or 0)
    return dict(groups)


# 표 칸: 평균 차이 [구간 아래, 위]. 짝지은 문항이 없으면 n/a.
def _ci_cell(paired: Paired) -> str:
    if not paired.ids:
        return "n/a"
    mean, low, high = paired_bootstrap_ci(paired.diffs)
    return f"{mean:+.3f} [{low:+.3f}, {high:+.3f}]"


# 정수면 소수점 없이, 아니면 소수 둘째 자리까지.
def _num(value: float) -> str:
    return f"{value:.0f}" if float(value).is_integer() else f"{value:.2f}"


# 비교표 한 줄: 짝지은 문항 수, 지표마다 합계 a -> b(차이), 정확도·충실도는 평균 차이 구간과 오른/내린/같은
# 수, 마지막에 답이 달라진 문항 수. 환각은 개수 합계만 보인다.
def _pair_row(label: str, a_rows: list[dict], b_rows: list[dict]) -> str:
    cells = [label]
    for metric in METRICS:
        paired = pair_metric(a_rows, b_rows, metric)
        if metric == "correctness_score":
            cells.append(str(len(paired.ids)))
        delta = paired.sum_b - paired.sum_a
        cells.append(f"{_num(paired.sum_a)} -> {_num(paired.sum_b)} ({delta:+.0f})")
        if metric != "hallucinated":
            cells.append(_ci_cell(paired))
            cells.append(f"{paired.up} / {paired.down} / {paired.same}")
    cells.append(str(answers_changed(a_rows, b_rows)))
    return "| " + " | ".join(cells) + " |"


# 비교표 머리글(마크다운 표).
PAIR_HEADER = [
    "| set | n paired | correctness sum a -> b (diff) | correctness mean diff [90% CI] | up / down / same "
    "| faithfulness sum a -> b (diff) | faithfulness mean diff [90% CI] | up / down / same "
    "| hallucinated a -> b (diff) | answers differ |",
    "|---|---|---|---|---|---|---|---|---|---|",
]


# pair 리포트. 두 쪽의 질문셋 구성이 다르면 오류. 셋마다 한 줄, 셋이 둘 이상이면 문항 id 앞에 셋 이름을 붙여
# 합친 '전체' 줄을 더한다.
# --split-by-truncation을 주면 한쪽의 잘림 표시(truncated / ok)로 문항을 나눠 다시 비교한다. 잘린 문항과
# 잘리지 않은 문항에서 점수 차이가 따로 어떻게 나는지 볼 수 있다(docstring의 사용 예는 J1 - J0 비교에서 J0 쪽
# 잘림 표시로 나눈다).
def pair_report(
    title: str, a_paths: list[Path], b_paths: list[Path], split_by_truncation: str | None
) -> str:
    a_sets, b_sets = _by_dataset(a_paths), _by_dataset(b_paths)
    if set(a_sets) != set(b_sets):
        raise ValueError(f"datasets differ: a has {sorted(a_sets)}, b has {sorted(b_sets)}")
    lines = [
        f"# Judgment comparison: {title}",
        "",
        f"- date: {datetime.now(UTC).isoformat()}",
        f"- a: {', '.join(display_path(p) for p in a_paths)}",
        f"- b: {', '.join(display_path(p) for p in b_paths)}",
        f"- diff = b - a per item; interval: paired percentile bootstrap, {BOOTSTRAP_RESAMPLES} "
        f"resamples, seed {BOOTSTRAP_SEED}, {CONFIDENCE:.0%}",
        "- items without a score on either side (no passages, judge error) are left out of that metric",
        "",
        *PAIR_HEADER,
    ]
    pooled_a, pooled_b = [], []
    for dataset in sorted(a_sets):
        a_rows, b_rows = a_sets[dataset], b_sets[dataset]
        lines.append(_pair_row(dataset, a_rows, b_rows))
        pooled_a += [{**r, "id": f"{dataset}/{r['id']}"} for r in a_rows]
        pooled_b += [{**r, "id": f"{dataset}/{r['id']}"} for r in b_rows]
    if len(a_sets) > 1:
        lines.append(_pair_row("all sets", pooled_a, pooled_b))

    if split_by_truncation:
        side = pooled_a if split_by_truncation == "a" else pooled_b
        flags = {r["id"]: r.get("truncation") for r in side}
        lines += [
            "",
            f"## Split by the truncation flag of side {split_by_truncation}",
            "",
            *PAIR_HEADER,
        ]
        for flag in ("truncated", "ok"):
            ids = {i for i, f in flags.items() if f == flag}
            if ids:
                lines.append(
                    _pair_row(
                        f"{flag} ({len(ids)})",
                        [r for r in pooled_a if r["id"] in ids],
                        [r for r in pooled_b if r["id"] in ids],
                    )
                )
    return "\n".join(lines)


# truncation 리포트. 판정을 실제로 보낸 행(원문 응답이나 오류가 있는 행)만 센다.
# - over context: 토크나이저 수가 문맥 - 1을 넘은 프롬프트(Ollama 0.35.1은 그보다 길면 자른다). 문맥은 --ctx로
#   주거나 기록의 judge_num_ctx를 쓴다.
# - truncated: 판정 결과의 잘림 표시 수.
# - offset: 잘리지 않은 프롬프트에서 Ollama가 읽은 수 - 토크나이저 수. 0 근처면 토크나이저로 센 값을 믿을 수
#   있다(카운터 보정 확인).
# 파일이 둘 이상이면 합계 줄과 잘림 비율을 더한다.
def truncation_report(paths: list[Path], ctx: int | None) -> str:
    lines = [
        "# Judge prompt truncation",
        "",
        f"- date: {datetime.now(UTC).isoformat()}",
        f"- truncated: prompt_eval_count < tokenizer count - {TRUNCATION_TOLERANCE}",
        "- over context: tokenizer count > context - 1 (Ollama 0.35.1 cuts above that); context = "
        + (f"{ctx} (given)" if ctx else "each run's num_ctx"),
        "- offset: prompt_eval_count - tokenizer count, on prompts that were not cut",
        "",
        "| run | judged | tokens counted p50 / max | over context | truncated | judge errors "
        "| offset median / min / max |",
        "|---|---|---|---|---|---|---|",
    ]
    total = defaultdict(int)
    for path in paths:
        rows = [r for r in read_jsonl(path) if r.get("raw") or r.get("error")]
        context = ctx or (rows[0].get("judge_num_ctx") if rows else None)
        counted = [r["prompt_tokens_counted"] for r in rows if r.get("prompt_tokens_counted") is not None]
        over = sum(1 for n in counted if context and n > context - 1)
        truncated = sum(1 for r in rows if r.get("truncation") == "truncated")
        errors = sum(1 for r in rows if r.get("error"))
        offsets = [
            r["prompt_eval_count"] - r["prompt_tokens_counted"]
            for r in rows
            if r.get("truncation") == "ok"
        ]
        counted_cell = f"{statistics.median(counted):.0f} / {max(counted)}" if counted else "n/a"
        offset_cell = (
            f"{statistics.median(offsets):+.0f} / {min(offsets):+d} / {max(offsets):+d}" if offsets else "n/a"
        )
        lines.append(
            f"| {path.name} | {len(rows)} | {counted_cell} | {over} | {truncated} | {errors} "
            f"| {offset_cell} |"
        )
        total["judged"] += len(rows)
        total["over"] += over
        total["truncated"] += truncated
        total["errors"] += errors
    if len(paths) > 1:
        rate = total["truncated"] / total["judged"] if total["judged"] else 0.0
        lines.append(
            f"| **all** | {total['judged']} | | {total['over']} | {total['truncated']} ({rate:.1%}) "
            f"| {total['errors']} | |"
        )
    return "\n".join(lines)


# 명령줄 진입점. pair는 --a, --b에 판정 파일을 여러 개 받을 수 있다. 콘솔이 표현하지 못하는 문자(한국어 등)가
# 있어도 죽지 않도록 표준 출력의 인코딩 오류를 역슬래시 표기로 바꾼다. 리포트는 시각을 붙인 파일 이름으로
# eval/reports/에 쓰고 화면에도 출력한다.
def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    pair = sub.add_parser("pair")
    pair.add_argument("--title", required=True)
    pair.add_argument("--tag", required=True)
    pair.add_argument("--a", type=Path, nargs="+", required=True)
    pair.add_argument("--b", type=Path, nargs="+", required=True)
    pair.add_argument("--split-by-truncation", choices=["a", "b"], default=None)
    trunc = sub.add_parser("truncation")
    trunc.add_argument("--tag", required=True)
    trunc.add_argument("--ctx", type=int, default=None, help="context the runs used, if not in the records")
    trunc.add_argument("paths", type=Path, nargs="+")
    args = parser.parse_args()
    sys.stdout.reconfigure(errors="backslashreplace")  # see eval/run_answer_eval.py

    if args.command == "pair":
        report = pair_report(args.title, args.a, args.b, args.split_by_truncation)
        name = f"judge_compare_{args.tag}"
    else:
        report = truncation_report(args.paths, args.ctx)
        name = f"judge_truncation_{args.tag}"
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path = write_report(f"{name}_{timestamp}.md", report)
    print(report)
    print(f"\nwritten to {path}")


if __name__ == "__main__":
    main()

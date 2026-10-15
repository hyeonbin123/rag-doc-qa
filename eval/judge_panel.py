"""다른 계열 판정기로 저장된 답 다시 판정하기와 Claude 라벨 일치도(docs/experiments.md v15 I5).

사용법:
    # 판정 점수를 보지 않고 라벨을 붙일 80문항 층화 표본(라벨러용 파일과 열쇠 파일)을 만든다
    python -m eval.judge_panel sample --blind <blind.jsonl> --key <key.jsonl>

    # 판정기별 결정 방향, 판정기 사이 순위 상관, 답 길이 상관, Claude 라벨과의 가중 kappa를 보고한다
    python -m eval.judge_panel report --tag v15_i5 --labels J1 J2 J3 \
        --claude eval/runs/v15_i5_claude_labels.jsonl --key eval/runs/v15_i5_panel_key.jsonl
"""

# [파일 역할] v15 I5의 표본 추출기와 분석기. 생성 없이, 지난 세 결정(v13 채택, v13 단계 B B2, v14)에 쓴 저장된
# 답 448개를 다른 계열 판정기(J2 gemma4:12b-it-qat, J3 qwen3.5:9b)로 다시 판정한 결과를 J1(qwen2.5:7b)과
# 나란히 본다. 과거 결정은 다시 열지 않고 보고만 한다.
# [왜 필요한가] A.X-4.0-Light는 J1과 같은 Qwen2.5-7B 계열이고 답이 3~5배 길다. 그래서 J1 점수에 자기 계열
# 선호와 긴 답 선호가 섞였을 수 있는데, 그 크기를 잰 적이 없다(README 한계). 다른 계열 판정기와, 판정 점수를
# 보지 않고 붙인 Claude 라벨 80문항으로 어느 판정 구성이 라벨과 더 맞는지 본다. 사람 라벨이 아니다.
# [표본] 층(언어 × 생성기 × J1 점수 구간) 안에서 답 길이 순으로 고르게 뽑는다. J1 점수 구간으로 층을 나누는
# 것은 낮은 점수 문항이 표본에 들어오게 하려는 것이고, 라벨러에게 주는 파일에는 점수가 없다.
# [연결] 판정 파일은 eval/run_judge.py가 쓴다(<gen>.<라벨>.judge.jsonl). bootstrap은 compare_judgments의 것을
# 쓴다.

from __future__ import annotations

import argparse
import hashlib
import random
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path

from eval.common import read_jsonl, write_json, write_jsonl, write_report
from eval.compare_judgments import paired_bootstrap_ci
from eval.judge import answer_sha1, judge_context
from eval.run_judge import judged_path

RUNS = Path(__file__).parent / "runs"
# 다시 판정할 저장된 답: 지난 세 결정의 결정 팔 파일들(J1 판정이 같은 파일에 붙어 있음). 비교 이름 → 팔 이름 →
# 생성 기록 목록. v13 채택은 가드가 한 번도 걸리지 않아 raw 팔이 결정 팔(lg)과 답이 같다.
COMPARISONS: dict[str, dict[str, list[Path]]] = {
    "v13_adopt": {
        "G0": [
            RUNS / "v13_adopt_g0_qa_test3b_ko.raw.gen.jsonl",
            RUNS / "v13_adopt_g0_qa_test3b_en.raw.gen.jsonl",
        ],
        "G3": [
            RUNS / "v13_adopt_g3_qa_test3b_ko.raw.gen.jsonl",
            RUNS / "v13_adopt_g3_qa_test3b_en.raw.gen.jsonl",
        ],
    },
    "v13b_b2": {
        "B0": [RUNS / "v13b_b2_g3_b0.lg.gen.jsonl"],
        "P": [RUNS / "v13b_b2_g3_p.lg.gen.jsonl"],
    },
    "v14": {
        "C3": [RUNS / f"v14_c3_{s}.lg.gen.jsonl" for s in ("qa_dev", "qa_dev_ko", "qa_dev2_ko")],
        "C4": [RUNS / f"v14_c4_{s}.lg.gen.jsonl" for s in ("qa_dev", "qa_dev_ko", "qa_dev2_ko")],
    },
}
# 각 비교에서 기준 팔(앞)과 바꾼 팔(뒤). 차이는 뒤 − 앞.
BASELINES = {"v13_adopt": ("G0", "G3"), "v13b_b2": ("B0", "P"), "v14": ("C3", "C4")}

SAMPLE_SIZE = 80
SAMPLE_SEED = 20261015
# 층 나누기: 생성기(A.X / Qwen2.5)와 언어로 네 칸, 칸마다 뽑을 수. Qwen 답은 v13 채택의 G0 80개뿐이라 칸이
# 작다.
CELL_QUOTA = {("qwen", "en"): 15, ("qwen", "ko"): 15, ("ax", "en"): 20, ("ax", "ko"): 30}
# 칸 안에서 J1 정확도 구간별 몫(낮은 점수부터). 몫보다 문항이 적으면 남는 수는 다음 구간으로 넘긴다.
SCORE_BANDS = (("low", (1, 2, 3)), ("four", (4,)), ("five", (5,)))
# 판정 구성의 채택 제안 기준: Claude 라벨과의 가중 kappa가 J1보다 이만큼 이상 높을 때.
KAPPA_MARGIN = 0.1


def all_gen_paths() -> list[Path]:
    return [p for arms in COMPARISONS.values() for paths in arms.values() for p in paths]


# 생성 기록 하나의 표본 키(파일 이름 + 문항 id). 라벨러 파일에는 이 키를 해시한 짧은 id만 들어간다.
def item_key(gen_path: Path, record: dict) -> str:
    return f"{gen_path.name}#{record['id']}"


def generator_family(record: dict) -> str:
    return "qwen" if str(record.get("model", "")).startswith("qwen2.5") else "ax"


# 표본 모집단: 결정 팔 파일의 모든 답. 같은 질문·같은 답·같은 문맥은 한 번만 넣는다(v13b B2의 B0는 v13 채택 G3
# 한국어와 같은 요청이라 답이 40개 모두 같았다).
def population(label: str = "J1") -> list[dict]:
    seen: set[tuple] = set()
    items = []
    for gen in all_gen_paths():
        judgments = {j["id"]: j for j in read_jsonl(judged_path(gen, label))}
        for r in read_jsonl(gen):
            fingerprint = (r["id"], answer_sha1(r["answer"]), tuple(c["chunk_id"] for c in r["chunks"]))
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            j = judgments.get(r["id"]) or {}
            items.append(
                {
                    "key": item_key(gen, r),
                    "record": r,
                    "family": generator_family(r),
                    "language": r["language"],
                    "j1": j.get("correctness_score"),
                    "length": len(r["answer"]),
                }
            )
    return items


# 층화 표본. 칸(생성기 × 언어)마다 몫만큼, 칸 안에서는 J1 구간별로 나눠 뽑는다. 구간 안에서는 seed로 섞은 뒤
# 답 길이 순으로 정렬해 같은 간격으로 고른다(길이 분포를 고르게 덮으려고).
def stratified_sample(items: list[dict], seed: int = SAMPLE_SEED) -> list[dict]:
    rng = random.Random(seed)
    chosen: list[dict] = []
    for (family, language), quota in CELL_QUOTA.items():
        cell = [i for i in items if i["family"] == family and i["language"] == language and i["j1"]]
        bands = [[i for i in cell if i["j1"] in scores] for _, scores in SCORE_BANDS]
        per_band = [quota // 3, quota // 3, quota - 2 * (quota // 3)]
        carry = 0
        for band, want in zip(bands, per_band, strict=True):
            want += carry
            rng.shuffle(band)
            band.sort(key=lambda i: i["length"])
            take = min(want, len(band))
            if take:
                step = len(band) / take
                chosen += [band[int(k * step)] for k in range(take)]
            carry = want - take
    return chosen


# 라벨러 파일의 짧은 id: 키의 sha1 앞 10자리. 키(어느 실행·어느 조건의 답인지)를 라벨러가 알 수 없게 한다.
def blind_id(key: str) -> str:
    return "s" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:10]


# sample 명령: 라벨러용 파일(질문·판정이 보는 문단·답·참고 답안, 점수와 출처 없음)과 열쇠 파일(짧은 id →
# 키·층)을 쓴다. 라벨러 파일은 짧은 id 순서로 섞어 둔다(층·조건 순서가 드러나지 않게).
def sample_command(blind_path: Path, key_path: Path) -> int:
    chosen = stratified_sample(population())
    blind = sorted(
        (
            {
                "sample_id": blind_id(i["key"]),
                "language": i["language"],
                "question": i["record"]["question"],
                "context_passages": judge_context(i["record"]),
                "answer": i["record"]["answer"],
                "reference_answer": i["record"]["reference_answer"],
            }
            for i in chosen
        ),
        key=lambda b: b["sample_id"],
    )
    keys = [
        {
            "sample_id": blind_id(i["key"]),
            "key": i["key"],
            "family": i["family"],
            "language": i["language"],
            "length": i["length"],
        }
        for i in chosen
    ]
    write_jsonl(blind_path, blind)
    write_jsonl(key_path, sorted(keys, key=lambda k: k["sample_id"]))
    print(f"{len(blind)} items -> {blind_path} (key {key_path})")
    return 0


# --- 통계 도구 ---


# 같은 값에는 평균 순위를 주는 순위.
def _ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def _pearson(x: list[float], y: list[float]) -> float | None:
    mx, my = statistics.fmean(x), statistics.fmean(y)
    sx = sum((a - mx) ** 2 for a in x) ** 0.5
    sy = sum((b - my) ** 2 for b in y) ** 0.5
    if not sx or not sy:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y, strict=True)) / (sx * sy)


# Spearman 순위 상관(순위의 Pearson 상관). 한쪽 값이 모두 같으면 None.
def spearman(x: list[float], y: list[float]) -> float | None:
    return _pearson(_ranks(x), _ranks(y)) if len(x) >= 2 else None


# 이차 가중 Cohen kappa. 값 자체의 차이 제곱을 가중치로 써서, 1~5 정수뿐 아니라 두 판정기 평균(0.5 단위)에도
# 그대로 쓴다. 1 − (관측 불일치 가중합 / 우연 불일치 가중합)이고, 우연 불일치는 두 쪽 주변 분포의 모든 짝으로
# 센다.
def quadratic_kappa(a: list[float], b: list[float]) -> float | None:
    n = len(a)
    if n == 0:
        return None
    observed = sum((x - y) ** 2 for x, y in zip(a, b, strict=True)) / n
    expected = sum((x - y) ** 2 for x in a for y in b) / (n * n)
    return None if expected == 0 else 1 - observed / expected


# kappa 차이(구성 − J1)의 bootstrap 90% 구간. 문항을 짝지은 채로 다시 뽑는다(compare_judgments와 같은
# seed·횟수).
def kappa_diff_ci(
    labels: list[float], base: list[float], other: list[float], n_resamples: int = 2000, seed: int = 20261003
) -> tuple[float, float]:
    rng = random.Random(seed)
    n = len(labels)
    diffs = []
    for _ in range(n_resamples):
        idx = [rng.randrange(n) for _ in range(n)]
        ka = quadratic_kappa([labels[i] for i in idx], [base[i] for i in idx])
        kb = quadratic_kappa([labels[i] for i in idx], [other[i] for i in idx])
        if ka is not None and kb is not None:
            diffs.append(kb - ka)
    diffs.sort()
    return diffs[int(0.05 * len(diffs))], diffs[int(0.95 * len(diffs)) - 1]


# 판정 라벨 하나의 정확도 점수: 키 → 점수.
def scores_for(label: str) -> dict[str, int]:
    out = {}
    for gen in all_gen_paths():
        path = judged_path(gen, label)
        if not path.exists():
            continue
        for j in read_jsonl(path):
            if j.get("correctness_score") is not None:
                out[f"{gen.name}#{j['id']}"] = j["correctness_score"]
    return out


# 한 비교(예: v13 채택 G0 → G3)의 판정기별 합과 차이 구간. 언어별과 전체.
def comparison_summary(name: str, label: str, scores: dict[str, int]) -> dict:
    base_arm, new_arm = BASELINES[name]
    arms = COMPARISONS[name]

    def by_id(arm: str) -> dict[tuple[str, str], tuple[str, int | None]]:
        out = {}
        for gen in arms[arm]:
            for r in read_jsonl(gen):
                out[(r["dataset"], r["id"])] = (r["language"], scores.get(f"{gen.name}#{r['id']}"))
        return out

    base, new = by_id(base_arm), by_id(new_arm)
    result = {}
    for scope in ("all", "en", "ko"):
        keys = [
            k
            for k in base
            if k in new
            and (scope == "all" or base[k][0] == scope)
            and base[k][1] is not None
            and new[k][1] is not None
        ]
        if not keys:
            continue
        diffs = [new[k][1] - base[k][1] for k in keys]
        mean, low, high = paired_bootstrap_ci(diffs)
        result[scope] = {
            "n": len(keys),
            base_arm: sum(base[k][1] for k in keys),
            new_arm: sum(new[k][1] for k in keys),
            "diff": sum(diffs),
            "mean_ci90": [round(mean, 3), round(low, 3), round(high, 3)],
        }
    return result


# report 명령의 본체.
def report(labels: list[str], claude_path: Path | None, key_path: Path | None) -> dict:
    scores = {label: scores_for(label) for label in labels}
    lengths = {f"{gen.name}#{r['id']}": len(r["answer"]) for gen in all_gen_paths() for r in read_jsonl(gen)}
    out: dict = {"labels": labels, "comparisons": {}, "spearman_between": {}, "length_spearman": {}}
    for name in COMPARISONS:
        out["comparisons"][name] = {label: comparison_summary(name, label, scores[label]) for label in labels}
    # 결정 방향이 J1과 같은지(전체 차이의 부호).
    out["direction_matches_j1"] = {
        name: {
            label: (
                (out["comparisons"][name][label]["all"]["diff"] > 0)
                == (out["comparisons"][name][labels[0]]["all"]["diff"] > 0)
            )
            for label in labels
        }
        for name in COMPARISONS
    }
    for i, a in enumerate(labels):
        for b in labels[i + 1 :]:
            keys = sorted(set(scores[a]) & set(scores[b]))
            out["spearman_between"][f"{a}~{b}"] = spearman(
                [scores[a][k] for k in keys], [scores[b][k] for k in keys]
            )
    for label in labels:
        keys = sorted(scores[label])
        out["length_spearman"][label] = spearman([lengths[k] for k in keys], [scores[label][k] for k in keys])
    if claude_path and key_path:
        out["kappa"] = kappa_report(labels, scores, claude_path, key_path)
    return out


# Claude 라벨과의 이차 가중 kappa: 판정기 단독, 그리고 두세 판정기 평균 구성. J1보다 KAPPA_MARGIN 이상 높은
# 구성이 있으면 제안한다(다음 등록 실험부터, 채택은 사람이 정함).
def kappa_report(
    labels: list[str], scores: dict[str, dict[str, int]], claude_path: Path, key_path: Path
) -> dict:
    keys = {k["sample_id"]: k["key"] for k in read_jsonl(key_path)}
    claude = {c["sample_id"]: c["correctness_score"] for c in read_jsonl(claude_path)}
    ids = sorted(i for i in claude if all(keys[i] in scores[label] for label in labels))
    gold = [float(claude[i]) for i in ids]
    configs: dict[str, list[float]] = {
        label: [float(scores[label][keys[i]]) for i in ids] for label in labels
    }
    for size in (2, 3):
        if len(labels) >= size:
            from itertools import combinations

            for combo in combinations(labels, size):
                configs["+".join(combo)] = [
                    statistics.fmean(scores[label][keys[i]] for label in combo) for i in ids
                ]
    base = configs[labels[0]]
    table = {}
    for name, values in configs.items():
        kappa = quadratic_kappa(gold, values)
        low, high = kappa_diff_ci(gold, base, values) if name != labels[0] else (0.0, 0.0)
        table[name] = {"kappa": kappa, "diff_vs_j1_ci90": [low, high]}
    j1 = table[labels[0]]["kappa"]
    better = [
        n
        for n, t in table.items()
        if t["kappa"] is not None and j1 is not None and t["kappa"] >= j1 + KAPPA_MARGIN
    ]
    return {
        "n": len(ids),
        "configs": table,
        "proposal": max(better, key=lambda n: table[n]["kappa"]) if better else None,
    }


def render(tag: str, result: dict) -> str:
    import json

    return f"# 판정 패널 {tag}\n\n```json\n{json.dumps(result, ensure_ascii=False, indent=2)}\n```\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="v15 I5 다른 계열 판정기 재판정과 Claude 라벨 일치도")
    sub = parser.add_subparsers(dest="command", required=True)
    sp = sub.add_parser("sample", help="라벨러용 80문항 층화 표본과 열쇠 파일을 만든다")
    sp.add_argument("--blind", type=Path, required=True)
    sp.add_argument("--key", type=Path, required=True)
    rp = sub.add_parser("report", help="판정기별 보고와 Claude 라벨 kappa")
    rp.add_argument("--tag", required=True)
    rp.add_argument("--labels", nargs="+", required=True, help="판정 라벨들. 첫 번째가 기준(J1)")
    rp.add_argument("--claude", type=Path, default=None)
    rp.add_argument("--key", type=Path, default=None)
    sub.add_parser("files", help="다시 판정할 생성 기록 경로를 한 줄에 하나씩 출력한다")
    args = parser.parse_args()
    if args.command == "sample":
        return sample_command(args.blind, args.key)
    if args.command == "files":
        for path in all_gen_paths():
            print(path.as_posix())
        return 0
    result = report(args.labels, args.claude, args.key)
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    write_json(RUNS / f"{args.tag}.panel.json", result)
    path = write_report(f"judge_panel_{args.tag}_{stamp}.md", render(args.tag, result))
    print(f"report {path}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(errors="backslashreplace")
    sys.exit(main())

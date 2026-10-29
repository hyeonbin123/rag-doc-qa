"""다른 계열 판정기로 저장된 답 다시 판정하기와 Claude 라벨 일치도(docs/experiments.md v15 I5).

사용법:
    # 판정 점수를 보지 않고 라벨을 붙일 80문항 층화 표본(라벨러용 파일과 열쇠 파일)을 만든다.
    # 커밋된 v15 표본(eval/runs/v15_i5_panel_*.jsonl)을 다시 뽑으려면 그때의 옛 지문인 --dedup v15를 준다
    python -m eval.judge_panel sample --blind <blind.jsonl> --key <key.jsonl> [--dedup content|v15]

    # 판정기별 결정 방향, 판정기 사이 순위 상관, 답 길이 상관(전체·생성기별), Claude 라벨과의 가중
    # kappa(단독·평균 구성, 가장 좋은 단독 판정기와의 차이), 라벨 기준 잔차-길이 상관을 보고한다
    python -m eval.judge_panel report --tag v15_i5 --labels J1 J2 J3 \
        --claude eval/runs/v15_i5_claude_labels.jsonl --key eval/runs/v15_i5_panel_key.jsonl
"""

# [파일 역할] v15 I5의 표본 추출기와 분석기. 생성 없이, 지난 세 결정(v13 채택, v13 단계 B B2, v14)에 쓴 저장된
# 답 448개를 다른 판정기(J2 gemma4:12b-it-qat, J3 qwen3.5:9b)로 다시 판정한 결과를 J1(qwen2.5:7b)과
# 나란히 본다. 과거 결정은 다시 열지 않고 보고만 한다. J2는 다른 계열이고, J3는 A.X의 바탕(Qwen2.5)과 같은
# Qwen 계열의 다른 세대다.
# [왜 필요한가] A.X-4.0-Light는 J1과 같은 Qwen2.5-7B 계열이고 답이 3~5배 길다. 그래서 J1 점수에 자기 계열
# 선호와 긴 답 선호가 섞였을 수 있는데, 그 크기를 잰 적이 없다(README 한계). 다른 판정기와, 판정 점수를
# 보지 않고 붙인 Claude 라벨 80문항으로 어느 판정 구성이 라벨과 더 맞는지 본다. 사람 라벨이 아니다.
# [표본] 층(언어 × 생성기 × J1 점수 구간) 안에서 답 길이 순으로 고르게 뽑는다. J1 점수 구간으로 층을 나누는
# 것은 낮은 점수 문항이 표본에 들어오게 하려는 것이고, 라벨러에게 주는 파일에는 점수가 없다.
# [2026-10-29 보강] (1) 같은 문항을 가리는 지문을 (데이터셋, id, 답, 청크 본문)으로 바꿨다. v15 표본에 쓴 옛
# 지문 (id, 답, 청크 id)은 다른 DB에서 만든 같은 답을 둘로 셌다(표본에 n086이 두 번). 분석(판정기 사이·길이
# 상관)과 새 표본은 새 지문을 쓰고, 커밋된 v15 표본 재현에만 옛 지문을 쓴다. (2) 보고에 생성기별 길이 상관,
# Claude 라벨 기준 잔차-길이 상관, 평균 구성과 가장 좋은 단독 판정기의 kappa 차이 구간, 표본 안 중복과 그것을
# 뺀 kappa를 더했다(docs/experiments.md v15 I5 결과의 추가 분석). 기록된 v15 kappa 표와
# eval/runs/v15_i5.panel.json은 그대로다.
# [연결] 판정 파일은 eval/run_judge.py가 쓴다(<gen>.<라벨>.judge.jsonl). bootstrap은 compare_judgments의 것을
# 쓴다.

from __future__ import annotations

import argparse
import hashlib
import random
import statistics
import sys
from datetime import UTC, datetime
from itertools import combinations
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
# 판정 구성의 채택 제안 기준: Claude 라벨과의 가중 kappa가 J1보다 이만큼 이상 높을 때. v15 I5 측정 전에 등록한
# 규칙이라 그대로 둔다. 이 규칙은 J1과만 견주므로 평균 구성이 가장 좋은 단독 판정기보다 나은지는 보지 않는다.
# 그 비교는 kappa_report의 diff_vs_best_single_ci90이 따로 보고한다.
KAPPA_MARGIN = 0.1
# 생성기 계열. A.X-4.0-Light(ax)와 Qwen2.5-7B(qwen). 길이 상관을 계열별로 나눌 때 쓴다.
FAMILIES = ("ax", "qwen")
# '같은 문항'을 가리는 지문의 종류(fingerprint).
# - "content"(기본, 2026-10-29부터): (데이터셋, id, 답의 sha1, 판정기·라벨러가 보는 청크 본문의 sha1).
#   판정기와 라벨러가 받는 입력(질문·문단·답·참고 답안)이 같으면 같은 문항이다. 청크 id는 DB마다
#   다르므로(복제·재적재 DB) 넣지 않는다. 데이터셋은 test3b 영어·한국어처럼 다른 셋이 같은 id를 쓰므로 넣는다.
# - "v15": v15 I5 표본을 뽑을 때 쓴 옛 지문 (id, 답의 sha1, 청크 id 목록). 다른 DB에서 만든 같은 답(v13b B2의
#   B0와 v13 채택 G3 한국어, 청크 id만 다름)을 둘로 셌다. 커밋된 v15 표본을 다시 뽑아 확인할 때만 쓴다.
DEDUP_SCHEMES = ("content", "v15")


def all_gen_paths() -> list[Path]:
    return [p for arms in COMPARISONS.values() for paths in arms.values() for p in paths]


# 생성 기록 하나의 표본 키(파일 이름 + 문항 id). 라벨러 파일에는 이 키를 해시한 짧은 id만 들어간다.
def item_key(gen_path: Path, record: dict) -> str:
    return f"{gen_path.name}#{record['id']}"


def generator_family(record: dict) -> str:
    return "qwen" if str(record.get("model", "")).startswith("qwen2.5") else "ax"


# 생성 기록 하나의 지문(위 DEDUP_SCHEMES). 지문이 같은 기록은 표본과 분석에서 한 번만 센다. 청크 본문은
# judge_context(판정기가 보는 형태, 순위 순서로 본문만 이은 것)의 sha1이다. 모르는 종류면 ValueError.
def fingerprint(record: dict, dedup: str = "content") -> tuple:
    if dedup == "content":
        context = hashlib.sha1(judge_context(record).encode("utf-8")).hexdigest()
        return (record.get("dataset"), record["id"], answer_sha1(record["answer"]), context)
    if dedup == "v15":
        return (record["id"], answer_sha1(record["answer"]), tuple(c["chunk_id"] for c in record["chunks"]))
    raise ValueError(f"unknown dedup scheme {dedup!r}; use one of {', '.join(DEDUP_SCHEMES)}")


# 결정 팔 파일의 모든 생성 기록: 키(파일 이름#id) → 기록, all_gen_paths() 순서. 분석이 답 길이·생성기·지문을
# 여기서 찾는다. 같은 답이 여러 파일에 있으면 키마다 따로 들어 있다(비교 요약은 팔마다 모든 문항을 쓰므로).
def records_by_key() -> dict[str, dict]:
    return {item_key(gen, r): r for gen in all_gen_paths() for r in read_jsonl(gen)}


# 중복을 뺀 키 집합: 지문이 같은 기록 중 처음(all_gen_paths 순서) 것만 남긴다. population()과 같은 규칙이라
# 표본과 분석이 같은 문항 집합을 본다. 입력은 records_by_key()의 결과.
def unique_keys(records: dict[str, dict], dedup: str = "content") -> set[str]:
    seen: set[tuple] = set()
    keep: set[str] = set()
    for key, record in records.items():
        mark = fingerprint(record, dedup)
        if mark not in seen:
            seen.add(mark)
            keep.add(key)
    return keep


# 표본 모집단: 결정 팔 파일의 모든 답. 지문(dedup)이 같은 답은 처음 것만 넣는다(v13b B2의 B0는 v13 채택 G3
# 한국어와 같은 요청이라 답이 40개 모두 같았다). 기본 "content"는 저장된 448개 중 402개를 남긴다(B0 40개, v13
# 채택 G0·G3 한국어에서 답이 같았던 1개, v14 C3·C4에서 문맥과 답이 같았던 5개를 뺌). "v15"는 v15 표본을 뽑은
# 옛 모집단(447개)이다.
def population(label: str = "J1", dedup: str = "content") -> list[dict]:
    if dedup not in DEDUP_SCHEMES:
        raise ValueError(f"unknown dedup scheme {dedup!r}; use one of {', '.join(DEDUP_SCHEMES)}")
    seen: set[tuple] = set()
    items = []
    for gen in all_gen_paths():
        judgments = {j["id"]: j for j in read_jsonl(judged_path(gen, label))}
        for r in read_jsonl(gen):
            mark = fingerprint(r, dedup)
            if mark in seen:
                continue
            seen.add(mark)
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
# 키·층)을 쓴다. 라벨러 파일은 짧은 id 순서로 섞어 둔다(층·조건 순서가 드러나지 않게). dedup은 모집단의 지문
# 종류다: 새 표본은 기본값("content"), 커밋된 v15 표본을 다시 뽑아 비교할 때만 "v15".
def sample_command(blind_path: Path, key_path: Path, dedup: str = "content") -> int:
    chosen = stratified_sample(population(dedup=dedup))
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


# 키 목록 위에서 x와 y의 Spearman을 전체("all")와 생성기 계열(FAMILIES)별로 낸다. x·y·families는 키 → 값 사전.
# 계열에 문항이 둘보다 적거나 한쪽 값이 모두 같으면 그 칸은 None.
# 왜 나누나: A.X 답은 Qwen 답보다 3~5배 길어(답 중앙값 약 800자 대 250자), 풀링한 길이 상관에는 '어느 생성기의
# 답인가'가 섞인다. 생성기 안의 상관과 함께 봐야 판정기의 길이 선호를 읽을 수 있다(docs/experiments.md v15 I5
# 결과의 추가 분석). y에 '판정 점수 − 기준 라벨'(잔차)을 넣으면 기준이 설명하지 못하는 길이 선호만 남는다.
def family_spearman(
    keys: list[str], x: dict[str, float], y: dict[str, float], families: dict[str, str]
) -> dict[str, float | None]:
    out = {"all": spearman([x[k] for k in keys], [y[k] for k in keys])}
    for family in FAMILIES:
        part = [k for k in keys if families[k] == family]
        out[family] = spearman([x[k] for k in part], [y[k] for k in part])
    return out


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


# kappa 차이(구성 − 비교 기준 구성)의 bootstrap 90% 구간. 문항을 짝지은 채로 다시 뽑는다. seed는
# compare_judgments와 같은 20261003이지만 횟수는 2,000회다(compare_judgments의 대응표본 구간은 10,000회). v15
# I5의 기록된 구간이 2,000회로 나왔으므로 기본값을 그대로 두고, 횟수를 바꾸려면 다음 등록 실험의 규칙에 먼저
# 적는다. 입력: 기준 라벨, 비교 기준 구성의 점수(base), 비교할 구성의 점수(other). 셋 모두 같은 문항 순서.
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


# 판정 라벨 하나의 정확도 점수: 키 → 점수. 중복을 빼지 않은 모든 키다(비교 요약은 팔마다 모든 문항을 쓰고,
# kappa는 표본 키로 찾는다). 판정기 사이·길이 상관은 report가 unique_keys로 중복을 뺀 키에서만 센다.
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


# report 명령의 본체. 비교 요약(결정 방향)은 팔마다 모든 문항으로, 판정기 사이 Spearman과 길이 상관은
# 중복(같은 지문)을 뺀 답으로 센다. 2026-10-29 전에는 중복도 셌다(v13b B2의 B0 40개 등 46개,
# eval/runs/v15_i5.panel.json의 spearman_between·length_spearman은 448개 값). length_spearman은 풀링 값,
# length_spearman_by_family는 그것을 생성기 계열별로 나눈 값이다.
def report(labels: list[str], claude_path: Path | None, key_path: Path | None) -> dict:
    scores = {label: scores_for(label) for label in labels}
    records = records_by_key()
    keep = unique_keys(records)
    lengths = {key: len(r["answer"]) for key, r in records.items()}
    families = {key: generator_family(r) for key, r in records.items()}
    out: dict = {
        "labels": labels,
        "answers": {"all": len(records), "unique": len(keep)},
        "comparisons": {},
        "spearman_between": {},
        "length_spearman": {},
        "length_spearman_by_family": {},
    }
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
            keys = sorted(set(scores[a]) & set(scores[b]) & keep)
            out["spearman_between"][f"{a}~{b}"] = spearman(
                [scores[a][k] for k in keys], [scores[b][k] for k in keys]
            )
    for label in labels:
        split = family_spearman(sorted(set(scores[label]) & keep), lengths, scores[label], families)
        out["length_spearman"][label] = split["all"]
        out["length_spearman_by_family"][label] = split
    if claude_path and key_path:
        out["kappa"] = kappa_report(labels, scores, claude_path, key_path, records)
    return out


# 표본 문항(ids) 위의 판정 구성별 점수: 판정기 단독(라벨 이름)과 두·세 판정기 평균("J1+J2" 꼴, 라벨 순서의
# 조합). 평균은 0.5·0.33 단위 값이 되지만 quadratic_kappa는 그대로 받는다. keys는 표본 id → 키.
def judge_configs(
    labels: list[str], scores: dict[str, dict[str, int]], keys: dict[str, str], ids: list[str]
) -> dict[str, list[float]]:
    configs: dict[str, list[float]] = {
        label: [float(scores[label][keys[i]]) for i in ids] for label in labels
    }
    for size in (2, 3):
        if len(labels) >= size:
            for combo in combinations(labels, size):
                configs["+".join(combo)] = [
                    statistics.fmean(scores[label][keys[i]] for label in combo) for i in ids
                ]
    return configs


# 표본 문항 중 지문이 같은 무리(둘 이상인 것만). 무리 안은 records 순서(all_gen_paths 순서)로 놓아 첫 것이
# population()이 남기는 문항이고, 무리끼리도 그 순서다. v15 표본은 옛 지문으로 뽑아 이런 무리가 있을 수 있다.
def duplicate_groups(
    ids: list[str], keys: dict[str, str], records: dict[str, dict], dedup: str = "content"
) -> list[list[str]]:
    order = {key: n for n, key in enumerate(records)}
    groups: dict[tuple, list[str]] = {}
    for sample_id in ids:
        groups.setdefault(fingerprint(records[keys[sample_id]], dedup), []).append(sample_id)
    found = [sorted(group, key=lambda s: order[keys[s]]) for group in groups.values() if len(group) > 1]
    return sorted(found, key=lambda group: order[keys[group[0]]])


# Claude 라벨과의 이차 가중 kappa: 판정기 단독, 그리고 두세 판정기 평균 구성. J1보다 KAPPA_MARGIN 이상 높은
# 구성이 있으면 제안한다(다음 등록 실험부터, 채택은 사람이 정함). 여기까지가 v15 I5에 등록한 보고이고 그대로
# 둔다. 2026-10-29에 더한 보고(결정 규칙은 바꾸지 않음):
# - 평균 구성마다 가장 좋은 단독 판정기(best_single)와의 kappa 차이 구간(diff_vs_best_single_ci90). 평균
#   구성은 J1(단독)이 아니라 같은 표본의 가장 좋은 단독과 견줘야 '평균을 쓸 값이 있는지'를 읽을 수
#   있다(v15에서 J2+J3 평균은 J2 단독보다 0.013 높았을 뿐임).
# - duplicates: 표본 안에서 지문이 같은 무리, dedup: 무리마다 첫 것만 남긴 표본의 kappa.
# - reference_length_spearman: 기준 라벨 자체의 답 길이 상관. residual_length_spearman: 판정기마다 (판정 점수
#   − 기준 라벨)의 길이 상관. 둘 다 중복을 뺀 표본에서 전체와 생성기 계열별로 낸다. 잔차 상관이 양수면
#   기준보다 긴 답에 더 준다는 뜻이다.
# records는 records_by_key()의 결과(답 길이·생성기·지문을 찾는 데 쓴다).
def kappa_report(
    labels: list[str],
    scores: dict[str, dict[str, int]],
    claude_path: Path,
    key_path: Path,
    records: dict[str, dict],
) -> dict:
    keys = {k["sample_id"]: k["key"] for k in read_jsonl(key_path)}
    claude = {c["sample_id"]: c["correctness_score"] for c in read_jsonl(claude_path)}
    ids = sorted(i for i in claude if all(keys[i] in scores[label] for label in labels))
    gold = [float(claude[i]) for i in ids]
    configs = judge_configs(labels, scores, keys, ids)
    base = configs[labels[0]]
    single = {label: quadratic_kappa(gold, configs[label]) for label in labels}
    rated = [label for label in labels if single[label] is not None]
    best_single = max(rated, key=lambda label: single[label]) if rated else None
    table = {}
    for name, values in configs.items():
        kappa = quadratic_kappa(gold, values)
        low, high = kappa_diff_ci(gold, base, values) if name != labels[0] else (0.0, 0.0)
        entry: dict = {"kappa": kappa, "diff_vs_j1_ci90": [low, high]}
        if name not in labels and best_single is not None:
            best_low, best_high = kappa_diff_ci(gold, configs[best_single], values)
            entry.update(best_single=best_single, diff_vs_best_single_ci90=[best_low, best_high])
        table[name] = entry
    j1 = table[labels[0]]["kappa"]
    better = [
        n
        for n, t in table.items()
        if t["kappa"] is not None and j1 is not None and t["kappa"] >= j1 + KAPPA_MARGIN
    ]

    groups = duplicate_groups(ids, keys, records)
    dropped = {sample_id for group in groups for sample_id in group[1:]}
    kept = [n for n, sample_id in enumerate(ids) if sample_id not in dropped]
    kept_gold = [gold[n] for n in kept]
    kept_keys = [keys[ids[n]] for n in kept]
    lengths = {key: len(records[key]["answer"]) for key in kept_keys}
    families = {key: generator_family(records[key]) for key in kept_keys}
    reference = {keys[ids[n]]: gold[n] for n in kept}
    residual = {
        label: family_spearman(
            kept_keys, lengths, {keys[ids[n]]: configs[label][n] - gold[n] for n in kept}, families
        )
        for label in labels
    }
    return {
        "n": len(ids),
        "configs": table,
        "proposal": max(better, key=lambda n: table[n]["kappa"]) if better else None,
        "duplicates": groups,
        "dedup": {
            "n": len(kept),
            "kappa": {
                name: quadratic_kappa(kept_gold, [values[n] for n in kept])
                for name, values in configs.items()
            },
        },
        "reference_length_spearman": family_spearman(kept_keys, lengths, reference, families),
        "residual_length_spearman": residual,
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
    sp.add_argument(
        "--dedup",
        choices=DEDUP_SCHEMES,
        default="content",
        help="모집단에서 같은 문항을 가리는 지문. content(기본): 데이터셋·id·답·청크 본문. "
        "v15: 커밋된 v15 표본을 뽑은 옛 지문(id·답·청크 id, 다른 DB의 같은 답을 둘로 셈). 재현 확인에만 쓴다",
    )
    rp = sub.add_parser("report", help="판정기별 보고와 Claude 라벨 kappa")
    rp.add_argument("--tag", required=True)
    rp.add_argument("--labels", nargs="+", required=True, help="판정 라벨들. 첫 번째가 기준(J1)")
    rp.add_argument("--claude", type=Path, default=None)
    rp.add_argument("--key", type=Path, default=None)
    sub.add_parser("files", help="다시 판정할 생성 기록 경로를 한 줄에 하나씩 출력한다")
    args = parser.parse_args()
    if args.command == "sample":
        return sample_command(args.blind, args.key, args.dedup)
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

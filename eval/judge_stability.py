"""판정 흔들림 진단(docs/experiments.md v15 I2), 반복 판정 비교, 여러 판정의 중앙값·평균 합치기.

사용법:
    # 같은 저장된 답을 여러 조건(패스)으로 판정한 뒤, 기준 패스와 문항별로 비교하고 규칙대로 판정 방식을
    # 고른다
    python -m eval.judge_stability compare --tag v15_i2 --base J1sA1 \
        --passes J1sA2 J1sR J1sF1 J1sF2 J1sL --gen eval/runs/v14_c3_qa_dev.lg.gen.jsonl ...

    # 같은 답에 대한 판정 파일 세 개를 문항별 중앙값으로 합쳐 새 라벨의 판정 파일을 쓴다
    python -m eval.judge_stability median --labels J1a J1b J1c --out-label J1m3 --gen <gen.jsonl> ...

    # 같은 답을 같은 판정기로 여러 번 판정한 파일들이 서로 얼마나 다른지 센다(첫 라벨이 기준)
    python -m eval.judge_stability repeats --tag v15_J1v15 \
        --labels J1v15r1 J1v15r2 J1v15r3 --gen <gen.jsonl> ...

    # 두 판정기의 판정을 문항별 평균으로 합쳐 새 라벨의 판정 파일을 쓴다
    python -m eval.judge_stability average --labels J2 J3 --out-label J23 --gen <gen.jsonl> ...
"""

# [파일 역할] v15 I2 진단의 분석기. 저장된 dev 답 104개를 같은 J1 설정으로 여러 번(같은 순서 두 번, 역순,
# 문항마다 캐시 되돌리기 정순·역순, 모델 다시 올린 뒤) 판정한 파일들을 문항 단위로 비교해, 판정 흔들림의 원인
# 후보를 가르고 이후 비교에 쓸 판정 방식을 규칙대로 정한다.
# [왜 필요한가] v13에서 같은 답·같은 프롬프트·같은 순서인데도 J1 원문이 40문항 중 5개 달랐다. 원인이 '앞
# 문항이 남긴 프롬프트 캐시'인지, 같은 순서에서도 생기는 비결정성인지에 따라 처방이 다르다(캐시면 문항마다
# 캐시 되돌리기, 비결정성이면 여러 번 판정의 중앙값). 규칙은 측정 전에 docs/experiments.md v15에 적었고, 이
# 파일의 decide()가 그 규칙을 코드로 옮긴 것이다.
# [반복 판정·평균] repeats는 같은 답을 같은 판정기로 여러 번 판정한 파일들(예: v15 I3~I5의 같은
# 순서 3회)을 비교해 반복이 점수를 실제로 바꿨는지 센다. v15의 3회는 커밋된 1,847문항에서 점수를
# 한 번도 바꾸지 않아, v16부터 결정 판정은 1회 + 경계 규칙이 됐다(docs/experiments.md의 '규칙
# 변경 (v16부터): 판정 절차'). 경계 규칙으로 이력이 다른 판정을 더 모았을 때도 같은 명령으로 차이를
# 기록한다. average는 판정기 둘의 평균 구성(v15 I5에서 비교한 J2+J3 등)으로 결정할 때 쓸 판정
# 파일을 만든다.
# [연결] 판정 파일은 eval/run_judge.py가 쓴다(<gen>.<라벨>.judge.jsonl). median·average가 쓴 파일은
# eval/generator_arms.py summary --label <out-label>과 eval/refusal.py --label <out-label>로 그대로
# 읽힌다.

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path

from eval.answer_report import display_path
from eval.common import RUNS_DIR, read_jsonl, write_json, write_jsonl, write_report
from eval.run_judge import judged_path, meta_path

# 패스 이름의 뜻(docs/experiments.md v15 I2). 기준(A1)과 다섯 패스.
PASS_ROLES = {
    "A2": "같은 순서로 한 번 더",
    "R": "역순",
    "F1": "문항마다 캐시 되돌리기, 정순",
    "F2": "문항마다 캐시 되돌리기, 역순",
    "L": "모델을 내렸다가 다시 올린 뒤 정순",
}


# (데이터셋, 문항 id) → 판정 기록. 판정 순서가 달라도 같은 문항끼리 비교하려고 키로 묶는다.
def load_judgments(gen_paths: list[Path], label: str) -> dict[tuple[str, str], dict]:
    out: dict[tuple[str, str], dict] = {}
    for gen in gen_paths:
        for j in read_jsonl(judged_path(gen, label)):
            out[(j.get("dataset") or gen.name, j["id"])] = j
    return out


# 판정 기록의 점수 묶음(정확도, 충실도, 환각). 두 판정의 '점수가 같은가'는 이 셋이 모두 같은지로
# 가른다(pass_diff, repeats, average가 같은 정의를 쓴다).
def _scores(judgment: dict) -> tuple:
    return (
        judgment.get("correctness_score"),
        judgment.get("faithfulness_score"),
        judgment.get("hallucinated"),
    )


# 두 패스의 차이: 판정 원문(raw)이 다른 문항 수, 점수(정확도·충실도·환각) 중 하나라도 다른 문항 수, 정확도 합.
# 판정이 없는 문항(청크 0개, 오류)은 두 패스 모두 없을 때만 같다고 본다.
def pass_diff(base: dict[tuple[str, str], dict], other: dict[tuple[str, str], dict]) -> dict:
    if set(base) != set(other):
        raise ValueError("the two passes judged different items")
    raw_diff = score_diff = 0
    changed: list[str] = []
    for key, b in base.items():
        o = other[key]
        if b.get("raw") != o.get("raw"):
            raw_diff += 1
        if _scores(b) != _scores(o):
            score_diff += 1
            changed.append(key[1])
    return {
        "raw_diff": raw_diff,
        "score_diff": score_diff,
        "correctness_sum_base": sum(j.get("correctness_score") or 0 for j in base.values()),
        "correctness_sum": sum(j.get("correctness_score") or 0 for j in other.values()),
        "changed_ids": sorted(changed),
    }


# 패스의 보고용 통계: 판정 시간 중앙값과, Ollama가 알려 준 경우 캐시에서 다시 쓴 프롬프트 토큰 수의 분포.
def pass_stats(judgments: dict[tuple[str, str], dict]) -> dict:
    times = [j["judge_ms"] for j in judgments.values() if j.get("judge_ms") is not None]
    cached = [
        j["prompt_eval_cached_count"]
        for j in judgments.values()
        if j.get("prompt_eval_cached_count") is not None
    ]
    return {
        "n": len(judgments),
        "judge_ms_p50": statistics.median(times) if times else None,
        "cached_tokens_seen": len(cached),
        "cached_tokens_p50": statistics.median(cached) if cached else None,
        "cached_tokens_max": max(cached) if cached else None,
    }


# 측정 전에 등록한 결정 규칙(docs/experiments.md v15 I2). diffs는 패스 이름(A2, R, F1, F2, L) → pass_diff
# 결과이고, F2는 기준 A1이 아니라 F1과 비교한 결과다. 같음·다름은 판정 원문(raw)으로 가른다.
# - (b) A2가 A1과 다르면: 같은 순서에서도 비결정 → 이후 결정 판정은 같은 순서 3회의 문항별 중앙값(J1×3)
# - (c) A2 = A1이고 R과 L이 모두 A1과 같으면: 흔들림이 재현되지 않음 → 판정 설정 그대로(J1), /api/ps 기록만
#   더함
# - (a) A2 = A1, R 또는 L이 다름, F2 = F1이면: 캐시(앞 문항) 원인 → 이후 판정은 문항마다 캐시 되돌리기(J1f)
# - (d) A2 = A1, R 또는 L이 다름, F2 ≠ F1이면: 순서에 기대지만 캐시 되돌리기로 없어지지 않음 → 이후 결정
#   판정은 세 순서(정순, 역순, 캐시 되돌리기 정순) 판정의 문항별 중앙값(J1×3o)
def decide(diffs: dict[str, dict]) -> dict:
    if diffs["A2"]["raw_diff"] >= 1:
        outcome, method = "b", "J1x3_same_order_median"
    elif diffs["R"]["raw_diff"] == 0 and diffs["L"]["raw_diff"] == 0:
        outcome, method = "c", "J1"
    elif diffs["F2"]["raw_diff"] == 0:
        outcome, method = "a", "J1f"
    else:
        outcome, method = "d", "J1x3_three_order_median"
    return {"outcome": outcome, "judge_method": method}


# compare 명령: 기준 패스와 다섯 패스를 읽어 차이·통계·결정을 JSON과 마크다운 리포트로 쓴다.
def compare(tag: str, gen_paths: list[Path], base_label: str, pass_labels: dict[str, str]) -> dict:
    base = load_judgments(gen_paths, base_label)
    passes = {name: load_judgments(gen_paths, label) for name, label in pass_labels.items()}
    diffs = {name: pass_diff(base, passes[name]) for name in ("A2", "R", "F1", "L")}
    diffs["F2"] = pass_diff(passes["F1"], passes["F2"])  # 캐시 되돌리기 정순과 역순끼리
    result = {
        "tag": tag,
        "date": datetime.now(UTC).isoformat(),
        "base_label": base_label,
        "pass_labels": pass_labels,
        "gen_files": [str(p) for p in gen_paths],
        "diffs": diffs,
        "stats": {"A1": pass_stats(base), **{n: pass_stats(p) for n, p in passes.items()}},
        "ps_before": {
            label: _ps_models(gen_paths[0], label) for label in [base_label, *pass_labels.values()]
        },
        **decide(diffs),
    }
    return result


# 판정 실행 기록(.meta.json)에서 판정 직전 /api/ps에 올라 있던 모델 이름과 GPU 적재 여부를 꺼낸다(보고용).
def _ps_models(gen_path: Path, label: str) -> list[dict]:
    meta_file = meta_path(judged_path(gen_path, label))
    if not meta_file.exists():
        return []
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    models = ((meta.get("ollama_ps_before") or {}).get("models")) or []
    return [{"name": m.get("name"), "full_gpu": m.get("size_vram") == m.get("size")} for m in models]


# 리포트(마크다운). 패스마다 기준과 다른 문항 수와 정확도 합, 그리고 결정.
def render(result: dict) -> str:
    lines = [
        f"# 판정 흔들림 진단 {result['tag']}",
        "",
        f"- 기준 패스: `{result['base_label']}` (같은 순서 첫 번째)",
        f"- 결정: ({result['outcome']}) → 이후 판정 방식 `{result['judge_method']}`",
        "",
        "| 패스 | 뜻 | 비교 대상 | 원문이 다른 문항 | 점수가 다른 문항 "
        "| 정확도 합 (대상 → 패스) | 바뀐 문항 |",
        "|---|---|---|---|---|---|---|",
    ]
    for name in ("A2", "R", "F1", "F2", "L"):
        d = result["diffs"][name]
        against = "F1" if name == "F2" else "A1"
        ids = ", ".join(d["changed_ids"][:12]) + (" …" if len(d["changed_ids"]) > 12 else "")
        lines.append(
            f"| {name} | {PASS_ROLES[name]} | {against} | {d['raw_diff']} | {d['score_diff']} | "
            f"{d['correctness_sum_base']} → {d['correctness_sum']} | {ids} |"
        )
    lines += [
        "",
        "| 패스 | 판정 시간 p50 (ms) | 캐시 재사용 토큰 기록 수 | 캐시 재사용 p50 / 최대 |",
        "|---|---|---|---|",
    ]
    for name, s in result["stats"].items():
        lines.append(
            f"| {name} | {s['judge_ms_p50']:.0f} | {s['cached_tokens_seen']} | "
            f"{s['cached_tokens_p50']} / {s['cached_tokens_max']} |"
            if s["judge_ms_p50"] is not None
            else f"| {name} | - | {s['cached_tokens_seen']} | - |"
        )
    return "\n".join(lines) + "\n"


# median 명령: 같은 답에 대한 판정 파일 여러 개(보통 3개)를 문항별로 합친다. 정확도·충실도는 중앙값(3개면
# 가운데 값), 환각은 다수결이다. 한 판정이라도 오류·빈 판정이면 그 문항은 빈 판정(점수 None)으로 둔다. 판정
# 순서는 첫 파일 것을 따른다. 결과 파일은 다른 판정 파일과 같은 모양이라 generator_arms summary가 그대로
# 읽는다.
def median_judgments(per_label: list[list[dict]], out_label: str) -> list[dict]:
    keyed = [{(j.get("dataset"), j["id"]): j for j in judgments} for judgments in per_label]
    merged = []
    for first in per_label[0]:
        key = (first.get("dataset"), first["id"])
        group = [k[key] for k in keyed]
        record = dict(first)
        record.update(judge_label=out_label, raw=None, merged_from=[g.get("judge_label") for g in group])
        if any(g.get("error") or g.get("correctness_score") is None for g in group):
            record.update(correctness_score=None, faithfulness_score=None, hallucinated=None)
        else:
            record.update(
                correctness_score=int(statistics.median_low(g["correctness_score"] for g in group)),
                faithfulness_score=int(statistics.median_low(g["faithfulness_score"] for g in group)),
                hallucinated=sum(bool(g["hallucinated"]) for g in group) * 2 > len(group),
            )
        merged.append(record)
    return merged


# 합칠 판정 파일들이 같은 문항에서 같은 답을 판정했는지 확인한다. groups는 (라벨 이름, {(데이터셋, id):
# 판정}) 목록이고 첫 묶음이 기준이다. 문항 집합이 다르거나 answer_sha1이 다른 문항이 있으면 ValueError를
# 낸다. 다른 답의 판정을 반복의 차이나 판정기의 차이로 잘못 세지 않으려는 것이다. 사전이 아니라 목록을 받는
# 것은 같은 이름의 라벨이 둘 와도 확인을 건너뛰지 않게 하려는 것이다. where는 오류 문구에 붙일 위치(생성
# 기록 이름)다.
def _check_same_answers(groups: list[tuple[str, dict]], where: str) -> None:
    (first, base), *rest = groups
    for label, judgments in rest:
        if set(judgments) != set(base):
            raise ValueError(f"{where}: {label} judged different items than {first}")
        for key, j in judgments.items():
            if j.get("answer_sha1") != base[key].get("answer_sha1"):
                raise ValueError(f"{where}: {label} judged a different answer than {first} for {key[1]}")


# repeats 명령: 같은 답을 같은 판정기로 여러 번 판정한 라벨들(첫 라벨이 기준)을 생성 기록마다 비교한다.
# - vs_first: 기준 다음 라벨마다 판정 원문이 다른 문항 수·점수가 다른 문항 수(pass_diff)와 점수가 바뀐
#   문항('<생성 기록 이름>#<id>')
# - any_raw_diff·any_score_diff: 어느 라벨에서든 원문·점수가 다른 문항 수(문항 하나는 한 번만 셈)
# - first_differs_from_median: 기준의 점수가 모든 라벨의 문항별 중앙값(median_judgments와 같은 규칙)과 다른
#   문항 수. 0이면 그 반복을 한 번으로 줄여도 바뀌는 점수가 없다(v15 I3~I5의 3회가 그랬음)
# - correctness_sum: 라벨마다와 중앙값의 정확도 합, stats: 라벨마다 판정 시간·캐시 재사용 토큰(pass_stats),
#   per_file: 생성 기록마다 문항 수와 라벨별 차이 수
# 생성 기록마다 따로 읽는 것은 같은 (데이터셋, id)가 다른 팔의 생성 기록에도 있어서다. load_judgments로
# 한꺼번에 읽으면 서로 덮어써 문항이 빠진다. 다른 문항·다른 답을 판정한 라벨이 섞이면 ValueError.
def repeats(gen_paths: list[Path], labels: list[str]) -> dict:
    if len(labels) < 2:
        raise ValueError("repeats needs at least two labels")
    first, *others = labels
    vs_first: dict[str, dict] = {label: {"raw_diff": 0, "score_diff": 0, "changed": []} for label in others}
    sums = dict.fromkeys([*labels, "median"], 0)
    pooled: dict[str, dict] = {label: {} for label in labels}
    per_file = []
    n = any_raw = any_score = first_vs_median = 0
    for gen in gen_paths:
        loaded = [(label, load_judgments([gen], label)) for label in labels]
        _check_same_answers(loaded, gen.name)
        base = loaded[0][1]
        row: dict = {"gen": display_path(gen), "n": len(base), "raw_diff": {}, "score_diff": {}}
        for label, judgments in loaded[1:]:
            diff = pass_diff(base, judgments)
            vs_first[label]["raw_diff"] += diff["raw_diff"]
            vs_first[label]["score_diff"] += diff["score_diff"]
            vs_first[label]["changed"] += [f"{gen.name}#{item}" for item in diff["changed_ids"]]
            row["raw_diff"][label] = diff["raw_diff"]
            row["score_diff"][label] = diff["score_diff"]
        # 문항마다: 라벨들 사이에 원문·점수가 갈리는지, 기준이 중앙값과 같은지. 키는 load_judgments와 같게
        # (데이터셋이 없으면 생성 기록 이름, id)로 만든다.
        for merged in median_judgments([list(j.values()) for _, j in loaded], "median"):
            key = (merged.get("dataset") or gen.name, merged["id"])
            group = [judgments[key] for _, judgments in loaded]
            any_raw += len({g.get("raw") for g in group}) > 1
            any_score += len({_scores(g) for g in group}) > 1
            first_vs_median += _scores(base[key]) != _scores(merged)
            sums["median"] += merged.get("correctness_score") or 0
        for label, judgments in loaded:
            sums[label] += sum(j.get("correctness_score") or 0 for j in judgments.values())
            pooled[label].update({(gen.name, *key): j for key, j in judgments.items()})
        n += len(base)
        per_file.append(row)
    return {
        "labels": labels,
        "gen_files": [display_path(p) for p in gen_paths],
        "n": n,
        "any_raw_diff": any_raw,
        "any_score_diff": any_score,
        "first_differs_from_median": first_vs_median,
        "vs_first": vs_first,
        "correctness_sum": sums,
        "stats": {label: pass_stats(pooled[label]) for label in labels},
        "per_file": per_file,
    }


# repeats 리포트(마크다운): 요약 줄, 라벨마다 기준과 다른 문항 수·정확도 합·판정 시간·캐시 재사용 토큰, 그리고
# 반복 사이에 다른 문항이 있는 생성 기록과 점수가 바뀐 문항(있을 때만).
def render_repeats(result: dict) -> str:
    first, *others = result["labels"]
    lines = [
        f"# 반복 판정 비교 {result['tag']}",
        "",
        f"- 라벨: `{first}`(기준), " + ", ".join(f"`{label}`" for label in others),
        f"- 생성 기록 {len(result['gen_files'])}개, 문항 {result['n']}",
        f"- 어느 반복에서든 판정 원문이 다른 문항: {result['any_raw_diff']}, 점수가 다른 문항: "
        f"{result['any_score_diff']}",
        "- 기준의 점수가 문항별 중앙값(정확도·충실도는 가운데 값, 환각은 다수결)과 다른 문항: "
        f"{result['first_differs_from_median']}",
        "",
        "| 라벨 | 기준과 원문이 다른 문항 | 점수가 다른 문항 | 정확도 합 | 판정 시간 p50 (ms) "
        "| 캐시 재사용 토큰 기록 수 | 캐시 재사용 p50 / 최대 |",
        "|---|---|---|---|---|---|---|",
    ]
    for label in result["labels"]:
        d = result["vs_first"].get(label)
        s = result["stats"][label]
        p50 = "-" if s["judge_ms_p50"] is None else f"{s['judge_ms_p50']:.0f}"
        lines.append(
            f"| {label} | {d['raw_diff'] if d else '-'} | {d['score_diff'] if d else '-'} "
            f"| {result['correctness_sum'][label]} | {p50} | {s['cached_tokens_seen']} "
            f"| {s['cached_tokens_p50']} / {s['cached_tokens_max']} |"
        )
    lines.append(f"| 중앙값 | | | {result['correctness_sum']['median']} | | | |")
    differing = [
        f for f in result["per_file"] if any(f["raw_diff"].values()) or any(f["score_diff"].values())
    ]
    if differing:
        lines += [
            "",
            "| 반복 사이에 다른 문항이 있는 생성 기록 | 문항 | 원문이 다른 문항 | 점수가 다른 문항 |",
            "|---|---|---|---|",
        ]
        for f in differing:
            raw = ", ".join(f"{label} {k}" for label, k in f["raw_diff"].items())
            score = ", ".join(f"{label} {k}" for label, k in f["score_diff"].items())
            lines.append(f"| {f['gen']} | {f['n']} | {raw} | {score} |")
    changed = sorted({item for label in others for item in result["vs_first"][label]["changed"]})
    if changed:
        lines += ["", "점수가 바뀐 문항: " + ", ".join(changed[:40]) + (" …" if len(changed) > 40 else "")]
    return "\n".join(lines) + "\n"


# 평균 판정 기록에서 비우는 필드. 한 번의 판정 호출이 낸 값(원문, 시간, 토큰 수, 멈춘 이유, 캐시 재사용
# 토큰, 캐시 되돌리기 결과)이라 평균 기록에는 그에 맞는 값이 없다. 원래 값은 merged_from 라벨의 판정
# 파일에 그대로 있다.
AVERAGE_CLEARED_FIELDS = (
    "raw",
    "judge_ms",
    "prompt_eval_count",
    "eval_count",
    "done_reason",
    "prompt_eval_cached_count",
    "prompt_tokens_counted",
    "flush",
)
# 잘림 상태를 합칠 때의 순서(앞이 더 나쁨). 판정기마다 토크나이저가 달라 한쪽만 잘릴 수 있으므로 평균
# 기록에는 가장 나쁜 상태를 남긴다(eval/compare_judgments.py truncation이 평균 라벨에서도 잘림을 보게).
TRUNCATION_SEVERITY = ("error", "truncated", "unchecked", "ok")


# 판정 묶음의 잘림 상태 중 가장 나쁜 것. 알 수 없는 값만 있으면 첫 판정의 값을 그대로 둔다.
def _worst_truncation(group: list[dict]) -> str | None:
    states = [g.get("truncation") for g in group]
    known = [state for state in TRUNCATION_SEVERITY if state in states]
    return known[0] if known else states[0]


def average_judgments(per_label: list[list[dict]], out_label: str, where: str = "judgments") -> list[dict]:
    """판정기마다 같은 답을 판정한 파일들을 문항별 평균으로 합친 판정 기록 목록을 돌려준다.

    규칙:
    - 정확도·충실도: 판정기 점수의 평균(statistics.fmean). 판정기 둘이면 0.5점 단위(4와 5 → 4.5)이고
      반올림하지 않는다. v15 I5가 Claude 라벨과의 kappa를 잰 평균 구성(eval/judge_panel.py의
      judge_configs)과 같은 값이라, 잰 구성 그대로 결정에 쓰려는 것이다.
    - 환각: 한 판정기라도 표시하면 표시(any). 평균으로 지우지 않고 보수적으로 센다.
    - 한 판정기라도 오류·빈 판정(점수 None, 청크 0개 문항 포함)이면 그 문항은 빈 판정(점수 None)이고 첫 오류
      문구를 error에 남긴다. median_judgments와 같은 처리다.
    - truncation은 가장 나쁜 상태(error > truncated > unchecked > ok). 한 번의 호출이 낸 값(원문, 시간,
      토큰 수 등, AVERAGE_CLEARED_FIELDS)은 비우고, judge_model은 판정 모델 이름을 '+'로 잇고,
      merged_from에 합친 라벨을 남긴다. 순서와 나머지 필드(id, dataset, order_index 등)는 첫 파일을 따른다.

    결과는 다른 판정 파일과 같은 모양이라 eval/generator_arms.py summary와 eval/refusal.py가 그대로 읽고
    점수를 합친다(합이 정수가 아니어도 됨). 문턱 비교(예: eval/refusal.py dev의 '판정 정확도 4 이상')는
    평균값으로 한다(4와 3이면 3.5라 4 미만). 다른 문항이나 다른 답(answer_sha1)을 판정한 파일이 섞이면
    ValueError. where는 오류 문구에 붙일 위치(생성 기록 이름)다.
    """
    if len(per_label) < 2:
        raise ValueError("average needs at least two labels")
    keyed = [{(j.get("dataset"), j["id"]): j for j in judgments} for judgments in per_label]
    names = [
        (judgments[0].get("judge_label") if judgments else None) or f"label {i + 1}"
        for i, judgments in enumerate(per_label)
    ]
    _check_same_answers(list(zip(names, keyed, strict=True)), where)
    merged = []
    for first in per_label[0]:
        key = (first.get("dataset"), first["id"])
        group = [k[key] for k in keyed]
        record = dict(first)
        record.update(dict.fromkeys(AVERAGE_CLEARED_FIELDS))
        record.update(
            judge_label=out_label,
            judge_model="+".join(dict.fromkeys(str(g.get("judge_model")) for g in group)),
            merged_from=[g.get("judge_label") for g in group],
            error=next((g["error"] for g in group if g.get("error")), None),
            truncation=_worst_truncation(group),
        )
        if any(g.get("error") or (None in _scores(g)) for g in group):
            record.update(correctness_score=None, faithfulness_score=None, hallucinated=None)
        else:
            record.update(
                correctness_score=statistics.fmean(g["correctness_score"] for g in group),
                faithfulness_score=statistics.fmean(g["faithfulness_score"] for g in group),
                hallucinated=any(bool(g["hallucinated"]) for g in group),
            )
        merged.append(record)
    return merged


# median·average의 --out-label이 --labels 중 하나와 같은 판정 파일을 가리키는지 본다(2026-11-05). 판정 파일
# 이름이 <gen>.<라벨>.judge.jsonl이라, 대소문자를 가리지 않는 파일 시스템(측정이 도는 Windows NTFS, macOS 기본
# APFS)에서는 대소문자만 다른 라벨(J1과 j1)이 같은 파일이 된다. 그래서 문자열을 그대로 비교하지 않고
# casefold()로 비교한다(그대로 비교하던 때는 'median --labels J1 J1b --out-label j1'이 가드를 지나 J1 판정
# 파일을 덮어썼다). 대소문자를 가리는 Linux에서는 둘이 다른 파일이지만, 파일 시스템을 묻지 않고 라벨로 보므로
# 어디서 돌려도 같게 막는다. 대소문자만 다른 라벨은 기록을 읽을 때도 헷갈려 막아서 잃는 쓰임이 없다.
def _out_label_overlaps(out_label: str, labels: list[str]) -> bool:
    folded = out_label.casefold()
    return any(label.casefold() == folded for label in labels)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="판정 흔들림 진단(v15 I2), 반복 판정 비교, 여러 판정의 중앙값·평균 합치기"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    cp = sub.add_parser("compare", help="기준 패스와 다섯 패스를 문항별로 비교하고 판정 방식을 고른다")
    cp.add_argument("--tag", required=True)
    cp.add_argument("--base", required=True, help="기준 패스(같은 순서 첫 번째)의 판정 라벨")
    cp.add_argument(
        "--passes",
        nargs=5,
        required=True,
        metavar=("A2", "R", "F1", "F2", "L"),
        help="A2 R F1 F2 L 순서의 판정 라벨 다섯 개",
    )
    cp.add_argument("--gen", type=Path, nargs="+", required=True, help="판정한 생성 기록(.gen.jsonl)")
    mp = sub.add_parser("median", help="판정 파일 여러 개를 문항별 중앙값으로 합친다")
    mp.add_argument("--labels", nargs="+", required=True, help="합칠 판정 라벨들(보통 3개)")
    mp.add_argument(
        "--out-label",
        required=True,
        help="합친 판정 파일의 라벨. 입력 라벨과 같으면 안 된다(대소문자만 달라도 안 됨, 덮어쓰기 방지)",
    )
    mp.add_argument("--gen", type=Path, nargs="+", required=True)
    rp = sub.add_parser(
        "repeats",
        help="같은 답을 같은 판정기로 여러 번 판정한 파일들이 서로 얼마나 다른지 센다",
        description=(
            "첫 라벨을 기준으로, 뒤 라벨마다 판정 원문이 다른 문항 수와 점수(정확도·충실도·환각)가 다른 "
            "문항 수, 그리고 기준의 점수가 문항별 중앙값과 다른 문항 수를 센다. 결과는 "
            "eval/runs/<tag>.repeats.json과 eval/reports/judge_repeats_<tag>_<시각>.md에 쓴다. 라벨들이 다른 "
            "문항이나 다른 답(answer_sha1)을 판정했으면 멈춘다."
        ),
    )
    rp.add_argument("--tag", required=True, help="결과 파일 이름에 붙일 이름. 예: v15_J1v15")
    rp.add_argument(
        "--labels",
        nargs="+",
        required=True,
        help="비교할 판정 라벨 둘 이상. 첫 라벨이 기준이다. 예: J1v15r1 J1v15r2 J1v15r3",
    )
    rp.add_argument(
        "--gen",
        type=Path,
        nargs="+",
        required=True,
        help="판정한 생성 기록(.gen.jsonl). 모든 라벨의 판정 파일이 기록마다 있어야 한다",
    )
    ap = sub.add_parser(
        "average",
        help="두 판정기의 판정 파일을 문항별 평균으로 합친다(0.5점 단위, 환각은 둘 중 하나라도)",
        description=(
            "생성 기록마다 두 라벨의 판정을 문항별로 합쳐 <gen>.<out-label>.judge.jsonl을 쓴다. "
            "정확도·충실도는 평균(반올림 없음), 환각은 한쪽이라도 표시하면 표시, 한쪽이라도 오류·빈 "
            "판정이면 빈 판정이다. eval/generator_arms.py summary와 eval/refusal.py가 "
            "--label <out-label>로 그대로 읽는다."
        ),
    )
    ap.add_argument(
        "--labels",
        nargs=2,
        required=True,
        metavar=("A", "B"),
        help="합칠 두 판정기의 판정 라벨. 예: J2v15 J3v15(v15 I5의 J2+J3 평균 구성)",
    )
    ap.add_argument(
        "--out-label",
        required=True,
        help="합친 판정 파일의 라벨. 입력 라벨과 같으면 안 된다(대소문자만 달라도 안 됨, 덮어쓰기 방지)",
    )
    ap.add_argument("--gen", type=Path, nargs="+", required=True, help="판정한 생성 기록(.gen.jsonl)")
    args = parser.parse_args()

    if args.command == "compare":
        names = ("A2", "R", "F1", "F2", "L")
        result = compare(args.tag, args.gen, args.base, dict(zip(names, args.passes, strict=True)))
        stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        write_json(Path("eval/runs") / f"{args.tag}.stability.json", result)
        path = write_report(f"judge_stability_{args.tag}_{stamp}.md", render(result))
        print(f"outcome ({result['outcome']}) -> {result['judge_method']}; report {path}")
        return 0

    if args.command == "repeats":
        if len(args.labels) < 2:
            parser.error("repeats needs at least two labels")
        result = {"tag": args.tag, "date": datetime.now(UTC).isoformat(), **repeats(args.gen, args.labels)}
        stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        write_json(RUNS_DIR / f"{args.tag}.repeats.json", result)
        path = write_report(f"judge_repeats_{args.tag}_{stamp}.md", render_repeats(result))
        print(
            f"{args.tag}: {result['n']} items; raw differs {result['any_raw_diff']}, scores differ "
            f"{result['any_score_diff']}, first != median {result['first_differs_from_median']}; "
            f"report {path}"
        )
        return 0

    if args.command == "average":
        if _out_label_overlaps(args.out_label, args.labels):
            parser.error("--out-label must differ from the input labels (ignoring case)")
        for gen in args.gen:
            per_label = [read_jsonl(judged_path(gen, label)) for label in args.labels]
            out = judged_path(gen, args.out_label)
            write_jsonl(out, average_judgments(per_label, args.out_label, where=gen.name))
            print(f"{gen.name}: {args.out_label} <- mean of {', '.join(args.labels)} -> {out}")
        return 0

    # median도 average처럼 출력 라벨이 입력 라벨 중 하나면 쓰기 전에 멈춘다. 같으면
    # <gen>.<out-label>.judge.jsonl이 입력 판정 파일 자체라 합친 결과가 그 파일을 덮어쓴다. 경계 규칙
    # (docs/experiments.md v15 절 끝 '규칙 변경 (v16부터): 판정 절차')에서 1회 판정 파일이 덮이면 결정의
    # 근거가 된 원래 판정이 사라지고, 되살리려면 판정을 다시 돌려야 한다. 판정 파일을 하나도 읽거나 쓰기
    # 전에 확인하므로 이 오류로 멈추면 아무 파일도 바뀌지 않는다. 대소문자만 다른 라벨도 같은 파일일 수 있어
    # 함께 막는다(_out_label_overlaps).
    if _out_label_overlaps(args.out_label, args.labels):
        parser.error("--out-label must differ from the input labels (ignoring case)")
    for gen in args.gen:
        per_label = [read_jsonl(judged_path(gen, label)) for label in args.labels]
        out = judged_path(gen, args.out_label)
        write_jsonl(out, median_judgments(per_label, args.out_label))
        print(f"{gen.name}: {args.out_label} <- {', '.join(args.labels)} -> {out}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(errors="backslashreplace")
    sys.exit(main())

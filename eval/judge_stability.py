"""판정 흔들림 진단(docs/experiments.md v15 I2)과 여러 번 판정의 중앙값 합치기.

사용법:
    # 같은 저장된 답을 여러 조건(패스)으로 판정한 뒤, 기준 패스와 문항별로 비교하고 규칙대로 판정 방식을
    # 고른다
    python -m eval.judge_stability compare --tag v15_i2 --base J1sA1 \
        --passes J1sA2 J1sR J1sF1 J1sF2 J1sL --gen eval/runs/v14_c3_qa_dev.lg.gen.jsonl ...

    # 같은 답에 대한 판정 파일 세 개를 문항별 중앙값으로 합쳐 새 라벨의 판정 파일을 쓴다
    python -m eval.judge_stability median --labels J1a J1b J1c --out-label J1m3 --gen <gen.jsonl> ...
"""

# [파일 역할] v15 I2 진단의 분석기. 저장된 dev 답 104개를 같은 J1 설정으로 여러 번(같은 순서 두 번, 역순,
# 문항마다 캐시 되돌리기 정순·역순, 모델 다시 올린 뒤) 판정한 파일들을 문항 단위로 비교해, 판정 흔들림의 원인
# 후보를 가르고 이후 비교에 쓸 판정 방식을 규칙대로 정한다.
# [왜 필요한가] v13에서 같은 답·같은 프롬프트·같은 순서인데도 J1 원문이 40문항 중 5개 달랐다. 원인이 '앞
# 문항이 남긴 프롬프트 캐시'인지, 같은 순서에서도 생기는 비결정성인지에 따라 처방이 다르다(캐시면 문항마다
# 캐시 되돌리기, 비결정성이면 여러 번 판정의 중앙값). 규칙은 측정 전에 docs/experiments.md v15에 적었고, 이
# 파일의 decide()가 그 규칙을 코드로 옮긴 것이다.
# [연결] 판정 파일은 eval/run_judge.py가 쓴다(<gen>.<라벨>.judge.jsonl). median이 쓴 파일은
# eval/generator_arms.py summary --label <out-label>로 그대로 읽힌다.

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path

from eval.common import read_jsonl, write_json, write_jsonl, write_report
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
        scores_b = (b.get("correctness_score"), b.get("faithfulness_score"), b.get("hallucinated"))
        scores_o = (o.get("correctness_score"), o.get("faithfulness_score"), o.get("hallucinated"))
        if scores_b != scores_o:
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


def main() -> int:
    parser = argparse.ArgumentParser(description="판정 흔들림 진단(v15 I2)과 여러 판정의 중앙값 합치기")
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
    mp.add_argument("--out-label", required=True, help="합친 판정 파일의 라벨")
    mp.add_argument("--gen", type=Path, nargs="+", required=True)
    args = parser.parse_args()

    if args.command == "compare":
        names = ("A2", "R", "F1", "F2", "L")
        result = compare(args.tag, args.gen, args.base, dict(zip(names, args.passes, strict=True)))
        stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        write_json(Path("eval/runs") / f"{args.tag}.stability.json", result)
        path = write_report(f"judge_stability_{args.tag}_{stamp}.md", render(result))
        print(f"outcome ({result['outcome']}) -> {result['judge_method']}; report {path}")
        return 0

    for gen in args.gen:
        per_label = [read_jsonl(judged_path(gen, label)) for label in args.labels]
        out = judged_path(gen, args.out_label)
        write_jsonl(out, median_judgments(per_label, args.out_label))
        print(f"{gen.name}: {args.out_label} <- {', '.join(args.labels)} -> {out}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(errors="backslashreplace")
    sys.exit(main())

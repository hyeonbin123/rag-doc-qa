"""답변 평가 한 번의 마크다운 리포트: 집계와 문항별 표.

eval/run_answer_eval.py(생성 + 판정)와 eval/run_judge.py(저장된 답을 판정)가 쓴다. 리포트에 보이는 내용은
모두 리포트가 이름을 적어 두는 문항별 JSONL 파일에 들어 있다.
"""

# [파일 역할] 답변 평가 한 번의 결과를 마크다운 리포트로 만든다: 실행 조건(모델, digest, 판정 설정, 검색 모드,
# 데이터셋), 집계표(키워드 커버리지·충실도·정확도·환각·생성 시간·한자/가나 섞임·판정 잘림), 문항별 표,
# 커버리지가 낮은 문항.
# [왜 따로 두나] 답을 만들고 판정하는 run_answer_eval.py와, 저장된 답을 다시 판정만 하는 run_judge.py가 같은
# 리포트 형식을 써야 두 결과를 나란히 비교할 수 있다. 리포트는 eval/reports/에, 원자료는 문항별
# JSONL(eval/runs/)에 있다.
# [연결] display_path는 compare_judgments.py, generator_arms.py도 쓴다.

from __future__ import annotations

import statistics
from datetime import UTC, datetime
from pathlib import Path

# 저장소 루트. 리포트에 파일 경로를 저장소 기준 상대 경로로 적는 데 쓴다.
PROJECT_ROOT = Path(__file__).resolve().parent.parent


# 경로를 저장소 기준 상대 경로(슬래시 구분)로 바꾼다. 리포트에 실행한 PC의 절대 경로가 남지 않고, OS가 달라도
# 같은 표기가 된다. 저장소 밖이면 절대 경로를, 없으면 '-'를 돌려준다.
def display_path(path: Path | str | None) -> str:
    if path is None:
        return "-"
    path = Path(path).resolve()
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


# 평균. 값이 없으면 0이 아니라 None(리포트에는 n/a)으로 둬 '0점'과 '판정 없음'을 구분한다.
def _avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


# 숫자를 형식에 맞춰 문자열로, None이면 n/a.
def _fmt(value: float | None, spec: str = ".2f") -> str:
    return "n/a" if value is None else format(value, spec)


# 집계표의 값을 계산한다. records는 생성 기록(문항별 답·커버리지·생성 시간·섞임), judgments는 판정 기록이다.
# - 충실도·정확도·환각은 점수가 있는(판정 오류가 아니고 검색 결과가 있었던) 문항만으로 낸다. scored가 그 수다.
# - 커버리지와 생성 시간 중앙값은 모든 문항으로 낸다.
# - truncated: 판정 프롬프트가 잘린 것으로 보이는 수(Ollama가 읽은 토큰 수가 토크나이저 수보다 적음,
#   eval/judge.py).
# - unchecked: 토크나이저가 없어 잘림을 확인하지 못했지만 판정은 된 수.
# - errors: 문맥 초과 등으로 판정하지 못한 수.
def summarize(records: list[dict], judgments: list[dict] | None) -> dict:
    by_id = {j["id"]: j for j in judgments or []}
    scored = [by_id[r["id"]] for r in records if by_id.get(r["id"], {}).get("correctness_score") is not None]
    return {
        "n": len(records),
        "coverage": _avg([r["keyword_coverage"] for r in records]),
        "faithfulness": _avg([j["faithfulness_score"] for j in scored]),
        "correctness": _avg([j["correctness_score"] for j in scored]),
        "correctness_sum": sum(j["correctness_score"] for j in scored) if scored else None,
        "scored": len(scored),
        "hallucinated": sum(1 for j in scored if j["hallucinated"]),
        "generation_p50": statistics.median(r["generation_ms"] for r in records),
        "kana_han": sum(1 for r in records if r["kana_han"]),
        "truncated": sum(1 for j in by_id.values() if j["truncation"] == "truncated"),
        "unchecked": sum(1 for j in by_id.values() if j["truncation"] == "unchecked" and j["raw"]),
        "errors": sum(1 for j in by_id.values() if j["error"]),
    }


# v13에서 생긴 실행 메모 줄들: 생성 모델 digest(정확히 어떤 모델 파일로 잰 것인지), think·언어 가드 설정과
# 가드가 다시 만든 문항 수, 그리고 문항별 호출 진단 집계. 진단이 없는 예전 기록이면 이 줄들은 생략된다.
# - done_reason=length: 최종 답변 호출이 출력 상한(1024토큰)에서 잘린 수.
# - reasoning output: 추론 출력이 나왔거나 답에 think 태그가 섞인 수.
# - 인용 응답이 스키마를 어긴 수.
def generation_notes(gen_meta: dict, records: list[dict]) -> list[str]:
    """v13에서 더한 실행 메모: 모델 digest, think·언어 가드 설정, 호출마다 멈춘 이유."""
    n = len(records)
    calls = [r.get("generation_calls") for r in records]
    lines = []
    if gen_meta.get("model_digest"):
        lines.append(f"- model digest: {gen_meta['model_digest']}")
    if "think" in gen_meta or "language_guard" in gen_meta:
        guard = "on" if gen_meta.get("language_guard") else "off"
        if gen_meta.get("language_guard"):
            guard += f" (regenerated {sum(1 for r in records if r.get('guard_applied'))}/{n})"
        lines.append(f"- think: {gen_meta.get('think')}, language guard: {guard}")
    if any(calls):
        cut = sum(1 for c in calls if c and c["answer"][-1].get("done_reason") == "length")
        thinking = sum(
            1
            for r, c in zip(records, calls, strict=True)
            if c
            and (
                r.get("think_tag_in_answer")
                or any(x.get("thinking_chars") for x in [*c["answer"], c["citation"]])
            )
        )
        bad = sum(1 for r in records if r.get("citation_schema_error"))
        lines.append(
            f"- final answer call stopped by the output limit, done_reason=length: {cut}/{n}; "
            f"reasoning output: {thinking}/{n}; citation replies breaking the schema: {bad}/{n}"
        )
    return lines


# 판정 설정 줄들. 판정을 건너뛰었으면 그렇게 적는다. num_ctx가 None이면 v10까지의 예전 호출(Ollama 기본 문맥,
# 넘치면 잘림)이고, 아니면 v11 호출(num_ctx 지정, truncate=false)이다. 판정 뒤 Ollama가 실제로 쓴 문맥 크기,
# 잘림 확인에 쓴 토크나이저, 판정 순서·날짜도 적는다. v11에서 판정 문맥 크기와 순서만 바꿔도 점수가
# 움직였으므로(docs/experiments.md v11) 이 조건들을 리포트마다 남긴다.
def judge_description(judge_meta: dict | None) -> list[str]:
    if judge_meta is None:
        return ["- judge: skipped"]
    num_ctx = judge_meta["num_ctx"]
    context = "Ollama default (num_ctx not sent, truncation on)" if num_ctx is None else (
        f"num_ctx {num_ctx}, truncate=false"
    )
    counter = judge_meta.get("tokenizer") or "none (truncation unchecked)"
    return [
        f"- judge: {judge_meta['label']}, {judge_meta['model']}, {context}",
        "- judge context in use (Ollama /api/ps after judging): "
        f"{judge_meta.get('context_in_use') or 'unknown'}",
        f"- judge prompt token counter: {counter}",
        f"- judge order: {judge_meta.get('order', 'dataset')}",
        f"- judge date: {judge_meta.get('date', '-')}",
    ]


# 리포트 본문을 만든다. 머리의 실행 조건 목록 → 집계표 → 문항별 표(판정 프롬프트의 토크나이저 수 / Ollama가
# 읽은 수, 잘림 상태) → 키워드 커버리지가 가장 낮은 5문항과 답 앞 200자 → 판정 오류 목록 순서다. 생성 순서가
# 섞기(shuffle)였으면 seed도 적어 재현할 수 있게 한다.
def render_report(
    tag: str,
    gen_meta: dict,
    records: list[dict],
    judgments: list[dict] | None,
    judge_meta: dict | None,
) -> str:
    s = summarize(records, judgments)
    by_id = {j["id"]: j for j in judgments or []}
    order = gen_meta.get("order", "dataset")
    if order == "shuffle":
        order = f"shuffle (seed {gen_meta.get('seed')})"
    lines = [
        f"# Answer eval report ({tag})",
        "",
        f"- date: {datetime.now(UTC).isoformat()}",
        f"- generated: {gen_meta.get('date', '-')}",
        f"- provider: {gen_meta.get('provider', '-')}",
        f"- model: {gen_meta.get('model', '-')}",
        *generation_notes(gen_meta, records),
        *judge_description(judge_meta),
        f"- ollama version: {gen_meta.get('ollama_version') or '-'} (generation)"
        + (f", {judge_meta.get('ollama_version') or '-'} (judge)" if judge_meta else ""),
        f"- top_k: {gen_meta.get('top_k', '-')}",
        f"- retrieval mode: {gen_meta.get('retrieval_mode', '-')}"
        + (
            " (Korean questions search the Korean and English chunks)"
            if gen_meta.get("cross_lingual")
            else ""
        ),
        f"- database: {gen_meta.get('database', '-')}, "
        f"embedding models: {gen_meta.get('embedding_models', '-')}",
        f"- dataset: {gen_meta.get('dataset', '-')}",
        f"- questions: {s['n']}",
        f"- generation order: {order}",
        "- generation time: both generation calls (answer + citations), this machine's GPU",
        f"- per-item records: {display_path(gen_meta.get('records_path'))}"
        + (f", {display_path(judge_meta.get('judgments_path'))}" if judge_meta else ""),
        "",
        "## Aggregate metrics",
        "",
        "| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum "
        "| Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated "
        "| Judge errors |",
        "|---|---|---|---|---|---|---|---|---|",
        f"| {_fmt(s['coverage'])} | {_fmt(s['faithfulness'])} | {_fmt(s['correctness'])} "
        f"| {_fmt(s['correctness_sum'], 'd')} | {s['hallucinated']}/{s['scored']} "
        f"| {s['generation_p50']:.0f} | {s['kana_han']}/{s['n']} "
        f"| {s['truncated']}/{s['scored'] + s['errors']}"
        + (f" ({s['unchecked']} unchecked)" if s["unchecked"] else "")
        + f" | {s['errors']} |",
        "",
        "## Per-question",
        "",
        "| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han "
        "| judge prompt tokens (counted / read) | truncation |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in records:
        j = by_id.get(r["id"], {})
        lines.append(
            f"| {r['id']} | {r['keyword_coverage']:.2f} | {j.get('faithfulness_score')} "
            f"| {j.get('correctness_score')} | {j.get('hallucinated')} | {r['generation_ms']:.0f} "
            f"| {r['kana_han']} | {j.get('prompt_tokens_counted')} / {j.get('prompt_eval_count')} "
            f"| {j.get('truncation', '-')} |"
        )
    lines += ["", "## Worst questions (lowest keyword coverage)", ""]
    for r in sorted(records, key=lambda r: r["keyword_coverage"])[:5]:
        lines.append(f"- **{r['id']}** ({r['keyword_coverage']:.2f}): {r['question']}")
        lines.append(f"  > {r['answer'][:200]}")
    errors = [j for j in by_id.values() if j["error"]]
    if errors:
        lines += ["", "## Judge errors", ""]
        lines += [f"- **{j['id']}**: {j['error']}" for j in errors]
    return "\n".join(lines)

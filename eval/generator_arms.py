"""Arms, gate and summaries for the generation-model comparison (docs/experiments.md v13).

Selection and adoption runs generate with the language guard on (LANGUAGE_GUARD=true).
eval/run_answer_eval.py then records the final answer and, when the guard regenerated,
the first answer too. One run therefore gives two arms:

- raw: the generator alone, i.e. the first answer call, which is what a run without the
  guard returns (same request; the guard's extra call comes after it)
- lg: the generator with the guard, i.e. the final answer

`split` writes them as <stem>.raw.gen.jsonl and <stem>.lg.gen.jsonl next to the run, so
eval/run_judge.py judges each like any other run. In the raw arm an item the guard
regenerated has no citations (the citation call saw the final answer) and its generation
time leaves out the retry.

`gate` checks a guard-off run of one candidate against the v13 smoke gate: the model fully
on the GPU, its pinned digest, no reasoning output, schema-valid citation replies on the
first 10 items, at most one answer cut by the output limit, and the generation p50.

`summary` lines up arms over the same items: J1 correctness, hallucination flags,
kana/han answers, generation p50, stop reasons, citation checks, guard counts, by
language, with paired bootstrap intervals against a baseline arm.

Usage:
    python -m eval.generator_arms split eval/runs/v13_sel_g0_qa_dev.gen.jsonl [...]
    python -m eval.generator_arms gate eval/runs/v13_gate_g1_qa_dev_ko.gen.jsonl --digest <sha256>
        [--max-p50-ms 10000] [--require-prompt-match MODEL] [--prompt-tolerance 1]
    python -m eval.generator_arms summary --tag v13_sel --label J1 --baseline G0
        --arm G0=eval/runs/v13_sel_g0_qa_dev.raw.gen.jsonl,eval/runs/v13_sel_g0_qa_dev_ko.raw.gen.jsonl
        --arm G1=... [--share G0+LG=G0]
"""

# [파일 역할] v13 생성 모델 교체 시험(docs/experiments.md v13)의 분석 도구. 세 하위 명령이 있다.
# - split: 언어 가드를 켜고 만든 생성 기록 하나를 raw 팔(가드 없이 생성기만, 첫 답)과 lg 팔(가드를 거친 최종
#   답) 두 파일로 나눈다. 한 번의 생성으로 '가드 없음'과 '가드 있음'을 같은 조건에서 비교하려는 것이다.
# - gate: 후보 모델의 관문(스모크) 검사. GPU에 다 올라갔는지, 고정한 digest인지, 추론 출력이 없는지, 처음
#   10문항의 인용 응답이 스키마대로인지, 출력 상한에서 잘린 답이 1개 이하인지, 생성 시간 중앙값이 한도 안인지.
# - summary: 여러 팔을 같은 문항에서 나란히 놓고 언어별로 J1 정확도 합, 환각, 한자·가나 섞임, 생성 시간, 인용
#   지표, 가드 횟수를 집계하고, 기준 팔과의 정확도 차이를 대응표본 bootstrap 구간으로 낸다.
# [왜 필요한가] v13의 관문·선택·채택 조건이 이 지표들로 미리 정해져 있었고, 같은 표를 기계적으로 만들어야
# 규칙대로 판정할 수 있다. 리포트는 eval/reports/generator_gate_*, generator_summary_*로 남는다.

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path

# 앱의 섞임 정규식(KANA_HAN_RE)과 페이지 키(page_key)를 그대로 써서 평가와 앱의 정의가 어긋나지 않게 한다.
# 판정 기록 경로·bootstrap·답 해시는 다른 평가 모듈과 공유한다.
from app.services.generation import KANA_HAN_RE
from app.services.retrieval import page_key
from eval.answer_report import display_path
from eval.common import (
    REPORTS_DIR,
    keyword_coverage,
    read_json,
    read_jsonl,
    write_json,
    write_jsonl,
    write_report,
)
from eval.compare_judgments import paired_bootstrap_ci
from eval.judge import answer_sha1
from eval.run_judge import judged_path, meta_path

# 관문 기준(docs/experiments.md v13 관문 4~6): 인용 스키마를 보는 처음 문항 수 10, 출력
# 상한(done_reason=length)에서 잘린 답 최대 1개, 생성 시간(두 호출 합) 중앙값 10초 이하.
GATE_FIRST_ITEMS = 10
GATE_MAX_LENGTH_STOPS = 1
GATE_MAX_P50_MS = 10_000.0
# 관문 7: Ollama가 읽은 프롬프트 토큰 수와 공식 템플릿으로 센 수의 허용 차이(±1). 어시스턴트 머리말이 빠진
# 템플릿은 2토큰 차이라 이 값이어야 잡힌다. 예전 기본값은 잘림 판정 허용치(16)라, 규칙대로 보려면
# --prompt-tolerance 1을 따로 줘야 했다(기록된 관문 실행은 1을 줬다).
PROMPT_MATCH_TOLERANCE = 1


# 문항 기록에서 답변 호출들의 진단 목록(첫 답, 가드가 걸렸으면 재시도). 진단이 없는 옛 기록이면 빈 목록.
def _calls(record: dict) -> list[dict]:
    return ((record.get("generation_calls") or {}).get("answer")) or []


# raw 팔 기록. 가드가 걸린 문항은 가드 전 답으로 되돌리고, 그 답 기준으로 키워드 커버리지·섞임을 다시
# 계산하며, 생성 시간에서 재시도 시간을 뺀다. 인용 호출은 최종 답을 보고 했으므로 이 문항의 인용은
# 없음(None)으로 둔다. 가드가 걸리지 않은 문항은 그대로다.
def unguarded_record(record: dict) -> dict:
    """The raw arm: what the generator returned before the guard looked at it."""
    out = dict(record)
    calls = _calls(record)
    if record.get("guard_applied"):
        answer = record["unguarded_answer"]
        out.update(
            answer=answer,
            cited_chunk_numbers=None,  # the citation call saw the final answer
            generation_ms=record["generation_ms"] - (record.get("guard_retry_ms") or 0.0),
            keyword_coverage=keyword_coverage(answer, record.get("must_include_keywords") or []),
            kana_han=bool(KANA_HAN_RE.search(answer)),
        )
    out["answer_done_reason"] = calls[0]["done_reason"] if calls else None
    out["arm"] = "raw"
    return out


# lg 팔 기록: 원래 기록(최종 답) 그대로에 팔 이름과 마지막 답변 호출의 끝난 이유만 더한다.
def guarded_record(record: dict) -> dict:
    """The lg arm: the final answer, as the app with the guard on would return it."""
    out = dict(record)
    calls = _calls(record)
    out["answer_done_reason"] = calls[-1]["done_reason"] if calls else None
    out["arm"] = "lg"
    return out


# <stem>.gen.jsonl → <stem>.<팔>.gen.jsonl 경로.
def _arm_path(gen_path: Path, arm: str) -> Path:
    stem = gen_path.name.removesuffix(".jsonl").removesuffix(".gen")
    return gen_path.with_name(f"{stem}.{arm}.gen.jsonl")


# 생성 기록 하나를 두 팔 파일(+ 각각의 .meta.json)로 쓴다. 가드를 끄고 만든 기록은 팔이 하나뿐이므로 거부한다.
# 나뉜 파일은 eval/run_judge.py로 다른 실행처럼 판정한다.
def split_file(gen_path: Path) -> tuple[Path, Path]:
    meta = read_json(meta_path(gen_path))
    if not meta.get("language_guard"):
        raise ValueError(f"{gen_path.name} was generated without the language guard; there is one arm only")
    records = read_jsonl(gen_path)
    paths = []
    for arm, derive in (("raw", unguarded_record), ("lg", guarded_record)):
        out = _arm_path(gen_path, arm)
        # The arm goes into the run tag, so the two arms' judge reports never share a name.
        write_jsonl(out, [{**derive(r), "run_tag": f"{r.get('run_tag')}.{arm}"} for r in records])
        write_json(meta_path(out), {**meta, "arm": arm, "derived_from": display_path(gen_path)})
        paths.append(out)
    return paths[0], paths[1]


# --- per-item metrics ------------------------------------------------------------------


# 추론 출력이 있었는지: 어느 호출에서든 thinking 글자가 나왔거나 답에 think 태그가 섞였으면 True. 관문 3은
# 모든 호출에서 추론 출력이 0이어야 한다(think를 끄도록 설정한 모델이 실제로 추론하지 않는지 확인).
def _thinking(record: dict) -> bool:
    calls = record.get("generation_calls") or {}
    every = [*(calls.get("answer") or []), *([calls["citation"]] if calls.get("citation") else [])]
    return bool(record.get("think_tag_in_answer")) or any((c.get("thinking_chars") or 0) > 0 for c in every)


# 문항 하나의 지표 행. 판정 점수, 섞임, 생성 시간, 출력 상한 잘림, 추론 출력, 인용 지표, 가드 정보, 답 해시를
# 모은다.
# - 인용 지표(인용이 있는 문항만): 스키마 오류 여부, 인용 번호가 모두 1~k 안인지, 인용한 문단 중 정답
#   페이지(번역 무관)가 있는지.
# - context_has_expected_page: 생성기에 넘어간 문단에 정답 페이지가 있었는지. 답이 틀렸을 때 검색 탓인지 생성
#   탓인지 가르는 데 쓴다.
def item_row(record: dict, judgment: dict | None) -> dict:
    j = judgment or {}
    cited = record.get("cited_chunk_numbers")
    chunks = record.get("chunks") or []
    expected = {page_key(p) for p in record.get("expected_source_paths") or []}
    in_range = cites_expected = None
    if cited is not None:
        in_range = bool(cited) and all(isinstance(n, int) and 1 <= n <= len(chunks) for n in cited)
        cites_expected = any(
            isinstance(n, int)
            and 1 <= n <= len(chunks)
            and page_key(chunks[n - 1]["source_path"]) in expected
            for n in cited
        )
    return {
        "dataset": record.get("dataset"),
        "id": record["id"],
        "language": record.get("language"),
        "arm": record.get("arm"),
        "correctness": j.get("correctness_score"),
        "faithfulness": j.get("faithfulness_score"),
        "hallucinated": j.get("hallucinated"),
        "judged": j.get("correctness_score") is not None,
        "kana_han": bool(record.get("kana_han")),
        "generation_ms": record.get("generation_ms"),
        "done_length": record.get("answer_done_reason") == "length",
        "thinking": _thinking(record),
        "citation_error": record.get("citation_schema_error") is not None if cited is not None else None,
        "citations_in_range": in_range,
        "cites_expected_page": cites_expected,
        # Retrieval's share: the generator saw a passage of an expected page (any translation).
        "context_has_expected_page": any(page_key(c["source_path"]) in expected for c in chunks),
        "guard_applied": bool(record.get("guard_applied")),
        "guard_retry_ms": record.get("guard_retry_ms"),
        "answer_sha1": answer_sha1(record.get("answer") or ""),
    }


# 참/전체 형태의 문자열. None(해당 없음)은 분모에서 뺀다.
def _ratio(values: list) -> str:
    known = [v for v in values if v is not None]
    return f"{sum(1 for v in known if v)}/{len(known)}"


# 행 묶음의 집계: 판정된 문항의 정확도·충실도 합과 환각 수, 섞인 답 수, 생성 시간 중앙값, 잘림·추론·인용 오류
# 수, 인용 비율들, 가드 횟수와 재시도 시간 중앙값. 평균이 아니라 합을 쓰는 것은 v13 조건이 합으로 정해져 있기
# 때문이다.
def _summary(rows: list[dict]) -> dict:
    judged = [r for r in rows if r["judged"]]
    times = [r["generation_ms"] for r in rows if r["generation_ms"] is not None]
    retries = [r["guard_retry_ms"] for r in rows if r.get("guard_retry_ms") is not None]
    return {
        "n": len(rows),
        "judged": len(judged),
        "correctness_sum": sum(r["correctness"] for r in judged),
        "faithfulness_sum": sum(r["faithfulness"] for r in judged),
        "hallucinated": sum(1 for r in judged if r["hallucinated"]),
        "kana_han": sum(1 for r in rows if r["kana_han"]),
        "generation_p50_ms": statistics.median(times) if times else None,
        "done_length": sum(1 for r in rows if r["done_length"]),
        "thinking": sum(1 for r in rows if r["thinking"]),
        "citation_errors": sum(1 for r in rows if r["citation_error"]),
        "citations_in_range": _ratio([r["citations_in_range"] for r in rows]),
        "cites_expected_page": _ratio([r["cites_expected_page"] for r in rows]),
        "context_expected_page": _ratio([r.get("context_has_expected_page") for r in rows]),
        "guard_applied": sum(1 for r in rows if r["guard_applied"]),
        "guard_retry_p50_ms": statistics.median(retries) if retries else None,
    }


# 전체, 영어, 한국어로 나눠 집계한다(v13 조건이 언어별 기준을 따로 둔다).
def summarize(rows: list[dict]) -> dict:
    return {
        "all": _summary(rows),
        "en": _summary([r for r in rows if r["language"] == "en"]),
        "ko": _summary([r for r in rows if r["language"] == "ko"]),
    }


# 한 팔에 속한 생성 파일들을 읽어, 같은 라벨(J1 등)의 판정 파일이 있으면 붙여 지표 행을 만든다. 셋 안의 원래
# 순서로 정렬한다.
def arm_rows(gen_paths: list[Path], label: str | None) -> list[dict]:
    rows = []
    for gen_path in gen_paths:
        judgments = {}
        if label:
            judged = judged_path(gen_path, label)
            if judged.exists():
                judgments = {j["id"]: j for j in read_jsonl(judged)}
        records = sorted(read_jsonl(gen_path), key=lambda r: r.get("dataset_index") or 0)
        rows += [item_row(r, judgments.get(r["id"])) for r in records]
    return rows


# --- the smoke gate --------------------------------------------------------------------


# 생성이 끝난 뒤 기록해 둔 Ollama /api/ps에서 이 실행의 모델 항목을 찾는다.
def _loaded(meta: dict) -> dict | None:
    for m in (meta.get("ollama_ps_after") or {}).get("models", []):
        if m.get("name") == meta.get("model") or m.get("model") == meta.get("model"):
            return m
    return None


# 생성 기록 하나(가드 끔)에 관문 검사를 한다. 각 검사는 통과 여부(ok)와 실제 값(value)을 함께 남긴다.
# - full_gpu: size_vram == size(모델 전체가 GPU에 있음)이고 문맥이 8192. 일부가 CPU로 넘치면 생성이 크게
#   느려진다.
# - digest: 미리 고정한 모델 digest와 같은지(다른 파일로 잰 결과가 섞이지 않게).
# - no_thinking, citations_first_10, done_length, p50: 위 기준값.
# - prompt_match(지정한 모델만): Ollama가 읽은 프롬프트 토큰 수와 공식 채팅 템플릿으로 센 수의 차이. 직접
#   변환한 A.X 모델의 템플릿이 공식 템플릿과 같은지 보는 관문 7이다.
# 허용치 기본값은 관문 7 규칙의 ±1(PROMPT_MATCH_TOLERANCE)이다. 기록된 관문 실행에서는 32문항 모두 차이가
# 없었다(docs/experiments.md v13 관문 결과).
def gate(
    gen_path: Path,
    *,
    digest: str | None,
    max_p50_ms: float = GATE_MAX_P50_MS,
    require_prompt_match: bool = False,
    prompt_tolerance: int = PROMPT_MATCH_TOLERANCE,
) -> dict:
    meta = read_json(meta_path(gen_path))
    records = sorted(read_jsonl(gen_path), key=lambda r: r.get("dataset_index") or 0)
    rows = [item_row(guarded_record(r), None) for r in records]
    loaded = _loaded(meta)
    first = rows[:GATE_FIRST_ITEMS]
    p50 = statistics.median(r["generation_ms"] for r in rows)
    diffs = [
        _calls(r)[0]["prompt_eval_count"] - r["generation_prompt_tokens_counted"]
        for r in records
        if _calls(r)
        and r.get("generation_prompt_tokens_counted") is not None
        and _calls(r)[0].get("prompt_eval_count") is not None
    ]
    checks = {
        "full_gpu": {
            "ok": bool(loaded)
            and loaded.get("size_vram") == loaded.get("size")
            and loaded.get("context_length") in (None, 8192),
            "value": {k: (loaded or {}).get(k) for k in ("size", "size_vram", "context_length")},
        },
        "digest": {
            "ok": digest is None or meta.get("model_digest") == digest,
            "value": meta.get("model_digest"),
        },
        "no_thinking": {
            "ok": not any(r["thinking"] for r in rows),
            "value": sum(r["thinking"] for r in rows),
        },
        "citations_first_10": {
            "ok": len(first) == GATE_FIRST_ITEMS and not any(r["citation_error"] for r in first),
            "value": f"{sum(1 for r in first if not r['citation_error'])}/{len(first)} valid "
            f"({sum(1 for r in rows if r['citation_error'])} invalid in all {len(rows)})",
        },
        "done_length": {
            "ok": sum(r["done_length"] for r in rows) <= GATE_MAX_LENGTH_STOPS,
            "value": sum(r["done_length"] for r in rows),
        },
        "p50": {"ok": p50 <= max_p50_ms, "value": round(p50, 1)},
    }
    prompt_count = {
        "items": len(diffs),
        "max_abs_diff": max((abs(d) for d in diffs), default=None),
        "median_diff": statistics.median(diffs) if diffs else None,
    }
    if require_prompt_match:
        checks["prompt_match"] = {
            "ok": len(diffs) == len(records) and all(abs(d) <= prompt_tolerance for d in diffs),
            "value": prompt_count,
        }
    return {
        "run": display_path(gen_path),
        "model": meta.get("model"),
        "think": meta.get("think"),
        "language_guard": meta.get("language_guard"),
        "questions": len(rows),
        "passed": all(c["ok"] for c in checks.values()),
        "checks": checks,
        "prompt_count": prompt_count,
    }


# --- reports ---------------------------------------------------------------------------


# 기준 팔과 다른 팔의 같은 문항(셋, id)끼리 정확도 차이를 모아 '차이 합 (평균 [bootstrap 90% 구간])'으로 쓴다.
# 양쪽 다 판정된 문항만 쓰고, language를 주면 그 언어만 본다.
def _ci_cell(base: list[dict], other: list[dict], language: str | None) -> str:
    by_key = {(r["dataset"], r["id"]): r for r in other}
    diffs = []
    for r in base:
        o = by_key.get((r["dataset"], r["id"]))
        if o and r["judged"] and o["judged"] and (language is None or r["language"] == language):
            diffs.append(o["correctness"] - r["correctness"])
    if not diffs:
        return "n/a"
    mean, low, high = paired_bootstrap_ci(diffs)
    return f"{sum(diffs):+d} ({mean:+.3f} [{low:+.3f}, {high:+.3f}])"


# 두 팔에서 답 글이 다른 문항 수(답 해시 비교).
def _answers_differ(base: list[dict], other: list[dict]) -> int:
    by_key = {(r["dataset"], r["id"]): r["answer_sha1"] for r in other}
    return sum(1 for r in base if by_key.get((r["dataset"], r["id"])) != r["answer_sha1"])


# 판정 공유 때 옮기는 판정 필드들.
JUDGMENT_FIELDS = ("correctness", "faithfulness", "hallucinated", "judged")


# 가드가 걸리지 않은 문항은 lg 팔의 답이 raw 팔과 같은 글이므로 raw 팔의 판정을 그대로 쓴다. 같은 답이라도
# 판정 순서의 다른 자리에 놓이면 J1 점수가 1점 달라질 수 있어서, 그 판정 노이즈가 가드 효과로 잘못 잡히지 않게
# 하려는 규칙 변경(docstring)이다. lg 팔 자신의 판정이 달랐던 문항 수는 보고용으로 센다.
def share_unguarded_judgments(lg_rows: list[dict], raw_rows: list[dict], raw_name: str) -> dict:
    """Give the lg arm the raw arm's judgment wherever the guard did not fire.

    Those answers are the same text in both arms, yet J1 can score the same answer a point
    apart when it sits at another place in the judge order (docs/experiments.md v13, rule
    change 2026-10-05). Sharing keeps that noise out of the guard's effect; the lg arm's own
    differing judgments are only counted.
    """
    by_key = {(r["dataset"], r["id"]): r for r in raw_rows}
    shared = differs = 0
    for row in lg_rows:
        raw = by_key.get((row["dataset"], row["id"]))
        if raw is None or row["guard_applied"]:
            continue
        if any(row[f] != raw[f] for f in JUDGMENT_FIELDS):
            differs += 1
        row.update({f: raw[f] for f in JUDGMENT_FIELDS})
        shared += 1
    return {"from": raw_name, "items": shared, "own_judgment_differs": differs}


# summary 리포트: 팔마다 언어별(en, ko, 전체) 집계 줄, 판정 공유 메모, 기준 팔이 있으면 정확도 차이 표.
# 마크다운과 함께 같은 내용(문항별 행 포함)을 JSON 데이터로도 돌려준다.
def summary_report(
    tag: str,
    label: str,
    arms: dict[str, list[Path]],
    baseline: str | None,
    shares: dict[str, str] | None = None,
) -> tuple[str, dict]:
    rows = {name: arm_rows(paths, label) for name, paths in arms.items()}
    data = {"tag": tag, "label": label, "baseline": baseline, "arms": {}}
    shared_notes = {}
    for lg_name, raw_name in (shares or {}).items():
        shared_notes[lg_name] = share_unguarded_judgments(rows[lg_name], rows[raw_name], raw_name)
    lines = [
        f"# Generator comparison ({tag}, judge {label})",
        "",
        f"- date: {datetime.now(UTC).isoformat()}",
        *[f"- {name}: {', '.join(display_path(p) for p in paths)}" for name, paths in arms.items()],
        "- correctness/faithfulness: J1 sums over judged items; kana/han: answers with kana or Han anywhere",
        "- citations: replies that break the schema; cited numbers within 1..k; a cited passage on an "
        "expected page (raw-arm items the guard regenerated have no citations of their own and are left out)",
        "- passages hold an expected page: answers written from passages that include a page the item "
        "expects (any translation), i.e. retrieval's share",
        *[
            f"- {lg}: items the guard left alone take {n['from']}'s judgment ({n['items']} items; "
            f"its own judgment differed on {n['own_judgment_differs']})"
            for lg, n in shared_notes.items()
        ],
        "",
        "| arm | lang | n | correctness sum | hallucinated | kana/han | faithfulness sum | gen p50 ms "
        "| done=length | thinking | citation errors | cites in range | cites expected page "
        "| passages hold an expected page | guard applied | guard retry p50 ms |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name, arm in rows.items():
        s = summarize(arm)
        data["arms"][name] = {"summary": s, "files": [display_path(p) for p in arms[name]], "rows": arm}
        if name in shared_notes:
            data["arms"][name]["shared"] = shared_notes[name]
        for lang in ("en", "ko", "all"):
            x = s[lang]
            if not x["n"]:
                continue
            p50 = "n/a" if x["generation_p50_ms"] is None else f"{x['generation_p50_ms']:.0f}"
            retry = "-" if x["guard_retry_p50_ms"] is None else f"{x['guard_retry_p50_ms']:.0f}"
            lines.append(
                f"| {name} | {lang} | {x['n']} | {x['correctness_sum']} ({x['judged']} judged) "
                f"| {x['hallucinated']} | {x['kana_han']} | {x['faithfulness_sum']} | {p50} "
                f"| {x['done_length']} | {x['thinking']} "
                f"| {x['citation_errors']} | {x['citations_in_range']} | {x['cites_expected_page']} "
                f"| {x['context_expected_page']} | {x['guard_applied']} | {retry} |"
            )
    if baseline:
        lines += [
            "",
            f"## Correctness against {baseline} (sum of per-item differences, mean [paired bootstrap 90%])",
            "",
            "| arm | en | ko | all | answers differ |",
            "|---|---|---|---|---|",
        ]
        base = rows[baseline]
        for name, arm in rows.items():
            if name == baseline:
                continue
            cells = [_ci_cell(base, arm, lang) for lang in ("en", "ko", None)]
            lines.append(f"| {name} | {' | '.join(cells)} | {_answers_differ(base, arm)} |")
            data["arms"][name]["vs_baseline"] = dict(zip(("en", "ko", "all"), cells, strict=True))
    return "\n".join(lines), data


# gate 리포트: 실행마다 한 줄, 검사마다 ok/FAIL과 값, 프롬프트 토큰 수 차이 요약.
def gate_report(results: list[dict]) -> str:
    # Runs can have different checks (only the A.X run checks its prompt counts), so the
    # columns are every check any run has; a run without one gets "-" there.
    names = list(dict.fromkeys(name for r in results for name in r["checks"]))
    lines = [
        "# Generation smoke gate (docs/experiments.md v13)",
        "",
        f"- date: {datetime.now(UTC).isoformat()}",
        f"- first {GATE_FIRST_ITEMS} citation replies schema-valid, "
        f"done_reason=length <= {GATE_MAX_LENGTH_STOPS}, no reasoning output, "
        "model fully on the GPU (size_vram == size), pinned digest, p50 limit",
        "",
        "| run | model | think | passed | " + " | ".join(names) + " | prompt count Ollama - tokenizer |",
        "|---|---|---|---|" + "---|" * len(names) + "---|",
    ]
    for r in results:
        cells = [
            f"{'ok' if r['checks'][name]['ok'] else 'FAIL'}: {r['checks'][name]['value']}"
            if name in r["checks"]
            else "-"
            for name in names
        ]
        pc = r["prompt_count"]
        lines.append(
            f"| {r['run']} | {r['model']} | {r['think']} | {r['passed']} | {' | '.join(cells)} "
            f"| {pc['items']} items, median {pc['median_diff']}, max abs {pc['max_abs_diff']} |"
        )
    return "\n".join(lines)


# 리포트를 시각을 붙인 이름의 마크다운(.md)과 데이터(.json)로 eval/reports/에 함께 쓴다. JSON이 있으면 표를
# 고쳐야 할 때 같은 실행으로 리포트를 다시 만들 수 있다.
def _write(name: str, report: str, data: dict | list) -> Path:
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path = write_report(f"{name}_{timestamp}.md", report)
    (REPORTS_DIR / f"{name}_{timestamp}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    return path


# 명령줄 진입점. gate의 --digest는 '모델=sha256'을 모델마다, summary의 --arm은 '이름=파일1,파일2', --share는
# 'lg팔=raw팔' 형식이다. gate는 하나라도 통과하지 못하면 종료 코드 1을 돌려줘, 셸에서 실패로 감지할 수 있다.
def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sp = sub.add_parser("split")
    sp.add_argument("paths", type=Path, nargs="+")
    gp = sub.add_parser("gate")
    gp.add_argument("paths", type=Path, nargs="+")
    gp.add_argument("--tag", required=True)
    gp.add_argument("--digest", action="append", default=[], help="model=sha256, one per model")
    gp.add_argument("--max-p50-ms", type=float, default=GATE_MAX_P50_MS)
    gp.add_argument(
        "--require-prompt-match", action="append", default=[], help="model whose counts must agree"
    )
    gp.add_argument(
        "--prompt-tolerance",
        type=int,
        default=PROMPT_MATCH_TOLERANCE,
        help="allowed |Ollama - tokenizer| tokens (gate 7 rule: 1)",
    )
    su = sub.add_parser("summary")
    su.add_argument("--tag", required=True)
    su.add_argument("--label", default="J1")
    su.add_argument("--baseline", default=None)
    su.add_argument("--arm", action="append", required=True, help="NAME=gen1,gen2,...")
    su.add_argument(
        "--share",
        action="append",
        default=[],
        help="LG=RAW: the LG arm takes RAW's judgment where the guard did not fire",
    )
    args = parser.parse_args()
    sys.stdout.reconfigure(errors="backslashreplace")  # see eval/run_answer_eval.py

    if args.command == "split":
        for path in args.paths:
            raw, lg = split_file(path)
            print(f"{path.name} -> {raw.name}, {lg.name}")
        return 0
    if args.command == "gate":
        digests = dict(d.split("=", 1) for d in args.digest)
        results = []
        for path in args.paths:
            model = read_json(meta_path(path)).get("model")
            results.append(
                gate(
                    path,
                    digest=digests.get(model),
                    max_p50_ms=args.max_p50_ms,
                    require_prompt_match=model in args.require_prompt_match,
                    prompt_tolerance=args.prompt_tolerance,
                )
            )
        report = gate_report(results)
        path = _write(f"generator_gate_{args.tag}", report, results)
        print(report)
        print(f"\nwritten to {path}")
        return 0 if all(r["passed"] for r in results) else 1
    arms = {}
    for spec in args.arm:
        name, files = spec.split("=", 1)
        arms[name] = [Path(f) for f in files.split(",") if f]
    shares = dict(spec.split("=", 1) for spec in args.share)
    report, data = summary_report(args.tag, args.label, arms, args.baseline, shares)
    path = _write(f"generator_summary_{args.tag}", report, data)
    print(report)
    print(f"\nwritten to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

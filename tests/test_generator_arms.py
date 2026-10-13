"""The v13 generation-model comparison: guard arms, per-item metrics, the gate, summaries.

docs/experiments.md v13 runs every selection and adoption generation with the language
guard on and records the first (unguarded) answer next to the final one, so one run gives
two arms: the generator alone ("raw", what a run without the guard returns) and the
generator with the guard ("lg"). These tests pin how the two arms are derived and counted.
No Ollama or database is needed.
"""

# [테스트 묶음] v13 생성 모델 비교 도구(eval/generator_arms.py)의 단위 테스트: 한 번의 생성 기록을 raw/lg 두
# 팔로 나누기, 문항별 지표, 관문(gate) 조건, 요약 표와 판정 공유.
# [왜 중요한가] v13은 모든 선택·채택 생성을 언어 가드를 켠 채 한 번만 하고, 첫 답(가드 전)과 최종 답을 함께
# 기록해 '생성기 단독'(raw)과 '생성기 + 가드'(lg) 두 조건을 얻는다(docs/experiments.md v13 '한 번의 생성으로
# 두 팔'). 팔을 잘못 나누면 채택 결정의 숫자가 틀어지므로 나누는 규칙을 하나하나 고정한다.
# [방법] Ollama·DB 없이, 가짜 생성 기록(gen)과 판정 기록을 tmp_path에 JSONL로 써서 검사한다.

import json
import uuid

# pytest: 근사 비교, 예외 검사, parametrize.
import pytest

# 테스트 대상 모듈과 기록 파일 입출력 도우미.
from eval import generator_arms
from eval.common import read_json, read_jsonl, write_json, write_jsonl


# 호출별 진단 목록을 만든다. done_reason을 여러 개 주면 그만큼의 답변 호출(첫 답, 가드 재시도)이 생긴다.
def calls(*done_reasons, thinking=0, eval_count=50, prompt=1500):
    return [
        {
            "prompt_eval_count": prompt,
            "eval_count": eval_count,
            "done_reason": d,
            "thinking_chars": thinking,
            "ms": 900.0,
        }
        for d in done_reasons
    ]


# run_answer_eval의 gen.jsonl 한 행과 같은 모양의 가짜 기록. 기본은 가드가 걸리지 않은 한국어 문항이고, 1번
# 패시지가 정답 페이지(docs/ko/docs/p1.md)라 인용·정답 페이지 지표가 맞게 나온다. extra로 필드를 덮어쓴다.
def gen(item_id, answer="답입니다.", language="ko", dataset="qa_dev_ko.jsonl", **extra):
    record = {
        "id": item_id,
        "dataset": dataset,
        "dataset_index": int(item_id[1:]),
        "run_tag": "unit",
        "question": "질문?" if language == "ko" else "Question?",
        "language": language,
        "reference_answer": "Ref.",
        "expected_source_paths": ["docs/ko/docs/p1.md"],
        "must_include_keywords": ["Query"],
        "chunks": [
            {
                "rank": n,
                "chunk_id": str(uuid.uuid4()),
                "source_path": f"docs/{language}/docs/p{n}.md",
                "content": "c",
            }
            for n in (1, 2, 3)
        ],
        "answer": answer,
        "cited_chunk_numbers": [1],
        "generation_ms": 3000.0,
        "keyword_coverage": 0.0,
        "kana_han": False,
        "guard_applied": False,
        "generation_calls": {"answer": calls("stop"), "citation": calls("stop")[0]},
        "citation_schema_error": None,
        "think_tag_in_answer": False,
    }
    record.update(extra)
    return record


# 가드가 걸린 문항의 필드: 첫 답에 중국어가 섞였고(length로 끝남), 재시도한 최종 답은 깨끗하다. 재시도 시간
# 1200ms를 포함한 전체 생성 시간은 4200ms.
GUARDED = dict(
    answer="`Query` 답입니다.",
    guard_applied=True,
    unguarded_answer="답입니다. 中文으로 다시",
    guard_retry_ms=1200.0,
    generation_ms=4200.0,
    kana_han=False,
    keyword_coverage=1.0,
    generation_calls={"answer": calls("length", "stop"), "citation": calls("stop")[0]},
)


# raw 팔은 첫 답변 호출이다: 답·섞임·키워드 커버리지를 첫 답으로 다시 계산하고, 생성 시간에서 재시도 시간을
# 빼며(4200 − 1200), done_reason은 첫 호출의 것이다. 인용 호출은 최종 답을 보고 했으므로 raw 팔의 인용은
# None(알 수 없음)이다.
def test_the_raw_arm_is_the_first_answer_call():
    raw = generator_arms.unguarded_record(gen("k1", **GUARDED))

    assert raw["arm"] == "raw"
    assert raw["answer"] == "답입니다. 中文으로 다시"
    assert raw["kana_han"] is True
    assert raw["keyword_coverage"] == 0.0
    assert raw["generation_ms"] == pytest.approx(3000.0)  # the retry is not part of this arm
    assert raw["answer_done_reason"] == "length"
    assert raw["cited_chunk_numbers"] is None  # the citation call saw the final answer


# lg 팔은 최종 답 그대로이고 done_reason은 마지막 답변 호출의 것이다. 가드가 걸리지 않은 문항은 두 팔의 답과
# 인용이 같다.
def test_the_lg_arm_is_the_final_answer_and_unguarded_items_are_shared():
    lg = generator_arms.guarded_record(gen("k1", **GUARDED))
    plain = gen("k2")

    assert lg["arm"] == "lg"
    assert lg["answer"] == "`Query` 답입니다."
    assert lg["answer_done_reason"] == "stop"
    assert lg["generation_ms"] == 4200.0
    raw2, lg2 = generator_arms.unguarded_record(plain), generator_arms.guarded_record(plain)
    assert raw2["answer"] == lg2["answer"] == plain["answer"]
    assert raw2["cited_chunk_numbers"] == lg2["cited_chunk_numbers"] == [1]


# split_file이 <tag>.raw.gen.jsonl과 <tag>.lg.gen.jsonl을 만들고, 팔 이름을 run_tag에 붙이며(두 팔의 판정
# 리포트 이름이 겹치지 않게), 각 meta에 팔 이름과 원본 파일을 남기는지 확인한다.
def test_split_writes_both_arm_files_with_their_run_notes(tmp_path):
    gen_path = tmp_path / "v13_unit_g0_qa_dev_ko.gen.jsonl"
    write_jsonl(gen_path, [gen("k1", **GUARDED), gen("k2")])
    write_json(tmp_path / "v13_unit_g0_qa_dev_ko.gen.meta.json", {"model": "m", "language_guard": True})

    raw_path, lg_path = generator_arms.split_file(gen_path)

    assert raw_path.name == "v13_unit_g0_qa_dev_ko.raw.gen.jsonl"
    assert lg_path.name == "v13_unit_g0_qa_dev_ko.lg.gen.jsonl"
    assert [r["answer"] for r in read_jsonl(raw_path)] == ["답입니다. 中文으로 다시", "답입니다."]
    # The arm is part of the run tag, so the two arms' judge reports never share a name.
    assert {r["run_tag"] for r in read_jsonl(raw_path)} == {"unit.raw"}
    assert {r["run_tag"] for r in read_jsonl(lg_path)} == {"unit.lg"}
    assert read_json(tmp_path / "v13_unit_g0_qa_dev_ko.raw.gen.meta.json")["arm"] == "raw"
    lg_meta = read_json(tmp_path / "v13_unit_g0_qa_dev_ko.lg.gen.meta.json")
    assert lg_meta["arm"] == "lg" and lg_meta["derived_from"].endswith("v13_unit_g0_qa_dev_ko.gen.jsonl")


# 가드를 끄고 만든 실행은 팔이 하나뿐이므로 나누기를 거부해야 한다(가드 전 답이 기록되지 않았기 때문).
def test_split_refuses_a_run_made_without_the_guard(tmp_path):
    gen_path = tmp_path / "x.gen.jsonl"
    write_jsonl(gen_path, [gen("k1")])
    write_json(tmp_path / "x.gen.meta.json", {"language_guard": False})

    with pytest.raises(ValueError, match="guard"):
        generator_arms.split_file(gen_path)


# 문항 행의 인용 검사: 번호가 1~패시지 수 안인지, 정답 페이지 청크를 인용했는지. 범위를 벗어난 번호(7)가
# 있으면 둘 다 False, raw 팔처럼 인용을 모르면 None이다. 판정 점수도 행에 옮겨지는지 본다.
def test_item_row_checks_citations_against_the_passages():
    judgment = {"id": "k1", "correctness_score": 4, "faithfulness_score": 3, "hallucinated": False}

    ok = generator_arms.item_row(generator_arms.guarded_record(gen("k1")), judgment)
    out_of_range = generator_arms.item_row(
        generator_arms.guarded_record(gen("k1", cited_chunk_numbers=[2, 7])), judgment
    )
    unknown = generator_arms.item_row(generator_arms.unguarded_record(gen("k1", **GUARDED)), judgment)

    assert ok["citations_in_range"] is True and ok["cites_expected_page"] is True
    assert out_of_range["citations_in_range"] is False and out_of_range["cites_expected_page"] is False
    assert unknown["citations_in_range"] is None and unknown["cites_expected_page"] is None
    assert unknown["done_length"] is True and unknown["kana_han"] is True
    assert ok["correctness"] == 4 and ok["hallucinated"] is False


# summarize가 전체·영어·한국어별로 정확도 합, 환각·섞임 수, 생성 시간 중앙값, length·추론 출력·인용 오류 수,
# 인용 비율('맞음/알 수 있는 문항'), 가드 적용 수를 세는지 확인한다. 인용을 모르는 문항(None)은 비율의
# 분모에서 빠진다.
def test_summary_counts_by_language():
    rows = [
        {
            "language": "en",
            "correctness": 5,
            "faithfulness": 4,
            "hallucinated": False,
            "kana_han": False,
            "generation_ms": 2000.0,
            "done_length": False,
            "thinking": False,
            "citation_error": False,
            "citations_in_range": True,
            "cites_expected_page": True,
            "guard_applied": False,
            "judged": True,
        },
        {
            "language": "ko",
            "correctness": 3,
            "faithfulness": 3,
            "hallucinated": True,
            "kana_han": True,
            "generation_ms": 4000.0,
            "done_length": True,
            "thinking": False,
            "citation_error": True,
            "citations_in_range": None,
            "cites_expected_page": None,
            "guard_applied": True,
            "judged": True,
        },
        {
            "language": "ko",
            "correctness": 4,
            "faithfulness": 4,
            "hallucinated": False,
            "kana_han": False,
            "generation_ms": 3000.0,
            "done_length": False,
            "thinking": True,
            "citation_error": False,
            "citations_in_range": True,
            "cites_expected_page": False,
            "guard_applied": False,
            "judged": True,
        },
    ]

    s = generator_arms.summarize(rows)

    assert (
        s["all"]["correctness_sum"] == 12
        and s["en"]["correctness_sum"] == 5
        and s["ko"]["correctness_sum"] == 7
    )
    assert s["all"]["hallucinated"] == 1 and s["ko"]["kana_han"] == 1
    assert s["all"]["generation_p50_ms"] == 3000.0
    assert s["all"]["done_length"] == 1 and s["all"]["thinking"] == 1 and s["all"]["citation_errors"] == 1
    assert s["all"]["citations_in_range"] == "2/2" and s["all"]["cites_expected_page"] == "1/2"
    assert s["ko"]["guard_applied"] == 1


# 관문 테스트용 생성 기록과 meta를 tmp_path에 쓰고 gen.jsonl 경로를 돌려준다.
def write_gate_run(tmp_path, records, meta):
    gen_path = tmp_path / "v13_gate_x_qa_dev_ko.gen.jsonl"
    write_jsonl(gen_path, records)
    write_json(tmp_path / "v13_gate_x_qa_dev_ko.gen.meta.json", meta)
    return gen_path


# 모든 관문을 통과하는 meta: digest 일치, 가드 꺼짐, 실행 뒤 /api/ps에서 size == size_vram(모델이 GPU에 다
# 올라감)이고 문맥 8192.
GATE_META = {
    "model": "m:tag",
    "model_digest": "abc123",
    "language_guard": False,
    "ollama_ps_after": {"models": [{"name": "m:tag", "size": 100, "size_vram": 100, "context_length": 8192}]},
}


# 깨끗한 실행(12문항, 프롬프트 토큰 수가 Ollama와 같음)은 관문을 통과한다. 처음 10문항 인용 조건 때문에 문항을
# 10개보다 많이 만든다.
def test_gate_passes_a_clean_run(tmp_path):
    records = [gen(f"k{i}", generation_prompt_tokens_counted=1500) for i in range(1, 13)]
    result = generator_arms.gate(write_gate_run(tmp_path, records, GATE_META), digest="abc123")

    assert result["passed"] is True
    assert result["checks"]["full_gpu"]["ok"] and result["checks"]["digest"]["ok"]
    assert result["prompt_count"]["max_abs_diff"] == 0


# 관문 조건을 하나씩만 어긴 실행이 정확히 그 조건 하나로만 떨어지는지 확인한다: 일부가 CPU에 올라감(size_vram
# < size), digest 불일치, 추론 출력(thinking 글자 수나 답 안의 <think>), 처음 10문항 중 인용 스키마 오류,
# length로 끝난 답 2개(한도 1개), 생성 시간 중앙값 10초 초과(docs/experiments.md v13 관문 1~6).
@pytest.mark.parametrize(
    ("change", "failed"),
    [
        (
            {"meta": {"ollama_ps_after": {"models": [{"name": "m:tag", "size": 100, "size_vram": 88}]}}},
            "full_gpu",
        ),
        ({"meta": {"model_digest": "zzz"}}, "digest"),
        (
            {
                "record": {
                    "generation_calls": {"answer": calls("stop", thinking=12), "citation": calls("stop")[0]}
                }
            },
            "no_thinking",
        ),
        ({"record": {"think_tag_in_answer": True}}, "no_thinking"),
        ({"record": {"citation_schema_error": "not JSON"}}, "citations_first_10"),
        ({"records_length": 2}, "done_length"),
        ({"record": {"generation_ms": 12000.0}, "all": True}, "p50"),
    ],
)
def test_gate_fails_each_condition(tmp_path, change, failed):
    records = [gen(f"k{i}") for i in range(1, 13)]
    if "record" in change:
        targets = records if change.get("all") else records[:1]
        for r in targets:
            r.update(change["record"])
    for r in records[: change.get("records_length", 0)]:
        r["generation_calls"] = {"answer": calls("length"), "citation": calls("stop")[0]}
    meta = {**GATE_META, **change.get("meta", {})}

    result = generator_arms.gate(write_gate_run(tmp_path, records, meta), digest="abc123")

    assert result["passed"] is False
    assert result["checks"][failed]["ok"] is False
    assert [name for name, c in result["checks"].items() if not c["ok"]] == [failed]


# 관문 7(A.X 전용): Ollama가 읽은 프롬프트 토큰 수와 토크나이저 수가 다르면, 요구하지 않을 때는 차이만
# 보고하고 요구할 때(require_prompt_match)는 떨어진다.
def test_gate_can_require_ollama_and_tokenizer_prompt_counts_to_agree(tmp_path):
    records = [gen(f"k{i}", generation_prompt_tokens_counted=1500) for i in range(1, 13)]
    records[3]["generation_prompt_tokens_counted"] = 1460  # Ollama read 1500: 40 more than the template gives

    loose = generator_arms.gate(write_gate_run(tmp_path, records, GATE_META), digest="abc123")
    strict = generator_arms.gate(
        write_gate_run(tmp_path, records, GATE_META), digest="abc123", require_prompt_match=True
    )

    assert loose["passed"] is True and loose["prompt_count"]["max_abs_diff"] == 40
    assert strict["passed"] is False and strict["checks"]["prompt_match"]["ok"] is False


# 허용 차이를 ±1로 좁혀야 '어시스턴트 머리말이 빠진 템플릿'(2토큰 차이)을 잡을 수 있다. 기본 허용치(잘림
# 판정의 16토큰)로는 통과해 버리므로, v13 관문 7은 ±1로 돌렸다.
def test_the_prompt_match_tolerance_catches_a_missing_assistant_header(tmp_path):
    # A Modelfile template that drops "<|im_start|><|assistant|>" reads 2 tokens fewer.
    records = [gen(f"k{i}", generation_prompt_tokens_counted=1500) for i in range(1, 13)]
    records[0]["generation_prompt_tokens_counted"] = 1502
    path = write_gate_run(tmp_path, records, GATE_META)

    within_16 = generator_arms.gate(path, digest="abc123", require_prompt_match=True)
    within_1 = generator_arms.gate(path, digest="abc123", require_prompt_match=True, prompt_tolerance=1)

    assert within_16["checks"]["prompt_match"]["ok"] is True
    assert within_1["checks"]["prompt_match"]["ok"] is False


# 관문 리포트 표의 모든 줄이 머리와 같은 칸 수인지 확인한다. 2026-10-05 리포트는 첫 실행의 확인 항목으로
# 머리를 만들어, 관문 7이 있는 G3 줄만 칸이 하나 많아 GitHub에서 표가 깨졌다(커밋 928349b). 없는 칸은 '-'로
# 채운다.
def test_gate_report_gives_every_row_the_header_s_columns(tmp_path):
    # Only the A.X run checks its prompt counts (rule 7). The 2026-10-05 report took its
    # header from the first run, so that row had one cell more than the header.
    records = [gen(f"k{i}", generation_prompt_tokens_counted=1500) for i in range(1, 13)]
    path = write_gate_run(tmp_path, records, GATE_META)
    results = [
        generator_arms.gate(path, digest="abc123"),
        generator_arms.gate(path, digest="abc123", require_prompt_match=True),
    ]

    lines = generator_arms.gate_report(results).splitlines()
    table = [line for line in lines if line.startswith("|")]

    header = [c.strip() for c in table[0].strip("|").split("|")]
    assert "prompt_match" in header
    assert {line.count("|") for line in table} == {table[0].count("|")}
    first, second = ([c.strip() for c in row.strip("|").split("|")] for row in table[2:])
    column = header.index("prompt_match")
    assert first[column] == "-" and second[column].startswith("ok: ")
    assert first[-1] == second[-1] == "12 items, median 0.0, max abs 0"


# 팔 파일(<tag>.raw.gen.jsonl)을 같은 이름 규칙의 판정 파일(<tag>.raw.J1.judge.jsonl)과 문항별로 짝짓고,
# 결과가 요약 JSON에 그대로 저장할 수 있는 단순 데이터인지 확인한다.
def test_arm_files_pair_with_their_judgments(tmp_path):
    gen_path = tmp_path / "v13_sel_g0_qa_dev_ko.raw.gen.jsonl"
    write_jsonl(gen_path, [generator_arms.unguarded_record(gen("k1"))])
    judged = tmp_path / "v13_sel_g0_qa_dev_ko.raw.J1.judge.jsonl"
    write_jsonl(
        judged, [{"id": "k1", "correctness_score": 5, "faithfulness_score": 4, "hallucinated": False}]
    )

    rows = generator_arms.arm_rows([gen_path], "J1")

    assert rows[0]["correctness"] == 5 and rows[0]["dataset"] == "qa_dev_ko.jsonl"
    assert json.loads(json.dumps(rows))  # plain data, kept in the summary JSON


# v13 규칙 변경 2(2026-10-05)를 고정한다: 같은 답이라도 판정 순서의 다른 자리에서 판정되면 점수가 ±1 움직일 수
# 있으므로, shares={"G0+LG": "G0"}(명령행의 --share)를 주면 가드가 걸리지 않은 문항은 lg 팔도 raw 팔의 판정을
# 쓰고, 자기 판정과 다른 문항 수는 세기만 한다. 가드가 걸린 k1만 lg 자신의 점수(5)를 쓴다.
def test_an_lg_arm_can_share_the_raw_judgments_of_items_the_guard_left_alone(tmp_path):
    # docs/experiments.md v13, rule change 2026-10-05: the same answer judged at another place
    # in the judge order can move by a point, so where the guard did not fire the lg arm takes
    # the raw arm's judgment; its own differing judgments are only counted.
    records = [gen("k1", **GUARDED), gen("k2"), gen("k3")]
    paths = {}
    for arm, derive in (("raw", generator_arms.unguarded_record), ("lg", generator_arms.guarded_record)):
        gen_path = tmp_path / f"v13_adopt_g0_qa_test3b_ko.{arm}.gen.jsonl"
        write_jsonl(gen_path, [derive(r) for r in records])
        paths[arm] = gen_path
    scores = {"raw": {"k1": 2, "k2": 4, "k3": 5}, "lg": {"k1": 5, "k2": 3, "k3": 5}}
    for arm, by_id in scores.items():
        write_jsonl(
            tmp_path / f"v13_adopt_g0_qa_test3b_ko.{arm}.J1.judge.jsonl",
            [
                {"id": i, "correctness_score": s, "faithfulness_score": s, "hallucinated": s < 3}
                for i, s in by_id.items()
            ],
        )
    arms = {"G0": [paths["raw"]], "G0+LG": [paths["lg"]]}

    _, own = generator_arms.summary_report("t", "J1", arms, "G0")
    _, shared = generator_arms.summary_report("t", "J1", arms, "G0", shares={"G0+LG": "G0"})

    assert own["arms"]["G0+LG"]["summary"]["all"]["correctness_sum"] == 13
    lg = shared["arms"]["G0+LG"]
    assert lg["summary"]["all"]["correctness_sum"] == 5 + 4 + 5  # k1 its own, k2 and k3 from G0
    assert lg["shared"] == {"from": "G0", "items": 2, "own_judgment_differs": 1}
    assert shared["arms"]["G0+LG"]["vs_baseline"]["all"].startswith("+3")


# 문항 행의 '생성 컨텍스트에 정답 페이지가 있었는가'(v13 단계 B 보고 항목, v12에서 손으로 센 36/39를 표에
# 넣으려고 추가). 다른 번역의 같은 페이지도 맞음으로 세고, 패시지가 없으면 False다.
def test_item_row_says_whether_the_answer_s_passages_held_an_expected_page():
    # docs/experiments.md v13 stage B compares two Korean embedders with one generator and
    # reports how many answers were written from passages that held an expected page (v12
    # counted 36 vs 39 of 40). A page counts in any translation, as a retrieval hit does.
    hit = generator_arms.item_row(gen("k1"), None)  # passage 1 is docs/ko/docs/p1.md
    other_translation = generator_arms.item_row(
        gen("k2", expected_source_paths=["docs/en/docs/p2.md"]), None
    )
    miss = generator_arms.item_row(gen("k3", expected_source_paths=["docs/ko/docs/p9.md"]), None)
    no_passages = generator_arms.item_row(gen("k4", chunks=[]), None)

    assert hit["context_has_expected_page"] is True
    assert other_translation["context_has_expected_page"] is True
    assert miss["context_has_expected_page"] is False
    assert no_passages["context_has_expected_page"] is False


# 요약 표에 'passages hold an expected page' 열이 생기고, 그 줄의 칸 수가 머리와 같으며 값이 '1/2'인지
# 확인한다.
def test_the_summary_reports_answers_written_from_an_expected_page(tmp_path):
    records = [gen("k1"), gen("k2", expected_source_paths=["docs/ko/docs/p9.md"])]
    gen_path = tmp_path / "v13b_unit.gen.jsonl"
    write_jsonl(gen_path, records)

    report, data = generator_arms.summary_report("t", "", {"B0": [gen_path]}, None)

    assert data["arms"]["B0"]["summary"]["ko"]["context_expected_page"] == "1/2"
    table = [line for line in report.splitlines() if line.startswith("|")]
    header = [c.strip() for c in table[0].strip("|").split("|")]
    row = [c.strip() for c in table[2].strip("|").split("|")]
    assert len(row) == len(header)
    assert row[header.index("passages hold an expected page")] == "1/2"

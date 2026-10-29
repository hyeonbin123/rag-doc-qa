"""v16-L(Claude 라벨 확장) 표본 추출과 보고, v16-B(생성 쪽 거절 지시) 결정 도구 테스트."""

# [테스트 묶음] eval/judge_panel.py의 v16-L 부분. sample-pairs(v13 채택 G0·G3 짝 전수 + 나머지에서 단순
# 무작위 + 라벨러 묶음 나누기)와 report-pairs(Claude 라벨 기준 G3 − G0, 판정 구성별 kappa, 재라벨 일치, 길이
# 상관)를 합성 기록과 커밋된 기록으로 확인한다. 규칙은 docs/experiments.md v16-L(라벨 전에 커밋)이다. v15 I5
# 표본 재현 테스트는 tests/test_v15_eval.py에 그대로 있다.
# 뒤쪽은 eval/refusal.py prompt-arms(v16-B의 dev 관문과 test 결정)다. 측정 전에 커밋한
# 규칙(docs/experiments.md v16-B)의 조건 1~6과 관문, 멈춤 조건을 합성 기록의 경계값으로 고정한다(v15 I4 결정
# 도구와 같은 방식).

import json
import math
from pathlib import Path

import pytest

from app.services.generation import FIXED_REFUSAL
from app.services.language import detect_language
from eval import judge_panel, refusal
from eval.common import read_jsonl
from eval.judge import answer_sha1, judge_context
from eval.run_judge import judged_path, meta_path

BLIND_FIELDS = {"sample_id", "language", "question", "context_passages", "answer", "reference_answer"}


def _record(dataset: str, item_id: str, language: str, model: str, answer: str, chunk_id: str = "1") -> dict:
    return {
        "id": item_id,
        "dataset": dataset,
        "language": language,
        "model": model,
        "question": f"질문 {dataset} {item_id}",
        "answer": answer,
        "reference_answer": f"참고 {item_id}",
        "chunks": [{"chunk_id": chunk_id, "content": f"문단 {dataset} {item_id}", "source_path": "a.md"}],
    }


# 생성 기록 파일 하나와 라벨별 판정 파일(<이름>.<라벨>.judge.jsonl)을 쓴다. scores: 라벨 → (기록 → 정확도).
def _write(tmp_path: Path, name: str, records: list[dict], scores: dict) -> Path:
    gen = tmp_path / f"{name}.gen.jsonl"
    gen.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")
    for label, score_of in scores.items():
        judged_path(gen, label).write_text(
            "".join(
                json.dumps(
                    {"id": r["id"], "correctness_score": score_of(r), "answer_sha1": answer_sha1(r["answer"])}
                )
                + "\n"
                for r in records
            ),
            encoding="utf-8",
        )
    return gen


# 합성 기록 묶음. 짝 비교 v13_adopt: 질문 6개(영어 n0~n2, 한국어 n0~n2)에 G0(Qwen)·G3(A.X) 답. 한국어 n2는 두
# 팔의 답과 문맥이 같다(실제 기록의 n048처럼 한 번만 센다). 나머지: b2의 B0는 G3 한국어 n0과 같은 답(청크 id만
# 다름, 실제 B0처럼 모집단에서 빠짐)이고 P는 4개, v14의 C3·C4는 5개씩이며 C4 q3은 C3 q3과 같은 답이다.
# 판정: J1v15는 A.X에 5·Qwen에 4, J2v15는 A.X에 3·Qwen에 4, 나머지 답에는 둘 다 3을 준다.
def _world(tmp_path: Path, monkeypatch) -> dict[str, Path]:
    def j1(r: dict) -> int:
        return 3 if r["dataset"] == "dev.jsonl" else (5 if r["model"] == "a.x-4.0-light" else 4)

    def j2(r: dict) -> int:
        return 3 if r["dataset"] == "dev.jsonl" else (3 if r["model"] == "a.x-4.0-light" else 4)

    scores = {"J1v15": j1, "J2v15": j2}
    files = {}
    for arm, model in (("g0", "qwen2.5:7b-instruct"), ("g3", "a.x-4.0-light")):
        for language in ("ko", "en"):
            records = [
                _record(
                    f"t_{language}.jsonl",
                    f"n{k}",
                    language,
                    model,
                    "같은 답" if (language, k) == ("ko", 2) else f"{arm} {language} 답 {k}",
                )
                for k in range(3)
            ]
            files[f"{arm}_{language}"] = _write(tmp_path, f"pair_{arm}_{language}", records, scores)
    b0 = _record("t_ko.jsonl", "n0", "ko", "a.x-4.0-light", "g3 ko 답 0", chunk_id="99")
    files["b0"] = _write(tmp_path, "rest_b0", [b0], scores)
    files["p"] = _write(
        tmp_path,
        "rest_p",
        [_record("t_ko.jsonl", f"n{k}", "ko", "a.x-4.0-light", f"p 답 {k}") for k in range(4)],
        scores,
    )
    for arm in ("c3", "c4"):
        records = [
            _record("dev.jsonl", f"q{k}", "en", "a.x-4.0-light", "겹친 답" if k == 3 else f"{arm} 답 {k}")
            for k in range(5)
        ]
        files[arm] = _write(tmp_path, f"rest_{arm}", records, scores)
    monkeypatch.setattr(
        judge_panel,
        "COMPARISONS",
        {
            "v13_adopt": {"G0": [files["g0_ko"], files["g0_en"]], "G3": [files["g3_ko"], files["g3_en"]]},
            "b2": {"B0": [files["b0"]], "P": [files["p"]]},
            "v14": {"C3": [files["c3"]], "C4": [files["c4"]]},
        },
    )
    monkeypatch.setattr(
        judge_panel, "BASELINES", {"v13_adopt": ("G0", "G3"), "b2": ("B0", "P"), "v14": ("C3", "C4")}
    )
    return files


# 짝 비교의 질문마다 (G0 키, G3 키). 짝 완결 확인에 쓴다.
def _pair_keys() -> dict[tuple[str, str], dict[str, str]]:
    out: dict[tuple[str, str], dict[str, str]] = {}
    for arm, paths in judge_panel.COMPARISONS["v13_adopt"].items():
        for path in paths:
            for r in read_jsonl(path):
                out.setdefault((r["dataset"], r["id"]), {})[arm] = judge_panel.item_key(path, r)
    return out


# 표본 문항이 덮는 지문 → 표본 문항. 같은 답(같은 지문)을 가진 다른 키가 어느 표본 문항에 붙는지 찾는다.
def _by_mark(chosen: list[dict]) -> dict[tuple, dict]:
    return {judge_panel.fingerprint(i["record"]): i for i in chosen}


def _check_pairs_complete(chosen: list[dict], records: dict[str, dict]) -> None:
    by_mark = _by_mark(chosen)
    for question, arms in _pair_keys().items():
        items = [by_mark.get(judge_panel.fingerprint(records[arms[arm]])) for arm in ("G0", "G3")]
        assert all(items), question  # 모든 G0에 같은 질문의 G3가 있고 둘 다 표본에 있다
        assert items[0]["batch"] == items[1]["batch"], question  # 같은 라벨러 묶음


# 표본: 짝 비교의 답은 중복을 뺀 전부, 나머지는 seed 고정 단순 무작위. 같은 seed면 같은 표본(순서·묶음까지),
# 같은 질문의 두 답은 같은 묶음, 묶음 크기는 고르다. 판정 점수는 읽지 않는다(population(label=None)).
def test_pair_sample_takes_every_pair_and_a_simple_random_rest(tmp_path, monkeypatch):
    _world(tmp_path, monkeypatch)
    items = judge_panel.population(label=None)
    assert all(i["j1"] is None for i in items)
    # 모집단: 짝 12개 중 한국어 n2 중복 1개, B0(G3 한국어 n0과 같은 답), C4 q3(C3 q3과 같은 답)이 빠진다.
    assert len(items) == 11 + 4 + 5 + 4
    chosen = judge_panel.pair_sample(items, seed=7, rest_size=5, batches=3)
    assert chosen == judge_panel.pair_sample(items, seed=7, rest_size=5, batches=3)
    other_seed = judge_panel.pair_sample(items, seed=8, rest_size=5, batches=3)
    assert [i["key"] for i in other_seed] != [i["key"] for i in chosen]
    pairs = [i for i in chosen if i["stratum"] == "pairs"]
    rest = [i for i in chosen if i["stratum"] == "rest"]
    assert len(pairs) == 11 and len(rest) == 5
    assert len({i["key"] for i in chosen}) == len(chosen)
    assert all(not i["key"].startswith("pair_") for i in rest)
    _check_pairs_complete(chosen, judge_panel.records_by_key())
    sizes = [sum(1 for i in chosen if i["batch"] == b) for b in (1, 2, 3)]
    assert sum(sizes) == 16 and max(sizes) - min(sizes) <= 2
    # 파일 순서는 묶음 순서다(라벨러 k는 k번째 묶음의 줄을 받는다).
    assert [i["batch"] for i in chosen] == sorted(i["batch"] for i in chosen)
    with pytest.raises(ValueError):
        judge_panel.pair_sample(items, seed=7, rest_size=99, batches=3)


# sample-pairs 명령: 라벨러 파일에는 v15와 같은 여섯 항목만 있고(팔·출처·층·묶음·점수 없음), 짧은 id는 v15
# 표본의 id와 다른 소금을 친 키 해시다. 열쇠 파일은 라벨러 파일과 같은 순서로 키·층·묶음을 갖는다.
def test_sample_pairs_command_writes_a_blind_file_without_arm_source_or_score(tmp_path, monkeypatch):
    _world(tmp_path, monkeypatch)
    monkeypatch.setattr(judge_panel, "REST_SAMPLE_SIZE", 5)
    monkeypatch.setattr(judge_panel, "PAIR_BATCHES", 3)
    blind_path, key_path = tmp_path / "out" / "blind.jsonl", tmp_path / "out" / "key.jsonl"
    assert judge_panel.sample_pairs_command(blind_path, key_path) == 0
    blind, keys = read_jsonl(blind_path), read_jsonl(key_path)
    assert len(blind) == 16
    assert all(set(b) == BLIND_FIELDS for b in blind)
    assert [b["sample_id"] for b in blind] == [k["sample_id"] for k in keys]
    assert len({b["sample_id"] for b in blind}) == len(blind)
    for k in keys:
        assert k["sample_id"] == judge_panel.pair_blind_id(k["key"]) != judge_panel.blind_id(k["key"])
        assert set(k) == {"sample_id", "key", "stratum", "batch", "family", "language", "length"}
    text = blind_path.read_text(encoding="utf-8")
    for word in ("pair_", "rest_", "qwen", "a.x-4.0", "stratum", "batch", "correctness"):
        assert word not in text
    records = judge_panel.records_by_key()
    for b, k in zip(blind, keys, strict=True):
        r = records[k["key"]]
        assert (b["question"], b["answer"], b["reference_answer"]) == (
            r["question"],
            r["answer"],
            r["reference_answer"],
        )
        assert b["context_passages"] == judge_context(r)
        assert k["length"] == len(r["answer"])


# kappa 차이 구간의 질문 단위 재표집: 문항마다 다른 무리를 주면 문항 단위 재표집과 같은 구간이 나온다(같은
# 난수열). 무리 목록의 길이가 문항 수와 다르면 ValueError.
def test_kappa_diff_ci_with_one_item_per_cluster_matches_item_resampling():
    labels = [1, 2, 3, 4, 5, 3, 2, 4, 5, 1]
    base = [2, 2, 3, 5, 4, 3, 1, 4, 4, 2]
    other = [1, 3, 3, 4, 5, 2, 2, 5, 5, 1]
    item_level = judge_panel.kappa_diff_ci(labels, base, other, n_resamples=300)
    assert (
        judge_panel.kappa_diff_ci(labels, base, other, n_resamples=300, clusters=list(range(10)))
        == item_level
    )
    paired = judge_panel.kappa_diff_ci(
        labels, base, other, n_resamples=300, clusters=[k // 2 for k in range(10)]
    )
    assert paired[0] <= paired[1]
    with pytest.raises(ValueError):
        judge_panel.kappa_diff_ci(labels, base, other, clusters=[0, 1])


# 판정 구성별 짝 요약은 기존 comparison_summary와 같은 계산이다. 커밋된 판정으로 단독 판정기의 v13 채택
# G3 − G0를 다시 내면 v15 I5 결정 방향 표의 값과 같다(J1 기록 +20, J1v15 +25, J2 −13, J3 −1).
def test_pair_summaries_reproduce_the_v15_decision_table_for_each_judge():
    labels = ["J1v15", "J2v15", "J3v15"]
    scores = {label: judge_panel.scores_for(label) for label in labels}
    summaries = judge_panel.pair_config_summaries(labels, scores)
    for label, diff in (("J1v15", 25), ("J2v15", -13), ("J3v15", -1)):
        assert summaries[label] == judge_panel.comparison_summary("v13_adopt", label, scores[label])
        assert summaries[label]["all"]["diff"] == diff
    assert summaries["J2v15+J3v15"]["all"]["diff"] == pytest.approx((-13 - 1) / 2)
    recorded = judge_panel.scores_for("J1")
    assert judge_panel.comparison_summary("v13_adopt", "J1", recorded)["all"]["diff"] == 20


# report-pairs 본체(합성 기록): Claude 라벨 기준 G3 − G0(같은 답인 한국어 n2는 두 팔에 같은 라벨), 판정
# 구성별 G3 − G0, 표본 kappa와 따로 보는 구성 쌍의 구간, 층별 kappa, v15 라벨과의 재라벨 일치(지문으로 맞추고
# v15 표본 안의 같은 답은 한 번), 라벨 분포, 길이 상관.
def test_report_pairs_on_synthetic_records(tmp_path, monkeypatch):
    _world(tmp_path, monkeypatch)
    chosen = judge_panel.pair_sample(judge_panel.population(label=None), seed=7, rest_size=5, batches=3)

    def label(i: dict) -> int:
        if i["stratum"] == "rest":
            return 2
        if i["record"]["answer"] == "같은 답":
            return 5
        return 4 if i["record"]["model"] == "a.x-4.0-light" else 3

    key_path, claude_path = tmp_path / "key.jsonl", tmp_path / "claude.jsonl"
    rows = [
        {
            "sample_id": judge_panel.pair_blind_id(i["key"]),
            "key": i["key"],
            "stratum": i["stratum"],
            "batch": i["batch"],
        }
        for i in chosen
    ]
    key_path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    claude_path.write_text(
        "".join(
            json.dumps({"sample_id": r["sample_id"], "correctness_score": label(i)}) + "\n"
            for r, i in zip(rows, chosen, strict=True)
        ),
        encoding="utf-8",
    )
    # v15 라벨: G3 영어 n0(같은 키, 4 → 일치), B0(G3 한국어 n0과 같은 답, 2 → 새 라벨 4와 2점 차이)와 그 중복
    # 한 줄(같은 답이라 한 번만 셈), 새 표본에 뽑히지 않은 나머지 문항 하나(재라벨 일치에서 빠짐).
    sampled = {i["key"] for i in chosen}
    unsampled = next(i["key"] for i in judge_panel.population(label=None) if i["key"] not in sampled)
    old = [
        ("s1", "pair_g3_en.gen.jsonl#n0", 4),
        ("s2", "rest_b0.gen.jsonl#n0", 2),
        ("s3", "rest_b0.gen.jsonl#n0", 2),
        ("s4", unsampled, 1),
    ]
    v15_key, v15_claude = tmp_path / "v15_key.jsonl", tmp_path / "v15_claude.jsonl"
    v15_key.write_text(
        "".join(json.dumps({"sample_id": s, "key": k}) + "\n" for s, k, _ in old), encoding="utf-8"
    )
    v15_claude.write_text(
        "".join(json.dumps({"sample_id": s, "correctness_score": g}) + "\n" for s, _, g in old),
        encoding="utf-8",
    )

    result = judge_panel.report_pairs(
        ["J1v15", "J2v15"], claude_path, key_path, v15_claude, v15_key, focus=("J2v15", "J1v15+J2v15")
    )
    claude_pairs = result["pairs"]["claude"]
    assert claude_pairs["en"]["G0"] == 9 and claude_pairs["en"]["G3"] == 12
    assert claude_pairs["ko"]["G0"] == 3 + 3 + 5 and claude_pairs["ko"]["G3"] == 4 + 4 + 5
    assert claude_pairs["all"]["n"] == 6 and claude_pairs["all"]["diff"] == 5
    judges = result["pairs"]["judges"]
    assert judges["J1v15"]["all"]["diff"] == 6 and judges["J2v15"]["all"]["diff"] == -6
    assert judges["J1v15+J2v15"]["all"]["diff"] == 0
    kappa = result["kappa"]
    assert kappa["n"] == 16
    assert set(kappa["configs"]) == {"J1v15", "J2v15", "J1v15+J2v15"}
    assert "diff_vs_first_ci90" not in kappa["configs"]["J1v15"]
    assert kappa["focus"]["base"] == "J2v15" and kappa["focus"]["other"] == "J1v15+J2v15"
    low, high = kappa["focus"]["ci90"]
    assert low <= high and kappa["focus"]["width"] == pytest.approx(high - low)
    assert kappa["by_stratum"]["pairs"]["n"] == 11 and kappa["by_stratum"]["rest"]["n"] == 5
    assert kappa["bootstrap"]["unit"] == "question"
    relabel = result["relabel"]
    assert relabel["n"] == 2
    assert relabel["exact"] == pytest.approx(0.5) and relabel["within_one"] == pytest.approx(0.5)
    assert relabel["mean_diff_new_minus_old"] == pytest.approx(1.0)
    assert result["claude"]["n"] == 16
    assert result["claude"]["counts"] == {"1": 0, "2": 5, "3": 5, "4": 5, "5": 1}
    assert sum(b["n"] for b in result["claude"]["by_batch"].values()) == 16
    assert set(result["reference_length_spearman"]) == {"all", "ax", "qwen"}
    assert set(result["residual_length_spearman"]) == {"J1v15", "J2v15"}


# report-pairs 명령: <태그>.pairs.json과 리포트를 쓰고, 출처(커밋, 입력 파일 이름과 sha256)를 남긴다.
# 로컬 절대 경로는 남기지 않는다. --v15-claude와 --v15-key는 함께만 받는다.
def test_report_pairs_cli_writes_results_with_provenance(tmp_path, monkeypatch, capsys):
    import eval.common

    _world(tmp_path, monkeypatch)
    monkeypatch.setattr(judge_panel, "REST_SAMPLE_SIZE", 5)
    monkeypatch.setattr(judge_panel, "PAIR_BATCHES", 3)
    runs, reports = tmp_path / "runs", tmp_path / "reports"
    monkeypatch.setattr(judge_panel, "RUNS", runs)
    monkeypatch.setattr(eval.common, "REPORTS_DIR", reports)
    blind_path, key_path = runs / "sample.jsonl", runs / "key.jsonl"
    judge_panel.sample_pairs_command(blind_path, key_path)
    claude_path = runs / "claude.jsonl"
    claude_path.write_text(
        "".join(
            json.dumps({"sample_id": b["sample_id"], "correctness_score": 1 + n % 5}) + "\n"
            for n, b in enumerate(read_jsonl(blind_path))
        ),
        encoding="utf-8",
    )
    argv = ["judge_panel", "report-pairs", "--tag", "t", "--labels", "J1v15", "J2v15"]
    argv += ["--claude", str(claude_path), "--key", str(key_path)]
    monkeypatch.setattr("sys.argv", argv)
    assert judge_panel.main() == 0
    result = json.loads((runs / "t.pairs.json").read_text(encoding="utf-8"))
    assert result["relabel"] is None
    assert set(result["provenance"]["files"]) == {"claude.jsonl", "key.jsonl"}
    assert all(len(sha) == 64 for sha in result["provenance"]["files"].values())
    assert str(tmp_path) not in (runs / "t.pairs.json").read_text(encoding="utf-8")
    assert len(list(reports.glob("judge_pairs_t_*.md"))) == 1
    monkeypatch.setattr("sys.argv", argv + ["--v15-key", str(key_path)])
    with pytest.raises(SystemExit):
        judge_panel.main()
    capsys.readouterr()


# 라벨이 짝 비교의 답 하나라도 덮지 못하면(짝 완결이 깨지면) 보고하지 않고 멈춘다. 라벨과 열쇠의 id가 다르면
# 멈춘다.
def test_report_pairs_refuses_incomplete_pairs_and_mismatched_ids(tmp_path, monkeypatch):
    _world(tmp_path, monkeypatch)
    chosen = judge_panel.pair_sample(judge_panel.population(label=None), seed=7, rest_size=5, batches=3)
    rows = [
        {
            "sample_id": judge_panel.pair_blind_id(i["key"]),
            "key": i["key"],
            "stratum": i["stratum"],
            "batch": 1,
        }
        for i in chosen
    ]
    key_path, claude_path = tmp_path / "key.jsonl", tmp_path / "claude.jsonl"
    dropped = next(r for r in rows if r["stratum"] == "pairs")
    kept = [r for r in rows if r is not dropped]
    key_path.write_text("".join(json.dumps(r) + "\n" for r in kept), encoding="utf-8")
    claude_path.write_text(
        "".join(json.dumps({"sample_id": r["sample_id"], "correctness_score": 3}) + "\n" for r in kept),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="no label"):
        judge_panel.report_pairs(["J1v15"], claude_path, key_path)
    claude_path.write_text(
        "".join(json.dumps({"sample_id": r["sample_id"], "correctness_score": 3}) + "\n" for r in rows),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="same sample ids"):
        judge_panel.report_pairs(["J1v15"], claude_path, key_path)


# 커밋된 v16 표본(라벨러 파일·열쇠 파일)이 저장된 기록에서 고정 seed로 다시 뽑은 표본과 순서·묶음까지
# 같다(라벨을 붙인 뒤 표본을 바꾸지 않았다는 확인). 짝 비교는 질문 80개 · 중복을 뺀 답 159개 전부이고 모든
# G0에 같은 질문의 G3가 같은 묶음에 있다. 나머지는 중복을 뺀 243개에서 40개다.
def test_committed_v16_panel_sample_matches_the_sampler():
    runs = judge_panel.RUNS
    chosen = judge_panel.pair_sample(judge_panel.population(label=None))
    keys = read_jsonl(runs / "v16_panel_key.jsonl")
    blind = read_jsonl(runs / "v16_panel_sample.jsonl")
    assert [k["key"] for k in keys] == [i["key"] for i in chosen]
    assert [k["batch"] for k in keys] == [i["batch"] for i in chosen]
    assert [k["stratum"] for k in keys] == [i["stratum"] for i in chosen]
    assert [b["sample_id"] for b in blind] == [k["sample_id"] for k in keys]
    assert all(set(b) == BLIND_FIELDS for b in blind)
    records = judge_panel.records_by_key()
    assert all(b["answer"] == records[k["key"]]["answer"] for b, k in zip(blind, keys, strict=True))
    assert len(_pair_keys()) == 80
    assert sum(1 for k in keys if k["stratum"] == "pairs") == 159
    assert sum(1 for k in keys if k["stratum"] == "rest") == judge_panel.REST_SAMPLE_SIZE == 40
    pair_files = {p.name for paths in judge_panel.COMPARISONS["v13_adopt"].values() for p in paths}
    population = judge_panel.population(label=None)
    assert len(population) == 402
    assert sum(1 for i in population if i["key"].split("#")[0] not in pair_files) == 243
    _check_pairs_complete(chosen, records)
    sizes = [sum(1 for k in keys if k["batch"] == b) for b in range(1, judge_panel.PAIR_BATCHES + 1)]
    assert sizes == [26, 25, 25, 25, 26, 24, 24, 24]


# 커밋된 v16 Claude 라벨(표본·열쇠 커밋 뒤에 붙임)이 라벨러 파일의 199개를 같은 순서로 하나씩 덮고, I5와
# 같은 항목(정확도·충실도 1~5 정수, 환각 여부, 메모)만 갖는다. 짝 비교의 답 160개는 모두 지문으로 라벨을
# 찾을 수 있다(짝 완결).
def test_committed_v16_labels_cover_the_sample_in_order():
    sample = read_jsonl(judge_panel.RUNS / "v16_panel_sample.jsonl")
    labels = read_jsonl(judge_panel.RUNS / "v16_claude_labels.jsonl")
    assert [label["sample_id"] for label in labels] == [s["sample_id"] for s in sample]
    for label in labels:
        assert set(label) == {"sample_id", "correctness_score", "faithfulness_score", "hallucinated", "note"}
        for field in ("correctness_score", "faithfulness_score"):
            assert type(label[field]) is int and 1 <= label[field] <= 5
        assert type(label["hallucinated"]) is bool and isinstance(label["note"], str)
    keys = {k["sample_id"]: k["key"] for k in read_jsonl(judge_panel.RUNS / "v16_panel_key.jsonl")}
    records = judge_panel.records_by_key()
    labelled = {judge_panel.fingerprint(records[keys[label["sample_id"]]]) for label in labels}
    pair_keys = judge_panel.pair_record_keys()
    assert len(pair_keys) == 160
    assert all(judge_panel.fingerprint(records[key]) in labelled for key in pair_keys)


# 커밋된 v16-L 보고(eval/runs/v16_panel.pairs.json)가 커밋된 라벨·판정으로 다시 센 값과 같다. kappa 차이
# 구간은 질문 단위 bootstrap이 오래 걸려(약 4분) 빼고, 합·차이·짝 구간(10,000회)·kappa 점추정·재라벨 일치·길이
# 상관을 비교한다. 기록한 핵심 수치(docs/experiments.md v16-L 결과): Claude 라벨 G3 − G0 = −3(284 → 281),
# J1v15 +25, J2+J3 − J2 kappa +0.063, 재라벨 58개 중 완전 일치 40개.
def test_committed_v16_report_matches_a_recount(monkeypatch):
    runs = judge_panel.RUNS
    committed = json.loads((runs / "v16_panel.pairs.json").read_text(encoding="utf-8"))
    monkeypatch.setattr(judge_panel, "kappa_diff_ci", lambda *args, **kwargs: (0.0, 0.0))
    result = judge_panel.report_pairs(
        ["J1v15", "J2v15", "J3v15"],
        runs / "v16_claude_labels.jsonl",
        runs / "v16_panel_key.jsonl",
        runs / "v15_i5_claude_labels.jsonl",
        runs / "v15_i5_panel_key.jsonl",
        focus=("J2v15", "J2v15+J3v15"),
    )
    fields = ("labels", "claude", "pairs", "relabel", "reference_length_spearman", "residual_length_spearman")
    for field in fields:
        assert result[field] == committed[field], field
    for name, entry in committed["kappa"]["configs"].items():
        assert result["kappa"]["configs"][name]["kappa"] == entry["kappa"], name
    assert result["kappa"]["by_stratum"] == committed["kappa"]["by_stratum"]
    assert result["kappa"]["focus"]["diff"] == pytest.approx(0.063, abs=5e-4)
    claude = committed["pairs"]["claude"]["all"]
    assert (claude["G0"], claude["G3"], claude["diff"]) == (284, 281, -3)
    assert committed["pairs"]["judges"]["J1v15"]["all"]["diff"] == 25
    assert committed["relabel"]["n"] == 58 and round(committed["relabel"]["exact"] * 58) == 40
    low, high = committed["kappa"]["focus"]["ci90"]
    assert 0 < low < high and committed["kappa"]["focus"]["width_below_target"]


# --- v16-B: eval/refusal.py prompt-arms (A = REFUSAL_STYLE=legacy, B = fixed) ---

GOOD = {"en": "Use Query.", "ko": "Query를 씁니다."}
NO = {"en": "I don't know.", "ko": "모르겠습니다."}
MADE_UP = {"en": "Celery does it like this.", "ko": "Celery는 이렇게 합니다."}
# 첫 문장이 거절이지만 뒤에서 답하는 답(판정 4점이면 '잘 답했는데 거절로 분류된 답').
PARTIAL = {"en": "I don't know all of it, but use Query.", "ko": "모르겠습니다. 다만 Query를 씁니다."}


# 언어별 임베딩 모델 identity(실행 meta의 embedding_models는 그 셋의 질문 언어만 담는다).
EMBEDDING = {"en": "BAAI/bge-small-en-v1.5", "ko": "granite@rev:dim384"}


# 한 팔의 생성 meta: 등록한 기본값(refusal.REGISTERED_META) + 두 팔이 같아야 하는 나머지 조건.
def _pa_meta(dataset: str, style: str, **changes) -> dict:
    language = "ko" if "_ko" in dataset else "en"
    meta = {
        **refusal.REGISTERED_META,
        "model_digest": "a874a70d",
        "embedding_models": {language: EMBEDDING[language]},
        "dataset": dataset,
        "dataset_sha256": {dataset: "s" * 64},
        "corpus": {"chunks_by_language": {"en": 914, "ko": 621}},
        "ollama_version": "0.35.1",
        "git_commit": "abc1234",
        "refusal_style": style,
    }
    return {**meta, **changes}


# 셋 하나의 (기록, 판정) 사전. scores가 None이면 판정 없음(답 없는 셋), kana는 섞인 답으로 둘 위치들.
def _pa_set(dataset: str, language: str, answers: list[str], scores=None, ms=5000.0, kana=()) -> dict:
    out = {}
    for n, answer in enumerate(answers):
        item_id = f"{dataset.removesuffix('.jsonl')}-{n}"
        record = {
            "id": item_id,
            "dataset": dataset,
            "language": language,
            "answer": answer,
            "generation_ms": ms,
            "kana_han": n in kana,
            "chunks": [{"chunk_id": f"c-{item_id}"}],
            "cited_chunk_numbers": [] if answer in NO.values() else [1],
            "citation_skipped": "refusal" if answer in NO.values() else None,
        }
        judgment = None
        if scores is not None:
            judgment = {
                "id": item_id,
                "correctness_score": scores[n],
                "error": None,
                "answer_sha1": answer_sha1(answer),
                "truncation": "ok",
            }
        out[(dataset, item_id)] = (record, judgment)
    return out


# 두 팔(A legacy, B fixed)의 합성 기록. 기본값은 B가 dev 관문의 모든 조건을 딱 경계에서 넘는 경우다:
# 한국어 답 없는 dev 거절 +1, 답 있는 dev '판정 4 이상인데 거절' +1·거절 +2(조건 2), 정확도 합 차이 0(조건 3),
# "You don't know"로 시작하는 영어 답 0(조건 5), 생성 시간 중앙값 +500ms(조건 6). test=True면 답 없는
# test(한국어 42·영어 52문항)를 더하고, ko_gain·en_gain은 B − A 거절 수, test_kana·test_you는 B의 test 답에
# 섞인 답·2인칭 거절을 몇 개 넣을지다.
def _pa_arms(
    *,
    ko_na_gain=1,
    false_refusals=1,
    refusals=2,
    accuracy_diff=(0, 0),
    b_ms=5500.0,
    b_you=0,
    test=False,
    ko_gain=7,
    en_gain=-1,
    test_kana=0,
    test_you=0,
):
    def arm(fixed: bool) -> refusal.PromptArm:
        ans, na, tests = {}, {}, {}
        for i, (lang, accuracy_set, refusal_set) in enumerate(
            [
                ("en", "qa_dev.jsonl", "qa_pool5_ans_dev_en.jsonl"),
                ("ko", "qa_dev_ko.jsonl", "qa_pool5_ans_dev_ko.jsonl"),
            ]
        ):
            scores = [5, 5, 5, 5 + (accuracy_diff[i] if fixed else 0)]
            ans |= _pa_set(accuracy_set, lang, [GOOD[lang]] * 4, scores, ms=b_ms if fixed else 5000.0)
            answers, ref_scores = [GOOD[lang]] * 4, [5] * 4
            if fixed:
                answers = [PARTIAL[lang]] * false_refusals + [NO[lang]] * (refusals - false_refusals)
                ref_scores = [4] * false_refusals + [1] * (refusals - false_refusals)
                answers += [GOOD[lang]] * (4 - len(answers))
                ref_scores += [5] * (4 - len(ref_scores))
            ans |= _pa_set(refusal_set, lang, answers, ref_scores, ms=b_ms if fixed else 5000.0)
        na_en = [NO["en"], NO["en"], MADE_UP["en"]]
        if fixed:
            na_en = ["You don't know how to set it up."] * b_you + na_en[b_you:]
        na |= _pa_set("qa_pool4_na_dev_en.jsonl", "en", na_en)
        ko_refusals = 1 + (ko_na_gain if fixed else 0)
        na |= _pa_set(
            "qa_pool4_na_dev_ko.jsonl", "ko", [NO["ko"]] * ko_refusals + [MADE_UP["ko"]] * (4 - ko_refusals)
        )
        if test:
            ko_n = 10 + (ko_gain if fixed else 0)
            en_n = 40 + (en_gain if fixed else 0)
            ko_answers = [NO["ko"]] * ko_n + [MADE_UP["ko"]] * (42 - ko_n)
            en_answers = [NO["en"]] * en_n + [MADE_UP["en"]] * (52 - en_n)
            if fixed:
                en_answers = ["You don't know."] * test_you + en_answers[test_you:]
            kana = range(42 - test_kana, 42) if fixed else ()
            tests |= _pa_set("qa_pool5_na_test_ko.jsonl", "ko", ko_answers, kana=kana)
            tests |= _pa_set("qa_pool5_na_test_en.jsonl", "en", en_answers)
        style = "fixed" if fixed else "legacy"
        metas = {d: _pa_meta(d, style) for d, _ in [*ans, *na, *tests]}
        return refusal.PromptArm(ans=ans, na=na, test=tests, metas=metas)

    return arm(False), arm(True)


def _pa(a, b, **kwargs) -> dict:
    return refusal.prompt_arms_command(a, b, check_registered=False, **kwargs)


# 기본 합성 기록: B가 모든 dev 조건을 경계에서 넘으므로 test를 연다. 경계(조건 3 '정확도 합 B ≥ A − 2'의
# −3~−1) 밖이라 경계 규칙도 필요 없다.
def test_prompt_arms_opens_the_test_when_every_dev_condition_holds_at_its_limit():
    result = _pa(*_pa_arms())
    assert result["verdict"] == "open_test" and result["stop"] == []
    gate = result["dev_gate"]
    assert gate["ko_unanswerable_dev_refusals"] == {"a": 1, "b": 2, "n": 4, "pass": True}
    c = result["conditions"]
    assert c["C2_false_refusals"]["en"] == {"a": [], "b": ["qa_pool5_ans_dev_en-0"], "pass": True}
    assert (c["C2_refusals"]["ko"]["a"], c["C2_refusals"]["ko"]["b"], c["C2_refusals"]["ko"]["pass"]) == (
        0,
        2,
        True,
    )
    assert (c["C3_accuracy"]["en"]["diff"], c["C3_accuracy"]["en"]["boundary"]) == (0, False)
    assert (
        c["C3_accuracy"]["en"]["n"] == 4
    )  # 정확도 합은 등록한 정확도 셋(qa_dev 등)만, pool5 답 있는 셋은 뺌
    assert (c["C6_generation_p50"]["a_ms"], c["C6_generation_p50"]["b_ms"]) == (5000.0, 5500.0)
    assert c["C5_you_dont_know"]["b"] == []
    assert result["adopt"] is None and result["boundary_rule_needed"] is False


# dev 관문의 각 조건을 경계 한 칸 밖으로 넘기면 test를 열지 않는다(기록만).
@pytest.mark.parametrize(
    ("changes", "failing"),
    [
        ({"ko_na_gain": 0}, "ko_unanswerable_dev_refusals"),  # 한국어 거절 B ≤ A
        ({"false_refusals": 2}, "C2_false_refusals"),  # B = A + 2
        ({"refusals": 3}, "C2_refusals"),  # B = A + 3
        ({"b_ms": 5501.0}, "C6_generation_p50"),  # +501ms
        ({"b_you": 1}, "C5_you_dont_know"),  # B의 영어 답 하나가 "You don't know"로 시작
        ({"accuracy_diff": (-4, 0)}, "C3_accuracy"),  # −4: 경계(−3~−1) 밖이라 경계 규칙 없이 떨어짐
    ],
)
def test_prompt_arms_keeps_the_test_closed_when_a_dev_condition_fails(changes, failing):
    result = _pa(*_pa_arms(**changes))
    assert result["verdict"] == "gate_failed"
    assert result["dev_gate"]["open_test"] is False
    failed = [name for name, ok in result["dev_gate"]["parts"].items() if not ok]
    assert failed == [failing]


# 판정 규칙의 경계 규칙: 1회 판정으로 센 정확도 합 차이가 허용 한계(−2)에서 1점 안(−3, −2, −1)이면 결정하지
# 않고 경계 규칙(다시 두 번 판정한 중앙값)을 요구한다. 중앙값 라벨(--judged-with median)로는 그 값대로 정한다.
# 판정과 무관한 조건이 이미 떨어졌으면 판정을 더 해도 결과가 같으므로 경계 규칙을 요구하지 않는다.
@pytest.mark.parametrize(("diff", "passes"), [(-1, True), (-2, True), (-3, False)])
def test_prompt_arms_asks_for_the_boundary_rule_near_the_accuracy_limit(diff, passes):
    a, b = _pa_arms(accuracy_diff=(0, diff))
    once = _pa(a, b)
    assert once["verdict"] == "boundary" and once["boundary_rule_needed"] is True
    assert once["conditions"]["C3_accuracy"]["ko"]["boundary"] is True
    median = _pa(a, b, judged_with="median")
    assert median["boundary_rule_needed"] is False
    assert median["verdict"] == ("open_test" if passes else "gate_failed")
    slow = _pa(*_pa_arms(accuracy_diff=(0, diff), b_ms=6000.0))
    assert slow["verdict"] == "gate_failed" and slow["boundary_rule_needed"] is False


# test 결정: 조건 1(한국어 B − A ≥ 7, 영어 ≥ −1; 42·52문항에 맞춘 값), 조건 4(한국어 섞인 답 B ≤ A, 모든 답),
# 조건 5(B의 영어 답 중 "You don't know"로 시작하는 답 0, 모든 답)와 dev 조건을 모두 만족하면 채택.
def test_prompt_arms_adopts_at_the_test_limits():
    result = _pa(*_pa_arms(test=True))
    assert result["verdict"] == "adopt" and result["adopt"] is True
    c1 = result["conditions"]["C1_test_refusals"]
    assert (c1["ko"]["a"], c1["ko"]["b"], c1["ko"]["n"], c1["ko"]["min_gain"]) == (10, 17, 42, 7)
    assert (c1["en"]["a"], c1["en"]["b"], c1["en"]["n"], c1["en"]["min_gain"]) == (40, 39, 52, -1)
    assert result["report"]["refusals"]["test"]["ko"]["b_by_kind"] == {"other": {"n": 42, "refusals": 17}}


@pytest.mark.parametrize(
    ("changes", "failing"),
    [
        ({"ko_gain": 6}, "C1_test_refusals"),
        ({"en_gain": -2}, "C1_test_refusals"),
        ({"test_kana": 1}, "C4_mixed"),
        ({"test_you": 1}, "C5_you_dont_know"),
    ],
)
def test_prompt_arms_rejects_when_a_test_condition_fails(changes, failing):
    result = _pa(*_pa_arms(test=True, **changes))
    assert result["verdict"] == "reject" and result["adopt"] is False
    assert [name for name, ok in result["final_parts"].items() if not ok] == [failing]


# test 기록을 줬는데 dev 관문이 닫혀 있었으면(관문을 어기고 test를 열었음) 결정하지 않고 멈춘다.
def test_prompt_arms_stops_when_the_test_was_opened_past_a_closed_gate():
    result = _pa(*_pa_arms(test=True, ko_na_gain=0))
    assert result["verdict"] == "stop"
    assert any("gate" in problem for problem in result["stop"])


# 멈춤 조건: 팔의 거절 지시 꼴이 등록과 다름, 두 팔의 다른 생성 조건이 다름, 등록한 기본값과 다름, 문항이
# 다름, 검색된 청크가 다름, 결정 판정이 없음·오류·다른 답의 판정. 하나라도 있으면 결정하지 않는다.
def _break_style(a, b):
    b.metas["qa_dev.jsonl"]["refusal_style"] = "legacy"


def _break_model(a, b):
    b.metas["qa_dev.jsonl"]["model_digest"] = "other"


def _break_registered(a, b):
    for arm in (a, b):
        for meta in arm.metas.values():
            meta["language_guard"] = False


def _break_items(a, b):
    b.na.pop(next(iter(b.na)))


def _break_chunks(a, b):
    record, _ = next(iter(b.ans.values()))
    record["chunks"] = [{"chunk_id": "other"}]


def _break_judgment(a, b):
    key = next(iter(b.ans))
    b.ans[key] = (b.ans[key][0], None)


def _break_judge_error(a, b):
    key = next(iter(a.ans))
    a.ans[key][1]["error"] = "timeout"


# 같은 셋의 두 팔은 같지만, 단계 안의 다른 영어 셋과 임베딩 모델이 다름(사이에 모델을 바꿔 다시 적재한 경우).
def _break_stage_embedding(a, b):
    for arm in (a, b):
        arm.metas["qa_dev.jsonl"]["embedding_models"] = {"en": "intfloat/multilingual-e5-small"}


def _break_answer_hash(a, b):
    key = next(iter(a.ans))
    a.ans[key][1]["answer_sha1"] = "0" * 40


@pytest.mark.parametrize(
    "breaker",
    [
        _break_style,
        _break_model,
        _break_registered,
        _break_items,
        _break_chunks,
        _break_judgment,
        _break_judge_error,
        _break_answer_hash,
        _break_stage_embedding,
    ],
)
def test_prompt_arms_stops_on_broken_inputs(breaker):
    a, b = _pa_arms()
    breaker(a, b)
    result = _pa(a, b)
    assert result["verdict"] == "stop" and result["stop"]


# 등록 확인(check_registered=True, 명령행 기본): 셋 이름·문항 수가 등록한 셋과 다르면 멈춘다.
def test_prompt_arms_checks_the_registered_sets_by_default():
    result = refusal.prompt_arms_command(*_pa_arms())
    assert result["verdict"] == "stop"
    assert any("qa_pool4_dev_en.jsonl" in problem for problem in result["stop"])


# 등록한 셋 목록·문항 수·언어가 커밋된 질문셋과 같다. 정확도 셋은 184문항(영어 72, 한국어 112), 답 없는 test는
# 한국어 42·영어 52문항이고, 조건 1의 문턱은 '30문항 기준'(한국어 +5, 영어 −1)을 같은 비율로 맞춰 올림한
# 값이다. 문항 id는 13개 셋 전체에서 겹치지 않아(보고의 문항 목록을 id만으로 적음) 그것도 확인한다.
def test_the_registered_v16b_sets_match_the_committed_question_sets():
    eval_dir = Path(refusal.__file__).parent
    groups = (refusal.ANS_DEV_SETS, refusal.NA_DEV_SETS, refusal.TEST_SETS)
    assert set(refusal.SET_SIZES) == set().union(*groups)
    ids: list[str] = []
    for name, (size, language) in refusal.SET_SIZES.items():
        questions = read_jsonl(eval_dir / name)
        assert len(questions) == size, name
        assert {detect_language(q["question"]) for q in questions} == {language}, name
        ids += [q["id"] for q in questions]
    assert len(ids) == len(set(ids)) == 327  # 답 있는 dev 193 + 답 없는 dev 40 + 답 없는 test 94
    sizes = refusal.SET_SIZES.items()
    accuracy = {
        lang: sum(size for name, (size, of) in sizes if name in refusal.ACCURACY_SETS and of == lang)
        for lang in ("en", "ko")
    }
    assert accuracy == {"en": 72, "ko": 112}
    for lang, base in (("ko", 5), ("en", -1)):
        test_size = next(size for name, (size, of) in sizes if name in refusal.TEST_SETS and of == lang)
        assert refusal.MIN_TEST_GAIN[lang] == math.ceil(base * test_size / 30)
    assert refusal.MIN_TEST_GAIN == {"ko": 7, "en": -1}


# 고정 거절문 준수 분류와 2인칭 거절 판별(보고와 조건 5에 씀).
def test_fixed_sentence_use_and_second_person_refusals():
    assert refusal.fixed_sentence_use(" " + FIXED_REFUSAL["en"] + "\n", "en") == "exact"
    assert refusal.fixed_sentence_use(FIXED_REFUSAL["ko"] + " 다만 …", "ko") == "prefix"
    assert refusal.fixed_sentence_use(FIXED_REFUSAL["en"], "ko") == "other_language"
    assert refusal.fixed_sentence_use("모르겠습니다.", "ko") == "none"
    assert refusal.starts_with_you_dont_know("You don't know.")
    assert refusal.starts_with_you_dont_know("  you do not know how to tune it")
    assert refusal.starts_with_you_dont_know("You don’t know how.")
    assert not refusal.starts_with_you_dont_know("If you don't know, use Query.")
    assert not refusal.starts_with_you_dont_know("I don't know.")


# 명령행: 파일에서 두 팔을 읽고(<기록>.<라벨>.judge.jsonl, <기록>.meta.json) <RUNS_DIR>/<태그>.json과 리포트를
# 쓴다. 종료 코드는 판정대로(0 test 열기·채택, 2 관문 탈락·채택 안 함, 3 멈춤, 4 경계 규칙 필요). 출처에는
# 파일 이름과 sha256만 남기고 로컬 절대 경로는 남기지 않는다.
def test_prompt_arms_cli_reads_files_and_exits_by_verdict(tmp_path, monkeypatch, capsys):
    import eval.common

    a, b = _pa_arms(ko_na_gain=0)
    paths = {}
    for name, arm in (("a", a), ("b", b)):
        for group in ("ans", "na"):
            rows = getattr(arm, group)
            for dataset in sorted({d for d, _ in rows}):
                gen = tmp_path / f"v16b_{name}_{dataset.removesuffix('.jsonl')}.gen.jsonl"
                items = [pair for (d, _), pair in rows.items() if d == dataset]
                gen.write_text(
                    "".join(json.dumps(r, ensure_ascii=False) + "\n" for r, _ in items), encoding="utf-8"
                )
                meta_path(gen).write_text(json.dumps(arm.metas[dataset]), encoding="utf-8")
                if group == "ans":
                    judged_path(gen, "J2v16b").write_text(
                        "".join(json.dumps(j) + "\n" for _, j in items), encoding="utf-8"
                    )
                paths.setdefault(f"--{name}-{group}", []).append(str(gen))
    runs, reports = tmp_path / "runs", tmp_path / "reports"
    monkeypatch.setattr(refusal, "RUNS_DIR", runs)
    monkeypatch.setattr(eval.common, "REPORTS_DIR", reports)
    argv = ["eval.refusal", "prompt-arms", "--tag", "t", "--label", "J2v16b", "--no-registered-check"]
    for flag, files in paths.items():
        argv += [flag, *files]
    monkeypatch.setattr("sys.argv", argv)

    assert refusal.main() == 2  # 한국어 답 없는 dev 거절 B = A → 관문 탈락
    saved = (runs / "t.json").read_text(encoding="utf-8")
    result = json.loads(saved)
    assert result["verdict"] == "gate_failed"
    assert "v16b_a_qa_dev.gen.jsonl" in result["provenance"]["files"]
    assert "v16b_b_qa_dev.J2v16b.judge.jsonl" in result["provenance"]["files"]
    assert str(tmp_path) not in saved
    assert len(list(reports.glob("refusal_prompt_arms_t_*.md"))) == 1
    capsys.readouterr()

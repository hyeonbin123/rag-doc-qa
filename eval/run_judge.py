"""저장된 답을 다시 생성하지 않고 다시 판정한다.

eval/run_answer_eval.py가 쓴 문항별 생성 기록(eval/runs/<tag>.gen.jsonl)을 읽고,
eval/runs/<tag>.<label>.judge.jsonl과 eval/reports/의 리포트를 쓴다. 여러 파일을 한 판정 설정으로 차례로
판정하므로 Ollama는 모델 하나만 올려 둔 채로 있다.

사용법:
    python -m eval.run_judge eval/runs/v11_A_test2.gen.jsonl [more .gen.jsonl ...]
        --label J0 --num-ctx 0 [--model qwen2.5:7b-instruct] [--order dataset|reverse]
        [--no-token-count] [--think false] [--flush]

--num-ctx 0은 v11 이전 판정 호출을 보낸다(num_ctx 없음: Ollama 기본 문맥이고, 너무 긴 프롬프트는 조용히
잘린다). 그 밖의 값이면 모든 프롬프트가 들어가는지 확인한 뒤 truncate=false와 함께 보낸다.
"""

# [파일 역할] 저장된 답변 기록(<tag>.gen.jsonl)을 생성 없이 다시 판정하는 명령과, 판정 실행·기록 저장을 맡는
# 공용 함수(judge_and_save)를 둔다.
# [왜 필요한가] v11에서 판정 설정(J0: Ollama 기본 문맥, J1: num_ctx 8192 + truncate false)만 바꿔 같은 답을
# 다시 채점해야 했다. 답을 다시 만들면 생성 노이즈가 섞이므로 저장된 답을 그대로 판정한다. v13 선택·채택
# 단계는 여러 파일을 '한 번의 run_judge 호출, 정해진 파일 순서, 데이터셋 순서'로 판정하게 규칙을 정했다(판정
# 순서만 바꿔도 점수가 ±1 움직였기 때문, docs/experiments.md v11 D3).
# [흐름] main: 파일마다 판정 설정 결정 → judge_file(순서 정렬 → judge_and_save) → 판정 기록·meta 저장 → 리포트
# 작성.
# [연결] eval/run_answer_eval.py가 judge_and_save·meta_path·model_digest·ollama_state·default_label을,
# eval/generator_arms.py가 judged_path·meta_path를 가져다 쓴다.

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

# httpx: Ollama의 상태 API(/api/version, /api/ps, /api/tags)를 비동기로 읽어 실행 조건으로 기록한다.
import httpx

# 앱 설정(프로바이더, Ollama 주소, 기본 모델), 공유 SSL 컨텍스트와 평가 하네스 모듈(리포트, 기록 입출력, 판정
# 로직, 토크나이저)을 가져온다.
from app.config import get_settings
from app.services.generation import ollama_ssl_context
from eval.answer_report import display_path, render_report
from eval.common import read_json, read_jsonl, write_json, write_jsonl, write_report
from eval.judge import (
    DEFAULT_JUDGE_NUM_CTX,
    JudgeConfig,
    TokenCounter,
    flush_ollama,
    judge_call_for,
    judge_items,
)
from eval.tokens import counter_for_model, tokenizer_source


# Ollama 서버의 버전, 지금 올라간 모델(ps), 로컬 모델 목록(tags)을 읽어 dict로 돌려준다. 실패한 항목은
# None으로 두고 예외를 내지 않는다(기록용이라 평가를 막지 않으려고).
# 이 값으로 '판정 뒤 모델이 GPU에 다 올라가 있었는가'(size_vram == size), 실제 문맥 크기(context_length), 모델
# digest를 결과 옆에 남긴다.
# 클라이언트는 생성·판정 호출과 같은 공유 SSL 컨텍스트로 연다(CA 번들을 프로세스에서 한 번만 읽음,
# app/services/generation.py의 ollama_ssl_context).
async def ollama_state(base_url: str) -> dict:
    """Ollama 버전, 올라간 모델, 로컬 태그 목록을 되는 대로 읽는다(결과와 함께 기록)."""
    state: dict = {}
    async with httpx.AsyncClient(timeout=10.0, verify=ollama_ssl_context()) as client:
        for key, path in (("version", "/api/version"), ("ps", "/api/ps"), ("tags", "/api/tags")):
            try:
                response = await client.get(f"{base_url.rstrip('/')}{path}")
                response.raise_for_status()
                state[key] = response.json()
            except (httpx.HTTPError, ValueError):
                state[key] = None
    return state


# tags 목록에서 모델의 digest를 찾는다. 같은 태그가 다시 올라오면 다른 모델이 될 수 있어서, 측정한 모델을
# digest로 고정해 기록한다(v13 후보 표가 digest로 모델을 정함).
def model_digest(state: dict, model: str) -> str | None:
    """로컬 모델의 manifest digest. 태그는 다시 올라올 수 있어 태그만으로는 모델이 고정되지 않는다."""
    for local in (state.get("tags") or {}).get("models", []):
        if local.get("name") == model or local.get("model") == model:
            return local.get("digest")
    return None


# ps 목록에서 그 모델이 실제로 쓴 문맥 길이(context_length)를 찾는다. J0처럼 num_ctx를 보내지 않은 판정의 실제
# 문맥(이 PC에서 4096)을 기록하는 데 쓴다.
def context_in_use(state: dict, model: str) -> int | None:
    for loaded in (state.get("ps") or {}).get("models", []):
        if loaded.get("name") == model or loaded.get("model") == model:
            return loaded.get("context_length")
    return None


# <tag>.gen.jsonl → <tag>.<라벨>.judge.jsonl. 판정 라벨(J0, J1 등)이 파일 이름에 들어가 같은 답의 여러 판정을
# 나란히 둘 수 있다.
def judged_path(gen_path: Path, label: str) -> Path:
    stem = gen_path.name.removesuffix(".jsonl").removesuffix(".gen")
    return gen_path.with_name(f"{stem}.{label}.judge.jsonl")


# x.jsonl 옆의 실행 기록 파일 이름 x.meta.json.
def meta_path(jsonl_path: Path) -> Path:
    return jsonl_path.with_name(jsonl_path.name.removesuffix(".jsonl") + ".meta.json")


# 라벨을 주지 않았을 때의 이름: num_ctx가 없으면 'legacy', 있으면 'ctx<크기>'.
def default_label(num_ctx: int | None) -> str:
    return "legacy" if num_ctx is None else f"ctx{num_ctx}"


# 주어진 순서대로 기록을 판정하고 판정 기록(JSONL)과 실행 기록(.meta.json)을 쓴다. (판정 목록, meta)를
# 돌려준다.
# meta에는 판정 라벨·모델·num_ctx·truncate 여부·순서·Ollama 버전·판정 뒤 /api/ps·실제 문맥·토크나이저(리비전
# 앞 7자리)가 들어가, 나중에 같은 판정 설정인지 확인할 수 있다.
# 토크나이저가 없으면(count_tokens None) 길이 확인과 잘림 표시 없이 판정한다.
async def judge_and_save(
    records: list[dict],
    config: JudgeConfig,
    out_path: Path,
    *,
    provider: str,
    base_url: str,
    api_key: str = "",
    count_tokens: TokenCounter | None,
    order: str = "dataset",
) -> tuple[list[dict], dict]:
    """기록을 받은 순서대로 판정하고, 판정 기록과 그 실행 메모를 쓴다."""
    started = datetime.now(UTC).isoformat()
    # 판정 직전 Ollama 상태(올라간 모델). 판정 모델이 다른 모델과 함께 올라와 있었는지를 진단에 남긴다(v15
    # I2).
    state_before = await ollama_state(base_url) if provider == "ollama" else {}
    call = judge_call_for(provider, config, base_url, api_key)
    # JudgeConfig.flush면 문항마다 판정 직전에 캐시 되돌리기 요청을 보낸다(Ollama만).
    before_each = (lambda: flush_ollama(base_url, config)) if config.flush and provider == "ollama" else None
    judgments = await judge_items(records, config, call, count_tokens, before_each=before_each)
    write_jsonl(out_path, judgments)

    # 판정이 끝난 직후의 Ollama 상태를 읽어야 판정 모델이 올라간 상태(문맥 크기, GPU 적재)가 기록된다.
    state = await ollama_state(base_url) if provider == "ollama" else {}
    source = tokenizer_source(config.model) if count_tokens is not None else None
    judge_meta = {
        "date": started,
        "label": config.label,
        "model": config.model,
        "num_ctx": config.num_ctx,
        "truncate": None if config.legacy else False,
        "provider": provider,
        "order": order,
        "think": config.think,
        "flush": config.flush,
        "ollama_version": (state.get("version") or {}).get("version"),
        "ollama_ps_before": state_before.get("ps"),
        "ollama_ps_after": state.get("ps"),
        "context_in_use": context_in_use(state, config.model),
        "tokenizer": f"{source[0]}@{source[1][:7]}" if source else None,
        "judgments_path": display_path(out_path),
    }
    write_json(meta_path(out_path), judge_meta)
    return judgments, judge_meta


# 판정 순서를 정한다. 기록을 dataset_index로 다시 정렬한 뒤(셔플 순서로 생성했어도 데이터셋 순서), --order
# reverse면 뒤집는다. 역순은 v11의 판정 반복성(M5) 측정에 쓰였다.
def ordered(records: list[dict], order: str) -> list[dict]:
    records = sorted(records, key=lambda r: r.get("dataset_index", 0))
    return list(reversed(records)) if order == "reverse" else records


# gen.jsonl 파일 하나를 판정해 같은 폴더에 judge.jsonl을 쓰고 그 경로를 돌려준다. tests/test_answer_eval.py가
# 가짜 Ollama로 이 함수를 검증한다.
async def judge_file(
    gen_path: Path,
    config: JudgeConfig,
    *,
    base_url: str,
    count_tokens: TokenCounter | None,
    order: str = "dataset",
    provider: str = "ollama",
    api_key: str = "",
) -> Path:
    records = ordered(read_jsonl(gen_path), order)
    out_path = judged_path(gen_path, config.label)
    await judge_and_save(
        records,
        config,
        out_path,
        provider=provider,
        base_url=base_url,
        api_key=api_key,
        count_tokens=count_tokens,
        order=order,
    )
    return out_path


# 명령행으로 받은 gen.jsonl 파일들을 하나의 판정 설정으로 차례로 판정한다. 파일을 한 호출에서 이어서
# 판정하므로 Ollama는 판정 모델 하나만 올린 채로 간다.
# 판정 오류가 있으면 종료 코드 1.
async def main(args: argparse.Namespace) -> int:
    settings = get_settings()
    # --num-ctx 0이면 None, 즉 v10까지의 판정 호출(J0)을 보낸다.
    num_ctx = args.num_ctx or None
    errors = 0
    for gen_path in args.generations:
        records = read_jsonl(gen_path)
        # --model을 주지 않으면 그 답을 만든 생성 모델이 판정한다. v13 이후 기본 생성 모델이 A.X라서 README는
        # --model qwen2.5:7b-instruct를 꼭 주라고 적는다.
        model = args.model or records[0].get("model") or settings.ollama_model_name
        config = JudgeConfig(
            model=model,
            num_ctx=num_ctx,
            label=args.label or default_label(num_ctx),
            think=args.think,
            flush=args.flush,
        )
        count_tokens = None
        if not args.no_token_count and settings.generation_provider == "ollama":
            count_tokens = counter_for_model(model)
            if count_tokens is None:
                print(f"warning: no tokenizer mapped for {model}; truncation is not checked")
        out_path = await judge_file(
            gen_path,
            config,
            base_url=settings.ollama_base_url,
            count_tokens=count_tokens,
            order=args.order,
            provider=settings.generation_provider,
            api_key=settings.anthropic_api_key,
        )

        # 생성 때의 실행 기록과 방금 쓴 판정 기록을 다시 읽어 run_answer_eval과 같은 형식의 리포트를 만든다.
        # 리포트 표는 데이터셋 순서로 둔다.
        gen_meta = read_json(meta_path(gen_path))
        judgments = read_jsonl(out_path)
        judge_meta = read_json(meta_path(out_path))
        tag = records[0].get("run_tag") or gen_path.stem
        report = render_report(
            f"{tag}, judge {config.label}", gen_meta, ordered(records, "dataset"), judgments, judge_meta
        )
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        path = write_report(f"answer_eval_{tag}_{config.label}_{timestamp}.md", report)
        errors += sum(1 for j in judgments if j["error"])
        print(f"{gen_path.name}: {len(judgments)} judged -> {display_path(out_path)}, report {path.name}")
    if errors:
        print(f"{errors} judge errors; see the reports", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    # 명령행 옵션. --num-ctx 기본값은 J1의 8192, --order는 dataset(기본)과 reverse만 받는다.
    parser = argparse.ArgumentParser()
    parser.add_argument("generations", type=Path, nargs="+", help="eval/runs/<tag>.gen.jsonl 파일들")
    parser.add_argument("--label", default=None, help="출력 파일 이름에 붙는 라벨. 예: J0, J1")
    parser.add_argument("--model", default=None, help="판정 모델. 기본값은 답을 생성한 모델")
    parser.add_argument(
        "--num-ctx",
        type=int,
        default=DEFAULT_JUDGE_NUM_CTX,
        help="판정 문맥 크기. 0이면 num_ctx 없이 v11 이전 호출을 보낸다",
    )
    parser.add_argument("--order", choices=["dataset", "reverse"], default="dataset")
    parser.add_argument("--no-token-count", action="store_true", help="토크나이저로 토큰 수 세기를 건너뛴다")
    # v15: 다른 계열 판정기(gemma4:12b-it-qat, qwen3.5:9b)는 추론을 꺼야 하므로 think false를 보낸다. 주지
    # 않으면 think 필드를 보내지 않는다(J1 요청 그대로).
    parser.add_argument(
        "--think",
        type=lambda v: {"true": True, "false": False}[v.lower()],
        default=None,
        help="Ollama think 필드 값(true/false). 주지 않으면 보내지 않는다",
    )
    parser.add_argument(
        "--flush",
        action="store_true",
        help="문항마다 판정 직전에 짧은 무관한 요청을 보내 프롬프트 캐시를 같은 상태로 되돌린다(v15 I2 진단)",
    )
    sys.stdout.reconfigure(errors="backslashreplace")  # 이유는 eval/run_answer_eval.py 참고
    sys.exit(asyncio.run(main(parser.parse_args())))

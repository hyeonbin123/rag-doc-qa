"""답변 평가의 LLM 판정(LLM-as-judge).

판정 모델은 질문, 검색된 문단, 모델의 답, 참고 답안을 읽고 충실도·정확도 점수(1~5)와 환각 여부를 돌려준다.

v10까지 Ollama 판정 호출은 temperature 0만 지정해서 Ollama 기본 문맥으로 돌았다. 실험 PC의 11GB GPU에서는
4096토큰이다(Ollama 0.35는 VRAM 크기로 기본값을 정한다). 판정 프롬프트에는 문단 5개, 최대 1024토큰의 답,
참고 답안이 들어가는데, Ollama는 너무 긴 프롬프트를 서버 로그 경고 하나만 남기고 잘라 버린다. 0.35.1은
처음 4토큰과 창의 뒤쪽 절반쯤을 남기므로, 사라지는 것은 질문과 앞쪽 문단이다. v11 판정(docs/experiments.md)은
truncate=false로 8192토큰을 요청하고, 첫 호출 전에 모든 프롬프트가 들어가는지 확인하며, Ollama의
prompt_eval_count를 같은 프롬프트를 토크나이저로 센 수와 나란히 남겨 잘린 프롬프트가 문항별 기록에 드러나게
한다. 예전 호출은 얼마나 자주 잘렸는지 재려고 "legacy" 판정(num_ctx=None)으로 남겨 둔다.
"""

# [파일 역할] 답변 평가의 LLM 판정(LLM-as-judge). 질문·검색된 문단·생성된 답·참고 답안을 판정 모델에게 보여
# 주고 충실도(1~5), 정확도(1~5), 환각 여부를 JSON 스키마로 받는다.
# [설계 이유]
# - 점수 범위를 스키마(minimum/maximum)와 코드 검사 양쪽으로 강제해, 범위를 벗어난 점수가 평균을 조용히 비틀지
#   못하게 한다.
# - 위 docstring처럼 v11부터 판정 문맥을 8192로 정하고 truncate=false로 넘치면 오류가 나게 했다. 보내기 전에
#   모든 프롬프트가 들어가는지 토크나이저로 확인하고, Ollama가 실제로 읽은 토큰 수를 함께 남겨 잘린 판정을
#   문항 단위로 찾을 수 있다.
# - 판정 모델은 생성 모델과 따로 고정한다(README: v11 이후 판정 모델은 qwen2.5:7b-instruct, J1). 판정 설정이
#   바뀌면 점수가 움직이므로 비교하는 조건들은 같은 판정 설정·순서로 잰다.
# [연결] eval/run_answer_eval.py(생성 후 판정)와 eval/run_judge.py(저장된 답 다시 판정)가 judge_items를
# 부른다. compare_judgments.py와 generator_arms.py는 TRUNCATION_TOLERANCE, answer_sha1을 가져다 쓴다.

from __future__ import annotations

# hashlib: 답 문자열의 SHA-1(같은 답인지 비교용). httpx: Ollama /api/chat 호출. AsyncAnthropic: Claude로
# 판정할 때의 클라이언트. ollama_ssl_context: 생성기와 함께 쓰는 SSL 컨텍스트(호출마다 클라이언트를 열어도 CA
# 번들은 프로세스에서 한 번만 읽게 한다, app/services/generation.py).
import hashlib
import json
import time
from collections.abc import Awaitable, Callable
from dataclasses import asdict, dataclass

import httpx
from anthropic import AsyncAnthropic

from app.services.generation import ollama_ssl_context

# 판정 출력 스키마: faithfulness_score(문맥이 답을 뒷받침하는 정도), hallucinated(문맥에 없는 내용을
# 말했는지), correctness_score(참고 답안과 얼마나 맞는지). Ollama에는 format으로, Claude에는 도구 입력
# 스키마(JUDGE_TOOL)로 넘긴다.
JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "faithfulness_score": {
            "type": "integer",
            "minimum": 1,
            "maximum": 5,
            "description": "1-5, is the answer supported by the given context?",
        },
        "hallucinated": {
            "type": "boolean",
            "description": "true if the answer states something not supported by context",
        },
        "correctness_score": {
            "type": "integer",
            "minimum": 1,
            "maximum": 5,
            "description": "1-5, how well does the answer match the reference answer?",
        },
    },
    "required": ["faithfulness_score", "hallucinated", "correctness_score"],
}

# Claude 판정용 도구 정의. tool_choice로 강제해 항상 스키마 모양으로 답하게 한다.
JUDGE_TOOL = {
    "name": "score_answer",
    "description": "Score a generated answer for faithfulness/groundedness and correctness.",
    "input_schema": JUDGE_SCHEMA,
}

# DEFAULT_JUDGE_NUM_CTX: v11 판정의 문맥 크기(J1). 판정 프롬프트 + 답에 남길 몫(REPLY_RESERVE_TOKENS)이 이
# 안에 들어가야 보낸다.
# TRUNCATION_TOLERANCE: Ollama가 읽은 토큰 수가 토크나이저 수보다 이만큼 넘게 적으면 잘린 것으로 본다.
# 정상이면 몇 토큰 차이지만 잘리면 문맥 창의 절반쯤이 빠지므로 16이면 충분히 구분된다(v11 측정에서 차이는
# 750회 모두 0이었다, docs/experiments.md v11).
DEFAULT_JUDGE_NUM_CTX = 8192
# REPLY_RESERVE_TOKENS: 판정 응답(약 40토큰짜리 JSON 객체)을 위해 남겨 두는 문맥.
REPLY_RESERVE_TOKENS = 256
# prompt_eval_count와 같은 프롬프트를 토크나이저로 센 수는 몇 토큰 안에서 일치하고, 잘린 프롬프트는 창의
# 절반쯤 적게 돌아온다.
TRUNCATION_TOLERANCE = 16

# JudgeCall: 프롬프트 하나를 받아 판정 결과를 돌려주는 비동기 함수(제공자별로 judge_call_for가 만든다.
# 테스트는 가짜를 넘긴다). TokenCounter: 채팅 메시지의 토큰 수를 세는 함수(eval/tokens.py가 판정 모델의
# 토크나이저로 만든다).
JudgeCall = Callable[[str], Awaitable["JudgeOutcome"]]
TokenCounter = Callable[[list[dict]], int]


# 판정 설정: 모델, 문맥 크기, 리포트·파일 이름에 붙는 라벨(J1 = 8192, J0 = 예전 호출). num_ctx=None이면 legacy
# 호출이다.
@dataclass(frozen=True)
class JudgeConfig:
    model: str
    # None이면 num_ctx와 truncate 플래그를 보내지 않는다: v11 이전 호출과 같다(Ollama 기본 문맥, 너무 긴
    # 프롬프트는 조용히 잘림).
    num_ctx: int | None = DEFAULT_JUDGE_NUM_CTX
    label: str = "J1"
    # v15: 값이 있으면 Ollama 요청의 think 필드로 보낸다(qwen3.5·gemma4 같은 추론 모델을 판정기로 쓸 때
    # false). None이면 보내지 않아 J1(qwen2.5) 요청은 전과 바이트 단위로 같다.
    think: bool | None = None
    # v15: True면 문항마다 판정 직전에 짧은 무관한 요청(FLUSH_MESSAGES)을 같은 모델·같은 num_ctx로 보내,
    # Ollama의 프롬프트 캐시를 늘 같은 상태로 되돌린다. 판정이 앞 문항(캐시에 남은 앞부분)에 따라 흔들리는지
    # 가르는 진단용이다(docs/experiments.md v15 I2).
    flush: bool = False

    @property
    def legacy(self) -> bool:
        return self.num_ctx is None


# 판정 한 번의 결과. 점수 세 개와 함께 원문 응답(raw), Ollama가 읽은·쓴 토큰 수, 끝난 이유, 걸린 시간을
# 남긴다. error가 있으면 점수는 비어 있다(문맥 초과로 판정 못 함).
@dataclass
class JudgeOutcome:
    faithfulness_score: int | None = None
    hallucinated: bool | None = None
    correctness_score: int | None = None
    raw: str | None = None
    prompt_eval_count: int | None = None
    eval_count: int | None = None
    done_reason: str | None = None
    judge_ms: float | None = None
    error: str | None = None
    # v15: Ollama가 응답에 캐시에서 다시 쓴 프롬프트 토큰 수를 알려 주면 그 값(필드가 없는 버전이면 None).
    prompt_eval_cached_count: int | None = None


# 보내기 전 길이 확인에서 들어가지 않는 프롬프트가 있을 때 내는 예외. 한 건도 보내지 않으므로 실행이 일부만
# 판정된 채로 남지 않는다.
class JudgeContextError(RuntimeError):
    """설정한 문맥에 들어가지 않는 판정 프롬프트가 있다. 아무것도 보내지 않았다."""


# 판정 프롬프트 문장. 이 문장이 바뀌면 이전 판정과 비교할 수 없으므로 테스트(tests/test_answer_eval.py)가 글자
# 그대로 고정한다.
def build_judge_prompt(question: str, context: str, answer: str, reference: str) -> str:
    return (
        f"Question: {question}\n\n"
        f"Context passages the model was given:\n{context}\n\n"
        f"Model's answer:\n{answer}\n\n"
        f"Reference answer:\n{reference}\n\n"
        "Score the model's answer. Both scores use a 1-5 scale, where 1 is worst and 5 is best."
    )


# 판정은 시스템 메시지 없이 사용자 메시지 하나로 보낸다. 토큰 수를 셀 때도 이 같은 메시지 모양을 쓴다.
def judge_messages(prompt: str) -> list[dict]:
    return [{"role": "user", "content": prompt}]


# 판정에 보여 줄 문단: 생성 기록에 저장된 청크 본문을 순위 순서로 이은 것(헤딩·번호 없이). 예전 판정과 같은
# 입력을 유지하려는 것이다.
def judge_context(record: dict) -> str:
    """판정 모델이 늘 보아 온 형태의 문단: 본문만, 순위 순서대로."""
    return "\n\n".join(chunk["content"] for chunk in record["chunks"])


# Ollama 판정 요청. 스키마를 format으로 걸어 제약 디코딩하고 temperature 0으로 둔다. legacy가 아니면 num_ctx와
# truncate=false를 더한다. legacy면 v10까지와 똑같은 요청이다(옛 판정이 얼마나 잘렸는지 재려고 남겨 둠).
def ollama_judge_payload(prompt: str, config: JudgeConfig) -> dict:
    payload = {
        "model": config.model,
        "messages": judge_messages(prompt),
        "format": JUDGE_SCHEMA,
        "stream": False,
        "options": {"temperature": 0},
    }
    if not config.legacy:
        payload["options"]["num_ctx"] = config.num_ctx
        # 이것이 없으면 Ollama는 너무 긴 프롬프트를 잘라 낸 채로 그냥 답한다.
        payload["truncate"] = False
    if config.think is not None:
        payload["think"] = config.think
    return payload


# 캐시 되돌리기 요청(JudgeConfig.flush). 판정과 다른 system 메시지로 시작하는 아주 짧은 대화라, 다음 판정
# 프롬프트와 겹치는 앞부분이 채팅 템플릿의 첫 몇 토큰뿐이다. 늘 같은 요청이므로 판정 직전 캐시 상태가 문항과
# 순서에 상관없이 같아진다. 모델에게 그대로 가는 글이라 영어 원문이다.
FLUSH_MESSAGES = [
    {"role": "system", "content": "You are a calculator. Reply with a number."},
    {"role": "user", "content": "1+1="},
]


# 캐시 되돌리기 요청 본문. num_ctx·think를 판정과 같게 해야 Ollama가 모델을 다른 문맥 크기로 다시 올리지
# 않는다. num_predict 1이라 출력은 한 토큰뿐이다.
def ollama_flush_payload(config: JudgeConfig) -> dict:
    payload = {
        "model": config.model,
        "messages": FLUSH_MESSAGES,
        "stream": False,
        "options": {"temperature": 0, "num_predict": 1},
    }
    if not config.legacy:
        payload["options"]["num_ctx"] = config.num_ctx
    if config.think is not None:
        payload["think"] = config.think
    return payload


# 캐시 되돌리기 요청을 한 번 보내고 Ollama가 알려 준 토큰 수를 돌려준다(기록용). 클라이언트는 호출마다 열고
# SSL 컨텍스트는 공유한다(판정 호출과 같음). 요청 본문은 그대로다.
async def flush_ollama(base_url: str, config: JudgeConfig, timeout: float = 180.0) -> dict:
    async with httpx.AsyncClient(timeout=timeout, verify=ollama_ssl_context()) as client:
        response = await client.post(
            f"{base_url.rstrip('/')}/api/chat", json=ollama_flush_payload(config)
        )
    response.raise_for_status()
    data = response.json()
    return {
        "prompt_eval_count": data.get("prompt_eval_count"),
        "prompt_eval_cached_count": data.get("prompt_eval_cached_count"),
    }


# 점수가 1~5 밖이면 오류를 낸다. 스키마로 강제해도 제공자가 범위를 지키지 않을 수 있어 코드에서 한 번 더
# 확인한다.
def validate_scores(result: dict) -> None:
    # 범위를 벗어난 점수는 모든 평균을 조용히 비틀므로, 그 대신 분명하게 실패시킨다.
    for key in ("faithfulness_score", "correctness_score"):
        if not 1 <= result[key] <= 5:
            raise ValueError(f"judge returned {key}={result[key]}, outside the 1-5 scale")


# Ollama 오류 문구가 '문맥 길이 초과' 종류인지 본다(truncate=false에서 넘치면 HTTP 400과 함께 오는 문구,
# docs/experiments.md v11 스모크). 이런 오류만 문항별 기록으로 남기고 나머지 오류는 그대로 올린다.
def is_context_error(message: str) -> bool:
    message = message.lower()
    return any(
        phrase in message
        for phrase in ("context length", "context size", "available context", "longer than the context")
    )


# 오류 응답의 error 필드(JSON이 아니면 본문 전체)를 꺼낸다.
def _error_message(response: httpx.Response) -> str:
    try:
        return str(response.json().get("error", response.text))
    except ValueError:
        return response.text


# Ollama로 판정 한 번. 문맥 초과 오류는 점수 없는 결과로 돌려줘 실행이 멈추지 않고 개수를 셀 수 있게 하고,
# 다른 HTTP 오류는 예외로 올린다. 응답 JSON을 파싱하고 점수 범위를 확인한 뒤, 잘림 확인에 쓸
# prompt_eval_count를 함께 남긴다.
# judge_ms는 클라이언트 생성부터 응답까지 잰다. 클라이언트마다 CA 번들을 읽던 때(2026-10-24 전)의 기록에는
# Windows 호스트에서 호출당 약 0.3초가 더 들어 있다(docs/experiments.md '기타 관찰'). 지금은 SSL 컨텍스트를
# 공유해 그 비용이 첫 호출 한 번뿐이다.
async def judge_with_ollama(
    base_url: str, prompt: str, config: JudgeConfig, timeout: float = 180.0
) -> JudgeOutcome:
    start = time.perf_counter()
    async with httpx.AsyncClient(timeout=timeout, verify=ollama_ssl_context()) as client:
        response = await client.post(
            f"{base_url.rstrip('/')}/api/chat", json=ollama_judge_payload(prompt, config)
        )
    elapsed_ms = (time.perf_counter() - start) * 1000
    if response.status_code >= 400:
        message = _error_message(response)
        if is_context_error(message):
            # 문항별 오류로 남겨 한 실행에서 몇 건인지 셀 수 있게 한다. 점수는 비워 둔다.
            return JudgeOutcome(judge_ms=elapsed_ms, error=f"HTTP {response.status_code}: {message}")
        response.raise_for_status()

    data = response.json()
    raw = data["message"]["content"]
    result = json.loads(raw)
    validate_scores(result)
    return JudgeOutcome(
        faithfulness_score=result["faithfulness_score"],
        hallucinated=result["hallucinated"],
        correctness_score=result["correctness_score"],
        raw=raw,
        prompt_eval_count=data.get("prompt_eval_count"),
        eval_count=data.get("eval_count"),
        done_reason=data.get("done_reason"),
        judge_ms=elapsed_ms,
        prompt_eval_cached_count=data.get("prompt_eval_cached_count"),
    )


# Claude로 판정 한 번. score_answer 도구를 강제하고 그 입력을 점수로 쓴다. 토큰 수는 API 사용량에서 가져온다.
async def judge_with_anthropic(api_key: str, prompt: str, model: str) -> JudgeOutcome:
    start = time.perf_counter()
    client = AsyncAnthropic(api_key=api_key)
    response = await client.messages.create(
        model=model,
        max_tokens=256,
        tools=[JUDGE_TOOL],
        tool_choice={"type": "tool", "name": "score_answer"},
        messages=judge_messages(prompt),
    )
    tool_use = next(b for b in response.content if b.type == "tool_use")
    result = tool_use.input
    validate_scores(result)
    return JudgeOutcome(
        faithfulness_score=result["faithfulness_score"],
        hallucinated=result["hallucinated"],
        correctness_score=result["correctness_score"],
        raw=json.dumps(result),
        prompt_eval_count=response.usage.input_tokens,
        eval_count=response.usage.output_tokens,
        done_reason=response.stop_reason,
        judge_ms=(time.perf_counter() - start) * 1000,
    )


# 제공자에 맞는 판정 함수를 만든다. 설정을 미리 묶어 두어 judge_items는 프롬프트만 넘기면 된다.
def judge_call_for(provider: str, config: JudgeConfig, base_url: str, api_key: str = "") -> JudgeCall:
    if provider == "ollama":
        return lambda prompt: judge_with_ollama(base_url, prompt, config)
    return lambda prompt: judge_with_anthropic(api_key, prompt, config.model)


# 판정 프롬프트가 잘렸는지: 두 수 중 하나라도 없으면 unchecked, Ollama가 읽은 수가 토크나이저 수보다 허용치
# 넘게 적으면 truncated, 아니면 ok.
def truncation_status(
    prompt_eval_count: int | None, counted_tokens: int | None, tolerance: int = TRUNCATION_TOLERANCE
) -> str:
    if prompt_eval_count is None or counted_tokens is None:
        return "unchecked"
    return "truncated" if prompt_eval_count < counted_tokens - tolerance else "ok"


# 답 문자열의 SHA-1. 두 판정 기록이 정말 같은 답을 판정했는지 비교하는 데 쓴다(보안 용도가 아니라 동일성
# 확인용).
def answer_sha1(answer: str) -> str:
    return hashlib.sha1(answer.encode("utf-8")).hexdigest()


# 저장된 답들을 순서대로 판정해 문항별 판정 기록을 만든다. 순서도 점수에 영향을 줄 수 있어(docs/experiments.md
# v13) 받은 순서 그대로 보내고 order_index로 남긴다.
async def judge_items(
    records: list[dict],
    config: JudgeConfig,
    call: JudgeCall,
    count_tokens: TokenCounter | None = None,
    before_each: Callable[[], Awaitable[dict]] | None = None,
) -> list[dict]:
    """저장된 답들을 받은 순서대로 판정한다. 문항마다 판정 기록 하나를 만든다.

    토큰 수를 세는 함수와 고정 문맥이 있으면 첫 호출 전에 모든 프롬프트를 확인하므로, 한 실행은 모두
    들어가거나 아무것도 보내지 않는다.
    """
    # 검색 결과가 있는 문항만 프롬프트를 만든다. 토크나이저가 있으면 모든 프롬프트의 토큰 수를 먼저 세고,
    # legacy가 아니면 하나라도 문맥에 안 들어갈 때 아무것도 보내지 않고 멈춘다. legacy는 잘림을 재는 것이
    # 목적이라 넘쳐도 보낸다.
    prompts = {
        r["id"]: build_judge_prompt(r["question"], judge_context(r), r["answer"], r["reference_answer"])
        for r in records
        if r["chunks"]
    }
    counts = {}
    if count_tokens is not None:
        counts = {item_id: count_tokens(judge_messages(p)) for item_id, p in prompts.items()}
    if counts and not config.legacy:
        over = {i: n for i, n in counts.items() if n + REPLY_RESERVE_TOKENS > config.num_ctx}
        if over:
            raise JudgeContextError(
                f"{len(over)} judge prompts do not fit in num_ctx={config.num_ctx} with "
                f"{REPLY_RESERVE_TOKENS} tokens left for the reply (largest {max(over.values())}): "
                f"{', '.join(sorted(over))}"
            )

    judgments = []
    # 문항마다 판정하고, 판정 설정·순서·답 해시·토큰 수·잘림 상태를 함께 기록한다. dataset, run_tag는 어느
    # 셋·어느 생성 실행의 문항인지 남긴다(eval/run_judge.py는 생성 파일 여러 개를 한 번에 판정할 수 있다).
    for order_index, r in enumerate(records):
        # v15: before_each(캐시 되돌리기 요청 등)가 있으면 판정 직전에 부르고 그 결과를 기록에 남긴다.
        flush = await before_each() if before_each is not None and r["id"] in prompts else None
        # 검색된 것이 없으면 충실도를 판단할 근거가 없으므로 판정하지 않는다(v11 이전과 같음).
        outcome = await call(prompts[r["id"]]) if r["id"] in prompts else JudgeOutcome()
        counted = counts.get(r["id"])
        truncation = (
            "error" if outcome.error else truncation_status(outcome.prompt_eval_count, counted)
        )
        judgments.append(
            {
                "id": r["id"],
                "dataset": r.get("dataset"),
                "dataset_index": r.get("dataset_index"),
                "run_tag": r.get("run_tag"),
                "judge_label": config.label,
                "judge_model": config.model,
                "judge_num_ctx": config.num_ctx,
                "judge_truncate": None if config.legacy else False,
                "order_index": order_index,
                "answer_sha1": answer_sha1(r["answer"]),
                "prompt_tokens_counted": counted,
                **asdict(outcome),
                "truncation": truncation,
                "judge_think": config.think,
                "flush": flush,
            }
        )
        # 문항마다 한 줄씩 출력해, 오래 걸리는 실행의 로그에서 진행 상황(과 멈춤)이 보이게 한다.
        print(
            f"[judge {config.label} {order_index + 1}/{len(records)}] {r['id']} "
            f"read={outcome.prompt_eval_count} counted={counted} {truncation}"
            + (f" error={outcome.error}" if outcome.error else ""),
            flush=True,
        )
    return judgments

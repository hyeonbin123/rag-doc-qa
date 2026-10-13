"""LLM-as-judge for the answer eval.

The judge reads the question, the retrieved passages, the model's answer and the
reference answer, and returns faithfulness and correctness scores (1-5) and a
hallucination flag.

Until v10 the Ollama judge call set only temperature 0, so it ran in Ollama's default
context: 4096 tokens on this machine's 11 GB GPU (Ollama 0.35 picks the default by
VRAM). A judge prompt carries five passages, an answer of up to 1024 tokens and the
reference answer, and Ollama cuts an over-long prompt with only a server-log warning:
0.35.1 keeps the first 4 tokens and roughly the last half of the window, so the question
and the first passages are what disappear. The v11 judge (docs/experiments.md) asks for
8192 tokens with truncate=false, checks before the first call that every prompt fits, and
keeps Ollama's prompt_eval_count next to a tokenizer count of the same prompt, so a cut
prompt shows up in the per-item record. The old call stays available as the "legacy"
judge (num_ctx=None) to measure how often it was cut.
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
# 판정할 때의 클라이언트.
import hashlib
import json
import time
from collections.abc import Awaitable, Callable
from dataclasses import asdict, dataclass

import httpx
from anthropic import AsyncAnthropic

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
# Context left for the judge's reply, a JSON object of about 40 tokens.
REPLY_RESERVE_TOKENS = 256
# prompt_eval_count and a tokenizer count of the same prompt agree to a few tokens; a cut
# prompt comes back about half a window short.
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
    # None sends no num_ctx and no truncate flag: the pre-v11 call (Ollama's default
    # context, over-long prompts cut silently).
    num_ctx: int | None = DEFAULT_JUDGE_NUM_CTX
    label: str = "J1"

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


# 보내기 전 길이 확인에서 들어가지 않는 프롬프트가 있을 때 내는 예외. 한 건도 보내지 않으므로 실행이 일부만
# 판정된 채로 남지 않는다.
class JudgeContextError(RuntimeError):
    """Some judge prompts do not fit in the configured context; nothing was sent."""


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
    """The passages as the judge has always seen them: contents only, in rank order."""
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
        # Without this, Ollama cuts an over-long prompt and answers anyway.
        payload["truncate"] = False
    return payload


# 점수가 1~5 밖이면 오류를 낸다. 스키마로 강제해도 제공자가 범위를 지키지 않을 수 있어 코드에서 한 번 더
# 확인한다.
def validate_scores(result: dict) -> None:
    # An out-of-range score would silently skew every average, so fail loudly instead.
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
async def judge_with_ollama(
    base_url: str, prompt: str, config: JudgeConfig, timeout: float = 180.0
) -> JudgeOutcome:
    start = time.perf_counter()
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{base_url.rstrip('/')}/api/chat", json=ollama_judge_payload(prompt, config)
        )
    elapsed_ms = (time.perf_counter() - start) * 1000
    if response.status_code >= 400:
        message = _error_message(response)
        if is_context_error(message):
            # Kept as a per-item error so a run can count them; scores stay empty.
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
) -> list[dict]:
    """Judge stored answers in the given order; one judgment record per item.

    With a counter and a fixed context, every prompt is checked before the first call,
    so a run either fits completely or sends nothing.
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
        # Nothing retrieved: there is nothing to judge faithfulness against (as before v11).
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
            }
        )
        # One line per item, so a long run's log shows progress (and a stall).
        print(
            f"[judge {config.label} {order_index + 1}/{len(records)}] {r['id']} "
            f"read={outcome.prompt_eval_count} counted={counted} {truncation}"
            + (f" error={outcome.error}" if outcome.error else ""),
            flush=True,
        )
    return judgments

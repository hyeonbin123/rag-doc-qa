"""채팅 프롬프트의 토큰 수. 잘린 프롬프트와 온전한 프롬프트를 구별하는 데 쓴다.

Ollama는 prompt_eval_count, 즉 모델이 실제로 읽은 프롬프트 토큰 수를 알려 준다. 같은 채팅 프롬프트를 그
모델의 토크나이저와 채팅 템플릿으로 세면 읽었어야 할 수가 나온다. Ollama가 자른 프롬프트는 이보다 훨씬
적게 돌아온다: Ollama 0.35.1에서 너무 긴 프롬프트는 처음 4토큰과 문맥 창의 뒤쪽 절반쯤만 남는다.

토크나이저 파일만 내려받고(수십 MB, Hugging Face 캐시로), 그것도 실행이 토큰 수를 요청할 때만 받는다.
테스트는 자체 계수기를 넘긴다.
"""

# [파일 역할] Ollama 모델 태그마다 같은 모델의 Hugging Face 토크나이저(리비전 고정)를 대응시키고, 채팅
# 프롬프트를 그 모델의 채팅 템플릿으로 렌더링한 토큰 수를 센다.
# [왜 필요한가] Ollama는 문맥보다 긴 프롬프트를 응답에 표시 없이 잘라 버린다. 그래서 판정·생성 프롬프트를
# 보내기 전에 길이를 확인하고(판정은 토큰 수 + 256 > num_ctx면 아무것도 보내지 않음), 보낸 뒤에는 Ollama의
# prompt_eval_count와 비교해 문항마다 잘림을 표시한다(docs/experiments.md v11). v11 측정에서 두 값의 차이는
# 750회 모두 0이었다(M6).
# [연결] eval/run_answer_eval.py와 eval/run_judge.py가 counter_for_model·tokenizer_source를 쓴다. 테스트는
# 가짜 토크나이저로 ChatTokenCounter를 검증해 실제 파일을 받지 않는다.

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache


# 토크나이저 하나를 가리키는 설정: 저장소, 고정 리비전, 불러오는 방식, 채팅 템플릿 추가 인자. 리비전을 고정해
# 저장소가 바뀌어도 같은 수가 나오게 한다.
@dataclass(frozen=True)
class TokenizerSpec:
    repo: str
    revision: str
    # "auto": AutoTokenizer. "gpt2": 저장소가 선언한 GPT-2 토크나이저(tokenizer.json). transformers가 그대로
    # 두면 다른 모델 종류의 사전 분할기로 불러오는 저장소에 쓴다(아래 A.X 항목 참고).
    loader: str = "auto"
    # 모델을 호출하는 방식에 맞춘 채팅 템플릿 추가 인자.
    template_kwargs: dict = field(default_factory=dict)


# Ollama 태그 → 같은 모델 토크나이저의 Hugging Face 저장소와 고정 리비전.
# 판정 모델(qwen2.5:7b-instruct)과 v13 생성 후보 세 모델(qwen3.5:9b, gemma4:12b-it-qat, A.X-4.0-Light)의
# 토크나이저. 여기에 없는 모델은 토큰 수를 세지 않는다(counter_for_model이 None).
TOKENIZERS = {
    # Ollama의 qwen2.5 템플릿은 사용자 메시지 하나만 있으면 Hugging Face 채팅 템플릿과 같은 기본 시스템
    # 프롬프트("You are Qwen, created by Alibaba Cloud...")를 붙여 렌더링한다.
    "qwen2.5:7b-instruct": TokenizerSpec(
        "Qwen/Qwen2.5-7B-Instruct", "a09a35458c702b33eeacc393d103063234e8bc28"
    ),
    # v13 후보들(docs/experiments.md). qwen3.5는 think=false로 돌리는데, Ollama의 렌더러와 Hugging Face
    # 템플릿 모두 이를 빈 think 블록으로 렌더링한다.
    "qwen3.5:9b": TokenizerSpec(
        "Qwen/Qwen3.5-9B",
        "c202236235762e1c871ad0ccb60c8ee5ba337b9a",
        template_kwargs={"enable_thinking": False},
    ),
    "gemma4:12b-it-qat": TokenizerSpec("google/gemma-4-12B-it", "707f0a3b8a3c7ad586ed01e27eafbad8a27dd0f7"),
    # transformers 5.17은 이 저장소를 (config.json의 model_type을 보고) Qwen2Tokenizer로 불러와 Qwen2의
    # 정규식으로 사전 분할한다. 하지만 저장소는 GPT2Tokenizer를 선언하고 GPT-2 바이트 수준 정규식이 든
    # tokenizer.json을 함께 내놓으며, GGUF 변환도 이쪽을 따른다.
    "a.x-4.0-light:q4_k_m": TokenizerSpec(
        "skt/A.X-4.0-Light", "ba21c20ea1b31ded1ec3e2fb432335077dc4be98", loader="gpt2"
    ),
}


# 메시지 목록을 모델의 채팅 템플릿으로 문자열로 만든 뒤 토큰 수를 센다. Ollama가 실제로 읽는 것도 템플릿을
# 거친 프롬프트이므로 같은 형태로 세야 비교가 된다.
class ChatTokenCounter:
    """모델의 채팅 템플릿으로 렌더링한 채팅 프롬프트의 토큰 수를 센다."""

    def __init__(self, tokenizer, template_kwargs: dict | None = None) -> None:
        self._tokenizer = tokenizer
        self._template_kwargs = template_kwargs or {}

    # add_generation_prompt=True: 어시스턴트 답의 머리말까지 붙인 형태로 센다(Ollama가 생성 직전에 읽는
    # 프롬프트와 같게).
    # add_special_tokens=False: 템플릿 문자열에 특수 토큰이 이미 들어 있으므로 토크나이저가 BOS 등을 한 번 더
    # 붙여 수가 늘지 않게 한다.
    def __call__(self, messages: list[dict]) -> int:
        text = self._tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True, **self._template_kwargs
        )
        return len(self._tokenizer(text, add_special_tokens=False)["input_ids"])


# 모델의 토크나이저 저장소와 리비전. 판정 meta에 어떤 토크나이저로 셌는지 기록하는 데 쓴다.
def tokenizer_source(model: str) -> tuple[str, str] | None:
    spec = TOKENIZERS.get(model)
    return (spec.repo, spec.revision) if spec else None


# 설정대로 토크나이저를 불러온다. transformers는 무거워서 실제로 셀 때만 함수 안에서 import한다(평가를
# --no-token-count로 돌리거나 테스트할 때는 불러오지 않는다).
# loader가 'gpt2'면 저장소가 선언한 GPT2TokenizerFast(tokenizer.json)로 불러온다. A.X를 AutoTokenizer로 올리면
# Qwen2Tokenizer가 되어 사전 분할이 달라지기 때문이다(docs/experiments.md v13 'A.X-4.0-Light 변환').
def load_tokenizer(spec: TokenizerSpec):
    if spec.loader == "gpt2":
        from transformers import GPT2TokenizerFast  # 무거운 import라 셀 때만 한다

        return GPT2TokenizerFast.from_pretrained(spec.repo, revision=spec.revision)
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(spec.repo, revision=spec.revision)


# 모델 태그로 토큰 계수기를 만든다. lru_cache로 모델마다 한 번만 불러와, 문항마다 토크나이저를 다시 읽지
# 않는다. 매핑이 없으면 None.
@lru_cache
def counter_for_model(model: str) -> ChatTokenCounter | None:
    """Ollama 모델 태그에 맞는 토큰 계수기. 그 토크나이저가 매핑돼 있지 않으면 None."""
    spec = TOKENIZERS.get(model)
    if spec is None:
        return None
    return ChatTokenCounter(load_tokenizer(spec), spec.template_kwargs)

# Answer eval report (v13b_b2_g3_b0.lg, judge J1)

- date: 2026-10-08T16:58:24.991240+00:00
- generated: 2026-10-08T16:43:26.577463+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-08T16:56:11.012095+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb_p1_e5s, embedding models: {'ko': 'intfloat/multilingual-e5-small'}
- dataset: qa_test3b_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13b_b2_g3_b0.gen.jsonl, eval/runs/v13b_b2_g3_b0.lg.J1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.85 | 4.30 | 4.62 | 185 | 0/40 | 7489 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n007 | 1.00 | 4 | 5 | False | 5717 | False | 1877 / 1877 | ok |
| n008 | 1.00 | 5 | 5 | False | 5687 | False | 1930 / 1930 | ok |
| n010 | 1.00 | 4 | 5 | False | 5843 | False | 2058 / 2058 | ok |
| n013 | 1.00 | 4 | 4 | False | 10912 | False | 2223 / 2223 | ok |
| n017 | 1.00 | 4 | 5 | False | 9150 | False | 2238 / 2238 | ok |
| n019 | 1.00 | 5 | 5 | False | 10814 | False | 2007 / 2007 | ok |
| n020 | 1.00 | 5 | 5 | False | 12637 | False | 2415 / 2415 | ok |
| n023 | 1.00 | 4 | 5 | False | 7519 | False | 2018 / 2018 | ok |
| n025 | 1.00 | 4 | 4 | False | 5807 | False | 1978 / 1978 | ok |
| n027 | 1.00 | 5 | 5 | False | 5916 | False | 1641 / 1641 | ok |
| n028 | 1.00 | 4 | 5 | False | 4674 | False | 1933 / 1933 | ok |
| n029 | 1.00 | 5 | 5 | False | 5803 | False | 1874 / 1874 | ok |
| n030 | 1.00 | 4 | 4 | False | 5191 | False | 1845 / 1845 | ok |
| n032 | 1.00 | 5 | 5 | False | 7675 | False | 1940 / 1940 | ok |
| n034 | 1.00 | 5 | 5 | False | 8052 | False | 2039 / 2039 | ok |
| n035 | 1.00 | 4 | 5 | False | 12077 | False | 2520 / 2520 | ok |
| n036 | 0.00 | 4 | 5 | False | 7341 | False | 2098 / 2098 | ok |
| n039 | 0.00 | 4 | 4 | False | 5118 | False | 2082 / 2082 | ok |
| n047 | 1.00 | 5 | 5 | False | 14461 | False | 2730 / 2730 | ok |
| n048 | 1.00 | 4 | 5 | False | 3825 | False | 1914 / 1914 | ok |
| n050 | 1.00 | 4 | 4 | False | 9543 | False | 1899 / 1899 | ok |
| n051 | 0.00 | 4 | 4 | False | 12375 | False | 2170 / 2170 | ok |
| n054 | 1.00 | 4 | 4 | False | 4443 | False | 1998 / 1998 | ok |
| n055 | 1.00 | 4 | 5 | False | 5248 | False | 1915 / 1915 | ok |
| n061 | 1.00 | 4 | 4 | False | 8449 | False | 2117 / 2117 | ok |
| n067 | 1.00 | 4 | 5 | False | 10448 | False | 2434 / 2434 | ok |
| n077 | 1.00 | 4 | 4 | False | 5521 | False | 2008 / 2008 | ok |
| n083 | 1.00 | 4 | 5 | False | 6002 | False | 1942 / 1942 | ok |
| n086 | 0.00 | 4 | 4 | False | 7488 | False | 2289 / 2289 | ok |
| n091 | 1.00 | 5 | 5 | False | 9018 | False | 2213 / 2213 | ok |
| n096 | 1.00 | 4 | 4 | False | 11875 | False | 2373 / 2373 | ok |
| n097 | 1.00 | 4 | 5 | False | 5429 | False | 2248 / 2248 | ok |
| n099 | 0.50 | 4 | 4 | False | 4522 | False | 1770 / 1770 | ok |
| n105 | 1.00 | 4 | 4 | False | 8495 | False | 2149 / 2149 | ok |
| n106 | 0.50 | 5 | 5 | False | 4800 | False | 1895 / 1895 | ok |
| n112 | 1.00 | 5 | 5 | False | 6539 | False | 2135 / 2135 | ok |
| n113 | 1.00 | 5 | 5 | False | 7490 | False | 1919 / 1919 | ok |
| n115 | 0.00 | 4 | 4 | False | 10906 | False | 2541 / 2541 | ok |
| n116 | 1.00 | 4 | 5 | False | 10797 | False | 2354 / 2354 | ok |
| n120 | 1.00 | 4 | 4 | False | 7874 | False | 2309 / 2309 | ok |

## Worst questions (lowest keyword coverage)

- **n036** (0.00): RequestValidationError 핸들러를 덮어쓰면서 FastAPI 기본 핸들러 동작도 재사용하는 방법이 있을까?
  > ```python
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.res
- **n039** (0.00): 의존성 안에서 또 다른 의존성을 쓰는 하위 의존성은 어떻게 동작해?
  > 하위 의존성은 중첩된 구조로 동작하며, FastAPI가 이를 자동으로 처리합니다. 예를 들어, `dependable` 함수가 다른 의존성인 `query_extractor`에 의존하는 경우, `dependable` 함수가 호출될 때 `query_extractor`도 함께 실행됩니다. 이는 매우 깊은 중첩 구조에서도 동일하게 적용되며, FastAPI는 이러한 
- **n051** (0.00): 비활성화된 계정은 로그인돼도 API를 못 쓰게 막고 싶은데 의존성을 어떻게 구성하나요?
  > 의존성을 구성하여 비활성화된 계정에 대한 접근을 제한하려면, 다음과 같은 단계를 따를 수 있습니다:

1. **사용자 상태 확인 함수 작성**:
   - 사용자 상태를 확인하는 함수를 작성합니다. 예를 들어, `is_user_active` 함수를 만들어 사용자 ID를 받아 해당 사용자가 활성화 상태인지 확인합니다.

   ```python
   from t
- **n086** (0.00): 기본 JSONResponse 대신 ORJSONResponse를 쓰면 성능이 좋아지나요?
  > 네, ORJSONResponse를 사용하면 성능이 향상될 수 있습니다.

ORJSON은 Rust 기반으로 구현되어 있어 Python의 표준 JSON 라이브러리보다 더 빠르게 JSON 직렬화를 수행합니다.

FastAPI에서 ORJSON을 사용하려면 `orjson` 라이브러리를 설치하고, `Response`를 상속받아 `ORJSONResponse` 클래스를 
- **n115** (0.00): JSON 바디를 분명히 보냈는데 422 Unprocessable Entity가 계속 떠요. 뭘 잘못한 걸까요?
  > 422 Unprocessable Entity 오류는 일반적으로 클라이언트가 보낸 JSON 데이터가 유효하지 않거나, 스키마에 맞지 않을 때 발생합니다. 이 문제를 해결하기 위해 다음 사항을 확인해 보세요:

1. **데이터 검증**: FastAPI의 `Body`와 함께 사용하는 스키마가 올바른지 확인하세요. 예를 들어, `Pydantic` 모델을 사용하여 
# Answer eval report (v13_adopt_g3_qa_test3b_ko)

- date: 2026-10-08T14:05:07.685361+00:00
- generated: 2026-10-08T13:59:21.144913+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'intfloat/multilingual-e5-small'}
- dataset: qa_test3b_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_adopt_g3_qa_test3b_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.85 | n/a | n/a | n/a | 0/0 | 7635 | 0/40 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n007 | 1.00 | None | None | None | 5864 | False | None / None | - |
| n008 | 1.00 | None | None | None | 5663 | False | None / None | - |
| n010 | 1.00 | None | None | None | 11933 | False | None / None | - |
| n013 | 1.00 | None | None | None | 12041 | False | None / None | - |
| n017 | 1.00 | None | None | None | 11456 | False | None / None | - |
| n019 | 1.00 | None | None | None | 12234 | False | None / None | - |
| n020 | 1.00 | None | None | None | 14531 | False | None / None | - |
| n023 | 1.00 | None | None | None | 7865 | False | None / None | - |
| n025 | 1.00 | None | None | None | 6321 | False | None / None | - |
| n027 | 1.00 | None | None | None | 5918 | False | None / None | - |
| n028 | 1.00 | None | None | None | 4536 | False | None / None | - |
| n029 | 1.00 | None | None | None | 5755 | False | None / None | - |
| n030 | 1.00 | None | None | None | 5120 | False | None / None | - |
| n032 | 1.00 | None | None | None | 7576 | False | None / None | - |
| n034 | 1.00 | None | None | None | 8010 | False | None / None | - |
| n035 | 1.00 | None | None | None | 12109 | False | None / None | - |
| n036 | 0.00 | None | None | None | 7245 | False | None / None | - |
| n039 | 0.00 | None | None | None | 5035 | False | None / None | - |
| n047 | 1.00 | None | None | None | 14475 | False | None / None | - |
| n048 | 1.00 | None | None | None | 3694 | False | None / None | - |
| n050 | 1.00 | None | None | None | 9223 | False | None / None | - |
| n051 | 0.00 | None | None | None | 12451 | False | None / None | - |
| n054 | 1.00 | None | None | None | 4333 | False | None / None | - |
| n055 | 1.00 | None | None | None | 5239 | False | None / None | - |
| n061 | 1.00 | None | None | None | 8632 | False | None / None | - |
| n067 | 1.00 | None | None | None | 10487 | False | None / None | - |
| n077 | 1.00 | None | None | None | 5426 | False | None / None | - |
| n083 | 1.00 | None | None | None | 5958 | False | None / None | - |
| n086 | 0.00 | None | None | None | 7606 | False | None / None | - |
| n091 | 1.00 | None | None | None | 9128 | False | None / None | - |
| n096 | 1.00 | None | None | None | 11956 | False | None / None | - |
| n097 | 1.00 | None | None | None | 5480 | False | None / None | - |
| n099 | 0.50 | None | None | None | 4601 | False | None / None | - |
| n105 | 1.00 | None | None | None | 8507 | False | None / None | - |
| n106 | 0.50 | None | None | None | 4839 | False | None / None | - |
| n112 | 1.00 | None | None | None | 6672 | False | None / None | - |
| n113 | 1.00 | None | None | None | 7664 | False | None / None | - |
| n115 | 0.00 | None | None | None | 10711 | False | None / None | - |
| n116 | 1.00 | None | None | None | 10617 | False | None / None | - |
| n120 | 1.00 | None | None | None | 7991 | False | None / None | - |

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
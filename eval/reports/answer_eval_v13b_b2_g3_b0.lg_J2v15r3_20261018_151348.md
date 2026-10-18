# Answer eval report (v13b_b2_g3_b0.lg, judge J2v15r3)

- date: 2026-10-18T15:13:48.907011+00:00
- generated: 2026-10-08T16:43:26.577463+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J2v15r3, gemma4:12b-it-qat, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: google/gemma-4-12B-it@707f0a3
- judge order: dataset
- judge date: 2026-10-18T15:11:35.916057+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb_p1_e5s, embedding models: {'ko': 'intfloat/multilingual-e5-small'}
- dataset: qa_test3b_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13b_b2_g3_b0.gen.jsonl, eval/runs/v13b_b2_g3_b0.lg.J2v15r3.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.85 | 4.58 | 4.28 | 171 | 5/40 | 7489 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n007 | 1.00 | 5 | 5 | False | 5717 | False | 1744 / 1744 | ok |
| n008 | 1.00 | 5 | 5 | False | 5687 | False | 1842 / 1842 | ok |
| n010 | 1.00 | 5 | 5 | False | 5843 | False | 1948 / 1948 | ok |
| n013 | 1.00 | 5 | 5 | False | 10912 | False | 2037 / 2037 | ok |
| n017 | 1.00 | 3 | 2 | True | 9150 | False | 2109 / 2109 | ok |
| n019 | 1.00 | 3 | 2 | True | 10814 | False | 1883 / 1883 | ok |
| n020 | 1.00 | 5 | 5 | False | 12637 | False | 2334 / 2334 | ok |
| n023 | 1.00 | 2 | 1 | True | 7519 | False | 1838 / 1838 | ok |
| n025 | 1.00 | 5 | 5 | False | 5807 | False | 1869 / 1869 | ok |
| n027 | 1.00 | 5 | 5 | False | 5916 | False | 1494 / 1494 | ok |
| n028 | 1.00 | 5 | 5 | False | 4674 | False | 1815 / 1815 | ok |
| n029 | 1.00 | 5 | 5 | False | 5803 | False | 1743 / 1743 | ok |
| n030 | 1.00 | 5 | 5 | False | 5191 | False | 1656 / 1656 | ok |
| n032 | 1.00 | 5 | 5 | False | 7675 | False | 1848 / 1848 | ok |
| n034 | 1.00 | 5 | 4 | False | 8052 | False | 1926 / 1926 | ok |
| n035 | 1.00 | 5 | 5 | False | 12077 | False | 2377 / 2377 | ok |
| n036 | 0.00 | 5 | 4 | False | 7341 | False | 1957 / 1957 | ok |
| n039 | 0.00 | 5 | 5 | False | 5118 | False | 1931 / 1931 | ok |
| n047 | 1.00 | 5 | 4 | False | 14461 | False | 2431 / 2431 | ok |
| n048 | 1.00 | 5 | 5 | False | 3825 | False | 1618 / 1618 | ok |
| n050 | 1.00 | 5 | 5 | False | 9543 | False | 1868 / 1868 | ok |
| n051 | 0.00 | 5 | 5 | False | 12375 | False | 2069 / 2069 | ok |
| n054 | 1.00 | 5 | 5 | False | 4443 | False | 1848 / 1848 | ok |
| n055 | 1.00 | 4 | 4 | False | 5248 | False | 1789 / 1789 | ok |
| n061 | 1.00 | 4 | 3 | False | 8449 | False | 1993 / 1993 | ok |
| n067 | 1.00 | 2 | 2 | True | 10448 | False | 2211 / 2211 | ok |
| n077 | 1.00 | 5 | 4 | False | 5521 | False | 1804 / 1804 | ok |
| n083 | 1.00 | 5 | 5 | False | 6002 | False | 1853 / 1853 | ok |
| n086 | 0.00 | 5 | 4 | False | 7488 | False | 2079 / 2079 | ok |
| n091 | 1.00 | 5 | 5 | False | 9018 | False | 2082 / 2082 | ok |
| n096 | 1.00 | 2 | 2 | True | 11875 | False | 2263 / 2263 | ok |
| n097 | 1.00 | 5 | 5 | False | 5429 | False | 2142 / 2142 | ok |
| n099 | 0.50 | 5 | 4 | False | 4522 | False | 1651 / 1651 | ok |
| n105 | 1.00 | 4 | 2 | False | 8495 | False | 1972 / 1972 | ok |
| n106 | 0.50 | 5 | 5 | False | 4800 | False | 1730 / 1730 | ok |
| n112 | 1.00 | 5 | 5 | False | 6539 | False | 1904 / 1904 | ok |
| n113 | 1.00 | 5 | 5 | False | 7490 | False | 1816 / 1816 | ok |
| n115 | 0.00 | 4 | 4 | False | 10906 | False | 2316 / 2316 | ok |
| n116 | 1.00 | 5 | 5 | False | 10797 | False | 2154 / 2154 | ok |
| n120 | 1.00 | 5 | 5 | False | 7874 | False | 2096 / 2096 | ok |

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
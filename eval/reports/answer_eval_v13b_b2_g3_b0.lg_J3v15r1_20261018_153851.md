# Answer eval report (v13b_b2_g3_b0.lg, judge J3v15r1)

- date: 2026-10-18T15:38:51.441643+00:00
- generated: 2026-10-08T16:43:26.577463+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J3v15r1, qwen3.5:9b, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen3.5-9B@c202236
- judge order: dataset
- judge date: 2026-10-18T15:37:13.762708+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb_p1_e5s, embedding models: {'ko': 'intfloat/multilingual-e5-small'}
- dataset: qa_test3b_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13b_b2_g3_b0.gen.jsonl, eval/runs/v13b_b2_g3_b0.lg.J3v15r1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.85 | 4.55 | 4.17 | 167 | 2/40 | 7489 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n007 | 1.00 | 5 | 5 | False | 5717 | False | 1671 / 1671 | ok |
| n008 | 1.00 | 5 | 5 | False | 5687 | False | 1755 / 1755 | ok |
| n010 | 1.00 | 5 | 5 | False | 5843 | False | 1829 / 1829 | ok |
| n013 | 1.00 | 4 | 3 | False | 10912 | False | 1923 / 1923 | ok |
| n017 | 1.00 | 4 | 3 | False | 9150 | False | 1989 / 1989 | ok |
| n019 | 1.00 | 2 | 3 | True | 10814 | False | 1706 / 1706 | ok |
| n020 | 1.00 | 5 | 5 | False | 12637 | False | 2148 / 2148 | ok |
| n023 | 1.00 | 4 | 3 | False | 7519 | False | 1730 / 1730 | ok |
| n025 | 1.00 | 5 | 5 | False | 5807 | False | 1742 / 1742 | ok |
| n027 | 1.00 | 5 | 5 | False | 5916 | False | 1399 / 1399 | ok |
| n028 | 1.00 | 5 | 5 | False | 4674 | False | 1717 / 1717 | ok |
| n029 | 1.00 | 5 | 5 | False | 5803 | False | 1616 / 1616 | ok |
| n030 | 1.00 | 5 | 5 | False | 5191 | False | 1564 / 1564 | ok |
| n032 | 1.00 | 5 | 5 | False | 7675 | False | 1699 / 1699 | ok |
| n034 | 1.00 | 5 | 5 | False | 8052 | False | 1828 / 1828 | ok |
| n035 | 1.00 | 5 | 4 | False | 12077 | False | 2221 / 2221 | ok |
| n036 | 0.00 | 4 | 3 | False | 7341 | False | 1811 / 1811 | ok |
| n039 | 0.00 | 5 | 5 | False | 5118 | False | 1802 / 1802 | ok |
| n047 | 1.00 | 5 | 5 | False | 14461 | False | 2348 / 2348 | ok |
| n048 | 1.00 | 5 | 5 | False | 3825 | False | 1602 / 1602 | ok |
| n050 | 1.00 | 4 | 3 | False | 9543 | False | 1722 / 1722 | ok |
| n051 | 0.00 | 4 | 3 | False | 12375 | False | 1900 / 1900 | ok |
| n054 | 1.00 | 5 | 5 | False | 4443 | False | 1773 / 1773 | ok |
| n055 | 1.00 | 5 | 5 | False | 5248 | False | 1692 / 1692 | ok |
| n061 | 1.00 | 4 | 3 | False | 8449 | False | 1874 / 1874 | ok |
| n067 | 1.00 | 4 | 3 | False | 10448 | False | 2077 / 2077 | ok |
| n077 | 1.00 | 4 | 3 | False | 5521 | False | 1722 / 1722 | ok |
| n083 | 1.00 | 4 | 3 | False | 6002 | False | 1721 / 1721 | ok |
| n086 | 0.00 | 5 | 4 | False | 7488 | False | 1914 / 1914 | ok |
| n091 | 1.00 | 4 | 3 | False | 9018 | False | 1920 / 1920 | ok |
| n096 | 1.00 | 3 | 2 | True | 11875 | False | 2105 / 2105 | ok |
| n097 | 1.00 | 5 | 5 | False | 5429 | False | 2016 / 2016 | ok |
| n099 | 0.50 | 5 | 5 | False | 4522 | False | 1559 / 1559 | ok |
| n105 | 1.00 | 5 | 5 | False | 8495 | False | 1849 / 1849 | ok |
| n106 | 0.50 | 5 | 5 | False | 4800 | False | 1650 / 1650 | ok |
| n112 | 1.00 | 5 | 5 | False | 6539 | False | 1817 / 1817 | ok |
| n113 | 1.00 | 5 | 5 | False | 7490 | False | 1700 / 1700 | ok |
| n115 | 0.00 | 4 | 3 | False | 10906 | False | 2199 / 2199 | ok |
| n116 | 1.00 | 5 | 5 | False | 10797 | False | 2035 / 2035 | ok |
| n120 | 1.00 | 4 | 3 | False | 7874 | False | 2009 / 2009 | ok |

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
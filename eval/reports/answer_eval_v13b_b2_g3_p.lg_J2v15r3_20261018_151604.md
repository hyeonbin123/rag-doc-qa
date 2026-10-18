# Answer eval report (v13b_b2_g3_p.lg, judge J2v15r3)

- date: 2026-10-18T15:16:04.071102+00:00
- generated: 2026-10-08T16:49:14.638971+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J2v15r3, gemma4:12b-it-qat, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: google/gemma-4-12B-it@707f0a3
- judge order: dataset
- judge date: 2026-10-18T15:13:48.914269+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb_p1_g311, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_test3b_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13b_b2_g3_p.gen.jsonl, eval/runs/v13b_b2_g3_p.lg.J2v15r3.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.83 | 4.30 | 4.20 | 168 | 8/40 | 6784 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n007 | 0.67 | 3 | 2 | True | 6401 | False | 1887 / 1887 | ok |
| n008 | 1.00 | 5 | 5 | False | 3671 | False | 1679 / 1679 | ok |
| n010 | 1.00 | 5 | 5 | False | 5651 | False | 1892 / 1892 | ok |
| n013 | 1.00 | 5 | 5 | False | 7709 | False | 1688 / 1688 | ok |
| n017 | 1.00 | 5 | 5 | False | 7583 | False | 1959 / 1959 | ok |
| n019 | 1.00 | 1 | 1 | True | 15049 | False | 2422 / 2422 | ok |
| n020 | 1.00 | 5 | 5 | False | 11557 | False | 2174 / 2174 | ok |
| n023 | 1.00 | 5 | 5 | False | 5246 | False | 1699 / 1699 | ok |
| n025 | 1.00 | 5 | 5 | False | 6077 | False | 1907 / 1907 | ok |
| n027 | 1.00 | 5 | 5 | False | 6016 | False | 1618 / 1618 | ok |
| n028 | 1.00 | 5 | 5 | False | 4228 | False | 1830 / 1830 | ok |
| n029 | 1.00 | 5 | 5 | False | 6308 | False | 1931 / 1931 | ok |
| n030 | 1.00 | 5 | 5 | False | 4024 | False | 1692 / 1692 | ok |
| n032 | 1.00 | 5 | 5 | False | 8254 | False | 1793 / 1793 | ok |
| n034 | 1.00 | 5 | 5 | False | 6608 | False | 1643 / 1643 | ok |
| n035 | 1.00 | 5 | 5 | False | 12514 | False | 2419 / 2419 | ok |
| n036 | 0.00 | 2 | 2 | True | 11210 | False | 2217 / 2217 | ok |
| n039 | 0.00 | 5 | 5 | False | 5461 | False | 1843 / 1843 | ok |
| n047 | 1.00 | 5 | 5 | False | 15409 | False | 2501 / 2501 | ok |
| n048 | 1.00 | 5 | 5 | False | 3623 | False | 1560 / 1560 | ok |
| n050 | 1.00 | 5 | 5 | False | 9116 | False | 1915 / 1915 | ok |
| n051 | 0.00 | 5 | 5 | False | 13204 | False | 2194 / 2194 | ok |
| n054 | 1.00 | 5 | 5 | False | 4449 | False | 1664 / 1664 | ok |
| n055 | 1.00 | 5 | 5 | False | 5729 | False | 1838 / 1838 | ok |
| n061 | 1.00 | 2 | 2 | True | 16242 | False | 2224 / 2224 | ok |
| n067 | 1.00 | 2 | 2 | True | 10293 | False | 2195 / 2195 | ok |
| n077 | 0.50 | 4 | 3 | False | 5714 | False | 1799 / 1799 | ok |
| n083 | 1.00 | 5 | 5 | False | 4963 | False | 1877 / 1877 | ok |
| n086 | 0.00 | 2 | 2 | True | 11152 | False | 2390 / 2390 | ok |
| n091 | 1.00 | 5 | 5 | False | 8566 | False | 2104 / 2104 | ok |
| n096 | 1.00 | 2 | 1 | True | 6850 | False | 1847 / 1847 | ok |
| n097 | 1.00 | 5 | 5 | False | 6564 | False | 2108 / 2108 | ok |
| n099 | 0.50 | 5 | 4 | False | 4559 | False | 1975 / 1975 | ok |
| n105 | 1.00 | 5 | 5 | False | 7909 | False | 2072 / 2072 | ok |
| n106 | 0.50 | 5 | 5 | False | 5635 | False | 2161 / 2161 | ok |
| n112 | 1.00 | 5 | 5 | False | 6717 | False | 2010 / 2010 | ok |
| n113 | 1.00 | 5 | 5 | False | 8291 | False | 1999 / 1999 | ok |
| n115 | 0.00 | 3 | 3 | False | 11026 | False | 2361 / 2361 | ok |
| n116 | 1.00 | 4 | 4 | False | 9708 | False | 1891 / 1891 | ok |
| n120 | 1.00 | 2 | 2 | True | 10898 | False | 2296 / 2296 | ok |

## Worst questions (lowest keyword coverage)

- **n036** (0.00): RequestValidationError 핸들러를 덮어쓰면서 FastAPI 기본 핸들러 동작도 재사용하는 방법이 있을까?
  > 네, 가능합니다. `RequestValidationError` 핸들러를 오버라이드하면서 FastAPI의 기본 예외 핸들러도 재사용할 수 있습니다.

```python
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from starl
- **n039** (0.00): 의존성 안에서 또 다른 의존성을 쓰는 하위 의존성은 어떻게 동작해?
  > FastAPI에서 하위 의존성은 중첩된 형태로 선언할 수 있으며, FastAPI가 이를 자동으로 해결합니다. 예를 들어, `query_extractor` 함수가 `query_or_cookie_extractor` 함수의 하위 의존성으로 사용될 수 있습니다. 이 경우, `query_or_cookie_extractor`가 호출될 때 먼저 `query_extrac
- **n051** (0.00): 비활성화된 계정은 로그인돼도 API를 못 쓰게 막고 싶은데 의존성을 어떻게 구성하나요?
  > 의존성을 구성하여 비활성화된 계정에 대한 접근을 제한하려면, 다음과 같은 방법을 사용할 수 있습니다:

1. **사용자 상태 검증 함수 작성**:
   - 사용자 상태를 검증하는 함수를 작성합니다. 이 함수는 사용자 ID를 받아 해당 사용자가 활성화 상태인지 확인합니다.
   - 예: `is_user_active(user_id: int) -> bool`


- **n086** (0.00): 기본 JSONResponse 대신 ORJSONResponse를 쓰면 성능이 좋아지나요?
  > 네, ORJSONResponse를 사용하면 성능이 향상될 수 있습니다.

ORJSON은 Python의 표준 JSON 라이브러리보다 더 빠른 JSON 직렬화 및 역직렬화를 제공하는 라이브러리입니다. FastAPI에서 ORJSONResponse를 사용하면 다음과 같은 이점이 있습니다:

1. **성능 향상**: ORJSON은 Rust 기반으로 구현되어 있어, 
- **n115** (0.00): JSON 바디를 분명히 보냈는데 422 Unprocessable Entity가 계속 떠요. 뭘 잘못한 걸까요?
  > 422 Unprocessable Entity 오류는 주로 요청된 데이터가 서버의 스키마나 유효성 검사 규칙을 충족하지 못할 때 발생합니다. 이 오류의 원인을 찾기 위해 다음 사항을 확인해 보세요:

1. **데이터 타입 확인**:
   - JSON 바디에 포함된 데이터가 예상하는 타입과 일치하는지 확인하세요. 예를 들어, 숫자 필드에 문자열이 들어가 있거나
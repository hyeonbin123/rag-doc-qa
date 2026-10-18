# Answer eval report (v13b_b2_g3_p.lg, judge J3v15r1)

- date: 2026-10-18T15:40:29.661778+00:00
- generated: 2026-10-08T16:49:14.638971+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J3v15r1, qwen3.5:9b, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen3.5-9B@c202236
- judge order: dataset
- judge date: 2026-10-18T15:38:51.449922+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb_p1_g311, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_test3b_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13b_b2_g3_p.gen.jsonl, eval/runs/v13b_b2_g3_p.lg.J3v15r1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.83 | 4.47 | 4.17 | 167 | 3/40 | 6784 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n007 | 0.67 | 4 | 3 | False | 6401 | False | 1800 / 1800 | ok |
| n008 | 1.00 | 5 | 5 | False | 3671 | False | 1591 / 1591 | ok |
| n010 | 1.00 | 5 | 5 | False | 5651 | False | 1789 / 1789 | ok |
| n013 | 1.00 | 5 | 5 | False | 7709 | False | 1560 / 1560 | ok |
| n017 | 1.00 | 5 | 5 | False | 7583 | False | 1849 / 1849 | ok |
| n019 | 1.00 | 2 | 3 | True | 15049 | False | 2244 / 2244 | ok |
| n020 | 1.00 | 5 | 5 | False | 11557 | False | 2023 / 2023 | ok |
| n023 | 1.00 | 4 | 3 | False | 5246 | False | 1566 / 1566 | ok |
| n025 | 1.00 | 5 | 5 | False | 6077 | False | 1803 / 1803 | ok |
| n027 | 1.00 | 5 | 5 | False | 6016 | False | 1542 / 1542 | ok |
| n028 | 1.00 | 5 | 5 | False | 4228 | False | 1710 / 1710 | ok |
| n029 | 1.00 | 5 | 5 | False | 6308 | False | 1770 / 1770 | ok |
| n030 | 1.00 | 5 | 5 | False | 4024 | False | 1601 / 1601 | ok |
| n032 | 1.00 | 5 | 5 | False | 8254 | False | 1684 / 1684 | ok |
| n034 | 1.00 | 5 | 5 | False | 6608 | False | 1555 / 1555 | ok |
| n035 | 1.00 | 5 | 5 | False | 12514 | False | 2225 / 2225 | ok |
| n036 | 0.00 | 4 | 3 | False | 11210 | False | 2080 / 2080 | ok |
| n039 | 0.00 | 5 | 5 | False | 5461 | False | 1712 / 1712 | ok |
| n047 | 1.00 | 5 | 5 | False | 15409 | False | 2412 / 2412 | ok |
| n048 | 1.00 | 5 | 5 | False | 3623 | False | 1576 / 1576 | ok |
| n050 | 1.00 | 4 | 3 | False | 9116 | False | 1776 / 1776 | ok |
| n051 | 0.00 | 4 | 3 | False | 13204 | False | 2006 / 2006 | ok |
| n054 | 1.00 | 5 | 5 | False | 4449 | False | 1576 / 1576 | ok |
| n055 | 1.00 | 5 | 5 | False | 5729 | False | 1742 / 1742 | ok |
| n061 | 1.00 | 4 | 3 | False | 16242 | False | 2104 / 2104 | ok |
| n067 | 1.00 | 4 | 3 | False | 10293 | False | 2056 / 2056 | ok |
| n077 | 0.50 | 5 | 4 | False | 5714 | False | 1761 / 1761 | ok |
| n083 | 1.00 | 4 | 3 | False | 4963 | False | 1722 / 1722 | ok |
| n086 | 0.00 | 2 | 2 | True | 11152 | False | 2173 / 2173 | ok |
| n091 | 1.00 | 5 | 5 | False | 8566 | False | 1942 / 1942 | ok |
| n096 | 1.00 | 2 | 2 | True | 6850 | False | 1714 / 1714 | ok |
| n097 | 1.00 | 5 | 5 | False | 6564 | False | 1957 / 1957 | ok |
| n099 | 0.50 | 4 | 3 | False | 4559 | False | 1857 / 1857 | ok |
| n105 | 1.00 | 5 | 5 | False | 7909 | False | 1945 / 1945 | ok |
| n106 | 0.50 | 5 | 5 | False | 5635 | False | 2047 / 2047 | ok |
| n112 | 1.00 | 5 | 5 | False | 6717 | False | 1912 / 1912 | ok |
| n113 | 1.00 | 5 | 5 | False | 8291 | False | 1866 / 1866 | ok |
| n115 | 0.00 | 4 | 3 | False | 11026 | False | 2210 / 2210 | ok |
| n116 | 1.00 | 4 | 3 | False | 9708 | False | 1790 / 1790 | ok |
| n120 | 1.00 | 4 | 3 | False | 10898 | False | 2183 / 2183 | ok |

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
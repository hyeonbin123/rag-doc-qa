# Answer eval report (v13_adopt_g0_qa_test3b_ko)

- date: 2026-10-08T13:36:42.864934+00:00
- generated: 2026-10-08T13:32:57.106473+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- model digest: 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e
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
- per-item records: eval/runs/v13_adopt_g0_qa_test3b_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.65 | n/a | n/a | n/a | 0/0 | 5005 | 0/40 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n007 | 1.00 | None | None | None | 6664 | False | None / None | - |
| n008 | 1.00 | None | None | None | 4050 | False | None / None | - |
| n010 | 1.00 | None | None | None | 4455 | False | None / None | - |
| n013 | 0.00 | None | None | None | 5115 | False | None / None | - |
| n017 | 1.00 | None | None | None | 8041 | False | None / None | - |
| n019 | 1.00 | None | None | None | 5040 | False | None / None | - |
| n020 | 1.00 | None | None | None | 4533 | False | None / None | - |
| n023 | 1.00 | None | None | None | 4970 | False | None / None | - |
| n025 | 0.50 | None | None | None | 4221 | False | None / None | - |
| n027 | 1.00 | None | None | None | 3935 | False | None / None | - |
| n028 | 1.00 | None | None | None | 4305 | False | None / None | - |
| n029 | 1.00 | None | None | None | 4126 | False | None / None | - |
| n030 | 0.00 | None | None | None | 4780 | False | None / None | - |
| n032 | 0.50 | None | None | None | 5351 | False | None / None | - |
| n034 | 1.00 | None | None | None | 7183 | False | None / None | - |
| n035 | 1.00 | None | None | None | 5554 | False | None / None | - |
| n036 | 0.00 | None | None | None | 4967 | False | None / None | - |
| n039 | 0.00 | None | None | None | 5414 | False | None / None | - |
| n047 | 1.00 | None | None | None | 9216 | False | None / None | - |
| n048 | 1.00 | None | None | None | 4144 | False | None / None | - |
| n050 | 0.50 | None | None | None | 4820 | False | None / None | - |
| n051 | 0.00 | None | None | None | 5914 | False | None / None | - |
| n054 | 1.00 | None | None | None | 5178 | False | None / None | - |
| n055 | 1.00 | None | None | None | 5128 | False | None / None | - |
| n061 | 1.00 | None | None | None | 7505 | False | None / None | - |
| n067 | 1.00 | None | None | None | 4692 | False | None / None | - |
| n077 | 0.00 | None | None | None | 3807 | False | None / None | - |
| n083 | 1.00 | None | None | None | 6042 | False | None / None | - |
| n086 | 0.00 | None | None | None | 5367 | False | None / None | - |
| n091 | 1.00 | None | None | None | 4074 | False | None / None | - |
| n096 | 1.00 | None | None | None | 6110 | False | None / None | - |
| n097 | 0.00 | None | None | None | 5174 | False | None / None | - |
| n099 | 0.50 | None | None | None | 4638 | False | None / None | - |
| n105 | 1.00 | None | None | None | 3983 | False | None / None | - |
| n106 | 0.50 | None | None | None | 4719 | False | None / None | - |
| n112 | 1.00 | None | None | None | 4927 | False | None / None | - |
| n113 | 0.50 | None | None | None | 4648 | False | None / None | - |
| n115 | 0.00 | None | None | None | 5704 | False | None / None | - |
| n116 | 0.00 | None | None | None | 5097 | False | None / None | - |
| n120 | 0.00 | None | None | None | 6081 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **n013** (0.00): 한 엔드포인트에서 경로 파라미터, 쿼리 파라미터, 요청 본문을 같이 받으면 FastAPI는 각각을 어떻게 구분하나요?
  > FastAPI는 각 요청 파라미터를 명확하게 구분합니다. 경로 파라미터는 경로 내의 템플릿 변수로 선언되며, 쿼리 파라미터는 함수의 키워드 인수로 선언되며, 요청 본문은 `Body` 매개변수를 사용하여 선언됩니다. 만약 Pydantic 모델 타입으로 선언되면, 요청 본문으로 해석됩니다.
- **n030** (0.00): Header로 헤더 값을 읽을 때 언더스코어가 하이픈으로 자동 변환된다는 게 무슨 뜻이야?
  > 헤더 이름에 언더스코어가 포함되어 있더라도, FastAPI는 이를 하이픈으로 자동 변환하여 헤더 값을 읽습니다. 예를 들어, `Header` 매개변수로 `save_data`를 선언하면, 실제 HTTP 헤더는 `save-data`가 됩니다.
- **n036** (0.00): RequestValidationError 핸들러를 덮어쓰면서 FastAPI 기본 핸들러 동작도 재사용하는 방법이 있을까?
  > 네, 가능합니다. Starlette의 `HTTPException`을 등록하여 Starlette의 예외를 잡을 수 있으며, 동시에 FastAPI의 기본 예외 핸들러도 재사용할 수 있습니다. 이를 위해 `fastapi.exception_handlers`에서 기본 예외 핸들러를 가져와 사용할 수 있습니다.
- **n039** (0.00): 의존성 안에서 또 다른 의존성을 쓰는 하위 의존성은 어떻게 동작해?
  > 하위 의존성은 선언된 의존성의 반환값을 파라미터로 사용할 수 있습니다. 이 경우, 의존성 함수는 `yield`를 사용하여 실행을 일시 중지하고, 하위 의존성 함수가 실행된 후 다시 실행됩니다. 이렇게 하면 하위 의존성이 먼저 종료되지만, 상위 의존성은 여전히 하위 의존성의 반환값을 사용할 수 있습니다.
- **n051** (0.00): 비활성화된 계정은 로그인돼도 API를 못 쓰게 막고 싶은데 의존성을 어떻게 구성하나요?
  > 의존성을 구성하여 비활성화된 계정은 로그인돼도 API를 못 쓰게 하려면, `current_user` 의존성을 추가하고, 그 안에서 사용자 상태를 확인하여 비활성화된 계정이면 API 호출을 거부하는 로직을 작성하면 됩니다.

```python
from fastapi import Depends, HTTPException, status

async def act
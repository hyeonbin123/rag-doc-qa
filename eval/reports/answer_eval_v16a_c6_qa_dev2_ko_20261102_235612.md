# Answer eval report (v16a_c6_qa_dev2_ko)

- date: 2026-11-02T23:56:12.254604+00:00
- generated: 2026-11-02T23:52:39.449474+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb_v16a, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- corpus: source commit 50113da (277 documents); last fetched 2026-11-02T22:42:36.604069+00:00; chunks en 914, ko 621
- dataset: qa_dev2_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16a_c6_qa_dev2_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.89 | n/a | n/a | n/a | 0/0 | 4899 | 0/40 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n001 | 1.00 | None | None | None | 4942 | False | None / None | - |
| n005 | 1.00 | None | None | None | 5036 | False | None / None | - |
| n006 | 1.00 | None | None | None | 5839 | False | None / None | - |
| n009 | 1.00 | None | None | None | 1356 | False | None / None | - |
| n011 | 1.00 | None | None | None | 1503 | False | None / None | - |
| n012 | 1.00 | None | None | None | 3506 | False | None / None | - |
| n015 | 0.00 | None | None | None | 7000 | False | None / None | - |
| n018 | 1.00 | None | None | None | 6380 | False | None / None | - |
| n031 | 1.00 | None | None | None | 4856 | False | None / None | - |
| n041 | 1.00 | None | None | None | 3578 | False | None / None | - |
| n044 | 1.00 | None | None | None | 6171 | False | None / None | - |
| n049 | 0.50 | None | None | None | 1252 | False | None / None | - |
| n053 | 1.00 | None | None | None | 5539 | False | None / None | - |
| n058 | 1.00 | None | None | None | 3935 | False | None / None | - |
| n059 | 1.00 | None | None | None | 5312 | False | None / None | - |
| n063 | 1.00 | None | None | None | 3689 | False | None / None | - |
| n066 | 1.00 | None | None | None | 2511 | False | None / None | - |
| n068 | 1.00 | None | None | None | 2434 | False | None / None | - |
| n069 | 1.00 | None | None | None | 9458 | False | None / None | - |
| n073 | 1.00 | None | None | None | 6238 | False | None / None | - |
| n074 | 0.50 | None | None | None | 2333 | False | None / None | - |
| n076 | 0.50 | None | None | None | 7447 | False | None / None | - |
| n080 | 1.00 | None | None | None | 7394 | False | None / None | - |
| n084 | 1.00 | None | None | None | 4747 | False | None / None | - |
| n087 | 1.00 | None | None | None | 1924 | False | None / None | - |
| n088 | 1.00 | None | None | None | 5884 | False | None / None | - |
| n089 | 1.00 | None | None | None | 3684 | False | None / None | - |
| n090 | 1.00 | None | None | None | 4070 | False | None / None | - |
| n092 | 1.00 | None | None | None | 6104 | False | None / None | - |
| n094 | 0.50 | None | None | None | 2975 | False | None / None | - |
| n098 | 1.00 | None | None | None | 6098 | False | None / None | - |
| n100 | 1.00 | None | None | None | 6222 | False | None / None | - |
| n102 | 1.00 | None | None | None | 8919 | False | None / None | - |
| n103 | 0.50 | None | None | None | 13062 | False | None / None | - |
| n107 | 1.00 | None | None | None | 3004 | False | None / None | - |
| n110 | 1.00 | None | None | None | 3298 | False | None / None | - |
| n114 | 1.00 | None | None | None | 8437 | False | None / None | - |
| n117 | 0.00 | None | None | None | 2005 | False | None / None | - |
| n118 | 1.00 | None | None | None | 4642 | False | None / None | - |
| n119 | 1.00 | None | None | None | 7933 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **n015** (0.00): 요청 본문에 Pydantic 모델 두 개를 동시에 받을 수 있어?
  > 네, 같은 FastAPI 경로에서 Pydantic v1 모델과 Pydantic v2 모델을 함께 사용할 수 있습니다. 예를 들어, 입력 모델은 Pydantic v1 모델을 사용하고, 출력 모델은 Pydantic v2 모델을 사용하는 방식으로 구성할 수 있습니다.

```python
from fastapi import FastAPI, HTTPException
- **n117** (0.00): 헤더나 쿠키도 Pydantic 모델 하나로 한꺼번에 선언할 수 있을까요?
  > 네, 헤더나 쿠키도 Pydantic 모델로 한꺼번에 선언할 수 있습니다. 관련 있는 헤더나 쿠키 매개변수의 그룹을 Pydantic 모델로 정의하여 여러 위치에서 재사용하고, 유효성 검사 및 메타데이터를 한 번에 선언할 수 있습니다.
- **n049** (0.50): 비밀번호 해싱은 뭘로 해야 돼? passlib, bcrypt, argon2 중에 뭐가 나아?
  > Argon2가 추천됩니다.
- **n074** (0.50): 경로 함수를 async def 말고 그냥 def로 선언하면 스레드풀에서 돌아간다는데 맞습니까?
  > 네, 맞습니다. 경로 함수를 `def`로 선언하면, FastAPI는 해당 함수를 외부 스레드풀에서 실행합니다. 이는 `async def`로 선언된 함수가 코루틴으로 처리되어 비동기적으로 실행되는 것과 대비됩니다. `def`로 선언된 함수는 동기적으로 실행되며, FastAPI는 이를 외부 스레드풀에서 호출하여 병렬 처리를 가능하게 합니다.
- **n076** (0.50): 앱 시작할 때 ML 모델을 메모리에 올리고 종료할 때 정리하려면 lifespan을 어떻게 써야 하나요?
  > ```python
from fastapi import FastAPI
from starlette.lifespan import LifespanManager
import asyncio

app = FastAPI()

# 비동기 컨텍스트 매니저로 정의
@asyncio.coroutine
async def load_models():
    # 모델 로드 시뮬레이션 (
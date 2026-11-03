# Answer eval report (v16b_a_qa_dev2_ko)

- date: 2026-11-03T15:39:51.316398+00:00
- generated: 2026-11-03T15:35:47.432416+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- corpus: source commit 50113da (277 documents); last fetched 2026-11-03T08:04:42.172603+00:00; chunks en 914, ko 621
- dataset: qa_dev2_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_a_qa_dev2_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.88 | n/a | n/a | n/a | 0/0 | 5865 | 0/40 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n001 | 1.00 | None | None | None | 4921 | False | None / None | - |
| n005 | 1.00 | None | None | None | 4994 | False | None / None | - |
| n006 | 1.00 | None | None | None | 6554 | False | None / None | - |
| n009 | 1.00 | None | None | None | 2478 | False | None / None | - |
| n011 | 1.00 | None | None | None | 2602 | False | None / None | - |
| n012 | 1.00 | None | None | None | 4076 | False | None / None | - |
| n015 | 0.00 | None | None | None | 6829 | False | None / None | - |
| n018 | 1.00 | None | None | None | 7765 | False | None / None | - |
| n031 | 1.00 | None | None | None | 5556 | False | None / None | - |
| n041 | 1.00 | None | None | None | 4804 | False | None / None | - |
| n044 | 1.00 | None | None | None | 6145 | False | None / None | - |
| n049 | 0.50 | None | None | None | 2371 | False | None / None | - |
| n053 | 1.00 | None | None | None | 6684 | False | None / None | - |
| n058 | 1.00 | None | None | None | 4338 | False | None / None | - |
| n059 | 1.00 | None | None | None | 5806 | False | None / None | - |
| n063 | 1.00 | None | None | None | 4635 | False | None / None | - |
| n066 | 1.00 | None | None | None | 3641 | False | None / None | - |
| n068 | 1.00 | None | None | None | 2804 | False | None / None | - |
| n069 | 1.00 | None | None | None | 8893 | False | None / None | - |
| n073 | 1.00 | None | None | None | 7972 | False | None / None | - |
| n074 | 0.50 | None | None | None | 3480 | False | None / None | - |
| n076 | 0.50 | None | None | None | 7460 | False | None / None | - |
| n080 | 1.00 | None | None | None | 6954 | False | None / None | - |
| n084 | 1.00 | None | None | None | 5925 | False | None / None | - |
| n087 | 1.00 | None | None | None | 2647 | False | None / None | - |
| n088 | 1.00 | None | None | None | 6956 | False | None / None | - |
| n089 | 1.00 | None | None | None | 4382 | False | None / None | - |
| n090 | 1.00 | None | None | None | 5236 | False | None / None | - |
| n092 | 1.00 | None | None | None | 7275 | False | None / None | - |
| n094 | 0.50 | None | None | None | 8022 | False | None / None | - |
| n098 | 1.00 | None | None | None | 6046 | False | None / None | - |
| n100 | 1.00 | None | None | None | 6156 | False | None / None | - |
| n102 | 0.50 | None | None | None | 10104 | False | None / None | - |
| n103 | 0.50 | None | None | None | 14094 | False | None / None | - |
| n107 | 1.00 | None | None | None | 3062 | False | None / None | - |
| n110 | 1.00 | None | None | None | 4553 | False | None / None | - |
| n114 | 1.00 | None | None | None | 8865 | False | None / None | - |
| n117 | 0.00 | None | None | None | 3194 | False | None / None | - |
| n118 | 1.00 | None | None | None | 6042 | False | None / None | - |
| n119 | 1.00 | None | None | None | 7922 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **n015** (0.00): 요청 본문에 Pydantic 모델 두 개를 동시에 받을 수 있어?
  > 요청 본문에 Pydantic 모델 두 개를 동시에 받는 것은 **FastAPI 0.119.0부터 0.127.x까지**에서만 `fastapi.temp_pydantic_v1_params`를 통해 가능합니다. 그러나 이 기능은 **FastAPI 0.128.0**에서 제거되었으며, 최신 버전에서는 Pydantic v2 모델을 사용해야 합니다.

따라서, **같은 
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
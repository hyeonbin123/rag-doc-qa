# Answer eval report (v14_c4_qa_dev2_ko)

- date: 2026-10-14T04:42:26.598819+00:00
- generated: 2026-10-14T04:36:50.646289+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 1/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb_c4, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_dev2_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v14_c4_qa_dev2_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | n/a | n/a | n/a | 0/0 | 7768 | 0/40 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n001 | 1.00 | None | None | None | 3953 | False | None / None | - |
| n005 | 1.00 | None | None | None | 7687 | False | None / None | - |
| n006 | 1.00 | None | None | None | 9280 | False | None / None | - |
| n009 | 1.00 | None | None | None | 3090 | False | None / None | - |
| n011 | 1.00 | None | None | None | 3729 | False | None / None | - |
| n012 | 1.00 | None | None | None | 3973 | False | None / None | - |
| n015 | 0.00 | None | None | None | 10839 | False | None / None | - |
| n018 | 1.00 | None | None | None | 10172 | False | None / None | - |
| n031 | 1.00 | None | None | None | 7724 | False | None / None | - |
| n041 | 1.00 | None | None | None | 6153 | False | None / None | - |
| n044 | 1.00 | None | None | None | 10486 | False | None / None | - |
| n049 | 0.50 | None | None | None | 3712 | False | None / None | - |
| n053 | 1.00 | None | None | None | 12545 | False | None / None | - |
| n058 | 1.00 | None | None | None | 6483 | False | None / None | - |
| n059 | 1.00 | None | None | None | 7565 | False | None / None | - |
| n063 | 1.00 | None | None | None | 6838 | False | None / None | - |
| n066 | 1.00 | None | None | None | 6030 | False | None / None | - |
| n068 | 1.00 | None | None | None | 3563 | False | None / None | - |
| n069 | 1.00 | None | None | None | 14923 | False | None / None | - |
| n073 | 1.00 | None | None | None | 8070 | False | None / None | - |
| n074 | 0.50 | None | None | None | 3564 | False | None / None | - |
| n076 | 0.50 | None | None | None | 6801 | False | None / None | - |
| n080 | 1.00 | None | None | None | 9366 | False | None / None | - |
| n084 | 1.00 | None | None | None | 7812 | False | None / None | - |
| n087 | 1.00 | None | None | None | 4447 | False | None / None | - |
| n088 | 1.00 | None | None | None | 7864 | False | None / None | - |
| n089 | 1.00 | None | None | None | 12969 | False | None / None | - |
| n090 | 1.00 | None | None | None | 5704 | False | None / None | - |
| n092 | 1.00 | None | None | None | 8171 | False | None / None | - |
| n094 | 0.50 | None | None | None | 11872 | False | None / None | - |
| n098 | 1.00 | None | None | None | 8282 | False | None / None | - |
| n100 | 1.00 | None | None | None | 7251 | False | None / None | - |
| n102 | 1.00 | None | None | None | 13524 | False | None / None | - |
| n103 | 0.50 | None | None | None | 19933 | False | None / None | - |
| n107 | 1.00 | None | None | None | 3269 | False | None / None | - |
| n110 | 1.00 | None | None | None | 4290 | False | None / None | - |
| n114 | 1.00 | None | None | None | 11438 | False | None / None | - |
| n117 | 1.00 | None | None | None | 9593 | False | None / None | - |
| n118 | 1.00 | None | None | None | 8376 | False | None / None | - |
| n119 | 1.00 | None | None | None | 13043 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **n015** (0.00): 요청 본문에 Pydantic 모델 두 개를 동시에 받을 수 있어?
  > 요청 본문에 Pydantic 모델 두 개를 동시에 받는 것은 **같은 경로 처리**에서 가능합니다. 예를 들어, 입력 모델은 Pydantic v1 모델을 사용하고, 출력 모델은 Pydantic v2 모델을 사용하는 방식으로 구현할 수 있습니다.

```python
from fastapi import FastAPI, HTTPException
from pyda
- **n049** (0.50): 비밀번호 해싱은 뭘로 해야 돼? passlib, bcrypt, argon2 중에 뭐가 나아?
  > Argon2가 가장 나은 선택입니다.
- **n074** (0.50): 경로 함수를 async def 말고 그냥 def로 선언하면 스레드풀에서 돌아간다는데 맞습니까?
  > 네, 맞습니다. 경로 함수를 `def`로 선언하면, FastAPI는 해당 함수를 스레드풀에서 실행합니다. 이는 `async def`로 선언된 함수가 비동기적으로 실행되는 것과 대비됩니다. `def`로 선언된 함수는 동기적으로 실행되며, 외부 스레드풀에서 호출됩니다.
- **n076** (0.50): 앱 시작할 때 ML 모델을 메모리에 올리고 종료할 때 정리하려면 lifespan을 어떻게 써야 하나요?
  > ```python
from fastapi import FastAPI
from starlette.lifespan import LifespanManager
import asyncio

app = FastAPI()

# 비동기 컨텍스트 매니저로 정의
@asyncio.coroutine
async def load_models():
    # 모델 로드 로직 (예: 
- **n094** (0.50): WebSocket 연결에서도 Depends나 쿼리 파라미터, 쿠키로 인증할 수 있나요?
  > 네, WebSocket 연결에서도 `Depends`, 쿼리 파라미터, 쿠키로 인증할 수 있습니다.

WebSocket 엔드포인트에서도 `Depends`를 사용하여 인증 토큰을 처리할 수 있으며, 쿼리 파라미터와 쿠키 매개변수를 동일하게 사용할 수 있습니다.

예를 들어, WebSocket 엔드포인트에서 `Depends`를 사용하여 인증 토큰을 처리하는 방법
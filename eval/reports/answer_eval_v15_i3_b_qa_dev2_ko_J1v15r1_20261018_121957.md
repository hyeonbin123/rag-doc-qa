# Answer eval report (v15_i3_b_qa_dev2_ko, judge J1v15r1)

- date: 2026-10-18T12:19:57.733604+00:00
- generated: 2026-10-18T12:07:25.663860+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 1/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J1v15r1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-18T12:18:32.204468+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_dev2_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i3_b_qa_dev2_ko.gen.jsonl, eval/runs/v15_i3_b_qa_dev2_ko.J1v15r1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.89 | 4.38 | 4.78 | 191 | 0/40 | 4079 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n001 | 1.00 | 5 | 5 | False | 3442 | False | 2180 / 2180 | ok |
| n005 | 1.00 | 5 | 5 | False | 3878 | False | 2107 / 2107 | ok |
| n006 | 1.00 | 4 | 4 | False | 5529 | False | 2182 / 2182 | ok |
| n009 | 1.00 | 4 | 5 | False | 1482 | False | 1786 / 1786 | ok |
| n011 | 1.00 | 4 | 5 | False | 1667 | False | 1801 / 1801 | ok |
| n012 | 1.00 | 5 | 5 | False | 2888 | False | 1854 / 1854 | ok |
| n015 | 0.00 | 4 | 4 | False | 4873 | False | 2263 / 2263 | ok |
| n018 | 1.00 | 5 | 5 | False | 6646 | False | 2323 / 2323 | ok |
| n031 | 1.00 | 4 | 4 | False | 3861 | False | 2094 / 2094 | ok |
| n041 | 1.00 | 4 | 5 | False | 3622 | False | 2071 / 2071 | ok |
| n044 | 1.00 | 4 | 5 | False | 4798 | False | 2384 / 2384 | ok |
| n049 | 0.50 | 5 | 5 | False | 1414 | False | 1824 / 1824 | ok |
| n053 | 1.00 | 4 | 4 | False | 5400 | False | 2332 / 2332 | ok |
| n058 | 1.00 | 4 | 5 | False | 3383 | False | 1762 / 1762 | ok |
| n059 | 1.00 | 5 | 5 | False | 4281 | False | 2125 / 2125 | ok |
| n063 | 1.00 | 5 | 5 | False | 3301 | False | 1855 / 1855 | ok |
| n066 | 1.00 | 5 | 5 | False | 2534 | False | 1692 / 1692 | ok |
| n068 | 1.00 | 4 | 5 | False | 1488 | False | 1650 / 1650 | ok |
| n069 | 1.00 | 4 | 5 | False | 8686 | False | 2328 / 2328 | ok |
| n073 | 1.00 | 4 | 5 | False | 4795 | False | 2123 / 2123 | ok |
| n074 | 0.50 | 4 | 5 | False | 2199 | False | 1937 / 1937 | ok |
| n076 | 0.50 | 4 | 5 | False | 6078 | False | 2302 / 2302 | ok |
| n080 | 1.00 | 4 | 4 | False | 5661 | False | 2203 / 2203 | ok |
| n084 | 1.00 | 5 | 5 | False | 4698 | False | 2120 / 2120 | ok |
| n087 | 1.00 | 4 | 5 | False | 1457 | False | 1523 / 1523 | ok |
| n088 | 1.00 | 5 | 5 | False | 4629 | False | 2334 / 2334 | ok |
| n089 | 1.00 | 5 | 5 | False | 2083 | False | 2171 / 2171 | ok |
| n090 | 1.00 | 5 | 5 | False | 3856 | False | 2039 / 2039 | ok |
| n092 | 1.00 | 4 | 5 | False | 6298 | False | 2057 / 2057 | ok |
| n094 | 0.50 | 4 | 5 | False | 3104 | False | 1838 / 1838 | ok |
| n098 | 1.00 | 4 | 5 | False | 4734 | False | 2286 / 2286 | ok |
| n100 | 1.00 | 5 | 5 | False | 5859 | False | 2368 / 2368 | ok |
| n102 | 1.00 | 4 | 4 | False | 5676 | False | 2375 / 2375 | ok |
| n103 | 0.50 | 5 | 5 | False | 14030 | False | 2825 / 2825 | ok |
| n107 | 1.00 | 4 | 4 | False | 2108 | False | 499 / 499 | ok |
| n110 | 1.00 | 4 | 4 | False | 3295 | False | 2165 / 2165 | ok |
| n114 | 1.00 | 4 | 4 | False | 8855 | False | 2314 / 2314 | ok |
| n117 | 0.00 | 4 | 5 | False | 1943 | False | 1993 / 1993 | ok |
| n118 | 1.00 | 5 | 5 | False | 4561 | False | 2314 / 2314 | ok |
| n119 | 1.00 | 4 | 5 | False | 4945 | False | 2558 / 2558 | ok |

## Worst questions (lowest keyword coverage)

- **n015** (0.00): 요청 본문에 Pydantic 모델 두 개를 동시에 받을 수 있어?
  > 요청 본문에 Pydantic 모델 두 개를 동시에 받는 것은 **FastAPI 0.119.0부터 0.127.x까지**에서만 `fastapi.temp_pydantic_v1_params`를 통해 가능합니다. 그러나 이 기능은 **FastAPI 0.128.0**에서 제거되었으며, 최신 버전에서는 Pydantic v2 모델만 지원됩니다.

따라서, **같은 앱에서
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
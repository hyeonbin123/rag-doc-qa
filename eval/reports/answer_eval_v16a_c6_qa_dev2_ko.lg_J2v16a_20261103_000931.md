# Answer eval report (v16a_c6_qa_dev2_ko.lg, judge J2v16a)

- date: 2026-11-03T00:09:31.376032+00:00
- generated: 2026-11-02T23:52:39.449474+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J2v16a, gemma4:12b-it-qat, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: google/gemma-4-12B-it@707f0a3
- judge order: dataset
- judge date: 2026-11-03T00:07:30.840069+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb_v16a, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_dev2_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16a_c6_qa_dev2_ko.gen.jsonl, eval/runs/v16a_c6_qa_dev2_ko.lg.J2v16a.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.89 | 4.50 | 4.28 | 171 | 5/40 | 4899 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n001 | 1.00 | 2 | 2 | True | 4942 | False | 2060 / 2060 | ok |
| n005 | 1.00 | 4 | 4 | False | 5036 | False | 1993 / 1993 | ok |
| n006 | 1.00 | 5 | 5 | False | 5839 | False | 2101 / 2101 | ok |
| n009 | 1.00 | 5 | 5 | False | 1356 | False | 1646 / 1646 | ok |
| n011 | 1.00 | 5 | 5 | False | 1503 | False | 1665 / 1665 | ok |
| n012 | 1.00 | 5 | 5 | False | 3506 | False | 1739 / 1739 | ok |
| n015 | 0.00 | 2 | 1 | True | 7000 | False | 2241 / 2241 | ok |
| n018 | 1.00 | 5 | 5 | False | 6380 | False | 2189 / 2189 | ok |
| n031 | 1.00 | 5 | 5 | False | 4856 | False | 2008 / 2008 | ok |
| n041 | 1.00 | 2 | 1 | True | 3578 | False | 1929 / 1929 | ok |
| n044 | 1.00 | 5 | 5 | False | 6171 | False | 2190 / 2190 | ok |
| n049 | 0.50 | 5 | 5 | False | 1252 | False | 1605 / 1605 | ok |
| n053 | 1.00 | 4 | 3 | False | 5539 | False | 2110 / 2110 | ok |
| n058 | 1.00 | 5 | 5 | False | 3935 | False | 1650 / 1650 | ok |
| n059 | 1.00 | 5 | 5 | False | 5312 | False | 1975 / 1975 | ok |
| n063 | 1.00 | 5 | 4 | False | 3689 | False | 1723 / 1723 | ok |
| n066 | 1.00 | 5 | 5 | False | 2511 | False | 1601 / 1601 | ok |
| n068 | 1.00 | 5 | 5 | False | 2434 | False | 1455 / 1455 | ok |
| n069 | 1.00 | 5 | 4 | False | 9458 | False | 2081 / 2081 | ok |
| n073 | 1.00 | 2 | 2 | True | 6238 | False | 2174 / 2174 | ok |
| n074 | 0.50 | 5 | 5 | False | 2333 | False | 1804 / 1804 | ok |
| n076 | 0.50 | 1 | 1 | True | 7447 | False | 2093 / 2093 | ok |
| n080 | 1.00 | 5 | 5 | False | 7394 | False | 2147 / 2147 | ok |
| n084 | 1.00 | 5 | 5 | False | 4747 | False | 2037 / 2037 | ok |
| n087 | 1.00 | 5 | 5 | False | 1924 | False | 1477 / 1477 | ok |
| n088 | 1.00 | 5 | 5 | False | 5884 | False | 2266 / 2266 | ok |
| n089 | 1.00 | 5 | 5 | False | 3684 | False | 2033 / 2033 | ok |
| n090 | 1.00 | 5 | 5 | False | 4070 | False | 1961 / 1961 | ok |
| n092 | 1.00 | 5 | 5 | False | 6104 | False | 1938 / 1938 | ok |
| n094 | 0.50 | 5 | 4 | False | 2975 | False | 1656 / 1656 | ok |
| n098 | 1.00 | 5 | 5 | False | 6098 | False | 2190 / 2190 | ok |
| n100 | 1.00 | 4 | 3 | False | 6222 | False | 2066 / 2066 | ok |
| n102 | 1.00 | 5 | 5 | False | 8919 | False | 2422 / 2422 | ok |
| n103 | 0.50 | 5 | 4 | False | 13062 | False | 2791 / 2791 | ok |
| n107 | 1.00 | 5 | 5 | False | 3004 | False | 930 / 930 | ok |
| n110 | 1.00 | 5 | 5 | False | 3298 | False | 1965 / 1965 | ok |
| n114 | 1.00 | 4 | 3 | False | 8437 | False | 2261 / 2261 | ok |
| n117 | 0.00 | 5 | 5 | False | 2005 | False | 1806 / 1806 | ok |
| n118 | 1.00 | 5 | 5 | False | 4642 | False | 2107 / 2107 | ok |
| n119 | 1.00 | 5 | 5 | False | 7933 | False | 2485 / 2485 | ok |

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
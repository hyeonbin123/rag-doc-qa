# Answer eval report (v14_c4_qa_dev2_ko.lg, judge J2v15r3)

- date: 2026-10-18T15:28:02.852802+00:00
- generated: 2026-10-14T04:36:50.646289+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 1/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J2v15r3, gemma4:12b-it-qat, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: google/gemma-4-12B-it@707f0a3
- judge order: dataset
- judge date: 2026-10-18T15:25:50.054278+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb_c4, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_dev2_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v14_c4_qa_dev2_ko.gen.jsonl, eval/runs/v14_c4_qa_dev2_ko.lg.J2v15r3.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | 4.50 | 4.40 | 176 | 5/40 | 7768 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n001 | 1.00 | 1 | 1 | True | 3953 | False | 1717 / 1717 | ok |
| n005 | 1.00 | 5 | 5 | False | 7687 | False | 1936 / 1936 | ok |
| n006 | 1.00 | 4 | 4 | False | 9280 | False | 2150 / 2150 | ok |
| n009 | 1.00 | 5 | 5 | False | 3090 | False | 1753 / 1753 | ok |
| n011 | 1.00 | 5 | 5 | False | 3729 | False | 1710 / 1710 | ok |
| n012 | 1.00 | 5 | 5 | False | 3973 | False | 1740 / 1740 | ok |
| n015 | 0.00 | 2 | 2 | True | 10839 | False | 2119 / 2119 | ok |
| n018 | 1.00 | 5 | 5 | False | 10172 | False | 2082 / 2082 | ok |
| n031 | 1.00 | 3 | 2 | False | 7724 | False | 2061 / 2061 | ok |
| n041 | 1.00 | 2 | 1 | True | 6153 | False | 1760 / 1760 | ok |
| n044 | 1.00 | 5 | 5 | False | 10486 | False | 2216 / 2216 | ok |
| n049 | 0.50 | 5 | 5 | False | 3712 | False | 1456 / 1456 | ok |
| n053 | 1.00 | 5 | 5 | False | 12545 | False | 2070 / 2070 | ok |
| n058 | 1.00 | 5 | 5 | False | 6483 | False | 1730 / 1730 | ok |
| n059 | 1.00 | 5 | 5 | False | 7565 | False | 2011 / 2011 | ok |
| n063 | 1.00 | 5 | 4 | False | 6838 | False | 1857 / 1857 | ok |
| n066 | 1.00 | 5 | 5 | False | 6030 | False | 1725 / 1725 | ok |
| n068 | 1.00 | 5 | 5 | False | 3563 | False | 1275 / 1275 | ok |
| n069 | 1.00 | 5 | 5 | False | 14923 | False | 2192 / 2192 | ok |
| n073 | 1.00 | 5 | 5 | False | 8070 | False | 2020 / 2020 | ok |
| n074 | 0.50 | 5 | 5 | False | 3564 | False | 1685 / 1685 | ok |
| n076 | 0.50 | 1 | 1 | True | 6801 | False | 1680 / 1680 | ok |
| n080 | 1.00 | 5 | 5 | False | 9366 | False | 1868 / 1868 | ok |
| n084 | 1.00 | 5 | 5 | False | 7812 | False | 2011 / 2011 | ok |
| n087 | 1.00 | 5 | 5 | False | 4447 | False | 1738 / 1738 | ok |
| n088 | 1.00 | 5 | 5 | False | 7864 | False | 1980 / 1980 | ok |
| n089 | 1.00 | 5 | 5 | False | 12969 | False | 2129 / 2129 | ok |
| n090 | 1.00 | 5 | 5 | False | 5704 | False | 1961 / 1961 | ok |
| n092 | 1.00 | 5 | 5 | False | 8171 | False | 1930 / 1930 | ok |
| n094 | 0.50 | 5 | 5 | False | 11872 | False | 2137 / 2137 | ok |
| n098 | 1.00 | 5 | 5 | False | 8282 | False | 1951 / 1951 | ok |
| n100 | 1.00 | 5 | 5 | False | 7251 | False | 2048 / 2048 | ok |
| n102 | 1.00 | 5 | 5 | False | 13524 | False | 2408 / 2408 | ok |
| n103 | 0.50 | 4 | 4 | False | 19933 | False | 2642 / 2642 | ok |
| n107 | 1.00 | 5 | 5 | False | 3269 | False | 438 / 438 | ok |
| n110 | 1.00 | 5 | 5 | False | 4290 | False | 1744 / 1744 | ok |
| n114 | 1.00 | 3 | 2 | True | 11438 | False | 2256 / 2256 | ok |
| n117 | 1.00 | 5 | 5 | False | 9593 | False | 2057 / 2057 | ok |
| n118 | 1.00 | 5 | 5 | False | 8376 | False | 2156 / 2156 | ok |
| n119 | 1.00 | 5 | 5 | False | 13043 | False | 2400 / 2400 | ok |

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
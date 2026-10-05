# Answer eval report (v13_sel_g3_qa_dev2_ko.raw, judge J1)

- date: 2026-10-05T06:42:29.742713+00:00
- generated: 2026-10-05T06:08:51.432150+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 1/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-05T06:40:19.870151+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'intfloat/multilingual-e5-small'}
- dataset: qa_dev2_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_sel_g3_qa_dev2_ko.gen.jsonl, eval/runs/v13_sel_g3_qa_dev2_ko.raw.J1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.85 | 4.40 | 4.60 | 184 | 1/40 | 10419 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n001 | 1.00 | 4 | 5 | False | 4315 | False | 1679 / 1679 | ok |
| n005 | 1.00 | 5 | 5 | False | 12000 | False | 2239 / 2239 | ok |
| n006 | 1.00 | 5 | 5 | False | 10585 | False | 2189 / 2189 | ok |
| n009 | 1.00 | 3 | 2 | True | 5210 | False | 1932 / 1932 | ok |
| n011 | 1.00 | 4 | 5 | False | 5055 | False | 1912 / 1912 | ok |
| n012 | 1.00 | 5 | 5 | False | 7322 | False | 1808 / 1808 | ok |
| n015 | 0.00 | 4 | 5 | False | 10529 | False | 2180 / 2180 | ok |
| n018 | 0.00 | 4 | 5 | False | 10054 | False | 2151 / 2151 | ok |
| n031 | 1.00 | 4 | 4 | False | 13646 | False | 2147 / 2147 | ok |
| n041 | 1.00 | 4 | 5 | False | 8059 | False | 2056 / 2056 | ok |
| n044 | 1.00 | 5 | 5 | False | 12280 | False | 2422 / 2422 | ok |
| n049 | 0.50 | 5 | 5 | False | 4792 | False | 1888 / 1888 | ok |
| n053 | 1.00 | 4 | 4 | False | 13699 | False | 2379 / 2379 | ok |
| n058 | 1.00 | 5 | 5 | False | 8587 | False | 1954 / 1954 | ok |
| n059 | 1.00 | 5 | 5 | False | 13511 | False | 2368 / 2368 | ok |
| n063 | 1.00 | 5 | 5 | False | 8914 | False | 2070 / 2070 | ok |
| n066 | 1.00 | 4 | 5 | False | 6724 | False | 2020 / 2020 | ok |
| n068 | 1.00 | 4 | 5 | False | 4735 | False | 1659 / 1659 | ok |
| n069 | 0.00 | 4 | 4 | False | 18329 | False | 2578 / 2578 | ok |
| n073 | 1.00 | 4 | 5 | False | 10998 | False | 2262 / 2262 | ok |
| n074 | 0.50 | 5 | 5 | False | 5710 | False | 1812 / 1812 | ok |
| n076 | 0.50 | 4 | 4 | False | 13980 | False | 2280 / 2280 | ok |
| n080 | 1.00 | 4 | 4 | False | 11766 | False | 2082 / 2082 | ok |
| n084 | 1.00 | 5 | 5 | False | 9703 | False | 2141 / 2141 | ok |
| n087 | 1.00 | 4 | 4 | False | 6006 | False | 1918 / 1918 | ok |
| n088 | 1.00 | 4 | 4 | False | 10309 | False | 2337 / 2337 | ok |
| n089 | 0.50 | 5 | 5 | False | 6273 | False | 2097 / 2097 | ok |
| n090 | 1.00 | 4 | 4 | False | 12914 | False | 1892 / 1892 | ok |
| n092 | 1.00 | 5 | 5 | False | 14438 | False | 2113 / 2113 | ok |
| n094 | 1.00 | 5 | 5 | False | 14049 | False | 2421 / 2421 | ok |
| n098 | 1.00 | 5 | 5 | False | 13087 | False | 2215 / 2215 | ok |
| n100 | 1.00 | 4 | 4 | False | 8284 | False | 2181 / 2181 | ok |
| n102 | 1.00 | 5 | 5 | False | 13824 | False | 2446 / 2446 | ok |
| n103 | 0.00 | 4 | 4 | False | 25912 | False | 2791 / 2791 | ok |
| n107 | 1.00 | 4 | 4 | False | 5595 | False | 605 / 605 | ok |
| n110 | 1.00 | 4 | 4 | False | 6656 | False | 2064 / 2064 | ok |
| n114 | 1.00 | 4 | 4 | False | 15866 | False | 2211 / 2211 | ok |
| n117 | 1.00 | 5 | 5 | False | 13650 | False | 2261 / 2261 | ok |
| n118 | 1.00 | 5 | 5 | False | 9912 | False | 2219 / 2219 | ok |
| n119 | 1.00 | 4 | 5 | False | 14531 | False | 2843 / 2843 | ok |

## Worst questions (lowest keyword coverage)

- **n015** (0.00): 요청 본문에 Pydantic 모델 두 개를 동시에 받을 수 있어?
  > 네, 요청 본문에 Pydantic 모델 두 개를 동시에 받을 수 있습니다. FastAPI는 경로 매개변수, 요청 본문, 쿼리 매개변수를 동시에 선언하고 사용할 수 있도록 설계되어 있습니다.

예를 들어, 다음과 같이 두 개의 Pydantic 모델을 요청 본문에 동시에 받을 수 있습니다:

```python
from fastapi import FastAPI,
- **n018** (0.00): Swagger 문서에 요청 바디 예시를 여러 개 보여주고 싶은데 가능할까요?
  > 네, 가능합니다. FastAPI에서 `Body()` 매개변수에 여러 개의 `examples`를 선언하여 Swagger 문서에 여러 요청 바디 예시를 보여줄 수 있습니다.

```python
from fastapi import FastAPI, Body
from pydantic import BaseModel

app = FastAPI()

class Item(
- **n069** (0.00): 테스트용 DB를 운영 DB와 분리해서 쓰고 싶은데 어떻게 구성하는 게 좋을까요?
  > 테스트용 DB를 운영 DB와 분리하려면 다음과 같은 구성을 고려할 수 있습니다:

1. **환경 변수 사용**:
   - `DATABASE_URL` 같은 환경 변수를 사용하여 운영 환경과 테스트 환경의 데이터베이스 연결 문자열을 구분합니다.
   - 예: `.env` 파일에 `DATABASE_URL_PRODUCTION`과 `DATABASE_URL_TEST`
- **n103** (0.00): 인터넷이 안 되는 사내망이라 Swagger UI가 CDN에서 안 불러와져요. 오프라인에서 문서 보는 방법은?
  > 정적 파일을 직접 호스팅하여 오프라인에서도 문서를 볼 수 있도록 설정해야 합니다.

### 1. 정적 파일 테스트용 경로 처리 만들기

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templa
- **n049** (0.50): 비밀번호 해싱은 뭘로 해야 돼? passlib, bcrypt, argon2 중에 뭐가 나아?
  > Argon2가 가장 나아.
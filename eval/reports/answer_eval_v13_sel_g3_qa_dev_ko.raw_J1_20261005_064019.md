# Answer eval report (v13_sel_g3_qa_dev_ko.raw, judge J1)

- date: 2026-10-05T06:40:19.845548+00:00
- generated: 2026-10-05T06:03:31.347046+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 1/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: J1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-05T06:38:37.609144+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'intfloat/multilingual-e5-small'}
- dataset: qa_dev_ko.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_sel_g3_qa_dev_ko.gen.jsonl, eval/runs/v13_sel_g3_qa_dev_ko.raw.J1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.97 | 4.34 | 4.53 | 145 | 0/32 | 8706 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| kd001 | 1.00 | 4 | 5 | False | 8668 | False | 1788 / 1788 | ok |
| kd002 | 1.00 | 5 | 5 | False | 8339 | False | 1951 / 1951 | ok |
| kd003 | 1.00 | 5 | 5 | False | 7293 | False | 1953 / 1953 | ok |
| kd004 | 1.00 | 5 | 5 | False | 8148 | False | 2002 / 2002 | ok |
| kd005 | 1.00 | 4 | 4 | False | 5158 | False | 1765 / 1765 | ok |
| kd006 | 1.00 | 5 | 5 | False | 9233 | False | 2079 / 2079 | ok |
| kd007 | 1.00 | 4 | 4 | False | 23315 | False | 2706 / 2706 | ok |
| kd008 | 1.00 | 4 | 4 | False | 4253 | False | 1640 / 1640 | ok |
| kd009 | 1.00 | 5 | 5 | False | 12468 | False | 2285 / 2285 | ok |
| kd010 | 1.00 | 4 | 5 | False | 4618 | False | 1855 / 1855 | ok |
| kd011 | 1.00 | 4 | 5 | False | 9262 | False | 2015 / 2015 | ok |
| kd012 | 1.00 | 5 | 5 | False | 12423 | False | 2045 / 2045 | ok |
| kd013 | 1.00 | 2 | 1 | False | 4246 | False | 1773 / 1773 | ok |
| kd014 | 1.00 | 4 | 4 | False | 4983 | False | 1761 / 1761 | ok |
| kd015 | 1.00 | 4 | 5 | False | 8744 | False | 2143 / 2143 | ok |
| kd016 | 1.00 | 4 | 5 | False | 9229 | False | 2194 / 2194 | ok |
| kd017 | 1.00 | 5 | 5 | False | 17894 | False | 2710 / 2710 | ok |
| kd018 | 0.00 | 4 | 4 | False | 10467 | False | 2122 / 2122 | ok |
| kd019 | 1.00 | 4 | 4 | False | 12715 | False | 2119 / 2119 | ok |
| kd020 | 1.00 | 5 | 5 | False | 9918 | False | 2129 / 2129 | ok |
| kd021 | 1.00 | 5 | 5 | False | 10738 | False | 2227 / 2227 | ok |
| kd022 | 1.00 | 4 | 4 | False | 6016 | False | 2194 / 2194 | ok |
| kd023 | 1.00 | 4 | 5 | False | 10702 | False | 2254 / 2254 | ok |
| kd024 | 1.00 | 4 | 5 | False | 4778 | False | 1692 / 1692 | ok |
| kd025 | 1.00 | 5 | 5 | False | 7775 | False | 2186 / 2186 | ok |
| kd026 | 1.00 | 5 | 5 | False | 10948 | False | 2377 / 2377 | ok |
| kd027 | 1.00 | 5 | 5 | False | 3582 | False | 1273 / 1273 | ok |
| kd028 | 1.00 | 5 | 5 | False | 5724 | False | 1731 / 1731 | ok |
| kd029 | 1.00 | 3 | 2 | False | 4113 | False | 1956 / 1956 | ok |
| kd030 | 1.00 | 5 | 5 | False | 6962 | False | 1974 / 1974 | ok |
| kd031 | 1.00 | 4 | 4 | False | 10512 | False | 2128 / 2128 | ok |
| kd032 | 1.00 | 4 | 5 | False | 10729 | False | 2157 / 2157 | ok |

## Worst questions (lowest keyword coverage)

- **kd018** (0.00): 경로 처리에서 JSON 대신 HTML 페이지를 반환하려면 어떻게 하나요?
  > 경로 처리에서 JSON 대신 HTML 페이지를 반환하려면, FastAPI의 `Response` 객체를 사용하여 HTML 파일을 직접 반환할 수 있습니다. 예를 들어, 다음과 같이 할 수 있습니다:

```python
from fastapi import FastAPI, Response
import uvicorn

app = FastAPI()

@app.get
- **kd001** (1.00): 경로 처리 함수에서 클라이언트가 보낸 쿠키 값을 읽으려면 어떻게 하나요?
  > 쿠키 값을 읽으려면 `Cookie` 매개변수를 사용해야 합니다. 예를 들어, 다음과 같이 쿠키 값을 선언할 수 있습니다:

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.co
- **kd002** (1.00): FastAPI가 돌려보내는 응답에 쿠키를 설정하려면 어떻게 하나요?
  > `Response` 매개변수를 사용하여 쿠키를 설정할 수 있습니다. 경로 처리 함수에서 `Response` 타입 매개변수를 선언하고, 해당 임시 응답 객체에서 쿠키를 설정한 후 필요한 객체를 반환하면 됩니다.

예시:
```python
from fastapi import FastAPI, Response
app = FastAPI()

@app.get("/se
- **kd003** (1.00): Response 객체를 직접 반환하지 않고 응답에 사용자 정의 헤더를 추가하려면 어떻게 하나요?
  > `Response` 타입의 매개변수를 경로 처리 함수에 선언하고, 해당 객체에서 헤더를 설정할 수 있습니다. 예를 들어, `Response` 매개변수를 사용하여 헤더를 설정하는 방법은 다음과 같습니다:

```python
from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/custom-he
- **kd004** (1.00): 경로 처리가 반환하는 데이터의 타입을 선언해서 FastAPI가 검증하고 걸러 내게 하려면 어떻게 하나요?
  > `response_model` 매개변수를 사용하여 경로 처리 함수의 반환 타입을 선언합니다. 예를 들어, 반환 타입이 `Item`이라는 Pydantic 모델이라면, 다음과 같이 사용할 수 있습니다:

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import 
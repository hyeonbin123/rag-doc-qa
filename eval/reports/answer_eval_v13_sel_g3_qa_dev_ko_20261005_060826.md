# Answer eval report (v13_sel_g3_qa_dev_ko)

- date: 2026-10-05T06:08:26.890630+00:00
- generated: 2026-10-05T06:03:31.347046+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 1/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'intfloat/multilingual-e5-small'}
- dataset: qa_dev_ko.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_sel_g3_qa_dev_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.97 | n/a | n/a | n/a | 0/0 | 8706 | 0/32 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| kd001 | 1.00 | None | None | None | 8668 | False | None / None | - |
| kd002 | 1.00 | None | None | None | 8339 | False | None / None | - |
| kd003 | 1.00 | None | None | None | 7293 | False | None / None | - |
| kd004 | 1.00 | None | None | None | 8148 | False | None / None | - |
| kd005 | 1.00 | None | None | None | 5158 | False | None / None | - |
| kd006 | 1.00 | None | None | None | 9233 | False | None / None | - |
| kd007 | 1.00 | None | None | None | 23315 | False | None / None | - |
| kd008 | 1.00 | None | None | None | 4253 | False | None / None | - |
| kd009 | 1.00 | None | None | None | 12468 | False | None / None | - |
| kd010 | 1.00 | None | None | None | 4618 | False | None / None | - |
| kd011 | 1.00 | None | None | None | 9262 | False | None / None | - |
| kd012 | 1.00 | None | None | None | 12423 | False | None / None | - |
| kd013 | 1.00 | None | None | None | 4246 | False | None / None | - |
| kd014 | 1.00 | None | None | None | 4983 | False | None / None | - |
| kd015 | 1.00 | None | None | None | 8744 | False | None / None | - |
| kd016 | 1.00 | None | None | None | 9229 | False | None / None | - |
| kd017 | 1.00 | None | None | None | 17894 | False | None / None | - |
| kd018 | 0.00 | None | None | None | 10467 | False | None / None | - |
| kd019 | 1.00 | None | None | None | 12715 | False | None / None | - |
| kd020 | 1.00 | None | None | None | 9918 | False | None / None | - |
| kd021 | 1.00 | None | None | None | 10738 | False | None / None | - |
| kd022 | 1.00 | None | None | None | 6016 | False | None / None | - |
| kd023 | 1.00 | None | None | None | 10702 | False | None / None | - |
| kd024 | 1.00 | None | None | None | 4778 | False | None / None | - |
| kd025 | 1.00 | None | None | None | 7775 | False | None / None | - |
| kd026 | 1.00 | None | None | None | 10948 | False | None / None | - |
| kd027 | 1.00 | None | None | None | 3582 | False | None / None | - |
| kd028 | 1.00 | None | None | None | 5724 | False | None / None | - |
| kd029 | 1.00 | None | None | None | 4113 | False | None / None | - |
| kd030 | 1.00 | None | None | None | 6962 | False | None / None | - |
| kd031 | 1.00 | None | None | None | 10512 | False | None / None | - |
| kd032 | 1.00 | None | None | None | 10729 | False | None / None | - |

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
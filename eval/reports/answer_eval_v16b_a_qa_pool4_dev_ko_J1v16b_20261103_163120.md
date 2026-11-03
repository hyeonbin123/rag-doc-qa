# Answer eval report (v16b_a_qa_pool4_dev_ko, judge J1v16b)

- date: 2026-11-03T16:31:20.772204+00:00
- generated: 2026-11-03T15:44:07.517301+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J1v16b, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-11-03T16:30:05.801548+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_pool4_dev_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_a_qa_pool4_dev_ko.gen.jsonl, eval/runs/v16b_a_qa_pool4_dev_ko.J1v16b.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.93 | 4.55 | 4.80 | 192 | 0/40 | 5087 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| k4010 | 1.00 | 5 | 5 | False | 3651 | False | 2052 / 2052 | ok |
| k4011 | 1.00 | 5 | 5 | False | 8220 | False | 3406 / 3406 | ok |
| k4017 | 1.00 | 5 | 5 | False | 5432 | False | 2185 / 2185 | ok |
| k4019 | 1.00 | 4 | 5 | False | 6023 | False | 2264 / 2264 | ok |
| k4020 | 1.00 | 5 | 5 | False | 6137 | False | 2301 / 2301 | ok |
| k4021 | 1.00 | 4 | 4 | False | 7828 | False | 2378 / 2378 | ok |
| k4027 | 1.00 | 5 | 5 | False | 5055 | False | 1790 / 1790 | ok |
| k4032 | 1.00 | 5 | 5 | False | 12716 | False | 3009 / 3009 | ok |
| k4033 | 1.00 | 4 | 5 | False | 2906 | False | 1690 / 1690 | ok |
| k4034 | 1.00 | 4 | 4 | False | 2867 | False | 1907 / 1907 | ok |
| k4037 | 0.50 | 4 | 4 | False | 3425 | False | 2118 / 2118 | ok |
| k4039 | 0.50 | 4 | 5 | False | 4991 | False | 1825 / 1825 | ok |
| k4040 | 1.00 | 5 | 5 | False | 6790 | False | 2298 / 2298 | ok |
| k4041 | 1.00 | 5 | 5 | False | 2836 | False | 1981 / 1981 | ok |
| k4042 | 0.50 | 5 | 5 | False | 3749 | False | 2226 / 2226 | ok |
| k4044 | 1.00 | 4 | 5 | False | 2935 | False | 1975 / 1975 | ok |
| k4048 | 1.00 | 5 | 5 | False | 4830 | False | 1946 / 1946 | ok |
| k4050 | 1.00 | 5 | 5 | False | 5372 | False | 2097 / 2097 | ok |
| k4052 | 1.00 | 5 | 5 | False | 5675 | False | 2249 / 2249 | ok |
| k4053 | 0.67 | 4 | 4 | False | 3719 | False | 1861 / 1861 | ok |
| k4054 | 1.00 | 5 | 5 | False | 5420 | False | 2204 / 2204 | ok |
| k4059 | 1.00 | 4 | 5 | False | 4387 | False | 2204 / 2204 | ok |
| k4060 | 1.00 | 4 | 5 | False | 2877 | False | 1825 / 1825 | ok |
| k4061 | 1.00 | 4 | 5 | False | 5223 | False | 2055 / 2055 | ok |
| k4063 | 1.00 | 4 | 5 | False | 4171 | False | 2135 / 2135 | ok |
| k4065 | 1.00 | 4 | 5 | False | 2711 | False | 1762 / 1762 | ok |
| k4066 | 1.00 | 4 | 4 | False | 4349 | False | 1987 / 1987 | ok |
| k4067 | 1.00 | 5 | 5 | False | 5721 | False | 2098 / 2098 | ok |
| k4072 | 1.00 | 5 | 5 | False | 5513 | False | 2435 / 2435 | ok |
| k4073 | 1.00 | 5 | 5 | False | 8923 | False | 2627 / 2627 | ok |
| k4075 | 1.00 | 4 | 4 | False | 8783 | False | 2673 / 2673 | ok |
| k4076 | 1.00 | 5 | 5 | False | 7401 | False | 2277 / 2277 | ok |
| k4077 | 1.00 | 5 | 5 | False | 5119 | False | 2158 / 2158 | ok |
| k4080 | 1.00 | 5 | 5 | False | 4013 | False | 1993 / 1993 | ok |
| k4085 | 1.00 | 5 | 5 | False | 5121 | False | 2459 / 2459 | ok |
| k4092 | 1.00 | 5 | 5 | False | 7807 | False | 2293 / 2293 | ok |
| k4097 | 0.50 | 3 | 3 | False | 3141 | False | 1956 / 1956 | ok |
| k4107 | 0.33 | 5 | 5 | False | 9475 | False | 2512 / 2512 | ok |
| k4109 | 1.00 | 4 | 5 | False | 3206 | False | 1941 / 1941 | ok |
| k4110 | 1.00 | 5 | 5 | False | 4838 | False | 2059 / 2059 | ok |

## Worst questions (lowest keyword coverage)

- **k4107** (0.33): 엔드포인트에 tags, summary 붙이고 docstring을 마크다운 설명으로 쓰는 방법
  > ```python
from fastapi import FastAPI, APIRouter, HTTPException
from typing import Any, Dict, List, Optional

# 태그 메타데이터 정의
tags_metadata = [
    {
        "name": "users",
        "description": "사용자
- **k4037** (0.50): yield 의존성에서 yield 뒤 코드는 응답 보내기 전에 돌아요, 후에 돌아요? 버전에 따라 바뀌었다는 얘기가 있던데
  > 0.118.0 이전 버전에서는 `yield`가 있는 의존성의 종료 코드가 응답이 네트워크를 통해 전달되기 직전에 실행되었습니다. 그러나 0.118.0에서는 이 동작이 변경되어, `yield` 이후의 종료 코드가 **응답이 전송된 후에** 실행되도록 수정되었습니다.

즉, 0.118.0 이후에는 `yield` 이후의 코드가 **응답이 클라이언트로 전송된 후에
- **k4039** (0.50): 모든 요청의 처리 시간을 X-Process-Time 응답 헤더로 넣어주는 미들웨어 만들고 싶어요
  > ```python
from fastapi import FastAPI, middleware
from fastapi.middleware.base import BaseMiddleware
import time

app = FastAPI()

class ProcessTimeMiddleware(BaseMiddleware):
    def __init__(self, a
- **k4042** (0.50): 운영 환경에선 /docs 를 꺼두고 싶어요. 환경 변수 보고 openapi_url 을 None 으로 주는 방식이면 되나요?
  > 네, 환경 변수를 사용하여 OpenAPI 및 문서 UI를 비활성화하는 방법이 맞습니다.

구체적으로, 환경 변수 `OPENAPI_URL`을 빈 문자열로 설정하면 `openapi_url`이 `None`이 되어 `/docs`와 `/redoc` 등의 URL이 작동하지 않게 됩니다.

예시:
```console
$ OPENAPI_URL= uvicorn main:a
- **k4097** (0.50): Jinja2Templates로 HTML 렌더링할 때 템플릿 안에서 url_for로 static 파일 경로 만드는 법
  > ```jinja
<a href="{{ url_for('static', filename='styles.css') }}">CSS 파일</a>
```
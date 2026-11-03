# Answer eval report (v16b_a_qa_pool4_dev_ko, judge J3v16b)

- date: 2026-11-03T16:46:57.440530+00:00
- generated: 2026-11-03T15:44:07.517301+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J3v16b, qwen3.5:9b, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen3.5-9B@c202236
- judge order: dataset
- judge date: 2026-11-03T16:45:30.601130+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_pool4_dev_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_a_qa_pool4_dev_ko.gen.jsonl, eval/runs/v16b_a_qa_pool4_dev_ko.J3v16b.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.93 | 4.70 | 4.45 | 178 | 2/40 | 5087 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| k4010 | 1.00 | 5 | 5 | False | 3651 | False | 1865 / 1865 | ok |
| k4011 | 1.00 | 5 | 5 | False | 8220 | False | 3220 / 3220 | ok |
| k4017 | 1.00 | 5 | 5 | False | 5432 | False | 1938 / 1938 | ok |
| k4019 | 1.00 | 5 | 5 | False | 6023 | False | 2038 / 2038 | ok |
| k4020 | 1.00 | 5 | 5 | False | 6137 | False | 2058 / 2058 | ok |
| k4021 | 1.00 | 5 | 5 | False | 7828 | False | 2182 / 2182 | ok |
| k4027 | 1.00 | 5 | 5 | False | 5055 | False | 1516 / 1516 | ok |
| k4032 | 1.00 | 4 | 3 | False | 12716 | False | 2772 / 2772 | ok |
| k4033 | 1.00 | 5 | 5 | False | 2906 | False | 1443 / 1443 | ok |
| k4034 | 1.00 | 5 | 5 | False | 2867 | False | 1661 / 1661 | ok |
| k4037 | 0.50 | 5 | 5 | False | 3425 | False | 1797 / 1797 | ok |
| k4039 | 0.50 | 5 | 4 | False | 4991 | False | 1624 / 1624 | ok |
| k4040 | 1.00 | 4 | 3 | False | 6790 | False | 2058 / 2058 | ok |
| k4041 | 1.00 | 5 | 5 | False | 2836 | False | 1666 / 1666 | ok |
| k4042 | 0.50 | 4 | 3 | False | 3749 | False | 1956 / 1956 | ok |
| k4044 | 1.00 | 5 | 4 | False | 2935 | False | 1694 / 1694 | ok |
| k4048 | 1.00 | 5 | 5 | False | 4830 | False | 1689 / 1689 | ok |
| k4050 | 1.00 | 5 | 5 | False | 5372 | False | 1874 / 1874 | ok |
| k4052 | 1.00 | 5 | 5 | False | 5675 | False | 1966 / 1966 | ok |
| k4053 | 0.67 | 5 | 5 | False | 3719 | False | 1634 / 1634 | ok |
| k4054 | 1.00 | 5 | 5 | False | 5420 | False | 1955 / 1955 | ok |
| k4059 | 1.00 | 5 | 5 | False | 4387 | False | 1908 / 1908 | ok |
| k4060 | 1.00 | 5 | 5 | False | 2877 | False | 1555 / 1555 | ok |
| k4061 | 1.00 | 4 | 5 | False | 5223 | False | 1835 / 1835 | ok |
| k4063 | 1.00 | 5 | 5 | False | 4171 | False | 1756 / 1756 | ok |
| k4065 | 1.00 | 5 | 5 | False | 2711 | False | 1495 / 1495 | ok |
| k4066 | 1.00 | 5 | 5 | False | 4349 | False | 1781 / 1781 | ok |
| k4067 | 1.00 | 5 | 5 | False | 5721 | False | 1857 / 1857 | ok |
| k4072 | 1.00 | 4 | 3 | False | 5513 | False | 2168 / 2168 | ok |
| k4073 | 1.00 | 3 | 2 | True | 8923 | False | 2392 / 2392 | ok |
| k4075 | 1.00 | 2 | 1 | True | 8783 | False | 2338 / 2338 | ok |
| k4076 | 1.00 | 5 | 5 | False | 7401 | False | 2000 / 2000 | ok |
| k4077 | 1.00 | 5 | 5 | False | 5119 | False | 1987 / 1987 | ok |
| k4080 | 1.00 | 5 | 5 | False | 4013 | False | 1690 / 1690 | ok |
| k4085 | 1.00 | 5 | 4 | False | 5121 | False | 2087 / 2087 | ok |
| k4092 | 1.00 | 4 | 3 | False | 7807 | False | 2000 / 2000 | ok |
| k4097 | 0.50 | 5 | 5 | False | 3141 | False | 1734 / 1734 | ok |
| k4107 | 0.33 | 4 | 3 | False | 9475 | False | 2222 / 2222 | ok |
| k4109 | 1.00 | 5 | 5 | False | 3206 | False | 1678 / 1678 | ok |
| k4110 | 1.00 | 5 | 5 | False | 4838 | False | 1826 / 1826 | ok |

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
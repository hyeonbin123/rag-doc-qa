# Answer eval report (v16b_b_qa_pool4_dev_ko, judge J1v16b)

- date: 2026-11-03T16:32:08.800008+00:00
- generated: 2026-11-03T15:48:18.284232+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J1v16b, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-11-03T16:31:20.781858+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_pool4_dev_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_b_qa_pool4_dev_ko.gen.jsonl, eval/runs/v16b_b_qa_pool4_dev_ko.J1v16b.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | 4.42 | 4.58 | 183 | 0/40 | 3577 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| k4010 | 1.00 | 5 | 5 | False | 3048 | False | 2052 / 2052 | ok |
| k4011 | 1.00 | 5 | 5 | False | 6819 | False | 3342 / 3342 | ok |
| k4017 | 1.00 | 5 | 5 | False | 3460 | False | 2085 / 2085 | ok |
| k4019 | 1.00 | 4 | 5 | False | 6276 | False | 2346 / 2346 | ok |
| k4020 | 1.00 | 4 | 4 | False | 6593 | False | 2442 / 2442 | ok |
| k4021 | 1.00 | 5 | 5 | False | 8055 | False | 2416 / 2416 | ok |
| k4027 | 1.00 | 5 | 5 | False | 4979 | False | 1796 / 1796 | ok |
| k4032 | 1.00 | 4 | 4 | False | 10412 | False | 2869 / 2869 | ok |
| k4033 | 1.00 | 4 | 5 | False | 2430 | False | 1689 / 1689 | ok |
| k4034 | 1.00 | 4 | 4 | False | 2351 | False | 1908 / 1908 | ok |
| k4037 | 0.50 | 4 | 4 | False | 2537 | False | 2072 / 2072 | ok |
| k4039 | 0.50 | 4 | 4 | False | 6021 | False | 1910 / 1910 | ok |
| k4040 | 1.00 | 4 | 4 | False | 2604 | False | 1967 / 1967 | ok |
| k4041 | 1.00 | 5 | 5 | False | 2280 | False | 1981 / 1981 | ok |
| k4042 | 0.50 | 5 | 5 | False | 3783 | False | 2292 / 2292 | ok |
| k4044 | 1.00 | 4 | 5 | False | 2374 | False | 1978 / 1978 | ok |
| k4048 | 1.00 | 5 | 5 | False | 4089 | False | 1922 / 1922 | ok |
| k4050 | 1.00 | 5 | 5 | False | 2928 | False | 1964 / 1964 | ok |
| k4052 | 1.00 | 5 | 5 | False | 3471 | False | 2096 / 2096 | ok |
| k4053 | 0.67 | 4 | 5 | False | 3101 | False | 1861 / 1861 | ok |
| k4054 | 1.00 | 5 | 5 | False | 4954 | False | 2207 / 2207 | ok |
| k4059 | 1.00 | 5 | 5 | False | 3593 | False | 2193 / 2193 | ok |
| k4060 | 1.00 | 4 | 4 | False | 2472 | False | 1836 / 1836 | ok |
| k4061 | 1.00 | 4 | 4 | False | 3729 | False | 1961 / 1961 | ok |
| k4063 | 0.00 | 3 | 4 | False | 2180 | False | 1978 / 1978 | ok |
| k4065 | 1.00 | 4 | 4 | False | 2203 | False | 1761 / 1761 | ok |
| k4066 | 1.00 | 4 | 4 | False | 3476 | False | 1979 / 1979 | ok |
| k4067 | 1.00 | 5 | 5 | False | 3336 | False | 2003 / 2003 | ok |
| k4072 | 1.00 | 4 | 5 | False | 2865 | False | 2278 / 2278 | ok |
| k4073 | 1.00 | 4 | 4 | False | 8473 | False | 2653 / 2653 | ok |
| k4075 | 1.00 | 4 | 4 | False | 8017 | False | 2653 / 2653 | ok |
| k4076 | 1.00 | 5 | 5 | False | 3218 | False | 1977 / 1977 | ok |
| k4077 | 1.00 | 5 | 5 | False | 3968 | False | 2131 / 2131 | ok |
| k4080 | 1.00 | 5 | 5 | False | 3560 | False | 2004 / 2004 | ok |
| k4085 | 1.00 | 5 | 5 | False | 5161 | False | 2461 / 2461 | ok |
| k4092 | 1.00 | 4 | 4 | False | 7501 | False | 2326 / 2326 | ok |
| k4097 | 0.50 | 3 | 3 | False | 2527 | False | 1951 / 1951 | ok |
| k4107 | 0.67 | 4 | 4 | False | 6717 | False | 2348 / 2348 | ok |
| k4109 | 1.00 | 5 | 5 | False | 5491 | False | 2209 / 2209 | ok |
| k4110 | 1.00 | 5 | 5 | False | 4197 | False | 2033 / 2033 | ok |

## Worst questions (lowest keyword coverage)

- **k4063** (0.00): tiangolo/uvicorn-gunicorn-fastapi 베이스 이미지 아직 써도 되나요? deprecated 됐다는 말이 있던데
  > I don't know: the provided documentation passages do not cover this question.
- **k4037** (0.50): yield 의존성에서 yield 뒤 코드는 응답 보내기 전에 돌아요, 후에 돌아요? 버전에 따라 바뀌었다는 얘기가 있던데
  > 0.118.0 버전 이전에는 `yield`가 있는 의존성의 종료 코드가 응답이 네트워크를 통해 전달되기 직전에 실행되었지만, 0.118.0에서는 이 동작이 변경되어 응답이 전송된 **후에** 실행되도록 수정되었습니다.
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

구체적으로, `OPENAPI_URL` 환경 변수를 빈 문자열로 설정하면 OpenAPI 문서와 관련된 URL (`/openapi.json`, `/docs`, `/redoc`)이 404 오류를 반환하도록 구성할 수 있습니다.

예를 들어:

```console
$ OPEN
- **k4097** (0.50): Jinja2Templates로 HTML 렌더링할 때 템플릿 안에서 url_for로 static 파일 경로 만드는 법
  > ```jinja
<a href="{{ url_for('static', filename='styles.css') }}">
```
# Answer eval report (v16b_b_qa_pool4_dev_ko)

- date: 2026-11-03T15:51:25.455996+00:00
- generated: 2026-11-03T15:48:18.284232+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- corpus: source commit 50113da (277 documents); last fetched 2026-11-03T08:04:42.172603+00:00; chunks en 914, ko 621
- dataset: qa_pool4_dev_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_b_qa_pool4_dev_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | n/a | n/a | n/a | 0/0 | 3577 | 0/40 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| k4010 | 1.00 | None | None | None | 3048 | False | None / None | - |
| k4011 | 1.00 | None | None | None | 6819 | False | None / None | - |
| k4017 | 1.00 | None | None | None | 3460 | False | None / None | - |
| k4019 | 1.00 | None | None | None | 6276 | False | None / None | - |
| k4020 | 1.00 | None | None | None | 6593 | False | None / None | - |
| k4021 | 1.00 | None | None | None | 8055 | False | None / None | - |
| k4027 | 1.00 | None | None | None | 4979 | False | None / None | - |
| k4032 | 1.00 | None | None | None | 10412 | False | None / None | - |
| k4033 | 1.00 | None | None | None | 2430 | False | None / None | - |
| k4034 | 1.00 | None | None | None | 2351 | False | None / None | - |
| k4037 | 0.50 | None | None | None | 2537 | False | None / None | - |
| k4039 | 0.50 | None | None | None | 6021 | False | None / None | - |
| k4040 | 1.00 | None | None | None | 2604 | False | None / None | - |
| k4041 | 1.00 | None | None | None | 2280 | False | None / None | - |
| k4042 | 0.50 | None | None | None | 3783 | False | None / None | - |
| k4044 | 1.00 | None | None | None | 2374 | False | None / None | - |
| k4048 | 1.00 | None | None | None | 4089 | False | None / None | - |
| k4050 | 1.00 | None | None | None | 2928 | False | None / None | - |
| k4052 | 1.00 | None | None | None | 3471 | False | None / None | - |
| k4053 | 0.67 | None | None | None | 3101 | False | None / None | - |
| k4054 | 1.00 | None | None | None | 4954 | False | None / None | - |
| k4059 | 1.00 | None | None | None | 3593 | False | None / None | - |
| k4060 | 1.00 | None | None | None | 2472 | False | None / None | - |
| k4061 | 1.00 | None | None | None | 3729 | False | None / None | - |
| k4063 | 0.00 | None | None | None | 2180 | False | None / None | - |
| k4065 | 1.00 | None | None | None | 2203 | False | None / None | - |
| k4066 | 1.00 | None | None | None | 3476 | False | None / None | - |
| k4067 | 1.00 | None | None | None | 3336 | False | None / None | - |
| k4072 | 1.00 | None | None | None | 2865 | False | None / None | - |
| k4073 | 1.00 | None | None | None | 8473 | False | None / None | - |
| k4075 | 1.00 | None | None | None | 8017 | False | None / None | - |
| k4076 | 1.00 | None | None | None | 3218 | False | None / None | - |
| k4077 | 1.00 | None | None | None | 3968 | False | None / None | - |
| k4080 | 1.00 | None | None | None | 3560 | False | None / None | - |
| k4085 | 1.00 | None | None | None | 5161 | False | None / None | - |
| k4092 | 1.00 | None | None | None | 7501 | False | None / None | - |
| k4097 | 0.50 | None | None | None | 2527 | False | None / None | - |
| k4107 | 0.67 | None | None | None | 6717 | False | None / None | - |
| k4109 | 1.00 | None | None | None | 5491 | False | None / None | - |
| k4110 | 1.00 | None | None | None | 4197 | False | None / None | - |

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
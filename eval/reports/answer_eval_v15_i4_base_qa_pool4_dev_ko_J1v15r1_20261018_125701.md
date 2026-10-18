# Answer eval report (v15_i4_base_qa_pool4_dev_ko, judge J1v15r1)

- date: 2026-10-18T12:57:01.534857+00:00
- generated: 2026-10-18T12:39:53.972290+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J1v15r1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-18T12:55:35.221930+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_pool4_dev_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_base_qa_pool4_dev_ko.gen.jsonl, eval/runs/v15_i4_base_qa_pool4_dev_ko.J1v15r1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.93 | 4.60 | 4.85 | 194 | 0/40 | 5875 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| k4010 | 1.00 | 5 | 5 | False | 4225 | False | 2052 / 2052 | ok |
| k4011 | 1.00 | 5 | 5 | False | 8820 | False | 3406 / 3406 | ok |
| k4017 | 1.00 | 5 | 5 | False | 5864 | False | 2194 / 2194 | ok |
| k4019 | 1.00 | 4 | 5 | False | 6867 | False | 2257 / 2257 | ok |
| k4020 | 1.00 | 5 | 5 | False | 7574 | False | 2358 / 2358 | ok |
| k4021 | 1.00 | 4 | 5 | False | 7411 | False | 2406 / 2406 | ok |
| k4027 | 1.00 | 5 | 5 | False | 5885 | False | 1790 / 1790 | ok |
| k4032 | 1.00 | 5 | 5 | False | 14096 | False | 3009 / 3009 | ok |
| k4033 | 1.00 | 4 | 5 | False | 7468 | False | 2047 / 2047 | ok |
| k4034 | 1.00 | 5 | 5 | False | 3339 | False | 1907 / 1907 | ok |
| k4037 | 0.50 | 4 | 4 | False | 4050 | False | 2118 / 2118 | ok |
| k4039 | 0.50 | 4 | 5 | False | 5535 | False | 1811 / 1811 | ok |
| k4040 | 1.00 | 4 | 4 | False | 7203 | False | 2240 / 2240 | ok |
| k4041 | 1.00 | 5 | 5 | False | 3378 | False | 1981 / 1981 | ok |
| k4042 | 0.50 | 4 | 5 | False | 4538 | False | 2273 / 2273 | ok |
| k4044 | 1.00 | 4 | 5 | False | 3493 | False | 1975 / 1975 | ok |
| k4048 | 1.00 | 5 | 5 | False | 5580 | False | 1946 / 1946 | ok |
| k4050 | 1.00 | 5 | 5 | False | 6296 | False | 2113 / 2113 | ok |
| k4052 | 1.00 | 5 | 5 | False | 6470 | False | 2249 / 2249 | ok |
| k4053 | 0.67 | 4 | 4 | False | 4416 | False | 1866 / 1866 | ok |
| k4054 | 1.00 | 5 | 5 | False | 6126 | False | 2204 / 2204 | ok |
| k4059 | 1.00 | 4 | 5 | False | 4987 | False | 2204 / 2204 | ok |
| k4060 | 1.00 | 4 | 5 | False | 3354 | False | 1825 / 1825 | ok |
| k4061 | 1.00 | 5 | 5 | False | 5703 | False | 2114 / 2114 | ok |
| k4063 | 1.00 | 4 | 5 | False | 4837 | False | 2135 / 2135 | ok |
| k4065 | 1.00 | 4 | 5 | False | 3310 | False | 1762 / 1762 | ok |
| k4066 | 1.00 | 4 | 4 | False | 4987 | False | 1987 / 1987 | ok |
| k4067 | 1.00 | 5 | 5 | False | 6390 | False | 2098 / 2098 | ok |
| k4072 | 1.00 | 5 | 5 | False | 6200 | False | 2432 / 2432 | ok |
| k4073 | 1.00 | 5 | 5 | False | 9641 | False | 2627 / 2627 | ok |
| k4075 | 1.00 | 4 | 4 | False | 9490 | False | 2673 / 2673 | ok |
| k4076 | 1.00 | 5 | 5 | False | 7975 | False | 2241 / 2241 | ok |
| k4077 | 1.00 | 5 | 5 | False | 6671 | False | 2222 / 2222 | ok |
| k4080 | 1.00 | 5 | 5 | False | 4819 | False | 1993 / 1993 | ok |
| k4085 | 1.00 | 5 | 5 | False | 5009 | False | 2356 / 2356 | ok |
| k4092 | 1.00 | 5 | 5 | False | 8897 | False | 2293 / 2293 | ok |
| k4097 | 0.50 | 4 | 4 | False | 3774 | False | 1939 / 1939 | ok |
| k4107 | 0.67 | 5 | 5 | False | 9863 | False | 2466 / 2466 | ok |
| k4109 | 1.00 | 5 | 5 | False | 6938 | False | 2219 / 2219 | ok |
| k4110 | 1.00 | 5 | 5 | False | 5471 | False | 2059 / 2059 | ok |

## Worst questions (lowest keyword coverage)

- **k4037** (0.50): yield 의존성에서 yield 뒤 코드는 응답 보내기 전에 돌아요, 후에 돌아요? 버전에 따라 바뀌었다는 얘기가 있던데
  > 0.118.0 버전 이전에는 `yield`가 있는 의존성의 종료 코드가 응답이 네트워크를 통해 전달되기 직전에 실행되었습니다. 하지만 0.118.0에서는 이 동작이 변경되어, `yield` 이후의 종료 코드가 **응답이 전송된 후에** 실행되도록 수정되었습니다.

즉, 0.118.0 이후에는 `yield` 이후의 코드가 **응답이 클라이언트로 전송된 후에*
- **k4039** (0.50): 모든 요청의 처리 시간을 X-Process-Time 응답 헤더로 넣어주는 미들웨어 만들고 싶어요
  > ```python
from fastapi import FastAPI, middleware
from fastapi.middleware.base import BaseMiddleware
import time

app = FastAPI()

class ProcessTimeMiddleware(BaseMiddleware):
    def __init__(self, a
- **k4042** (0.50): 운영 환경에선 /docs 를 꺼두고 싶어요. 환경 변수 보고 openapi_url 을 None 으로 주는 방식이면 되나요?
  > 네, 맞습니다. 운영 환경에서 `/docs`를 비활성화하려면 환경 변수를 사용하여 `openapi_url`을 빈 문자열로 설정하면 됩니다.

```console
$ OPENAPI_URL= uvicorn main:app
```

이렇게 하면 `/openapi.json`, `/docs`, `/redoc` 등의 URL로 접근했을 때 `404 Not Found` 
- **k4097** (0.50): Jinja2Templates로 HTML 렌더링할 때 템플릿 안에서 url_for로 static 파일 경로 만드는 법
  > ```jinja
<a href="{{ url_for('static', filename='styles.css') }}">
```
- **k4053** (0.67): 파일 다운로드 엔드포인트에서 FileResponse로 filename 지정해서 내려주는 방법 알려주세요
  > ```python
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from typing import List

app = FastAPI()

@app.get("/download")
async def download_file(file: UploadF
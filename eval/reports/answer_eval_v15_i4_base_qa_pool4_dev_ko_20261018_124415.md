# Answer eval report (v15_i4_base_qa_pool4_dev_ko)

- date: 2026-10-18T12:44:15.599170+00:00
- generated: 2026-10-18T12:39:53.972290+00:00
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
- dataset: qa_pool4_dev_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_base_qa_pool4_dev_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.93 | n/a | n/a | n/a | 0/0 | 5875 | 0/40 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| k4010 | 1.00 | None | None | None | 4225 | False | None / None | - |
| k4011 | 1.00 | None | None | None | 8820 | False | None / None | - |
| k4017 | 1.00 | None | None | None | 5864 | False | None / None | - |
| k4019 | 1.00 | None | None | None | 6867 | False | None / None | - |
| k4020 | 1.00 | None | None | None | 7574 | False | None / None | - |
| k4021 | 1.00 | None | None | None | 7411 | False | None / None | - |
| k4027 | 1.00 | None | None | None | 5885 | False | None / None | - |
| k4032 | 1.00 | None | None | None | 14096 | False | None / None | - |
| k4033 | 1.00 | None | None | None | 7468 | False | None / None | - |
| k4034 | 1.00 | None | None | None | 3339 | False | None / None | - |
| k4037 | 0.50 | None | None | None | 4050 | False | None / None | - |
| k4039 | 0.50 | None | None | None | 5535 | False | None / None | - |
| k4040 | 1.00 | None | None | None | 7203 | False | None / None | - |
| k4041 | 1.00 | None | None | None | 3378 | False | None / None | - |
| k4042 | 0.50 | None | None | None | 4538 | False | None / None | - |
| k4044 | 1.00 | None | None | None | 3493 | False | None / None | - |
| k4048 | 1.00 | None | None | None | 5580 | False | None / None | - |
| k4050 | 1.00 | None | None | None | 6296 | False | None / None | - |
| k4052 | 1.00 | None | None | None | 6470 | False | None / None | - |
| k4053 | 0.67 | None | None | None | 4416 | False | None / None | - |
| k4054 | 1.00 | None | None | None | 6126 | False | None / None | - |
| k4059 | 1.00 | None | None | None | 4987 | False | None / None | - |
| k4060 | 1.00 | None | None | None | 3354 | False | None / None | - |
| k4061 | 1.00 | None | None | None | 5703 | False | None / None | - |
| k4063 | 1.00 | None | None | None | 4837 | False | None / None | - |
| k4065 | 1.00 | None | None | None | 3310 | False | None / None | - |
| k4066 | 1.00 | None | None | None | 4987 | False | None / None | - |
| k4067 | 1.00 | None | None | None | 6390 | False | None / None | - |
| k4072 | 1.00 | None | None | None | 6200 | False | None / None | - |
| k4073 | 1.00 | None | None | None | 9641 | False | None / None | - |
| k4075 | 1.00 | None | None | None | 9490 | False | None / None | - |
| k4076 | 1.00 | None | None | None | 7975 | False | None / None | - |
| k4077 | 1.00 | None | None | None | 6671 | False | None / None | - |
| k4080 | 1.00 | None | None | None | 4819 | False | None / None | - |
| k4085 | 1.00 | None | None | None | 5009 | False | None / None | - |
| k4092 | 1.00 | None | None | None | 8897 | False | None / None | - |
| k4097 | 0.50 | None | None | None | 3774 | False | None / None | - |
| k4107 | 0.67 | None | None | None | 9863 | False | None / None | - |
| k4109 | 1.00 | None | None | None | 6938 | False | None / None | - |
| k4110 | 1.00 | None | None | None | 5471 | False | None / None | - |

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
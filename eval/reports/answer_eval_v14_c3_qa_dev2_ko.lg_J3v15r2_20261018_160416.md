# Answer eval report (v14_c3_qa_dev2_ko.lg, judge J3v15r2)

- date: 2026-10-18T16:04:16.225025+00:00
- generated: 2026-10-14T04:30:58.320696+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J3v15r2, qwen3.5:9b, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen3.5-9B@c202236
- judge order: dataset
- judge date: 2026-10-18T16:02:38.762828+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_dev2_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v14_c3_qa_dev2_ko.gen.jsonl, eval/runs/v14_c3_qa_dev2_ko.lg.J3v15r2.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.88 | 4.47 | 4.20 | 168 | 4/40 | 8017 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n001 | 1.00 | 5 | 5 | False | 6482 | False | 1935 / 1935 | ok |
| n005 | 1.00 | 5 | 5 | False | 8006 | False | 1941 / 1941 | ok |
| n006 | 1.00 | 4 | 3 | False | 8936 | False | 1985 / 1985 | ok |
| n009 | 1.00 | 5 | 5 | False | 3676 | False | 1556 / 1556 | ok |
| n011 | 1.00 | 5 | 5 | False | 3786 | False | 1603 / 1603 | ok |
| n012 | 1.00 | 5 | 5 | False | 5445 | False | 1651 / 1651 | ok |
| n015 | 0.00 | 2 | 2 | True | 7404 | False | 1937 / 1937 | ok |
| n018 | 1.00 | 5 | 5 | False | 10374 | False | 2143 / 2143 | ok |
| n031 | 1.00 | 4 | 3 | False | 5844 | False | 1846 / 1846 | ok |
| n041 | 1.00 | 2 | 3 | True | 6717 | False | 1853 / 1853 | ok |
| n044 | 1.00 | 5 | 5 | False | 9905 | False | 2133 / 2133 | ok |
| n049 | 0.50 | 5 | 4 | False | 3403 | False | 1528 / 1528 | ok |
| n053 | 1.00 | 5 | 4 | False | 9294 | False | 1959 / 1959 | ok |
| n058 | 1.00 | 5 | 5 | False | 6371 | False | 1604 / 1604 | ok |
| n059 | 1.00 | 5 | 5 | False | 8102 | False | 1833 / 1833 | ok |
| n063 | 1.00 | 5 | 5 | False | 6456 | False | 1601 / 1601 | ok |
| n066 | 1.00 | 5 | 5 | False | 5029 | False | 1506 / 1506 | ok |
| n068 | 1.00 | 5 | 5 | False | 3735 | False | 1424 / 1424 | ok |
| n069 | 1.00 | 4 | 3 | False | 12725 | False | 1958 / 1958 | ok |
| n073 | 1.00 | 2 | 3 | True | 8994 | False | 1822 / 1822 | ok |
| n074 | 0.50 | 4 | 3 | False | 4794 | False | 1694 / 1694 | ok |
| n076 | 0.50 | 2 | 1 | True | 8819 | False | 1904 / 1904 | ok |
| n080 | 1.00 | 4 | 3 | False | 9485 | False | 1938 / 1938 | ok |
| n084 | 1.00 | 5 | 5 | False | 8175 | False | 1835 / 1835 | ok |
| n087 | 1.00 | 5 | 5 | False | 3629 | False | 1297 / 1297 | ok |
| n088 | 1.00 | 5 | 5 | False | 8027 | False | 2096 / 2096 | ok |
| n089 | 1.00 | 5 | 5 | False | 4913 | False | 1833 / 1833 | ok |
| n090 | 1.00 | 5 | 5 | False | 7097 | False | 1784 / 1784 | ok |
| n092 | 1.00 | 5 | 5 | False | 9746 | False | 1820 / 1820 | ok |
| n094 | 0.50 | 5 | 5 | False | 10837 | False | 1888 / 1888 | ok |
| n098 | 1.00 | 5 | 5 | False | 8059 | False | 2043 / 2043 | ok |
| n100 | 1.00 | 5 | 5 | False | 10897 | False | 2170 / 2170 | ok |
| n102 | 1.00 | 4 | 3 | False | 14900 | False | 2431 / 2431 | ok |
| n103 | 0.00 | 4 | 3 | False | 14660 | False | 2317 / 2317 | ok |
| n107 | 1.00 | 5 | 4 | False | 3592 | False | 428 / 428 | ok |
| n110 | 1.00 | 5 | 5 | False | 6401 | False | 1838 / 1838 | ok |
| n114 | 1.00 | 4 | 3 | False | 12108 | False | 2056 / 2056 | ok |
| n117 | 0.00 | 5 | 5 | False | 4551 | False | 1737 / 1737 | ok |
| n118 | 1.00 | 5 | 5 | False | 8167 | False | 2016 / 2016 | ok |
| n119 | 1.00 | 4 | 3 | False | 9683 | False | 2269 / 2269 | ok |

## Worst questions (lowest keyword coverage)

- **n015** (0.00): 요청 본문에 Pydantic 모델 두 개를 동시에 받을 수 있어?
  > 요청 본문에 Pydantic 모델 두 개를 동시에 받는 것은 **FastAPI 0.119.0부터 0.127.x까지**에서만 `fastapi.temp_pydantic_v1_params`를 통해 가능합니다. 그러나 이 기능은 **FastAPI 0.128.0**에서 제거되었으며, 최신 버전에서는 Pydantic v2 모델만 지원됩니다.

따라서, **같은 앱에서
- **n103** (0.00): 인터넷이 안 되는 사내망이라 Swagger UI가 CDN에서 안 불러와져요. 오프라인에서 문서 보는 방법은?
  > 인터넷이 없는 사내망에서도 Swagger UI와 ReDoc 문서를 오프라인으로 보려면, 다음 단계를 따라 정적 파일을 직접 호스팅해야 합니다:

1. **Swagger UI와 ReDoc의 정적 파일 다운로드**:
   - [Swagger UI](https://github.com/swagger-api/swagger-ui)와 [ReDoc](https://git
- **n117** (0.00): 헤더나 쿠키도 Pydantic 모델 하나로 한꺼번에 선언할 수 있을까요?
  > 네, 헤더나 쿠키도 Pydantic 모델로 한꺼번에 선언할 수 있습니다. 관련 있는 헤더나 쿠키 매개변수의 그룹을 Pydantic 모델로 정의하여 여러 위치에서 재사용하고, 유효성 검사 및 메타데이터를 한 번에 선언할 수 있습니다.
- **n049** (0.50): 비밀번호 해싱은 뭘로 해야 돼? passlib, bcrypt, argon2 중에 뭐가 나아?
  > Argon2가 추천됩니다.
- **n074** (0.50): 경로 함수를 async def 말고 그냥 def로 선언하면 스레드풀에서 돌아간다는데 맞습니까?
  > 네, 맞습니다. 경로 함수를 `def`로 선언하면, FastAPI는 해당 함수를 외부 스레드풀에서 실행합니다. 이는 `async def`로 선언된 함수가 코루틴으로 처리되어 비동기적으로 실행되는 것과 대비됩니다. `def`로 선언된 함수는 동기적으로 실행되며, FastAPI는 이를 외부 스레드풀에서 호출하여 병렬 처리를 가능하게 합니다.
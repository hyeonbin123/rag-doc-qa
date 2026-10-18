# Answer eval report (v14_c3_qa_dev2_ko.lg, judge J1v15r1)

- date: 2026-10-18T16:42:31.870726+00:00
- generated: 2026-10-14T04:30:58.320696+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J1v15r1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-18T16:41:06.770734+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_dev2_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v14_c3_qa_dev2_ko.gen.jsonl, eval/runs/v14_c3_qa_dev2_ko.lg.J1v15r1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.88 | 4.40 | 4.80 | 192 | 0/40 | 8017 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n001 | 1.00 | 5 | 5 | False | 6482 | False | 2180 / 2180 | ok |
| n005 | 1.00 | 5 | 5 | False | 8006 | False | 2171 / 2171 | ok |
| n006 | 1.00 | 4 | 4 | False | 8936 | False | 2186 / 2186 | ok |
| n009 | 1.00 | 4 | 5 | False | 3676 | False | 1786 / 1786 | ok |
| n011 | 1.00 | 4 | 5 | False | 3786 | False | 1801 / 1801 | ok |
| n012 | 1.00 | 5 | 5 | False | 5445 | False | 1854 / 1854 | ok |
| n015 | 0.00 | 4 | 4 | False | 7404 | False | 2216 / 2216 | ok |
| n018 | 1.00 | 5 | 5 | False | 10374 | False | 2323 / 2323 | ok |
| n031 | 1.00 | 4 | 4 | False | 5844 | False | 2057 / 2057 | ok |
| n041 | 1.00 | 4 | 5 | False | 6717 | False | 2073 / 2073 | ok |
| n044 | 1.00 | 4 | 5 | False | 9905 | False | 2463 / 2463 | ok |
| n049 | 0.50 | 5 | 5 | False | 3403 | False | 1824 / 1824 | ok |
| n053 | 1.00 | 4 | 4 | False | 9294 | False | 2333 / 2333 | ok |
| n058 | 1.00 | 4 | 5 | False | 6371 | False | 1762 / 1762 | ok |
| n059 | 1.00 | 5 | 5 | False | 8102 | False | 2127 / 2127 | ok |
| n063 | 1.00 | 5 | 5 | False | 6456 | False | 1851 / 1851 | ok |
| n066 | 1.00 | 5 | 5 | False | 5029 | False | 1692 / 1692 | ok |
| n068 | 1.00 | 4 | 5 | False | 3735 | False | 1650 / 1650 | ok |
| n069 | 1.00 | 4 | 5 | False | 12725 | False | 2307 / 2307 | ok |
| n073 | 1.00 | 4 | 5 | False | 8994 | False | 2126 / 2126 | ok |
| n074 | 0.50 | 4 | 5 | False | 4794 | False | 1937 / 1937 | ok |
| n076 | 0.50 | 4 | 5 | False | 8819 | False | 2181 / 2181 | ok |
| n080 | 1.00 | 4 | 4 | False | 9485 | False | 2203 / 2203 | ok |
| n084 | 1.00 | 5 | 5 | False | 8175 | False | 2106 / 2106 | ok |
| n087 | 1.00 | 4 | 5 | False | 3629 | False | 1523 / 1523 | ok |
| n088 | 1.00 | 5 | 5 | False | 8027 | False | 2317 / 2317 | ok |
| n089 | 1.00 | 5 | 5 | False | 4913 | False | 2171 / 2171 | ok |
| n090 | 1.00 | 5 | 5 | False | 7097 | False | 2039 / 2039 | ok |
| n092 | 1.00 | 4 | 5 | False | 9746 | False | 2057 / 2057 | ok |
| n094 | 0.50 | 4 | 4 | False | 10837 | False | 2130 / 2130 | ok |
| n098 | 1.00 | 4 | 5 | False | 8059 | False | 2287 / 2287 | ok |
| n100 | 1.00 | 5 | 5 | False | 10897 | False | 2442 / 2442 | ok |
| n102 | 1.00 | 5 | 5 | False | 14900 | False | 2690 / 2690 | ok |
| n103 | 0.00 | 5 | 5 | False | 14660 | False | 2599 / 2599 | ok |
| n107 | 1.00 | 4 | 4 | False | 3592 | False | 499 / 499 | ok |
| n110 | 1.00 | 4 | 5 | False | 6401 | False | 2167 / 2167 | ok |
| n114 | 1.00 | 4 | 4 | False | 12108 | False | 2289 / 2289 | ok |
| n117 | 0.00 | 4 | 5 | False | 4551 | False | 1993 / 1993 | ok |
| n118 | 1.00 | 5 | 5 | False | 8167 | False | 2318 / 2318 | ok |
| n119 | 1.00 | 4 | 5 | False | 9683 | False | 2627 / 2627 | ok |

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
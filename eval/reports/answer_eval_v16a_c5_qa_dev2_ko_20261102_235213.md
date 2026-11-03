# Answer eval report (v16a_c5_qa_dev2_ko)

- date: 2026-11-02T23:52:13.335340+00:00
- generated: 2026-11-02T23:48:13.711377+00:00
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
- corpus: source commit 50113da (277 documents); last fetched 2026-10-09T02:59:20.705331+00:00; chunks en 914, ko 621
- dataset: qa_dev2_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16a_c5_qa_dev2_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.88 | n/a | n/a | n/a | 0/0 | 5785 | 0/40 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n001 | 1.00 | None | None | None | 4921 | False | None / None | - |
| n005 | 1.00 | None | None | None | 5794 | False | None / None | - |
| n006 | 1.00 | None | None | None | 6569 | False | None / None | - |
| n009 | 1.00 | None | None | None | 2359 | False | None / None | - |
| n011 | 1.00 | None | None | None | 2631 | False | None / None | - |
| n012 | 1.00 | None | None | None | 3943 | False | None / None | - |
| n015 | 0.00 | None | None | None | 5393 | False | None / None | - |
| n018 | 1.00 | None | None | None | 7751 | False | None / None | - |
| n031 | 1.00 | None | None | None | 4489 | False | None / None | - |
| n041 | 1.00 | None | None | None | 4851 | False | None / None | - |
| n044 | 1.00 | None | None | None | 7242 | False | None / None | - |
| n049 | 0.50 | None | None | None | 2412 | False | None / None | - |
| n053 | 1.00 | None | None | None | 6725 | False | None / None | - |
| n058 | 1.00 | None | None | None | 4623 | False | None / None | - |
| n059 | 1.00 | None | None | None | 6080 | False | None / None | - |
| n063 | 1.00 | None | None | None | 4674 | False | None / None | - |
| n066 | 1.00 | None | None | None | 3601 | False | None / None | - |
| n068 | 1.00 | None | None | None | 2645 | False | None / None | - |
| n069 | 1.00 | None | None | None | 9586 | False | None / None | - |
| n073 | 1.00 | None | None | None | 6615 | False | None / None | - |
| n074 | 0.50 | None | None | None | 3520 | False | None / None | - |
| n076 | 0.50 | None | None | None | 6307 | False | None / None | - |
| n080 | 1.00 | None | None | None | 6814 | False | None / None | - |
| n084 | 1.00 | None | None | None | 5935 | False | None / None | - |
| n087 | 1.00 | None | None | None | 2526 | False | None / None | - |
| n088 | 1.00 | None | None | None | 5931 | False | None / None | - |
| n089 | 1.00 | None | None | None | 3501 | False | None / None | - |
| n090 | 1.00 | None | None | None | 5246 | False | None / None | - |
| n092 | 1.00 | None | None | None | 7283 | False | None / None | - |
| n094 | 0.50 | None | None | None | 8029 | False | None / None | - |
| n098 | 1.00 | None | None | None | 5956 | False | None / None | - |
| n100 | 1.00 | None | None | None | 8222 | False | None / None | - |
| n102 | 1.00 | None | None | None | 10824 | False | None / None | - |
| n103 | 0.00 | None | None | None | 10648 | False | None / None | - |
| n107 | 1.00 | None | None | None | 2528 | False | None / None | - |
| n110 | 1.00 | None | None | None | 4539 | False | None / None | - |
| n114 | 1.00 | None | None | None | 8861 | False | None / None | - |
| n117 | 0.00 | None | None | None | 3204 | False | None / None | - |
| n118 | 1.00 | None | None | None | 5776 | False | None / None | - |
| n119 | 1.00 | None | None | None | 7308 | False | None / None | - |

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
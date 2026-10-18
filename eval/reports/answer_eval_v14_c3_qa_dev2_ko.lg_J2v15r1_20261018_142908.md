# Answer eval report (v14_c3_qa_dev2_ko.lg, judge J2v15r1)

- date: 2026-10-18T14:29:08.384797+00:00
- generated: 2026-10-14T04:30:58.320696+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J2v15r1, gemma4:12b-it-qat, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: google/gemma-4-12B-it@707f0a3
- judge order: dataset
- judge date: 2026-10-18T14:26:54.520483+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_dev2_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v14_c3_qa_dev2_ko.gen.jsonl, eval/runs/v14_c3_qa_dev2_ko.lg.J2v15r1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.88 | 4.53 | 4.35 | 174 | 5/40 | 8017 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n001 | 1.00 | 2 | 2 | True | 6482 | False | 2060 / 2060 | ok |
| n005 | 1.00 | 5 | 5 | False | 8006 | False | 2065 / 2065 | ok |
| n006 | 1.00 | 5 | 5 | False | 8936 | False | 2101 / 2101 | ok |
| n009 | 1.00 | 5 | 5 | False | 3676 | False | 1646 / 1646 | ok |
| n011 | 1.00 | 5 | 5 | False | 3786 | False | 1665 / 1665 | ok |
| n012 | 1.00 | 5 | 5 | False | 5445 | False | 1740 / 1740 | ok |
| n015 | 0.00 | 2 | 1 | True | 7404 | False | 2072 / 2072 | ok |
| n018 | 1.00 | 5 | 5 | False | 10374 | False | 2189 / 2189 | ok |
| n031 | 1.00 | 5 | 5 | False | 5844 | False | 1953 / 1953 | ok |
| n041 | 1.00 | 2 | 1 | True | 6717 | False | 1929 / 1929 | ok |
| n044 | 1.00 | 5 | 5 | False | 9905 | False | 2260 / 2260 | ok |
| n049 | 0.50 | 5 | 5 | False | 3403 | False | 1605 / 1605 | ok |
| n053 | 1.00 | 4 | 3 | False | 9294 | False | 2111 / 2111 | ok |
| n058 | 1.00 | 5 | 5 | False | 6371 | False | 1694 / 1694 | ok |
| n059 | 1.00 | 5 | 5 | False | 8102 | False | 1983 / 1983 | ok |
| n063 | 1.00 | 5 | 4 | False | 6456 | False | 1719 / 1719 | ok |
| n066 | 1.00 | 5 | 5 | False | 5029 | False | 1601 / 1601 | ok |
| n068 | 1.00 | 5 | 5 | False | 3735 | False | 1455 / 1455 | ok |
| n069 | 1.00 | 4 | 4 | False | 12725 | False | 2108 / 2108 | ok |
| n073 | 1.00 | 2 | 2 | True | 8994 | False | 1989 / 1989 | ok |
| n074 | 0.50 | 5 | 5 | False | 4794 | False | 1804 / 1804 | ok |
| n076 | 0.50 | 1 | 1 | True | 8819 | False | 1960 / 1960 | ok |
| n080 | 1.00 | 5 | 4 | False | 9485 | False | 2099 / 2099 | ok |
| n084 | 1.00 | 5 | 5 | False | 8175 | False | 2025 / 2025 | ok |
| n087 | 1.00 | 5 | 5 | False | 3629 | False | 1414 / 1414 | ok |
| n088 | 1.00 | 5 | 5 | False | 8027 | False | 2230 / 2230 | ok |
| n089 | 1.00 | 5 | 5 | False | 4913 | False | 1961 / 1961 | ok |
| n090 | 1.00 | 5 | 5 | False | 7097 | False | 1961 / 1961 | ok |
| n092 | 1.00 | 5 | 5 | False | 9746 | False | 1938 / 1938 | ok |
| n094 | 0.50 | 5 | 5 | False | 10837 | False | 1986 / 1986 | ok |
| n098 | 1.00 | 5 | 5 | False | 8059 | False | 2180 / 2180 | ok |
| n100 | 1.00 | 5 | 5 | False | 10897 | False | 2264 / 2264 | ok |
| n102 | 1.00 | 5 | 5 | False | 14900 | False | 2561 / 2561 | ok |
| n103 | 0.00 | 4 | 3 | False | 14660 | False | 2495 / 2495 | ok |
| n107 | 1.00 | 5 | 5 | False | 3592 | False | 438 / 438 | ok |
| n110 | 1.00 | 5 | 5 | False | 6401 | False | 1966 / 1966 | ok |
| n114 | 1.00 | 5 | 4 | False | 12108 | False | 2200 / 2200 | ok |
| n117 | 0.00 | 5 | 5 | False | 4551 | False | 1806 / 1806 | ok |
| n118 | 1.00 | 5 | 5 | False | 8167 | False | 2110 / 2110 | ok |
| n119 | 1.00 | 5 | 5 | False | 9683 | False | 2423 / 2423 | ok |

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
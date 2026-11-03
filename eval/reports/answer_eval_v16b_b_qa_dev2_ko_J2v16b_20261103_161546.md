# Answer eval report (v16b_b_qa_dev2_ko, judge J2v16b)

- date: 2026-11-03T16:15:46.341464+00:00
- generated: 2026-11-03T15:40:08.981925+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J2v16b, gemma4:12b-it-qat, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: google/gemma-4-12B-it@707f0a3
- judge order: dataset
- judge date: 2026-11-03T16:13:46.766420+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_dev2_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_b_qa_dev2_ko.gen.jsonl, eval/runs/v16b_b_qa_dev2_ko.J2v16b.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.86 | 4.47 | 4.38 | 175 | 6/40 | 5255 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n001 | 1.00 | 1 | 2 | True | 4056 | False | 2027 / 2027 | ok |
| n005 | 1.00 | 5 | 5 | False | 3593 | False | 1902 / 1902 | ok |
| n006 | 1.00 | 5 | 5 | False | 6439 | False | 2147 / 2147 | ok |
| n009 | 1.00 | 5 | 5 | False | 1954 | False | 1646 / 1646 | ok |
| n011 | 1.00 | 5 | 5 | False | 2044 | False | 1665 / 1665 | ok |
| n012 | 1.00 | 5 | 5 | False | 3601 | False | 1740 / 1740 | ok |
| n015 | 0.00 | 2 | 1 | True | 6716 | False | 2204 / 2204 | ok |
| n018 | 1.00 | 5 | 5 | False | 5884 | False | 2084 / 2084 | ok |
| n031 | 1.00 | 5 | 5 | False | 5197 | False | 2045 / 2045 | ok |
| n041 | 1.00 | 2 | 1 | True | 4496 | False | 1958 / 1958 | ok |
| n044 | 1.00 | 5 | 5 | False | 5042 | False | 2133 / 2133 | ok |
| n049 | 0.50 | 5 | 5 | False | 1866 | False | 1605 / 1605 | ok |
| n053 | 1.00 | 5 | 5 | False | 6978 | False | 2190 / 2190 | ok |
| n058 | 1.00 | 5 | 5 | False | 3553 | False | 1650 / 1650 | ok |
| n059 | 1.00 | 5 | 5 | False | 6047 | False | 2058 / 2058 | ok |
| n063 | 1.00 | 5 | 4 | False | 4104 | False | 1718 / 1718 | ok |
| n066 | 1.00 | 5 | 5 | False | 3239 | False | 1610 / 1610 | ok |
| n068 | 1.00 | 5 | 5 | False | 2595 | False | 1493 / 1493 | ok |
| n069 | 1.00 | 2 | 3 | True | 7356 | False | 2098 / 2098 | ok |
| n073 | 1.00 | 5 | 4 | False | 7826 | False | 2287 / 2287 | ok |
| n074 | 0.50 | 5 | 5 | False | 3137 | False | 1825 / 1825 | ok |
| n076 | 0.50 | 1 | 1 | True | 5561 | False | 1950 / 1950 | ok |
| n080 | 1.00 | 5 | 5 | False | 6571 | False | 2076 / 2076 | ok |
| n084 | 1.00 | 5 | 5 | False | 7214 | False | 2163 / 2163 | ok |
| n087 | 1.00 | 5 | 5 | False | 2153 | False | 1477 / 1477 | ok |
| n088 | 1.00 | 5 | 5 | False | 6674 | False | 2335 / 2335 | ok |
| n089 | 1.00 | 5 | 5 | False | 9185 | False | 2534 / 2534 | ok |
| n090 | 1.00 | 5 | 5 | False | 5116 | False | 2007 / 2007 | ok |
| n092 | 1.00 | 5 | 5 | False | 5825 | False | 1858 / 1858 | ok |
| n094 | 0.50 | 5 | 5 | False | 5532 | False | 1799 / 1799 | ok |
| n098 | 1.00 | 5 | 5 | False | 5073 | False | 2148 / 2148 | ok |
| n100 | 1.00 | 5 | 5 | False | 6139 | False | 2124 / 2124 | ok |
| n102 | 0.50 | 3 | 2 | True | 7183 | False | 2237 / 2237 | ok |
| n103 | 0.00 | 4 | 4 | False | 10737 | False | 2547 / 2547 | ok |
| n107 | 1.00 | 5 | 5 | False | 2791 | False | 930 / 930 | ok |
| n110 | 1.00 | 5 | 5 | False | 3988 | False | 1958 / 1958 | ok |
| n114 | 1.00 | 4 | 3 | False | 8482 | False | 2219 / 2219 | ok |
| n117 | 0.00 | 5 | 5 | False | 2624 | False | 1806 / 1806 | ok |
| n118 | 1.00 | 5 | 5 | False | 5313 | False | 2110 / 2110 | ok |
| n119 | 1.00 | 5 | 5 | False | 7781 | False | 2536 / 2536 | ok |

## Worst questions (lowest keyword coverage)

- **n015** (0.00): 요청 본문에 Pydantic 모델 두 개를 동시에 받을 수 있어?
  > 네, 같은 FastAPI 경로 처리에서 Pydantic v1 모델과 Pydantic v2 모델을 함께 사용할 수 있습니다. 예를 들어, 입력 모델은 Pydantic v1 모델을 사용하고, 출력 모델은 Pydantic v2 모델을 사용하는 것이 가능합니다.

```python
from fastapi import FastAPI, HTTPException
fro
- **n103** (0.00): 인터넷이 안 되는 사내망이라 Swagger UI가 CDN에서 안 불러와져요. 오프라인에서 문서 보는 방법은?
  > 인터넷이 없는 사내망에서도 Swagger UI와 ReDoc 문서를 오프라인으로 볼 수 있는 방법은 다음과 같습니다:

1. **정적 파일 직접 호스팅**:
   - Swagger UI와 ReDoc에 필요한 JavaScript와 CSS 파일을 직접 호스팅해야 합니다.
   - 이 파일들은 보통 CDN에서 제공되지만, 로컬 서버나 파일 시스템에 직접 저장할 수
- **n117** (0.00): 헤더나 쿠키도 Pydantic 모델 하나로 한꺼번에 선언할 수 있을까요?
  > 네, 헤더나 쿠키도 Pydantic 모델로 한꺼번에 선언할 수 있습니다. 관련 있는 헤더나 쿠키 매개변수의 그룹을 Pydantic 모델로 정의하여 여러 위치에서 재사용하고, 유효성 검사 및 메타데이터를 한 번에 선언할 수 있습니다.
- **n049** (0.50): 비밀번호 해싱은 뭘로 해야 돼? passlib, bcrypt, argon2 중에 뭐가 나아?
  > Argon2가 추천됩니다.
- **n074** (0.50): 경로 함수를 async def 말고 그냥 def로 선언하면 스레드풀에서 돌아간다는데 맞습니까?
  > 네, 맞습니다. 경로 함수를 `def`로 선언하면, 해당 함수는 외부 스레드풀에서 실행됩니다. 이는 FastAPI가 비동기적으로 동작하는 방식과 관련이 있습니다. `async def`로 선언된 함수는 코루틴으로 처리되며, `await`를 통해 비동기 작업을 수행할 수 있습니다. 반면, `def`로 선언된 함수는 동기적으로 실행되며, FastAPI는 이를 외
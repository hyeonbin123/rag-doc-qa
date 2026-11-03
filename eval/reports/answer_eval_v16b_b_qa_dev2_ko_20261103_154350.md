# Answer eval report (v16b_b_qa_dev2_ko)

- date: 2026-11-03T15:43:50.275704+00:00
- generated: 2026-11-03T15:40:08.981925+00:00
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
- dataset: qa_dev2_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_b_qa_dev2_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.86 | n/a | n/a | n/a | 0/0 | 5255 | 0/40 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n001 | 1.00 | None | None | None | 4056 | False | None / None | - |
| n005 | 1.00 | None | None | None | 3593 | False | None / None | - |
| n006 | 1.00 | None | None | None | 6439 | False | None / None | - |
| n009 | 1.00 | None | None | None | 1954 | False | None / None | - |
| n011 | 1.00 | None | None | None | 2044 | False | None / None | - |
| n012 | 1.00 | None | None | None | 3601 | False | None / None | - |
| n015 | 0.00 | None | None | None | 6716 | False | None / None | - |
| n018 | 1.00 | None | None | None | 5884 | False | None / None | - |
| n031 | 1.00 | None | None | None | 5197 | False | None / None | - |
| n041 | 1.00 | None | None | None | 4496 | False | None / None | - |
| n044 | 1.00 | None | None | None | 5042 | False | None / None | - |
| n049 | 0.50 | None | None | None | 1866 | False | None / None | - |
| n053 | 1.00 | None | None | None | 6978 | False | None / None | - |
| n058 | 1.00 | None | None | None | 3553 | False | None / None | - |
| n059 | 1.00 | None | None | None | 6047 | False | None / None | - |
| n063 | 1.00 | None | None | None | 4104 | False | None / None | - |
| n066 | 1.00 | None | None | None | 3239 | False | None / None | - |
| n068 | 1.00 | None | None | None | 2595 | False | None / None | - |
| n069 | 1.00 | None | None | None | 7356 | False | None / None | - |
| n073 | 1.00 | None | None | None | 7826 | False | None / None | - |
| n074 | 0.50 | None | None | None | 3137 | False | None / None | - |
| n076 | 0.50 | None | None | None | 5561 | False | None / None | - |
| n080 | 1.00 | None | None | None | 6571 | False | None / None | - |
| n084 | 1.00 | None | None | None | 7214 | False | None / None | - |
| n087 | 1.00 | None | None | None | 2153 | False | None / None | - |
| n088 | 1.00 | None | None | None | 6674 | False | None / None | - |
| n089 | 1.00 | None | None | None | 9185 | False | None / None | - |
| n090 | 1.00 | None | None | None | 5116 | False | None / None | - |
| n092 | 1.00 | None | None | None | 5825 | False | None / None | - |
| n094 | 0.50 | None | None | None | 5532 | False | None / None | - |
| n098 | 1.00 | None | None | None | 5073 | False | None / None | - |
| n100 | 1.00 | None | None | None | 6139 | False | None / None | - |
| n102 | 0.50 | None | None | None | 7183 | False | None / None | - |
| n103 | 0.00 | None | None | None | 10737 | False | None / None | - |
| n107 | 1.00 | None | None | None | 2791 | False | None / None | - |
| n110 | 1.00 | None | None | None | 3988 | False | None / None | - |
| n114 | 1.00 | None | None | None | 8482 | False | None / None | - |
| n117 | 0.00 | None | None | None | 2624 | False | None / None | - |
| n118 | 1.00 | None | None | None | 5313 | False | None / None | - |
| n119 | 1.00 | None | None | None | 7781 | False | None / None | - |

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
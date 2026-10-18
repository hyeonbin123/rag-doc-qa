# Answer eval report (v15_i4_ubase_qa_test2_ko)

- date: 2026-10-18T13:29:33.542824+00:00
- generated: 2026-10-18T13:27:56.874897+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/12)
- final answer call stopped by the output limit, done_reason=length: 0/12; reasoning output: 0/12; citation replies breaking the schema: 0/12
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_test2_ko.jsonl
- questions: 12
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_ubase_qa_test2_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.75 | n/a | n/a | n/a | 0/0 | 6296 | 0/12 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| k001 | 1.00 | None | None | None | 9864 | False | None / None | - |
| k006 | 1.00 | None | None | None | 9628 | False | None / None | - |
| k008 | 0.00 | None | None | None | 7327 | False | None / None | - |
| k010 | 1.00 | None | None | None | 8883 | False | None / None | - |
| k011 | 1.00 | None | None | None | 6058 | False | None / None | - |
| k013 | 1.00 | None | None | None | 9995 | False | None / None | - |
| k014 | 1.00 | None | None | None | 6037 | False | None / None | - |
| k015 | 0.00 | None | None | None | 6300 | False | None / None | - |
| k019 | 1.00 | None | None | None | 5083 | False | None / None | - |
| k023 | 1.00 | None | None | None | 5569 | False | None / None | - |
| k034 | 1.00 | None | None | None | 3362 | False | None / None | - |
| k043 | 0.00 | None | None | None | 6291 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **k008** (0.00): 모든 요청이 처리되는 데 얼마나 걸리는지 기록하려면 어떻게 하나요?
  > 요청 처리 시간을 기록하려면 FastAPI의 `Lifespan` 이벤트를 활용할 수 있습니다. 애플리케이션이 **시작**할 때(`on_startup`)와 **종료**할 때(`on_shutdown`) 시간을 기록하여 요청 처리 시간을 계산할 수 있습니다.

```python
from fastapi import FastAPI
import time

app = 
- **k015** (0.00): 요청의 이메일 필드가 정말 이메일 형식인지 확인하려면 어떻게 하나요?
  > 요청의 이메일 필드가 정말 이메일 형식인지 확인하려면, `Form` 매개변수를 사용하여 이메일 필드를 받고, Pydantic의 커스텀 검증기를 활용해야 합니다.

```python
from fastapi import FastAPI, Form, HTTPException
from pydantic import ValidationError
import re

ap
- **k043** (0.00): 클라이언트가 보내지만 문서에는 절대 보이지 않아야 하는 필드를 추가하려면 어떻게 하나요?
  > 클라이언트가 보내지만 문서에는 보이지 않아야 하는 필드를 추가하려면, Pydantic 모델을 사용하여 `extra` 필드를 금지(`forbid`)해야 합니다. 그러나, 문서에서 해당 필드가 보이지 않도록 하려면, 모델 정의 시 `extra` 필드를 명시적으로 처리하거나, 문서 생성 시 해당 필드를 제외하는 방법을 사용해야 합니다.

하지만, 주어진 문맥에서
- **k001** (1.00): 로컬 3000번 포트에서 돌아가는 React 앱이 8000번 포트의 API를 호출하면 막힙니다. 어떻게 해결하나요?
  > 프록시 설정을 통해 경로 접두사를 조정해야 합니다. React 앱이 8000번 포트의 API를 호출할 때, 프록시가 `/api/v1` 접두사를 제거하도록 설정해야 합니다.

### 해결 방법:

1. **프록시 설정 확인**:
   - React 앱의 `package.json` 파일에 `proxy` 설정을 추가합니다.
   - 예시: `"proxy": "h
- **k006** (1.00): 로그인한 사용자만 호출할 수 있게 엔드포인트를 보호하려면 어떻게 하나요?
  > `get_current_active_user` 의존성을 사용하여 엔드포인트를 보호할 수 있습니다. 이 의존성은 사용자가 활성화되어 있는지 확인하고, 그렇지 않으면 HTTP 오류를 반환합니다. 예를 들어, `/users/me` 엔드포인트에 대해 다음과 같이 구현할 수 있습니다:

```python
from fastapi import FastAPI, Depen
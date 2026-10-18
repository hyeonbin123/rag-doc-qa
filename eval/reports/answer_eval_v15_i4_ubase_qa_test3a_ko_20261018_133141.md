# Answer eval report (v15_i4_ubase_qa_test3a_ko)

- date: 2026-10-18T13:31:41.657628+00:00
- generated: 2026-10-18T13:30:58.252538+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/5)
- final answer call stopped by the output limit, done_reason=length: 0/5; reasoning output: 0/5; citation replies breaking the schema: 0/5
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_test3a_ko.jsonl
- questions: 5
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_ubase_qa_test3a_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 1.00 | n/a | n/a | n/a | 0/0 | 6141 | 0/5 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n004 | 1.00 | None | None | None | 3310 | False | None / None | - |
| n046 | 1.00 | None | None | None | 6141 | False | None / None | - |
| n056 | 1.00 | None | None | None | 11447 | False | None / None | - |
| n064 | 1.00 | None | None | None | 3610 | False | None / None | - |
| n071 | 1.00 | None | None | None | 7222 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **n004** (1.00): 경로 파라미터에 미리 정해진 몇 가지 값만 허용하고 싶은데 Enum을 쓰면 되나요?
  > 네, Enum을 사용하면 경로 파라미터에 미리 정해진 값만 허용할 수 있습니다.
- **n046** (1.00): 테스트할 때 실제 의존성 대신 가짜 의존성으로 바꿔치기하는 방법
  > `app.dependency_overrides` 속성을 사용하여 테스트 중 실제 의존성 대신 가짜 의존성을 제공할 수 있습니다. 이를 위해 원래 의존성을 키로, 오버라이드할 의존성을 값으로 설정합니다. 예를 들어:

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
- **n056** (1.00): 액세스 토큰 만료 시간을 설정하고 만료된 토큰이 오면 401을 돌려주려면?
  > 토큰의 만료 시간으로 `timedelta`를 생성하고, 만료된 토큰이 오면 401을 반환하는 로직을 구현해야 합니다.

```python
from fastapi import FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
- **n064** (1.00): 백그라운드 작업이 무겁고 오래 걸리면 BackgroundTasks 말고 Celery 같은 걸 써야 하나요?
  > 네, 백그라운드 작업이 무겁고 오래 걸리면 Celery 같은 외부 메시지 큐 기반 작업 큐 시스템을 사용하는 것이 좋습니다. Celery는 RabbitMQ나 Redis 같은 메시지 브로커를 사용하여 여러 프로세스나 서버에서 작업을 분산 처리할 수 있게 해줍니다. FastAPI 앱 내에서 `BackgroundTasks`는 간단한 백그라운드 작업에 적합하지만,
- **n071** (1.00): SQLAlchemy 세션을 요청마다 열고 닫으려면 어떻게 해야 하죠?
  > `yield`를 사용하여 FastAPI의 의존성을 생성하고, 각 요청마다 새로운 세션을 제공하는 방법을 사용해야 합니다. 이를 통해 요청마다 단일 세션을 보장할 수 있습니다.

```python
from fastapi import FastAPI, Depends
from sqlmodel import create_engine, Session, SQLModel,
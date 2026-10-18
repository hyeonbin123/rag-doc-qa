# Answer eval report (v15_i4_ucand_qa_test3a_ko, judge J1v15r2)

- date: 2026-10-18T13:59:13.624638+00:00
- generated: 2026-10-18T13:31:55.537869+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/5)
- final answer call stopped by the output limit, done_reason=length: 0/5; reasoning output: 0/5; citation replies breaking the schema: 0/5
- judge: J1v15r2, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-18T13:59:06.983670+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_test3a_ko.jsonl
- questions: 5
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_ucand_qa_test3a_ko.gen.jsonl, eval/runs/v15_i4_ucand_qa_test3a_ko.J1v15r2.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.80 | 4.25 | 4.25 | 17 | 0/4 | 2108 | 0/5 | 0/4 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n004 | 1.00 | 4 | 4 | False | 2087 | False | 811 / 811 | ok |
| n046 | 1.00 | 5 | 5 | False | 3465 | False | 942 / 942 | ok |
| n056 | 0.00 | None | None | None | 0 | False | None / None | unchecked |
| n064 | 1.00 | 4 | 4 | False | 2653 | False | 1528 / 1528 | ok |
| n071 | 1.00 | 4 | 4 | False | 2108 | False | 909 / 909 | ok |

## Worst questions (lowest keyword coverage)

- **n056** (0.00): 액세스 토큰 만료 시간을 설정하고 만료된 토큰이 오면 401을 돌려주려면?
  > 모르겠습니다. 찾은 문서 구절에는 이 질문에 대한 내용이 없습니다.
- **n004** (1.00): 경로 파라미터에 미리 정해진 몇 가지 값만 허용하고 싶은데 Enum을 쓰면 되나요?
  > 네, Enum을 사용하면 경로 파라미터에 미리 정해진 값만 허용할 수 있습니다.
- **n046** (1.00): 테스트할 때 실제 의존성 대신 가짜 의존성으로 바꿔치기하는 방법
  > `app.dependency_overrides` 속성을 사용하여 테스트 시 실제 의존성 대신 가짜 의존성을 사용할 수 있습니다. 이는 `dict` 형태로 설정하며, 원래 의존성을 키로, 오버라이드할 의존성을 값으로 지정합니다. 예를 들어:

```python
app.dependency_overrides = {
    my_dependency_function
- **n064** (1.00): 백그라운드 작업이 무겁고 오래 걸리면 BackgroundTasks 말고 Celery 같은 걸 써야 하나요?
  > 네, 백그라운드 작업이 무겁고 오래 걸리면 Celery 같은 더 큰 도구를 사용하는 것이 좋습니다. Celery는 RabbitMQ나 Redis 같은 메시지/작업 큐 관리자를 사용하여 여러 프로세스에서, 특히 여러 서버에서 백그라운드 작업을 실행할 수 있게 해줍니다. FastAPI의 `BackgroundTasks`는 작은 백그라운드 작업(예: 이메일 알림 전
- **n071** (1.00): SQLAlchemy 세션을 요청마다 열고 닫으려면 어떻게 해야 하죠?
  > `yield`를 사용해 FastAPI의 의존성을 생성하여 각 요청마다 새로운 `Session`을 제공하는 방법을 사용해야 합니다. 이는 요청당 하나의 세션만 사용되도록 보장합니다.
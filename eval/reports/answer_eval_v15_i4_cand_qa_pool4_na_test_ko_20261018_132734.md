# Answer eval report (v15_i4_cand_qa_pool4_na_test_ko)

- date: 2026-10-18T13:27:34.707442+00:00
- generated: 2026-10-18T13:26:59.187383+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/14)
- final answer call stopped by the output limit, done_reason=length: 0/14; reasoning output: 0/14; citation replies breaking the schema: 0/14
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_pool4_na_test_ko.jsonl
- questions: 14
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_cand_qa_pool4_na_test_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 1.00 | n/a | n/a | n/a | 0/0 | 1072 | 0/14 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| k4a03 | 1.00 | None | None | None | 2580 | False | None / None | - |
| k4a04 | 1.00 | None | None | None | 6030 | False | None / None | - |
| k4a05 | 1.00 | None | None | None | 4518 | False | None / None | - |
| k4a06 | 1.00 | None | None | None | 2295 | False | None / None | - |
| k4a07 | 1.00 | None | None | None | 0 | False | None / None | - |
| k4a12 | 1.00 | None | None | None | 2144 | False | None / None | - |
| k4a13 | 1.00 | None | None | None | 0 | False | None / None | - |
| k4a16 | 1.00 | None | None | None | 0 | False | None / None | - |
| k4a20 | 1.00 | None | None | None | 0 | False | None / None | - |
| k4a21 | 1.00 | None | None | None | 0 | False | None / None | - |
| k4a22 | 1.00 | None | None | None | 0 | False | None / None | - |
| k4a25 | 1.00 | None | None | None | 2757 | False | None / None | - |
| k4a29 | 1.00 | None | None | None | 2345 | False | None / None | - |
| k4a30 | 1.00 | None | None | None | 0 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **k4a03** (1.00): SQLAlchemy 2.0에서 relationship에 lazy="selectin" 주는 거랑 쿼리에서 joinedload 쓰는 거 성능 차이가 어느 정도예요?
  > 죄송하지만, 주어진 문맥에서 이 질문에 대한 정보를 찾을 수 없습니다. 따라서 정확한 답변을 제공하기 어렵습니다.
- **k4a04** (1.00): Alembic autogenerate가 컬럼 타입 변경을 못 잡는데 compare_type 옵션은 env.py 어디에 넣어야 해요?
  > `compare_type` 옵션은 `env.py` 파일의 `upgrade` 함수 내에 넣어야 합니다.

```python
def upgrade(migrate_engine, metadata):
    # 기존 코드
    ...

    # compare_type 옵션 추가
    with migrate_engine.connect() as conn:
    
- **k4a05** (1.00): Celery beat로 매일 새벽 3시에 배치 돌리려면 crontab 스케줄 설정을 어떻게 써요?
  > Celery Beat로 매일 새벽 3시에 배치 작업을 돌리려면 crontab 스케줄 설정은 다음과 같이 작성합니다:

```
0 3 * * * /usr/bin/celery -A your_project_name.tasks beat --schedule=/path/to/your/schedule.py
```

여기서:
- `0 3 * * *`는 매일 03:00에 
- **k4a06** (1.00): slowapi로 IP당 분당 10회 제한 거는 데코레이터 사용법이랑 Redis 백엔드 연결하는 방법
  > 죄송하지만, 주어진 문맥에서는 slowapi의 데코레이터 사용법이나 Redis 백엔드 연결 방법에 대한 구체적인 정보를 제공하지 않습니다. 따라서 해당 질문에 대한 답변을 드릴 수 없습니다.
- **k4a07** (1.00): 업로드하면 Nginx에서 413 Request Entity Too Large가 떠요. client_max_body_size는 http, server, location 중 어디에 넣어야 해요?
  > 모르겠습니다. 찾은 문서 구절에는 이 질문에 대한 내용이 없습니다.
# Answer eval report (v15_i4_base_qa_pool4_na_test_ko)

- date: 2026-10-18T13:24:46.551016+00:00
- generated: 2026-10-18T13:22:38.713168+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/20)
- final answer call stopped by the output limit, done_reason=length: 1/20; reasoning output: 0/20; citation replies breaking the schema: 0/20
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_pool4_na_test_ko.jsonl
- questions: 20
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_base_qa_pool4_na_test_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 1.00 | n/a | n/a | n/a | 0/0 | 4094 | 0/20 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| k4a01 | 1.00 | None | None | None | 9195 | False | None / None | - |
| k4a02 | 1.00 | None | None | None | 15508 | False | None / None | - |
| k4a03 | 1.00 | None | None | None | 3499 | False | None / None | - |
| k4a04 | 1.00 | None | None | None | 6345 | False | None / None | - |
| k4a05 | 1.00 | None | None | None | 4742 | False | None / None | - |
| k4a06 | 1.00 | None | None | None | 3158 | False | None / None | - |
| k4a07 | 1.00 | None | None | None | 7448 | False | None / None | - |
| k4a09 | 1.00 | None | None | None | 11812 | False | None / None | - |
| k4a10 | 1.00 | None | None | None | 3141 | False | None / None | - |
| k4a12 | 1.00 | None | None | None | 3708 | False | None / None | - |
| k4a13 | 1.00 | None | None | None | 3182 | False | None / None | - |
| k4a16 | 1.00 | None | None | None | 3348 | False | None / None | - |
| k4a18 | 1.00 | None | None | None | 6140 | False | None / None | - |
| k4a19 | 1.00 | None | None | None | 3169 | False | None / None | - |
| k4a20 | 1.00 | None | None | None | 6690 | False | None / None | - |
| k4a21 | 1.00 | None | None | None | 3181 | False | None / None | - |
| k4a22 | 1.00 | None | None | None | 3678 | False | None / None | - |
| k4a25 | 1.00 | None | None | None | 4480 | False | None / None | - |
| k4a29 | 1.00 | None | None | None | 3429 | False | None / None | - |
| k4a30 | 1.00 | None | None | None | 8578 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **k4a01** (1.00): DRF에서 FastAPI로 옮기는 중인데, DRF ModelSerializer의 read_only_fields랑 extra_kwargs는 정확히 뭐가 달랐죠?
  > DRF의 `read_only_fields`와 `extra_kwargs`는 FastAPI의 Pydantic 모델과 `Field`를 사용하여 유사한 기능을 구현할 수 있습니다.

1. **read_only_fields**:
   - DRF에서 `read_only_fields`는 직렬화 시 읽기 전용 필드를 지정하는 데 사용됩니다.
   - FastAPI에서는 
- **k4a02** (1.00): FastAPI를 Mangum으로 감싸서 Lambda에 올리려는데 AWS 콘솔에서 API Gateway 연결하는 클릭 순서 좀 알려주세요
  > AWS 콘솔에서 FastAPI 애플리케이션을 Mangum으로 감싸서 Lambda에 올리고 API Gateway와 연결하는 일반적인 클릭 순서는 다음과 같습니다:

1. **AWS 콘솔 접속**
   - AWS 계정으로 로그인 후 AWS Management Console에 접속합니다.

2. **Lambda 서비스 선택**
   - 서비스 메뉴에서 **Lam
- **k4a03** (1.00): SQLAlchemy 2.0에서 relationship에 lazy="selectin" 주는 거랑 쿼리에서 joinedload 쓰는 거 성능 차이가 어느 정도예요?
  > 죄송하지만, 주어진 문맥에서 SQLAlchemy 2.0의 `lazy="selectin"`과 `joinedload`의 성능 차이에 대한 구체적인 정보는 제공되지 않았습니다.
- **k4a04** (1.00): Alembic autogenerate가 컬럼 타입 변경을 못 잡는데 compare_type 옵션은 env.py 어디에 넣어야 해요?
  > `compare_type` 옵션은 `env.py` 파일의 `upgrade` 함수 내에 넣어야 합니다.

```python
def upgrade(migrate_engine, metadata):
    # 기존 코드
    ...

    # compare_type 옵션 추가
    with migrate_engine.connect() as conn:
    
- **k4a05** (1.00): Celery beat로 매일 새벽 3시에 배치 돌리려면 crontab 스케줄 설정을 어떻게 써요?
  > Celery beat로 매일 새벽 3시에 배치 작업을 돌리려면 crontab에 다음과 같이 설정합니다:

```
0 3 * * * /usr/bin/celery -A your_project_name.celery_app.celery beat --schedule=/path/to/your/schedule.py
```

여기서:
- `0 3 * * *`는 매일 03
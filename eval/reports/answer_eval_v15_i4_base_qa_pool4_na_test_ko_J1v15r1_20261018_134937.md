# Answer eval report (v15_i4_base_qa_pool4_na_test_ko, judge J1v15r1)

- date: 2026-10-18T13:49:37.081327+00:00
- generated: 2026-10-18T13:22:38.713168+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/20)
- final answer call stopped by the output limit, done_reason=length: 1/20; reasoning output: 0/20; citation replies breaking the schema: 0/20
- judge: J1v15r1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-18T13:48:54.735575+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_pool4_na_test_ko.jsonl
- questions: 20
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_base_qa_pool4_na_test_ko.gen.jsonl, eval/runs/v15_i4_base_qa_pool4_na_test_ko.J1v15r1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 1.00 | 3.25 | 3.35 | 67 | 3/20 | 4094 | 0/20 | 0/20 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| k4a01 | 1.00 | 4 | 4 | False | 9195 | False | 2393 / 2393 | ok |
| k4a02 | 1.00 | 3 | 2 | True | 15508 | False | 2892 / 2892 | ok |
| k4a03 | 1.00 | 3 | 3 | False | 3499 | False | 1725 / 1725 | ok |
| k4a04 | 1.00 | 4 | 4 | False | 6345 | False | 2156 / 2156 | ok |
| k4a05 | 1.00 | 4 | 4 | False | 4742 | False | 1578 / 1578 | ok |
| k4a06 | 1.00 | 3 | 3 | False | 3158 | False | 1510 / 1510 | ok |
| k4a07 | 1.00 | 4 | 5 | False | 7448 | False | 2337 / 2337 | ok |
| k4a09 | 1.00 | 4 | 4 | False | 11812 | False | 2708 / 2708 | ok |
| k4a10 | 1.00 | 3 | 3 | False | 3141 | False | 1932 / 1932 | ok |
| k4a12 | 1.00 | 2 | 3 | False | 3708 | False | 2141 / 2141 | ok |
| k4a13 | 1.00 | 3 | 3 | False | 3182 | False | 1875 / 1875 | ok |
| k4a16 | 1.00 | 2 | 2 | False | 3348 | False | 1886 / 1886 | ok |
| k4a18 | 1.00 | 3 | 3 | False | 6140 | False | 2286 / 2286 | ok |
| k4a19 | 1.00 | 3 | 3 | False | 3169 | False | 1812 / 1812 | ok |
| k4a20 | 1.00 | 4 | 4 | False | 6690 | False | 2171 / 2171 | ok |
| k4a21 | 1.00 | 2 | 1 | True | 3181 | False | 1788 / 1788 | ok |
| k4a22 | 1.00 | 2 | 1 | True | 3678 | False | 1987 / 1987 | ok |
| k4a25 | 1.00 | 4 | 5 | False | 4480 | False | 2044 / 2044 | ok |
| k4a29 | 1.00 | 4 | 5 | False | 3429 | False | 1891 / 1891 | ok |
| k4a30 | 1.00 | 4 | 5 | False | 8578 | False | 2406 / 2406 | ok |

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
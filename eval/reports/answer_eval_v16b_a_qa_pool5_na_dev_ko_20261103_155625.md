# Answer eval report (v16b_a_qa_pool5_na_dev_ko)

- date: 2026-11-03T15:56:25.440043+00:00
- generated: 2026-11-03T15:55:36.142479+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/10)
- final answer call stopped by the output limit, done_reason=length: 0/10; reasoning output: 0/10; citation replies breaking the schema: 0/10
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- corpus: source commit 50113da (277 documents); last fetched 2026-11-03T08:04:42.172603+00:00; chunks en 914, ko 621
- dataset: qa_pool5_na_dev_ko.jsonl
- questions: 10
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_a_qa_pool5_na_dev_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 1.00 | n/a | n/a | n/a | 0/0 | 3593 | 0/10 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| k5a07 | 1.00 | None | None | None | 6278 | False | None / None | - |
| k5a08 | 1.00 | None | None | None | 5497 | False | None / None | - |
| k5n02 | 1.00 | None | None | None | 3432 | False | None / None | - |
| k5n10 | 1.00 | None | None | None | 2435 | False | None / None | - |
| k5n17 | 1.00 | None | None | None | 4092 | False | None / None | - |
| k5n27 | 1.00 | None | None | None | 3375 | False | None / None | - |
| k5n30 | 1.00 | None | None | None | 3572 | False | None / None | - |
| k5n33 | 1.00 | None | None | None | 3613 | False | None / None | - |
| k5n34 | 1.00 | None | None | None | 2841 | False | None / None | - |
| k5n55 | 1.00 | None | None | None | 4748 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **k5a07** (1.00): PostgreSQL ENUM 타입에 값을 추가했는데 Alembic autogenerate가 감지를 못 해요. 마이그레이션은 어떻게 짜야 하나요?
  > 죄송하지만, 주어진 문맥에서는 PostgreSQL ENUM 타입에 대한 Alembic 마이그레이션 방법에 대한 구체적인 정보를 제공하지 않습니다. Alembic은 SQLAlchemy 기반의 데이터베이스 마이그레이션 도구로, 일반적으로 테이블 구조 변경을 다루지만, ENUM 타입과 같은 특정 데이터베이스 특화 타입에 대한 자동 감지는 제한적일 수 있습니다.

- **k5a08** (1.00): Google Cloud Run 콘솔에서 최소 인스턴스 수와 CPU 항상 할당 옵션은 어디서 켜나요?
  > Google Cloud Run 콘솔에서 최소 인스턴스 수와 CPU 항상 할당 옵션은 다음과 같은 위치에서 설정할 수 있습니다:

1. **최소 인스턴스 수 설정**:
   - Google Cloud Console에 로그인합니다.
   - Cloud Run 서비스로 이동합니다.
   - 배포할 서비스를 선택합니다.
   - **설정(Settings)** 탭에
- **k5n02** (1.00): BackgroundTasks에 add_task로 작업 세 개를 넣었는데, 두 번째 작업에서 예외가 나면 세 번째 작업은 그래도 실행되나요?
  > 네, 두 번째 작업에서 예외가 발생하더라도 세 번째 작업은 여전히 실행됩니다. `BackgroundTasks`의 `.add_task()` 메서드는 각 작업을 독립적으로 처리하며, 하나의 작업에서 예외가 발생해도 다른 작업들에 영향을 주지 않습니다. 이는 FastAPI의 설계 철학에 따라 각 작업이 별도의 백그라운드 태스크로 실행되기 때문입니다.
- **k5n10** (1.00): GET 경로만 정의해 뒀는데 HEAD 요청이 오면 FastAPI가 자동으로 처리해 주나요, 405를 돌려주나요?
  > 405를 돌려줍니다.
- **k5n17** (1.00): int 경로 매개변수에 "/items/007"처럼 앞에 0이 붙은 값이 오면 7로 받아주나요, 422가 나나요?
  > 네, int 경로 매개변수는 앞에 0이 붙은 값을 7로 받아줍니다. FastAPI는 경로 매개변수의 타입을 파이썬 표준 타입 어노테이션으로 선언할 수 있으며, 이 경우 `item_id: int`로 선언하면 0으로 시작하는 숫자도 정상적으로 처리됩니다. 예를 들어, [http://127.0.0.1:8000/items/007](http://127.0.0.1:8
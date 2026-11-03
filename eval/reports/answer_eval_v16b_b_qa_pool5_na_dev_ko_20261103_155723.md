# Answer eval report (v16b_b_qa_pool5_na_dev_ko)

- date: 2026-11-03T15:57:23.815906+00:00
- generated: 2026-11-03T15:56:44.941426+00:00
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
- per-item records: eval/runs/v16b_b_qa_pool5_na_dev_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 1.00 | n/a | n/a | n/a | 0/0 | 2888 | 0/10 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| k5a07 | 1.00 | None | None | None | 3591 | False | None / None | - |
| k5a08 | 1.00 | None | None | None | 2449 | False | None / None | - |
| k5n02 | 1.00 | None | None | None | 2662 | False | None / None | - |
| k5n10 | 1.00 | None | None | None | 2383 | False | None / None | - |
| k5n17 | 1.00 | None | None | None | 3114 | False | None / None | - |
| k5n27 | 1.00 | None | None | None | 2069 | False | None / None | - |
| k5n30 | 1.00 | None | None | None | 2412 | False | None / None | - |
| k5n33 | 1.00 | None | None | None | 3294 | False | None / None | - |
| k5n34 | 1.00 | None | None | None | 3642 | False | None / None | - |
| k5n55 | 1.00 | None | None | None | 3978 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **k5a07** (1.00): PostgreSQL ENUM 타입에 값을 추가했는데 Alembic autogenerate가 감지를 못 해요. 마이그레이션은 어떻게 짜야 하나요?
  > 죄송합니다. 제공된 문서 구절에는 PostgreSQL ENUM 타입에 값을 추가하고 Alembic이 이를 감지하지 못할 때의 마이그레이션 방법에 대한 정보가 없습니다.

죄송합니다. 제공된 문서에는 이 질문에 대한 정보가 없습니다.
- **k5a08** (1.00): Google Cloud Run 콘솔에서 최소 인스턴스 수와 CPU 항상 할당 옵션은 어디서 켜나요?
  > 죄송합니다. 제공된 문서 구절에는 Google Cloud Run 콘솔에서 최소 인스턴스 수와 CPU 항상 할당 옵션을 설정하는 방법에 대한 정보가 없습니다.

죄송합니다. 제공된 문서에는 해당 질문에 대한 정보가 없습니다.
- **k5n02** (1.00): BackgroundTasks에 add_task로 작업 세 개를 넣었는데, 두 번째 작업에서 예외가 나면 세 번째 작업은 그래도 실행되나요?
  > 네, 두 번째 작업에서 예외가 발생하더라도 세 번째 작업은 여전히 실행됩니다. `BackgroundTasks`의 `.add_task()` 메서드는 각 작업을 독립적으로 처리하며, 하나의 작업에서 예외가 발생하더라도 다른 작업들에 영향을 주지 않습니다. 이는 FastAPI의 설계 철학에 따라 각 작업이 별도의 컨텍스트에서 실행되기 때문입니다.
- **k5n10** (1.00): GET 경로만 정의해 뒀는데 HEAD 요청이 오면 FastAPI가 자동으로 처리해 주나요, 405를 돌려주나요?
  > 405를 돌려줍니다. FastAPI는 명시적으로 정의되지 않은 HTTP 메서드에 대해 405 Method Not Allowed 응답을 반환합니다.
- **k5n17** (1.00): int 경로 매개변수에 "/items/007"처럼 앞에 0이 붙은 값이 오면 7로 받아주나요, 422가 나나요?
  > 네, int 경로 매개변수는 앞에 0이 붙은 값을 7로 받아줍니다. FastAPI는 경로 매개변수의 타입을 파이썬 표준 타입 어노테이션을 통해 선언할 수 있으며, 이 경우 `item_id: int`로 선언된 매개변수는 문자열 `"007"`을 정수 `7`로 변환하여 처리합니다. 따라서 `/items/007`로 요청하면 `item_id` 값은 `7`로 전달됩니
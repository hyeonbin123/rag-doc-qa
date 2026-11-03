# Answer eval report (v16b_a_qa_pool4_na_dev_en)

- date: 2026-11-03T15:26:43.643097+00:00
- generated: 2026-11-03T15:26:23.822601+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/10)
- final answer call stopped by the output limit, done_reason=length: 0/10; reasoning output: 0/10; citation replies breaking the schema: 0/10
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- corpus: source commit 50113da (277 documents); last fetched 2026-11-03T08:04:42.172603+00:00; chunks en 914, ko 621
- dataset: qa_pool4_na_dev_en.jsonl
- questions: 10
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_a_qa_pool4_na_dev_en.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 1.00 | n/a | n/a | n/a | 0/0 | 1437 | 0/10 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| e4a01 | 1.00 | None | None | None | 1670 | False | None / None | - |
| e4a02 | 1.00 | None | None | None | 1645 | False | None / None | - |
| e4a04 | 1.00 | None | None | None | 1393 | False | None / None | - |
| e4a05 | 1.00 | None | None | None | 1346 | False | None / None | - |
| e4a07 | 1.00 | None | None | None | 1622 | False | None / None | - |
| e4a08 | 1.00 | None | None | None | 1146 | False | None / None | - |
| e4a17 | 1.00 | None | None | None | 1218 | False | None / None | - |
| e4a18 | 1.00 | None | None | None | 1356 | False | None / None | - |
| e4a21 | 1.00 | None | None | None | 1481 | False | None / None | - |
| e4a24 | 1.00 | None | None | None | 1650 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **e4a01** (1.00): How do I tune Gunicorn's max_requests and max_requests_jitter so workers that leak memory get recycled?
  > I don't know.
- **e4a02** (1.00): What's the AWS console sequence to put an Application Load Balancer in front of an ECS Fargate service running my FastAPI container?
  > I don't know the AWS console sequence for setting up an Application Load Balancer in front of an ECS Fargate service running a FastAPI container.
- **e4a04** (1.00): Why does touching a lazy-loaded relationship in an SQLAlchemy AsyncSession raise MissingGreenlet, and how does the greenlet bridge work internally?
  > I don't know.
- **e4a05** (1.00): How does Alembic's batch mode work when altering columns in SQLite migrations?
  > I don't know.
- **e4a07** (1.00): How do I configure Celery with RabbitMQ so failed tasks retry with exponential backoff?
  > I don't know how to configure Celery with RabbitMQ for retrying failed tasks with exponential backoff based on the provided context passages.
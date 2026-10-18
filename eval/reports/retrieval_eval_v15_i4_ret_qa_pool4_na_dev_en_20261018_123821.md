# Retrieval eval report (v15_i4_ret_qa_pool4_na_dev_en)

- date: 2026-10-18T12:38:13.489726+00:00
- embedding models: en BAAI/bge-small-en-v1.5, ko ibm-granite/granite-embedding-311m-multilingual-r2
- database: ragdb
- top_k: 10
- retrieval mode: dense
- search: as planned; dense plan: en Sort > Seq Scan on chunks c > Seq Scan on documents d
- score floor: en 0.0
- stored vectors checked: en chunks vs BAAI/bge-small-en-v1.5 (min cosine 1.0)
- dataset: qa_pool4_na_dev_en.jsonl
- questions: 10
- hit: a chunk of an expected page, in any translation
- short: questions with fewer than 5 results (the score floor cut the rest)
- latency: retrieval only (after the query embedding), this machine's CPU

## Aggregate metrics

| set | questions | Hit@3 | Hit@5 | Hit@10 | MRR | short | latency p50 (ms) | latency p95 (ms) |
|---|---|---|---|---|---|---|---|---|
| all | 10 | 0.00 | 0.00 | 0.00 | 0.000 | 0 | 9 | 11 |

## Per-question

| id | hit@3 | hit@5 | hit@10 | RR | results | ms | question |
|---|---|---|---|---|---|---|---|
| e4a01 | False | False | False | 0.00 | 10 | 10 | How do I tune Gunicorn's max_requests and max_requests_jitter so workers that leak memory get recycled? |
| e4a02 | False | False | False | 0.00 | 10 | 8 | What's the AWS console sequence to put an Application Load Balancer in front of an ECS Fargate service running my FastAPI container? |
| e4a04 | False | False | False | 0.00 | 10 | 9 | Why does touching a lazy-loaded relationship in an SQLAlchemy AsyncSession raise MissingGreenlet, and how does the greenlet bridge work internally? |
| e4a05 | False | False | False | 0.00 | 10 | 9 | How does Alembic's batch mode work when altering columns in SQLite migrations? |
| e4a07 | False | False | False | 0.00 | 10 | 8 | How do I configure Celery with RabbitMQ so failed tasks retry with exponential backoff? |
| e4a08 | False | False | False | 0.00 | 10 | 9 | How do I use Redis Streams consumer groups as a job queue and reclaim pending messages after a worker crash? |
| e4a17 | False | False | False | 0.00 | 10 | 8 | How does Django Ninja's per-router authentication compare with Django REST Framework's permission classes? |
| e4a18 | False | False | False | 0.00 | 10 | 11 | How should I size PostgreSQL max_connections and choose PgBouncer's pool_mode when I have many async workers? |
| e4a21 | False | False | False | 0.00 | 10 | 9 | How do I create an AWS WAF rate-based rule that blocks IPs sending too many requests to my API? |
| e4a24 | False | False | False | 0.00 | 10 | 10 | How do I set up OpenTelemetry auto-instrumentation for a Python service and ship traces to Jaeger? |
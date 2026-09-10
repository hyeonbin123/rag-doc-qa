# Retrieval eval report (v1_baseline)

- date: 2026-09-10T16:58:12.368496+00:00
- embedding model: BAAI/bge-small-en-v1.5
- top_k: 10
- questions: 5

## Aggregate metrics

| Hit@3 | Hit@5 | Hit@10 | MRR |
|---|---|---|---|
| 1.00 | 1.00 | 1.00 | 0.800 |

## Per-question

| id | hit@3 | hit@5 | hit@10 | RR | question |
|---|---|---|---|---|---|
| q001 | True | True | True | 1.00 | How do you declare a path parameter with a type hint in FastAPI? |
| q002 | True | True | True | 1.00 | How do you mark a query parameter as optional in FastAPI? |
| q003 | True | True | True | 0.50 | How do you declare a request body in FastAPI? |
| q004 | True | True | True | 1.00 | How does FastAPI's dependency injection system work at a basic level? |
| q005 | True | True | True | 0.50 | How do you add authentication with OAuth2 and a bearer token in FastAPI? |
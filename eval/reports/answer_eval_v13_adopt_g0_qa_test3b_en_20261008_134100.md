# Answer eval report (v13_adopt_g0_qa_test3b_en)

- date: 2026-10-08T13:41:00.892820+00:00
- generated: 2026-10-08T13:37:01.459336+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- model digest: 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_test3b_en.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_adopt_g0_qa_test3b_en.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.81 | n/a | n/a | n/a | 0/0 | 5382 | 0/40 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n007 | 1.00 | None | None | None | 6384 | False | None / None | - |
| n008 | 1.00 | None | None | None | 4640 | False | None / None | - |
| n010 | 1.00 | None | None | None | 6597 | False | None / None | - |
| n013 | 1.00 | None | None | None | 4531 | False | None / None | - |
| n017 | 1.00 | None | None | None | 7305 | False | None / None | - |
| n019 | 1.00 | None | None | None | 4710 | False | None / None | - |
| n020 | 1.00 | None | None | None | 5383 | False | None / None | - |
| n023 | 1.00 | None | None | None | 4488 | False | None / None | - |
| n025 | 1.00 | None | None | None | 5679 | False | None / None | - |
| n027 | 1.00 | None | None | None | 4213 | False | None / None | - |
| n028 | 1.00 | None | None | None | 4704 | False | None / None | - |
| n029 | 1.00 | None | None | None | 5032 | False | None / None | - |
| n030 | 0.00 | None | None | None | 4625 | False | None / None | - |
| n032 | 1.00 | None | None | None | 8529 | False | None / None | - |
| n034 | 1.00 | None | None | None | 6760 | False | None / None | - |
| n035 | 1.00 | None | None | None | 5340 | False | None / None | - |
| n036 | 0.00 | None | None | None | 5224 | False | None / None | - |
| n039 | 1.00 | None | None | None | 5373 | False | None / None | - |
| n047 | 1.00 | None | None | None | 10619 | False | None / None | - |
| n048 | 1.00 | None | None | None | 5334 | False | None / None | - |
| n050 | 1.00 | None | None | None | 5141 | False | None / None | - |
| n051 | 0.00 | None | None | None | 9371 | False | None / None | - |
| n054 | 0.00 | None | None | None | 3801 | False | None / None | - |
| n055 | 1.00 | None | None | None | 4832 | False | None / None | - |
| n061 | 1.00 | None | None | None | 6596 | False | None / None | - |
| n067 | 1.00 | None | None | None | 5093 | False | None / None | - |
| n077 | 1.00 | None | None | None | 4810 | False | None / None | - |
| n083 | 1.00 | None | None | None | 5651 | False | None / None | - |
| n086 | 0.00 | None | None | None | 5381 | False | None / None | - |
| n091 | 1.00 | None | None | None | 5658 | False | None / None | - |
| n096 | 1.00 | None | None | None | 6367 | False | None / None | - |
| n097 | 0.00 | None | None | None | 4347 | False | None / None | - |
| n099 | 1.00 | None | None | None | 6096 | False | None / None | - |
| n105 | 1.00 | None | None | None | 4468 | False | None / None | - |
| n106 | 0.50 | None | None | None | 7049 | False | None / None | - |
| n112 | 1.00 | None | None | None | 5508 | False | None / None | - |
| n113 | 1.00 | None | None | None | 6551 | False | None / None | - |
| n115 | 0.00 | None | None | None | 7639 | False | None / None | - |
| n116 | 1.00 | None | None | None | 5658 | False | None / None | - |
| n120 | 1.00 | None | None | None | 5492 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **n030** (0.00): When reading a header value with Header, what does it mean that underscores are automatically converted to hyphens?
  > When reading a header value with Header, underscores in the parameter names are automatically converted to hyphens. For example, a header parameter named `save_data` would result in the HTTP header `s
- **n036** (0.00): Is there a way to override the RequestValidationError handler while still reusing FastAPI's default handler behavior?
  > Yes, you can override the `RequestValidationError` handler while still reusing FastAPI's default handler behavior by importing and using the default exception handlers from `fastapi.exception_handlers
- **n051** (0.00): I want to block disabled accounts from using the API even if they log in. How should I structure the dependencies?
  > You can structure your dependencies to check if a user account is disabled. Here's a basic approach:

1. Create a dependency that checks if the user is authenticated.
2. Create another dependency that
- **n054** (0.00): Is authentication with an API key sent in a header or a query parameter also supported?
  > don't know
- **n086** (0.00): Does using ORJSONResponse instead of the default JSONResponse improve performance?
  > Yes, using `ORJSONResponse` instead of the default `JSONResponse` can improve performance, especially for JSON serialization, due to the underlying Rust mechanisms used by `orjson`. However, for maxim
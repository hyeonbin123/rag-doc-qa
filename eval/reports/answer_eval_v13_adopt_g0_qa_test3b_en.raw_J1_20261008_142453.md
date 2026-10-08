# Answer eval report (v13_adopt_g0_qa_test3b_en.raw, judge J1)

- date: 2026-10-08T14:24:53.687254+00:00
- generated: 2026-10-08T13:37:01.459336+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- model digest: 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-08T14:23:12.113878+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_test3b_en.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_adopt_g0_qa_test3b_en.gen.jsonl, eval/runs/v13_adopt_g0_qa_test3b_en.raw.J1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.81 | 4.25 | 4.58 | 183 | 0/40 | 5382 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n007 | 1.00 | 5 | 5 | False | 6384 | False | 2351 / 2351 | ok |
| n008 | 1.00 | 4 | 5 | False | 4640 | False | 2355 / 2355 | ok |
| n010 | 1.00 | 5 | 5 | False | 6597 | False | 2382 / 2382 | ok |
| n013 | 1.00 | 4 | 4 | False | 4531 | False | 1845 / 1845 | ok |
| n017 | 1.00 | 5 | 5 | False | 7305 | False | 2364 / 2364 | ok |
| n019 | 1.00 | 4 | 5 | False | 4710 | False | 2215 / 2215 | ok |
| n020 | 1.00 | 5 | 5 | False | 5383 | False | 2564 / 2564 | ok |
| n023 | 1.00 | 4 | 5 | False | 4488 | False | 2063 / 2063 | ok |
| n025 | 1.00 | 4 | 5 | False | 5679 | False | 2316 / 2316 | ok |
| n027 | 1.00 | 4 | 5 | False | 4213 | False | 1925 / 1925 | ok |
| n028 | 1.00 | 4 | 5 | False | 4704 | False | 1994 / 1994 | ok |
| n029 | 1.00 | 4 | 5 | False | 5032 | False | 2059 / 2059 | ok |
| n030 | 0.00 | 4 | 4 | False | 4625 | False | 2201 / 2201 | ok |
| n032 | 1.00 | 5 | 5 | False | 8529 | False | 2326 / 2326 | ok |
| n034 | 1.00 | 5 | 5 | False | 6760 | False | 2418 / 2418 | ok |
| n035 | 1.00 | 4 | 5 | False | 5340 | False | 2415 / 2415 | ok |
| n036 | 0.00 | 4 | 5 | False | 5224 | False | 2433 / 2433 | ok |
| n039 | 1.00 | 4 | 4 | False | 5373 | False | 2252 / 2252 | ok |
| n047 | 1.00 | 4 | 4 | False | 10619 | False | 2668 / 2668 | ok |
| n048 | 1.00 | 4 | 5 | False | 5334 | False | 2440 / 2440 | ok |
| n050 | 1.00 | 4 | 4 | False | 5141 | False | 2277 / 2277 | ok |
| n051 | 0.00 | 5 | 5 | False | 9371 | False | 2652 / 2652 | ok |
| n054 | 0.00 | 2 | 1 | False | 3801 | False | 2108 / 2108 | ok |
| n055 | 1.00 | 4 | 4 | False | 4832 | False | 2329 / 2329 | ok |
| n061 | 1.00 | 5 | 5 | False | 6596 | False | 2370 / 2370 | ok |
| n067 | 1.00 | 4 | 4 | False | 5093 | False | 2258 / 2258 | ok |
| n077 | 1.00 | 4 | 5 | False | 4810 | False | 2248 / 2248 | ok |
| n083 | 1.00 | 5 | 5 | False | 5651 | False | 2066 / 2066 | ok |
| n086 | 0.00 | 4 | 4 | False | 5381 | False | 2376 / 2376 | ok |
| n091 | 1.00 | 4 | 4 | False | 5658 | False | 2460 / 2460 | ok |
| n096 | 1.00 | 4 | 4 | False | 6367 | False | 2199 / 2199 | ok |
| n097 | 0.00 | 4 | 4 | False | 4347 | False | 2174 / 2174 | ok |
| n099 | 1.00 | 4 | 5 | False | 6096 | False | 2010 / 2010 | ok |
| n105 | 1.00 | 4 | 5 | False | 4468 | False | 1874 / 1874 | ok |
| n106 | 0.50 | 4 | 5 | False | 7049 | False | 2527 / 2527 | ok |
| n112 | 1.00 | 5 | 5 | False | 5508 | False | 2426 / 2426 | ok |
| n113 | 1.00 | 5 | 5 | False | 6551 | False | 1928 / 1928 | ok |
| n115 | 0.00 | 4 | 4 | False | 7639 | False | 2495 / 2495 | ok |
| n116 | 1.00 | 5 | 5 | False | 5658 | False | 2467 / 2467 | ok |
| n120 | 1.00 | 4 | 4 | False | 5492 | False | 2261 / 2261 | ok |

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
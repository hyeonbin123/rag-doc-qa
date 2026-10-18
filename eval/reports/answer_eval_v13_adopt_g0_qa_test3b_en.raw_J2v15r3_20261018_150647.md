# Answer eval report (v13_adopt_g0_qa_test3b_en.raw, judge J2v15r3)

- date: 2026-10-18T15:06:47.239273+00:00
- generated: 2026-10-08T13:37:01.459336+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- model digest: 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J2v15r3, gemma4:12b-it-qat, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: google/gemma-4-12B-it@707f0a3
- judge order: dataset
- judge date: 2026-10-18T15:04:19.966218+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_test3b_en.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_adopt_g0_qa_test3b_en.gen.jsonl, eval/runs/v13_adopt_g0_qa_test3b_en.raw.J2v15r3.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.81 | 4.65 | 4.53 | 181 | 2/40 | 5382 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n007 | 1.00 | 5 | 5 | False | 6384 | False | 2448 / 2448 | ok |
| n008 | 1.00 | 5 | 5 | False | 4640 | False | 2477 / 2477 | ok |
| n010 | 1.00 | 5 | 5 | False | 6597 | False | 2525 / 2525 | ok |
| n013 | 1.00 | 5 | 5 | False | 4531 | False | 1908 / 1908 | ok |
| n017 | 1.00 | 5 | 5 | False | 7305 | False | 2507 / 2507 | ok |
| n019 | 1.00 | 5 | 5 | False | 4710 | False | 2342 / 2342 | ok |
| n020 | 1.00 | 5 | 5 | False | 5383 | False | 2773 / 2773 | ok |
| n023 | 1.00 | 5 | 5 | False | 4488 | False | 2157 / 2157 | ok |
| n025 | 1.00 | 5 | 5 | False | 5679 | False | 2479 / 2479 | ok |
| n027 | 1.00 | 5 | 5 | False | 4213 | False | 2031 / 2031 | ok |
| n028 | 1.00 | 5 | 5 | False | 4704 | False | 2114 / 2114 | ok |
| n029 | 1.00 | 5 | 5 | False | 5032 | False | 2221 / 2221 | ok |
| n030 | 0.00 | 5 | 5 | False | 4625 | False | 2326 / 2326 | ok |
| n032 | 1.00 | 5 | 5 | False | 8529 | False | 2523 / 2523 | ok |
| n034 | 1.00 | 5 | 5 | False | 6760 | False | 2618 / 2618 | ok |
| n035 | 1.00 | 5 | 5 | False | 5340 | False | 2584 / 2584 | ok |
| n036 | 0.00 | 5 | 5 | False | 5224 | False | 2656 / 2656 | ok |
| n039 | 1.00 | 5 | 5 | False | 5373 | False | 2427 / 2427 | ok |
| n047 | 1.00 | 5 | 5 | False | 10619 | False | 2795 / 2795 | ok |
| n048 | 1.00 | 2 | 2 | True | 5334 | False | 2563 / 2563 | ok |
| n050 | 1.00 | 5 | 5 | False | 5141 | False | 2435 / 2435 | ok |
| n051 | 0.00 | 5 | 5 | False | 9371 | False | 2815 / 2815 | ok |
| n054 | 0.00 | 1 | 1 | False | 3801 | False | 2226 / 2226 | ok |
| n055 | 1.00 | 4 | 4 | False | 4832 | False | 2465 / 2465 | ok |
| n061 | 1.00 | 5 | 5 | False | 6596 | False | 2499 / 2499 | ok |
| n067 | 1.00 | 5 | 5 | False | 5093 | False | 2406 / 2406 | ok |
| n077 | 1.00 | 5 | 5 | False | 4810 | False | 2315 / 2315 | ok |
| n083 | 1.00 | 5 | 5 | False | 5651 | False | 2182 / 2182 | ok |
| n086 | 0.00 | 5 | 4 | False | 5381 | False | 2499 / 2499 | ok |
| n091 | 1.00 | 2 | 2 | True | 5658 | False | 2585 / 2585 | ok |
| n096 | 1.00 | 4 | 3 | False | 6367 | False | 2355 / 2355 | ok |
| n097 | 0.00 | 5 | 5 | False | 4347 | False | 2329 / 2329 | ok |
| n099 | 1.00 | 5 | 5 | False | 6096 | False | 2179 / 2179 | ok |
| n105 | 1.00 | 5 | 5 | False | 4468 | False | 1944 / 1944 | ok |
| n106 | 0.50 | 5 | 5 | False | 7049 | False | 2664 / 2664 | ok |
| n112 | 1.00 | 5 | 5 | False | 5508 | False | 2528 / 2528 | ok |
| n113 | 1.00 | 5 | 5 | False | 6551 | False | 2009 / 2009 | ok |
| n115 | 0.00 | 3 | 2 | False | 7639 | False | 2614 / 2614 | ok |
| n116 | 1.00 | 5 | 5 | False | 5658 | False | 2587 / 2587 | ok |
| n120 | 1.00 | 5 | 3 | False | 5492 | False | 2370 / 2370 | ok |

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
# Answer eval report (v13_adopt_g0_qa_test3b_en.raw, judge J3v15r1)

- date: 2026-10-18T15:33:42.560578+00:00
- generated: 2026-10-08T13:37:01.459336+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- model digest: 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J3v15r1, qwen3.5:9b, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen3.5-9B@c202236
- judge order: dataset
- judge date: 2026-10-18T15:31:52.043977+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_test3b_en.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_adopt_g0_qa_test3b_en.gen.jsonl, eval/runs/v13_adopt_g0_qa_test3b_en.raw.J3v15r1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.81 | 4.70 | 4.35 | 174 | 1/40 | 5382 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n007 | 1.00 | 5 | 4 | False | 6384 | False | 2406 / 2406 | ok |
| n008 | 1.00 | 5 | 5 | False | 4640 | False | 2438 / 2438 | ok |
| n010 | 1.00 | 5 | 5 | False | 6597 | False | 2441 / 2441 | ok |
| n013 | 1.00 | 5 | 4 | False | 4531 | False | 1903 / 1903 | ok |
| n017 | 1.00 | 5 | 5 | False | 7305 | False | 2464 / 2464 | ok |
| n019 | 1.00 | 5 | 5 | False | 4710 | False | 2270 / 2270 | ok |
| n020 | 1.00 | 5 | 5 | False | 5383 | False | 2625 / 2625 | ok |
| n023 | 1.00 | 5 | 5 | False | 4488 | False | 2107 / 2107 | ok |
| n025 | 1.00 | 5 | 5 | False | 5679 | False | 2370 / 2370 | ok |
| n027 | 1.00 | 5 | 5 | False | 4213 | False | 1969 / 1969 | ok |
| n028 | 1.00 | 5 | 5 | False | 4704 | False | 2039 / 2039 | ok |
| n029 | 1.00 | 5 | 5 | False | 5032 | False | 2112 / 2112 | ok |
| n030 | 0.00 | 5 | 5 | False | 4625 | False | 2269 / 2269 | ok |
| n032 | 1.00 | 5 | 5 | False | 8529 | False | 2407 / 2407 | ok |
| n034 | 1.00 | 5 | 5 | False | 6760 | False | 2518 / 2518 | ok |
| n035 | 1.00 | 5 | 5 | False | 5340 | False | 2493 / 2493 | ok |
| n036 | 0.00 | 5 | 4 | False | 5224 | False | 2533 / 2533 | ok |
| n039 | 1.00 | 5 | 5 | False | 5373 | False | 2323 / 2323 | ok |
| n047 | 1.00 | 5 | 4 | False | 10619 | False | 2739 / 2739 | ok |
| n048 | 1.00 | 3 | 2 | True | 5334 | False | 2476 / 2476 | ok |
| n050 | 1.00 | 5 | 4 | False | 5141 | False | 2338 / 2338 | ok |
| n051 | 0.00 | 5 | 5 | False | 9371 | False | 2731 / 2731 | ok |
| n054 | 0.00 | 2 | 2 | False | 3801 | False | 2169 / 2169 | ok |
| n055 | 1.00 | 5 | 4 | False | 4832 | False | 2395 / 2395 | ok |
| n061 | 1.00 | 5 | 5 | False | 6596 | False | 2438 / 2438 | ok |
| n067 | 1.00 | 4 | 3 | False | 5093 | False | 2321 / 2321 | ok |
| n077 | 1.00 | 5 | 5 | False | 4810 | False | 2287 / 2287 | ok |
| n083 | 1.00 | 5 | 4 | False | 5651 | False | 2125 / 2125 | ok |
| n086 | 0.00 | 4 | 3 | False | 5381 | False | 2436 / 2436 | ok |
| n091 | 1.00 | 4 | 3 | False | 5658 | False | 2512 / 2512 | ok |
| n096 | 1.00 | 4 | 3 | False | 6367 | False | 2265 / 2265 | ok |
| n097 | 0.00 | 4 | 4 | False | 4347 | False | 2222 / 2222 | ok |
| n099 | 1.00 | 5 | 5 | False | 6096 | False | 2051 / 2051 | ok |
| n105 | 1.00 | 5 | 5 | False | 4468 | False | 1918 / 1918 | ok |
| n106 | 0.50 | 5 | 5 | False | 7049 | False | 2594 / 2594 | ok |
| n112 | 1.00 | 5 | 5 | False | 5508 | False | 2466 / 2466 | ok |
| n113 | 1.00 | 5 | 5 | False | 6551 | False | 1973 / 1973 | ok |
| n115 | 0.00 | 4 | 3 | False | 7639 | False | 2586 / 2586 | ok |
| n116 | 1.00 | 5 | 5 | False | 5658 | False | 2534 / 2534 | ok |
| n120 | 1.00 | 4 | 3 | False | 5492 | False | 2303 / 2303 | ok |

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
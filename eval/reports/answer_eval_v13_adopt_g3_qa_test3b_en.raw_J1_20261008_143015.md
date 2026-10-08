# Answer eval report (v13_adopt_g3_qa_test3b_en.raw, judge J1)

- date: 2026-10-08T14:30:15.045085+00:00
- generated: 2026-10-08T14:06:00.674398+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 1/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-08T14:28:02.852501+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_test3b_en.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_adopt_g3_qa_test3b_en.gen.jsonl, eval/runs/v13_adopt_g3_qa_test3b_en.raw.J1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.85 | 4.62 | 4.75 | 190 | 0/40 | 10221 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n007 | 1.00 | 5 | 5 | False | 16150 | False | 2906 / 2906 | ok |
| n008 | 1.00 | 5 | 5 | False | 7314 | False | 2478 / 2478 | ok |
| n010 | 1.00 | 5 | 5 | False | 11099 | False | 2595 / 2595 | ok |
| n013 | 1.00 | 5 | 5 | False | 8839 | False | 2077 / 2077 | ok |
| n017 | 1.00 | 5 | 5 | False | 13403 | False | 2638 / 2638 | ok |
| n019 | 1.00 | 5 | 5 | False | 10310 | False | 2487 / 2487 | ok |
| n020 | 1.00 | 5 | 5 | False | 12946 | False | 2948 / 2948 | ok |
| n023 | 1.00 | 5 | 5 | False | 15526 | False | 2670 / 2670 | ok |
| n025 | 1.00 | 4 | 5 | False | 7445 | False | 2347 / 2347 | ok |
| n027 | 1.00 | 5 | 5 | False | 8966 | False | 2177 / 2177 | ok |
| n028 | 1.00 | 4 | 5 | False | 5332 | False | 1986 / 1986 | ok |
| n029 | 1.00 | 5 | 5 | False | 6362 | False | 2097 / 2097 | ok |
| n030 | 0.00 | 4 | 4 | False | 5999 | False | 2251 / 2251 | ok |
| n032 | 1.00 | 5 | 5 | False | 10420 | False | 2362 / 2362 | ok |
| n034 | 1.00 | 5 | 5 | False | 19760 | False | 3108 / 3108 | ok |
| n035 | 1.00 | 5 | 5 | False | 12348 | False | 2788 / 2788 | ok |
| n036 | 0.00 | 4 | 4 | False | 14881 | False | 2904 / 2904 | ok |
| n039 | 1.00 | 5 | 5 | False | 13801 | False | 2681 / 2681 | ok |
| n047 | 1.00 | 4 | 4 | False | 21212 | False | 3085 / 3085 | ok |
| n048 | 0.00 | 4 | 5 | False | 5081 | False | 2389 / 2389 | ok |
| n050 | 1.00 | 5 | 5 | False | 10072 | False | 2489 / 2489 | ok |
| n051 | 1.00 | 5 | 5 | False | 13566 | False | 2799 / 2799 | ok |
| n054 | 1.00 | 4 | 4 | False | 11383 | False | 2458 / 2458 | ok |
| n055 | 1.00 | 4 | 5 | False | 7101 | False | 2419 / 2419 | ok |
| n061 | 1.00 | 5 | 5 | False | 10132 | False | 2501 / 2501 | ok |
| n067 | 1.00 | 4 | 4 | False | 13307 | False | 2685 / 2685 | ok |
| n077 | 1.00 | 5 | 5 | False | 10117 | False | 2512 / 2512 | ok |
| n083 | 1.00 | 5 | 5 | False | 12309 | False | 2391 / 2391 | ok |
| n086 | 0.00 | 4 | 4 | False | 8803 | False | 2543 / 2543 | ok |
| n091 | 1.00 | 5 | 5 | False | 12810 | False | 2862 / 2862 | ok |
| n096 | 1.00 | 4 | 4 | False | 13989 | False | 2583 / 2583 | ok |
| n097 | 1.00 | 4 | 4 | False | 6702 | False | 2284 / 2284 | ok |
| n099 | 0.50 | 5 | 5 | False | 9144 | False | 2174 / 2174 | ok |
| n105 | 1.00 | 5 | 5 | False | 6916 | False | 1974 / 1974 | ok |
| n106 | 0.50 | 4 | 5 | False | 6218 | False | 2456 / 2456 | ok |
| n112 | 1.00 | 5 | 5 | False | 5861 | False | 2422 / 2422 | ok |
| n113 | 1.00 | 5 | 5 | False | 9126 | False | 2050 / 2050 | ok |
| n115 | 0.00 | 4 | 4 | False | 13426 | False | 2827 / 2827 | ok |
| n116 | 1.00 | 5 | 5 | False | 9050 | False | 2621 / 2621 | ok |
| n120 | 1.00 | 4 | 4 | False | 20252 | False | 3046 / 3046 | ok |

## Worst questions (lowest keyword coverage)

- **n030** (0.00): When reading a header value with Header, what does it mean that underscores are automatically converted to hyphens?
  > Underscores in header parameter names are automatically converted to hyphens by FastAPI when using the `Header` class. This means that if you define a header parameter as `user_agent`, the correspondi
- **n036** (0.00): Is there a way to override the RequestValidationError handler while still reusing FastAPI's default handler behavior?
  > Yes, you can override the `RequestValidationError` handler while still reusing FastAPI's default handler behavior by following these steps:

1. **Import the necessary modules**: Import `RequestValidat
- **n048** (0.00): Which library is good for issuing and verifying JWT tokens?
  > You don't know which specific library is recommended for issuing and verifying JWT tokens based on the provided context passages.
- **n086** (0.00): Does using ORJSONResponse instead of the default JSONResponse improve performance?
  > Yes, using `ORJSONResponse` instead of the default `JSONResponse` can improve performance.

`ORJSONResponse` is a subclass of `Response` that uses the `orjson` library for serialization, which is know
- **n115** (0.00): I am definitely sending a JSON body, but I keep getting 422 Unprocessable Entity. What am I doing wrong?
  > You are likely sending a JSON body that does not match the expected schema defined by your Pydantic model. FastAPI will validate the incoming JSON against the model you declared. If the data does not 
# Answer eval report (v13_adopt_g3_qa_test3b_en.raw, judge J3v15r3)

- date: 2026-10-18T16:15:57.038935+00:00
- generated: 2026-10-08T14:06:00.674398+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 1/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J3v15r3, qwen3.5:9b, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen3.5-9B@c202236
- judge order: dataset
- judge date: 2026-10-18T16:14:02.379251+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_test3b_en.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_adopt_g3_qa_test3b_en.gen.jsonl, eval/runs/v13_adopt_g3_qa_test3b_en.raw.J3v15r3.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.85 | 4.60 | 4.22 | 169 | 0/40 | 10221 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n007 | 1.00 | 4 | 3 | False | 16150 | False | 2972 / 2972 | ok |
| n008 | 1.00 | 5 | 5 | False | 7314 | False | 2567 / 2567 | ok |
| n010 | 1.00 | 5 | 5 | False | 11099 | False | 2686 / 2686 | ok |
| n013 | 1.00 | 4 | 3 | False | 8839 | False | 2149 / 2149 | ok |
| n017 | 1.00 | 5 | 5 | False | 13403 | False | 2758 / 2758 | ok |
| n019 | 1.00 | 5 | 5 | False | 10310 | False | 2553 / 2553 | ok |
| n020 | 1.00 | 5 | 5 | False | 12946 | False | 3036 / 3036 | ok |
| n023 | 1.00 | 4 | 3 | False | 15526 | False | 2736 / 2736 | ok |
| n025 | 1.00 | 5 | 5 | False | 7445 | False | 2404 / 2404 | ok |
| n027 | 1.00 | 5 | 5 | False | 8966 | False | 2234 / 2234 | ok |
| n028 | 1.00 | 5 | 5 | False | 5332 | False | 2031 / 2031 | ok |
| n029 | 1.00 | 5 | 5 | False | 6362 | False | 2151 / 2151 | ok |
| n030 | 0.00 | 5 | 5 | False | 5999 | False | 2319 / 2319 | ok |
| n032 | 1.00 | 5 | 5 | False | 10420 | False | 2446 / 2446 | ok |
| n034 | 1.00 | 4 | 3 | False | 19760 | False | 3239 / 3239 | ok |
| n035 | 1.00 | 5 | 5 | False | 12348 | False | 2900 / 2900 | ok |
| n036 | 0.00 | 4 | 3 | False | 14881 | False | 3023 / 3023 | ok |
| n039 | 1.00 | 5 | 5 | False | 13801 | False | 2774 / 2774 | ok |
| n047 | 1.00 | 5 | 5 | False | 21212 | False | 3199 / 3199 | ok |
| n048 | 0.00 | 2 | 1 | False | 5081 | False | 2425 / 2425 | ok |
| n050 | 1.00 | 4 | 3 | False | 10072 | False | 2562 / 2562 | ok |
| n051 | 1.00 | 5 | 5 | False | 13566 | False | 2879 / 2879 | ok |
| n054 | 1.00 | 4 | 3 | False | 11383 | False | 2535 / 2535 | ok |
| n055 | 1.00 | 5 | 5 | False | 7101 | False | 2488 / 2488 | ok |
| n061 | 1.00 | 5 | 5 | False | 10132 | False | 2562 / 2562 | ok |
| n067 | 1.00 | 4 | 3 | False | 13307 | False | 2767 / 2767 | ok |
| n077 | 1.00 | 5 | 5 | False | 10117 | False | 2565 / 2565 | ok |
| n083 | 1.00 | 5 | 5 | False | 12309 | False | 2469 / 2469 | ok |
| n086 | 0.00 | 4 | 2 | False | 8803 | False | 2608 / 2608 | ok |
| n091 | 1.00 | 4 | 3 | False | 12810 | False | 2938 / 2938 | ok |
| n096 | 1.00 | 4 | 3 | False | 13989 | False | 2656 / 2656 | ok |
| n097 | 1.00 | 5 | 5 | False | 6702 | False | 2332 / 2332 | ok |
| n099 | 0.50 | 5 | 5 | False | 9144 | False | 2225 / 2225 | ok |
| n105 | 1.00 | 5 | 5 | False | 6916 | False | 2027 / 2027 | ok |
| n106 | 0.50 | 5 | 5 | False | 6218 | False | 2517 / 2517 | ok |
| n112 | 1.00 | 5 | 5 | False | 5861 | False | 2462 / 2462 | ok |
| n113 | 1.00 | 5 | 5 | False | 9126 | False | 2103 / 2103 | ok |
| n115 | 0.00 | 4 | 3 | False | 13426 | False | 2927 / 2927 | ok |
| n116 | 1.00 | 5 | 5 | False | 9050 | False | 2699 / 2699 | ok |
| n120 | 1.00 | 4 | 3 | False | 20252 | False | 3144 / 3144 | ok |

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
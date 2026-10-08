# Answer eval report (v13_adopt_g3_qa_test3b_en)

- date: 2026-10-08T14:13:26.472518+00:00
- generated: 2026-10-08T14:06:00.674398+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 1/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_test3b_en.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_adopt_g3_qa_test3b_en.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.85 | n/a | n/a | n/a | 0/0 | 10221 | 0/40 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n007 | 1.00 | None | None | None | 16150 | False | None / None | - |
| n008 | 1.00 | None | None | None | 7314 | False | None / None | - |
| n010 | 1.00 | None | None | None | 11099 | False | None / None | - |
| n013 | 1.00 | None | None | None | 8839 | False | None / None | - |
| n017 | 1.00 | None | None | None | 13403 | False | None / None | - |
| n019 | 1.00 | None | None | None | 10310 | False | None / None | - |
| n020 | 1.00 | None | None | None | 12946 | False | None / None | - |
| n023 | 1.00 | None | None | None | 15526 | False | None / None | - |
| n025 | 1.00 | None | None | None | 7445 | False | None / None | - |
| n027 | 1.00 | None | None | None | 8966 | False | None / None | - |
| n028 | 1.00 | None | None | None | 5332 | False | None / None | - |
| n029 | 1.00 | None | None | None | 6362 | False | None / None | - |
| n030 | 0.00 | None | None | None | 5999 | False | None / None | - |
| n032 | 1.00 | None | None | None | 10420 | False | None / None | - |
| n034 | 1.00 | None | None | None | 19760 | False | None / None | - |
| n035 | 1.00 | None | None | None | 12348 | False | None / None | - |
| n036 | 0.00 | None | None | None | 14881 | False | None / None | - |
| n039 | 1.00 | None | None | None | 13801 | False | None / None | - |
| n047 | 1.00 | None | None | None | 21212 | False | None / None | - |
| n048 | 0.00 | None | None | None | 5081 | False | None / None | - |
| n050 | 1.00 | None | None | None | 10072 | False | None / None | - |
| n051 | 1.00 | None | None | None | 13566 | False | None / None | - |
| n054 | 1.00 | None | None | None | 11383 | False | None / None | - |
| n055 | 1.00 | None | None | None | 7101 | False | None / None | - |
| n061 | 1.00 | None | None | None | 10132 | False | None / None | - |
| n067 | 1.00 | None | None | None | 13307 | False | None / None | - |
| n077 | 1.00 | None | None | None | 10117 | False | None / None | - |
| n083 | 1.00 | None | None | None | 12309 | False | None / None | - |
| n086 | 0.00 | None | None | None | 8803 | False | None / None | - |
| n091 | 1.00 | None | None | None | 12810 | False | None / None | - |
| n096 | 1.00 | None | None | None | 13989 | False | None / None | - |
| n097 | 1.00 | None | None | None | 6702 | False | None / None | - |
| n099 | 0.50 | None | None | None | 9144 | False | None / None | - |
| n105 | 1.00 | None | None | None | 6916 | False | None / None | - |
| n106 | 0.50 | None | None | None | 6218 | False | None / None | - |
| n112 | 1.00 | None | None | None | 5861 | False | None / None | - |
| n113 | 1.00 | None | None | None | 9126 | False | None / None | - |
| n115 | 0.00 | None | None | None | 13426 | False | None / None | - |
| n116 | 1.00 | None | None | None | 9050 | False | None / None | - |
| n120 | 1.00 | None | None | None | 20252 | False | None / None | - |

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
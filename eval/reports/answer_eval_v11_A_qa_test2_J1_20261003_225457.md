# Answer eval report (v11_A_qa_test2, judge J1)

- date: 2026-10-03T22:54:57.386023+00:00
- generated: 2026-10-03T22:33:36.863404+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- judge: J1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-03T22:53:31.937605+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- dataset: qa_test2.jsonl
- questions: 43
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v11_A_qa_test2.gen.jsonl, eval/runs/v11_A_qa_test2.J1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.88 | 4.14 | 4.60 | 198 | 0/43 | 4108 | 0/43 | 0/43 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| t001 | 1.00 | 2 | 2 | False | 3807 | False | 2361 / 2361 | ok |
| t002 | 1.00 | 5 | 5 | False | 5049 | False | 2532 / 2532 | ok |
| t003 | 1.00 | 4 | 5 | False | 5432 | False | 2179 / 2179 | ok |
| t004 | 1.00 | 5 | 5 | False | 4358 | False | 2302 / 2302 | ok |
| t005 | 1.00 | 4 | 5 | False | 4487 | False | 2263 / 2263 | ok |
| t006 | 1.00 | 4 | 5 | False | 6329 | False | 2379 / 2379 | ok |
| t007 | 1.00 | 4 | 5 | False | 3711 | False | 2178 / 2178 | ok |
| t008 | 0.00 | 2 | 2 | False | 3154 | False | 2036 / 2036 | ok |
| t009 | 0.00 | 4 | 4 | False | 3624 | False | 2102 / 2102 | ok |
| t010 | 0.00 | 4 | 4 | False | 6333 | False | 2235 / 2235 | ok |
| t011 | 1.00 | 4 | 4 | False | 3144 | False | 1379 / 1379 | ok |
| t012 | 1.00 | 4 | 5 | False | 4047 | False | 2441 / 2441 | ok |
| t013 | 1.00 | 5 | 5 | False | 6184 | False | 2310 / 2310 | ok |
| t014 | 1.00 | 4 | 5 | False | 3686 | False | 2247 / 2247 | ok |
| t015 | 1.00 | 4 | 5 | False | 3555 | False | 1881 / 1881 | ok |
| t016 | 1.00 | 4 | 5 | False | 3585 | False | 1958 / 1958 | ok |
| t017 | 1.00 | 4 | 5 | False | 3791 | False | 1791 / 1791 | ok |
| t018 | 1.00 | 3 | 3 | False | 3720 | False | 2219 / 2219 | ok |
| t019 | 1.00 | 4 | 4 | False | 5189 | False | 2573 / 2573 | ok |
| t020 | 1.00 | 4 | 5 | False | 3343 | False | 1862 / 1862 | ok |
| t021 | 1.00 | 4 | 5 | False | 3188 | False | 1936 / 1936 | ok |
| t022 | 1.00 | 5 | 5 | False | 4247 | False | 2192 / 2192 | ok |
| t023 | 1.00 | 5 | 5 | False | 4108 | False | 2362 / 2362 | ok |
| t024 | 1.00 | 5 | 5 | False | 3527 | False | 2225 / 2225 | ok |
| t025 | 1.00 | 5 | 5 | False | 3699 | False | 1821 / 1821 | ok |
| t026 | 1.00 | 4 | 5 | False | 4479 | False | 2375 / 2375 | ok |
| t027 | 1.00 | 5 | 5 | False | 4943 | False | 2369 / 2369 | ok |
| t028 | 1.00 | 5 | 5 | False | 4219 | False | 2429 / 2429 | ok |
| t029 | 1.00 | 4 | 5 | False | 5558 | False | 2500 / 2500 | ok |
| t030 | 1.00 | 4 | 4 | False | 8204 | False | 2773 / 2773 | ok |
| t031 | 1.00 | 4 | 5 | False | 4047 | False | 2214 / 2214 | ok |
| t032 | 1.00 | 4 | 5 | False | 3957 | False | 2207 / 2207 | ok |
| t033 | 1.00 | 4 | 4 | False | 5694 | False | 2325 / 2325 | ok |
| t034 | 1.00 | 5 | 5 | False | 4536 | False | 2379 / 2379 | ok |
| t035 | 0.00 | 4 | 4 | False | 3723 | False | 2383 / 2383 | ok |
| t036 | 1.00 | 4 | 5 | False | 3282 | False | 1932 / 1932 | ok |
| t037 | 1.00 | 4 | 5 | False | 3966 | False | 2087 / 2087 | ok |
| t038 | 1.00 | 4 | 5 | False | 4256 | False | 2650 / 2650 | ok |
| t039 | 1.00 | 4 | 4 | False | 4902 | False | 2293 / 2293 | ok |
| t040 | 1.00 | 4 | 5 | False | 4552 | False | 2187 / 2187 | ok |
| t041 | 1.00 | 4 | 5 | False | 4383 | False | 2559 / 2559 | ok |
| t042 | 1.00 | 5 | 5 | False | 3826 | False | 2007 / 2007 | ok |
| t043 | 0.00 | 4 | 4 | False | 6296 | False | 2629 / 2629 | ok |

## Worst questions (lowest keyword coverage)

- **t008** (0.00): How can I log how long every request takes?
  > I don't know how to log the duration of every request based on the provided context passages.
- **t009** (0.00): How can I stream a large file to the client instead of loading it all into memory?
  > You can use the `UploadFile` type from `fastapi` instead of `bytes` for the file parameter. This allows the file to be stored in memory up to a certain limit and then spilled to disk, making it suitab
- **t010** (0.00): How do I let the user download a file from an endpoint?
  > You don't have a direct passage about letting the user download a file from an endpoint, but you can infer a solution from the context provided. Specifically, you can use a `StreamingResponse` to stre
- **t035** (0.00): How do I return plain text instead of JSON?
  > You can return a `Response` directly and put your plain text content inside it. FastAPI won't do any automatic data conversion or serialization in this case, giving you full control over the response.
- **t043** (0.00): How do I add a field that the client sends but that should never be shown in the docs?
  > You don't need to explicitly hide a field from the docs; FastAPI will only document fields that are part of the Pydantic model you use for the request body. If you have a field that you want to receiv
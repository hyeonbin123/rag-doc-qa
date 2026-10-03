# Answer eval report (v11_B_qa_test2)

- date: 2026-10-03T22:48:20.561726+00:00
- generated: 2026-10-03T22:45:03.415557+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- dataset: qa_test2.jsonl
- questions: 43
- generation order: shuffle (seed 20261003)
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v11_B_qa_test2.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.88 | n/a | n/a | n/a | 0/0 | 4158 | 0/43 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| t001 | 1.00 | None | None | None | 3810 | False | None / None | - |
| t002 | 1.00 | None | None | None | 5075 | False | None / None | - |
| t003 | 1.00 | None | None | None | 5489 | False | None / None | - |
| t004 | 1.00 | None | None | None | 4389 | False | None / None | - |
| t005 | 1.00 | None | None | None | 4309 | False | None / None | - |
| t006 | 1.00 | None | None | None | 6330 | False | None / None | - |
| t007 | 1.00 | None | None | None | 3705 | False | None / None | - |
| t008 | 0.00 | None | None | None | 3136 | False | None / None | - |
| t009 | 0.00 | None | None | None | 3655 | False | None / None | - |
| t010 | 0.00 | None | None | None | 6376 | False | None / None | - |
| t011 | 1.00 | None | None | None | 3130 | False | None / None | - |
| t012 | 1.00 | None | None | None | 4158 | False | None / None | - |
| t013 | 1.00 | None | None | None | 6173 | False | None / None | - |
| t014 | 1.00 | None | None | None | 3666 | False | None / None | - |
| t015 | 1.00 | None | None | None | 3572 | False | None / None | - |
| t016 | 1.00 | None | None | None | 3599 | False | None / None | - |
| t017 | 1.00 | None | None | None | 3811 | False | None / None | - |
| t018 | 1.00 | None | None | None | 3758 | False | None / None | - |
| t019 | 1.00 | None | None | None | 5184 | False | None / None | - |
| t020 | 1.00 | None | None | None | 3369 | False | None / None | - |
| t021 | 1.00 | None | None | None | 3216 | False | None / None | - |
| t022 | 1.00 | None | None | None | 4250 | False | None / None | - |
| t023 | 1.00 | None | None | None | 4136 | False | None / None | - |
| t024 | 1.00 | None | None | None | 3510 | False | None / None | - |
| t025 | 1.00 | None | None | None | 3711 | False | None / None | - |
| t026 | 1.00 | None | None | None | 4488 | False | None / None | - |
| t027 | 1.00 | None | None | None | 5082 | False | None / None | - |
| t028 | 1.00 | None | None | None | 4199 | False | None / None | - |
| t029 | 1.00 | None | None | None | 5591 | False | None / None | - |
| t030 | 1.00 | None | None | None | 8204 | False | None / None | - |
| t031 | 1.00 | None | None | None | 3982 | False | None / None | - |
| t032 | 1.00 | None | None | None | 3912 | False | None / None | - |
| t033 | 1.00 | None | None | None | 5680 | False | None / None | - |
| t034 | 1.00 | None | None | None | 4551 | False | None / None | - |
| t035 | 0.00 | None | None | None | 3732 | False | None / None | - |
| t036 | 1.00 | None | None | None | 3311 | False | None / None | - |
| t037 | 1.00 | None | None | None | 3984 | False | None / None | - |
| t038 | 1.00 | None | None | None | 4307 | False | None / None | - |
| t039 | 1.00 | None | None | None | 4933 | False | None / None | - |
| t040 | 1.00 | None | None | None | 4550 | False | None / None | - |
| t041 | 1.00 | None | None | None | 4456 | False | None / None | - |
| t042 | 1.00 | None | None | None | 3767 | False | None / None | - |
| t043 | 0.00 | None | None | None | 6377 | False | None / None | - |

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
# Answer eval report (v8b_test2_dense)

- date: 2026-09-12T11:50:40.151470+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- top_k: 5
- retrieval mode: dense
- dataset: qa_test2.jsonl
- questions: 43
- judge skipped: False

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Hallucinated |
|---|---|---|---|
| 0.79 | 4.12 | 4.60 | 0/43 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated |
|---|---|---|---|---|
| t001 | 1.00 | 2 | 2 | False |
| t002 | 1.00 | 5 | 5 | False |
| t003 | 1.00 | 4 | 5 | False |
| t004 | 1.00 | 5 | 5 | False |
| t005 | 1.00 | 4 | 5 | False |
| t006 | 1.00 | 4 | 5 | False |
| t007 | 1.00 | 4 | 5 | False |
| t008 | 0.00 | 2 | 2 | False |
| t009 | 0.00 | 4 | 4 | False |
| t010 | 0.00 | 4 | 4 | False |
| t011 | 1.00 | 4 | 4 | False |
| t012 | 1.00 | 5 | 5 | False |
| t013 | 1.00 | 4 | 5 | False |
| t014 | 1.00 | 4 | 5 | False |
| t015 | 1.00 | 4 | 5 | False |
| t016 | 1.00 | 4 | 5 | False |
| t017 | 1.00 | 4 | 4 | False |
| t018 | 1.00 | 3 | 3 | False |
| t019 | 1.00 | 4 | 5 | False |
| t020 | 0.00 | 4 | 5 | False |
| t021 | 1.00 | 4 | 5 | False |
| t022 | 1.00 | 5 | 5 | False |
| t023 | 1.00 | 5 | 5 | False |
| t024 | 1.00 | 5 | 5 | False |
| t025 | 1.00 | 5 | 5 | False |
| t026 | 0.00 | 4 | 5 | False |
| t027 | 1.00 | 5 | 5 | False |
| t028 | 1.00 | 5 | 5 | False |
| t029 | 1.00 | 4 | 5 | False |
| t030 | 0.00 | 3 | 4 | False |
| t031 | 1.00 | 4 | 5 | False |
| t032 | 1.00 | 4 | 5 | False |
| t033 | 0.00 | 4 | 4 | False |
| t034 | 1.00 | 5 | 5 | False |
| t035 | 0.00 | 4 | 4 | False |
| t036 | 1.00 | 4 | 5 | False |
| t037 | 1.00 | 4 | 5 | False |
| t038 | 1.00 | 4 | 5 | False |
| t039 | 1.00 | 4 | 4 | False |
| t040 | 1.00 | 4 | 5 | False |
| t041 | 1.00 | 4 | 5 | False |
| t042 | 1.00 | 5 | 5 | False |
| t043 | 0.00 | 4 | 4 | False |

## Worst questions (lowest keyword coverage)

- **t008** (0.00): How can I log how long every request takes?
  > I don't know how to log the duration of every request based on the provided context passages.
- **t009** (0.00): How can I stream a large file to the client instead of loading it all into memory?
  > You can use the `UploadFile` type from `fastapi` instead of `bytes` for the file parameter. This allows the file to be stored in memory up to a maximum size limit, and after passing this limit it will
- **t010** (0.00): How do I let the user download a file from an endpoint?
  > You don't have a direct passage about letting the user download a file from an endpoint, but you can infer a solution from the context provided. Specifically, you can use a `StreamingResponse` to stre
- **t020** (0.00): How do I upload several files in one request?
  > To upload several files in one request, you can declare multiple `File` or `UploadFile` parameters in your path operation function.
- **t026** (0.00): What's the difference between declaring my endpoint with def and with async def?
  > If your endpoint uses code that performs blocking I/O, you should declare it with `def`. Otherwise, for trivial compute-only operations, you should declare it with `async def` to take advantage of Fas
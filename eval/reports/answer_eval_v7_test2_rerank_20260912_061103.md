# Answer eval report (v7_test2_rerank)

- date: 2026-09-12T06:11:03.090005+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- top_k: 5
- retrieval mode: rerank
- dataset: qa_test2.jsonl
- questions: 43
- judge skipped: False

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Hallucinated |
|---|---|---|---|
| 0.88 | 4.23 | 4.60 | 0/43 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated |
|---|---|---|---|---|
| t001 | 1.00 | 4 | 5 | False |
| t002 | 1.00 | 5 | 5 | False |
| t003 | 1.00 | 4 | 4 | False |
| t004 | 1.00 | 5 | 5 | False |
| t005 | 1.00 | 4 | 5 | False |
| t006 | 1.00 | 4 | 5 | False |
| t007 | 1.00 | 5 | 5 | False |
| t008 | 1.00 | 3 | 3 | False |
| t009 | 0.00 | 3 | 4 | False |
| t010 | 1.00 | 4 | 4 | False |
| t011 | 1.00 | 4 | 5 | False |
| t012 | 1.00 | 5 | 5 | False |
| t013 | 1.00 | 4 | 5 | False |
| t014 | 1.00 | 5 | 5 | False |
| t015 | 0.00 | 4 | 5 | False |
| t016 | 1.00 | 4 | 5 | False |
| t017 | 1.00 | 4 | 5 | False |
| t018 | 1.00 | 4 | 4 | False |
| t019 | 1.00 | 4 | 5 | False |
| t020 | 0.00 | 4 | 5 | False |
| t021 | 1.00 | 4 | 4 | False |
| t022 | 1.00 | 5 | 5 | False |
| t023 | 1.00 | 5 | 5 | False |
| t024 | 1.00 | 5 | 5 | False |
| t025 | 1.00 | 5 | 5 | False |
| t026 | 1.00 | 4 | 4 | False |
| t027 | 1.00 | 5 | 5 | False |
| t028 | 1.00 | 5 | 5 | False |
| t029 | 1.00 | 4 | 5 | False |
| t030 | 0.00 | 3 | 2 | False |
| t031 | 1.00 | 5 | 5 | False |
| t032 | 1.00 | 4 | 5 | False |
| t033 | 1.00 | 4 | 5 | False |
| t034 | 1.00 | 5 | 5 | False |
| t035 | 1.00 | 4 | 5 | False |
| t036 | 1.00 | 3 | 2 | False |
| t037 | 1.00 | 4 | 4 | False |
| t038 | 1.00 | 4 | 5 | False |
| t039 | 1.00 | 4 | 5 | False |
| t040 | 1.00 | 5 | 5 | False |
| t041 | 1.00 | 4 | 5 | False |
| t042 | 1.00 | 5 | 5 | False |
| t043 | 0.00 | 3 | 3 | False |

## Worst questions (lowest keyword coverage)

- **t009** (0.00): How can I stream a large file to the client instead of loading it all into memory?
  > You can use the `UploadFile` type from `fastapi` instead of `bytes`. This allows the file to be stored in memory up to a maximum size limit, and after passing this limit it will be stored on disk, thu
- **t015** (0.00): How do I check that an email field in the request really is an email address?
  > You don't have a direct method to check if an email field in the request is a valid email address using FastAPI's built-in features based on the provided context. However, you can use Python's `email`
- **t020** (0.00): How do I upload several files in one request?
  > It's possible to upload several files at the same time.
- **t030** (0.00): How do I push updates to the browser in real time over one open HTTP connection?
  > You can use WebSockets to push updates to the browser in real time over one open HTTP connection. FastAPI supports WebSockets, allowing you to maintain a single connection for sending and receiving mu
- **t043** (0.00): How do I add a field that the client sends but that should never be shown in the docs?
  > You can declare a field in your Pydantic model that you don't want to appear in the docs by using the `Form` parameter when defining the field. This way, the field will be processed as a form field, b
# Answer eval report (v15_i4_ucand_qa_test2)

- date: 2026-10-18T13:42:46.934430+00:00
- generated: 2026-10-18T13:41:36.869557+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/14)
- final answer call stopped by the output limit, done_reason=length: 0/14; reasoning output: 0/14; citation replies breaking the schema: 0/14
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_test2.jsonl
- questions: 14
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_ucand_qa_test2.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.50 | n/a | n/a | n/a | 0/0 | 5057 | 0/14 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| t001 | 0.00 | None | None | None | 0 | False | None / None | - |
| t002 | 1.00 | None | None | None | 4850 | False | None / None | - |
| t003 | 1.00 | None | None | None | 10564 | False | None / None | - |
| t006 | 0.00 | None | None | None | 0 | False | None / None | - |
| t008 | 0.00 | None | None | None | 1902 | False | None / None | - |
| t010 | 0.00 | None | None | None | 5917 | False | None / None | - |
| t011 | 1.00 | None | None | None | 5265 | False | None / None | - |
| t013 | 0.00 | None | None | None | 0 | False | None / None | - |
| t014 | 1.00 | None | None | None | 7630 | False | None / None | - |
| t015 | 0.00 | None | None | None | 0 | False | None / None | - |
| t016 | 1.00 | None | None | None | 9028 | False | None / None | - |
| t019 | 1.00 | None | None | None | 7533 | False | None / None | - |
| t030 | 1.00 | None | None | None | 8719 | False | None / None | - |
| t043 | 0.00 | None | None | None | 0 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **t001** (0.00): My React app on localhost:3000 gets blocked when it calls my API on port 8000. How do I fix it?
  > I don't know: the documentation passages I found do not cover this question.
- **t006** (0.00): How do I protect an endpoint so only logged-in users can call it?
  > I don't know: the documentation passages I found do not cover this question.
- **t008** (0.00): How can I log how long every request takes?
  > You don't know.
- **t010** (0.00): How do I let the user download a file from an endpoint?
  > You don't need to use `UploadFile` to let the user download a file. Instead, you can use the `File` type to send a file as a response. Here's how you can do it:

```python
from fastapi import FastAPI,
- **t013** (0.00): How can I group my endpoints into sections in the docs page?
  > I don't know: the documentation passages I found do not cover this question.
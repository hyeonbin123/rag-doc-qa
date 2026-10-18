# Answer eval report (v15_i4_ucand_qa_test2, judge J1v15r3)

- date: 2026-10-18T14:05:40.520018+00:00
- generated: 2026-10-18T13:41:36.869557+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/14)
- final answer call stopped by the output limit, done_reason=length: 0/14; reasoning output: 0/14; citation replies breaking the schema: 0/14
- judge: J1v15r3, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-18T14:05:25.893202+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_test2.jsonl
- questions: 14
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_ucand_qa_test2.gen.jsonl, eval/runs/v15_i4_ucand_qa_test2.J1v15r3.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.50 | 4.11 | 4.44 | 40 | 0/9 | 5057 | 0/14 | 0/9 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| t001 | 0.00 | None | None | None | 0 | False | None / None | unchecked |
| t002 | 1.00 | 5 | 5 | False | 4850 | False | 2150 / 2150 | ok |
| t003 | 1.00 | 4 | 5 | False | 10564 | False | 2107 / 2107 | ok |
| t006 | 0.00 | None | None | None | 0 | False | None / None | unchecked |
| t008 | 0.00 | 3 | 4 | False | 1902 | False | 292 / 292 | ok |
| t010 | 0.00 | 4 | 4 | False | 5917 | False | 515 / 515 | ok |
| t011 | 1.00 | 4 | 5 | False | 5265 | False | 1116 / 1116 | ok |
| t013 | 0.00 | None | None | None | 0 | False | None / None | unchecked |
| t014 | 1.00 | 4 | 4 | False | 7630 | False | 928 / 928 | ok |
| t015 | 0.00 | None | None | None | 0 | False | None / None | unchecked |
| t016 | 1.00 | 4 | 4 | False | 9028 | False | 2314 / 2314 | ok |
| t019 | 1.00 | 5 | 5 | False | 7533 | False | 957 / 957 | ok |
| t030 | 1.00 | 4 | 4 | False | 8719 | False | 1490 / 1490 | ok |
| t043 | 0.00 | None | None | None | 0 | False | None / None | unchecked |

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
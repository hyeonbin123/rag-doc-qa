# Answer eval report (v16b_a_qa_dev)

- date: 2026-11-03T15:09:03.299108+00:00
- generated: 2026-11-03T15:04:59.726139+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- corpus: source commit 50113da (277 documents); last fetched 2026-11-03T08:04:42.172603+00:00; chunks en 914, ko 621
- dataset: qa_dev.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_a_qa_dev.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | n/a | n/a | n/a | 0/0 | 7864 | 0/32 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| d001 | 1.00 | None | None | None | 7333 | False | None / None | - |
| d002 | 1.00 | None | None | None | 5495 | False | None / None | - |
| d003 | 1.00 | None | None | None | 8027 | False | None / None | - |
| d004 | 0.00 | None | None | None | 5579 | False | None / None | - |
| d005 | 1.00 | None | None | None | 4524 | False | None / None | - |
| d006 | 1.00 | None | None | None | 3505 | False | None / None | - |
| d007 | 1.00 | None | None | None | 9059 | False | None / None | - |
| d008 | 1.00 | None | None | None | 15163 | False | None / None | - |
| d009 | 1.00 | None | None | None | 11779 | False | None / None | - |
| d010 | 1.00 | None | None | None | 4427 | False | None / None | - |
| d011 | 1.00 | None | None | None | 9496 | False | None / None | - |
| d012 | 1.00 | None | None | None | 10098 | False | None / None | - |
| d013 | 1.00 | None | None | None | 5540 | False | None / None | - |
| d014 | 1.00 | None | None | None | 4220 | False | None / None | - |
| d015 | 1.00 | None | None | None | 8666 | False | None / None | - |
| d016 | 1.00 | None | None | None | 11611 | False | None / None | - |
| d017 | 1.00 | None | None | None | 10775 | False | None / None | - |
| d018 | 1.00 | None | None | None | 10970 | False | None / None | - |
| d019 | 0.00 | None | None | None | 11492 | False | None / None | - |
| d020 | 1.00 | None | None | None | 7771 | False | None / None | - |
| d021 | 1.00 | None | None | None | 8988 | False | None / None | - |
| d022 | 1.00 | None | None | None | 4509 | False | None / None | - |
| d023 | 1.00 | None | None | None | 7956 | False | None / None | - |
| d024 | 1.00 | None | None | None | 3651 | False | None / None | - |
| d025 | 0.00 | None | None | None | 1370 | False | None / None | - |
| d026 | 1.00 | None | None | None | 8010 | False | None / None | - |
| d027 | 1.00 | None | None | None | 2761 | False | None / None | - |
| d028 | 1.00 | None | None | None | 4254 | False | None / None | - |
| d029 | 1.00 | None | None | None | 4293 | False | None / None | - |
| d030 | 1.00 | None | None | None | 4375 | False | None / None | - |
| d031 | 1.00 | None | None | None | 8856 | False | None / None | - |
| d032 | 1.00 | None | None | None | 10612 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **d004** (0.00): How do you declare the type of data a path operation returns so FastAPI validates and filters it?
  > You declare the type of data a path operation returns by using the `response_model` parameter in your path operation function. For example:

```python
from fastapi import FastAPI, HTTPException
from p
- **d019** (0.00): How can one path operation return 200 when it updates an item but 201 when it creates a new one?
  > You can achieve this behavior by using different HTTP methods for creating and updating items.

Here's how you can structure your path operations:

1. **Create a new item** using the `POST` method:
  
- **d025** (0.00): Why should each Python project keep its own isolated set of installed packages?
  > I don't know.
- **d001** (1.00): How do you read a cookie value sent by the client in a path operation?
  > You read a cookie value sent by the client in a path operation by using the `Cookie` parameter from the `fastapi` module. Here's how you do it:

```python
from fastapi import FastAPI, Cookie

app = Fa
- **d002** (1.00): How do you set a cookie on the response FastAPI sends back?
  > You can set a cookie on the response by using a `Response` parameter in your path operation function or by returning a `Response` directly.

**Using a `Response` parameter:**

```python
from fastapi i
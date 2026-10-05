# Answer eval report (v13_sel_g3_qa_dev)

- date: 2026-10-05T06:03:06.590114+00:00
- generated: 2026-10-05T05:56:28.811193+00:00
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
- dataset: qa_dev.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_sel_g3_qa_dev.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | n/a | n/a | n/a | 0/0 | 13598 | 0/32 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| d001 | 1.00 | None | None | None | 8855 | False | None / None | - |
| d002 | 1.00 | None | None | None | 8951 | False | None / None | - |
| d003 | 1.00 | None | None | None | 13829 | False | None / None | - |
| d004 | 0.00 | None | None | None | 9091 | False | None / None | - |
| d005 | 1.00 | None | None | None | 7403 | False | None / None | - |
| d006 | 1.00 | None | None | None | 5858 | False | None / None | - |
| d007 | 1.00 | None | None | None | 14654 | False | None / None | - |
| d008 | 1.00 | None | None | None | 24361 | False | None / None | - |
| d009 | 1.00 | None | None | None | 19738 | False | None / None | - |
| d010 | 1.00 | None | None | None | 7046 | False | None / None | - |
| d011 | 1.00 | None | None | None | 14396 | False | None / None | - |
| d012 | 1.00 | None | None | None | 16141 | False | None / None | - |
| d013 | 1.00 | None | None | None | 6458 | False | None / None | - |
| d014 | 1.00 | None | None | None | 6745 | False | None / None | - |
| d015 | 1.00 | None | None | None | 13367 | False | None / None | - |
| d016 | 1.00 | None | None | None | 16544 | False | None / None | - |
| d017 | 1.00 | None | None | None | 16862 | False | None / None | - |
| d018 | 1.00 | None | None | None | 17701 | False | None / None | - |
| d019 | 0.00 | None | None | None | 18787 | False | None / None | - |
| d020 | 1.00 | None | None | None | 17653 | False | None / None | - |
| d021 | 1.00 | None | None | None | 15142 | False | None / None | - |
| d022 | 1.00 | None | None | None | 7877 | False | None / None | - |
| d023 | 1.00 | None | None | None | 15200 | False | None / None | - |
| d024 | 1.00 | None | None | None | 6683 | False | None / None | - |
| d025 | 0.00 | None | None | None | 6222 | False | None / None | - |
| d026 | 1.00 | None | None | None | 14525 | False | None / None | - |
| d027 | 1.00 | None | None | None | 5087 | False | None / None | - |
| d028 | 1.00 | None | None | None | 7278 | False | None / None | - |
| d029 | 1.00 | None | None | None | 7472 | False | None / None | - |
| d030 | 1.00 | None | None | None | 7044 | False | None / None | - |
| d031 | 1.00 | None | None | None | 15552 | False | None / None | - |
| d032 | 1.00 | None | None | None | 17005 | False | None / None | - |

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
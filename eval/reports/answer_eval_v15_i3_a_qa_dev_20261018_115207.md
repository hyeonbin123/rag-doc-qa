# Answer eval report (v15_i3_a_qa_dev)

- date: 2026-10-18T11:52:07.574299+00:00
- generated: 2026-10-18T11:47:32.050193+00:00
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
- per-item records: eval/runs/v15_i3_a_qa_dev.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | n/a | n/a | n/a | 0/0 | 9265 | 0/32 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| d001 | 1.00 | None | None | None | 6088 | False | None / None | - |
| d002 | 1.00 | None | None | None | 6260 | False | None / None | - |
| d003 | 1.00 | None | None | None | 9492 | False | None / None | - |
| d004 | 0.00 | None | None | None | 6370 | False | None / None | - |
| d005 | 1.00 | None | None | None | 5283 | False | None / None | - |
| d006 | 1.00 | None | None | None | 4093 | False | None / None | - |
| d007 | 1.00 | None | None | None | 10000 | False | None / None | - |
| d008 | 1.00 | None | None | None | 16610 | False | None / None | - |
| d009 | 1.00 | None | None | None | 13353 | False | None / None | - |
| d010 | 1.00 | None | None | None | 4899 | False | None / None | - |
| d011 | 1.00 | None | None | None | 9718 | False | None / None | - |
| d012 | 1.00 | None | None | None | 10742 | False | None / None | - |
| d013 | 1.00 | None | None | None | 4578 | False | None / None | - |
| d014 | 1.00 | None | None | None | 4647 | False | None / None | - |
| d015 | 1.00 | None | None | None | 9297 | False | None / None | - |
| d016 | 1.00 | None | None | None | 11280 | False | None / None | - |
| d017 | 1.00 | None | None | None | 11530 | False | None / None | - |
| d018 | 1.00 | None | None | None | 12030 | False | None / None | - |
| d019 | 0.00 | None | None | None | 12449 | False | None / None | - |
| d020 | 1.00 | None | None | None | 11434 | False | None / None | - |
| d021 | 1.00 | None | None | None | 9797 | False | None / None | - |
| d022 | 1.00 | None | None | None | 5119 | False | None / None | - |
| d023 | 1.00 | None | None | None | 9745 | False | None / None | - |
| d024 | 1.00 | None | None | None | 4327 | False | None / None | - |
| d025 | 0.00 | None | None | None | 4094 | False | None / None | - |
| d026 | 1.00 | None | None | None | 9233 | False | None / None | - |
| d027 | 1.00 | None | None | None | 3397 | False | None / None | - |
| d028 | 1.00 | None | None | None | 4744 | False | None / None | - |
| d029 | 1.00 | None | None | None | 4960 | False | None / None | - |
| d030 | 1.00 | None | None | None | 4971 | False | None / None | - |
| d031 | 1.00 | None | None | None | 10857 | False | None / None | - |
| d032 | 1.00 | None | None | None | 11913 | False | None / None | - |

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
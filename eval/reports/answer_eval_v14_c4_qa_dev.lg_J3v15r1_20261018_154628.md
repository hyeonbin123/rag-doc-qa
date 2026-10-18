# Answer eval report (v14_c4_qa_dev.lg, judge J3v15r1)

- date: 2026-10-18T15:46:28.429835+00:00
- generated: 2026-10-14T04:15:37.435282+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: J3v15r1, qwen3.5:9b, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen3.5-9B@c202236
- judge order: dataset
- judge date: 2026-10-18T15:44:56.320684+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb_c4, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_dev.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v14_c4_qa_dev.gen.jsonl, eval/runs/v14_c4_qa_dev.lg.J3v15r1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | 4.44 | 4.06 | 130 | 1/32 | 10379 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| d001 | 1.00 | 5 | 5 | False | 9897 | False | 2225 / 2225 | ok |
| d002 | 1.00 | 5 | 5 | False | 7567 | False | 2197 / 2197 | ok |
| d003 | 1.00 | 5 | 5 | False | 11321 | False | 2374 / 2374 | ok |
| d004 | 0.00 | 4 | 3 | False | 10895 | False | 2654 / 2654 | ok |
| d005 | 1.00 | 5 | 5 | False | 6382 | False | 2511 / 2511 | ok |
| d006 | 1.00 | 4 | 3 | False | 5079 | False | 2294 / 2294 | ok |
| d007 | 1.00 | 5 | 5 | False | 12751 | False | 3119 / 3119 | ok |
| d008 | 1.00 | 4 | 3 | False | 20372 | False | 3227 / 3227 | ok |
| d009 | 1.00 | 4 | 3 | False | 17778 | False | 3101 / 3101 | ok |
| d010 | 1.00 | 5 | 5 | False | 7030 | False | 2508 / 2508 | ok |
| d011 | 1.00 | 5 | 5 | False | 5899 | False | 2201 / 2201 | ok |
| d012 | 1.00 | 5 | 5 | False | 15518 | False | 2893 / 2893 | ok |
| d013 | 1.00 | 4 | 3 | False | 6586 | False | 2529 / 2529 | ok |
| d014 | 1.00 | 5 | 5 | False | 5698 | False | 2045 / 2045 | ok |
| d015 | 1.00 | 4 | 3 | False | 8268 | False | 2148 / 2148 | ok |
| d016 | 1.00 | 4 | 3 | False | 14771 | False | 2991 / 2991 | ok |
| d017 | 1.00 | 4 | 3 | False | 18398 | False | 2957 / 2957 | ok |
| d018 | 1.00 | 5 | 5 | False | 18479 | False | 3224 / 3224 | ok |
| d019 | 0.00 | 4 | 3 | False | 16481 | False | 3197 / 3197 | ok |
| d020 | 1.00 | 4 | 3 | False | 10743 | False | 2441 / 2441 | ok |
| d021 | 1.00 | 5 | 5 | False | 13418 | False | 2526 / 2526 | ok |
| d022 | 1.00 | 5 | 5 | False | 6320 | False | 2482 / 2482 | ok |
| d023 | 1.00 | 4 | 3 | False | 10171 | False | 2667 / 2667 | ok |
| d024 | 1.00 | 5 | 5 | False | 5128 | False | 2104 / 2104 | ok |
| d025 | 0.00 | 1 | 1 | True | 5005 | False | 2236 / 2236 | ok |
| d026 | 1.00 | 5 | 5 | False | 10695 | False | 2201 / 2201 | ok |
| d027 | 1.00 | 5 | 5 | False | 3870 | False | 1510 / 1510 | ok |
| d028 | 1.00 | 5 | 5 | False | 6096 | False | 2065 / 2065 | ok |
| d029 | 1.00 | 4 | 4 | False | 10588 | False | 2577 / 2577 | ok |
| d030 | 1.00 | 5 | 5 | False | 6809 | False | 2244 / 2244 | ok |
| d031 | 1.00 | 4 | 3 | False | 12903 | False | 2591 / 2591 | ok |
| d032 | 1.00 | 4 | 4 | False | 15645 | False | 2950 / 2950 | ok |

## Worst questions (lowest keyword coverage)

- **d004** (0.00): How do you declare the type of data a path operation returns so FastAPI validates and filters it?
  > You declare the type of data a path operation returns by using the `response_model` parameter in your FastAPI path operation function.

For example:

```python
from fastapi import FastAPI, HTTPExcepti
- **d019** (0.00): How can one path operation return 200 when it updates an item but 201 when it creates a new one?
  > You can achieve this behavior by using different HTTP methods for creating and updating items, and by defining appropriate responses in your FastAPI application.

Here's how you can structure your pat
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
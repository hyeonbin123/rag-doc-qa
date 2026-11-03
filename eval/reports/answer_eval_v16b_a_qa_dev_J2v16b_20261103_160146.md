# Answer eval report (v16b_a_qa_dev, judge J2v16b)

- date: 2026-11-03T16:01:46.285430+00:00
- generated: 2026-11-03T15:04:59.726139+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: J2v16b, gemma4:12b-it-qat, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: google/gemma-4-12B-it@707f0a3
- judge order: dataset
- judge date: 2026-11-03T15:59:53.973046+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_dev.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_a_qa_dev.gen.jsonl, eval/runs/v16b_a_qa_dev.J2v16b.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | 4.19 | 4.06 | 130 | 6/32 | 7864 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| d001 | 1.00 | 2 | 2 | True | 7333 | False | 2235 / 2235 | ok |
| d002 | 1.00 | 5 | 4 | False | 5495 | False | 2262 / 2262 | ok |
| d003 | 1.00 | 5 | 5 | False | 8027 | False | 2501 / 2501 | ok |
| d004 | 0.00 | 2 | 2 | True | 5579 | False | 2533 / 2533 | ok |
| d005 | 1.00 | 5 | 5 | False | 4524 | False | 2576 / 2576 | ok |
| d006 | 1.00 | 5 | 3 | False | 3505 | False | 2345 / 2345 | ok |
| d007 | 1.00 | 5 | 5 | False | 9059 | False | 3192 / 3192 | ok |
| d008 | 1.00 | 4 | 4 | False | 15163 | False | 3362 / 3362 | ok |
| d009 | 1.00 | 5 | 5 | False | 11779 | False | 2932 / 2932 | ok |
| d010 | 1.00 | 5 | 5 | False | 4427 | False | 2483 / 2483 | ok |
| d011 | 1.00 | 5 | 5 | False | 9496 | False | 2806 / 2806 | ok |
| d012 | 1.00 | 5 | 5 | False | 10098 | False | 2845 / 2845 | ok |
| d013 | 1.00 | 5 | 5 | False | 5540 | False | 2435 / 2435 | ok |
| d014 | 1.00 | 5 | 5 | False | 4220 | False | 1873 / 1873 | ok |
| d015 | 1.00 | 5 | 5 | False | 8666 | False | 2737 / 2737 | ok |
| d016 | 1.00 | 2 | 2 | True | 11611 | False | 2820 / 2820 | ok |
| d017 | 1.00 | 4 | 3 | False | 10775 | False | 2683 / 2683 | ok |
| d018 | 1.00 | 5 | 5 | False | 10970 | False | 3171 / 3171 | ok |
| d019 | 0.00 | 1 | 2 | True | 11492 | False | 3147 / 3147 | ok |
| d020 | 1.00 | 2 | 1 | True | 7771 | False | 2961 / 2961 | ok |
| d021 | 1.00 | 5 | 5 | False | 8988 | False | 2430 / 2430 | ok |
| d022 | 1.00 | 5 | 5 | False | 4509 | False | 2502 / 2502 | ok |
| d023 | 1.00 | 5 | 5 | False | 7956 | False | 2667 / 2667 | ok |
| d024 | 1.00 | 5 | 5 | False | 3651 | False | 2161 / 2161 | ok |
| d025 | 0.00 | 1 | 1 | False | 1370 | False | 2432 / 2432 | ok |
| d026 | 1.00 | 5 | 5 | False | 8010 | False | 2723 / 2723 | ok |
| d027 | 1.00 | 5 | 5 | False | 2761 | False | 1571 / 1571 | ok |
| d028 | 1.00 | 5 | 5 | False | 4254 | False | 2133 / 2133 | ok |
| d029 | 1.00 | 5 | 5 | False | 4293 | False | 2263 / 2263 | ok |
| d030 | 1.00 | 5 | 5 | False | 4375 | False | 2159 / 2159 | ok |
| d031 | 1.00 | 2 | 2 | True | 8856 | False | 2585 / 2585 | ok |
| d032 | 1.00 | 4 | 4 | False | 10612 | False | 2835 / 2835 | ok |

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
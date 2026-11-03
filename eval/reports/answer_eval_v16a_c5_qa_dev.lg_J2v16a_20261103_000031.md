# Answer eval report (v16a_c5_qa_dev.lg, judge J2v16a)

- date: 2026-11-03T00:00:31.410232+00:00
- generated: 2026-11-02T23:32:46.761542+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: J2v16a, gemma4:12b-it-qat, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: google/gemma-4-12B-it@707f0a3
- judge order: dataset
- judge date: 2026-11-02T23:58:38.279564+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_dev.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16a_c5_qa_dev.gen.jsonl, eval/runs/v16a_c5_qa_dev.lg.J2v16a.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | 4.12 | 3.97 | 127 | 6/32 | 8401 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| d001 | 1.00 | 2 | 2 | True | 5636 | False | 2183 / 2183 | ok |
| d002 | 1.00 | 5 | 4 | False | 5473 | False | 2262 / 2262 | ok |
| d003 | 1.00 | 5 | 5 | False | 8562 | False | 2545 / 2545 | ok |
| d004 | 0.00 | 2 | 2 | True | 5545 | False | 2533 / 2533 | ok |
| d005 | 1.00 | 5 | 5 | False | 4552 | False | 2576 / 2576 | ok |
| d006 | 1.00 | 5 | 3 | False | 3537 | False | 2345 / 2345 | ok |
| d007 | 1.00 | 5 | 5 | False | 9031 | False | 3192 / 3192 | ok |
| d008 | 1.00 | 4 | 4 | False | 15106 | False | 3362 / 3362 | ok |
| d009 | 1.00 | 5 | 5 | False | 12244 | False | 2987 / 2987 | ok |
| d010 | 1.00 | 5 | 5 | False | 4354 | False | 2483 / 2483 | ok |
| d011 | 1.00 | 2 | 2 | True | 9034 | False | 2767 / 2767 | ok |
| d012 | 1.00 | 5 | 5 | False | 10064 | False | 2845 / 2845 | ok |
| d013 | 1.00 | 5 | 5 | False | 3945 | False | 2322 / 2322 | ok |
| d014 | 1.00 | 5 | 5 | False | 4124 | False | 1873 / 1873 | ok |
| d015 | 1.00 | 5 | 5 | False | 8609 | False | 2737 / 2737 | ok |
| d016 | 1.00 | 4 | 3 | False | 10531 | False | 2740 / 2740 | ok |
| d017 | 1.00 | 4 | 3 | False | 10708 | False | 2683 / 2683 | ok |
| d018 | 1.00 | 5 | 5 | False | 11176 | False | 3195 / 3195 | ok |
| d019 | 0.00 | 1 | 2 | True | 11482 | False | 3147 / 3147 | ok |
| d020 | 1.00 | 1 | 1 | True | 10037 | False | 3177 / 3177 | ok |
| d021 | 1.00 | 5 | 5 | False | 8642 | False | 2403 / 2403 | ok |
| d022 | 1.00 | 5 | 5 | False | 4435 | False | 2502 / 2502 | ok |
| d023 | 1.00 | 5 | 4 | False | 8623 | False | 2728 / 2728 | ok |
| d024 | 1.00 | 5 | 5 | False | 3584 | False | 2087 / 2087 | ok |
| d025 | 0.00 | 1 | 1 | False | 1345 | False | 2382 / 2382 | ok |
| d026 | 1.00 | 5 | 5 | False | 8239 | False | 2745 / 2745 | ok |
| d027 | 1.00 | 5 | 5 | False | 2819 | False | 1596 / 1596 | ok |
| d028 | 1.00 | 5 | 5 | False | 4088 | False | 2126 / 2126 | ok |
| d029 | 1.00 | 5 | 5 | False | 4412 | False | 2277 / 2277 | ok |
| d030 | 1.00 | 5 | 5 | False | 4375 | False | 2159 / 2159 | ok |
| d031 | 1.00 | 2 | 2 | True | 9737 | False | 2659 / 2659 | ok |
| d032 | 1.00 | 4 | 4 | False | 10627 | False | 2835 / 2835 | ok |

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
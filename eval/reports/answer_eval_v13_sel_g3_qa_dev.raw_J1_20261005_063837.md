# Answer eval report (v13_sel_g3_qa_dev.raw, judge J1)

- date: 2026-10-05T06:38:37.565377+00:00
- generated: 2026-10-05T05:56:28.811193+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: J1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-05T06:36:45.581651+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_dev.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_sel_g3_qa_dev.gen.jsonl, eval/runs/v13_sel_g3_qa_dev.raw.J1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | 4.47 | 4.78 | 153 | 1/32 | 13598 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| d001 | 1.00 | 5 | 5 | False | 8855 | False | 2079 / 2079 | ok |
| d002 | 1.00 | 5 | 5 | False | 8951 | False | 2134 / 2134 | ok |
| d003 | 1.00 | 5 | 5 | False | 13829 | False | 2410 / 2410 | ok |
| d004 | 0.00 | 4 | 5 | False | 9091 | False | 2440 / 2440 | ok |
| d005 | 1.00 | 4 | 5 | False | 7403 | False | 2446 / 2446 | ok |
| d006 | 1.00 | 4 | 5 | False | 5858 | False | 2209 / 2209 | ok |
| d007 | 1.00 | 5 | 5 | False | 14654 | False | 3054 / 3054 | ok |
| d008 | 1.00 | 4 | 4 | False | 24361 | False | 3084 / 3084 | ok |
| d009 | 1.00 | 4 | 4 | False | 19738 | False | 2812 / 2812 | ok |
| d010 | 1.00 | 4 | 5 | False | 7046 | False | 2332 / 2332 | ok |
| d011 | 1.00 | 4 | 5 | False | 14396 | False | 2590 / 2590 | ok |
| d012 | 1.00 | 5 | 5 | False | 16141 | False | 2665 / 2665 | ok |
| d013 | 1.00 | 4 | 5 | False | 6458 | False | 2217 / 2217 | ok |
| d014 | 1.00 | 4 | 5 | False | 6745 | False | 1753 / 1753 | ok |
| d015 | 1.00 | 5 | 5 | False | 13367 | False | 2601 / 2601 | ok |
| d016 | 1.00 | 5 | 5 | False | 16544 | False | 2639 / 2639 | ok |
| d017 | 1.00 | 5 | 5 | False | 16862 | False | 2544 / 2544 | ok |
| d018 | 1.00 | 5 | 5 | False | 17701 | False | 2952 / 2952 | ok |
| d019 | 0.00 | 4 | 5 | False | 18787 | False | 2962 / 2962 | ok |
| d020 | 1.00 | 5 | 5 | False | 17653 | False | 2934 / 2934 | ok |
| d021 | 1.00 | 5 | 5 | False | 15142 | False | 2259 / 2259 | ok |
| d022 | 1.00 | 4 | 5 | False | 7877 | False | 2408 / 2408 | ok |
| d023 | 1.00 | 5 | 5 | False | 15200 | False | 2579 / 2579 | ok |
| d024 | 1.00 | 5 | 5 | False | 6683 | False | 1962 / 1962 | ok |
| d025 | 0.00 | 1 | 1 | True | 6222 | False | 2183 / 2183 | ok |
| d026 | 1.00 | 5 | 5 | False | 14525 | False | 2718 / 2718 | ok |
| d027 | 1.00 | 5 | 5 | False | 5087 | False | 1516 / 1516 | ok |
| d028 | 1.00 | 5 | 5 | False | 7278 | False | 2028 / 2028 | ok |
| d029 | 1.00 | 5 | 5 | False | 7472 | False | 2178 / 2178 | ok |
| d030 | 1.00 | 4 | 5 | False | 7044 | False | 2100 / 2100 | ok |
| d031 | 1.00 | 4 | 4 | False | 15552 | False | 2543 / 2543 | ok |
| d032 | 1.00 | 5 | 5 | False | 17005 | False | 2686 / 2686 | ok |

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
# Answer eval report (v14_c3_qa_dev.lg, judge J1v15r2)

- date: 2026-10-18T16:56:22.421200+00:00
- generated: 2026-10-14T04:09:33.524106+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: J1v15r2, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-18T16:55:08.723887+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_dev.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v14_c3_qa_dev.gen.jsonl, eval/runs/v14_c3_qa_dev.lg.J1v15r2.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | 4.50 | 4.75 | 152 | 1/32 | 11728 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| d001 | 1.00 | 5 | 5 | False | 7765 | False | 2079 / 2079 | ok |
| d002 | 1.00 | 5 | 5 | False | 7782 | False | 2134 / 2134 | ok |
| d003 | 1.00 | 5 | 5 | False | 11949 | False | 2410 / 2410 | ok |
| d004 | 0.00 | 4 | 5 | False | 7933 | False | 2440 / 2440 | ok |
| d005 | 1.00 | 4 | 5 | False | 6477 | False | 2446 / 2446 | ok |
| d006 | 1.00 | 4 | 5 | False | 5138 | False | 2209 / 2209 | ok |
| d007 | 1.00 | 5 | 5 | False | 12570 | False | 3054 / 3054 | ok |
| d008 | 1.00 | 4 | 4 | False | 21108 | False | 3084 / 3084 | ok |
| d009 | 1.00 | 4 | 4 | False | 16979 | False | 2812 / 2812 | ok |
| d010 | 1.00 | 4 | 5 | False | 6188 | False | 2332 / 2332 | ok |
| d011 | 1.00 | 4 | 5 | False | 12721 | False | 2590 / 2590 | ok |
| d012 | 1.00 | 5 | 5 | False | 13894 | False | 2665 / 2665 | ok |
| d013 | 1.00 | 4 | 5 | False | 5681 | False | 2217 / 2217 | ok |
| d014 | 1.00 | 4 | 5 | False | 5954 | False | 1753 / 1753 | ok |
| d015 | 1.00 | 5 | 5 | False | 12114 | False | 2601 / 2601 | ok |
| d016 | 1.00 | 5 | 5 | False | 14581 | False | 2639 / 2639 | ok |
| d017 | 1.00 | 5 | 5 | False | 14991 | False | 2544 / 2544 | ok |
| d018 | 1.00 | 5 | 5 | False | 15630 | False | 2952 / 2952 | ok |
| d019 | 0.00 | 4 | 5 | False | 16035 | False | 2962 / 2962 | ok |
| d020 | 1.00 | 5 | 5 | False | 13954 | False | 2934 / 2934 | ok |
| d021 | 1.00 | 5 | 5 | False | 12086 | False | 2259 / 2259 | ok |
| d022 | 1.00 | 4 | 4 | False | 6250 | False | 2408 / 2408 | ok |
| d023 | 1.00 | 5 | 5 | False | 12036 | False | 2579 / 2579 | ok |
| d024 | 1.00 | 5 | 5 | False | 4938 | False | 1962 / 1962 | ok |
| d025 | 0.00 | 1 | 1 | True | 4992 | False | 2183 / 2183 | ok |
| d026 | 1.00 | 5 | 5 | False | 11506 | False | 2718 / 2718 | ok |
| d027 | 1.00 | 5 | 5 | False | 4061 | False | 1516 / 1516 | ok |
| d028 | 1.00 | 5 | 5 | False | 5531 | False | 2028 / 2028 | ok |
| d029 | 1.00 | 5 | 5 | False | 6226 | False | 2178 / 2178 | ok |
| d030 | 1.00 | 5 | 5 | False | 6128 | False | 2100 / 2100 | ok |
| d031 | 1.00 | 4 | 4 | False | 13393 | False | 2543 / 2543 | ok |
| d032 | 1.00 | 5 | 5 | False | 15084 | False | 2686 / 2686 | ok |

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
# Answer eval report (v16b_b_qa_dev, judge J1v16b)

- date: 2026-11-03T16:24:00.754681+00:00
- generated: 2026-11-03T15:09:26.710004+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: J1v16b, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-11-03T16:23:22.065423+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_dev.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_b_qa_dev.gen.jsonl, eval/runs/v16b_b_qa_dev.J1v16b.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | 4.47 | 4.69 | 150 | 2/32 | 6142 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| d001 | 1.00 | 5 | 5 | False | 6635 | False | 2134 / 2134 | ok |
| d002 | 1.00 | 5 | 5 | False | 5613 | False | 2136 / 2136 | ok |
| d003 | 1.00 | 5 | 5 | False | 11049 | False | 2595 / 2595 | ok |
| d004 | 0.00 | 4 | 5 | False | 5649 | False | 2446 / 2446 | ok |
| d005 | 1.00 | 4 | 5 | False | 4449 | False | 2434 / 2434 | ok |
| d006 | 1.00 | 4 | 5 | False | 3509 | False | 2202 / 2202 | ok |
| d007 | 1.00 | 5 | 5 | False | 8587 | False | 3014 / 3014 | ok |
| d008 | 1.00 | 4 | 4 | False | 12777 | False | 2917 / 2917 | ok |
| d009 | 1.00 | 5 | 5 | False | 13362 | False | 2898 / 2898 | ok |
| d010 | 1.00 | 4 | 5 | False | 4389 | False | 2331 / 2331 | ok |
| d011 | 1.00 | 4 | 5 | False | 10094 | False | 2683 / 2683 | ok |
| d012 | 1.00 | 5 | 5 | False | 7113 | False | 2432 / 2432 | ok |
| d013 | 1.00 | 4 | 5 | False | 4204 | False | 2213 / 2213 | ok |
| d014 | 1.00 | 4 | 5 | False | 3549 | False | 1723 / 1723 | ok |
| d015 | 1.00 | 5 | 5 | False | 9872 | False | 2706 / 2706 | ok |
| d016 | 1.00 | 5 | 5 | False | 13613 | False | 2853 / 2853 | ok |
| d017 | 1.00 | 5 | 5 | False | 11090 | False | 2581 / 2581 | ok |
| d018 | 1.00 | 5 | 5 | False | 11941 | False | 2991 / 2991 | ok |
| d019 | 0.00 | 2 | 1 | True | 1542 | False | 2339 / 2339 | ok |
| d020 | 1.00 | 5 | 5 | False | 13410 | False | 3172 / 3172 | ok |
| d021 | 1.00 | 5 | 5 | False | 4854 | False | 1945 / 1945 | ok |
| d022 | 1.00 | 4 | 4 | False | 4497 | False | 2408 / 2408 | ok |
| d023 | 1.00 | 5 | 5 | False | 7632 | False | 2476 / 2476 | ok |
| d024 | 1.00 | 5 | 5 | False | 3586 | False | 2032 / 2032 | ok |
| d025 | 0.00 | 1 | 1 | True | 1461 | False | 2258 / 2258 | ok |
| d026 | 1.00 | 5 | 5 | False | 8711 | False | 2751 / 2751 | ok |
| d027 | 1.00 | 5 | 5 | False | 2703 | False | 1514 / 1514 | ok |
| d028 | 1.00 | 5 | 5 | False | 4273 | False | 2033 / 2033 | ok |
| d029 | 1.00 | 5 | 5 | False | 4161 | False | 2177 / 2177 | ok |
| d030 | 1.00 | 5 | 5 | False | 4411 | False | 2103 / 2103 | ok |
| d031 | 1.00 | 4 | 5 | False | 7882 | False | 2413 / 2413 | ok |
| d032 | 1.00 | 5 | 5 | False | 10601 | False | 2696 / 2696 | ok |

## Worst questions (lowest keyword coverage)

- **d004** (0.00): How do you declare the type of data a path operation returns so FastAPI validates and filters it?
  > You declare the type of data a path operation returns by using the `response_model` parameter in your path operation function. This parameter specifies the Pydantic model that represents the expected 
- **d019** (0.00): How can one path operation return 200 when it updates an item but 201 when it creates a new one?
  > I don't know: the provided documentation passages do not cover this question.
- **d025** (0.00): Why should each Python project keep its own isolated set of installed packages?
  > I don't know: the provided documentation passages do not cover this question.
- **d001** (1.00): How do you read a cookie value sent by the client in a path operation?
  > To read a cookie value sent by the client in a path operation, you should use the `Cookie` parameter from the `fastapi` module. Here's how you do it:

```python
from fastapi import FastAPI, Cookie

ap
- **d002** (1.00): How do you set a cookie on the response FastAPI sends back?
  > You can set a cookie on the response by using a `Response` parameter in your path operation function or by returning a `Response` directly.

**Using a `Response` parameter:**

```python
from fastapi i
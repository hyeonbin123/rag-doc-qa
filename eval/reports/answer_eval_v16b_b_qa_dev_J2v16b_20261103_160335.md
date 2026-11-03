# Answer eval report (v16b_b_qa_dev, judge J2v16b)

- date: 2026-11-03T16:03:35.657278+00:00
- generated: 2026-11-03T15:09:26.710004+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: J2v16b, gemma4:12b-it-qat, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: google/gemma-4-12B-it@707f0a3
- judge order: dataset
- judge date: 2026-11-03T16:01:46.309527+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_dev.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_b_qa_dev.gen.jsonl, eval/runs/v16b_b_qa_dev.J2v16b.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | 4.75 | 4.50 | 144 | 2/32 | 6142 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| d001 | 1.00 | 5 | 4 | False | 6635 | False | 2209 / 2209 | ok |
| d002 | 1.00 | 5 | 5 | False | 5613 | False | 2265 / 2265 | ok |
| d003 | 1.00 | 5 | 4 | False | 11049 | False | 2757 / 2757 | ok |
| d004 | 0.00 | 5 | 4 | False | 5649 | False | 2538 / 2538 | ok |
| d005 | 1.00 | 5 | 5 | False | 4449 | False | 2561 / 2561 | ok |
| d006 | 1.00 | 5 | 3 | False | 3509 | False | 2338 / 2338 | ok |
| d007 | 1.00 | 5 | 5 | False | 8587 | False | 3148 / 3148 | ok |
| d008 | 1.00 | 5 | 4 | False | 12777 | False | 3163 / 3163 | ok |
| d009 | 1.00 | 5 | 5 | False | 13362 | False | 3064 / 3064 | ok |
| d010 | 1.00 | 5 | 5 | False | 4389 | False | 2482 / 2482 | ok |
| d011 | 1.00 | 4 | 4 | False | 10094 | False | 2868 / 2868 | ok |
| d012 | 1.00 | 5 | 5 | False | 7113 | False | 2583 / 2583 | ok |
| d013 | 1.00 | 5 | 5 | False | 4204 | False | 2318 / 2318 | ok |
| d014 | 1.00 | 5 | 5 | False | 3549 | False | 1845 / 1845 | ok |
| d015 | 1.00 | 5 | 4 | False | 9872 | False | 2843 / 2843 | ok |
| d016 | 1.00 | 2 | 2 | True | 13613 | False | 2985 / 2985 | ok |
| d017 | 1.00 | 4 | 3 | False | 11090 | False | 2711 / 2711 | ok |
| d018 | 1.00 | 5 | 5 | False | 11941 | False | 3252 / 3252 | ok |
| d019 | 0.00 | 5 | 5 | False | 1542 | False | 2467 / 2467 | ok |
| d020 | 1.00 | 5 | 5 | False | 13410 | False | 3447 / 3447 | ok |
| d021 | 1.00 | 5 | 5 | False | 4854 | False | 2068 / 2068 | ok |
| d022 | 1.00 | 5 | 5 | False | 4497 | False | 2502 / 2502 | ok |
| d023 | 1.00 | 5 | 5 | False | 7632 | False | 2635 / 2635 | ok |
| d024 | 1.00 | 5 | 5 | False | 3586 | False | 2161 / 2161 | ok |
| d025 | 0.00 | 5 | 5 | False | 1461 | False | 2442 / 2442 | ok |
| d026 | 1.00 | 5 | 5 | False | 8711 | False | 2779 / 2779 | ok |
| d027 | 1.00 | 5 | 5 | False | 2703 | False | 1571 / 1571 | ok |
| d028 | 1.00 | 5 | 5 | False | 4273 | False | 2133 / 2133 | ok |
| d029 | 1.00 | 5 | 5 | False | 4161 | False | 2276 / 2276 | ok |
| d030 | 1.00 | 5 | 5 | False | 4411 | False | 2161 / 2161 | ok |
| d031 | 1.00 | 2 | 2 | True | 7882 | False | 2514 / 2514 | ok |
| d032 | 1.00 | 5 | 5 | False | 10601 | False | 2830 / 2830 | ok |

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
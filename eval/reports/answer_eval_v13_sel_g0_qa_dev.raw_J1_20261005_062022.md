# Answer eval report (v13_sel_g0_qa_dev.raw, judge J1)

- date: 2026-10-05T06:20:22.787580+00:00
- generated: 2026-10-05T05:00:29.894696+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- model digest: 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e
- think: None, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: J1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-05T06:18:14.114258+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_dev.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_sel_g0_qa_dev.gen.jsonl, eval/runs/v13_sel_g0_qa_dev.raw.J1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.94 | 4.16 | 4.72 | 151 | 1/32 | 5614 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| d001 | 1.00 | 4 | 5 | False | 4915 | False | 1946 / 1946 | ok |
| d002 | 1.00 | 4 | 5 | False | 5148 | False | 2015 / 2015 | ok |
| d003 | 1.00 | 4 | 5 | False | 4817 | False | 2031 / 2031 | ok |
| d004 | 1.00 | 4 | 4 | False | 5918 | False | 2361 / 2361 | ok |
| d005 | 1.00 | 4 | 5 | False | 4824 | False | 2383 / 2383 | ok |
| d006 | 1.00 | 4 | 5 | False | 4631 | False | 2202 / 2202 | ok |
| d007 | 1.00 | 4 | 4 | False | 5864 | False | 2671 / 2671 | ok |
| d008 | 1.00 | 5 | 5 | False | 7176 | False | 2376 / 2376 | ok |
| d009 | 1.00 | 4 | 5 | False | 7587 | False | 2273 / 2273 | ok |
| d010 | 1.00 | 4 | 5 | False | 5138 | False | 2292 / 2292 | ok |
| d011 | 1.00 | 4 | 5 | False | 5737 | False | 2238 / 2238 | ok |
| d012 | 1.00 | 4 | 5 | False | 5256 | False | 2201 / 2201 | ok |
| d013 | 1.00 | 4 | 5 | False | 5476 | False | 2190 / 2190 | ok |
| d014 | 1.00 | 4 | 5 | False | 4767 | False | 1702 / 1702 | ok |
| d015 | 1.00 | 4 | 5 | False | 7772 | False | 2368 / 2368 | ok |
| d016 | 1.00 | 4 | 5 | False | 7267 | False | 2267 / 2267 | ok |
| d017 | 1.00 | 4 | 4 | False | 6594 | False | 2130 / 2130 | ok |
| d018 | 1.00 | 5 | 5 | False | 7104 | False | 2510 / 2510 | ok |
| d019 | 0.00 | 3 | 4 | False | 6185 | False | 2415 / 2415 | ok |
| d020 | 1.00 | 4 | 5 | False | 8433 | False | 2635 / 2635 | ok |
| d021 | 1.00 | 5 | 5 | False | 8076 | False | 2042 / 2042 | ok |
| d022 | 1.00 | 4 | 5 | False | 5491 | False | 2365 / 2365 | ok |
| d023 | 1.00 | 4 | 5 | False | 5806 | False | 2249 / 2249 | ok |
| d024 | 1.00 | 5 | 5 | False | 5034 | False | 1962 / 1962 | ok |
| d025 | 0.00 | 1 | 1 | True | 4508 | False | 2182 / 2182 | ok |
| d026 | 1.00 | 5 | 5 | False | 7746 | False | 2553 / 2553 | ok |
| d027 | 1.00 | 5 | 5 | False | 3755 | False | 1516 / 1516 | ok |
| d028 | 1.00 | 5 | 5 | False | 5135 | False | 2001 / 2001 | ok |
| d029 | 1.00 | 5 | 5 | False | 5057 | False | 2123 / 2123 | ok |
| d030 | 1.00 | 4 | 5 | False | 5354 | False | 2085 / 2085 | ok |
| d031 | 1.00 | 4 | 4 | False | 5903 | False | 2139 / 2139 | ok |
| d032 | 1.00 | 5 | 5 | False | 6764 | False | 2303 / 2303 | ok |

## Worst questions (lowest keyword coverage)

- **d019** (0.00): How can one path operation return 200 when it updates an item but 201 when it creates a new one?
  > You don't need different path operations for creating and updating items; you can use the same path operation and handle both cases inside the function. You can check if the item exists and return 200
- **d025** (0.00): Why should each Python project keep its own isolated set of installed packages?
  > don't know
- **d001** (1.00): How do you read a cookie value sent by the client in a path operation?
  > Declare the cookie parameter using the `Cookie` function from `fastapi`. For example:

```python
from fastapi import Cookie

async def read_cookie(cookie_value: str = Cookie(None)):
    return {"cooki
- **d002** (1.00): How do you set a cookie on the response FastAPI sends back?
  > You can declare a parameter of type `Response` in your *path operation function* and then set cookies in that *temporary* response object. FastAPI will use that *temporary* response to extract the coo
- **d003** (1.00): How do you add a custom header to a response without returning a Response object yourself?
  > You can add a custom header to a response without returning a `Response` object yourself by using the `Response` parameter in your path operation function or dependencies. FastAPI will then use that `
# Answer eval report (v11_B_qa_dev, judge J1)

- date: 2026-10-03T22:57:20.259258+00:00
- generated: 2026-10-03T22:40:16.431175+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- judge: J1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-03T22:56:16.648619+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- dataset: qa_dev.jsonl
- questions: 32
- generation order: shuffle (seed 20261003)
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v11_B_qa_dev.gen.jsonl, eval/runs/v11_B_qa_dev.J1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.94 | 4.09 | 4.62 | 148 | 1/32 | 3809 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| d001 | 1.00 | 4 | 5 | False | 3526 | False | 1946 / 1946 | ok |
| d002 | 1.00 | 4 | 5 | False | 3618 | False | 2015 / 2015 | ok |
| d003 | 1.00 | 4 | 5 | False | 3735 | False | 2032 / 2032 | ok |
| d004 | 1.00 | 4 | 5 | False | 3759 | False | 2330 / 2330 | ok |
| d005 | 1.00 | 4 | 5 | False | 3859 | False | 2411 / 2411 | ok |
| d006 | 1.00 | 4 | 5 | False | 3282 | False | 2202 / 2202 | ok |
| d007 | 1.00 | 4 | 4 | False | 4244 | False | 2700 / 2700 | ok |
| d008 | 1.00 | 5 | 5 | False | 4634 | False | 2376 / 2376 | ok |
| d009 | 1.00 | 4 | 5 | False | 4908 | False | 2276 / 2276 | ok |
| d010 | 1.00 | 4 | 5 | False | 3510 | False | 2292 / 2292 | ok |
| d011 | 1.00 | 4 | 5 | False | 3895 | False | 2238 / 2238 | ok |
| d012 | 1.00 | 4 | 4 | False | 3677 | False | 2217 / 2217 | ok |
| d013 | 1.00 | 4 | 5 | False | 3693 | False | 2190 / 2190 | ok |
| d014 | 1.00 | 4 | 5 | False | 3245 | False | 1702 / 1702 | ok |
| d015 | 1.00 | 4 | 5 | False | 8364 | False | 2361 / 2361 | ok |
| d016 | 1.00 | 4 | 5 | False | 4590 | False | 2252 / 2252 | ok |
| d017 | 1.00 | 4 | 5 | False | 4096 | False | 2103 / 2103 | ok |
| d018 | 1.00 | 5 | 5 | False | 4474 | False | 2499 / 2499 | ok |
| d019 | 0.00 | 3 | 2 | False | 5151 | False | 2489 / 2489 | ok |
| d020 | 1.00 | 4 | 5 | False | 5594 | False | 2635 / 2635 | ok |
| d021 | 1.00 | 4 | 4 | False | 4095 | False | 1941 / 1941 | ok |
| d022 | 1.00 | 4 | 5 | False | 3730 | False | 2366 / 2366 | ok |
| d023 | 1.00 | 4 | 5 | False | 3899 | False | 2249 / 2249 | ok |
| d024 | 1.00 | 5 | 5 | False | 3380 | False | 1962 / 1962 | ok |
| d025 | 0.00 | 1 | 1 | True | 3115 | False | 2182 / 2182 | ok |
| d026 | 1.00 | 5 | 5 | False | 5191 | False | 2553 / 2553 | ok |
| d027 | 1.00 | 5 | 5 | False | 2761 | False | 1516 / 1516 | ok |
| d028 | 1.00 | 4 | 4 | False | 3508 | False | 2003 / 2003 | ok |
| d029 | 1.00 | 5 | 5 | False | 3524 | False | 2123 / 2123 | ok |
| d030 | 1.00 | 4 | 5 | False | 3661 | False | 2085 / 2085 | ok |
| d031 | 1.00 | 4 | 4 | False | 3968 | False | 2128 / 2128 | ok |
| d032 | 1.00 | 5 | 5 | False | 4640 | False | 2303 / 2303 | ok |

## Worst questions (lowest keyword coverage)

- **d019** (0.00): How can one path operation return 200 when it updates an item but 201 when it creates a new one?
  > You don't need different path operations for creating and updating items; you can use the same path operation and handle it with different logic based on the request method. For example, you can use `
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
  > You can add a custom header to a response without returning a `Response` object yourself by using the `Response` parameter in your path operation function or a dependency. FastAPI will then use that `
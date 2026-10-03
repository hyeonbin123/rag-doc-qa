# Answer eval report (v11_A_qa_dev, judge J0)

- date: 2026-10-03T23:02:26.497169+00:00
- generated: 2026-10-03T22:28:35.792263+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- judge: J0, qwen2.5:7b-instruct, Ollama default (num_ctx not sent, truncation on)
- judge context in use (Ollama /api/ps after judging): 4096
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-03T23:01:15.799600+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- dataset: qa_dev.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v11_A_qa_dev.gen.jsonl, eval/runs/v11_A_qa_dev.J0.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.94 | 4.12 | 4.66 | 149 | 1/32 | 3821 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| d001 | 1.00 | 4 | 5 | False | 7232 | False | 1982 / 1982 | ok |
| d002 | 1.00 | 4 | 5 | False | 3636 | False | 2015 / 2015 | ok |
| d003 | 1.00 | 4 | 5 | False | 3502 | False | 2032 / 2032 | ok |
| d004 | 1.00 | 4 | 5 | False | 3773 | False | 2330 / 2330 | ok |
| d005 | 1.00 | 4 | 5 | False | 3808 | False | 2411 / 2411 | ok |
| d006 | 1.00 | 4 | 5 | False | 3281 | False | 2202 / 2202 | ok |
| d007 | 1.00 | 4 | 4 | False | 4210 | False | 2700 / 2700 | ok |
| d008 | 1.00 | 5 | 5 | False | 4645 | False | 2376 / 2376 | ok |
| d009 | 1.00 | 4 | 5 | False | 4886 | False | 2276 / 2276 | ok |
| d010 | 1.00 | 4 | 5 | False | 3516 | False | 2292 / 2292 | ok |
| d011 | 1.00 | 4 | 5 | False | 3833 | False | 2238 / 2238 | ok |
| d012 | 1.00 | 4 | 5 | False | 3676 | False | 2217 / 2217 | ok |
| d013 | 1.00 | 4 | 5 | False | 3679 | False | 2190 / 2190 | ok |
| d014 | 1.00 | 4 | 5 | False | 3260 | False | 1702 / 1702 | ok |
| d015 | 1.00 | 4 | 5 | False | 4947 | False | 2361 / 2361 | ok |
| d016 | 1.00 | 4 | 4 | False | 4662 | False | 2252 / 2252 | ok |
| d017 | 1.00 | 4 | 5 | False | 4081 | False | 2103 / 2103 | ok |
| d018 | 1.00 | 5 | 5 | False | 4567 | False | 2499 / 2499 | ok |
| d019 | 0.00 | 3 | 2 | False | 5095 | False | 2489 / 2489 | ok |
| d020 | 1.00 | 4 | 5 | False | 5639 | False | 2635 / 2635 | ok |
| d021 | 1.00 | 4 | 4 | False | 4186 | False | 1941 / 1941 | ok |
| d022 | 1.00 | 4 | 5 | False | 3739 | False | 2366 / 2366 | ok |
| d023 | 1.00 | 4 | 5 | False | 3970 | False | 2249 / 2249 | ok |
| d024 | 1.00 | 5 | 5 | False | 3474 | False | 1962 / 1962 | ok |
| d025 | 0.00 | 1 | 1 | True | 3114 | False | 2182 / 2182 | ok |
| d026 | 1.00 | 5 | 5 | False | 5259 | False | 2553 / 2553 | ok |
| d027 | 1.00 | 5 | 5 | False | 2890 | False | 1516 / 1516 | ok |
| d028 | 1.00 | 5 | 5 | False | 3600 | False | 2003 / 2003 | ok |
| d029 | 1.00 | 5 | 5 | False | 3486 | False | 2123 / 2123 | ok |
| d030 | 1.00 | 4 | 5 | False | 3706 | False | 2085 / 2085 | ok |
| d031 | 1.00 | 4 | 4 | False | 4047 | False | 2128 / 2128 | ok |
| d032 | 1.00 | 5 | 5 | False | 4687 | False | 2303 / 2303 | ok |

## Worst questions (lowest keyword coverage)

- **d019** (0.00): How can one path operation return 200 when it updates an item but 201 when it creates a new one?
  > You don't need different path operations for creating and updating items; you can use the same path operation and handle it with different logic based on the request method. For example, you can use `
- **d025** (0.00): Why should each Python project keep its own isolated set of installed packages?
  > don't know
- **d001** (1.00): How do you read a cookie value sent by the client in a path operation?
  > Declare the cookie parameter using the `Cookie` function from `fastapi`. Here is an example:

```python
from fastapi import FastAPI, Cookie

app = FastAPI()

@app.get("/")
async def read_root(usr: str
- **d002** (1.00): How do you set a cookie on the response FastAPI sends back?
  > You can declare a parameter of type `Response` in your *path operation function* and then set cookies in that *temporary* response object. FastAPI will use that *temporary* response to extract the coo
- **d003** (1.00): How do you add a custom header to a response without returning a Response object yourself?
  > You can add a custom header to a response without returning a `Response` object yourself by using the `Response` parameter in your path operation function or a dependency. FastAPI will then use that `
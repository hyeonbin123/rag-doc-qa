# Answer eval report (v13_sel_g0_qa_dev)

- date: 2026-10-05T05:03:47.440562+00:00
- generated: 2026-10-05T05:00:29.894696+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- model digest: 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e
- think: None, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_dev.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_sel_g0_qa_dev.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.94 | n/a | n/a | n/a | 0/0 | 5614 | 0/32 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| d001 | 1.00 | None | None | None | 4915 | False | None / None | - |
| d002 | 1.00 | None | None | None | 5148 | False | None / None | - |
| d003 | 1.00 | None | None | None | 4817 | False | None / None | - |
| d004 | 1.00 | None | None | None | 5918 | False | None / None | - |
| d005 | 1.00 | None | None | None | 4824 | False | None / None | - |
| d006 | 1.00 | None | None | None | 4631 | False | None / None | - |
| d007 | 1.00 | None | None | None | 5864 | False | None / None | - |
| d008 | 1.00 | None | None | None | 7176 | False | None / None | - |
| d009 | 1.00 | None | None | None | 7587 | False | None / None | - |
| d010 | 1.00 | None | None | None | 5138 | False | None / None | - |
| d011 | 1.00 | None | None | None | 5737 | False | None / None | - |
| d012 | 1.00 | None | None | None | 5256 | False | None / None | - |
| d013 | 1.00 | None | None | None | 5476 | False | None / None | - |
| d014 | 1.00 | None | None | None | 4767 | False | None / None | - |
| d015 | 1.00 | None | None | None | 7772 | False | None / None | - |
| d016 | 1.00 | None | None | None | 7267 | False | None / None | - |
| d017 | 1.00 | None | None | None | 6594 | False | None / None | - |
| d018 | 1.00 | None | None | None | 7104 | False | None / None | - |
| d019 | 0.00 | None | None | None | 6185 | False | None / None | - |
| d020 | 1.00 | None | None | None | 8433 | False | None / None | - |
| d021 | 1.00 | None | None | None | 8076 | False | None / None | - |
| d022 | 1.00 | None | None | None | 5491 | False | None / None | - |
| d023 | 1.00 | None | None | None | 5806 | False | None / None | - |
| d024 | 1.00 | None | None | None | 5034 | False | None / None | - |
| d025 | 0.00 | None | None | None | 4508 | False | None / None | - |
| d026 | 1.00 | None | None | None | 7746 | False | None / None | - |
| d027 | 1.00 | None | None | None | 3755 | False | None / None | - |
| d028 | 1.00 | None | None | None | 5135 | False | None / None | - |
| d029 | 1.00 | None | None | None | 5057 | False | None / None | - |
| d030 | 1.00 | None | None | None | 5354 | False | None / None | - |
| d031 | 1.00 | None | None | None | 5903 | False | None / None | - |
| d032 | 1.00 | None | None | None | 6764 | False | None / None | - |

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
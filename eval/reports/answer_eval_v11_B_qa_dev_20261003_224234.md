# Answer eval report (v11_B_qa_dev)

- date: 2026-10-03T22:42:34.118479+00:00
- generated: 2026-10-03T22:40:16.431175+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- dataset: qa_dev.jsonl
- questions: 32
- generation order: shuffle (seed 20261003)
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v11_B_qa_dev.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.94 | n/a | n/a | n/a | 0/0 | 3809 | 0/32 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| d001 | 1.00 | None | None | None | 3526 | False | None / None | - |
| d002 | 1.00 | None | None | None | 3618 | False | None / None | - |
| d003 | 1.00 | None | None | None | 3735 | False | None / None | - |
| d004 | 1.00 | None | None | None | 3759 | False | None / None | - |
| d005 | 1.00 | None | None | None | 3859 | False | None / None | - |
| d006 | 1.00 | None | None | None | 3282 | False | None / None | - |
| d007 | 1.00 | None | None | None | 4244 | False | None / None | - |
| d008 | 1.00 | None | None | None | 4634 | False | None / None | - |
| d009 | 1.00 | None | None | None | 4908 | False | None / None | - |
| d010 | 1.00 | None | None | None | 3510 | False | None / None | - |
| d011 | 1.00 | None | None | None | 3895 | False | None / None | - |
| d012 | 1.00 | None | None | None | 3677 | False | None / None | - |
| d013 | 1.00 | None | None | None | 3693 | False | None / None | - |
| d014 | 1.00 | None | None | None | 3245 | False | None / None | - |
| d015 | 1.00 | None | None | None | 8364 | False | None / None | - |
| d016 | 1.00 | None | None | None | 4590 | False | None / None | - |
| d017 | 1.00 | None | None | None | 4096 | False | None / None | - |
| d018 | 1.00 | None | None | None | 4474 | False | None / None | - |
| d019 | 0.00 | None | None | None | 5151 | False | None / None | - |
| d020 | 1.00 | None | None | None | 5594 | False | None / None | - |
| d021 | 1.00 | None | None | None | 4095 | False | None / None | - |
| d022 | 1.00 | None | None | None | 3730 | False | None / None | - |
| d023 | 1.00 | None | None | None | 3899 | False | None / None | - |
| d024 | 1.00 | None | None | None | 3380 | False | None / None | - |
| d025 | 0.00 | None | None | None | 3115 | False | None / None | - |
| d026 | 1.00 | None | None | None | 5191 | False | None / None | - |
| d027 | 1.00 | None | None | None | 2761 | False | None / None | - |
| d028 | 1.00 | None | None | None | 3508 | False | None / None | - |
| d029 | 1.00 | None | None | None | 3524 | False | None / None | - |
| d030 | 1.00 | None | None | None | 3661 | False | None / None | - |
| d031 | 1.00 | None | None | None | 3968 | False | None / None | - |
| d032 | 1.00 | None | None | None | 4640 | False | None / None | - |

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
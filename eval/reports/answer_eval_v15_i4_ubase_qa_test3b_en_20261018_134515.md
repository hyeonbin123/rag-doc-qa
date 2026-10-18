# Answer eval report (v15_i4_ubase_qa_test3b_en)

- date: 2026-10-18T13:45:15.274934+00:00
- generated: 2026-10-18T13:43:07.700446+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/14)
- final answer call stopped by the output limit, done_reason=length: 0/14; reasoning output: 0/14; citation replies breaking the schema: 0/14
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_test3b_en.jsonl
- questions: 14
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_ubase_qa_test3b_en.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.86 | n/a | n/a | n/a | 0/0 | 8391 | 0/14 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n010 | 1.00 | None | None | None | 9366 | False | None / None | - |
| n025 | 1.00 | None | None | None | 6280 | False | None / None | - |
| n027 | 1.00 | None | None | None | 7532 | False | None / None | - |
| n029 | 1.00 | None | None | None | 5450 | False | None / None | - |
| n030 | 0.00 | None | None | None | 5029 | False | None / None | - |
| n034 | 1.00 | None | None | None | 16565 | False | None / None | - |
| n050 | 1.00 | None | None | None | 8327 | False | None / None | - |
| n051 | 1.00 | None | None | None | 11096 | False | None / None | - |
| n061 | 1.00 | None | None | None | 8525 | False | None / None | - |
| n077 | 1.00 | None | None | None | 8456 | False | None / None | - |
| n083 | 1.00 | None | None | None | 10091 | False | None / None | - |
| n097 | 1.00 | None | None | None | 5647 | False | None / None | - |
| n105 | 1.00 | None | None | None | 5876 | False | None / None | - |
| n115 | 0.00 | None | None | None | 11221 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **n030** (0.00): When reading a header value with Header, what does it mean that underscores are automatically converted to hyphens?
  > Underscores in header parameter names are automatically converted to hyphens by FastAPI when using the `Header` class. This means that if you define a header parameter as `user_agent`, the correspondi
- **n115** (0.00): I am definitely sending a JSON body, but I keep getting 422 Unprocessable Entity. What am I doing wrong?
  > You are likely sending a JSON body that does not match the expected schema defined by your Pydantic model. FastAPI will validate the incoming JSON against the model you declared. If the data does not 
- **n010** (1.00): Can I put range validations like gt and le on a numeric path parameter with Path?
  > Yes, you can put range validations like `gt` (greater than) and `le` (less than or equal) on a numeric path parameter using `Path`.

Here's how you can do it:

```python
from fastapi import FastAPI, P
- **n025** (1.00): Is there a package I need to install separately to receive HTML form data? And how do I declare it?
  > You need to install the `python-multipart` package separately.

To install it, run:
```console
$ uv add python-multipart
```

To declare form data in FastAPI, use the `Form` class from `fastapi`. Here
- **n027** (1.00): How do I make an endpoint that accepts several file uploads at once?
  > To make an endpoint that accepts several file uploads at once, you can define a path operation with multiple `File` parameters, each specifying an `UploadFile` type. Here's how you can structure it:


# Answer eval report (v15_i4_ucand_qa_test3b_en)

- date: 2026-10-18T13:47:11.684603+00:00
- generated: 2026-10-18T13:45:34.606493+00:00
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
- per-item records: eval/runs/v15_i4_ucand_qa_test3b_en.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.79 | n/a | n/a | n/a | 0/0 | 5905 | 0/14 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n010 | 1.00 | None | None | None | 7680 | False | None / None | - |
| n025 | 1.00 | None | None | None | 3647 | False | None / None | - |
| n027 | 1.00 | None | None | None | 5796 | False | None / None | - |
| n029 | 1.00 | None | None | None | 2665 | False | None / None | - |
| n030 | 0.00 | None | None | None | 2867 | False | None / None | - |
| n034 | 1.00 | None | None | None | 8851 | False | None / None | - |
| n050 | 1.00 | None | None | None | 6015 | False | None / None | - |
| n051 | 0.00 | None | None | None | 12834 | False | None / None | - |
| n061 | 1.00 | None | None | None | 8748 | False | None / None | - |
| n077 | 1.00 | None | None | None | 5294 | False | None / None | - |
| n083 | 1.00 | None | None | None | 7883 | False | None / None | - |
| n097 | 1.00 | None | None | None | 3646 | False | None / None | - |
| n105 | 1.00 | None | None | None | 4664 | False | None / None | - |
| n115 | 0.00 | None | None | None | 8397 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **n030** (0.00): When reading a header value with Header, what does it mean that underscores are automatically converted to hyphens?
  > Underscores in header parameter names are automatically converted to hyphens by the `Header` class in FastAPI. This means that if you define a header parameter as `user_agent`, the corresponding HTTP 
- **n051** (0.00): I want to block disabled accounts from using the API even if they log in. How should I structure the dependencies?
  > You should structure your dependencies to check for user permissions based on their account status, using `SecurityScopes` and OAuth2 scopes.

Here's a structured approach:

1. **Define OAuth2 Scopes*
- **n115** (0.00): I am definitely sending a JSON body, but I keep getting 422 Unprocessable Entity. What am I doing wrong?
  > You are likely sending a JSON body that does not match the expected schema defined by your Pydantic model. FastAPI will validate the incoming JSON against the model you declared. If the data does not 
- **n010** (1.00): Can I put range validations like gt and le on a numeric path parameter with Path?
  > Yes, you can put range validations like `gt` (greater than) and `le` (less than or equal) on a numeric path parameter using `Path`.

Here's how you can do it:

```python
from fastapi import FastAPI, P
- **n025** (1.00): Is there a package I need to install separately to receive HTML form data? And how do I declare it?
  > Yes, you need to install the `python-multipart` package separately.

To install it, run:
```console
$ uv add python-multipart
```

To declare form data in FastAPI, use the `Form` class. Here's how you
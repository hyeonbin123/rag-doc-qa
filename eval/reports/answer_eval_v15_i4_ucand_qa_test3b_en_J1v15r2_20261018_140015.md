# Answer eval report (v15_i4_ucand_qa_test3b_en, judge J1v15r2)

- date: 2026-10-18T14:00:15.105732+00:00
- generated: 2026-10-18T13:45:34.606493+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/14)
- final answer call stopped by the output limit, done_reason=length: 0/14; reasoning output: 0/14; citation replies breaking the schema: 0/14
- judge: J1v15r2, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-18T13:59:53.846373+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_test3b_en.jsonl
- questions: 14
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_ucand_qa_test3b_en.gen.jsonl, eval/runs/v15_i4_ucand_qa_test3b_en.J1v15r2.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.79 | 4.57 | 4.71 | 66 | 0/14 | 5905 | 0/14 | 0/14 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n010 | 1.00 | 5 | 5 | False | 7680 | False | 2629 / 2629 | ok |
| n025 | 1.00 | 4 | 4 | False | 3647 | False | 1028 / 1028 | ok |
| n027 | 1.00 | 5 | 5 | False | 5796 | False | 1666 / 1666 | ok |
| n029 | 1.00 | 5 | 5 | False | 2665 | False | 1116 / 1116 | ok |
| n030 | 0.00 | 4 | 4 | False | 2867 | False | 1170 / 1170 | ok |
| n034 | 1.00 | 5 | 5 | False | 8851 | False | 2317 / 2317 | ok |
| n050 | 1.00 | 5 | 5 | False | 6015 | False | 2485 / 2485 | ok |
| n051 | 0.00 | 4 | 5 | False | 12834 | False | 2230 / 2230 | ok |
| n061 | 1.00 | 5 | 5 | False | 8748 | False | 2283 / 2283 | ok |
| n077 | 1.00 | 5 | 5 | False | 5294 | False | 2448 / 2448 | ok |
| n083 | 1.00 | 5 | 5 | False | 7883 | False | 1436 / 1436 | ok |
| n097 | 1.00 | 4 | 4 | False | 3646 | False | 2284 / 2284 | ok |
| n105 | 1.00 | 4 | 5 | False | 4664 | False | 929 / 929 | ok |
| n115 | 0.00 | 4 | 4 | False | 8397 | False | 2785 / 2785 | ok |

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
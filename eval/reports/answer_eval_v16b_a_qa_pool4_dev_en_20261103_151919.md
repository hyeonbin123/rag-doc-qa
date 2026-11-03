# Answer eval report (v16b_a_qa_pool4_dev_en)

- date: 2026-11-03T15:19:19.158366+00:00
- generated: 2026-11-03T15:13:37.752345+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 2/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- corpus: source commit 50113da (277 documents); last fetched 2026-11-03T08:04:42.172603+00:00; chunks en 914, ko 621
- dataset: qa_pool4_dev_en.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_a_qa_pool4_dev_en.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.78 | n/a | n/a | n/a | 0/0 | 8401 | 0/40 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| e4001 | 0.50 | None | None | None | 10232 | False | None / None | - |
| e4002 | 1.00 | None | None | None | 1413 | False | None / None | - |
| e4006 | 1.00 | None | None | None | 13792 | False | None / None | - |
| e4009 | 1.00 | None | None | None | 3971 | False | None / None | - |
| e4011 | 1.00 | None | None | None | 7072 | False | None / None | - |
| e4012 | 1.00 | None | None | None | 12998 | False | None / None | - |
| e4015 | 0.50 | None | None | None | 8849 | False | None / None | - |
| e4018 | 0.00 | None | None | None | 8515 | False | None / None | - |
| e4024 | 1.00 | None | None | None | 8579 | False | None / None | - |
| e4027 | 1.00 | None | None | None | 6149 | False | None / None | - |
| e4028 | 1.00 | None | None | None | 5688 | False | None / None | - |
| e4029 | 1.00 | None | None | None | 15716 | False | None / None | - |
| e4030 | 0.50 | None | None | None | 6881 | False | None / None | - |
| e4035 | 1.00 | None | None | None | 11564 | False | None / None | - |
| e4036 | 1.00 | None | None | None | 8362 | False | None / None | - |
| e4037 | 1.00 | None | None | None | 6738 | False | None / None | - |
| e4041 | 1.00 | None | None | None | 3430 | False | None / None | - |
| e4045 | 1.00 | None | None | None | 12045 | False | None / None | - |
| e4050 | 1.00 | None | None | None | 13435 | False | None / None | - |
| e4052 | 1.00 | None | None | None | 8809 | False | None / None | - |
| e4053 | 1.00 | None | None | None | 8918 | False | None / None | - |
| e4055 | 1.00 | None | None | None | 1814 | False | None / None | - |
| e4057 | 1.00 | None | None | None | 7609 | False | None / None | - |
| e4059 | 1.00 | None | None | None | 7481 | False | None / None | - |
| e4062 | 0.33 | None | None | None | 16041 | False | None / None | - |
| e4064 | 0.33 | None | None | None | 9272 | False | None / None | - |
| e4066 | 0.00 | None | None | None | 8313 | False | None / None | - |
| e4069 | 0.33 | None | None | None | 13690 | False | None / None | - |
| e4071 | 1.00 | None | None | None | 4587 | False | None / None | - |
| e4075 | 0.67 | None | None | None | 6003 | False | None / None | - |
| e4089 | 0.00 | None | None | None | 5730 | False | None / None | - |
| e4093 | 1.00 | None | None | None | 9677 | False | None / None | - |
| e4095 | 0.50 | None | None | None | 7665 | False | None / None | - |
| e4096 | 1.00 | None | None | None | 4428 | False | None / None | - |
| e4097 | 1.00 | None | None | None | 5549 | False | None / None | - |
| e4098 | 0.00 | None | None | None | 8440 | False | None / None | - |
| e4099 | 1.00 | None | None | None | 10020 | False | None / None | - |
| e4100 | 1.00 | None | None | None | 8916 | False | None / None | - |
| e4103 | 0.50 | None | None | None | 4345 | False | None / None | - |
| e4107 | 1.00 | None | None | None | 12373 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **e4018** (0.00): I return a RedirectResponse in one branch and a dict in another, and startup fails with "Invalid args for response field!". How do I fix the annotation?
  > You should use `Union[RedirectResponse, dict]` as the return type annotation, but since `RedirectResponse` is a subclass of `Response`, you can also use `response_model` to specify the type more clear
- **e4066** (0.00): What is dependency injection in FastAPI and how is it different from just calling a helper function inside my endpoint?
  > Dependency injection in FastAPI is a system that allows you to declare dependencies (functions or objects) that your path operation functions need, and FastAPI will handle providing those dependencies
- **e4089** (0.00): How do I hide an internal endpoint from the OpenAPI schema completely?
  > To hide an internal endpoint from the OpenAPI schema completely, you can use the `include_in_openapi` parameter in the route definition.

Here's how you can do it:

```python
from fastapi import FastA
- **e4098** (0.00): How do I gzip-compress large responses?
  > You can use the `GzipResponse` from Starlette, which is not directly provided in FastAPI's response classes but can be used through Starlette's API.

Here's how you can do it:

```python
from starlett
- **e4062** (0.33): How do I build username/password login that returns a bearer token using OAuth2PasswordRequestForm?
  > ```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Opt
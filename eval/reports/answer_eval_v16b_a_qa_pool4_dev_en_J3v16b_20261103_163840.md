# Answer eval report (v16b_a_qa_pool4_dev_en, judge J3v16b)

- date: 2026-11-03T16:38:40.727559+00:00
- generated: 2026-11-03T15:13:37.752345+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 2/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J3v16b, qwen3.5:9b, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen3.5-9B@c202236
- judge order: dataset
- judge date: 2026-11-03T16:36:56.390139+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_pool4_dev_en.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_a_qa_pool4_dev_en.gen.jsonl, eval/runs/v16b_a_qa_pool4_dev_en.J3v16b.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.78 | 4.12 | 3.70 | 148 | 3/40 | 8401 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| e4001 | 0.50 | 4 | 4 | False | 10232 | False | 2964 / 2964 | ok |
| e4002 | 1.00 | 1 | 1 | True | 1413 | False | 2364 / 2364 | ok |
| e4006 | 1.00 | 4 | 3 | False | 13792 | False | 3378 / 3378 | ok |
| e4009 | 1.00 | 5 | 5 | False | 3971 | False | 2337 / 2337 | ok |
| e4011 | 1.00 | 4 | 3 | False | 7072 | False | 2626 / 2626 | ok |
| e4012 | 1.00 | 4 | 3 | False | 12998 | False | 3057 / 3057 | ok |
| e4015 | 0.50 | 4 | 3 | False | 8849 | False | 2646 / 2646 | ok |
| e4018 | 0.00 | 3 | 2 | False | 8515 | False | 2733 / 2733 | ok |
| e4024 | 1.00 | 5 | 5 | False | 8579 | False | 2926 / 2926 | ok |
| e4027 | 1.00 | 5 | 5 | False | 6149 | False | 2542 / 2542 | ok |
| e4028 | 1.00 | 5 | 5 | False | 5688 | False | 1701 / 1701 | ok |
| e4029 | 1.00 | 4 | 3 | False | 15716 | False | 3125 / 3125 | ok |
| e4030 | 0.50 | 5 | 5 | False | 6881 | False | 2360 / 2360 | ok |
| e4035 | 1.00 | 4 | 3 | False | 11564 | False | 3143 / 3143 | ok |
| e4036 | 1.00 | 4 | 3 | False | 8362 | False | 2965 / 2965 | ok |
| e4037 | 1.00 | 5 | 5 | False | 6738 | False | 2569 / 2569 | ok |
| e4041 | 1.00 | 5 | 5 | False | 3430 | False | 2295 / 2295 | ok |
| e4045 | 1.00 | 4 | 3 | False | 12045 | False | 2808 / 2808 | ok |
| e4050 | 1.00 | 4 | 3 | False | 13435 | False | 3031 / 3031 | ok |
| e4052 | 1.00 | 5 | 4 | False | 8809 | False | 2946 / 2946 | ok |
| e4053 | 1.00 | 4 | 3 | False | 8918 | False | 2936 / 2936 | ok |
| e4055 | 1.00 | 2 | 3 | False | 1814 | False | 2150 / 2150 | ok |
| e4057 | 1.00 | 5 | 5 | False | 7609 | False | 2578 / 2578 | ok |
| e4059 | 1.00 | 4 | 3 | False | 7481 | False | 2554 / 2554 | ok |
| e4062 | 0.33 | 2 | 1 | True | 16041 | False | 3287 / 3287 | ok |
| e4064 | 0.33 | 4 | 3 | False | 9272 | False | 2944 / 2944 | ok |
| e4066 | 0.00 | 5 | 5 | False | 8313 | False | 2740 / 2740 | ok |
| e4069 | 0.33 | 2 | 1 | True | 13690 | False | 3077 / 3077 | ok |
| e4071 | 1.00 | 5 | 5 | False | 4587 | False | 2398 / 2398 | ok |
| e4075 | 0.67 | 5 | 5 | False | 6003 | False | 2459 / 2459 | ok |
| e4089 | 0.00 | 5 | 5 | False | 5730 | False | 2568 / 2568 | ok |
| e4093 | 1.00 | 5 | 5 | False | 9677 | False | 2830 / 2830 | ok |
| e4095 | 0.50 | 4 | 3 | False | 7665 | False | 2392 / 2392 | ok |
| e4096 | 1.00 | 4 | 4 | False | 4428 | False | 2463 / 2463 | ok |
| e4097 | 1.00 | 4 | 3 | False | 5549 | False | 2349 / 2349 | ok |
| e4098 | 0.00 | 2 | 3 | False | 8440 | False | 2911 / 2911 | ok |
| e4099 | 1.00 | 5 | 5 | False | 10020 | False | 2943 / 2943 | ok |
| e4100 | 1.00 | 5 | 5 | False | 8916 | False | 2463 / 2463 | ok |
| e4103 | 0.50 | 5 | 5 | False | 4345 | False | 2108 / 2108 | ok |
| e4107 | 1.00 | 4 | 3 | False | 12373 | False | 3045 / 3045 | ok |

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
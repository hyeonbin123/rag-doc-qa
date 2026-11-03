# Answer eval report (v16b_a_qa_pool4_dev_en, judge J2v16b)

- date: 2026-11-03T16:05:57.987090+00:00
- generated: 2026-11-03T15:13:37.752345+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 2/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J2v16b, gemma4:12b-it-qat, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: google/gemma-4-12B-it@707f0a3
- judge order: dataset
- judge date: 2026-11-03T16:03:35.667283+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_pool4_dev_en.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_a_qa_pool4_dev_en.gen.jsonl, eval/runs/v16b_a_qa_pool4_dev_en.J2v16b.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.78 | 3.67 | 3.52 | 141 | 13/40 | 8401 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| e4001 | 0.50 | 4 | 4 | False | 10232 | False | 2992 / 2992 | ok |
| e4002 | 1.00 | 1 | 1 | False | 1413 | False | 2457 / 2457 | ok |
| e4006 | 1.00 | 3 | 3 | False | 13792 | False | 3541 / 3541 | ok |
| e4009 | 1.00 | 5 | 5 | False | 3971 | False | 2397 / 2397 | ok |
| e4011 | 1.00 | 2 | 2 | True | 7072 | False | 2663 / 2663 | ok |
| e4012 | 1.00 | 2 | 2 | True | 12998 | False | 3234 / 3234 | ok |
| e4015 | 0.50 | 5 | 5 | False | 8849 | False | 2745 / 2745 | ok |
| e4018 | 0.00 | 2 | 1 | True | 8515 | False | 2822 / 2822 | ok |
| e4024 | 1.00 | 5 | 5 | False | 8579 | False | 3025 / 3025 | ok |
| e4027 | 1.00 | 5 | 5 | False | 6149 | False | 2698 / 2698 | ok |
| e4028 | 1.00 | 5 | 5 | False | 5688 | False | 1804 / 1804 | ok |
| e4029 | 1.00 | 2 | 2 | True | 15716 | False | 3281 / 3281 | ok |
| e4030 | 0.50 | 5 | 5 | False | 6881 | False | 2444 / 2444 | ok |
| e4035 | 1.00 | 2 | 2 | True | 11564 | False | 3277 / 3277 | ok |
| e4036 | 1.00 | 5 | 5 | False | 8362 | False | 3166 / 3166 | ok |
| e4037 | 1.00 | 5 | 5 | False | 6738 | False | 2591 / 2591 | ok |
| e4041 | 1.00 | 5 | 5 | False | 3430 | False | 2344 / 2344 | ok |
| e4045 | 1.00 | 5 | 5 | False | 12045 | False | 2909 / 2909 | ok |
| e4050 | 1.00 | 4 | 3 | False | 13435 | False | 3161 / 3161 | ok |
| e4052 | 1.00 | 5 | 5 | False | 8809 | False | 3014 / 3014 | ok |
| e4053 | 1.00 | 3 | 2 | True | 8918 | False | 3085 / 3085 | ok |
| e4055 | 1.00 | 1 | 1 | False | 1814 | False | 2184 / 2184 | ok |
| e4057 | 1.00 | 5 | 4 | False | 7609 | False | 2655 / 2655 | ok |
| e4059 | 1.00 | 5 | 5 | False | 7481 | False | 2657 / 2657 | ok |
| e4062 | 0.33 | 1 | 1 | True | 16041 | False | 3484 / 3484 | ok |
| e4064 | 0.33 | 2 | 2 | True | 9272 | False | 3068 / 3068 | ok |
| e4066 | 0.00 | 5 | 5 | False | 8313 | False | 2770 / 2770 | ok |
| e4069 | 0.33 | 1 | 1 | True | 13690 | False | 3149 / 3149 | ok |
| e4071 | 1.00 | 5 | 5 | False | 4587 | False | 2438 / 2438 | ok |
| e4075 | 0.67 | 5 | 4 | False | 6003 | False | 2523 / 2523 | ok |
| e4089 | 0.00 | 1 | 1 | True | 5730 | False | 2634 / 2634 | ok |
| e4093 | 1.00 | 5 | 5 | False | 9677 | False | 2919 / 2919 | ok |
| e4095 | 0.50 | 2 | 2 | True | 7665 | False | 2412 / 2412 | ok |
| e4096 | 1.00 | 5 | 4 | False | 4428 | False | 2512 / 2512 | ok |
| e4097 | 1.00 | 3 | 3 | True | 5549 | False | 2440 / 2440 | ok |
| e4098 | 0.00 | 1 | 1 | True | 8440 | False | 3104 / 3104 | ok |
| e4099 | 1.00 | 5 | 5 | False | 10020 | False | 2968 / 2968 | ok |
| e4100 | 1.00 | 5 | 5 | False | 8916 | False | 2527 / 2527 | ok |
| e4103 | 0.50 | 5 | 5 | False | 4345 | False | 2213 / 2213 | ok |
| e4107 | 1.00 | 5 | 5 | False | 12373 | False | 3099 / 3099 | ok |

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
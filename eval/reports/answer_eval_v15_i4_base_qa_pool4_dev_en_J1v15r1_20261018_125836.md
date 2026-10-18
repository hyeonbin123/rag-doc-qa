# Answer eval report (v15_i4_base_qa_pool4_dev_en, judge J1v15r1)

- date: 2026-10-18T12:58:36.778989+00:00
- generated: 2026-10-18T12:44:34.805626+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 2/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J1v15r1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-18T12:57:01.569052+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_pool4_dev_en.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_base_qa_pool4_dev_en.gen.jsonl, eval/runs/v15_i4_base_qa_pool4_dev_en.J1v15r1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.80 | 4.38 | 4.67 | 187 | 2/40 | 9083 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| e4001 | 0.50 | 4 | 5 | False | 10665 | False | 2894 / 2894 | ok |
| e4002 | 1.00 | 2 | 1 | True | 3973 | False | 2298 / 2298 | ok |
| e4006 | 1.00 | 4 | 5 | False | 12712 | False | 3153 / 3153 | ok |
| e4009 | 1.00 | 4 | 5 | False | 4471 | False | 2283 / 2283 | ok |
| e4011 | 1.00 | 4 | 5 | False | 7628 | False | 2509 / 2509 | ok |
| e4012 | 1.00 | 5 | 5 | False | 13965 | False | 2945 / 2945 | ok |
| e4015 | 0.50 | 4 | 5 | False | 10021 | False | 2554 / 2554 | ok |
| e4018 | 1.00 | 4 | 5 | False | 14999 | False | 3038 / 3038 | ok |
| e4024 | 1.00 | 5 | 5 | False | 7416 | False | 2644 / 2644 | ok |
| e4027 | 1.00 | 5 | 5 | False | 7032 | False | 2443 / 2443 | ok |
| e4028 | 1.00 | 5 | 5 | False | 5610 | False | 1592 / 1592 | ok |
| e4029 | 1.00 | 4 | 4 | False | 17402 | False | 3017 / 3017 | ok |
| e4030 | 0.50 | 4 | 4 | False | 8696 | False | 2377 / 2377 | ok |
| e4035 | 1.00 | 4 | 5 | False | 14303 | False | 3051 / 3051 | ok |
| e4036 | 1.00 | 5 | 5 | False | 9063 | False | 2887 / 2887 | ok |
| e4037 | 1.00 | 4 | 5 | False | 7311 | False | 2531 / 2531 | ok |
| e4041 | 1.00 | 5 | 5 | False | 3922 | False | 2213 / 2213 | ok |
| e4045 | 1.00 | 4 | 4 | False | 12949 | False | 2730 / 2730 | ok |
| e4050 | 1.00 | 4 | 4 | False | 13508 | False | 2852 / 2852 | ok |
| e4052 | 1.00 | 5 | 5 | False | 10856 | False | 2960 / 2960 | ok |
| e4053 | 0.50 | 4 | 4 | False | 7603 | False | 2593 / 2593 | ok |
| e4055 | 1.00 | 4 | 4 | False | 4350 | False | 2103 / 2103 | ok |
| e4057 | 1.00 | 5 | 5 | False | 8330 | False | 2513 / 2513 | ok |
| e4059 | 1.00 | 5 | 5 | False | 7968 | False | 2473 / 2473 | ok |
| e4062 | 1.00 | 5 | 5 | False | 15898 | False | 2945 / 2945 | ok |
| e4064 | 0.67 | 4 | 5 | False | 12309 | False | 3009 / 3009 | ok |
| e4066 | 0.00 | 4 | 5 | False | 8877 | False | 2615 / 2615 | ok |
| e4069 | 0.33 | 4 | 4 | False | 14437 | False | 2948 / 2948 | ok |
| e4071 | 0.50 | 3 | 4 | True | 16590 | False | 3051 / 3051 | ok |
| e4075 | 0.67 | 5 | 5 | False | 3906 | False | 2182 / 2182 | ok |
| e4089 | 0.00 | 5 | 5 | False | 6223 | False | 2478 / 2478 | ok |
| e4093 | 1.00 | 5 | 5 | False | 12324 | False | 2893 / 2893 | ok |
| e4095 | 0.50 | 4 | 5 | False | 15471 | False | 2973 / 2973 | ok |
| e4096 | 1.00 | 5 | 5 | False | 9103 | False | 2678 / 2678 | ok |
| e4097 | 1.00 | 5 | 5 | False | 6394 | False | 2287 / 2287 | ok |
| e4098 | 0.00 | 4 | 4 | False | 7943 | False | 2761 / 2761 | ok |
| e4099 | 1.00 | 5 | 5 | False | 11131 | False | 2850 / 2850 | ok |
| e4100 | 1.00 | 5 | 5 | False | 9912 | False | 2372 / 2372 | ok |
| e4103 | 0.50 | 4 | 5 | False | 5019 | False | 2044 / 2044 | ok |
| e4107 | 1.00 | 5 | 5 | False | 13603 | False | 2834 / 2834 | ok |

## Worst questions (lowest keyword coverage)

- **e4066** (0.00): What is dependency injection in FastAPI and how is it different from just calling a helper function inside my endpoint?
  > Dependency injection in FastAPI is a system that allows you to declare dependencies (functions or objects) that your path operation functions need, and FastAPI will handle providing those dependencies
- **e4089** (0.00): How do I hide an internal endpoint from the OpenAPI schema completely?
  > You can hide an internal endpoint from the OpenAPI schema by using the `include_in_openapi` parameter in the route definition.

Here's how you can do it:

```python
from fastapi import FastAPI
from fa
- **e4098** (0.00): How do I gzip-compress large responses?
  > You can use the `GzipResponse` from Starlette to gzip-compress large responses. However, this feature is not directly provided in FastAPI's response classes.

Here's how you can do it using Starlette'
- **e4069** (0.33): I want requests with unknown query parameters to fail instead of being silently ignored. How?
  > To ensure that requests with unknown query parameters fail instead of being silently ignored, you need to configure your FastAPI application to enforce strict validation of query parameters.

Here's h
- **e4001** (0.50): Can you explain concurrency vs parallelism and how it relates to choosing async def in FastAPI?
  > Concurrency and parallelism are two different concepts in computing:

1. **Concurrency** refers to the ability of a system to handle multiple tasks at once, but not necessarily executing them simultan
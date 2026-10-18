# Answer eval report (v15_i4_base_qa_pool4_dev_en)

- date: 2026-10-18T12:51:17.828049+00:00
- generated: 2026-10-18T12:44:34.805626+00:00
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
- dataset: qa_pool4_dev_en.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_base_qa_pool4_dev_en.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.80 | n/a | n/a | n/a | 0/0 | 9083 | 0/40 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| e4001 | 0.50 | None | None | None | 10665 | False | None / None | - |
| e4002 | 1.00 | None | None | None | 3973 | False | None / None | - |
| e4006 | 1.00 | None | None | None | 12712 | False | None / None | - |
| e4009 | 1.00 | None | None | None | 4471 | False | None / None | - |
| e4011 | 1.00 | None | None | None | 7628 | False | None / None | - |
| e4012 | 1.00 | None | None | None | 13965 | False | None / None | - |
| e4015 | 0.50 | None | None | None | 10021 | False | None / None | - |
| e4018 | 1.00 | None | None | None | 14999 | False | None / None | - |
| e4024 | 1.00 | None | None | None | 7416 | False | None / None | - |
| e4027 | 1.00 | None | None | None | 7032 | False | None / None | - |
| e4028 | 1.00 | None | None | None | 5610 | False | None / None | - |
| e4029 | 1.00 | None | None | None | 17402 | False | None / None | - |
| e4030 | 0.50 | None | None | None | 8696 | False | None / None | - |
| e4035 | 1.00 | None | None | None | 14303 | False | None / None | - |
| e4036 | 1.00 | None | None | None | 9063 | False | None / None | - |
| e4037 | 1.00 | None | None | None | 7311 | False | None / None | - |
| e4041 | 1.00 | None | None | None | 3922 | False | None / None | - |
| e4045 | 1.00 | None | None | None | 12949 | False | None / None | - |
| e4050 | 1.00 | None | None | None | 13508 | False | None / None | - |
| e4052 | 1.00 | None | None | None | 10856 | False | None / None | - |
| e4053 | 0.50 | None | None | None | 7603 | False | None / None | - |
| e4055 | 1.00 | None | None | None | 4350 | False | None / None | - |
| e4057 | 1.00 | None | None | None | 8330 | False | None / None | - |
| e4059 | 1.00 | None | None | None | 7968 | False | None / None | - |
| e4062 | 1.00 | None | None | None | 15898 | False | None / None | - |
| e4064 | 0.67 | None | None | None | 12309 | False | None / None | - |
| e4066 | 0.00 | None | None | None | 8877 | False | None / None | - |
| e4069 | 0.33 | None | None | None | 14437 | False | None / None | - |
| e4071 | 0.50 | None | None | None | 16590 | False | None / None | - |
| e4075 | 0.67 | None | None | None | 3906 | False | None / None | - |
| e4089 | 0.00 | None | None | None | 6223 | False | None / None | - |
| e4093 | 1.00 | None | None | None | 12324 | False | None / None | - |
| e4095 | 0.50 | None | None | None | 15471 | False | None / None | - |
| e4096 | 1.00 | None | None | None | 9103 | False | None / None | - |
| e4097 | 1.00 | None | None | None | 6394 | False | None / None | - |
| e4098 | 0.00 | None | None | None | 7943 | False | None / None | - |
| e4099 | 1.00 | None | None | None | 11131 | False | None / None | - |
| e4100 | 1.00 | None | None | None | 9912 | False | None / None | - |
| e4103 | 0.50 | None | None | None | 5019 | False | None / None | - |
| e4107 | 1.00 | None | None | None | 13603 | False | None / None | - |

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
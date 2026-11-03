# Answer eval report (v16b_b_qa_pool4_dev_en, judge J1v16b)

- date: 2026-11-03T16:26:15.877130+00:00
- generated: 2026-11-03T15:19:40.822851+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 2/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J1v16b, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-11-03T16:25:25.124575+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_pool4_dev_en.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_b_qa_pool4_dev_en.gen.jsonl, eval/runs/v16b_b_qa_pool4_dev_en.J1v16b.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.72 | 4.22 | 4.53 | 181 | 1/40 | 6258 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| e4001 | 1.00 | 4 | 5 | False | 11021 | False | 2969 / 2969 | ok |
| e4002 | 1.00 | 3 | 3 | False | 1501 | False | 2308 / 2308 | ok |
| e4006 | 1.00 | 5 | 5 | False | 14265 | False | 3321 / 3321 | ok |
| e4009 | 1.00 | 5 | 5 | False | 9769 | False | 2768 / 2768 | ok |
| e4011 | 1.00 | 5 | 5 | False | 5468 | False | 2391 / 2391 | ok |
| e4012 | 1.00 | 4 | 4 | False | 15312 | False | 3094 / 3094 | ok |
| e4015 | 0.50 | 4 | 5 | False | 8829 | False | 2568 / 2568 | ok |
| e4018 | 0.00 | 4 | 4 | False | 1488 | False | 2285 / 2285 | ok |
| e4024 | 1.00 | 4 | 5 | False | 4996 | False | 2556 / 2556 | ok |
| e4027 | 1.00 | 5 | 5 | False | 5830 | False | 2424 / 2424 | ok |
| e4028 | 1.00 | 4 | 5 | False | 2516 | False | 1439 / 1439 | ok |
| e4029 | 1.00 | 4 | 4 | False | 14494 | False | 2909 / 2909 | ok |
| e4030 | 1.00 | 4 | 4 | False | 5739 | False | 2213 / 2213 | ok |
| e4035 | 1.00 | 4 | 4 | False | 15449 | False | 3264 / 3264 | ok |
| e4036 | 0.00 | 4 | 5 | False | 1663 | False | 2575 / 2575 | ok |
| e4037 | 1.00 | 5 | 5 | False | 6639 | False | 2536 / 2536 | ok |
| e4041 | 1.00 | 5 | 5 | False | 3370 | False | 2213 / 2213 | ok |
| e4045 | 1.00 | 4 | 4 | False | 13087 | False | 2785 / 2785 | ok |
| e4050 | 1.00 | 4 | 4 | False | 13473 | False | 2916 / 2916 | ok |
| e4052 | 1.00 | 5 | 5 | False | 9137 | False | 2878 / 2878 | ok |
| e4053 | 0.00 | 4 | 5 | False | 1535 | False | 2442 / 2442 | ok |
| e4055 | 0.00 | 4 | 5 | False | 1291 | False | 2059 / 2059 | ok |
| e4057 | 1.00 | 5 | 5 | False | 7732 | False | 2528 / 2528 | ok |
| e4059 | 1.00 | 5 | 5 | False | 7920 | False | 2526 / 2526 | ok |
| e4062 | 0.33 | 4 | 4 | False | 16075 | False | 3166 / 3166 | ok |
| e4064 | 0.00 | 3 | 4 | False | 1538 | False | 2418 / 2418 | ok |
| e4066 | 0.00 | 5 | 5 | False | 8085 | False | 2637 / 2637 | ok |
| e4069 | 0.33 | 4 | 4 | False | 14646 | False | 3022 / 3022 | ok |
| e4071 | 1.00 | 4 | 5 | False | 4524 | False | 2343 / 2343 | ok |
| e4075 | 0.67 | 4 | 5 | False | 5876 | False | 2353 / 2353 | ok |
| e4089 | 0.00 | 3 | 4 | False | 1490 | False | 2302 / 2302 | ok |
| e4093 | 1.00 | 4 | 5 | False | 5025 | False | 2377 / 2377 | ok |
| e4095 | 1.00 | 4 | 4 | False | 9736 | False | 2482 / 2482 | ok |
| e4096 | 1.00 | 5 | 5 | False | 7613 | False | 2648 / 2648 | ok |
| e4097 | 1.00 | 5 | 5 | False | 4812 | False | 2235 / 2235 | ok |
| e4098 | 0.00 | 1 | 1 | True | 1573 | False | 2498 / 2498 | ok |
| e4099 | 1.00 | 5 | 5 | False | 9123 | False | 2784 / 2784 | ok |
| e4100 | 1.00 | 5 | 5 | False | 10782 | False | 2521 / 2521 | ok |
| e4103 | 0.50 | 5 | 5 | False | 5055 | False | 2082 / 2082 | ok |
| e4107 | 0.67 | 4 | 4 | False | 5498 | False | 2279 / 2279 | ok |

## Worst questions (lowest keyword coverage)

- **e4018** (0.00): I return a RedirectResponse in one branch and a dict in another, and startup fails with "Invalid args for response field!". How do I fix the annotation?
  > I don't know: the provided documentation passages do not cover this question.
- **e4036** (0.00): What's the difference between response_model_exclude_unset, response_model_exclude_defaults and response_model_exclude_none?
  > I don't know: the provided documentation passages do not cover this question.
- **e4053** (0.00): How do I make a DELETE endpoint return 204 by default?
  > I don't know: the provided documentation passages do not cover this question.
- **e4055** (0.00): How do I declare outgoing webhooks in my OpenAPI schema with app.webhooks?
  > I don't know: the provided documentation passages do not cover this question.
- **e4064** (0.00): How can the same endpoint return 201 when it creates a resource but 200 when it already exists?
  > I don't know: the provided documentation passages do not cover this question.
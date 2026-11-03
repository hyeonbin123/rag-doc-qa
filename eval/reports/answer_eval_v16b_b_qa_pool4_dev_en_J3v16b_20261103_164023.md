# Answer eval report (v16b_b_qa_pool4_dev_en, judge J3v16b)

- date: 2026-11-03T16:40:23.694579+00:00
- generated: 2026-11-03T15:19:40.822851+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 2/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J3v16b, qwen3.5:9b, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen3.5-9B@c202236
- judge order: dataset
- judge date: 2026-11-03T16:38:40.798524+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_pool4_dev_en.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_b_qa_pool4_dev_en.gen.jsonl, eval/runs/v16b_b_qa_pool4_dev_en.J3v16b.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.72 | 3.92 | 3.55 | 142 | 6/40 | 6258 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| e4001 | 1.00 | 4 | 4 | False | 11021 | False | 3037 / 3037 | ok |
| e4002 | 1.00 | 1 | 1 | True | 1501 | False | 2374 / 2374 | ok |
| e4006 | 1.00 | 4 | 3 | False | 14265 | False | 3425 / 3425 | ok |
| e4009 | 1.00 | 5 | 4 | False | 9769 | False | 2839 / 2839 | ok |
| e4011 | 1.00 | 4 | 3 | False | 5468 | False | 2506 / 2506 | ok |
| e4012 | 1.00 | 4 | 3 | False | 15312 | False | 3226 / 3226 | ok |
| e4015 | 0.50 | 4 | 3 | False | 8829 | False | 2638 / 2638 | ok |
| e4018 | 0.00 | 2 | 3 | False | 1488 | False | 2338 / 2338 | ok |
| e4024 | 1.00 | 5 | 5 | False | 4996 | False | 2632 / 2632 | ok |
| e4027 | 1.00 | 5 | 5 | False | 5830 | False | 2526 / 2526 | ok |
| e4028 | 1.00 | 5 | 5 | False | 2516 | False | 1470 / 1470 | ok |
| e4029 | 1.00 | 2 | 1 | True | 14494 | False | 3023 / 3023 | ok |
| e4030 | 1.00 | 5 | 5 | False | 5739 | False | 2267 / 2267 | ok |
| e4035 | 1.00 | 4 | 3 | False | 15449 | False | 3432 / 3432 | ok |
| e4036 | 0.00 | 2 | 1 | True | 1663 | False | 2636 / 2636 | ok |
| e4037 | 1.00 | 5 | 5 | False | 6639 | False | 2570 / 2570 | ok |
| e4041 | 1.00 | 5 | 5 | False | 3370 | False | 2295 / 2295 | ok |
| e4045 | 1.00 | 5 | 5 | False | 13087 | False | 2866 / 2866 | ok |
| e4050 | 1.00 | 5 | 5 | False | 13473 | False | 3030 / 3030 | ok |
| e4052 | 1.00 | 5 | 4 | False | 9137 | False | 2953 / 2953 | ok |
| e4053 | 0.00 | 1 | 1 | True | 1535 | False | 2500 / 2500 | ok |
| e4055 | 0.00 | 2 | 2 | False | 1291 | False | 2106 / 2106 | ok |
| e4057 | 1.00 | 4 | 3 | False | 7732 | False | 2593 / 2593 | ok |
| e4059 | 1.00 | 5 | 4 | False | 7920 | False | 2596 / 2596 | ok |
| e4062 | 0.33 | 2 | 1 | True | 16075 | False | 3248 / 3248 | ok |
| e4064 | 0.00 | 2 | 2 | False | 1538 | False | 2477 / 2477 | ok |
| e4066 | 0.00 | 5 | 5 | False | 8085 | False | 2731 / 2731 | ok |
| e4069 | 0.33 | 2 | 1 | True | 14646 | False | 3153 / 3153 | ok |
| e4071 | 1.00 | 5 | 5 | False | 4524 | False | 2386 / 2386 | ok |
| e4075 | 0.67 | 5 | 5 | False | 5876 | False | 2447 / 2447 | ok |
| e4089 | 0.00 | 2 | 1 | False | 1490 | False | 2374 / 2374 | ok |
| e4093 | 1.00 | 5 | 5 | False | 5025 | False | 2447 / 2447 | ok |
| e4095 | 1.00 | 4 | 3 | False | 9736 | False | 2555 / 2555 | ok |
| e4096 | 1.00 | 5 | 5 | False | 7613 | False | 2705 / 2705 | ok |
| e4097 | 1.00 | 5 | 5 | False | 4812 | False | 2295 / 2295 | ok |
| e4098 | 0.00 | 2 | 2 | False | 1573 | False | 2545 / 2545 | ok |
| e4099 | 1.00 | 5 | 5 | False | 9123 | False | 2870 / 2870 | ok |
| e4100 | 1.00 | 5 | 5 | False | 10782 | False | 2618 / 2618 | ok |
| e4103 | 0.50 | 5 | 5 | False | 5055 | False | 2148 / 2148 | ok |
| e4107 | 0.67 | 5 | 4 | False | 5498 | False | 2471 / 2471 | ok |

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
# Answer eval report (v16b_b_qa_pool4_dev_en, judge J2v16b)

- date: 2026-11-03T16:08:18.267729+00:00
- generated: 2026-11-03T15:19:40.822851+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 2/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J2v16b, gemma4:12b-it-qat, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: google/gemma-4-12B-it@707f0a3
- judge order: dataset
- judge date: 2026-11-03T16:05:58.003708+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_pool4_dev_en.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_b_qa_pool4_dev_en.gen.jsonl, eval/runs/v16b_b_qa_pool4_dev_en.J2v16b.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.72 | 3.65 | 3.55 | 142 | 7/40 | 6258 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| e4001 | 1.00 | 5 | 5 | False | 11021 | False | 3073 / 3073 | ok |
| e4002 | 1.00 | 1 | 1 | False | 1501 | False | 2467 / 2467 | ok |
| e4006 | 1.00 | 3 | 3 | False | 14265 | False | 3588 / 3588 | ok |
| e4009 | 1.00 | 5 | 4 | False | 9769 | False | 2901 / 2901 | ok |
| e4011 | 1.00 | 2 | 2 | False | 5468 | False | 2542 / 2542 | ok |
| e4012 | 1.00 | 2 | 2 | True | 15312 | False | 3432 / 3432 | ok |
| e4015 | 0.50 | 2 | 2 | True | 8829 | False | 2731 / 2731 | ok |
| e4018 | 0.00 | 1 | 1 | False | 1488 | False | 2409 / 2409 | ok |
| e4024 | 1.00 | 5 | 5 | False | 4996 | False | 2726 / 2726 | ok |
| e4027 | 1.00 | 5 | 5 | False | 5830 | False | 2684 / 2684 | ok |
| e4028 | 1.00 | 5 | 5 | False | 2516 | False | 1557 / 1557 | ok |
| e4029 | 1.00 | 2 | 1 | True | 14494 | False | 3177 / 3177 | ok |
| e4030 | 1.00 | 5 | 5 | False | 5739 | False | 2352 / 2352 | ok |
| e4035 | 1.00 | 2 | 2 | True | 15449 | False | 3600 / 3600 | ok |
| e4036 | 0.00 | 1 | 1 | False | 1663 | False | 2800 / 2800 | ok |
| e4037 | 1.00 | 5 | 5 | False | 6639 | False | 2592 / 2592 | ok |
| e4041 | 1.00 | 5 | 5 | False | 3370 | False | 2344 / 2344 | ok |
| e4045 | 1.00 | 4 | 4 | False | 13087 | False | 2987 / 2987 | ok |
| e4050 | 1.00 | 4 | 4 | False | 13473 | False | 3174 / 3174 | ok |
| e4052 | 1.00 | 5 | 5 | False | 9137 | False | 3019 / 3019 | ok |
| e4053 | 0.00 | 1 | 1 | False | 1535 | False | 2629 / 2629 | ok |
| e4055 | 0.00 | 1 | 1 | False | 1291 | False | 2141 / 2141 | ok |
| e4057 | 1.00 | 5 | 4 | False | 7732 | False | 2671 / 2671 | ok |
| e4059 | 1.00 | 5 | 5 | False | 7920 | False | 2701 / 2701 | ok |
| e4062 | 0.33 | 1 | 1 | True | 16075 | False | 3450 / 3450 | ok |
| e4064 | 0.00 | 5 | 5 | False | 1538 | False | 2582 / 2582 | ok |
| e4066 | 0.00 | 5 | 5 | False | 8085 | False | 2764 / 2764 | ok |
| e4069 | 0.33 | 1 | 1 | True | 14646 | False | 3233 / 3233 | ok |
| e4071 | 1.00 | 5 | 5 | False | 4524 | False | 2427 / 2427 | ok |
| e4075 | 0.67 | 5 | 5 | False | 5876 | False | 2511 / 2511 | ok |
| e4089 | 0.00 | 1 | 1 | False | 1490 | False | 2436 / 2436 | ok |
| e4093 | 1.00 | 5 | 5 | False | 5025 | False | 2529 / 2529 | ok |
| e4095 | 1.00 | 2 | 2 | True | 9736 | False | 2590 / 2590 | ok |
| e4096 | 1.00 | 5 | 5 | False | 7613 | False | 2761 / 2761 | ok |
| e4097 | 1.00 | 5 | 4 | False | 4812 | False | 2383 / 2383 | ok |
| e4098 | 0.00 | 5 | 5 | False | 1573 | False | 2711 / 2711 | ok |
| e4099 | 1.00 | 5 | 5 | False | 9123 | False | 2896 / 2896 | ok |
| e4100 | 1.00 | 5 | 5 | False | 10782 | False | 2690 / 2690 | ok |
| e4103 | 0.50 | 5 | 5 | False | 5055 | False | 2268 / 2268 | ok |
| e4107 | 0.67 | 5 | 5 | False | 5498 | False | 2503 / 2503 | ok |

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
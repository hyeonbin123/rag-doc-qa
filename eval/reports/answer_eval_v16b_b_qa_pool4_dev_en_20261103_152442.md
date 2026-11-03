# Answer eval report (v16b_b_qa_pool4_dev_en)

- date: 2026-11-03T15:24:42.320204+00:00
- generated: 2026-11-03T15:19:40.822851+00:00
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
- per-item records: eval/runs/v16b_b_qa_pool4_dev_en.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.72 | n/a | n/a | n/a | 0/0 | 6258 | 0/40 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| e4001 | 1.00 | None | None | None | 11021 | False | None / None | - |
| e4002 | 1.00 | None | None | None | 1501 | False | None / None | - |
| e4006 | 1.00 | None | None | None | 14265 | False | None / None | - |
| e4009 | 1.00 | None | None | None | 9769 | False | None / None | - |
| e4011 | 1.00 | None | None | None | 5468 | False | None / None | - |
| e4012 | 1.00 | None | None | None | 15312 | False | None / None | - |
| e4015 | 0.50 | None | None | None | 8829 | False | None / None | - |
| e4018 | 0.00 | None | None | None | 1488 | False | None / None | - |
| e4024 | 1.00 | None | None | None | 4996 | False | None / None | - |
| e4027 | 1.00 | None | None | None | 5830 | False | None / None | - |
| e4028 | 1.00 | None | None | None | 2516 | False | None / None | - |
| e4029 | 1.00 | None | None | None | 14494 | False | None / None | - |
| e4030 | 1.00 | None | None | None | 5739 | False | None / None | - |
| e4035 | 1.00 | None | None | None | 15449 | False | None / None | - |
| e4036 | 0.00 | None | None | None | 1663 | False | None / None | - |
| e4037 | 1.00 | None | None | None | 6639 | False | None / None | - |
| e4041 | 1.00 | None | None | None | 3370 | False | None / None | - |
| e4045 | 1.00 | None | None | None | 13087 | False | None / None | - |
| e4050 | 1.00 | None | None | None | 13473 | False | None / None | - |
| e4052 | 1.00 | None | None | None | 9137 | False | None / None | - |
| e4053 | 0.00 | None | None | None | 1535 | False | None / None | - |
| e4055 | 0.00 | None | None | None | 1291 | False | None / None | - |
| e4057 | 1.00 | None | None | None | 7732 | False | None / None | - |
| e4059 | 1.00 | None | None | None | 7920 | False | None / None | - |
| e4062 | 0.33 | None | None | None | 16075 | False | None / None | - |
| e4064 | 0.00 | None | None | None | 1538 | False | None / None | - |
| e4066 | 0.00 | None | None | None | 8085 | False | None / None | - |
| e4069 | 0.33 | None | None | None | 14646 | False | None / None | - |
| e4071 | 1.00 | None | None | None | 4524 | False | None / None | - |
| e4075 | 0.67 | None | None | None | 5876 | False | None / None | - |
| e4089 | 0.00 | None | None | None | 1490 | False | None / None | - |
| e4093 | 1.00 | None | None | None | 5025 | False | None / None | - |
| e4095 | 1.00 | None | None | None | 9736 | False | None / None | - |
| e4096 | 1.00 | None | None | None | 7613 | False | None / None | - |
| e4097 | 1.00 | None | None | None | 4812 | False | None / None | - |
| e4098 | 0.00 | None | None | None | 1573 | False | None / None | - |
| e4099 | 1.00 | None | None | None | 9123 | False | None / None | - |
| e4100 | 1.00 | None | None | None | 10782 | False | None / None | - |
| e4103 | 0.50 | None | None | None | 5055 | False | None / None | - |
| e4107 | 0.67 | None | None | None | 5498 | False | None / None | - |

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
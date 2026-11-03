# Judge prompt truncation

- date: 2026-11-03T00:26:54.086532+00:00
- truncated: prompt_eval_count < tokenizer count - 16
- over context: tokenizer count > context - 1 (Ollama 0.35.1 cuts above that); context = each run's num_ctx
- offset: prompt_eval_count - tokenizer count, on prompts that were not cut

| run | judged | tokens counted p50 / max | over context | truncated | judge errors | offset median / min / max |
|---|---|---|---|---|---|---|
| v16a_c5_qa_dev.lg.J3v16a.judge.jsonl | 32 | 2507 / 3208 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16a_c5_qa_dev2_ko.lg.J3v16a.judge.jsonl | 40 | 1850 / 2431 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16a_c5_qa_dev_ko.lg.J3v16a.judge.jsonl | 32 | 1769 / 2273 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16a_c6_qa_dev.lg.J3v16a.judge.jsonl | 32 | 2507 / 3208 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16a_c6_qa_dev2_ko.lg.J3v16a.judge.jsonl | 40 | 1882 / 2564 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16a_c6_qa_dev_ko.lg.J3v16a.judge.jsonl | 32 | 1786 / 2261 | 0 | 0 | 0 | +0 / +0 / +0 |
| **all** | 208 | | 0 | 0 (0.0%) | 0 | |
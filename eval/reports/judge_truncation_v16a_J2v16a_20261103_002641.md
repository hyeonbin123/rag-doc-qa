# Judge prompt truncation

- date: 2026-11-03T00:26:41.141911+00:00
- truncated: prompt_eval_count < tokenizer count - 16
- over context: tokenizer count > context - 1 (Ollama 0.35.1 cuts above that); context = each run's num_ctx
- offset: prompt_eval_count - tokenizer count, on prompts that were not cut

| run | judged | tokens counted p50 / max | over context | truncated | judge errors | offset median / min / max |
|---|---|---|---|---|---|---|
| v16a_c5_qa_dev.lg.J2v16a.judge.jsonl | 32 | 2560 / 3362 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16a_c5_qa_dev2_ko.lg.J2v16a.judge.jsonl | 40 | 1984 / 2561 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16a_c5_qa_dev_ko.lg.J2v16a.judge.jsonl | 32 | 1880 / 2405 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16a_c6_qa_dev.lg.J2v16a.judge.jsonl | 32 | 2554 / 3362 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16a_c6_qa_dev2_ko.lg.J2v16a.judge.jsonl | 40 | 2020 / 2791 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16a_c6_qa_dev_ko.lg.J2v16a.judge.jsonl | 32 | 1887 / 2393 | 0 | 0 | 0 | +0 / +0 / +0 |
| **all** | 208 | | 0 | 0 (0.0%) | 0 | |
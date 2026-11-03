# Judge prompt truncation

- date: 2026-11-03T00:26:47.288071+00:00
- truncated: prompt_eval_count < tokenizer count - 16
- over context: tokenizer count > context - 1 (Ollama 0.35.1 cuts above that); context = each run's num_ctx
- offset: prompt_eval_count - tokenizer count, on prompts that were not cut

| run | judged | tokens counted p50 / max | over context | truncated | judge errors | offset median / min / max |
|---|---|---|---|---|---|---|
| v16a_c5_qa_dev.lg.J1v16a.judge.jsonl | 32 | 2443 / 3084 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16a_c5_qa_dev2_ko.lg.J1v16a.judge.jsonl | 40 | 2148 / 2690 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16a_c5_qa_dev_ko.lg.J1v16a.judge.jsonl | 32 | 2036 / 2536 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16a_c6_qa_dev.lg.J1v16a.judge.jsonl | 32 | 2443 / 3084 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16a_c6_qa_dev2_ko.lg.J1v16a.judge.jsonl | 40 | 2154 / 2809 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16a_c6_qa_dev_ko.lg.J1v16a.judge.jsonl | 32 | 2038 / 2549 | 0 | 0 | 0 | +0 / +0 / +0 |
| **all** | 208 | | 0 | 0 (0.0%) | 0 | |
# Judge prompt truncation

- date: 2026-10-08T17:00:06.293475+00:00
- truncated: prompt_eval_count < tokenizer count - 16
- over context: tokenizer count > context - 1 (Ollama 0.35.1 cuts above that); context = each run's num_ctx
- offset: prompt_eval_count - tokenizer count, on prompts that were not cut

| run | judged | tokens counted p50 / max | over context | truncated | judge errors | offset median / min / max |
|---|---|---|---|---|---|---|
| v13b_b2_g3_b0.lg.J1.judge.jsonl | 40 | 2048 / 2730 | 0 | 0 | 0 | +0 / +0 / +0 |
| v13b_b2_g3_p.lg.J1.judge.jsonl | 40 | 2036 / 2724 | 0 | 0 | 0 | +0 / +0 / +0 |
| **all** | 80 | | 0 | 0 (0.0%) | 0 | |
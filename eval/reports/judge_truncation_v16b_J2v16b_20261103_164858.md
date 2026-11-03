# Judge prompt truncation

- date: 2026-11-03T16:48:58.035959+00:00
- truncated: prompt_eval_count < tokenizer count - 16
- over context: tokenizer count > context - 1 (Ollama 0.35.1 cuts above that); context = each run's num_ctx
- offset: prompt_eval_count - tokenizer count, on prompts that were not cut

| run | judged | tokens counted p50 / max | over context | truncated | judge errors | offset median / min / max |
|---|---|---|---|---|---|---|
| v16b_a_qa_dev.J2v16b.judge.jsonl | 32 | 2554 / 3362 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16b_a_qa_dev2_ko.J2v16b.judge.jsonl | 40 | 2009 / 2787 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16b_a_qa_dev_ko.J2v16b.judge.jsonl | 32 | 1887 / 2393 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16b_a_qa_pool4_dev_en.J2v16b.judge.jsonl | 40 | 2758 / 3541 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16b_a_qa_pool4_dev_ko.J2v16b.judge.jsonl | 40 | 1981 / 3313 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16b_a_qa_pool5_ans_dev_en.J2v16b.judge.jsonl | 3 | 2699 / 2815 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16b_a_qa_pool5_ans_dev_ko.J2v16b.judge.jsonl | 6 | 1854 / 2068 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16b_b_qa_dev.J2v16b.judge.jsonl | 32 | 2526 / 3447 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16b_b_qa_dev2_ko.J2v16b.judge.jsonl | 40 | 2036 / 2547 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16b_b_qa_dev_ko.J2v16b.judge.jsonl | 32 | 1836 / 2487 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16b_b_qa_pool4_dev_en.J2v16b.judge.jsonl | 40 | 2687 / 3600 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16b_b_qa_pool4_dev_ko.J2v16b.judge.jsonl | 40 | 1909 / 3267 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16b_b_qa_pool5_ans_dev_en.J2v16b.judge.jsonl | 3 | 2615 / 2779 | 0 | 0 | 0 | +0 / +0 / +0 |
| v16b_b_qa_pool5_ans_dev_ko.J2v16b.judge.jsonl | 6 | 1790 / 2027 | 0 | 0 | 0 | +0 / +0 / +0 |
| **all** | 386 | | 0 | 0 (0.0%) | 0 | |
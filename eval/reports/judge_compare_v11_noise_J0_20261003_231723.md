# Judgment comparison: pass B - pass A, judge J0

- date: 2026-10-03T23:17:21.128795+00:00
- a: eval/runs/v11_A_qa_dev.J0.judge.jsonl, eval/runs/v11_A_qa_dev_ko.J0.judge.jsonl, eval/runs/v11_A_qa_test2.J0.judge.jsonl, eval/runs/v11_A_qa_test2_ko.J0.judge.jsonl
- b: eval/runs/v11_B_qa_dev.J0.judge.jsonl, eval/runs/v11_B_qa_dev_ko.J0.judge.jsonl, eval/runs/v11_B_qa_test2.J0.judge.jsonl, eval/runs/v11_B_qa_test2_ko.J0.judge.jsonl
- diff = b - a per item; interval: paired percentile bootstrap, 10000 resamples, seed 20261003, 90%
- items without a score on either side (no passages, judge error) are left out of that metric

| set | n paired | correctness sum a -> b (diff) | correctness mean diff [90% CI] | up / down / same | faithfulness sum a -> b (diff) | faithfulness mean diff [90% CI] | up / down / same | hallucinated a -> b (diff) | answers differ |
|---|---|---|---|---|---|---|---|---|---|
| qa_dev.jsonl | 32 | 149 -> 149 (+0) | +0.000 [+0.000, +0.000] | 0 / 0 / 32 | 132 -> 132 (+0) | +0.000 [+0.000, +0.000] | 0 / 0 / 32 | 1 -> 1 (+0) | 1 |
| qa_dev_ko.jsonl | 32 | 133 -> 133 (+0) | +0.000 [+0.000, +0.000] | 0 / 0 / 32 | 122 -> 122 (+0) | +0.000 [+0.000, +0.000] | 0 / 0 / 32 | 1 -> 1 (+0) | 0 |
| qa_test2.jsonl | 43 | 199 -> 199 (+0) | +0.000 [+0.000, +0.000] | 0 / 0 / 43 | 180 -> 180 (+0) | +0.000 [+0.000, +0.000] | 0 / 0 / 43 | 0 -> 0 (+0) | 0 |
| qa_test2_ko.jsonl | 43 | 175 -> 174 (-1) | -0.023 [-0.070, +0.000] | 0 / 1 / 42 | 164 -> 162 (-2) | -0.047 [-0.140, +0.000] | 0 / 1 / 42 | 3 -> 4 (+1) | 1 |
| all sets | 150 | 656 -> 655 (-1) | -0.007 [-0.020, +0.000] | 0 / 1 / 149 | 598 -> 596 (-2) | -0.013 [-0.040, +0.000] | 0 / 1 / 149 | 5 -> 6 (+1) | 2 |
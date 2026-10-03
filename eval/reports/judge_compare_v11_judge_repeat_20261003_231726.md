# Judgment comparison: J1 reversed order - J1, pass A

- date: 2026-10-03T23:17:24.777448+00:00
- a: eval/runs/v11_A_qa_dev.J1.judge.jsonl, eval/runs/v11_A_qa_dev_ko.J1.judge.jsonl, eval/runs/v11_A_qa_test2.J1.judge.jsonl, eval/runs/v11_A_qa_test2_ko.J1.judge.jsonl
- b: eval/runs/v11_A_qa_dev.J1rev.judge.jsonl, eval/runs/v11_A_qa_dev_ko.J1rev.judge.jsonl, eval/runs/v11_A_qa_test2.J1rev.judge.jsonl, eval/runs/v11_A_qa_test2_ko.J1rev.judge.jsonl
- diff = b - a per item; interval: paired percentile bootstrap, 10000 resamples, seed 20261003, 90%
- items without a score on either side (no passages, judge error) are left out of that metric

| set | n paired | correctness sum a -> b (diff) | correctness mean diff [90% CI] | up / down / same | faithfulness sum a -> b (diff) | faithfulness mean diff [90% CI] | up / down / same | hallucinated a -> b (diff) | answers differ |
|---|---|---|---|---|---|---|---|---|---|
| qa_dev.jsonl | 32 | 148 -> 147 (-1) | -0.031 [-0.125, +0.062] | 1 / 2 / 29 | 132 -> 130 (-2) | -0.062 [-0.125, +0.000] | 0 / 2 / 30 | 1 -> 1 (+0) | 0 |
| qa_dev_ko.jsonl | 32 | 133 -> 132 (-1) | -0.031 [-0.094, +0.000] | 0 / 1 / 31 | 122 -> 122 (+0) | +0.000 [+0.000, +0.000] | 0 / 0 / 32 | 0 -> 0 (+0) | 0 |
| qa_test2.jsonl | 43 | 198 -> 198 (+0) | +0.000 [+0.000, +0.000] | 0 / 0 / 43 | 178 -> 177 (-1) | -0.023 [-0.070, +0.000] | 0 / 1 / 42 | 0 -> 0 (+0) | 0 |
| qa_test2_ko.jsonl | 43 | 180 -> 180 (+0) | +0.000 [+0.000, +0.000] | 0 / 0 / 43 | 164 -> 164 (+0) | +0.000 [+0.000, +0.000] | 0 / 0 / 43 | 2 -> 2 (+0) | 0 |
| all sets | 150 | 659 -> 657 (-2) | -0.013 [-0.033, +0.007] | 1 / 3 / 146 | 596 -> 593 (-3) | -0.020 [-0.040, -0.007] | 0 / 3 / 147 | 3 -> 3 (+0) | 0 |
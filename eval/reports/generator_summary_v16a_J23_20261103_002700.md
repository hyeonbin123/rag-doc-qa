# Generator comparison (v16a_J23, judge J23v16a)

- date: 2026-11-03T00:26:59.917761+00:00
- C5: eval/runs/v16a_c5_qa_dev.lg.gen.jsonl, eval/runs/v16a_c5_qa_dev_ko.lg.gen.jsonl, eval/runs/v16a_c5_qa_dev2_ko.lg.gen.jsonl
- C6: eval/runs/v16a_c6_qa_dev.lg.gen.jsonl, eval/runs/v16a_c6_qa_dev_ko.lg.gen.jsonl, eval/runs/v16a_c6_qa_dev2_ko.lg.gen.jsonl
- correctness/faithfulness: J1 sums over judged items; kana/han: answers with kana or Han anywhere
- citations: replies that break the schema; cited numbers within 1..k; a cited passage on an expected page (raw-arm items the guard regenerated have no citations of their own and are left out)
- passages hold an expected page: answers written from passages that include a page the item expects (any translation), i.e. retrieval's share

| arm | lang | n | correctness sum | hallucinated | kana/han | faithfulness sum | gen p50 ms | done=length | thinking | citation errors | cites in range | cites expected page | passages hold an expected page | guard applied | guard retry p50 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C5 | en | 32 | 129.5 (32 judged) | 7 | 0 | 137.0 | 8401 | 0 | 0 | 0 | 31/32 | 27/32 | 29/32 | 0 | - |
| C5 | ko | 72 | 311.0 (72 judged) | 8 | 0 | 326.0 | 5385 | 0 | 0 | 0 | 71/72 | 66/72 | 69/72 | 0 | - |
| C5 | all | 104 | 440.5 (104 judged) | 15 | 0 | 463.0 | 5571 | 0 | 0 | 0 | 102/104 | 93/104 | 98/104 | 0 | - |
| C6 | en | 32 | 133.5 (32 judged) | 7 | 0 | 139.0 | 7856 | 0 | 0 | 0 | 31/32 | 28/32 | 29/32 | 0 | - |
| C6 | ko | 72 | 312.0 (72 judged) | 12 | 0 | 323.5 | 4695 | 0 | 0 | 0 | 71/72 | 67/72 | 69/72 | 0 | - |
| C6 | all | 104 | 445.5 (104 judged) | 19 | 0 | 462.5 | 4989 | 0 | 0 | 0 | 102/104 | 95/104 | 98/104 | 0 | - |

## Correctness against C5 (sum of per-item differences, mean [paired bootstrap 90%])

| arm | en | ko | all | answers differ |
|---|---|---|---|---|
| C6 | +4 (+0.125 [+0.000, +0.281]) | +1 (+0.014 [-0.097, +0.125]) | +5 (+0.048 [-0.038, +0.139]) | 62 |
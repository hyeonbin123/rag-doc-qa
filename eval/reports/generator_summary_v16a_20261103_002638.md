# Generator comparison (v16a, judge J2v16a)

- date: 2026-11-03T00:26:37.747207+00:00
- C5: eval/runs/v16a_c5_qa_dev.lg.gen.jsonl, eval/runs/v16a_c5_qa_dev_ko.lg.gen.jsonl, eval/runs/v16a_c5_qa_dev2_ko.lg.gen.jsonl
- C6: eval/runs/v16a_c6_qa_dev.lg.gen.jsonl, eval/runs/v16a_c6_qa_dev_ko.lg.gen.jsonl, eval/runs/v16a_c6_qa_dev2_ko.lg.gen.jsonl
- correctness/faithfulness: J1 sums over judged items; kana/han: answers with kana or Han anywhere
- citations: replies that break the schema; cited numbers within 1..k; a cited passage on an expected page (raw-arm items the guard regenerated have no citations of their own and are left out)
- passages hold an expected page: answers written from passages that include a page the item expects (any translation), i.e. retrieval's share

| arm | lang | n | correctness sum | hallucinated | kana/han | faithfulness sum | gen p50 ms | done=length | thinking | citation errors | cites in range | cites expected page | passages hold an expected page | guard applied | guard retry p50 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C5 | en | 32 | 127 (32 judged) | 6 | 0 | 132 | 8401 | 0 | 0 | 0 | 31/32 | 27/32 | 29/32 | 0 | - |
| C5 | ko | 72 | 315 (72 judged) | 7 | 0 | 328 | 5385 | 0 | 0 | 0 | 71/72 | 66/72 | 69/72 | 0 | - |
| C5 | all | 104 | 442 (104 judged) | 13 | 0 | 460 | 5571 | 0 | 0 | 0 | 102/104 | 93/104 | 98/104 | 0 | - |
| C6 | en | 32 | 130 (32 judged) | 6 | 0 | 134 | 7856 | 0 | 0 | 0 | 31/32 | 28/32 | 29/32 | 0 | - |
| C6 | ko | 72 | 316 (72 judged) | 9 | 0 | 327 | 4695 | 0 | 0 | 0 | 71/72 | 67/72 | 69/72 | 0 | - |
| C6 | all | 104 | 446 (104 judged) | 15 | 0 | 461 | 4989 | 0 | 0 | 0 | 102/104 | 95/104 | 98/104 | 0 | - |

## Correctness against C5 (sum of per-item differences, mean [paired bootstrap 90%])

| arm | en | ko | all | answers differ |
|---|---|---|---|---|
| C6 | +3 (+0.094 [-0.031, +0.281]) | +1 (+0.014 [-0.125, +0.167]) | +4 (+0.038 [-0.077, +0.163]) | 62 |
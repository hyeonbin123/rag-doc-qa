# Generator comparison (v14, judge J1)

- date: 2026-10-14T04:53:18.750861+00:00
- C3: eval/runs/v14_c3_qa_dev.lg.gen.jsonl, eval/runs/v14_c3_qa_dev_ko.lg.gen.jsonl, eval/runs/v14_c3_qa_dev2_ko.lg.gen.jsonl
- C4: eval/runs/v14_c4_qa_dev.lg.gen.jsonl, eval/runs/v14_c4_qa_dev_ko.lg.gen.jsonl, eval/runs/v14_c4_qa_dev2_ko.lg.gen.jsonl
- correctness/faithfulness: J1 sums over judged items; kana/han: answers with kana or Han anywhere
- citations: replies that break the schema; cited numbers within 1..k; a cited passage on an expected page (raw-arm items the guard regenerated have no citations of their own and are left out)
- passages hold an expected page: answers written from passages that include a page the item expects (any translation), i.e. retrieval's share

| arm | lang | n | correctness sum | hallucinated | kana/han | faithfulness sum | gen p50 ms | done=length | thinking | citation errors | cites in range | cites expected page | passages hold an expected page | guard applied | guard retry p50 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C3 | en | 32 | 153 (32 judged) | 1 | 0 | 143 | 11728 | 0 | 0 | 0 | 32/32 | 27/32 | 29/32 | 0 | - |
| C3 | ko | 72 | 346 (72 judged) | 1 | 0 | 319 | 7427 | 0 | 0 | 0 | 72/72 | 66/72 | 69/72 | 0 | - |
| C3 | all | 104 | 499 (104 judged) | 2 | 0 | 462 | 7773 | 0 | 0 | 0 | 104/104 | 93/104 | 98/104 | 0 | - |
| C4 | en | 32 | 154 (32 judged) | 1 | 0 | 148 | 10379 | 0 | 0 | 0 | 32/32 | 27/32 | 28/32 | 0 | - |
| C4 | ko | 72 | 334 (72 judged) | 1 | 0 | 314 | 7408 | 1 | 0 | 0 | 72/72 | 65/72 | 68/72 | 0 | - |
| C4 | all | 104 | 488 (104 judged) | 2 | 0 | 462 | 7740 | 1 | 0 | 0 | 104/104 | 92/104 | 96/104 | 0 | - |

## Correctness against C3 (sum of per-item differences, mean [paired bootstrap 90%])

| arm | en | ko | all | answers differ |
|---|---|---|---|---|
| C4 | +1 (+0.031 [-0.094, +0.156]) | -12 (-0.167 [-0.278, -0.069]) | -11 (-0.106 [-0.183, -0.029]) | 94 |
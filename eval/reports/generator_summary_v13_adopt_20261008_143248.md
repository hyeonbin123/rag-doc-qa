# Generator comparison (v13_adopt, judge J1)

- date: 2026-10-08T14:32:47.254921+00:00
- G0: eval/runs/v13_adopt_g0_qa_test3b_ko.raw.gen.jsonl, eval/runs/v13_adopt_g0_qa_test3b_en.raw.gen.jsonl
- G0+LG: eval/runs/v13_adopt_g0_qa_test3b_ko.lg.gen.jsonl, eval/runs/v13_adopt_g0_qa_test3b_en.raw.gen.jsonl
- G3: eval/runs/v13_adopt_g3_qa_test3b_ko.raw.gen.jsonl, eval/runs/v13_adopt_g3_qa_test3b_en.raw.gen.jsonl
- G3+LG: eval/runs/v13_adopt_g3_qa_test3b_ko.lg.gen.jsonl, eval/runs/v13_adopt_g3_qa_test3b_en.raw.gen.jsonl
- correctness/faithfulness: J1 sums over judged items; kana/han: answers with kana or Han anywhere
- citations: replies that break the schema; cited numbers within 1..k; a cited passage on an expected page (raw-arm items the guard regenerated have no citations of their own and are left out)
- passages hold an expected page: answers written from passages that include a page the item expects (any translation), i.e. retrieval's share
- G0+LG: items the guard left alone take G0's judgment (80 items; its own judgment differed on 0)
- G3+LG: items the guard left alone take G3's judgment (80 items; its own judgment differed on 4)

| arm | lang | n | correctness sum | hallucinated | kana/han | faithfulness sum | gen p50 ms | done=length | thinking | citation errors | cites in range | cites expected page | passages hold an expected page | guard applied | guard retry p50 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G0 | en | 40 | 183 (40 judged) | 0 | 0 | 170 | 5382 | 0 | 0 | 0 | 40/40 | 37/40 | 37/40 | 0 | - |
| G0 | ko | 40 | 169 (40 judged) | 0 | 0 | 163 | 5005 | 0 | 0 | 0 | 40/40 | 36/40 | 39/40 | 0 | - |
| G0 | all | 80 | 352 (80 judged) | 0 | 0 | 333 | 5176 | 0 | 0 | 0 | 80/80 | 73/80 | 76/80 | 0 | - |
| G0+LG | en | 40 | 183 (40 judged) | 0 | 0 | 170 | 5382 | 0 | 0 | 0 | 40/40 | 37/40 | 37/40 | 0 | - |
| G0+LG | ko | 40 | 169 (40 judged) | 0 | 0 | 163 | 5005 | 0 | 0 | 0 | 40/40 | 36/40 | 39/40 | 0 | - |
| G0+LG | all | 80 | 352 (80 judged) | 0 | 0 | 333 | 5176 | 0 | 0 | 0 | 80/80 | 73/80 | 76/80 | 0 | - |
| G3 | en | 40 | 190 (40 judged) | 0 | 0 | 185 | 10221 | 1 | 0 | 0 | 40/40 | 37/40 | 37/40 | 0 | - |
| G3 | ko | 40 | 182 (40 judged) | 0 | 0 | 172 | 7635 | 0 | 0 | 0 | 40/40 | 39/40 | 39/40 | 0 | - |
| G3 | all | 80 | 372 (80 judged) | 0 | 0 | 357 | 9008 | 1 | 0 | 0 | 80/80 | 76/80 | 76/80 | 0 | - |
| G3+LG | en | 40 | 190 (40 judged) | 0 | 0 | 185 | 10221 | 1 | 0 | 0 | 40/40 | 37/40 | 37/40 | 0 | - |
| G3+LG | ko | 40 | 182 (40 judged) | 0 | 0 | 172 | 7635 | 0 | 0 | 0 | 40/40 | 39/40 | 39/40 | 0 | - |
| G3+LG | all | 80 | 372 (80 judged) | 0 | 0 | 357 | 9008 | 1 | 0 | 0 | 80/80 | 76/80 | 76/80 | 0 | - |

## Correctness against G0 (sum of per-item differences, mean [paired bootstrap 90%])

| arm | en | ko | all | answers differ |
|---|---|---|---|---|
| G0+LG | +0 (+0.000 [+0.000, +0.000]) | +0 (+0.000 [+0.000, +0.000]) | +0 (+0.000 [+0.000, +0.000]) | 0 |
| G3 | +7 (+0.175 [+0.025, +0.325]) | +13 (+0.325 [+0.200, +0.450]) | +20 (+0.250 [+0.150, +0.350]) | 79 |
| G3+LG | +7 (+0.175 [+0.025, +0.325]) | +13 (+0.325 [+0.200, +0.450]) | +20 (+0.250 [+0.150, +0.350]) | 79 |
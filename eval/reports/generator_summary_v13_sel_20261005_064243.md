# Generator comparison (v13_sel, judge J1)

- date: 2026-10-05T06:42:39.169508+00:00
- G0: eval/runs/v13_sel_g0_qa_dev.raw.gen.jsonl, eval/runs/v13_sel_g0_qa_dev_ko.raw.gen.jsonl, eval/runs/v13_sel_g0_qa_dev2_ko.raw.gen.jsonl
- G0+LG: eval/runs/v13_sel_g0_qa_dev.raw.gen.jsonl, eval/runs/v13_sel_g0_qa_dev_ko.lg.gen.jsonl, eval/runs/v13_sel_g0_qa_dev2_ko.lg.gen.jsonl
- G1: eval/runs/v13_sel_g1_qa_dev.raw.gen.jsonl, eval/runs/v13_sel_g1_qa_dev_ko.raw.gen.jsonl, eval/runs/v13_sel_g1_qa_dev2_ko.raw.gen.jsonl
- G1+LG: eval/runs/v13_sel_g1_qa_dev.raw.gen.jsonl, eval/runs/v13_sel_g1_qa_dev_ko.lg.gen.jsonl, eval/runs/v13_sel_g1_qa_dev2_ko.lg.gen.jsonl
- G2: eval/runs/v13_sel_g2_qa_dev.raw.gen.jsonl, eval/runs/v13_sel_g2_qa_dev_ko.raw.gen.jsonl, eval/runs/v13_sel_g2_qa_dev2_ko.raw.gen.jsonl
- G2+LG: eval/runs/v13_sel_g2_qa_dev.raw.gen.jsonl, eval/runs/v13_sel_g2_qa_dev_ko.lg.gen.jsonl, eval/runs/v13_sel_g2_qa_dev2_ko.lg.gen.jsonl
- G3: eval/runs/v13_sel_g3_qa_dev.raw.gen.jsonl, eval/runs/v13_sel_g3_qa_dev_ko.raw.gen.jsonl, eval/runs/v13_sel_g3_qa_dev2_ko.raw.gen.jsonl
- G3+LG: eval/runs/v13_sel_g3_qa_dev.raw.gen.jsonl, eval/runs/v13_sel_g3_qa_dev_ko.lg.gen.jsonl, eval/runs/v13_sel_g3_qa_dev2_ko.lg.gen.jsonl
- correctness/faithfulness: J1 sums over judged items; kana/han: answers with kana or Han anywhere
- citations: replies that break the schema; cited numbers within 1..k; a cited passage on an expected page (raw-arm items the guard regenerated have no citations of their own and are left out)

| arm | lang | n | correctness sum | hallucinated | kana/han | faithfulness sum | gen p50 ms | done=length | thinking | citation errors | cites in range | cites expected page | guard applied | guard retry p50 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G0 | en | 32 | 151 (32 judged) | 1 | 0 | 133 | 5614 | 0 | 0 | 0 | 31/32 | 29/32 | 0 | - |
| G0 | ko | 72 | 305 (72 judged) | 3 | 2 | 291 | 5220 | 0 | 0 | 0 | 70/70 | 57/70 | 2 | 1802 |
| G0 | all | 104 | 456 (104 judged) | 4 | 2 | 424 | 5319 | 0 | 0 | 0 | 101/102 | 86/102 | 2 | 1802 |
| G0+LG | en | 32 | 151 (32 judged) | 1 | 0 | 133 | 5614 | 0 | 0 | 0 | 31/32 | 29/32 | 0 | - |
| G0+LG | ko | 72 | 308 (72 judged) | 2 | 1 | 293 | 5260 | 0 | 0 | 0 | 72/72 | 58/72 | 2 | 1802 |
| G0+LG | all | 104 | 459 (104 judged) | 3 | 1 | 426 | 5344 | 0 | 0 | 0 | 103/104 | 87/104 | 2 | 1802 |
| G1 | en | 32 | 149 (32 judged) | 1 | 0 | 137 | 8581 | 0 | 0 | 0 | 32/32 | 29/32 | 0 | - |
| G1 | ko | 72 | 307 (72 judged) | 3 | 0 | 290 | 7304 | 0 | 0 | 0 | 72/72 | 63/72 | 0 | - |
| G1 | all | 104 | 456 (104 judged) | 4 | 0 | 427 | 7825 | 0 | 0 | 0 | 104/104 | 92/104 | 0 | - |
| G1+LG | en | 32 | 149 (32 judged) | 1 | 0 | 137 | 8581 | 0 | 0 | 0 | 32/32 | 29/32 | 0 | - |
| G1+LG | ko | 72 | 0 (0 judged) | 0 | 0 | 0 | 7304 | 0 | 0 | 0 | 72/72 | 63/72 | 0 | - |
| G1+LG | all | 104 | 149 (32 judged) | 1 | 0 | 137 | 7825 | 0 | 0 | 0 | 104/104 | 92/104 | 0 | - |
| G2 | en | 32 | 142 (32 judged) | 2 | 0 | 134 | 12008 | 0 | 0 | 0 | 32/32 | 29/32 | 0 | - |
| G2 | ko | 72 | 309 (72 judged) | 1 | 0 | 286 | 10791 | 0 | 0 | 0 | 72/72 | 62/72 | 0 | - |
| G2 | all | 104 | 451 (104 judged) | 3 | 0 | 420 | 11227 | 0 | 0 | 0 | 104/104 | 91/104 | 0 | - |
| G2+LG | en | 32 | 142 (32 judged) | 2 | 0 | 134 | 12008 | 0 | 0 | 0 | 32/32 | 29/32 | 0 | - |
| G2+LG | ko | 72 | 0 (0 judged) | 0 | 0 | 0 | 10791 | 0 | 0 | 0 | 72/72 | 62/72 | 0 | - |
| G2+LG | all | 104 | 142 (32 judged) | 2 | 0 | 134 | 11227 | 0 | 0 | 0 | 104/104 | 91/104 | 0 | - |
| G3 | en | 32 | 153 (32 judged) | 1 | 0 | 143 | 13598 | 0 | 0 | 0 | 32/32 | 27/32 | 0 | - |
| G3 | ko | 72 | 329 (72 judged) | 1 | 0 | 315 | 9483 | 2 | 0 | 0 | 72/72 | 59/72 | 0 | - |
| G3 | all | 104 | 482 (104 judged) | 2 | 0 | 458 | 9808 | 2 | 0 | 0 | 104/104 | 86/104 | 0 | - |
| G3+LG | en | 32 | 153 (32 judged) | 1 | 0 | 143 | 13598 | 0 | 0 | 0 | 32/32 | 27/32 | 0 | - |
| G3+LG | ko | 72 | 0 (0 judged) | 0 | 0 | 0 | 9483 | 2 | 0 | 0 | 72/72 | 59/72 | 0 | - |
| G3+LG | all | 104 | 153 (32 judged) | 1 | 0 | 143 | 9808 | 2 | 0 | 0 | 104/104 | 86/104 | 0 | - |

## Correctness against G0 (sum of per-item differences, mean [paired bootstrap 90%])

| arm | en | ko | all | answers differ |
|---|---|---|---|---|
| G0+LG | +0 (+0.000 [+0.000, +0.000]) | +3 (+0.042 [+0.000, +0.097]) | +3 (+0.029 [+0.000, +0.067]) | 2 |
| G1 | -2 (-0.062 [-0.156, +0.031]) | +2 (+0.028 [-0.125, +0.167]) | +0 (+0.000 [-0.106, +0.106]) | 104 |
| G1+LG | -2 (-0.062 [-0.156, +0.031]) | n/a | -2 (-0.062 [-0.156, +0.031]) | 104 |
| G2 | -9 (-0.281 [-0.469, -0.125]) | +4 (+0.056 [-0.069, +0.194]) | -5 (-0.048 [-0.163, +0.058]) | 104 |
| G2+LG | -9 (-0.281 [-0.469, -0.125]) | n/a | -9 (-0.281 [-0.469, -0.125]) | 104 |
| G3 | +2 (+0.062 [-0.062, +0.188]) | +24 (+0.333 [+0.208, +0.458]) | +26 (+0.250 [+0.154, +0.346]) | 103 |
| G3+LG | +2 (+0.062 [-0.062, +0.188]) | n/a | +2 (+0.062 [-0.062, +0.188]) | 103 |
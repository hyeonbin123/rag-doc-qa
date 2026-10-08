# Generator comparison (v13b_b2_g3_lg, judge J1)

- date: 2026-10-08T17:00:08.685116+00:00
- B0: eval/runs/v13b_b2_g3_b0.lg.gen.jsonl
- P: eval/runs/v13b_b2_g3_p.lg.gen.jsonl
- correctness/faithfulness: J1 sums over judged items; kana/han: answers with kana or Han anywhere
- citations: replies that break the schema; cited numbers within 1..k; a cited passage on an expected page (raw-arm items the guard regenerated have no citations of their own and are left out)
- passages hold an expected page: answers written from passages that include a page the item expects (any translation), i.e. retrieval's share

| arm | lang | n | correctness sum | hallucinated | kana/han | faithfulness sum | gen p50 ms | done=length | thinking | citation errors | cites in range | cites expected page | passages hold an expected page | guard applied | guard retry p50 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B0 | ko | 40 | 185 (40 judged) | 0 | 0 | 172 | 7489 | 0 | 0 | 0 | 40/40 | 39/40 | 39/40 | 0 | - |
| B0 | all | 40 | 185 (40 judged) | 0 | 0 | 172 | 7489 | 0 | 0 | 0 | 40/40 | 39/40 | 39/40 | 0 | - |
| P | ko | 40 | 186 (40 judged) | 0 | 0 | 174 | 6784 | 0 | 0 | 0 | 40/40 | 38/40 | 39/40 | 0 | - |
| P | all | 40 | 186 (40 judged) | 0 | 0 | 174 | 6784 | 0 | 0 | 0 | 40/40 | 38/40 | 39/40 | 0 | - |

## Correctness against B0 (sum of per-item differences, mean [paired bootstrap 90%])

| arm | en | ko | all | answers differ |
|---|---|---|---|---|
| P | n/a | +1 (+0.025 [-0.100, +0.150]) | +1 (+0.025 [-0.100, +0.150]) | 39 |
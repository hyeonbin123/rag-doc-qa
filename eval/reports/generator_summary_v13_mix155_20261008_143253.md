# Generator comparison (v13_mix155, judge )

- date: 2026-10-08T14:32:53.294018+00:00
- G0: eval/runs/v13_sel_g0_qa_dev_ko.raw.gen.jsonl, eval/runs/v13_sel_g0_qa_dev2_ko.raw.gen.jsonl, eval/runs/v13_adopt_g0_qa_test2_ko.raw.gen.jsonl, eval/runs/v13_adopt_g0_qa_test3b_ko.raw.gen.jsonl
- G0+LG: eval/runs/v13_sel_g0_qa_dev_ko.lg.gen.jsonl, eval/runs/v13_sel_g0_qa_dev2_ko.lg.gen.jsonl, eval/runs/v13_adopt_g0_qa_test2_ko.lg.gen.jsonl, eval/runs/v13_adopt_g0_qa_test3b_ko.lg.gen.jsonl
- G3: eval/runs/v13_sel_g3_qa_dev_ko.raw.gen.jsonl, eval/runs/v13_sel_g3_qa_dev2_ko.raw.gen.jsonl, eval/runs/v13_adopt_g3_qa_test2_ko.raw.gen.jsonl, eval/runs/v13_adopt_g3_qa_test3b_ko.raw.gen.jsonl
- G3+LG: eval/runs/v13_sel_g3_qa_dev_ko.lg.gen.jsonl, eval/runs/v13_sel_g3_qa_dev2_ko.lg.gen.jsonl, eval/runs/v13_adopt_g3_qa_test2_ko.lg.gen.jsonl, eval/runs/v13_adopt_g3_qa_test3b_ko.lg.gen.jsonl
- correctness/faithfulness: J1 sums over judged items; kana/han: answers with kana or Han anywhere
- citations: replies that break the schema; cited numbers within 1..k; a cited passage on an expected page (raw-arm items the guard regenerated have no citations of their own and are left out)
- passages hold an expected page: answers written from passages that include a page the item expects (any translation), i.e. retrieval's share

| arm | lang | n | correctness sum | hallucinated | kana/han | faithfulness sum | gen p50 ms | done=length | thinking | citation errors | cites in range | cites expected page | passages hold an expected page | guard applied | guard retry p50 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G0 | ko | 155 | 0 (0 judged) | 0 | 5 | 0 | 5174 | 0 | 0 | 0 | 150/150 | 123/150 | 135/155 | 5 | 1877 |
| G0 | all | 155 | 0 (0 judged) | 0 | 5 | 0 | 5174 | 0 | 0 | 0 | 150/150 | 123/150 | 135/155 | 5 | 1877 |
| G0+LG | ko | 155 | 0 (0 judged) | 0 | 2 | 0 | 5203 | 0 | 0 | 0 | 155/155 | 126/155 | 135/155 | 5 | 1877 |
| G0+LG | all | 155 | 0 (0 judged) | 0 | 2 | 0 | 5203 | 0 | 0 | 0 | 155/155 | 126/155 | 135/155 | 5 | 1877 |
| G3 | ko | 155 | 0 (0 judged) | 0 | 0 | 0 | 8257 | 2 | 0 | 0 | 155/155 | 129/155 | 135/155 | 0 | - |
| G3 | all | 155 | 0 (0 judged) | 0 | 0 | 0 | 8257 | 2 | 0 | 0 | 155/155 | 129/155 | 135/155 | 0 | - |
| G3+LG | ko | 155 | 0 (0 judged) | 0 | 0 | 0 | 8257 | 2 | 0 | 0 | 155/155 | 129/155 | 135/155 | 0 | - |
| G3+LG | all | 155 | 0 (0 judged) | 0 | 0 | 0 | 8257 | 2 | 0 | 0 | 155/155 | 129/155 | 135/155 | 0 | - |
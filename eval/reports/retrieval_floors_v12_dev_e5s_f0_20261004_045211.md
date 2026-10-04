# Score floors (v12_dev_e5s_f0.retrieval.jsonl)

- run: v12_dev_e5s_f0, database ragdb_p1_e5s, models {'ko': 'intfloat/multilingual-e5-small'}
- questions: 72; 'short' = questions keeping fewer than 5 results

| floor | short | Hit@3 | Hit@5 | Hit@10 | MRR |
|---|---|---|---|---|---|
| 0.3 | 0 | 0.833 | 0.875 | 0.944 | 0.816 |
| 0.25 | 0 | 0.833 | 0.875 | 0.944 | 0.816 |
| 0.2 | 0 | 0.833 | 0.875 | 0.944 | 0.816 |
| 0.15 | 0 | 0.833 | 0.875 | 0.944 | 0.816 |
| 0.1 | 0 | 0.833 | 0.875 | 0.944 | 0.816 |
| 0.05 | 0 | 0.833 | 0.875 | 0.944 | 0.816 |
| 0.0 | 0 | 0.833 | 0.875 | 0.944 | 0.816 |

rule pick (highest floor with no short question): **0.3**
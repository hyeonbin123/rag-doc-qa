# Score floors (v12_dev_g97_f0.retrieval.jsonl)

- run: v12_dev_g97_f0, database ragdb_p1_g97, models {'ko': 'ibm-granite/granite-embedding-97m-multilingual-r2@835ad14087e140460703cf0fae09f97d469d65c2'}
- questions: 72; 'short' = questions keeping fewer than 5 results

| floor | short | Hit@3 | Hit@5 | Hit@10 | MRR |
|---|---|---|---|---|---|
| 0.3 | 0 | 0.903 | 0.931 | 0.944 | 0.827 |
| 0.25 | 0 | 0.903 | 0.931 | 0.944 | 0.827 |
| 0.2 | 0 | 0.903 | 0.931 | 0.944 | 0.827 |
| 0.15 | 0 | 0.903 | 0.931 | 0.944 | 0.827 |
| 0.1 | 0 | 0.903 | 0.931 | 0.944 | 0.827 |
| 0.05 | 0 | 0.903 | 0.931 | 0.944 | 0.827 |
| 0.0 | 0 | 0.903 | 0.931 | 0.944 | 0.827 |

rule pick (highest floor with no short question): **0.3**
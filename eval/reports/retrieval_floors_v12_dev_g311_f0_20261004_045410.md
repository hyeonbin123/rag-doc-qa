# Score floors (v12_dev_g311_f0.retrieval.jsonl)

- run: v12_dev_g311_f0, database ragdb_p1_g311, models {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- questions: 72; 'short' = questions keeping fewer than 5 results

| floor | short | Hit@3 | Hit@5 | Hit@10 | MRR |
|---|---|---|---|---|---|
| 0.3 | 0 | 0.931 | 0.958 | 0.958 | 0.877 |
| 0.25 | 0 | 0.931 | 0.958 | 0.958 | 0.877 |
| 0.2 | 0 | 0.931 | 0.958 | 0.958 | 0.877 |
| 0.15 | 0 | 0.931 | 0.958 | 0.958 | 0.877 |
| 0.1 | 0 | 0.931 | 0.958 | 0.958 | 0.877 |
| 0.05 | 0 | 0.931 | 0.958 | 0.958 | 0.877 |
| 0.0 | 0 | 0.931 | 0.958 | 0.958 | 0.877 |

rule pick (highest floor with no short question): **0.3**
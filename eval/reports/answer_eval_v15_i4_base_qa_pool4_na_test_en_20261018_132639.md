# Answer eval report (v15_i4_base_qa_pool4_na_test_en)

- date: 2026-10-18T13:26:39.874604+00:00
- generated: 2026-10-18T13:25:05.394430+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/20)
- final answer call stopped by the output limit, done_reason=length: 0/20; reasoning output: 0/20; citation replies breaking the schema: 0/20
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_pool4_na_test_en.jsonl
- questions: 20
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_base_qa_pool4_na_test_en.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 1.00 | n/a | n/a | n/a | 0/0 | 4131 | 0/20 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| e4a03 | 1.00 | None | None | None | 4032 | False | None / None | - |
| e4a06 | 1.00 | None | None | None | 3914 | False | None / None | - |
| e4a09 | 1.00 | None | None | None | 4182 | False | None / None | - |
| e4a10 | 1.00 | None | None | None | 4410 | False | None / None | - |
| e4a11 | 1.00 | None | None | None | 4135 | False | None / None | - |
| e4a12 | 1.00 | None | None | None | 4480 | False | None / None | - |
| e4a13 | 1.00 | None | None | None | 3920 | False | None / None | - |
| e4a14 | 1.00 | None | None | None | 3802 | False | None / None | - |
| e4a15 | 1.00 | None | None | None | 7506 | False | None / None | - |
| e4a16 | 1.00 | None | None | None | 3855 | False | None / None | - |
| e4a19 | 1.00 | None | None | None | 3994 | False | None / None | - |
| e4a20 | 1.00 | None | None | None | 4040 | False | None / None | - |
| e4a22 | 1.00 | None | None | None | 4086 | False | None / None | - |
| e4a23 | 1.00 | None | None | None | 4493 | False | None / None | - |
| e4a25 | 1.00 | None | None | None | 4127 | False | None / None | - |
| e4a26 | 1.00 | None | None | None | 4350 | False | None / None | - |
| e4a27 | 1.00 | None | None | None | 4212 | False | None / None | - |
| e4a28 | 1.00 | None | None | None | 4339 | False | None / None | - |
| e4a29 | 1.00 | None | None | None | 4014 | False | None / None | - |
| e4a30 | 1.00 | None | None | None | 4346 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **e4a03** (1.00): On Azure App Service, where do I set the startup command and WEBSITES_PORT for a custom Python container?
  > You don't know.
- **e4a06** (1.00): In Tortoise ORM, how do I define a reverse ForeignKey relation and prefetch it in one query?
  > You don't know.
- **e4a09** (1.00): What Nginx proxy_read_timeout and proxy_buffering settings should I use for long-lived streaming responses?
  > I don't know the specific Nginx proxy_read_timeout and proxy_buffering settings you should use for long-lived streaming responses.
- **e4a10** (1.00): How do I write a Caddyfile that load-balances two upstream app servers with active health checks?
  > You don't know how to write a Caddyfile for load-balancing two upstream app servers with active health checks based on the provided context passages.
- **e4a11** (1.00): In Vue 3, how do I write an Axios interceptor that refreshes an expired JWT and replays the original request?
  > I don't know.
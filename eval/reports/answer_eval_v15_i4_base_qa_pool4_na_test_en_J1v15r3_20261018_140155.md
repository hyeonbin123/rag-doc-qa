# Answer eval report (v15_i4_base_qa_pool4_na_test_en, judge J1v15r3)

- date: 2026-10-18T14:01:55.428959+00:00
- generated: 2026-10-18T13:25:05.394430+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/20)
- final answer call stopped by the output limit, done_reason=length: 0/20; reasoning output: 0/20; citation replies breaking the schema: 0/20
- judge: J1v15r3, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-18T14:01:11.239840+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_pool4_na_test_en.jsonl
- questions: 20
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_base_qa_pool4_na_test_en.gen.jsonl, eval/runs/v15_i4_base_qa_pool4_na_test_en.J1v15r3.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 1.00 | 1.70 | 1.60 | 32 | 15/20 | 4131 | 0/20 | 0/20 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| e4a03 | 1.00 | 2 | 1 | True | 4032 | False | 2189 / 2189 | ok |
| e4a06 | 1.00 | 2 | 1 | True | 3914 | False | 2294 / 2294 | ok |
| e4a09 | 1.00 | 3 | 3 | False | 4182 | False | 2367 / 2367 | ok |
| e4a10 | 1.00 | 1 | 1 | True | 4410 | False | 2385 / 2385 | ok |
| e4a11 | 1.00 | 1 | 1 | True | 4135 | False | 2311 / 2311 | ok |
| e4a12 | 1.00 | 1 | 1 | True | 4480 | False | 2512 / 2512 | ok |
| e4a13 | 1.00 | 1 | 1 | True | 3920 | False | 2452 / 2452 | ok |
| e4a14 | 1.00 | 3 | 3 | False | 3802 | False | 2018 / 2018 | ok |
| e4a15 | 1.00 | 4 | 5 | False | 7506 | False | 2613 / 2613 | ok |
| e4a16 | 1.00 | 3 | 3 | False | 3855 | False | 1926 / 1926 | ok |
| e4a19 | 1.00 | 2 | 1 | False | 3994 | False | 2246 / 2246 | ok |
| e4a20 | 1.00 | 1 | 1 | True | 4040 | False | 2227 / 2227 | ok |
| e4a22 | 1.00 | 1 | 1 | True | 4086 | False | 2461 / 2461 | ok |
| e4a23 | 1.00 | 1 | 1 | True | 4493 | False | 2329 / 2329 | ok |
| e4a25 | 1.00 | 1 | 1 | True | 4127 | False | 2322 / 2322 | ok |
| e4a26 | 1.00 | 1 | 1 | True | 4350 | False | 2514 / 2514 | ok |
| e4a27 | 1.00 | 1 | 1 | True | 4212 | False | 2152 / 2152 | ok |
| e4a28 | 1.00 | 1 | 1 | True | 4339 | False | 2521 / 2521 | ok |
| e4a29 | 1.00 | 1 | 1 | True | 4014 | False | 2215 / 2215 | ok |
| e4a30 | 1.00 | 3 | 3 | True | 4346 | False | 2502 / 2502 | ok |

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
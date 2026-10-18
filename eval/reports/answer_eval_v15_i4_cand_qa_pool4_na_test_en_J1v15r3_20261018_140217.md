# Answer eval report (v15_i4_cand_qa_pool4_na_test_en, judge J1v15r3)

- date: 2026-10-18T14:02:17.913450+00:00
- generated: 2026-10-18T13:36:28.280013+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/17)
- final answer call stopped by the output limit, done_reason=length: 0/17; reasoning output: 0/17; citation replies breaking the schema: 0/17
- judge: J1v15r3, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-18T14:02:06.377146+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_pool4_na_test_en.jsonl
- questions: 17
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_cand_qa_pool4_na_test_en.gen.jsonl, eval/runs/v15_i4_cand_qa_pool4_na_test_en.J1v15r3.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 1.00 | 1.38 | 1.12 | 9 | 6/8 | 0 | 0/17 | 0/8 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| e4a03 | 1.00 | 2 | 1 | True | 3211 | False | 1321 / 1321 | ok |
| e4a06 | 1.00 | 1 | 1 | True | 2562 | False | 993 / 993 | ok |
| e4a09 | 1.00 | 2 | 1 | False | 3160 | False | 1400 / 1400 | ok |
| e4a10 | 1.00 | None | None | None | 0 | False | None / None | unchecked |
| e4a11 | 1.00 | None | None | None | 0 | False | None / None | unchecked |
| e4a12 | 1.00 | None | None | None | 0 | False | None / None | unchecked |
| e4a14 | 1.00 | 2 | 2 | False | 2581 | False | 1127 / 1127 | ok |
| e4a15 | 1.00 | 1 | 1 | True | 2166 | False | 571 / 571 | ok |
| e4a16 | 1.00 | None | None | None | 0 | False | None / None | unchecked |
| e4a19 | 1.00 | 1 | 1 | True | 2158 | False | 573 / 573 | ok |
| e4a20 | 1.00 | None | None | None | 0 | False | None / None | unchecked |
| e4a22 | 1.00 | None | None | None | 0 | False | None / None | unchecked |
| e4a23 | 1.00 | 1 | 1 | True | 2142 | False | 556 / 556 | ok |
| e4a26 | 1.00 | None | None | None | 0 | False | None / None | unchecked |
| e4a27 | 1.00 | 1 | 1 | True | 1754 | False | 896 / 896 | ok |
| e4a28 | 1.00 | None | None | None | 0 | False | None / None | unchecked |
| e4a29 | 1.00 | None | None | None | 0 | False | None / None | unchecked |

## Worst questions (lowest keyword coverage)

- **e4a03** (1.00): On Azure App Service, where do I set the startup command and WEBSITES_PORT for a custom Python container?
  > You don't know.
- **e4a06** (1.00): In Tortoise ORM, how do I define a reverse ForeignKey relation and prefetch it in one query?
  > You don't know.
- **e4a09** (1.00): What Nginx proxy_read_timeout and proxy_buffering settings should I use for long-lived streaming responses?
  > I don't know.
- **e4a10** (1.00): How do I write a Caddyfile that load-balances two upstream app servers with active health checks?
  > I don't know: the documentation passages I found do not cover this question.
- **e4a11** (1.00): In Vue 3, how do I write an Axios interceptor that refreshes an expired JWT and replays the original request?
  > I don't know: the documentation passages I found do not cover this question.
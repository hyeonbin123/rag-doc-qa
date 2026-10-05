# Answer eval report (v13_sel_g2_qa_dev.raw, judge J1)

- date: 2026-10-05T06:33:04.273914+00:00
- generated: 2026-10-05T05:31:53.009123+00:00
- provider: ollama
- model: gemma4:12b-it-qat
- model digest: 38044be4f923e5a55264ed7df4eaac2676651a905f735197c504045140c02bd3
- think: False, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: J1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-05T06:31:16.155183+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_dev.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_sel_g2_qa_dev.gen.jsonl, eval/runs/v13_sel_g2_qa_dev.raw.J1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.94 | 4.19 | 4.44 | 142 | 2/32 | 12008 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| d001 | 1.00 | 4 | 5 | False | 9586 | False | 1973 / 1973 | ok |
| d002 | 1.00 | 5 | 5 | False | 13871 | False | 2108 / 2108 | ok |
| d003 | 1.00 | 4 | 5 | False | 10171 | False | 2047 / 2047 | ok |
| d004 | 1.00 | 3 | 3 | False | 9957 | False | 2322 / 2322 | ok |
| d005 | 1.00 | 4 | 5 | False | 11233 | False | 2433 / 2433 | ok |
| d006 | 1.00 | 5 | 5 | False | 11521 | False | 2301 / 2301 | ok |
| d007 | 1.00 | 4 | 4 | False | 13536 | False | 2759 / 2759 | ok |
| d008 | 1.00 | 4 | 5 | False | 15826 | False | 2443 / 2443 | ok |
| d009 | 1.00 | 4 | 4 | False | 18259 | False | 2403 / 2403 | ok |
| d010 | 1.00 | 4 | 5 | False | 10015 | False | 2297 / 2297 | ok |
| d011 | 1.00 | 4 | 5 | False | 9314 | False | 2217 / 2217 | ok |
| d012 | 1.00 | 5 | 5 | False | 13907 | False | 2345 / 2345 | ok |
| d013 | 1.00 | 4 | 5 | False | 9375 | False | 2197 / 2197 | ok |
| d014 | 1.00 | 4 | 4 | False | 14468 | False | 1864 / 1864 | ok |
| d015 | 1.00 | 5 | 5 | False | 12495 | False | 2334 / 2334 | ok |
| d016 | 1.00 | 4 | 4 | False | 25333 | False | 2480 / 2480 | ok |
| d017 | 1.00 | 4 | 4 | False | 16175 | False | 2187 / 2187 | ok |
| d018 | 1.00 | 5 | 5 | False | 18365 | False | 2611 / 2611 | ok |
| d019 | 0.00 | 2 | 1 | True | 8258 | False | 2329 / 2329 | ok |
| d020 | 1.00 | 4 | 4 | False | 13106 | False | 2557 / 2557 | ok |
| d021 | 1.00 | 4 | 4 | False | 15275 | False | 2034 / 2034 | ok |
| d022 | 1.00 | 4 | 5 | False | 9769 | False | 2340 / 2340 | ok |
| d023 | 1.00 | 5 | 5 | False | 15194 | False | 2396 / 2396 | ok |
| d024 | 1.00 | 5 | 5 | False | 9357 | False | 1962 / 1962 | ok |
| d025 | 0.00 | 1 | 1 | True | 9815 | False | 2183 / 2183 | ok |
| d026 | 1.00 | 5 | 5 | False | 21230 | False | 2700 / 2700 | ok |
| d027 | 1.00 | 5 | 5 | False | 8471 | False | 1530 / 1530 | ok |
| d028 | 1.00 | 5 | 5 | False | 13619 | False | 2125 / 2125 | ok |
| d029 | 1.00 | 5 | 5 | False | 10647 | False | 2191 / 2191 | ok |
| d030 | 1.00 | 4 | 5 | False | 11158 | False | 2172 / 2172 | ok |
| d031 | 1.00 | 4 | 4 | False | 10206 | False | 2114 / 2114 | ok |
| d032 | 1.00 | 5 | 5 | False | 17831 | False | 2414 / 2414 | ok |

## Worst questions (lowest keyword coverage)

- **d019** (0.00): How can one path operation return 200 when it updates an item but 201 when it creates a new one?
  > I don't know.
- **d025** (0.00): Why should each Python project keep its own isolated set of installed packages?
  > I don't know.
- **d001** (1.00): How do you read a cookie value sent by the client in a path operation?
  > To read a cookie value sent by the client in a path operation, you can declare a cookie parameter using the `Cookie` class. You can define these parameters using the same structure as `Query` and `Pat
- **d002** (1.00): How do you set a cookie on the response FastAPI sends back?
  > You can set a cookie on the response in two ways:

*   **Use a `Response` parameter:** Declare a parameter of type `Response` in your path operation function (or in dependencies). You can then set the
- **d003** (1.00): How do you add a custom header to a response without returning a Response object yourself?
  > To add a custom header to a response without returning a `Response` object yourself, you can declare a parameter of type `Response` in your path operation function (or in dependencies). You can then s
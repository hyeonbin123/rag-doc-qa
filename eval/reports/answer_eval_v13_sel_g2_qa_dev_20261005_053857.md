# Answer eval report (v13_sel_g2_qa_dev)

- date: 2026-10-05T05:38:57.646310+00:00
- generated: 2026-10-05T05:31:53.009123+00:00
- provider: ollama
- model: gemma4:12b-it-qat
- model digest: 38044be4f923e5a55264ed7df4eaac2676651a905f735197c504045140c02bd3
- think: False, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_dev.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_sel_g2_qa_dev.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.94 | n/a | n/a | n/a | 0/0 | 12008 | 0/32 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| d001 | 1.00 | None | None | None | 9586 | False | None / None | - |
| d002 | 1.00 | None | None | None | 13871 | False | None / None | - |
| d003 | 1.00 | None | None | None | 10171 | False | None / None | - |
| d004 | 1.00 | None | None | None | 9957 | False | None / None | - |
| d005 | 1.00 | None | None | None | 11233 | False | None / None | - |
| d006 | 1.00 | None | None | None | 11521 | False | None / None | - |
| d007 | 1.00 | None | None | None | 13536 | False | None / None | - |
| d008 | 1.00 | None | None | None | 15826 | False | None / None | - |
| d009 | 1.00 | None | None | None | 18259 | False | None / None | - |
| d010 | 1.00 | None | None | None | 10015 | False | None / None | - |
| d011 | 1.00 | None | None | None | 9314 | False | None / None | - |
| d012 | 1.00 | None | None | None | 13907 | False | None / None | - |
| d013 | 1.00 | None | None | None | 9375 | False | None / None | - |
| d014 | 1.00 | None | None | None | 14468 | False | None / None | - |
| d015 | 1.00 | None | None | None | 12495 | False | None / None | - |
| d016 | 1.00 | None | None | None | 25333 | False | None / None | - |
| d017 | 1.00 | None | None | None | 16175 | False | None / None | - |
| d018 | 1.00 | None | None | None | 18365 | False | None / None | - |
| d019 | 0.00 | None | None | None | 8258 | False | None / None | - |
| d020 | 1.00 | None | None | None | 13106 | False | None / None | - |
| d021 | 1.00 | None | None | None | 15275 | False | None / None | - |
| d022 | 1.00 | None | None | None | 9769 | False | None / None | - |
| d023 | 1.00 | None | None | None | 15194 | False | None / None | - |
| d024 | 1.00 | None | None | None | 9357 | False | None / None | - |
| d025 | 0.00 | None | None | None | 9815 | False | None / None | - |
| d026 | 1.00 | None | None | None | 21230 | False | None / None | - |
| d027 | 1.00 | None | None | None | 8471 | False | None / None | - |
| d028 | 1.00 | None | None | None | 13619 | False | None / None | - |
| d029 | 1.00 | None | None | None | 10647 | False | None / None | - |
| d030 | 1.00 | None | None | None | 11158 | False | None / None | - |
| d031 | 1.00 | None | None | None | 10206 | False | None / None | - |
| d032 | 1.00 | None | None | None | 17831 | False | None / None | - |

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
# Answer eval report (v13_sel_g1_qa_dev.raw, judge J1)

- date: 2026-10-05T06:27:47.398837+00:00
- generated: 2026-10-05T05:13:50.652044+00:00
- provider: ollama
- model: qwen3.5:9b
- model digest: 6488c96fa5faab64bb65cbd30d4289e20e6130ef535a93ef9a49f42eda893ea7
- think: False, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: J1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-05T06:26:05.623428+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_dev.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_sel_g1_qa_dev.gen.jsonl, eval/runs/v13_sel_g1_qa_dev.raw.J1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | 4.28 | 4.66 | 149 | 1/32 | 8581 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| d001 | 1.00 | 4 | 5 | False | 8103 | False | 2002 / 2002 | ok |
| d002 | 1.00 | 5 | 5 | False | 9831 | False | 2132 / 2132 | ok |
| d003 | 1.00 | 5 | 5 | False | 6684 | False | 2039 / 2039 | ok |
| d004 | 0.00 | 3 | 3 | False | 7816 | False | 2349 / 2349 | ok |
| d005 | 1.00 | 4 | 5 | False | 7571 | False | 2413 / 2413 | ok |
| d006 | 1.00 | 5 | 5 | False | 8680 | False | 2290 / 2290 | ok |
| d007 | 1.00 | 4 | 5 | False | 8846 | False | 2725 / 2725 | ok |
| d008 | 1.00 | 5 | 5 | False | 14345 | False | 2519 / 2519 | ok |
| d009 | 1.00 | 4 | 5 | False | 9431 | False | 2248 / 2248 | ok |
| d010 | 1.00 | 4 | 5 | False | 7360 | False | 2305 / 2305 | ok |
| d011 | 1.00 | 4 | 5 | False | 6592 | False | 2206 / 2206 | ok |
| d012 | 1.00 | 5 | 5 | False | 9350 | False | 2308 / 2308 | ok |
| d013 | 1.00 | 4 | 5 | False | 6948 | False | 2186 / 2186 | ok |
| d014 | 1.00 | 4 | 5 | False | 8123 | False | 1776 / 1776 | ok |
| d015 | 1.00 | 5 | 5 | False | 9981 | False | 2344 / 2344 | ok |
| d016 | 1.00 | 4 | 4 | False | 14336 | False | 2450 / 2450 | ok |
| d017 | 1.00 | 4 | 4 | False | 9177 | False | 2127 / 2127 | ok |
| d018 | 1.00 | 5 | 5 | False | 10836 | False | 2561 / 2561 | ok |
| d019 | 0.00 | 3 | 3 | False | 9004 | False | 2406 / 2406 | ok |
| d020 | 1.00 | 5 | 5 | False | 11877 | False | 2640 / 2640 | ok |
| d021 | 1.00 | 4 | 5 | False | 8163 | False | 1946 / 1946 | ok |
| d022 | 1.00 | 4 | 5 | False | 7131 | False | 2372 / 2372 | ok |
| d023 | 1.00 | 4 | 5 | False | 7850 | False | 2263 / 2263 | ok |
| d024 | 1.00 | 5 | 5 | False | 6972 | False | 1954 / 1954 | ok |
| d025 | 0.00 | 1 | 1 | True | 8482 | False | 2222 / 2222 | ok |
| d026 | 1.00 | 4 | 5 | False | 15199 | False | 2696 / 2696 | ok |
| d027 | 1.00 | 5 | 5 | False | 6452 | False | 1531 / 1531 | ok |
| d028 | 1.00 | 5 | 5 | False | 8425 | False | 2039 / 2039 | ok |
| d029 | 1.00 | 5 | 5 | False | 9230 | False | 2225 / 2225 | ok |
| d030 | 1.00 | 5 | 5 | False | 9800 | False | 2200 / 2200 | ok |
| d031 | 1.00 | 4 | 4 | False | 8444 | False | 2157 / 2157 | ok |
| d032 | 1.00 | 5 | 5 | False | 10236 | False | 2318 / 2318 | ok |

## Worst questions (lowest keyword coverage)

- **d004** (0.00): How do you declare the type of data a path operation returns so FastAPI validates and filters it?
  > Based on the provided context passages, there is no information explaining how to declare the type of data a path operation **returns** for validation and filtering. The passages only describe how to 
- **d019** (0.00): How can one path operation return 200 when it updates an item but 201 when it creates a new one?
  > The provided context passages do not contain information about how to make a single path operation return different status codes (200 for updates and 201 for creation) based on the action performed. T
- **d025** (0.00): Why should each Python project keep its own isolated set of installed packages?
  > I don't know. The provided context passages discuss file structures, `APIRouter`, dependencies, and release notes, but they do not contain information about why each Python project should keep its own
- **d001** (1.00): How do you read a cookie value sent by the client in a path operation?
  > To read a cookie value sent by the client in a path operation, you declare a parameter of type `Cookie` in your function. You can define default values and validation parameters for it just like with 
- **d002** (1.00): How do you set a cookie on the response FastAPI sends back?
  > You can set a cookie on the response in two ways:

1. **Use a `Response` parameter**: Declare a parameter of type `Response` in your path operation function (or in dependencies). You can then set cook
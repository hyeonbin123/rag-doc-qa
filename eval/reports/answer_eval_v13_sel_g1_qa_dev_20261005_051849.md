# Answer eval report (v13_sel_g1_qa_dev)

- date: 2026-10-05T05:18:49.170138+00:00
- generated: 2026-10-05T05:13:50.652044+00:00
- provider: ollama
- model: qwen3.5:9b
- model digest: 6488c96fa5faab64bb65cbd30d4289e20e6130ef535a93ef9a49f42eda893ea7
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
- per-item records: eval/runs/v13_sel_g1_qa_dev.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | n/a | n/a | n/a | 0/0 | 8581 | 0/32 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| d001 | 1.00 | None | None | None | 8103 | False | None / None | - |
| d002 | 1.00 | None | None | None | 9831 | False | None / None | - |
| d003 | 1.00 | None | None | None | 6684 | False | None / None | - |
| d004 | 0.00 | None | None | None | 7816 | False | None / None | - |
| d005 | 1.00 | None | None | None | 7571 | False | None / None | - |
| d006 | 1.00 | None | None | None | 8680 | False | None / None | - |
| d007 | 1.00 | None | None | None | 8846 | False | None / None | - |
| d008 | 1.00 | None | None | None | 14345 | False | None / None | - |
| d009 | 1.00 | None | None | None | 9431 | False | None / None | - |
| d010 | 1.00 | None | None | None | 7360 | False | None / None | - |
| d011 | 1.00 | None | None | None | 6592 | False | None / None | - |
| d012 | 1.00 | None | None | None | 9350 | False | None / None | - |
| d013 | 1.00 | None | None | None | 6948 | False | None / None | - |
| d014 | 1.00 | None | None | None | 8123 | False | None / None | - |
| d015 | 1.00 | None | None | None | 9981 | False | None / None | - |
| d016 | 1.00 | None | None | None | 14336 | False | None / None | - |
| d017 | 1.00 | None | None | None | 9177 | False | None / None | - |
| d018 | 1.00 | None | None | None | 10836 | False | None / None | - |
| d019 | 0.00 | None | None | None | 9004 | False | None / None | - |
| d020 | 1.00 | None | None | None | 11877 | False | None / None | - |
| d021 | 1.00 | None | None | None | 8163 | False | None / None | - |
| d022 | 1.00 | None | None | None | 7131 | False | None / None | - |
| d023 | 1.00 | None | None | None | 7850 | False | None / None | - |
| d024 | 1.00 | None | None | None | 6972 | False | None / None | - |
| d025 | 0.00 | None | None | None | 8482 | False | None / None | - |
| d026 | 1.00 | None | None | None | 15199 | False | None / None | - |
| d027 | 1.00 | None | None | None | 6452 | False | None / None | - |
| d028 | 1.00 | None | None | None | 8425 | False | None / None | - |
| d029 | 1.00 | None | None | None | 9230 | False | None / None | - |
| d030 | 1.00 | None | None | None | 9800 | False | None / None | - |
| d031 | 1.00 | None | None | None | 8444 | False | None / None | - |
| d032 | 1.00 | None | None | None | 10236 | False | None / None | - |

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
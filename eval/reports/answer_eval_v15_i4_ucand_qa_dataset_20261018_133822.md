# Answer eval report (v15_i4_ucand_qa_dataset)

- date: 2026-10-18T13:38:22.671348+00:00
- generated: 2026-10-18T13:38:01.892498+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/3)
- final answer call stopped by the output limit, done_reason=length: 0/3; reasoning output: 0/3; citation replies breaking the schema: 0/3
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_dataset.jsonl
- questions: 3
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_ucand_qa_dataset.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 1.00 | n/a | n/a | n/a | 0/0 | 4914 | 0/3 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| q007 | 1.00 | None | None | None | 2233 | False | None / None | - |
| q011 | 1.00 | None | None | None | 4914 | False | None / None | - |
| q013 | 1.00 | None | None | None | 5987 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **q007** (1.00): What three things make up an 'origin' in the context of CORS?
  > Protocol, domain, and port.
- **q011** (1.00): How do you run cleanup code after a dependency has finished being used?
  > You can run cleanup code after a dependency has finished being used by using the `yield` statement in your dependency function. The code following the `yield` statement is executed after the response 
- **q013** (1.00): Why would you define separate input and output models for a user?
  > You define separate input and output models for a user to ensure that:

1. **Security**: The input model can include sensitive data like a password, while the output model excludes this sensitive data
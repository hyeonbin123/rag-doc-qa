# Answer eval report (v16b_b_qa_pool5_ans_dev_en)

- date: 2026-11-03T15:26:02.246101+00:00
- generated: 2026-11-03T15:25:48.669141+00:00
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
- corpus: source commit 50113da (277 documents); last fetched 2026-11-03T08:04:42.172603+00:00; chunks en 914, ko 621
- dataset: qa_pool5_ans_dev_en.jsonl
- questions: 3
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_b_qa_pool5_ans_dev_en.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.33 | n/a | n/a | n/a | 0/0 | 1562 | 0/3 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| e5n10 | 1.00 | None | None | None | 5671 | False | None / None | - |
| e5n27 | 0.00 | None | None | None | 1562 | False | None / None | - |
| e5n60 | 0.00 | None | None | None | 1375 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **e5n27** (0.00): Will a request with Content-Type: text/plain whose body is valid JSON still be parsed into my Pydantic body model, or is it rejected?
  > I don't know: the provided documentation passages do not cover this question.
- **e5n60** (0.00): Does pydantic-settings reread the .env file from disk every time I call Settings(), and how much does that actually cost per request if I don't wrap it in lru_cache?
  > I don't know: the provided documentation passages do not cover this question.
- **e5n10** (1.00): If a class-based dependency is listed in APIRouter(dependencies=[...]) and also declared as a parameter of the path operation, is the class instantiated once or twice per request?
  > The class-based dependency is instantiated once per request.

**Explanation:**

According to the context, when using dependencies in FastAPI, the system implements a dependency cache per request. This
# Answer eval report (v16b_b_qa_pool5_ans_dev_en, judge J2v16b)

- date: 2026-11-03T16:08:37.423620+00:00
- generated: 2026-11-03T15:25:48.669141+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/3)
- final answer call stopped by the output limit, done_reason=length: 0/3; reasoning output: 0/3; citation replies breaking the schema: 0/3
- judge: J2v16b, gemma4:12b-it-qat, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: google/gemma-4-12B-it@707f0a3
- judge order: dataset
- judge date: 2026-11-03T16:08:29.186847+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_pool5_ans_dev_en.jsonl
- questions: 3
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_b_qa_pool5_ans_dev_en.gen.jsonl, eval/runs/v16b_b_qa_pool5_ans_dev_en.J2v16b.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.33 | 5.00 | 5.00 | 15 | 0/3 | 1562 | 0/3 | 0/3 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| e5n10 | 1.00 | 5 | 5 | False | 5671 | False | 2779 / 2779 | ok |
| e5n27 | 0.00 | 5 | 5 | False | 1562 | False | 2615 / 2615 | ok |
| e5n60 | 0.00 | 5 | 5 | False | 1375 | False | 2286 / 2286 | ok |

## Worst questions (lowest keyword coverage)

- **e5n27** (0.00): Will a request with Content-Type: text/plain whose body is valid JSON still be parsed into my Pydantic body model, or is it rejected?
  > I don't know: the provided documentation passages do not cover this question.
- **e5n60** (0.00): Does pydantic-settings reread the .env file from disk every time I call Settings(), and how much does that actually cost per request if I don't wrap it in lru_cache?
  > I don't know: the provided documentation passages do not cover this question.
- **e5n10** (1.00): If a class-based dependency is listed in APIRouter(dependencies=[...]) and also declared as a parameter of the path operation, is the class instantiated once or twice per request?
  > The class-based dependency is instantiated once per request.

**Explanation:**

According to the context, when using dependencies in FastAPI, the system implements a dependency cache per request. This
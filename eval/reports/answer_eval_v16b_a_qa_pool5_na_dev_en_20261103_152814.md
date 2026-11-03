# Answer eval report (v16b_a_qa_pool5_na_dev_en)

- date: 2026-11-03T15:28:14.553454+00:00
- generated: 2026-11-03T15:27:34.131788+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/10)
- final answer call stopped by the output limit, done_reason=length: 0/10; reasoning output: 0/10; citation replies breaking the schema: 0/10
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- corpus: source commit 50113da (277 documents); last fetched 2026-11-03T08:04:42.172603+00:00; chunks en 914, ko 621
- dataset: qa_pool5_na_dev_en.jsonl
- questions: 10
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_a_qa_pool5_na_dev_en.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 1.00 | n/a | n/a | n/a | 0/0 | 3189 | 1/10 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| e5a02 | 1.00 | None | None | None | 1629 | False | None / None | - |
| e5a07 | 1.00 | None | None | None | 1335 | False | None / None | - |
| e5n14 | 1.00 | None | None | None | 1230 | False | None / None | - |
| e5n15 | 1.00 | None | None | None | 4205 | False | None / None | - |
| e5n25 | 1.00 | None | None | None | 3006 | False | None / None | - |
| e5n39 | 1.00 | None | None | None | 6664 | False | None / None | - |
| e5n40 | 1.00 | None | None | None | 6530 | True | None / None | - |
| e5n46 | 1.00 | None | None | None | 3372 | False | None / None | - |
| e5n56 | 1.00 | None | None | None | 5883 | False | None / None | - |
| e5n57 | 1.00 | None | None | None | 1334 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **e5a02** (1.00): In Django REST Framework, how do I write a custom throttle class that rate-limits requests per API key instead of per user?
  > I don't know.
- **e5a07** (1.00): In Flask, how does the g object differ from session, and how long does data stored in g live?
  > I don't know.
- **e5n14** (1.00): What is the default size of the threadpool FastAPI uses to run plain def path operations and dependencies, and how do I increase it?
  > I don't know.
- **e5n15** (1.00): If I set status_code=204 on a path operation but the function returns a dict, does FastAPI drop the body or send it anyway?
  > FastAPI will drop the body if the status code is 204, "No Content". This is because a 204 response indicates that the server successfully processed the request, but there is no content to return. When
- **e5n25** (1.00): When I use HTTPBasic(auto_error=False) and the Authorization header contains malformed base64, does the dependency return None or still raise a 401?
  > None
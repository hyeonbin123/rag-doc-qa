# Answer eval report (v15_i4_ubase_qa_test2)

- date: 2026-10-18T13:41:11.211191+00:00
- generated: 2026-10-18T13:38:36.430540+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/14)
- final answer call stopped by the output limit, done_reason=length: 0/14; reasoning output: 0/14; citation replies breaking the schema: 0/14
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'en': 'BAAI/bge-small-en-v1.5'}
- dataset: qa_test2.jsonl
- questions: 14
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_ubase_qa_test2.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.79 | n/a | n/a | n/a | 0/0 | 10011 | 0/14 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| t001 | 0.00 | None | None | None | 13044 | False | None / None | - |
| t002 | 1.00 | None | None | None | 5905 | False | None / None | - |
| t003 | 1.00 | None | None | None | 12578 | False | None / None | - |
| t006 | 1.00 | None | None | None | 15451 | False | None / None | - |
| t008 | 1.00 | None | None | None | 8680 | False | None / None | - |
| t010 | 0.00 | None | None | None | 9825 | False | None / None | - |
| t011 | 1.00 | None | None | None | 7090 | False | None / None | - |
| t013 | 1.00 | None | None | None | 10507 | False | None / None | - |
| t014 | 1.00 | None | None | None | 8795 | False | None / None | - |
| t015 | 1.00 | None | None | None | 9345 | False | None / None | - |
| t016 | 1.00 | None | None | None | 12293 | False | None / None | - |
| t019 | 1.00 | None | None | None | 15513 | False | None / None | - |
| t030 | 1.00 | None | None | None | 10197 | False | None / None | - |
| t043 | 0.00 | None | None | None | 7531 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **t001** (0.00): My React app on localhost:3000 gets blocked when it calls my API on port 8000. How do I fix it?
  > You need to configure your proxy settings in your React app to handle the path prefix added by the proxy server.

Here's how you can do it:

1. **Update your React app's proxy configuration:**

   If 
- **t010** (0.00): How do I let the user download a file from an endpoint?
  > You can use the `StreamingResponse` class in FastAPI to stream a file to the client. Here's how you can do it:

```python
from fastapi import FastAPI, File, UploadFile, StreamingResponse
from typing i
- **t043** (0.00): How do I add a field that the client sends but that should never be shown in the docs?
  > You can use the `exclude_from_schema` option in your Pydantic model to hide a field from the OpenAPI schema, which means it won't appear in the API documentation.

Here's how you can do it:

```python
- **t002** (1.00): How do I return a 404 error when the item someone asks for doesn't exist?
  > ```Python
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Example data structure
items = {
    "1": {"name": "Bar", "price": 10.0},
    "2": {"name": "Baz", "price": 20.0}
}

@app.get("
- **t003** (1.00): How can I load config values from a .env file?
  > To load config values from a `.env` file using Pydantic, follow these steps:

1. **Install the `python-dotenv` library**:
   ```bash
   $ uv add python-dotenv
   ```

2. **Create your `.env` file**:
 
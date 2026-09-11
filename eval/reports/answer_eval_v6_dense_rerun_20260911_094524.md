# Answer eval report (v6_dense_rerun)

- date: 2026-09-11T09:45:24.519045+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- top_k: 5
- retrieval mode: dense
- questions: 30
- judge skipped: False

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Hallucinated |
|---|---|---|---|
| 0.93 | 4.17 | 4.73 | 1/30 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated |
|---|---|---|---|---|
| q001 | 1.00 | 4 | 5 | False |
| q002 | 1.00 | 5 | 5 | False |
| q003 | 1.00 | 4 | 5 | False |
| q004 | 1.00 | 4 | 4 | False |
| q005 | 1.00 | 4 | 4 | False |
| q006 | 1.00 | 4 | 5 | False |
| q007 | 1.00 | 5 | 5 | False |
| q008 | 1.00 | 5 | 5 | False |
| q009 | 1.00 | 4 | 5 | False |
| q010 | 1.00 | 4 | 4 | False |
| q011 | 1.00 | 5 | 5 | False |
| q012 | 1.00 | 4 | 5 | False |
| q013 | 1.00 | 4 | 5 | False |
| q014 | 1.00 | 4 | 5 | False |
| q015 | 1.00 | 4 | 5 | False |
| q016 | 1.00 | 4 | 5 | False |
| q017 | 0.00 | 1 | 1 | True |
| q018 | 1.00 | 5 | 5 | False |
| q019 | 1.00 | 4 | 4 | False |
| q020 | 1.00 | 4 | 5 | False |
| q021 | 1.00 | 4 | 5 | False |
| q022 | 1.00 | 4 | 5 | False |
| q023 | 1.00 | 4 | 5 | False |
| q024 | 1.00 | 4 | 5 | False |
| q025 | 1.00 | 5 | 5 | False |
| q026 | 1.00 | 5 | 5 | False |
| q027 | 1.00 | 4 | 5 | False |
| q028 | 1.00 | 5 | 5 | False |
| q029 | 1.00 | 4 | 5 | False |
| q030 | 0.00 | 4 | 5 | False |

## Worst questions (lowest keyword coverage)

- **q017** (0.00): How should secrets like database credentials be provided to a FastAPI application?
  > You don't know. The provided context does not contain information about how to provide secrets like database credentials to a FastAPI application.
- **q030** (0.00): How do you split a large FastAPI application across multiple files?
  > To split a large FastAPI application across multiple files, you can use a structure similar to the example provided:

```
.
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── dependencies.py
│   └── 
- **q001** (1.00): How do you declare a path parameter with a type hint in FastAPI?
  > You can declare the type of a path parameter in the function, using standard Python type annotations. For example, declaring `item_id` to be an `int` provides editor support, data parsing, and data va
- **q002** (1.00): How do you mark a query parameter as optional in FastAPI?
  > You can mark a query parameter as optional in FastAPI by setting its default value to `None`.
- **q003** (1.00): How do you declare a request body in FastAPI?
  > To declare a request body in FastAPI, you use Pydantic models. You need to import `BaseModel` from `pydantic` and then declare your data model as a class that inherits from `BaseModel`. Use standard P
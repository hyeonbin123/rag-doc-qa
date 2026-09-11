# Answer eval report (v6_rerank_p05)

- date: 2026-09-11T09:34:49.757585+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- top_k: 5
- retrieval mode: rerank
- questions: 30
- judge skipped: False

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Hallucinated |
|---|---|---|---|
| 1.00 | 4.27 | 4.87 | 0/30 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated |
|---|---|---|---|---|
| q001 | 1.00 | 4 | 5 | False |
| q002 | 1.00 | 4 | 5 | False |
| q003 | 1.00 | 4 | 5 | False |
| q004 | 1.00 | 4 | 4 | False |
| q005 | 1.00 | 4 | 4 | False |
| q006 | 1.00 | 4 | 5 | False |
| q007 | 1.00 | 5 | 5 | False |
| q008 | 1.00 | 5 | 5 | False |
| q009 | 1.00 | 4 | 5 | False |
| q010 | 1.00 | 4 | 5 | False |
| q011 | 1.00 | 4 | 5 | False |
| q012 | 1.00 | 4 | 5 | False |
| q013 | 1.00 | 4 | 5 | False |
| q014 | 1.00 | 4 | 5 | False |
| q015 | 1.00 | 4 | 5 | False |
| q016 | 1.00 | 5 | 5 | False |
| q017 | 1.00 | 4 | 5 | False |
| q018 | 1.00 | 3 | 4 | False |
| q019 | 1.00 | 4 | 4 | False |
| q020 | 1.00 | 5 | 5 | False |
| q021 | 1.00 | 5 | 5 | False |
| q022 | 1.00 | 4 | 5 | False |
| q023 | 1.00 | 4 | 5 | False |
| q024 | 1.00 | 4 | 5 | False |
| q025 | 1.00 | 5 | 5 | False |
| q026 | 1.00 | 4 | 5 | False |
| q027 | 1.00 | 4 | 5 | False |
| q028 | 1.00 | 5 | 5 | False |
| q029 | 1.00 | 5 | 5 | False |
| q030 | 1.00 | 5 | 5 | False |

## Worst questions (lowest keyword coverage)

- **q001** (1.00): How do you declare a path parameter with a type hint in FastAPI?
  > You declare a path parameter with a type hint in FastAPI using standard Python type annotations. For example, you can declare an `item_id` path parameter to be of type `int` like this:

```python
from
- **q002** (1.00): How do you mark a query parameter as optional in FastAPI?
  > You can make a query parameter optional by setting its default value to `None`.
- **q003** (1.00): How do you declare a request body in FastAPI?
  > To declare a request body in FastAPI, you use Pydantic models. You can declare a body parameter as part of the function parameters, and FastAPI will recognize it and expect a JSON body with the attrib
- **q004** (1.00): How does FastAPI's dependency injection system work at a basic level?
  > FastAPI's dependency injection system works by allowing you to declare dependencies as functions that can take the same parameters as your path operation functions. These dependencies can then be used
- **q005** (1.00): How do you add authentication with OAuth2 and a bearer token in FastAPI?
  > To add authentication with OAuth2 and a bearer token in FastAPI, you would use the `OAuth2PasswordBearer` class. You create an instance of it by passing the `tokenUrl` parameter, which is the URL the 
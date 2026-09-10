# Answer eval report (v1_local_qwen)

- date: 2026-09-10T17:14:55.744892+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- top_k: 5
- questions: 5
- judge skipped: False

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Hallucinated |
|---|---|---|---|
| 0.80 | 4.20 | 4.60 | 0/5 |

## Worst questions (lowest keyword coverage)

- **q004** (0.00): How does FastAPI's dependency injection system work at a basic level?
  > FastAPI's dependency injection system works by allowing you to declare dependencies as functions that can take the same parameters as your path operation functions. These dependencies can then be inje
- **q001** (1.00): How do you declare a path parameter with a type hint in FastAPI?
  > You can declare the type of a path parameter in the function, using standard Python type annotations, as shown in this example:

```python
from fastapi import Path

async def read_item(item_id: int):

- **q002** (1.00): How do you mark a query parameter as optional in FastAPI?
  > You can mark a query parameter as optional by setting its default value to `None`.
- **q003** (1.00): How do you declare a request body in FastAPI?
  > To declare a request body in FastAPI, you use Pydantic models. Your API almost always has to send a response body, but clients don't necessarily need to send request bodies all the time. To declare a 
- **q005** (1.00): How do you add authentication with OAuth2 and a bearer token in FastAPI?
  > To add authentication with OAuth2 and a bearer token in FastAPI, you would use the `OAuth2PasswordBearer` class. You create an instance of it, passing the `tokenUrl` parameter which is the URL where t
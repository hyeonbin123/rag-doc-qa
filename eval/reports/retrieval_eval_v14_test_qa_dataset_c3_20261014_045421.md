# Retrieval eval report (v14_test_qa_dataset_c3)

- date: 2026-10-14T04:54:12.034871+00:00
- embedding models: en BAAI/bge-small-en-v1.5, ko ibm-granite/granite-embedding-311m-multilingual-r2
- database: ragdb
- top_k: 10
- retrieval mode: dense
- search: as planned; dense plan: en Sort > Seq Scan on chunks c > Seq Scan on documents d
- score floor: en 0.3
- stored vectors checked: en chunks vs BAAI/bge-small-en-v1.5 (min cosine 1.0)
- dataset: qa_dataset.jsonl
- questions: 30
- hit: a chunk of an expected page, in any translation
- short: questions with fewer than 5 results (the score floor cut the rest)
- latency: retrieval only (after the query embedding), this machine's CPU

## Aggregate metrics

| set | questions | Hit@3 | Hit@5 | Hit@10 | MRR | short | latency p50 (ms) | latency p95 (ms) |
|---|---|---|---|---|---|---|---|---|
| all | 30 | 0.97 | 0.97 | 0.97 | 0.933 | 0 | 9 | 25 |

## Per-question

| id | hit@3 | hit@5 | hit@10 | RR | results | ms | question |
|---|---|---|---|---|---|---|---|
| q001 | True | True | True | 1.00 | 10 | 44 | How do you declare a path parameter with a type hint in FastAPI? |
| q002 | True | True | True | 1.00 | 10 | 10 | How do you mark a query parameter as optional in FastAPI? |
| q003 | True | True | True | 0.50 | 10 | 9 | How do you declare a request body in FastAPI? |
| q004 | True | True | True | 1.00 | 10 | 9 | How does FastAPI's dependency injection system work at a basic level? |
| q005 | True | True | True | 1.00 | 10 | 9 | How do you add authentication with OAuth2 and a bearer token in FastAPI? |
| q006 | True | True | True | 1.00 | 10 | 9 | How do you run work after returning a response to the client in FastAPI? |
| q007 | True | True | True | 1.00 | 10 | 9 | What three things make up an 'origin' in the context of CORS? |
| q008 | True | True | True | 1.00 | 10 | 10 | Which HTTP status code range is used to report errors caused by the client? |
| q009 | True | True | True | 1.00 | 10 | 9 | How do you declare a header parameter in a FastAPI path operation? |
| q010 | True | True | True | 1.00 | 10 | 8 | How do you add middleware to a FastAPI application? |
| q011 | True | True | True | 1.00 | 10 | 8 | How do you run cleanup code after a dependency has finished being used? |
| q012 | True | True | True | 1.00 | 10 | 9 | Can you use a Python class as a dependency in FastAPI, and why would you? |
| q013 | True | True | True | 1.00 | 10 | 9 | Why would you define separate input and output models for a user? |
| q014 | True | True | True | 1.00 | 10 | 9 | How do you set the title of your API shown in the automatic documentation? |
| q015 | True | True | True | 1.00 | 10 | 9 | How do you receive an uploaded file in a FastAPI endpoint? |
| q016 | True | True | True | 1.00 | 10 | 9 | How do you run code once before the application starts receiving requests? |
| q017 | False | False | False | 0.00 | 10 | 9 | How should secrets like database credentials be provided to a FastAPI application? |
| q018 | True | True | True | 1.00 | 10 | 9 | What package do you need to install to use WebSockets with FastAPI? |
| q019 | True | True | True | 1.00 | 10 | 10 | Why would you run FastAPI behind a proxy like Nginx or Traefik? |
| q020 | True | True | True | 1.00 | 10 | 8 | What status code and header does an app return when HTTP Basic Auth credentials are missing? |
| q021 | True | True | True | 1.00 | 10 | 8 | How do you replace a dependency with a different one during tests? |
| q022 | True | True | True | 1.00 | 10 | 9 | What is the common approach for deploying FastAPI applications in production with containers? |
| q023 | True | True | True | 0.50 | 10 | 9 | How do you run multiple worker processes for a FastAPI application? |
| q024 | True | True | True | 1.00 | 10 | 9 | What does a server need in order to serve traffic over HTTPS? |
| q025 | True | True | True | 1.00 | 10 | 9 | Why is FastAPI still versioned as 0.x.x? |
| q026 | True | True | True | 1.00 | 10 | 9 | Which library do the FastAPI docs use for the SQL database tutorial? |
| q027 | True | True | True | 1.00 | 10 | 9 | What do you use to write automated tests for a FastAPI application? |
| q028 | True | True | True | 1.00 | 10 | 9 | How do you require a path parameter to be greater than or equal to a given number? |
| q029 | True | True | True | 1.00 | 10 | 9 | How do you enforce a maximum length on a query parameter? |
| q030 | True | True | True | 1.00 | 10 | 9 | How do you split a large FastAPI application across multiple files? |
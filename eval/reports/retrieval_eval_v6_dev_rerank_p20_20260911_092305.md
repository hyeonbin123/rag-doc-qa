# Retrieval eval report (v6_dev_rerank_p20)

- date: 2026-09-11T09:23:05.693219+00:00
- embedding model: BAAI/bge-small-en-v1.5
- top_k: 10
- retrieval mode: rerank
- reranker: cross-encoder/ms-marco-MiniLM-L-6-v2, top 20 of each of dense and BM25
- dataset: qa_dev.jsonl
- questions: 32
- latency: retrieval only (after the query embedding), this machine's CPU

## Aggregate metrics

| Hit@3 | Hit@5 | Hit@10 | MRR | latency p50 (ms) | latency p95 (ms) |
|---|---|---|---|---|---|
| 0.97 | 1.00 | 1.00 | 0.945 | 2700 | 3480 |

## Per-question

| id | hit@3 | hit@5 | hit@10 | RR | ms | question |
|---|---|---|---|---|---|---|
| d001 | True | True | True | 1.00 | 2703 | How do you read a cookie value sent by the client in a path operation? |
| d002 | True | True | True | 1.00 | 2584 | How do you set a cookie on the response FastAPI sends back? |
| d003 | True | True | True | 1.00 | 2277 | How do you add a custom header to a response without returning a Response object yourself? |
| d004 | False | True | True | 0.25 | 2878 | How do you declare the type of data a path operation returns so FastAPI validates and filters it? |
| d005 | True | True | True | 1.00 | 2798 | What values can the status_code parameter of a path operation decorator take? |
| d006 | True | True | True | 1.00 | 2616 | How do you receive form fields instead of JSON in a request? |
| d007 | True | True | True | 0.50 | 2615 | How do you serve files like images and CSS from a directory? |
| d008 | True | True | True | 0.50 | 3152 | How do you update only the fields the client actually sent, leaving the rest of the stored item unchanged? |
| d009 | True | True | True | 1.00 | 2664 | How do you declare a body field that is a list, or another Pydantic model nested inside the body? |
| d010 | True | True | True | 1.00 | 2691 | What does use_cache=False do when declaring a dependency? |
| d011 | True | True | True | 1.00 | 2389 | How do you apply a dependency to every path operation in the whole application? |
| d012 | True | True | True | 1.00 | 2517 | How do you get the object for the currently logged-in user inside a path operation? |
| d013 | True | True | True | 1.00 | 2942 | What does the deprecated parameter of a path operation decorator do? |
| d014 | True | True | True | 1.00 | 2722 | What is jsonable_encoder used for? |
| d015 | True | True | True | 1.00 | 3483 | How can you run your app under the debugger of an editor like VS Code or PyCharm? |
| d016 | True | True | True | 1.00 | 2698 | How do you show example request data in the interactive API docs? |
| d017 | True | True | True | 1.00 | 2761 | How do you give clients fine-grained permissions, like only reading items, following the OAuth2 standard? |
| d018 | True | True | True | 1.00 | 2888 | How do you return an HTML page instead of JSON from a path operation? |
| d019 | True | True | True | 1.00 | 3479 | How can one path operation return 200 when it updates an item but 201 when it creates a new one? |
| d020 | True | True | True | 1.00 | 3022 | How do you add a completely independent FastAPI app, with its own docs, under a path of the main app? |
| d021 | True | True | True | 1.00 | 2979 | How do you render a Jinja2 template from a path operation? |
| d022 | True | True | True | 1.00 | 3350 | What is WSGIMiddleware used for? |
| d023 | True | True | True | 1.00 | 2560 | How do you write async test functions, for example to check an async database from inside the test? |
| d024 | True | True | True | 1.00 | 2918 | What is an env var and where does it live? |
| d025 | True | True | True | 1.00 | 3476 | Why should each Python project keep its own isolated set of installed packages? |
| d026 | True | True | True | 1.00 | 2722 | What should you think about when deploying an API, such as restarts, replication and memory? |
| d027 | True | True | True | 1.00 | 2284 | Which command should you use to serve a FastAPI application in production? |
| d028 | True | True | True | 1.00 | 2517 | What does the fastapi dev command do? |
| d029 | True | True | True | 1.00 | 2459 | How can you turn off the OpenAPI schema and docs in production using settings? |
| d030 | True | True | True | 1.00 | 2580 | Can you use GraphQL with FastAPI, and which libraries work with it? |
| d031 | True | True | True | 1.00 | 2395 | How can your API document that it will send requests to your users' systems when some event happens? |
| d032 | True | True | True | 1.00 | 2593 | How do you generate a TypeScript client for a FastAPI backend? |
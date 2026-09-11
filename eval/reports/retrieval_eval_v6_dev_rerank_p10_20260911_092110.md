# Retrieval eval report (v6_dev_rerank_p10)

- date: 2026-09-11T09:21:10.211879+00:00
- embedding model: BAAI/bge-small-en-v1.5
- top_k: 10
- retrieval mode: rerank
- reranker: cross-encoder/ms-marco-MiniLM-L-6-v2, top 10 of each of dense and BM25
- dataset: qa_dev.jsonl
- questions: 32
- latency: retrieval only (after the query embedding), this machine's CPU

## Aggregate metrics

| Hit@3 | Hit@5 | Hit@10 | MRR | latency p50 (ms) | latency p95 (ms) |
|---|---|---|---|---|---|
| 1.00 | 1.00 | 1.00 | 0.953 | 1383 | 1786 |

## Per-question

| id | hit@3 | hit@5 | hit@10 | RR | ms | question |
|---|---|---|---|---|---|---|
| d001 | True | True | True | 1.00 | 1565 | How do you read a cookie value sent by the client in a path operation? |
| d002 | True | True | True | 1.00 | 1171 | How do you set a cookie on the response FastAPI sends back? |
| d003 | True | True | True | 1.00 | 1048 | How do you add a custom header to a response without returning a Response object yourself? |
| d004 | True | True | True | 0.50 | 1530 | How do you declare the type of data a path operation returns so FastAPI validates and filters it? |
| d005 | True | True | True | 1.00 | 1331 | What values can the status_code parameter of a path operation decorator take? |
| d006 | True | True | True | 1.00 | 1297 | How do you receive form fields instead of JSON in a request? |
| d007 | True | True | True | 0.50 | 1436 | How do you serve files like images and CSS from a directory? |
| d008 | True | True | True | 0.50 | 1407 | How do you update only the fields the client actually sent, leaving the rest of the stored item unchanged? |
| d009 | True | True | True | 1.00 | 1259 | How do you declare a body field that is a list, or another Pydantic model nested inside the body? |
| d010 | True | True | True | 1.00 | 1435 | What does use_cache=False do when declaring a dependency? |
| d011 | True | True | True | 1.00 | 1164 | How do you apply a dependency to every path operation in the whole application? |
| d012 | True | True | True | 1.00 | 1274 | How do you get the object for the currently logged-in user inside a path operation? |
| d013 | True | True | True | 1.00 | 1398 | What does the deprecated parameter of a path operation decorator do? |
| d014 | True | True | True | 1.00 | 1331 | What is jsonable_encoder used for? |
| d015 | True | True | True | 1.00 | 1388 | How can you run your app under the debugger of an editor like VS Code or PyCharm? |
| d016 | True | True | True | 1.00 | 1445 | How do you show example request data in the interactive API docs? |
| d017 | True | True | True | 1.00 | 1264 | How do you give clients fine-grained permissions, like only reading items, following the OAuth2 standard? |
| d018 | True | True | True | 1.00 | 1292 | How do you return an HTML page instead of JSON from a path operation? |
| d019 | True | True | True | 1.00 | 2079 | How can one path operation return 200 when it updates an item but 201 when it creates a new one? |
| d020 | True | True | True | 1.00 | 1563 | How do you add a completely independent FastAPI app, with its own docs, under a path of the main app? |
| d021 | True | True | True | 1.00 | 1463 | How do you render a Jinja2 template from a path operation? |
| d022 | True | True | True | 1.00 | 1613 | What is WSGIMiddleware used for? |
| d023 | True | True | True | 1.00 | 1357 | How do you write async test functions, for example to check an async database from inside the test? |
| d024 | True | True | True | 1.00 | 1413 | What is an env var and where does it live? |
| d025 | True | True | True | 1.00 | 1629 | Why should each Python project keep its own isolated set of installed packages? |
| d026 | True | True | True | 1.00 | 1111 | What should you think about when deploying an API, such as restarts, replication and memory? |
| d027 | True | True | True | 1.00 | 1145 | Which command should you use to serve a FastAPI application in production? |
| d028 | True | True | True | 1.00 | 1378 | What does the fastapi dev command do? |
| d029 | True | True | True | 1.00 | 1491 | How can you turn off the OpenAPI schema and docs in production using settings? |
| d030 | True | True | True | 1.00 | 1445 | Can you use GraphQL with FastAPI, and which libraries work with it? |
| d031 | True | True | True | 1.00 | 1225 | How can your API document that it will send requests to your users' systems when some event happens? |
| d032 | True | True | True | 1.00 | 1069 | How do you generate a TypeScript client for a FastAPI backend? |
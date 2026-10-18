# Retrieval eval report (v15_i4_ret_qa_pool4_dev_en)

- date: 2026-10-18T12:36:29.781767+00:00
- embedding models: en BAAI/bge-small-en-v1.5, ko ibm-granite/granite-embedding-311m-multilingual-r2
- database: ragdb
- top_k: 10
- retrieval mode: dense
- search: as planned; dense plan: en Sort > Seq Scan on chunks c > Seq Scan on documents d
- score floor: en 0.0
- stored vectors checked: en chunks vs BAAI/bge-small-en-v1.5 (min cosine 1.0)
- dataset: qa_pool4_dev_en.jsonl
- questions: 40
- hit: a chunk of an expected page, in any translation
- short: questions with fewer than 5 results (the score floor cut the rest)
- latency: retrieval only (after the query embedding), this machine's CPU

## Aggregate metrics

| set | questions | Hit@3 | Hit@5 | Hit@10 | MRR | short | latency p50 (ms) | latency p95 (ms) |
|---|---|---|---|---|---|---|---|---|
| all | 40 | 0.82 | 0.85 | 0.95 | 0.774 | 0 | 8 | 9 |

## Per-question

| id | hit@3 | hit@5 | hit@10 | RR | results | ms | question |
|---|---|---|---|---|---|---|---|
| e4001 | True | True | True | 1.00 | 10 | 11 | Can you explain concurrency vs parallelism and how it relates to choosing async def in FastAPI? |
| e4002 | False | False | True | 0.12 | 10 | 9 | Why does /items/{item_id} catch requests meant for /items/latest, and how should I order my routes? |
| e4006 | False | True | True | 0.25 | 10 | 8 | How do I keep internal fields like hashed_password out of my API responses? |
| e4009 | True | True | True | 1.00 | 10 | 9 | I get an error saying Form data requires "python-multipart" to be installed. What do I need to do? |
| e4011 | True | True | True | 1.00 | 10 | 9 | I want the body to look like {"item": {...}, "user": {...}, "importance": 5}. How do I declare that? |
| e4012 | True | True | True | 1.00 | 10 | 8 | My server has no internet access, so Swagger UI loads blank. How do I serve its JS and CSS from my own app? |
| e4015 | True | True | True | 1.00 | 10 | 8 | How do I stream a large video file from disk without reading it all into memory? |
| e4018 | True | True | True | 0.50 | 10 | 8 | I return a RedirectResponse in one branch and a dict in another, and startup fails with "Invalid args for response field!". How do I fix the annotation? |
| e4024 | True | True | True | 1.00 | 10 | 8 | How do I return a 404 with a custom message when a record isn't found? |
| e4027 | True | True | True | 0.33 | 10 | 8 | How do I avoid repeating Annotated[User, Depends(get_current_user)] in dozens of endpoints? |
| e4028 | True | True | True | 1.00 | 10 | 8 | How can I capture something like /files/home/johndoe/myfile.txt as one path parameter, slashes included? |
| e4029 | True | True | True | 1.00 | 10 | 8 | How do I document an OpenAPI callback that my API will send to the client's URL after an invoice is paid? |
| e4030 | True | True | True | 1.00 | 10 | 9 | When should I use File() with bytes versus UploadFile, and when does UploadFile spool to disk? |
| e4035 | True | True | True | 1.00 | 10 | 9 | How do I write a custom APIRoute class that logs the request body when an exception occurs? |
| e4036 | True | True | True | 1.00 | 10 | 8 | What's the difference between response_model_exclude_unset, response_model_exclude_defaults and response_model_exclude_none? |
| e4037 | True | True | True | 1.00 | 10 | 9 | In a typical deployment, who handles HTTPS certificates, and what is a TLS termination proxy? |
| e4041 | True | True | True | 1.00 | 10 | 8 | What's the right way to make a query parameter optional with a default of 10, like a limit for pagination? |
| e4045 | True | True | True | 1.00 | 10 | 9 | How do I decode a JWT in a dependency and return 401 when it's expired or tampered with? |
| e4050 | True | True | True | 1.00 | 10 | 8 | How do I implement a PATCH endpoint that only touches the fields the client actually sent? |
| e4052 | True | True | True | 1.00 | 10 | 9 | What does a good Dockerfile for FastAPI look like, and why copy requirements.txt before the source code? |
| e4053 | False | False | True | 0.11 | 10 | 8 | How do I make a DELETE endpoint return 204 by default? |
| e4055 | True | True | True | 1.00 | 10 | 8 | How do I declare outgoing webhooks in my OpenAPI schema with app.webhooks? |
| e4057 | True | True | True | 1.00 | 10 | 9 | How do I serve files from a static directory, and what is the name parameter in app.mount for? |
| e4059 | True | True | True | 1.00 | 10 | 9 | Why does the settings example wrap get_settings with lru_cache? |
| e4062 | True | True | True | 1.00 | 10 | 9 | How do I build username/password login that returns a bearer token using OAuth2PasswordRequestForm? |
| e4064 | False | False | False | 0.00 | 10 | 9 | How can the same endpoint return 201 when it creates a resource but 200 when it already exists? |
| e4066 | True | True | True | 1.00 | 10 | 9 | What is dependency injection in FastAPI and how is it different from just calling a helper function inside my endpoint? |
| e4069 | False | False | True | 0.12 | 10 | 8 | I want requests with unknown query parameters to fail instead of being silently ignored. How? |
| e4071 | True | True | True | 0.50 | 10 | 8 | How do I force all incoming requests to be redirected to HTTPS? |
| e4075 | True | True | True | 0.33 | 10 | 8 | How can one endpoint's response schema be either a PlaneItem or a CarItem? |
| e4089 | False | False | True | 0.17 | 10 | 9 | How do I hide an internal endpoint from the OpenAPI schema completely? |
| e4093 | True | True | True | 1.00 | 10 | 8 | How do I make a configurable dependency, like a checker instance that takes a fixed_content argument? |
| e4095 | True | True | True | 1.00 | 10 | 9 | Can I use Depends, Query or Cookie in a WebSocket endpoint, and how do I reject the connection if the token is invalid? |
| e4096 | True | True | True | 1.00 | 10 | 8 | Should I declare the return type annotation or pass response_model, and what happens if I do both? |
| e4097 | True | True | True | 1.00 | 10 | 9 | How do I set an environment variable for just one command in PowerShell versus bash? |
| e4098 | False | False | False | 0.00 | 10 | 8 | How do I gzip-compress large responses? |
| e4099 | True | True | True | 1.00 | 10 | 8 | How do I get the JSON request body parsed into a Pydantic model? |
| e4100 | True | True | True | 0.50 | 10 | 8 | How do I render a Jinja2 template and pass the request object into it? |
| e4103 | True | True | True | 1.00 | 10 | 8 | How do I write a dependency that depends on another dependency, like a query_or_cookie_extractor? |
| e4107 | True | True | True | 1.00 | 10 | 9 | How do I document extra responses in OpenAPI, like a 404 with a Message model and a 200 that returns image/png? |
# Retrieval eval report (v16a_dev_en_c6_planned)

- date: 2026-11-02T22:51:20.365479+00:00
- embedding models: en BAAI/bge-small-en-v1.5, ko ibm-granite/granite-embedding-311m-multilingual-r2
- database: ragdb_v16a
- corpus: source commit 50113da (277 documents); last fetched 2026-11-02T22:42:36.604069+00:00; chunks en 914, ko 621
- top_k: 10
- retrieval mode: dense
- search: as planned; dense plan: en Index Scan using chunks_embedding_en_hnsw_idx on chunks c > Index Scan using documents_pkey on documents d
- score floor: en 0.3
- stored vectors checked: en chunks vs BAAI/bge-small-en-v1.5 (min cosine 1.0)
- dataset: qa_dev.jsonl, qa_pool4_dev_en.jsonl
- questions: 72
- hit: a chunk of an expected page, in any translation
- short: questions with fewer than 5 results (the score floor cut the rest)
- latency: retrieval only (after the query embedding), this machine's CPU

## Aggregate metrics

| set | questions | Hit@3 | Hit@5 | Hit@10 | MRR | short | latency p50 (ms) | latency p95 (ms) |
|---|---|---|---|---|---|---|---|---|
| all | 72 | 0.86 | 0.88 | 0.96 | 0.819 | 0 | 3 | 4 |
| qa_dev.jsonl | 32 | 0.88 | 0.91 | 0.97 | 0.859 | 0 | 3 | 4 |
| qa_pool4_dev_en.jsonl | 40 | 0.85 | 0.85 | 0.95 | 0.788 | 0 | 3 | 4 |

## Per-question

| id | hit@3 | hit@5 | hit@10 | RR | results | ms | question |
|---|---|---|---|---|---|---|---|
| d001 | True | True | True | 1.00 | 10 | 5 | How do you read a cookie value sent by the client in a path operation? |
| d002 | True | True | True | 1.00 | 10 | 4 | How do you set a cookie on the response FastAPI sends back? |
| d003 | True | True | True | 1.00 | 10 | 3 | How do you add a custom header to a response without returning a Response object yourself? |
| d004 | False | False | True | 0.11 | 10 | 3 | How do you declare the type of data a path operation returns so FastAPI validates and filters it? |
| d005 | True | True | True | 1.00 | 10 | 3 | What values can the status_code parameter of a path operation decorator take? |
| d006 | True | True | True | 1.00 | 10 | 3 | How do you receive form fields instead of JSON in a request? |
| d007 | True | True | True | 0.50 | 10 | 4 | How do you serve files like images and CSS from a directory? |
| d008 | True | True | True | 1.00 | 10 | 3 | How do you update only the fields the client actually sent, leaving the rest of the stored item unchanged? |
| d009 | True | True | True | 1.00 | 10 | 3 | How do you declare a body field that is a list, or another Pydantic model nested inside the body? |
| d010 | True | True | True | 1.00 | 10 | 4 | What does use_cache=False do when declaring a dependency? |
| d011 | True | True | True | 1.00 | 10 | 3 | How do you apply a dependency to every path operation in the whole application? |
| d012 | True | True | True | 1.00 | 10 | 3 | How do you get the object for the currently logged-in user inside a path operation? |
| d013 | False | True | True | 0.25 | 10 | 4 | What does the deprecated parameter of a path operation decorator do? |
| d014 | True | True | True | 1.00 | 10 | 3 | What is jsonable_encoder used for? |
| d015 | True | True | True | 1.00 | 10 | 4 | How can you run your app under the debugger of an editor like VS Code or PyCharm? |
| d016 | True | True | True | 1.00 | 10 | 3 | How do you show example request data in the interactive API docs? |
| d017 | True | True | True | 1.00 | 10 | 3 | How do you give clients fine-grained permissions, like only reading items, following the OAuth2 standard? |
| d018 | True | True | True | 1.00 | 10 | 3 | How do you return an HTML page instead of JSON from a path operation? |
| d019 | False | False | False | 0.00 | 10 | 3 | How can one path operation return 200 when it updates an item but 201 when it creates a new one? |
| d020 | True | True | True | 1.00 | 10 | 3 | How do you add a completely independent FastAPI app, with its own docs, under a path of the main app? |
| d021 | True | True | True | 0.50 | 10 | 4 | How do you render a Jinja2 template from a path operation? |
| d022 | True | True | True | 1.00 | 10 | 4 | What is WSGIMiddleware used for? |
| d023 | True | True | True | 1.00 | 10 | 4 | How do you write async test functions, for example to check an async database from inside the test? |
| d024 | True | True | True | 1.00 | 10 | 4 | What is an env var and where does it live? |
| d025 | False | False | True | 0.11 | 10 | 3 | Why should each Python project keep its own isolated set of installed packages? |
| d026 | True | True | True | 1.00 | 10 | 3 | What should you think about when deploying an API, such as restarts, replication and memory? |
| d027 | True | True | True | 1.00 | 10 | 3 | Which command should you use to serve a FastAPI application in production? |
| d028 | True | True | True | 1.00 | 10 | 3 | What does the fastapi dev command do? |
| d029 | True | True | True | 1.00 | 10 | 3 | How can you turn off the OpenAPI schema and docs in production using settings? |
| d030 | True | True | True | 1.00 | 10 | 3 | Can you use GraphQL with FastAPI, and which libraries work with it? |
| d031 | True | True | True | 1.00 | 10 | 3 | How can your API document that it will send requests to your users' systems when some event happens? |
| d032 | True | True | True | 1.00 | 10 | 3 | How do you generate a TypeScript client for a FastAPI backend? |
| e4001 | True | True | True | 1.00 | 10 | 3 | Can you explain concurrency vs parallelism and how it relates to choosing async def in FastAPI? |
| e4002 | False | False | True | 0.12 | 10 | 3 | Why does /items/{item_id} catch requests meant for /items/latest, and how should I order my routes? |
| e4006 | True | True | True | 0.33 | 10 | 3 | How do I keep internal fields like hashed_password out of my API responses? |
| e4009 | True | True | True | 1.00 | 10 | 3 | I get an error saying Form data requires "python-multipart" to be installed. What do I need to do? |
| e4011 | True | True | True | 1.00 | 10 | 3 | I want the body to look like {"item": {...}, "user": {...}, "importance": 5}. How do I declare that? |
| e4012 | True | True | True | 1.00 | 10 | 3 | My server has no internet access, so Swagger UI loads blank. How do I serve its JS and CSS from my own app? |
| e4015 | True | True | True | 1.00 | 10 | 3 | How do I stream a large video file from disk without reading it all into memory? |
| e4018 | True | True | True | 0.50 | 10 | 4 | I return a RedirectResponse in one branch and a dict in another, and startup fails with "Invalid args for response field!". How do I fix the annotation? |
| e4024 | True | True | True | 1.00 | 10 | 4 | How do I return a 404 with a custom message when a record isn't found? |
| e4027 | True | True | True | 0.33 | 10 | 3 | How do I avoid repeating Annotated[User, Depends(get_current_user)] in dozens of endpoints? |
| e4028 | True | True | True | 1.00 | 10 | 3 | How can I capture something like /files/home/johndoe/myfile.txt as one path parameter, slashes included? |
| e4029 | True | True | True | 1.00 | 10 | 3 | How do I document an OpenAPI callback that my API will send to the client's URL after an invoice is paid? |
| e4030 | True | True | True | 1.00 | 10 | 3 | When should I use File() with bytes versus UploadFile, and when does UploadFile spool to disk? |
| e4035 | True | True | True | 1.00 | 10 | 3 | How do I write a custom APIRoute class that logs the request body when an exception occurs? |
| e4036 | True | True | True | 1.00 | 10 | 3 | What's the difference between response_model_exclude_unset, response_model_exclude_defaults and response_model_exclude_none? |
| e4037 | True | True | True | 1.00 | 10 | 3 | In a typical deployment, who handles HTTPS certificates, and what is a TLS termination proxy? |
| e4041 | True | True | True | 1.00 | 10 | 3 | What's the right way to make a query parameter optional with a default of 10, like a limit for pagination? |
| e4045 | True | True | True | 1.00 | 10 | 3 | How do I decode a JWT in a dependency and return 401 when it's expired or tampered with? |
| e4050 | True | True | True | 1.00 | 10 | 3 | How do I implement a PATCH endpoint that only touches the fields the client actually sent? |
| e4052 | True | True | True | 1.00 | 10 | 3 | What does a good Dockerfile for FastAPI look like, and why copy requirements.txt before the source code? |
| e4053 | False | False | True | 0.10 | 10 | 3 | How do I make a DELETE endpoint return 204 by default? |
| e4055 | True | True | True | 1.00 | 10 | 3 | How do I declare outgoing webhooks in my OpenAPI schema with app.webhooks? |
| e4057 | True | True | True | 1.00 | 10 | 4 | How do I serve files from a static directory, and what is the name parameter in app.mount for? |
| e4059 | True | True | True | 1.00 | 10 | 3 | Why does the settings example wrap get_settings with lru_cache? |
| e4062 | True | True | True | 1.00 | 10 | 3 | How do I build username/password login that returns a bearer token using OAuth2PasswordRequestForm? |
| e4064 | False | False | False | 0.00 | 10 | 3 | How can the same endpoint return 201 when it creates a resource but 200 when it already exists? |
| e4066 | True | True | True | 1.00 | 10 | 3 | What is dependency injection in FastAPI and how is it different from just calling a helper function inside my endpoint? |
| e4069 | False | False | True | 0.12 | 10 | 3 | I want requests with unknown query parameters to fail instead of being silently ignored. How? |
| e4071 | True | True | True | 1.00 | 10 | 3 | How do I force all incoming requests to be redirected to HTTPS? |
| e4075 | True | True | True | 0.33 | 10 | 3 | How can one endpoint's response schema be either a PlaneItem or a CarItem? |
| e4089 | False | False | True | 0.17 | 10 | 3 | How do I hide an internal endpoint from the OpenAPI schema completely? |
| e4093 | True | True | True | 1.00 | 10 | 3 | How do I make a configurable dependency, like a checker instance that takes a fixed_content argument? |
| e4095 | True | True | True | 1.00 | 10 | 3 | Can I use Depends, Query or Cookie in a WebSocket endpoint, and how do I reject the connection if the token is invalid? |
| e4096 | True | True | True | 1.00 | 10 | 3 | Should I declare the return type annotation or pass response_model, and what happens if I do both? |
| e4097 | True | True | True | 1.00 | 10 | 3 | How do I set an environment variable for just one command in PowerShell versus bash? |
| e4098 | False | False | False | 0.00 | 10 | 3 | How do I gzip-compress large responses? |
| e4099 | True | True | True | 1.00 | 10 | 3 | How do I get the JSON request body parsed into a Pydantic model? |
| e4100 | True | True | True | 0.50 | 10 | 3 | How do I render a Jinja2 template and pass the request object into it? |
| e4103 | True | True | True | 1.00 | 10 | 3 | How do I write a dependency that depends on another dependency, like a query_or_cookie_extractor? |
| e4107 | True | True | True | 1.00 | 10 | 3 | How do I document extra responses in OpenAPI, like a 404 with a Message model and a 200 that returns image/png? |
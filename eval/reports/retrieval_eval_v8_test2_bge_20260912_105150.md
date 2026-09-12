# Retrieval eval report (v8_test2_bge)

- date: 2026-09-12T10:51:50.613019+00:00
- embedding model: BAAI/bge-small-en-v1.5
- database: ragdb
- top_k: 10
- retrieval mode: dense
- dataset: qa_test2.jsonl
- questions: 43
- latency: retrieval only (after the query embedding), this machine's CPU

## Aggregate metrics

| Hit@3 | Hit@5 | Hit@10 | MRR | latency p50 (ms) | latency p95 (ms) |
|---|---|---|---|---|---|
| 0.86 | 0.88 | 0.95 | 0.786 | 5 | 7 |

## Per-question

| id | hit@3 | hit@5 | hit@10 | RR | ms | question |
|---|---|---|---|---|---|---|
| t001 | False | False | True | 0.11 | 108 | My React app on localhost:3000 gets blocked when it calls my API on port 8000. How do I fix it? |
| t002 | True | True | True | 1.00 | 5 | How do I return a 404 error when the item someone asks for doesn't exist? |
| t003 | True | True | True | 1.00 | 6 | How can I load config values from a .env file? |
| t004 | True | True | True | 0.33 | 5 | How do I give a field in my request JSON a default value so clients can leave it out? |
| t005 | True | True | True | 1.00 | 7 | How do I accept several values for the same query parameter, like ?tag=a&tag=b? |
| t006 | True | True | True | 0.50 | 5 | How do I protect an endpoint so only logged-in users can call it? |
| t007 | True | True | True | 1.00 | 5 | How should I hash user passwords before saving them? |
| t008 | False | False | False | 0.00 | 6 | How can I log how long every request takes? |
| t009 | True | True | True | 1.00 | 5 | How can I stream a large file to the client instead of loading it all into memory? |
| t010 | False | False | True | 0.11 | 5 | How do I let the user download a file from an endpoint? |
| t011 | True | True | True | 1.00 | 5 | How do I redirect a request to another URL? |
| t012 | True | True | True | 1.00 | 5 | How do I add a description and a version number to my API docs? |
| t013 | True | True | True | 1.00 | 5 | How can I group my endpoints into sections in the docs page? |
| t014 | True | True | True | 0.50 | 6 | How do I get the client's IP address inside an endpoint? |
| t015 | False | True | True | 0.25 | 5 | How do I check that an email field in the request really is an email address? |
| t016 | True | True | True | 1.00 | 6 | How do I connect to a SQL database and create the tables when the app starts? |
| t017 | True | True | True | 1.00 | 6 | How do I write a test for my WebSocket endpoint? |
| t018 | True | True | True | 1.00 | 5 | How do I let users log in with a username and password and get back a token? |
| t019 | True | True | True | 1.00 | 6 | How do I make the login tokens expire after some time? |
| t020 | True | True | True | 1.00 | 5 | How do I upload several files in one request? |
| t021 | True | True | True | 1.00 | 5 | How do I receive a file and some form fields in the same request? |
| t022 | True | True | True | 1.00 | 6 | How do I make a query parameter required? |
| t023 | True | True | True | 0.50 | 5 | How do I restrict a path parameter to a fixed set of allowed values? |
| t024 | True | True | True | 1.00 | 5 | How do I leave fields that were never set out of the JSON response? |
| t025 | True | True | True | 1.00 | 6 | Should I run Gunicorn with several Uvicorn workers inside each container when I deploy to Kubernetes? |
| t026 | True | True | True | 1.00 | 6 | What's the difference between declaring my endpoint with def and with async def? |
| t027 | True | True | True | 1.00 | 6 | How do I catch my own exception type everywhere and turn it into a custom JSON error? |
| t028 | True | True | True | 1.00 | 5 | How do I change the error response FastAPI sends when the request data is invalid? |
| t029 | True | True | True | 1.00 | 6 | How do I put all the routes of one module under a prefix like /api/v1? |
| t030 | True | True | True | 0.50 | 5 | How do I push updates to the browser in real time over one open HTTP connection? |
| t031 | True | True | True | 1.00 | 5 | Can I use Python dataclasses instead of Pydantic models? |
| t032 | True | True | True | 1.00 | 5 | How do I check a string query parameter against a regular expression? |
| t033 | False | False | True | 0.17 | 7 | How do I accept a JSON body whose keys I don't know in advance? |
| t034 | True | True | True | 0.50 | 5 | How do I run a dependency for every endpoint in one router but not the whole app? |
| t035 | True | True | True | 0.33 | 5 | How do I return plain text instead of JSON? |
| t036 | True | True | True | 1.00 | 6 | My header is called X-Token. How do I read it when Python names can't contain a hyphen? |
| t037 | True | True | True | 1.00 | 5 | How do type hints like list[str] or str | None work in Python? |
| t038 | True | True | True | 1.00 | 5 | How do I add a custom logo to the generated OpenAPI docs? |
| t039 | True | True | True | 1.00 | 5 | How do I upgrade my app from Pydantic v1 to v2? |
| t040 | True | True | True | 1.00 | 5 | How do I send a custom header along with an error response? |
| t041 | True | True | True | 1.00 | 6 | How do I serve a React single-page app build from my FastAPI app? |
| t042 | True | True | True | 1.00 | 6 | How do I stream a list of JSON objects one line at a time? |
| t043 | False | False | False | 0.00 | 5 | How do I add a field that the client sends but that should never be shown in the docs? |
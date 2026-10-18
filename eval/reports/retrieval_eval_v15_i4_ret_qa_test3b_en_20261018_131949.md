# Retrieval eval report (v15_i4_ret_qa_test3b_en)

- date: 2026-10-18T13:19:40.948529+00:00
- embedding models: en BAAI/bge-small-en-v1.5, ko ibm-granite/granite-embedding-311m-multilingual-r2
- database: ragdb
- top_k: 10
- retrieval mode: dense
- search: as planned; dense plan: en Sort > Seq Scan on chunks c > Seq Scan on documents d
- score floor: en 0.0
- stored vectors checked: en chunks vs BAAI/bge-small-en-v1.5 (min cosine 1.0)
- dataset: qa_test3b_en.jsonl
- questions: 40
- hit: a chunk of an expected page, in any translation
- short: questions with fewer than 5 results (the score floor cut the rest)
- latency: retrieval only (after the query embedding), this machine's CPU

## Aggregate metrics

| set | questions | Hit@3 | Hit@5 | Hit@10 | MRR | short | latency p50 (ms) | latency p95 (ms) |
|---|---|---|---|---|---|---|---|---|
| all | 40 | 0.90 | 0.93 | 0.93 | 0.865 | 0 | 8 | 10 |

## Per-question

| id | hit@3 | hit@5 | hit@10 | RR | results | ms | question |
|---|---|---|---|---|---|---|---|
| n007 | True | True | True | 1.00 | 10 | 11 | How do I put minimum/maximum string length limits and a regex validation on a parameter with Query? |
| n008 | True | True | True | 1.00 | 10 | 8 | I want a query parameter name with a hyphen, like item-query, but that is not a valid Python variable name. Does alias solve this? |
| n010 | True | True | True | 1.00 | 10 | 9 | Can I put range validations like gt and le on a numeric path parameter with Path? |
| n013 | False | False | False | 0.00 | 10 | 8 | If one endpoint takes path parameters, query parameters and a request body together, how does FastAPI tell them apart? |
| n017 | True | True | True | 1.00 | 10 | 9 | How do I define fields that are nested Pydantic models, lists or sets? |
| n019 | True | True | True | 1.00 | 10 | 8 | If I want to leave sensitive fields like the password out of the response, how should I use response_model? |
| n020 | True | True | True | 1.00 | 10 | 8 | In what situation do you use the response_model_exclude_unset option? |
| n023 | True | True | True | 1.00 | 10 | 8 | Can I give the response model a Union type, so the endpoint returns one of several shapes? |
| n025 | True | True | True | 1.00 | 10 | 8 | Is there a package I need to install separately to receive HTML form data? And how do I declare it? |
| n027 | True | True | True | 1.00 | 10 | 8 | How do I make an endpoint that accepts several file uploads at once? |
| n028 | True | True | True | 1.00 | 10 | 8 | In a request that takes files and form fields together, can I also receive a JSON body? |
| n029 | True | True | True | 1.00 | 10 | 9 | How do I check an uploaded file's original filename and content type? |
| n030 | True | True | True | 1.00 | 10 | 9 | When reading a header value with Header, what does it mean that underscores are automatically converted to hyphens? |
| n032 | True | True | True | 1.00 | 10 | 8 | How do I set a cookie or add a custom header on the response? |
| n034 | True | True | True | 1.00 | 10 | 9 | I want to create a custom exception class and register an exception handler that handles it across the whole app. |
| n035 | True | True | True | 0.33 | 10 | 8 | Can I change the format of the 422 error response returned when request validation fails to our company's format? |
| n036 | True | True | True | 1.00 | 10 | 9 | Is there a way to override the RequestValidationError handler while still reusing FastAPI's default handler behavior? |
| n039 | True | True | True | 1.00 | 10 | 9 | How do sub-dependencies work, where a dependency itself uses another dependency? |
| n047 | True | True | True | 1.00 | 10 | 9 | I'd like to know the whole flow of implementing token-based login with OAuth2PasswordBearer. |
| n048 | True | True | True | 1.00 | 10 | 8 | Which library is good for issuing and verifying JWT tokens? |
| n050 | True | True | True | 1.00 | 10 | 9 | How do I write a function like get_current_user that provides the currently logged-in user's information as a dependency? |
| n051 | False | False | False | 0.00 | 10 | 8 | I want to block disabled accounts from using the API even if they log in. How should I structure the dependencies? |
| n054 | False | False | False | 0.00 | 10 | 8 | Is authentication with an API key sent in a header or a query parameter also supported? |
| n055 | True | True | True | 1.00 | 10 | 8 | In the token endpoint, which fields does OAuth2PasswordRequestForm accept? |
| n061 | True | True | True | 1.00 | 10 | 8 | How do I add built-in middleware like HTTPS redirect, TrustedHost or GZip? |
| n067 | True | True | True | 1.00 | 10 | 9 | How do I test async functions in pytest? Do I have to use httpx AsyncClient? |
| n077 | True | True | True | 1.00 | 10 | 8 | Can I still use @app.on_event("startup")? Is it deprecated? |
| n083 | True | True | True | 0.50 | 10 | 8 | How to render and return an HTML page with Jinja2 templates |
| n086 | True | True | True | 1.00 | 10 | 8 | Does using ORJSONResponse instead of the default JSONResponse improve performance? |
| n091 | True | True | True | 1.00 | 10 | 8 | My endpoint also responds with status codes other than the default one, but they do not show up in the OpenAPI docs. How do I document them? |
| n096 | True | True | True | 1.00 | 10 | 10 | How to read settings values from a .env file |
| n097 | True | True | True | 1.00 | 10 | 8 | Why do you wrap the settings object in lru_cache so that it is created only once? |
| n099 | False | True | True | 0.25 | 10 | 8 | How do I change the /docs and /redoc paths, or turn them off completely in production? |
| n105 | True | True | True | 0.50 | 10 | 8 | The endpoint's docstring shows up as the description in the docs. How do I set summary and description separately? |
| n106 | True | True | True | 1.00 | 10 | 8 | I want to deploy a FastAPI app with Docker. Can you show me an example Dockerfile? |
| n112 | True | True | True | 1.00 | 10 | 10 | How should I pin the FastAPI version in requirements? Is it OK to write a range? |
| n113 | True | True | True | 1.00 | 10 | 9 | How to receive the Request object directly in a path function to read the client IP or the raw body |
| n115 | True | True | True | 1.00 | 10 | 8 | I am definitely sending a JSON body, but I keep getting 422 Unprocessable Entity. What am I doing wrong? |
| n116 | True | True | True | 1.00 | 10 | 8 | Can I receive several query parameters bundled into one Pydantic model? Can I also make it reject parameters that are not defined? |
| n120 | True | True | True | 1.00 | 10 | 8 | I'd like to know how to define OpenAPI callbacks or webhooks in the docs. |
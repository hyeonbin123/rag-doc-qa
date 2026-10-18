# Retrieval eval report (v15_i4_ret_qa_pool4_na_test_en)

- date: 2026-10-18T13:18:47.791807+00:00
- embedding models: en BAAI/bge-small-en-v1.5, ko ibm-granite/granite-embedding-311m-multilingual-r2
- database: ragdb
- top_k: 10
- retrieval mode: dense
- search: as planned; dense plan: en Sort > Seq Scan on chunks c > Seq Scan on documents d
- score floor: en 0.0
- stored vectors checked: en chunks vs BAAI/bge-small-en-v1.5 (min cosine 1.0)
- dataset: qa_pool4_na_test_en.jsonl
- questions: 20
- hit: a chunk of an expected page, in any translation
- short: questions with fewer than 5 results (the score floor cut the rest)
- latency: retrieval only (after the query embedding), this machine's CPU

## Aggregate metrics

| set | questions | Hit@3 | Hit@5 | Hit@10 | MRR | short | latency p50 (ms) | latency p95 (ms) |
|---|---|---|---|---|---|---|---|---|
| all | 20 | 0.00 | 0.00 | 0.00 | 0.000 | 0 | 8 | 11 |

## Per-question

| id | hit@3 | hit@5 | hit@10 | RR | results | ms | question |
|---|---|---|---|---|---|---|---|
| e4a03 | False | False | False | 0.00 | 10 | 11 | On Azure App Service, where do I set the startup command and WEBSITES_PORT for a custom Python container? |
| e4a06 | False | False | False | 0.00 | 10 | 9 | In Tortoise ORM, how do I define a reverse ForeignKey relation and prefetch it in one query? |
| e4a09 | False | False | False | 0.00 | 10 | 8 | What Nginx proxy_read_timeout and proxy_buffering settings should I use for long-lived streaming responses? |
| e4a10 | False | False | False | 0.00 | 10 | 8 | How do I write a Caddyfile that load-balances two upstream app servers with active health checks? |
| e4a11 | False | False | False | 0.00 | 10 | 8 | In Vue 3, how do I write an Axios interceptor that refreshes an expired JWT and replays the original request? |
| e4a12 | False | False | False | 0.00 | 10 | 9 | How do I set TanStack Query's staleTime so my React app stops refetching my API every time the window regains focus? |
| e4a13 | False | False | False | 0.00 | 10 | 9 | Which Pydantic 2.x release added the experimental pipeline API, and when did it come out? |
| e4a14 | False | False | False | 0.00 | 10 | 8 | Roughly how many requests per second can a FastAPI app serve on a Raspberry Pi 5 versus an Intel NUC? |
| e4a15 | False | False | False | 0.00 | 10 | 8 | What round-trip latency should I expect calling my API hosted in AWS us-east-1 from a client in Seoul? |
| e4a16 | False | False | False | 0.00 | 10 | 8 | For a small startup, is Litestar or Sanic a safer bet than FastAPI in terms of hiring and long-term maintenance? |
| e4a19 | False | False | False | 0.00 | 10 | 8 | How do I register my API in Okta and find the issuer URL and JWKS endpoint I need to validate its tokens? |
| e4a20 | False | False | False | 0.00 | 10 | 8 | Where in the Auth0 dashboard do I set an API's audience and turn on RBAC permissions in access tokens? |
| e4a22 | False | False | False | 0.00 | 10 | 8 | On Ubuntu, how do I raise the open file descriptor limit for the service user running my app server? |
| e4a23 | False | False | False | 0.00 | 10 | 9 | How do I write Helm chart values for liveness and readiness probes on a Python web service? |
| e4a25 | False | False | False | 0.00 | 10 | 8 | How does pydantic-core compile a model schema into validators internally, and why is that faster than Pydantic v1? |
| e4a26 | False | False | False | 0.00 | 10 | 8 | What's the difference between Poetry dependency groups and PEP 735 dependency groups in pyproject.toml? |
| e4a27 | False | False | False | 0.00 | 10 | 8 | How do I configure a Cloudflare Tunnel so my local dev server is reachable from a public hostname? |
| e4a28 | False | False | False | 0.00 | 10 | 9 | How do I use Locust to simulate 1,000 concurrent users against my API and interpret its percentile charts? |
| e4a29 | False | False | False | 0.00 | 10 | 8 | How do I persist APScheduler cron jobs in a SQL job store so they survive restarts? |
| e4a30 | False | False | False | 0.00 | 10 | 8 | How do I enable mypy strict mode only for some modules in pyproject.toml so legacy code doesn't break CI? |
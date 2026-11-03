# Answer eval report (v16b_a_qa_pool5_ans_dev_ko)

- date: 2026-11-03T15:52:16.039617+00:00
- generated: 2026-11-03T15:51:42.511509+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/6)
- final answer call stopped by the output limit, done_reason=length: 0/6; reasoning output: 0/6; citation replies breaking the schema: 0/6
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- corpus: source commit 50113da (277 documents); last fetched 2026-11-03T08:04:42.172603+00:00; chunks en 914, ko 621
- dataset: qa_pool5_ans_dev_ko.jsonl
- questions: 6
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_a_qa_pool5_ans_dev_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.83 | n/a | n/a | n/a | 0/0 | 3260 | 0/6 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| k5n06 | 0.50 | None | None | None | 8283 | False | None / None | - |
| k5n14 | 1.00 | None | None | None | 3158 | False | None / None | - |
| k5n46 | 0.50 | None | None | None | 3130 | False | None / None | - |
| k5n56 | 1.00 | None | None | None | 3608 | False | None / None | - |
| k5n57 | 1.00 | None | None | None | 2921 | False | None / None | - |
| k5n60 | 1.00 | None | None | None | 3363 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **k5n06** (0.50): 하위 앱을 app.mount로 붙이고 그 앱에 lifespan을 넣었는데 실행이 안 되는 것 같아요. 마운트된 앱의 lifespan은 원래 안 도는 건가요?
  > 마운트된 하위 애플리케이션의 `lifespan`은 기본적으로 실행되지 않습니다. `FastAPI`에서 `lifespan`은 주로 최상위 애플리케이션에 적용되며, 마운트된 하위 애플리케이션에는 자동으로 적용되지 않습니다.

하위 애플리케이션의 `lifespan`을 실행하려면, 다음과 같은 방법을 사용할 수 있습니다:

1. **하위 애플리케이션에 별도의 `l
- **k5n46** (0.50): Decimal 필드가 있는 모델을 반환하면 JSON 응답에 숫자로 나가나요, 문자열로 나가나요? Pydantic v1 시절이랑 달라졌나요?
  > Pydantic v1 시절에는 Decimal 필드가 JSON 응답에 문자열로 변환되었습니다. 그러나 Pydantic v2에서는 Decimal 필드가 기본적으로 숫자로 직렬화됩니다. 이는 FastAPI의 최신 버전에서 Decimal 타입을 사용할 때 JSON 응답에 숫자가 출력된다는 것을 의미합니다.
- **k5n14** (1.00): openapi_url=None으로 꺼 두면 /docs에 접속했을 때 404가 나나요, 아니면 빈 페이지가 뜨나요?
  > `openapi_url=None`으로 설정하면 `/docs`에 접속했을 때 404 오류가 발생합니다. 이는 `openapi_url`이 설정되지 않으면 FastAPI가 OpenAPI 문서를 제공할 경로를 찾지 못해 `404 Not Found` 응답을 반환하기 때문입니다.
- **k5n56** (1.00): HTTPSRedirectMiddleware를 쓰면 ws:// 연결도 wss://로 리다이렉트되나요?
  > HTTPSRedirectMiddleware는 HTTPS 연결을 강제하는 데 사용되지만, ws:// 연결을 wss://로 리다이렉트하는 기능은 제공하지 않습니다. HTTPSRedirectMiddleware는 HTTP 요청을 HTTPS로 리다이렉트하는 데만 사용됩니다. ws://와 wss://는 WebSocket 프로토콜과 관련된 것이며, HTTPSRedire
- **k5n57** (1.00): TrustedHostMiddleware의 www_redirect 기본값은 뭔가요? 켜져 있으면 example.com 요청이 www.example.com으로 넘어가나요?
  > True입니다. `www_redirect`의 기본값은 `True`이며, 이 설정이 켜져 있으면 example.com과 같은 요청이 www.example.com으로 리디렉션됩니다.
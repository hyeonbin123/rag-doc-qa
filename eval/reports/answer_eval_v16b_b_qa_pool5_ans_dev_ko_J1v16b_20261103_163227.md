# Answer eval report (v16b_b_qa_pool5_ans_dev_ko, judge J1v16b)

- date: 2026-11-03T16:32:27.204993+00:00
- generated: 2026-11-03T15:52:30.151328+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/6)
- final answer call stopped by the output limit, done_reason=length: 0/6; reasoning output: 0/6; citation replies breaking the schema: 0/6
- judge: J1v16b, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-11-03T16:32:20.120024+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_pool5_ans_dev_ko.jsonl
- questions: 6
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_b_qa_pool5_ans_dev_ko.gen.jsonl, eval/runs/v16b_b_qa_pool5_ans_dev_ko.J1v16b.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.67 | 3.67 | 4.00 | 24 | 1/6 | 2266 | 0/6 | 0/6 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| k5n06 | 0.50 | 4 | 5 | False | 5539 | False | 2196 / 2196 | ok |
| k5n14 | 1.00 | 5 | 5 | False | 2287 | False | 2175 / 2175 | ok |
| k5n46 | 0.00 | 2 | 1 | True | 2128 | False | 1792 / 1792 | ok |
| k5n56 | 1.00 | 3 | 3 | False | 2109 | False | 1869 / 1869 | ok |
| k5n57 | 1.00 | 4 | 5 | False | 2245 | False | 2039 / 2039 | ok |
| k5n60 | 0.50 | 4 | 5 | False | 2708 | False | 1764 / 1764 | ok |

## Worst questions (lowest keyword coverage)

- **k5n46** (0.00): Decimal 필드가 있는 모델을 반환하면 JSON 응답에 숫자로 나가나요, 문자열로 나가나요? Pydantic v1 시절이랑 달라졌나요?
  > I don't know: the provided documentation passages do not cover this question.
- **k5n06** (0.50): 하위 앱을 app.mount로 붙이고 그 앱에 lifespan을 넣었는데 실행이 안 되는 것 같아요. 마운트된 앱의 lifespan은 원래 안 도는 건가요?
  > 마운트된 하위 애플리케이션의 `lifespan`은 기본적으로 실행되지 않습니다. `FastAPI`에서 `lifespan`은 주로 메인 애플리케이션에 대해 정의되며, 마운트된 하위 애플리케이션에는 자동으로 적용되지 않습니다.

하위 애플리케이션의 `lifespan`을 실행하려면, 해당 하위 애플리케이션 자체에서 `lifespan`을 명시적으로 정의해야 합니다
- **k5n60** (0.50): Content-Type 헤더 없이 JSON 본문을 POST했더니 422에 `{"type": "missing", "loc": ["body"]}`가 나옵니다. 이 경우 FastAPI는 본문을 JSON으로 파싱해 보기라도 하나요?
  > 아니요, FastAPI는 `Content-Type` 헤더가 없는 경우 JSON 본문을 파싱하려고 시도하지 않습니다. 이 경우 422 상태 코드와 함께 `{"type": "missing", "loc": ["body"]}` 오류가 반환됩니다. 이는 FastAPI가 JSON 파싱을 위해 `Content-Type` 헤더를 필수로 요구하기 때문입니다.
- **k5n14** (1.00): openapi_url=None으로 꺼 두면 /docs에 접속했을 때 404가 나나요, 아니면 빈 페이지가 뜨나요?
  > 네, `openapi_url=None`으로 설정하면 `/docs`에 접속했을 때 404 오류가 발생합니다. 이는 OpenAPI 문서가 비활성화되어 해당 경로로 접근 시 `Not Found` 응답이 반환되기 때문입니다.
- **k5n56** (1.00): HTTPSRedirectMiddleware를 쓰면 ws:// 연결도 wss://로 리다이렉트되나요?
  > 죄송합니다. 제공된 문서 구절에는 HTTPSRedirectMiddleware가 ws:// 연결을 wss://로 리다이렉트하는지에 대한 정보가 없습니다.
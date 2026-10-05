# Answer eval report (v13_sel_g1_qa_dev2_ko)

- date: 2026-10-05T05:29:22.839204+00:00
- generated: 2026-10-05T05:23:39.403880+00:00
- provider: ollama
- model: qwen3.5:9b
- model digest: 6488c96fa5faab64bb65cbd30d4289e20e6130ef535a93ef9a49f42eda893ea7
- think: False, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'intfloat/multilingual-e5-small'}
- dataset: qa_dev2_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_sel_g1_qa_dev2_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.80 | n/a | n/a | n/a | 0/0 | 7687 | 0/40 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n001 | 1.00 | None | None | None | 6117 | False | None / None | - |
| n005 | 1.00 | None | None | None | 7490 | False | None / None | - |
| n006 | 1.00 | None | None | None | 8499 | False | None / None | - |
| n009 | 1.00 | None | None | None | 6215 | False | None / None | - |
| n011 | 1.00 | None | None | None | 5823 | False | None / None | - |
| n012 | 0.00 | None | None | None | 7684 | False | None / None | - |
| n015 | 1.00 | None | None | None | 8656 | False | None / None | - |
| n018 | 1.00 | None | None | None | 7680 | False | None / None | - |
| n031 | 1.00 | None | None | None | 7690 | False | None / None | - |
| n041 | 1.00 | None | None | None | 7162 | False | None / None | - |
| n044 | 0.00 | None | None | None | 11485 | False | None / None | - |
| n049 | 1.00 | None | None | None | 6743 | False | None / None | - |
| n053 | 1.00 | None | None | None | 11453 | False | None / None | - |
| n058 | 1.00 | None | None | None | 14110 | False | None / None | - |
| n059 | 0.50 | None | None | None | 6268 | False | None / None | - |
| n063 | 1.00 | None | None | None | 8714 | False | None / None | - |
| n066 | 1.00 | None | None | None | 9842 | False | None / None | - |
| n068 | 1.00 | None | None | None | 5449 | False | None / None | - |
| n069 | 0.00 | None | None | None | 8112 | False | None / None | - |
| n073 | 1.00 | None | None | None | 7165 | False | None / None | - |
| n074 | 0.50 | None | None | None | 6206 | False | None / None | - |
| n076 | 0.50 | None | None | None | 7972 | False | None / None | - |
| n080 | 1.00 | None | None | None | 8178 | False | None / None | - |
| n084 | 1.00 | None | None | None | 6425 | False | None / None | - |
| n087 | 1.00 | None | None | None | 7874 | False | None / None | - |
| n088 | 1.00 | None | None | None | 7204 | False | None / None | - |
| n089 | 0.50 | None | None | None | 7092 | False | None / None | - |
| n090 | 0.50 | None | None | None | 5034 | False | None / None | - |
| n092 | 1.00 | None | None | None | 6900 | False | None / None | - |
| n094 | 0.50 | None | None | None | 7468 | False | None / None | - |
| n098 | 1.00 | None | None | None | 13059 | False | None / None | - |
| n100 | 1.00 | None | None | None | 11755 | False | None / None | - |
| n102 | 1.00 | None | None | None | 12559 | False | None / None | - |
| n103 | 0.00 | None | None | None | 8910 | False | None / None | - |
| n107 | 1.00 | None | None | None | 3932 | False | None / None | - |
| n110 | 1.00 | None | None | None | 8807 | False | None / None | - |
| n114 | 1.00 | None | None | None | 13797 | False | None / None | - |
| n117 | 0.00 | None | None | None | 6468 | False | None / None | - |
| n118 | 1.00 | None | None | None | 8305 | False | None / None | - |
| n119 | 1.00 | None | None | None | 12600 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **n012** (0.00): Pydantic BaseModel로 POST 요청 본문 받는 가장 기본적인 예제 보여주세요.
  > 제공된 문맥에는 Pydantic 모델을 사용하여 POST 요청 본문을 받는 구체적인 코드 예제는 포함되어 있지 않습니다. 문맥은 Pydantic 모델을 사용해야 함을 설명하고, `response_model`의 우선순위, 다중 본문 매개변수 선언 방법 등을 언급하고 있으나, 실제 함수 정의나 모델 클래스를 사용한 POST 엔드포인트 생성에 대한 가장 기본적인
- **n044** (0.00): yield 의존성에서 예외가 발생하면 except로 잡을 수 있나요? 거기서 HTTPException을 다시 던져도 되나?
  > 네, `yield`를 사용하는 의존성에서 `except`를 사용하여 예외를 포착할 수 있습니다. 하지만 예외를 다시 발생시키지 않으면 (또는 새 예외를 발생시키지 않으면), FastAPI는 해당 예외가 있었다는 것을 알아차리지 못해 클라이언트는 **HTTP 500 Internal Server Error** 응답을 받지만 서버에는 로그나 표시가 남지 않습니다
- **n069** (0.00): 테스트용 DB를 운영 DB와 분리해서 쓰고 싶은데 어떻게 구성하는 게 좋을까요?
  > 제공된 문맥에는 테스트용 데이터베이스를 운영 데이터베이스와 분리하여 사용하는 구체적인 구성 방법이나 권장 사항에 대한 정보가 포함되어 있지 않습니다. 따라서 주어진 정보만으로는 답변할 수 없습니다.
- **n103** (0.00): 인터넷이 안 되는 사내망이라 Swagger UI가 CDN에서 안 불러와져요. 오프라인에서 문서 보는 방법은?
  > 인터넷 연결 없이 API 문서를 보고 상호작용하려면, 먼저 자동 문서를 비활성화한 뒤 정적 파일 (JavaScript 와 CSS) 을 앱이 직접 제공하는 방식으로 설정해야 합니다. 이를 위해 `FastAPI` 앱을 생성할 때 해당 URL 을 `None` 으로 설정하고, Swagger UI 가 **JavaScript** 파일을 가져올 수 있는 URL (`sw
- **n117** (0.00): 헤더나 쿠키도 Pydantic 모델 하나로 한꺼번에 선언할 수 있을까요?
  > 네, 가능합니다. 관련 있는 헤더 매개변수 그룹이나 쿠키들의 그룹이 있는 경우, Pydantic 모델을 생성하여 한 번에 선언할 수 있습니다. 이를 통해 여러 위치에서 모델을 재사용하고 모든 매개변수에 대한 유효성 검사 및 메타데이터를 한 번에 선언할 수 있습니다.
# Answer eval report (v13_sel_g1_qa_dev2_ko.raw, judge J1)

- date: 2026-10-05T06:31:16.013655+00:00
- generated: 2026-10-05T05:23:39.403880+00:00
- provider: ollama
- model: qwen3.5:9b
- model digest: 6488c96fa5faab64bb65cbd30d4289e20e6130ef535a93ef9a49f42eda893ea7
- think: False, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-05T06:29:18.591380+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'intfloat/multilingual-e5-small'}
- dataset: qa_dev2_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_sel_g1_qa_dev2_ko.gen.jsonl, eval/runs/v13_sel_g1_qa_dev2_ko.raw.J1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.80 | 4.05 | 4.22 | 169 | 2/40 | 7687 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n001 | 1.00 | 4 | 5 | False | 6117 | False | 1764 / 1764 | ok |
| n005 | 1.00 | 5 | 5 | False | 7490 | False | 1979 / 1979 | ok |
| n006 | 1.00 | 4 | 4 | False | 8499 | False | 2014 / 2014 | ok |
| n009 | 1.00 | 2 | 1 | True | 6215 | False | 1943 / 1943 | ok |
| n011 | 1.00 | 4 | 5 | False | 5823 | False | 1913 / 1913 | ok |
| n012 | 0.00 | 3 | 3 | False | 7684 | False | 1828 / 1828 | ok |
| n015 | 1.00 | 4 | 4 | False | 8656 | False | 2048 / 2048 | ok |
| n018 | 1.00 | 4 | 4 | False | 7680 | False | 2012 / 2012 | ok |
| n031 | 1.00 | 4 | 4 | False | 7690 | False | 1804 / 1804 | ok |
| n041 | 1.00 | 4 | 4 | False | 7162 | False | 1952 / 1952 | ok |
| n044 | 0.00 | 4 | 4 | False | 11485 | False | 2282 / 2282 | ok |
| n049 | 1.00 | 4 | 5 | False | 6743 | False | 1982 / 1982 | ok |
| n053 | 1.00 | 4 | 5 | False | 11453 | False | 2300 / 2300 | ok |
| n058 | 1.00 | 5 | 5 | False | 14110 | False | 2187 / 2187 | ok |
| n059 | 0.50 | 4 | 5 | False | 6268 | False | 1954 / 1954 | ok |
| n063 | 1.00 | 5 | 5 | False | 8714 | False | 2057 / 2057 | ok |
| n066 | 1.00 | 4 | 4 | False | 9842 | False | 2159 / 2159 | ok |
| n068 | 1.00 | 4 | 5 | False | 5449 | False | 1681 / 1681 | ok |
| n069 | 0.00 | 3 | 3 | False | 8112 | False | 1912 / 1912 | ok |
| n073 | 1.00 | 4 | 5 | False | 7165 | False | 2050 / 2050 | ok |
| n074 | 0.50 | 5 | 5 | False | 6206 | False | 1808 / 1808 | ok |
| n076 | 0.50 | 4 | 4 | False | 7972 | False | 2005 / 2005 | ok |
| n080 | 1.00 | 3 | 3 | False | 8178 | False | 1822 / 1822 | ok |
| n084 | 1.00 | 4 | 5 | False | 6425 | False | 1992 / 1992 | ok |
| n087 | 1.00 | 3 | 2 | True | 7874 | False | 1916 / 1916 | ok |
| n088 | 1.00 | 4 | 4 | False | 7204 | False | 2183 / 2183 | ok |
| n089 | 0.50 | 5 | 5 | False | 7092 | False | 2107 / 2107 | ok |
| n090 | 0.50 | 3 | 3 | False | 5034 | False | 1464 / 1464 | ok |
| n092 | 1.00 | 4 | 4 | False | 6900 | False | 1743 / 1743 | ok |
| n094 | 0.50 | 5 | 5 | False | 7468 | False | 2068 / 2068 | ok |
| n098 | 1.00 | 4 | 4 | False | 13059 | False | 2135 / 2135 | ok |
| n100 | 1.00 | 4 | 4 | False | 11755 | False | 2315 / 2315 | ok |
| n102 | 1.00 | 5 | 5 | False | 12559 | False | 2327 / 2327 | ok |
| n103 | 0.00 | 4 | 4 | False | 8910 | False | 2041 / 2041 | ok |
| n107 | 1.00 | 4 | 4 | False | 3932 | False | 543 / 543 | ok |
| n110 | 1.00 | 4 | 4 | False | 8807 | False | 2087 / 2087 | ok |
| n114 | 1.00 | 5 | 5 | False | 13797 | False | 2046 / 2046 | ok |
| n117 | 0.00 | 4 | 4 | False | 6468 | False | 1843 / 1843 | ok |
| n118 | 1.00 | 5 | 5 | False | 8305 | False | 2073 / 2073 | ok |
| n119 | 1.00 | 4 | 5 | False | 12600 | False | 2565 / 2565 | ok |

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
# Answer eval report (v13_adopt_g0_qa_test2_ko)

- date: 2026-10-08T13:45:30.754236+00:00
- generated: 2026-10-08T13:41:22.785585+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- model digest: 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e
- think: None, language guard: on (regenerated 3/43)
- final answer call stopped by the output limit, done_reason=length: 0/43; reasoning output: 0/43; citation replies breaking the schema: 0/43
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'intfloat/multilingual-e5-small'}
- dataset: qa_test2_ko.jsonl
- questions: 43
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_adopt_g0_qa_test2_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.73 | n/a | n/a | n/a | 0/0 | 5352 | 1/43 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| k001 | 1.00 | None | None | None | 5803 | False | None / None | - |
| k002 | 0.50 | None | None | None | 4884 | False | None / None | - |
| k003 | 1.00 | None | None | None | 4894 | False | None / None | - |
| k004 | 1.00 | None | None | None | 4375 | False | None / None | - |
| k005 | 1.00 | None | None | None | 4429 | False | None / None | - |
| k006 | 0.00 | None | None | None | 6479 | False | None / None | - |
| k007 | 1.00 | None | None | None | 5469 | False | None / None | - |
| k008 | 0.00 | None | None | None | 5008 | False | None / None | - |
| k009 | 1.00 | None | None | None | 5513 | False | None / None | - |
| k010 | 0.00 | None | None | None | 5678 | True | None / None | - |
| k011 | 0.00 | None | None | None | 7028 | False | None / None | - |
| k012 | 1.00 | None | None | None | 4835 | False | None / None | - |
| k013 | 0.00 | None | None | None | 6057 | False | None / None | - |
| k014 | 0.00 | None | None | None | 4220 | False | None / None | - |
| k015 | 0.00 | None | None | None | 5116 | False | None / None | - |
| k016 | 1.00 | None | None | None | 5996 | False | None / None | - |
| k017 | 1.00 | None | None | None | 4335 | False | None / None | - |
| k018 | 1.00 | None | None | None | 6015 | False | None / None | - |
| k019 | 1.00 | None | None | None | 4921 | False | None / None | - |
| k020 | 1.00 | None | None | None | 4406 | False | None / None | - |
| k021 | 1.00 | None | None | None | 4480 | False | None / None | - |
| k022 | 1.00 | None | None | None | 4745 | False | None / None | - |
| k023 | 1.00 | None | None | None | 4557 | False | None / None | - |
| k024 | 1.00 | None | None | None | 5086 | False | None / None | - |
| k025 | 1.00 | None | None | None | 5345 | False | None / None | - |
| k026 | 1.00 | None | None | None | 5460 | False | None / None | - |
| k027 | 1.00 | None | None | None | 5541 | False | None / None | - |
| k028 | 1.00 | None | None | None | 4867 | False | None / None | - |
| k029 | 1.00 | None | None | None | 5832 | False | None / None | - |
| k030 | 0.00 | None | None | None | 6833 | False | None / None | - |
| k031 | 1.00 | None | None | None | 10773 | False | None / None | - |
| k032 | 1.00 | None | None | None | 5734 | False | None / None | - |
| k033 | 1.00 | None | None | None | 5981 | False | None / None | - |
| k034 | 0.00 | None | None | None | 4276 | False | None / None | - |
| k035 | 1.00 | None | None | None | 4553 | False | None / None | - |
| k036 | 1.00 | None | None | None | 5279 | False | None / None | - |
| k037 | 1.00 | None | None | None | 5916 | False | None / None | - |
| k038 | 1.00 | None | None | None | 5352 | False | None / None | - |
| k039 | 0.00 | None | None | None | 6105 | False | None / None | - |
| k040 | 1.00 | None | None | None | 5971 | False | None / None | - |
| k041 | 1.00 | None | None | None | 5705 | False | None / None | - |
| k042 | 1.00 | None | None | None | 5957 | False | None / None | - |
| k043 | 0.00 | None | None | None | 3890 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **k006** (0.00): 로그인한 사용자만 호출할 수 있게 엔드포인트를 보호하려면 어떻게 하나요?
  > `get_current_active_user` 의존성을 엔드포인트에 추가하여 로그인한 사용자만 호출할 수 있게 할 수 있습니다.
- **k008** (0.00): 모든 요청이 처리되는 데 얼마나 걸리는지 기록하려면 어떻게 하나요?
  > 라우터에서의 커스텀 `APIRoute` 클래스를 사용하면 됩니다. `APIRouter`의 `route_class` 파라미터를 `TimedRoute`로 설정하면, 응답을 생성하는 데 걸린 시간이 추가 헤더로 포함되어 응답에 포함됩니다.
- **k010** (0.00): 엔드포인트에서 사용자가 파일을 다운로드하게 하려면 어떻게 하나요?
  > 我不知道。
- **k011** (0.00): 요청을 다른 URL로 리디렉션하려면 어떻게 하나요?
  > 요청을 다른 URL로 리디렉션하려면, FastAPI의 `@app.get` 등의 경로 처리 함수에서 `Response` 객체를 사용하여 리디렉션할 URL을 지정할 수 있습니다. 예를 들어:

```python
from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/items/")
def read
- **k013** (0.00): 문서 페이지에서 엔드포인트를 섹션별로 묶으려면 어떻게 하나요?
  > 문서 페이지에서 엔드포인트를 섹션별로 묶는 방법에 대한 직접적인 언급은 없습니다. 하지만 FastAPI의 경로 처리 함수를 통해 여러 엔드포인트를 관리할 수 있으며, 이는 같은 보안 시스템을 사용하여 수천 개의 엔드포인트를 가질 수 있다는 점에서 암시적으로 언급되어 있습니다. 따라서 엔드포인트를 섹션별로 묶는 것은 개발자가 직접적인 코드 구조를 통해 관리할
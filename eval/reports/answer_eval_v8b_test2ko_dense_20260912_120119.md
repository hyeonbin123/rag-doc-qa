# Answer eval report (v8b_test2ko_dense)

- date: 2026-09-12T12:01:19.154468+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- top_k: 5
- retrieval mode: dense
- dataset: qa_test2_ko.jsonl
- questions: 43
- judge skipped: False

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Hallucinated |
|---|---|---|---|
| 0.69 | 3.74 | 4.07 | 2/43 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated |
|---|---|---|---|---|
| k001 | 0.00 | 2 | 1 | False |
| k002 | 0.50 | 4 | 4 | False |
| k003 | 1.00 | 4 | 4 | False |
| k004 | 1.00 | 4 | 5 | False |
| k005 | 0.50 | 4 | 4 | False |
| k006 | 0.00 | 4 | 4 | False |
| k007 | 1.00 | 4 | 4 | False |
| k008 | 0.00 | 3 | 3 | False |
| k009 | 1.00 | 4 | 5 | False |
| k010 | 0.00 | 2 | 1 | False |
| k011 | 0.00 | 4 | 4 | False |
| k012 | 0.50 | 4 | 5 | False |
| k013 | 0.00 | 3 | 2 | False |
| k014 | 0.00 | 1 | 1 | True |
| k015 | 0.00 | 4 | 4 | False |
| k016 | 1.00 | 4 | 4 | False |
| k017 | 1.00 | 4 | 5 | False |
| k018 | 1.00 | 4 | 4 | False |
| k019 | 1.00 | 3 | 4 | False |
| k020 | 1.00 | 4 | 5 | False |
| k021 | 1.00 | 4 | 5 | False |
| k022 | 1.00 | 4 | 5 | False |
| k023 | 1.00 | 4 | 5 | False |
| k024 | 1.00 | 4 | 5 | False |
| k025 | 1.00 | 4 | 5 | False |
| k026 | 1.00 | 4 | 4 | False |
| k027 | 1.00 | 4 | 5 | False |
| k028 | 1.00 | 4 | 4 | False |
| k029 | 1.00 | 5 | 5 | False |
| k030 | 0.00 | 3 | 2 | False |
| k031 | 1.00 | 5 | 5 | False |
| k032 | 1.00 | 4 | 5 | False |
| k033 | 1.00 | 4 | 4 | False |
| k034 | 0.00 | 4 | 5 | False |
| k035 | 1.00 | 4 | 5 | False |
| k036 | 1.00 | 4 | 5 | False |
| k037 | 1.00 | 4 | 4 | False |
| k038 | 1.00 | 4 | 4 | False |
| k039 | 1.00 | 4 | 5 | False |
| k040 | 1.00 | 4 | 5 | False |
| k041 | 0.00 | 4 | 4 | False |
| k042 | 1.00 | 4 | 5 | False |
| k043 | 0.00 | 2 | 1 | True |

## Worst questions (lowest keyword coverage)

- **k001** (0.00): 로컬 3000번 포트에서 돌아가는 React 앱이 8000번 포트의 API를 호출하면 막힙니다. 어떻게 해결하나요?
  > 문제의 상황과 직접적으로 관련된 정보는 제공된 컨텍스트 내에서 찾을 수 없습니다. 컨텍스트는 FastAPI와 Uvicorn, Traefik, 프록시 설정 등과 관련된 정보를 주로 다루고 있으며, 웹 애플리케이션 간의 직접적인 통신 문제에 대한 해결 방법은 다루지 않았습니다. 따라서 이 질문에 대한 정확한 답변을 제공하는 것은 어렵습니다.
- **k006** (0.00): 로그인한 사용자만 호출할 수 있게 엔드포인트를 보호하려면 어떻게 하나요?
  > 엔드ポイント를 보호하려면 `get_current_active_user` 의존성을 추가해야 합니다. 이를 통해 엔드포인트에서는 사용자가 존재하고 올바르게 인증되었으며 활성 상태인 경우에만 사용자를 얻을 수 있습니다.
- **k008** (0.00): 모든 요청이 처리되는 데 얼마나 걸리는지 기록하려면 어떻게 하나요?
  > `APIRouter`의 `route_class` 파라米ters를 설정하여 커스텀 `APIRoute` 클래스를 사용할 수 있습니다. 이 경우, `router` 아래의 경路处理都会使用您自定义的 `TimedRoute` 类，并在响应中包含一个额外的 `X-Response-Time` 头，记录生成响应所花费的时间。
- **k010** (0.00): 엔드포인트에서 사용자가 파일을 다운로드하게 하려면 어떻게 하나요?
  > 我不知道。
- **k011** (0.00): 요청을 다른 URL로 리디렉션하려면 어떻게 하나요?
  > 요청을 다른 URL로 리디렉션하려면, FastAPI의 `@app.get` 또는 관련 경로 처리 함수에서 `Response` 객체를 사용하여 리디렉션할 URL을 지정할 수 있습니다. 예를 들어:

```python
from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/items/")
def r
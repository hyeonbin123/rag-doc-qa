# Answer eval report (v8_test2ko_dense)

- date: 2026-09-12T11:20:38.187811+00:00
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
| 0.71 | 3.77 | 4.14 | 2/43 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated |
|---|---|---|---|---|
| k001 | 0.00 | 3 | 3 | False |
| k002 | 0.50 | 4 | 4 | False |
| k003 | 1.00 | 4 | 4 | False |
| k004 | 1.00 | 5 | 5 | False |
| k005 | 1.00 | 4 | 4 | False |
| k006 | 0.00 | 4 | 4 | False |
| k007 | 0.00 | 4 | 4 | False |
| k008 | 0.00 | 3 | 3 | False |
| k009 | 1.00 | 4 | 5 | False |
| k010 | 1.00 | 3 | 3 | False |
| k011 | 0.00 | 4 | 5 | False |
| k012 | 1.00 | 4 | 5 | False |
| k013 | 0.00 | 3 | 2 | False |
| k014 | 0.00 | 2 | 1 | False |
| k015 | 0.00 | 4 | 4 | False |
| k016 | 1.00 | 4 | 4 | False |
| k017 | 1.00 | 4 | 5 | False |
| k018 | 0.00 | 4 | 4 | False |
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
| k029 | 1.00 | 4 | 5 | False |
| k030 | 0.00 | 1 | 1 | True |
| k031 | 1.00 | 5 | 5 | False |
| k032 | 1.00 | 4 | 5 | False |
| k033 | 1.00 | 4 | 4 | False |
| k034 | 0.00 | 4 | 4 | False |
| k035 | 1.00 | 4 | 5 | False |
| k036 | 1.00 | 4 | 5 | False |
| k037 | 1.00 | 4 | 4 | False |
| k038 | 1.00 | 4 | 4 | False |
| k039 | 1.00 | 4 | 5 | False |
| k040 | 1.00 | 4 | 5 | False |
| k041 | 1.00 | 4 | 4 | False |
| k042 | 1.00 | 4 | 5 | False |
| k043 | 0.00 | 2 | 1 | True |

## Worst questions (lowest keyword coverage)

- **k001** (0.00): 로컬 3000번 포트에서 돌아가는 React 앱이 8000번 포트의 API를 호출하면 막힙니다. 어떻게 해결하나요?
  > 문제를 해결하기 위해서는 프록시 설정이 필요합니다. React 앱이 8000번 포트의 API를 호출할 때, 3000번 포트에서 돌아가는 React 앱을 통해 8000번 포트의 API에 요청을 전달하도록 프록시를 설정해야 합니다. 이를 통해 React 앱이 직접 8000번 포트의 API를 호출하는 대신, 프록시를 통해 요청을 전달하여 문제를 해결할 수 있습니
- **k006** (0.00): 로그인한 사용자만 호출할 수 있게 엔드포인트를 보호하려면 어떻게 하나요?
  > 엔드ポイント를 보호하려면 `get_current_active_user` 의존성을 추가해야 합니다. 이를 통해 엔드포인트에서는 사용자가 존재하고 올바르게 인증되었으며 활성 상태인 경우에만 사용자를 얻을 수 있습니다.
- **k007** (0.00): 사용자 비밀번호를 저장하기 전에 어떻게 해시해야 하나요?
  > 사용자 비밀번호를 저장하기 전에 Argon2나 Bcrypt와 같은 알고리즘을 사용하여 해싱해야 합니다. 해싱은 비밀번호를 안전하게 저장하고, 비밀번호를 다시 복원할 수 없도록 하는 방법입니다.
- **k008** (0.00): 모든 요청이 처리되는 데 얼마나 걸리는지 기록하려면 어떻게 하나요?
  > 라우터에서의 커스텀 `APIRoute` 클래스를 사용하면 됩니다. `APIRouter`의 `route_class` 파라미터를 설정하여 커스텀 `APIRoute`를 사용할 수 있습니다. 이렇게 하면 응답을 생성하는 데 걸린 시간을 포함한 추가 `X-Response-Time` 헤더가 자동으로 응답에 추가됩니다.
- **k011** (0.00): 요청을 다른 URL로 리디렉션하려면 어떻게 하나요?
  > 요청을 다른 URL로 리디렉션하려면, FastAPI 애플리케이션에서 `@app.get` 등의 경로 처리 함수를 사용하여 리디렉션 URL을 정의할 수 있습니다. 예를 들어, `/items` 경로에서 `/items/`로 리디렉션하려면 다음과 같이 할 수 있습니다:

```python
from fastapi import FastAPI, Response

app 
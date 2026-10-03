# Answer eval report (v11_A_qa_test2_ko)

- date: 2026-10-03T22:39:53.569130+00:00
- generated: 2026-10-03T22:37:06.397965+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- dataset: qa_test2_ko.jsonl
- questions: 43
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v11_A_qa_test2_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.78 | n/a | n/a | n/a | 0/0 | 3590 | 3/43 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| k001 | 1.00 | None | None | None | 4522 | False | None / None | - |
| k002 | 1.00 | None | None | None | 4164 | False | None / None | - |
| k003 | 1.00 | None | None | None | 3719 | False | None / None | - |
| k004 | 1.00 | None | None | None | 3379 | False | None / None | - |
| k005 | 1.00 | None | None | None | 3779 | False | None / None | - |
| k006 | 0.00 | None | None | None | 3484 | True | None / None | - |
| k007 | 1.00 | None | None | None | 3801 | False | None / None | - |
| k008 | 0.00 | None | None | None | 3438 | True | None / None | - |
| k009 | 1.00 | None | None | None | 4059 | False | None / None | - |
| k010 | 0.00 | None | None | None | 2666 | True | None / None | - |
| k011 | 0.00 | None | None | None | 4835 | False | None / None | - |
| k012 | 0.50 | None | None | None | 3398 | False | None / None | - |
| k013 | 0.00 | None | None | None | 3891 | False | None / None | - |
| k014 | 1.00 | None | None | None | 3688 | False | None / None | - |
| k015 | 0.00 | None | None | None | 3354 | False | None / None | - |
| k016 | 1.00 | None | None | None | 3718 | False | None / None | - |
| k017 | 1.00 | None | None | None | 3165 | False | None / None | - |
| k018 | 1.00 | None | None | None | 4188 | False | None / None | - |
| k019 | 1.00 | None | None | None | 3329 | False | None / None | - |
| k020 | 1.00 | None | None | None | 3097 | False | None / None | - |
| k021 | 1.00 | None | None | None | 3108 | False | None / None | - |
| k022 | 1.00 | None | None | None | 3144 | False | None / None | - |
| k023 | 1.00 | None | None | None | 3115 | False | None / None | - |
| k024 | 1.00 | None | None | None | 3379 | False | None / None | - |
| k025 | 1.00 | None | None | None | 3192 | False | None / None | - |
| k026 | 1.00 | None | None | None | 3746 | False | None / None | - |
| k027 | 1.00 | None | None | None | 3982 | False | None / None | - |
| k028 | 1.00 | None | None | None | 3323 | False | None / None | - |
| k029 | 1.00 | None | None | None | 4557 | False | None / None | - |
| k030 | 0.00 | None | None | None | 3379 | False | None / None | - |
| k031 | 1.00 | None | None | None | 3940 | False | None / None | - |
| k032 | 1.00 | None | None | None | 3935 | False | None / None | - |
| k033 | 1.00 | None | None | None | 4007 | False | None / None | - |
| k034 | 0.00 | None | None | None | 2953 | False | None / None | - |
| k035 | 1.00 | None | None | None | 2999 | False | None / None | - |
| k036 | 1.00 | None | None | None | 3554 | False | None / None | - |
| k037 | 1.00 | None | None | None | 3982 | False | None / None | - |
| k038 | 1.00 | None | None | None | 3439 | False | None / None | - |
| k039 | 1.00 | None | None | None | 4410 | False | None / None | - |
| k040 | 1.00 | None | None | None | 4407 | False | None / None | - |
| k041 | 1.00 | None | None | None | 3590 | False | None / None | - |
| k042 | 1.00 | None | None | None | 4327 | False | None / None | - |
| k043 | 0.00 | None | None | None | 2908 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **k006** (0.00): 로그인한 사용자만 호출할 수 있게 엔드포인트를 보호하려면 어떻게 하나요?
  > 엔드ポイント를 보호하려면 `get_current_active_user` 의존성을 추가해야 합니다. 이를 통해 엔드포인트에서는 사용자가 존재하고 올바르게 인증되었으며 활성 상태인 경우에만 사용자를 얻을 수 있습니다.
- **k008** (0.00): 모든 요청이 처리되는 데 얼마나 걸리는지 기록하려면 어떻게 하나요?
  > `APIRouter`의 `route_class` 파라米ters를 설정하여 커스텀 `TimedRoute` 클래스를 사용할 수 있습니다. 이렇게 하면 응답을 생성하는 데 걸린 시간이 포함된 추가 `X-Response-Time` 헤더가 자동으로 추가됩니다.
- **k010** (0.00): 엔드포인트에서 사용자가 파일을 다운로드하게 하려면 어떻게 하나요?
  > 我不知道。
- **k011** (0.00): 요청을 다른 URL로 리디렉션하려면 어떻게 하나요?
  > 요청을 다른 URL로 리디렉션하려면, FastAPI의 `@app.get` 또는 관련 경로 처리 함수에서 `Response` 객체를 사용하여 리디렉션할 URL을 지정할 수 있습니다. 예를 들어, `/items` 경로에서 `/items/`로 리디렉션하려면 다음과 같이 할 수 있습니다:

```python
from fastapi import FastAPI, Re
- **k013** (0.00): 문서 페이지에서 엔드포인트를 섹션별로 묶으려면 어떻게 하나요?
  > 문서 페이지에서 엔드포인트를 섹션별로 묶는 방법에 대한 직접적인 정보는 제공된 컨텍스트에서 찾을 수 없습니다. 하지만 FastAPI의 경로 처리 함수를 통해 여러 엔드포인트를 관리하고 그룹화할 수 있다는 점은 언급되어 있습니다. 각 그룹은 독립적인 경로 처리 함수로 구현될 수 있으며, 이 함수들은 필요한 경우 공통의 의존성을 재사용할 수 있습니다.
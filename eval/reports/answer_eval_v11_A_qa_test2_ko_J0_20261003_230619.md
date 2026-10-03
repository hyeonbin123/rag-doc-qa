# Answer eval report (v11_A_qa_test2_ko, judge J0)

- date: 2026-10-03T23:06:19.120686+00:00
- generated: 2026-10-03T22:37:06.397965+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- judge: J0, qwen2.5:7b-instruct, Ollama default (num_ctx not sent, truncation on)
- judge context in use (Ollama /api/ps after judging): 4096
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-03T23:04:56.659407+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- dataset: qa_test2_ko.jsonl
- questions: 43
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v11_A_qa_test2_ko.gen.jsonl, eval/runs/v11_A_qa_test2_ko.J0.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.78 | 3.81 | 4.07 | 175 | 3/43 | 3590 | 3/43 | 0/43 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| k001 | 1.00 | 3 | 3 | False | 4522 | False | 2185 / 2185 | ok |
| k002 | 1.00 | 5 | 5 | False | 4164 | False | 2025 / 2025 | ok |
| k003 | 1.00 | 4 | 4 | False | 3719 | False | 1965 / 1965 | ok |
| k004 | 1.00 | 4 | 5 | False | 3379 | False | 1874 / 1874 | ok |
| k005 | 1.00 | 4 | 4 | False | 3779 | False | 1812 / 1812 | ok |
| k006 | 0.00 | 4 | 4 | False | 3484 | True | 1833 / 1833 | ok |
| k007 | 1.00 | 4 | 5 | False | 3801 | False | 1908 / 1908 | ok |
| k008 | 0.00 | 3 | 2 | False | 3438 | True | 1722 / 1722 | ok |
| k009 | 1.00 | 4 | 5 | False | 4059 | False | 1938 / 1938 | ok |
| k010 | 0.00 | 2 | 1 | True | 2666 | True | 1676 / 1676 | ok |
| k011 | 0.00 | 4 | 4 | False | 4835 | False | 2129 / 2129 | ok |
| k012 | 0.50 | 4 | 5 | False | 3398 | False | 1981 / 1981 | ok |
| k013 | 0.00 | 2 | 1 | False | 3891 | False | 1759 / 1759 | ok |
| k014 | 1.00 | 3 | 2 | False | 3688 | False | 1812 / 1812 | ok |
| k015 | 0.00 | 4 | 4 | False | 3354 | False | 1799 / 1799 | ok |
| k016 | 1.00 | 4 | 4 | False | 3718 | False | 1930 / 1930 | ok |
| k017 | 1.00 | 4 | 5 | False | 3165 | False | 1712 / 1712 | ok |
| k018 | 1.00 | 4 | 4 | False | 4188 | False | 1979 / 1979 | ok |
| k019 | 1.00 | 3 | 4 | False | 3329 | False | 1935 / 1935 | ok |
| k020 | 1.00 | 4 | 5 | False | 3097 | False | 1689 / 1689 | ok |
| k021 | 1.00 | 4 | 5 | False | 3108 | False | 1674 / 1674 | ok |
| k022 | 1.00 | 4 | 5 | False | 3144 | False | 1793 / 1793 | ok |
| k023 | 1.00 | 4 | 4 | False | 3115 | False | 1774 / 1774 | ok |
| k024 | 1.00 | 4 | 5 | False | 3379 | False | 1940 / 1940 | ok |
| k025 | 1.00 | 4 | 5 | False | 3192 | False | 1625 / 1625 | ok |
| k026 | 1.00 | 4 | 4 | False | 3746 | False | 1813 / 1813 | ok |
| k027 | 1.00 | 4 | 5 | False | 3982 | False | 1773 / 1773 | ok |
| k028 | 1.00 | 4 | 4 | False | 3323 | False | 1870 / 1870 | ok |
| k029 | 1.00 | 5 | 5 | False | 4557 | False | 2100 / 2100 | ok |
| k030 | 0.00 | 2 | 1 | True | 3379 | False | 1972 / 1972 | ok |
| k031 | 1.00 | 5 | 5 | False | 3940 | False | 1999 / 1999 | ok |
| k032 | 1.00 | 4 | 4 | False | 3935 | False | 1842 / 1842 | ok |
| k033 | 1.00 | 4 | 4 | False | 4007 | False | 1940 / 1940 | ok |
| k034 | 0.00 | 4 | 5 | False | 2953 | False | 1579 / 1579 | ok |
| k035 | 1.00 | 4 | 5 | False | 2999 | False | 1641 / 1641 | ok |
| k036 | 1.00 | 4 | 5 | False | 3554 | False | 1725 / 1725 | ok |
| k037 | 1.00 | 4 | 4 | False | 3982 | False | 1886 / 1886 | ok |
| k038 | 1.00 | 4 | 4 | False | 3439 | False | 1835 / 1835 | ok |
| k039 | 1.00 | 4 | 5 | False | 4410 | False | 2135 / 2135 | ok |
| k040 | 1.00 | 4 | 5 | False | 4407 | False | 2033 / 2033 | ok |
| k041 | 1.00 | 4 | 4 | False | 3590 | False | 1897 / 1897 | ok |
| k042 | 1.00 | 5 | 5 | False | 4327 | False | 1762 / 1762 | ok |
| k043 | 0.00 | 2 | 1 | True | 2908 | False | 1694 / 1694 | ok |

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
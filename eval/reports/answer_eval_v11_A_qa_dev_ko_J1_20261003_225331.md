# Answer eval report (v11_A_qa_dev_ko, judge J1)

- date: 2026-10-03T22:53:31.924241+00:00
- generated: 2026-10-03T22:31:15.550377+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- judge: J1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-03T22:52:33.435065+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- dataset: qa_dev_ko.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v11_A_qa_dev_ko.gen.jsonl, eval/runs/v11_A_qa_dev_ko.J1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.75 | 3.81 | 4.16 | 133 | 0/32 | 3400 | 2/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| kd001 | 1.00 | 4 | 5 | False | 3079 | False | 1533 / 1533 | ok |
| kd002 | 1.00 | 4 | 5 | False | 3383 | False | 1758 / 1758 | ok |
| kd003 | 0.00 | 3 | 3 | False | 3802 | False | 1888 / 1888 | ok |
| kd004 | 1.00 | 4 | 5 | False | 4460 | False | 1925 / 1925 | ok |
| kd005 | 1.00 | 4 | 4 | False | 3286 | False | 1771 / 1771 | ok |
| kd006 | 1.00 | 4 | 5 | False | 3039 | False | 1841 / 1841 | ok |
| kd007 | 0.00 | 3 | 3 | False | 3416 | False | 1791 / 1791 | ok |
| kd008 | 1.00 | 4 | 4 | False | 3295 | False | 1664 / 1664 | ok |
| kd009 | 0.00 | 4 | 4 | False | 4321 | False | 1944 / 1944 | ok |
| kd010 | 1.00 | 4 | 5 | False | 3082 | False | 1826 / 1826 | ok |
| kd011 | 1.00 | 4 | 4 | False | 3645 | False | 1782 / 1782 | ok |
| kd012 | 1.00 | 4 | 4 | False | 3015 | False | 1625 / 1625 | ok |
| kd013 | 1.00 | 2 | 2 | False | 2972 | True | 1745 / 1745 | ok |
| kd014 | 1.00 | 4 | 4 | False | 3269 | False | 1721 / 1721 | ok |
| kd015 | 0.00 | 4 | 5 | False | 4837 | False | 2033 / 2033 | ok |
| kd016 | 1.00 | 4 | 4 | False | 3624 | False | 1990 / 1990 | ok |
| kd017 | 0.00 | 3 | 3 | False | 3214 | False | 1886 / 1886 | ok |
| kd018 | 0.00 | 3 | 3 | False | 3158 | False | 1833 / 1833 | ok |
| kd019 | 0.00 | 2 | 2 | False | 3062 | True | 1640 / 1640 | ok |
| kd020 | 1.00 | 4 | 5 | False | 5525 | False | 1936 / 1936 | ok |
| kd021 | 1.00 | 4 | 4 | False | 3853 | False | 1961 / 1961 | ok |
| kd022 | 1.00 | 4 | 4 | False | 3498 | False | 2118 / 2118 | ok |
| kd023 | 0.00 | 4 | 4 | False | 3645 | False | 1932 / 1932 | ok |
| kd024 | 1.00 | 4 | 5 | False | 3233 | False | 1657 / 1657 | ok |
| kd025 | 1.00 | 4 | 5 | False | 3604 | False | 1924 / 1924 | ok |
| kd026 | 1.00 | 4 | 5 | False | 5240 | False | 2088 / 2088 | ok |
| kd027 | 1.00 | 5 | 5 | False | 2555 | False | 1265 / 1265 | ok |
| kd028 | 1.00 | 5 | 5 | False | 3769 | False | 1670 / 1670 | ok |
| kd029 | 1.00 | 4 | 4 | False | 3271 | False | 1982 / 1982 | ok |
| kd030 | 1.00 | 5 | 5 | False | 3510 | False | 1884 / 1884 | ok |
| kd031 | 1.00 | 3 | 3 | False | 3747 | False | 1823 / 1823 | ok |
| kd032 | 1.00 | 4 | 5 | False | 3253 | False | 1794 / 1794 | ok |

## Worst questions (lowest keyword coverage)

- **kd003** (0.00): Response 객체를 직접 반환하지 않고 응답에 사용자 정의 헤더를 추가하려면 어떻게 하나요?
  > 커스텀 사설 헤더는 [`X-` 접두어를 사용하여](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers) 추가할 수 있습니다. 하지만, 브라우저에서 클라이언트가 볼 수 있는 커스텀 헤더가 있는 경우, CORS 설정에 이를 추가해야 합니다. Starlette의 CORS 문서에 문서화된 `expose_heade
- **kd007** (0.00): 이미지나 CSS 같은 파일을 디렉터리에서 그대로 서빙하려면 어떻게 하나요?
  > 프로젝트 파일 구조를 다음과 같이 만들 수 있습니다:

```
.
├── app
│   ├── __init__.py
│   ├── main.py
└── static/
```
- **kd009** (0.00): 요청 본문에 리스트 필드나 다른 Pydantic 모델을 중첩해서 선언하려면 어떻게 하나요?
  > 중첩 모델을 선언하려면 서브모델을 타입으로 사용할 수 있습니다. 예를 들어, `Image` 모델을 정의할 수 있으며, 이를 다른 모델의 어트리뷰트 타입으로 사용할 수 있습니다. 이렇게 하면 FastAPI는 임의의 깊이로 중첩된 JSON "객체"를 선언하고, 중첩된 모델도 편집기 지원을 받으며, 데이터 변환과 검증을 수행하고, 자동 문서화를 제공합니다.
- **kd015** (0.00): VS Code나 PyCharm 같은 에디터의 디버거로 앱을 실행하려면 어떻게 하나요?
  > Visual Studio Code에서 다음과 같이 할 수 있습니다.

1. "Debug" 패널로 이동합니다.
2. "Add configuration..."을 선택합니다.
3. "Python"을 선택합니다.
4. "`Python: Current File (Integrated Terminal)`" 옵션을 선택합니다.
5. 그런 다음 FastAPI 코드로 서버를
- **kd017** (0.00): OAuth2 표준에 따라 클라이언트에게 항목 읽기만 허용하는 식의 세분화된 권한을 주려면 어떻게 하나요?
  > `users:read`라는 스코프를 사용하면 됩니다.
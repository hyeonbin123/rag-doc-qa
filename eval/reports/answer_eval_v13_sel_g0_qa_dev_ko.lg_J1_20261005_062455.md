# Answer eval report (v13_sel_g0_qa_dev_ko.lg, judge J1)

- date: 2026-10-05T06:24:55.576793+00:00
- generated: 2026-10-05T05:04:07.936519+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- model digest: 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e
- think: None, language guard: on (regenerated 2/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: J1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-05T06:23:59.188094+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'intfloat/multilingual-e5-small'}
- dataset: qa_dev_ko.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_sel_g0_qa_dev_ko.gen.jsonl, eval/runs/v13_sel_g0_qa_dev_ko.lg.J1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.75 | 3.94 | 4.25 | 136 | 0/32 | 5187 | 1/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| kd001 | 1.00 | 4 | 5 | False | 8181 | False | 1533 / 1533 | ok |
| kd002 | 1.00 | 4 | 5 | False | 5034 | False | 1758 / 1758 | ok |
| kd003 | 0.00 | 3 | 3 | False | 5595 | False | 1888 / 1888 | ok |
| kd004 | 0.00 | 4 | 5 | False | 5901 | False | 1895 / 1895 | ok |
| kd005 | 1.00 | 4 | 4 | False | 4656 | False | 1767 / 1767 | ok |
| kd006 | 1.00 | 4 | 5 | False | 4364 | False | 1841 / 1841 | ok |
| kd007 | 0.00 | 3 | 3 | False | 5093 | False | 1805 / 1805 | ok |
| kd008 | 1.00 | 4 | 4 | False | 5225 | False | 1687 / 1687 | ok |
| kd009 | 0.00 | 4 | 4 | False | 6324 | False | 1938 / 1938 | ok |
| kd010 | 1.00 | 4 | 5 | False | 4364 | False | 1826 / 1826 | ok |
| kd011 | 1.00 | 4 | 4 | False | 5305 | False | 1782 / 1782 | ok |
| kd012 | 1.00 | 4 | 4 | False | 4227 | False | 1625 / 1625 | ok |
| kd013 | 1.00 | 2 | 2 | False | 5664 | True | 1745 / 1745 | ok |
| kd014 | 1.00 | 4 | 5 | False | 4569 | False | 1728 / 1728 | ok |
| kd015 | 0.00 | 4 | 5 | False | 7056 | False | 2024 / 2024 | ok |
| kd016 | 1.00 | 4 | 4 | False | 4854 | False | 1976 / 1976 | ok |
| kd017 | 0.00 | 3 | 3 | False | 4619 | False | 1886 / 1886 | ok |
| kd018 | 0.00 | 3 | 3 | False | 4485 | False | 1833 / 1833 | ok |
| kd019 | 0.00 | 4 | 4 | False | 8895 | False | 1900 / 1900 | ok |
| kd020 | 1.00 | 5 | 5 | False | 7892 | False | 1936 / 1936 | ok |
| kd021 | 1.00 | 4 | 4 | False | 5489 | False | 1961 / 1961 | ok |
| kd022 | 1.00 | 4 | 4 | False | 5171 | False | 2118 / 2118 | ok |
| kd023 | 1.00 | 4 | 4 | False | 5850 | False | 1946 / 1946 | ok |
| kd024 | 1.00 | 4 | 5 | False | 4601 | False | 1657 / 1657 | ok |
| kd025 | 1.00 | 4 | 5 | False | 5295 | False | 1922 / 1922 | ok |
| kd026 | 1.00 | 4 | 5 | False | 8428 | False | 2109 / 2109 | ok |
| kd027 | 1.00 | 5 | 5 | False | 3537 | False | 1265 / 1265 | ok |
| kd028 | 1.00 | 5 | 5 | False | 5139 | False | 1661 / 1661 | ok |
| kd029 | 1.00 | 4 | 4 | False | 4682 | False | 1982 / 1982 | ok |
| kd030 | 1.00 | 5 | 5 | False | 5203 | False | 1895 / 1895 | ok |
| kd031 | 1.00 | 4 | 4 | False | 5533 | False | 1816 / 1816 | ok |
| kd032 | 1.00 | 4 | 4 | False | 4692 | False | 1794 / 1794 | ok |

## Worst questions (lowest keyword coverage)

- **kd003** (0.00): Response 객체를 직접 반환하지 않고 응답에 사용자 정의 헤더를 추가하려면 어떻게 하나요?
  > 커스텀 사설 헤더는 [`X-` 접두어를 사용하여](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers) 추가할 수 있습니다. 하지만, 브라우저에서 클라이언트가 볼 수 있는 커스텀 헤더가 있는 경우, CORS 설정에 이를 추가해야 합니다. Starlette의 CORS 문서에 문서화된 `expose_heade
- **kd004** (0.00): 경로 처리가 반환하는 데이터의 타입을 선언해서 FastAPI가 검증하고 걸러 내게 하려면 어떻게 하나요?
  > FastAPI는 경로 처리 함수의 반환 타입을 어노테이션하여 이를 선언할 수 있습니다. 이 타입은 Pydantic 모델, 리스트, 딕셔너리, 정수/불리언 등과 같은 스칼라 값을 포함할 수 있으며, FastAPI는 이를 사용하여 반환된 데이터를 검증하고, OpenAPI 경로 처리의 응답에 JSON Schema을 추가하며, 반환된 데이터를 Pydantic을 사
- **kd007** (0.00): 이미지나 CSS 같은 파일을 디렉터리에서 그대로 서빙하려면 어떻게 하나요?
  > 프로젝트 파일 구조를 다음과 같이 만들고, 필요한 정적 파일을 저장할 디렉터리를 추가합니다:

```
.
├── app
│   ├── __init__.py
│   ├── main.py
└── static/
```
- **kd009** (0.00): 요청 본문에 리스트 필드나 다른 Pydantic 모델을 중첩해서 선언하려면 어떻게 하나요?
  > 중첩 모델을 선언하려면 서브모델을 타입으로 사용할 수 있습니다. 예를 들어, `Image` 모델을 정의할 수 있으며, 이를 다른 모델의 어트리뷰트 타입으로 사용할 수 있습니다. 이렇게 하면 FastAPI는 임의의 깊이로 중첩된 JSON "객체"를 선언하고, 중첩된 모델은 편집기 지원, 데이터 변환, 검증, 자동 문서화를 제공합니다.
- **kd015** (0.00): VS Code나 PyCharm 같은 에디터의 디버거로 앱을 실행하려면 어떻게 하나요?
  > Visual Studio Code에서 다음과 같이 할 수 있습니다.

1. "Debug" 패널로 이동합니다.
2. "Add configuration..."을 선택합니다.
3. "Python"을 선택합니다.
4. "`Python: Current File (Integrated Terminal)`" 옵션을 선택합니다.
5. 그런 다음 FastAPI 코드로 서버를
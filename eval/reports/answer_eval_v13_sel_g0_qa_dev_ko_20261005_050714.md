# Answer eval report (v13_sel_g0_qa_dev_ko)

- date: 2026-10-05T05:07:14.036951+00:00
- generated: 2026-10-05T05:04:07.936519+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- model digest: 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e
- think: None, language guard: on (regenerated 2/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'intfloat/multilingual-e5-small'}
- dataset: qa_dev_ko.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_sel_g0_qa_dev_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.75 | n/a | n/a | n/a | 0/0 | 5187 | 1/32 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| kd001 | 1.00 | None | None | None | 8181 | False | None / None | - |
| kd002 | 1.00 | None | None | None | 5034 | False | None / None | - |
| kd003 | 0.00 | None | None | None | 5595 | False | None / None | - |
| kd004 | 0.00 | None | None | None | 5901 | False | None / None | - |
| kd005 | 1.00 | None | None | None | 4656 | False | None / None | - |
| kd006 | 1.00 | None | None | None | 4364 | False | None / None | - |
| kd007 | 0.00 | None | None | None | 5093 | False | None / None | - |
| kd008 | 1.00 | None | None | None | 5225 | False | None / None | - |
| kd009 | 0.00 | None | None | None | 6324 | False | None / None | - |
| kd010 | 1.00 | None | None | None | 4364 | False | None / None | - |
| kd011 | 1.00 | None | None | None | 5305 | False | None / None | - |
| kd012 | 1.00 | None | None | None | 4227 | False | None / None | - |
| kd013 | 1.00 | None | None | None | 5664 | True | None / None | - |
| kd014 | 1.00 | None | None | None | 4569 | False | None / None | - |
| kd015 | 0.00 | None | None | None | 7056 | False | None / None | - |
| kd016 | 1.00 | None | None | None | 4854 | False | None / None | - |
| kd017 | 0.00 | None | None | None | 4619 | False | None / None | - |
| kd018 | 0.00 | None | None | None | 4485 | False | None / None | - |
| kd019 | 0.00 | None | None | None | 8895 | False | None / None | - |
| kd020 | 1.00 | None | None | None | 7892 | False | None / None | - |
| kd021 | 1.00 | None | None | None | 5489 | False | None / None | - |
| kd022 | 1.00 | None | None | None | 5171 | False | None / None | - |
| kd023 | 1.00 | None | None | None | 5850 | False | None / None | - |
| kd024 | 1.00 | None | None | None | 4601 | False | None / None | - |
| kd025 | 1.00 | None | None | None | 5295 | False | None / None | - |
| kd026 | 1.00 | None | None | None | 8428 | False | None / None | - |
| kd027 | 1.00 | None | None | None | 3537 | False | None / None | - |
| kd028 | 1.00 | None | None | None | 5139 | False | None / None | - |
| kd029 | 1.00 | None | None | None | 4682 | False | None / None | - |
| kd030 | 1.00 | None | None | None | 5203 | False | None / None | - |
| kd031 | 1.00 | None | None | None | 5533 | False | None / None | - |
| kd032 | 1.00 | None | None | None | 4692 | False | None / None | - |

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
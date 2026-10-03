# Answer eval report (v11_A_qa_dev_ko)

- date: 2026-10-03T22:33:23.979394+00:00
- generated: 2026-10-03T22:31:15.550377+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- dataset: qa_dev_ko.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v11_A_qa_dev_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.75 | n/a | n/a | n/a | 0/0 | 3400 | 2/32 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| kd001 | 1.00 | None | None | None | 3079 | False | None / None | - |
| kd002 | 1.00 | None | None | None | 3383 | False | None / None | - |
| kd003 | 0.00 | None | None | None | 3802 | False | None / None | - |
| kd004 | 1.00 | None | None | None | 4460 | False | None / None | - |
| kd005 | 1.00 | None | None | None | 3286 | False | None / None | - |
| kd006 | 1.00 | None | None | None | 3039 | False | None / None | - |
| kd007 | 0.00 | None | None | None | 3416 | False | None / None | - |
| kd008 | 1.00 | None | None | None | 3295 | False | None / None | - |
| kd009 | 0.00 | None | None | None | 4321 | False | None / None | - |
| kd010 | 1.00 | None | None | None | 3082 | False | None / None | - |
| kd011 | 1.00 | None | None | None | 3645 | False | None / None | - |
| kd012 | 1.00 | None | None | None | 3015 | False | None / None | - |
| kd013 | 1.00 | None | None | None | 2972 | True | None / None | - |
| kd014 | 1.00 | None | None | None | 3269 | False | None / None | - |
| kd015 | 0.00 | None | None | None | 4837 | False | None / None | - |
| kd016 | 1.00 | None | None | None | 3624 | False | None / None | - |
| kd017 | 0.00 | None | None | None | 3214 | False | None / None | - |
| kd018 | 0.00 | None | None | None | 3158 | False | None / None | - |
| kd019 | 0.00 | None | None | None | 3062 | True | None / None | - |
| kd020 | 1.00 | None | None | None | 5525 | False | None / None | - |
| kd021 | 1.00 | None | None | None | 3853 | False | None / None | - |
| kd022 | 1.00 | None | None | None | 3498 | False | None / None | - |
| kd023 | 0.00 | None | None | None | 3645 | False | None / None | - |
| kd024 | 1.00 | None | None | None | 3233 | False | None / None | - |
| kd025 | 1.00 | None | None | None | 3604 | False | None / None | - |
| kd026 | 1.00 | None | None | None | 5240 | False | None / None | - |
| kd027 | 1.00 | None | None | None | 2555 | False | None / None | - |
| kd028 | 1.00 | None | None | None | 3769 | False | None / None | - |
| kd029 | 1.00 | None | None | None | 3271 | False | None / None | - |
| kd030 | 1.00 | None | None | None | 3510 | False | None / None | - |
| kd031 | 1.00 | None | None | None | 3747 | False | None / None | - |
| kd032 | 1.00 | None | None | None | 3253 | False | None / None | - |

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
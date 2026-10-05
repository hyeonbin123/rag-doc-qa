# Answer eval report (v13_gate_g1_qa_dev_ko)

- date: 2026-10-05T04:22:22.578336+00:00
- generated: 2026-10-05T04:18:22.540861+00:00
- provider: ollama
- model: qwen3.5:9b
- model digest: 6488c96fa5faab64bb65cbd30d4289e20e6130ef535a93ef9a49f42eda893ea7
- think: False, language guard: off
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
- per-item records: eval/runs/v13_gate_g1_qa_dev_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.88 | n/a | n/a | n/a | 0/0 | 7075 | 0/32 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| kd001 | 1.00 | None | None | None | 6090 | False | None / None | - |
| kd002 | 1.00 | None | None | None | 7849 | False | None / None | - |
| kd003 | 1.00 | None | None | None | 6419 | False | None / None | - |
| kd004 | 1.00 | None | None | None | 7239 | False | None / None | - |
| kd005 | 1.00 | None | None | None | 8966 | False | None / None | - |
| kd006 | 1.00 | None | None | None | 5302 | False | None / None | - |
| kd007 | 0.00 | None | None | None | 10884 | False | None / None | - |
| kd008 | 1.00 | None | None | None | 5641 | False | None / None | - |
| kd009 | 1.00 | None | None | None | 8247 | False | None / None | - |
| kd010 | 1.00 | None | None | None | 5993 | False | None / None | - |
| kd011 | 1.00 | None | None | None | 6591 | False | None / None | - |
| kd012 | 1.00 | None | None | None | 5625 | False | None / None | - |
| kd013 | 1.00 | None | None | None | 6085 | False | None / None | - |
| kd014 | 1.00 | None | None | None | 9050 | False | None / None | - |
| kd015 | 0.00 | None | None | None | 9222 | False | None / None | - |
| kd016 | 1.00 | None | None | None | 6956 | False | None / None | - |
| kd017 | 1.00 | None | None | None | 6975 | False | None / None | - |
| kd018 | 0.00 | None | None | None | 7709 | False | None / None | - |
| kd019 | 0.00 | None | None | None | 5363 | False | None / None | - |
| kd020 | 1.00 | None | None | None | 6291 | False | None / None | - |
| kd021 | 1.00 | None | None | None | 8579 | False | None / None | - |
| kd022 | 1.00 | None | None | None | 7100 | False | None / None | - |
| kd023 | 1.00 | None | None | None | 7109 | False | None / None | - |
| kd024 | 1.00 | None | None | None | 5193 | False | None / None | - |
| kd025 | 1.00 | None | None | None | 5169 | False | None / None | - |
| kd026 | 1.00 | None | None | None | 10550 | False | None / None | - |
| kd027 | 1.00 | None | None | None | 4784 | False | None / None | - |
| kd028 | 1.00 | None | None | None | 7273 | False | None / None | - |
| kd029 | 1.00 | None | None | None | 7175 | False | None / None | - |
| kd030 | 1.00 | None | None | None | 9115 | False | None / None | - |
| kd031 | 1.00 | None | None | None | 7049 | False | None / None | - |
| kd032 | 1.00 | None | None | None | 7806 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **kd007** (0.00): 이미지나 CSS 같은 파일을 디렉터리에서 그대로 서빙하려면 어떻게 하나요?
  > 이미지나 CSS 같은 정적 파일 (예: JavaScript, CSS) 을 디렉터리에서 그대로 서빙하려면 다음과 같이 진행합니다.

1. **정적 파일 제공 디렉터리 생성**: 프로젝트 구조에 `static/`와 같은 디렉터리를 만듭니다.
2. **자동 문서 비활성화**: 기본적으로 FastAPI 는 CDN 을 사용하므로, 정적 파일을 직접 제공하려면 `Fa
- **kd015** (0.00): VS Code나 PyCharm 같은 에디터의 디버거로 앱을 실행하려면 어떻게 하나요?
  > VS Code 또는 PyCharm과 같은 편집기의 디버거를 사용하여 앱을 실행하는 방법은 다음과 같습니다.

**Visual Studio Code**의 경우:
1. "Debug" 패널로 이동합니다.
2. "Add configuration..."을 선택합니다.
3. "Python"을 선택합니다.
4. "`Python: Current File (Integrat
- **kd018** (0.00): 경로 처리에서 JSON 대신 HTML 페이지를 반환하려면 어떻게 하나요?
  > 경로 처리에서 JSON 대신 HTML 페이지를 반환하려면 `fallback="index.html"`을 사용하여 백엔드가 `index.html`에서 프론트엔드 애플리케이션을 제공하도록 해야 합니다. 이 설정은 브라우저 탐색 요청이 `Accept: text/html` 또는 `Accept: application/xhtml+xml` 헤더를 명시적으로 허용하는 `G
- **kd019** (0.00): 하나의 경로 처리가 항목을 수정할 때는 200을, 새로 만들 때는 201을 반환하게 하려면 어떻게 하나요?
  > 제공된 문서는 HTTP 상태 코드 (200 또는 201) 를 반환하는 방법에 대해 설명하지 않습니다. 따라서 이 정보를 알 수 없습니다.
- **kd001** (1.00): 경로 처리 함수에서 클라이언트가 보낸 쿠키 값을 읽으려면 어떻게 하나요?
  > 경로 처리 함수에서 클라이언트가 보낸 쿠키 값을 읽으려면 `Cookie` 매개변수를 선언하여 사용합니다. Pydantic의 모델 구성을 사용하여 추가(`extra`) 필드를 금지(`forbid`)할 수 있으며, 이를 통해 API 는 자신의 쿠키 동의 권한을 갖게 됩니다.
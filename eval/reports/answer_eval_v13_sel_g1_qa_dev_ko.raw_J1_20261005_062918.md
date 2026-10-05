# Answer eval report (v13_sel_g1_qa_dev_ko.raw, judge J1)

- date: 2026-10-05T06:29:18.554236+00:00
- generated: 2026-10-05T05:19:15.103019+00:00
- provider: ollama
- model: qwen3.5:9b
- model digest: 6488c96fa5faab64bb65cbd30d4289e20e6130ef535a93ef9a49f42eda893ea7
- think: False, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: J1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-05T06:27:47.423483+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'intfloat/multilingual-e5-small'}
- dataset: qa_dev_ko.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_sel_g1_qa_dev_ko.gen.jsonl, eval/runs/v13_sel_g1_qa_dev_ko.raw.J1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.88 | 4.00 | 4.31 | 138 | 1/32 | 7123 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| kd001 | 1.00 | 4 | 4 | False | 6420 | False | 1588 / 1588 | ok |
| kd002 | 1.00 | 4 | 4 | False | 7834 | False | 1833 / 1833 | ok |
| kd003 | 1.00 | 4 | 4 | False | 6384 | False | 1876 / 1876 | ok |
| kd004 | 1.00 | 4 | 4 | False | 7096 | False | 1905 / 1905 | ok |
| kd005 | 1.00 | 4 | 5 | False | 9061 | False | 1916 / 1916 | ok |
| kd006 | 1.00 | 4 | 5 | False | 5134 | False | 1844 / 1844 | ok |
| kd007 | 0.00 | 4 | 4 | False | 11095 | False | 2032 / 2032 | ok |
| kd008 | 1.00 | 4 | 4 | False | 5627 | False | 1657 / 1657 | ok |
| kd009 | 1.00 | 4 | 4 | False | 8300 | False | 1991 / 1991 | ok |
| kd010 | 1.00 | 4 | 5 | False | 5826 | False | 1856 / 1856 | ok |
| kd011 | 1.00 | 4 | 5 | False | 6631 | False | 1818 / 1818 | ok |
| kd012 | 1.00 | 4 | 5 | False | 5818 | False | 1649 / 1649 | ok |
| kd013 | 1.00 | 2 | 1 | True | 6155 | False | 1773 / 1773 | ok |
| kd014 | 1.00 | 4 | 5 | False | 9503 | False | 1878 / 1878 | ok |
| kd015 | 0.00 | 4 | 5 | False | 9147 | False | 2046 / 2046 | ok |
| kd016 | 1.00 | 4 | 4 | False | 6762 | False | 2027 / 2027 | ok |
| kd017 | 1.00 | 4 | 5 | False | 6894 | False | 1962 / 1962 | ok |
| kd018 | 0.00 | 4 | 4 | False | 7647 | False | 1949 / 1949 | ok |
| kd019 | 0.00 | 2 | 1 | False | 5326 | False | 1661 / 1661 | ok |
| kd020 | 1.00 | 4 | 4 | False | 6447 | False | 1833 / 1833 | ok |
| kd021 | 1.00 | 5 | 5 | False | 8727 | False | 2041 / 2041 | ok |
| kd022 | 1.00 | 4 | 5 | False | 7330 | False | 2179 / 2179 | ok |
| kd023 | 1.00 | 4 | 4 | False | 7264 | False | 1967 / 1967 | ok |
| kd024 | 1.00 | 4 | 5 | False | 5330 | False | 1664 / 1664 | ok |
| kd025 | 1.00 | 4 | 4 | False | 5297 | False | 1910 / 1910 | ok |
| kd026 | 1.00 | 4 | 5 | False | 11203 | False | 2197 / 2197 | ok |
| kd027 | 1.00 | 5 | 5 | False | 4778 | False | 1305 / 1305 | ok |
| kd028 | 1.00 | 5 | 5 | False | 7214 | False | 1684 / 1684 | ok |
| kd029 | 1.00 | 4 | 4 | False | 7279 | False | 2061 / 2061 | ok |
| kd030 | 1.00 | 5 | 5 | False | 9267 | False | 2044 / 2044 | ok |
| kd031 | 1.00 | 4 | 4 | False | 7150 | False | 1859 / 1859 | ok |
| kd032 | 1.00 | 4 | 5 | False | 7963 | False | 1931 / 1931 | ok |

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
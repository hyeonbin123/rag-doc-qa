# Answer eval report (v13_sel_g2_qa_dev_ko.raw, judge J1)

- date: 2026-10-05T06:34:41.406555+00:00
- generated: 2026-10-05T05:39:26.331456+00:00
- provider: ollama
- model: gemma4:12b-it-qat
- model digest: 38044be4f923e5a55264ed7df4eaac2676651a905f735197c504045140c02bd3
- think: False, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: J1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-05T06:33:04.295583+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'intfloat/multilingual-e5-small'}
- dataset: qa_dev_ko.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_sel_g2_qa_dev_ko.gen.jsonl, eval/runs/v13_sel_g2_qa_dev_ko.raw.J1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | 3.97 | 4.34 | 139 | 1/32 | 10602 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| kd001 | 1.00 | 3 | 3 | False | 7799 | False | 1541 / 1541 | ok |
| kd002 | 1.00 | 5 | 5 | False | 20221 | False | 2107 / 2107 | ok |
| kd003 | 1.00 | 4 | 5 | False | 11374 | False | 1931 / 1931 | ok |
| kd004 | 1.00 | 4 | 5 | False | 11870 | False | 1921 / 1921 | ok |
| kd005 | 1.00 | 4 | 4 | False | 10225 | False | 1815 / 1815 | ok |
| kd006 | 1.00 | 4 | 5 | False | 9178 | False | 1896 / 1896 | ok |
| kd007 | 0.00 | 3 | 2 | False | 9090 | False | 1823 / 1823 | ok |
| kd008 | 1.00 | 4 | 4 | False | 9103 | False | 1683 / 1683 | ok |
| kd009 | 1.00 | 5 | 5 | False | 16340 | False | 2114 / 2114 | ok |
| kd010 | 1.00 | 4 | 5 | False | 7536 | False | 1856 / 1856 | ok |
| kd011 | 1.00 | 4 | 5 | False | 8633 | False | 1789 / 1789 | ok |
| kd012 | 1.00 | 5 | 5 | False | 15711 | False | 1841 / 1841 | ok |
| kd013 | 1.00 | 2 | 1 | True | 8810 | False | 1761 / 1761 | ok |
| kd014 | 1.00 | 4 | 5 | False | 14695 | False | 1919 / 1919 | ok |
| kd015 | 1.00 | 4 | 5 | False | 12002 | False | 2020 / 2020 | ok |
| kd016 | 1.00 | 4 | 4 | False | 11222 | False | 2050 / 2050 | ok |
| kd017 | 1.00 | 4 | 5 | False | 11846 | False | 1992 / 1992 | ok |
| kd018 | 0.00 | 3 | 3 | False | 10451 | False | 1901 / 1901 | ok |
| kd019 | 0.00 | 2 | 2 | False | 9296 | False | 1668 / 1668 | ok |
| kd020 | 1.00 | 4 | 5 | False | 10752 | False | 1868 / 1868 | ok |
| kd021 | 1.00 | 5 | 5 | False | 12979 | False | 2044 / 2044 | ok |
| kd022 | 1.00 | 4 | 4 | False | 10301 | False | 2149 / 2149 | ok |
| kd023 | 1.00 | 4 | 5 | False | 11845 | False | 1985 / 1985 | ok |
| kd024 | 1.00 | 4 | 4 | False | 8403 | False | 1663 / 1663 | ok |
| kd025 | 1.00 | 4 | 5 | False | 8092 | False | 1908 / 1908 | ok |
| kd026 | 1.00 | 4 | 5 | False | 20753 | False | 2324 / 2324 | ok |
| kd027 | 1.00 | 5 | 5 | False | 7214 | False | 1297 / 1297 | ok |
| kd028 | 1.00 | 5 | 5 | False | 14535 | False | 1807 / 1807 | ok |
| kd029 | 1.00 | 4 | 4 | False | 10048 | False | 2039 / 2039 | ok |
| kd030 | 1.00 | 4 | 5 | False | 12954 | False | 1985 / 1985 | ok |
| kd031 | 1.00 | 4 | 4 | False | 12281 | False | 1903 / 1903 | ok |
| kd032 | 1.00 | 4 | 5 | False | 10316 | False | 1883 / 1883 | ok |

## Worst questions (lowest keyword coverage)

- **kd007** (0.00): 이미지나 CSS 같은 파일을 디렉터리에서 그대로 서빙하려면 어떻게 하나요?
  > 제공된 문맥에는 이미지나 CSS 같은 파일을 디렉터리에서 그대로 서빙하는 구체적인 방법에 대한 정보가 포함되어 있지 않습니다. 다만, 정적 파일을 자체 호스팅하기 위해 `static/` 디렉터리를 만들고 파일을 저장하는 구조에 대한 언급은 있습니다.
- **kd018** (0.00): 경로 처리에서 JSON 대신 HTML 페이지를 반환하려면 어떻게 하나요?
  > 제공된 문맥에는 경로 처리에서 JSON 대신 HTML 페이지를 반환하는 구체적인 방법에 대한 정보가 포함되어 있지 않습니다. 다만, `fallback="index.html"`을 사용하여 브라우저 탐색 요청에 대해 `index.html`을 제공할 수 있다는 내용과 `dict`, `list`, `str`, `int` 등을 반환할 수 있다는 내용만 언급되어 있습
- **kd019** (0.00): 하나의 경로 처리가 항목을 수정할 때는 200을, 새로 만들 때는 201을 반환하게 하려면 어떻게 하나요?
  > 제공된 문맥에는 하나의 경로 처리가 항목을 수정할 때 200을, 새로 만들 때 201을 반환하게 하는 방법에 대한 정보가 포함되어 있지 않습니다.
- **kd001** (1.00): 경로 처리 함수에서 클라이언트가 보낸 쿠키 값을 읽으려면 어떻게 하나요?
  > `Query`와 `Path`에서 사용하는 것과 동일한 공통 패턴으로, `Cookie`를 사용해 쿠키를 선언합니다.
- **kd002** (1.00): FastAPI가 돌려보내는 응답에 쿠키를 설정하려면 어떻게 하나요?
  > FastAPI에서 응답에 쿠키를 설정하는 방법은 다음과 같습니다.

1. **`Response` 매개변수 사용하기**:
*경로 처리 함수*에서 `Response` 타입의 매개변수를 선언하여 해당 *임시* 응답 객체에서 쿠키를 설정할 수 있습니다. 그 후 일반적으로 하듯이 필요한 객체(`dict`, 데이터베이스 모델 등)를 반환하면, FastAPI는 *임시*
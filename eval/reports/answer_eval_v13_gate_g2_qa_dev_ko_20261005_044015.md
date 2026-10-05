# Answer eval report (v13_gate_g2_qa_dev_ko)

- date: 2026-10-05T04:40:15.389192+00:00
- generated: 2026-10-05T04:34:39.631945+00:00
- provider: ollama
- model: gemma4:12b-it-qat
- model digest: 38044be4f923e5a55264ed7df4eaac2676651a905f735197c504045140c02bd3
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
- per-item records: eval/runs/v13_gate_g2_qa_dev_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | n/a | n/a | n/a | 0/0 | 9599 | 0/32 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| kd001 | 1.00 | None | None | None | 6239 | False | None / None | - |
| kd002 | 1.00 | None | None | None | 18490 | False | None / None | - |
| kd003 | 1.00 | None | None | None | 10321 | False | None / None | - |
| kd004 | 1.00 | None | None | None | 11309 | False | None / None | - |
| kd005 | 1.00 | None | None | None | 9979 | False | None / None | - |
| kd006 | 1.00 | None | None | None | 8731 | False | None / None | - |
| kd007 | 0.00 | None | None | None | 8492 | False | None / None | - |
| kd008 | 1.00 | None | None | None | 8319 | False | None / None | - |
| kd009 | 1.00 | None | None | None | 14983 | False | None / None | - |
| kd010 | 1.00 | None | None | None | 7820 | False | None / None | - |
| kd011 | 1.00 | None | None | None | 8147 | False | None / None | - |
| kd012 | 1.00 | None | None | None | 13616 | False | None / None | - |
| kd013 | 1.00 | None | None | None | 7516 | False | None / None | - |
| kd014 | 1.00 | None | None | None | 13567 | False | None / None | - |
| kd015 | 1.00 | None | None | None | 10640 | False | None / None | - |
| kd016 | 1.00 | None | None | None | 9634 | False | None / None | - |
| kd017 | 1.00 | None | None | None | 10912 | False | None / None | - |
| kd018 | 0.00 | None | None | None | 9564 | False | None / None | - |
| kd019 | 0.00 | None | None | None | 8270 | False | None / None | - |
| kd020 | 1.00 | None | None | None | 8924 | False | None / None | - |
| kd021 | 1.00 | None | None | None | 10795 | False | None / None | - |
| kd022 | 1.00 | None | None | None | 8969 | False | None / None | - |
| kd023 | 1.00 | None | None | None | 10361 | False | None / None | - |
| kd024 | 1.00 | None | None | None | 7033 | False | None / None | - |
| kd025 | 1.00 | None | None | None | 6977 | False | None / None | - |
| kd026 | 1.00 | None | None | None | 18117 | False | None / None | - |
| kd027 | 1.00 | None | None | None | 6212 | False | None / None | - |
| kd028 | 1.00 | None | None | None | 12335 | False | None / None | - |
| kd029 | 1.00 | None | None | None | 8501 | False | None / None | - |
| kd030 | 1.00 | None | None | None | 11091 | False | None / None | - |
| kd031 | 1.00 | None | None | None | 10726 | False | None / None | - |
| kd032 | 1.00 | None | None | None | 9021 | False | None / None | - |

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
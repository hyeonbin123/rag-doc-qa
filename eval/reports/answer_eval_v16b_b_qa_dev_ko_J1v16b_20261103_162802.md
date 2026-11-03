# Answer eval report (v16b_b_qa_dev_ko, judge J1v16b)

- date: 2026-11-03T16:28:02.678339+00:00
- generated: 2026-11-03T15:32:44.335491+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: J1v16b, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-11-03T16:27:24.983304+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_dev_ko.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_b_qa_dev_ko.gen.jsonl, eval/runs/v16b_b_qa_dev_ko.J1v16b.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | 4.16 | 4.62 | 148 | 2/32 | 4189 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| kd001 | 1.00 | 4 | 4 | False | 5923 | False | 1921 / 1921 | ok |
| kd002 | 1.00 | 5 | 5 | False | 4573 | False | 1673 / 1673 | ok |
| kd003 | 1.00 | 4 | 5 | False | 4756 | False | 1981 / 1981 | ok |
| kd004 | 1.00 | 5 | 5 | False | 8193 | False | 2388 / 2388 | ok |
| kd005 | 1.00 | 5 | 5 | False | 3347 | False | 2002 / 2002 | ok |
| kd006 | 1.00 | 4 | 5 | False | 2914 | False | 1895 / 1895 | ok |
| kd007 | 1.00 | 5 | 5 | False | 6816 | False | 2261 / 2261 | ok |
| kd008 | 1.00 | 5 | 5 | False | 2617 | False | 1963 / 1963 | ok |
| kd009 | 1.00 | 5 | 5 | False | 5718 | False | 2185 / 2185 | ok |
| kd010 | 1.00 | 4 | 4 | False | 2739 | False | 2110 / 2110 | ok |
| kd011 | 1.00 | 4 | 5 | False | 6481 | False | 2265 / 2265 | ok |
| kd012 | 1.00 | 5 | 5 | False | 6526 | False | 1981 / 1981 | ok |
| kd013 | 1.00 | 4 | 5 | False | 2255 | False | 1718 / 1718 | ok |
| kd014 | 1.00 | 4 | 5 | False | 2994 | False | 1955 / 1955 | ok |
| kd015 | 0.00 | 4 | 5 | False | 4409 | False | 2120 / 2120 | ok |
| kd016 | 1.00 | 4 | 5 | False | 6002 | False | 2296 / 2296 | ok |
| kd017 | 1.00 | 4 | 4 | False | 9536 | False | 2406 / 2406 | ok |
| kd018 | 1.00 | 5 | 5 | False | 5065 | False | 2044 / 2044 | ok |
| kd019 | 0.00 | 1 | 1 | True | 2259 | False | 1866 / 1866 | ok |
| kd020 | 1.00 | 4 | 5 | False | 9903 | False | 2700 / 2700 | ok |
| kd021 | 1.00 | 4 | 5 | False | 3802 | False | 1935 / 1935 | ok |
| kd022 | 1.00 | 4 | 5 | False | 2448 | False | 1843 / 1843 | ok |
| kd023 | 1.00 | 4 | 5 | False | 3969 | False | 1839 / 1839 | ok |
| kd024 | 1.00 | 4 | 5 | False | 2657 | False | 2027 / 2027 | ok |
| kd025 | 0.00 | 1 | 1 | True | 2811 | False | 1824 / 1824 | ok |
| kd026 | 1.00 | 4 | 5 | False | 5138 | False | 2334 / 2334 | ok |
| kd027 | 1.00 | 5 | 5 | False | 2375 | False | 1757 / 1757 | ok |
| kd028 | 1.00 | 5 | 5 | False | 3185 | False | 1763 / 1763 | ok |
| kd029 | 1.00 | 4 | 5 | False | 2976 | False | 1976 / 1976 | ok |
| kd030 | 1.00 | 5 | 5 | False | 5248 | False | 2221 / 2221 | ok |
| kd031 | 1.00 | 4 | 4 | False | 5754 | False | 2158 / 2158 | ok |
| kd032 | 1.00 | 4 | 5 | False | 2665 | False | 1983 / 1983 | ok |

## Worst questions (lowest keyword coverage)

- **kd015** (0.00): VS Code나 PyCharm 같은 에디터의 디버거로 앱을 실행하려면 어떻게 하나요?
  > VS Code나 PyCharm 같은 에디터의 디버거로 FastAPI 앱을 실행하려면 다음과 같이 할 수 있습니다:

### VS Code에서 디버거 실행
1. **"Debug" 패널**으로 이동합니다.
2. **"Add configuration..."**을 선택합니다.
3. **"Python"**을 선택합니다.
4. **"Python: Current Fil
- **kd019** (0.00): 하나의 경로 처리가 항목을 수정할 때는 200을, 새로 만들 때는 201을 반환하게 하려면 어떻게 하나요?
  > I don't know: the provided documentation passages do not cover this question.
- **kd025** (0.00): 파이썬 프로젝트마다 설치된 패키지를 따로 격리해 둬야 하는 이유는 무엇인가요?
  > 죄송합니다. 제공된 문서 구절에는 이 질문에 대한 내용이 없습니다.
- **kd001** (1.00): 경로 처리 함수에서 클라이언트가 보낸 쿠키 값을 읽으려면 어떻게 하나요?
  > 쿠키 값을 읽으려면 `Cookie` 매개변수를 경로 처리 함수에 선언해야 합니다. 예를 들어, 다음과 같이 사용할 수 있습니다:

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middlewar
- **kd002** (1.00): FastAPI가 돌려보내는 응답에 쿠키를 설정하려면 어떻게 하나요?
  > `Response` 매개변수를 사용하여 응답에 쿠키를 설정할 수 있습니다. 경로 처리 함수에서 `Response` 타입의 매개변수를 선언하고, 해당 임시 응답 객체에서 쿠키를 설정한 후 필요한 객체를 반환하면 됩니다. 또한, `Response`를 직접 반환하는 경우에도 쿠키를 설정할 수 있습니다.

```python
from fastapi import Fa
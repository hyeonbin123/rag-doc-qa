# Answer eval report (v16a_c6_qa_dev_ko.lg, judge J3v16a)

- date: 2026-11-03T00:23:30.456545+00:00
- generated: 2026-11-02T23:45:06.529730+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: J3v16a, qwen3.5:9b, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen3.5-9B@c202236
- judge order: dataset
- judge date: 2026-11-03T00:22:37.582804+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb_v16a, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_dev_ko.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16a_c6_qa_dev_ko.gen.jsonl, eval/runs/v16a_c6_qa_dev_ko.lg.J3v16a.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | 4.44 | 4.31 | 138 | 4/32 | 4166 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| kd001 | 1.00 | 2 | 3 | True | 4803 | False | 1599 / 1599 | ok |
| kd002 | 1.00 | 5 | 5 | False | 4855 | False | 1523 / 1523 | ok |
| kd003 | 1.00 | 5 | 5 | False | 3649 | False | 1635 / 1635 | ok |
| kd004 | 1.00 | 5 | 5 | False | 6413 | False | 1899 / 1899 | ok |
| kd005 | 1.00 | 5 | 5 | False | 4065 | False | 1862 / 1862 | ok |
| kd006 | 1.00 | 5 | 5 | False | 5442 | False | 1826 / 1826 | ok |
| kd007 | 1.00 | 5 | 5 | False | 5919 | False | 1962 / 1962 | ok |
| kd008 | 1.00 | 5 | 5 | False | 2101 | False | 1672 / 1672 | ok |
| kd009 | 1.00 | 5 | 5 | False | 9231 | False | 2240 / 2240 | ok |
| kd010 | 1.00 | 5 | 5 | False | 1942 | False | 1883 / 1883 | ok |
| kd011 | 1.00 | 2 | 2 | True | 8572 | False | 2143 / 2143 | ok |
| kd012 | 1.00 | 4 | 3 | False | 7083 | False | 1710 / 1710 | ok |
| kd013 | 1.00 | 5 | 5 | False | 2193 | False | 1521 / 1521 | ok |
| kd014 | 1.00 | 5 | 5 | False | 2525 | False | 1713 / 1713 | ok |
| kd015 | 0.00 | 4 | 3 | False | 4269 | False | 1870 / 1870 | ok |
| kd016 | 1.00 | 4 | 3 | False | 6114 | False | 2206 / 2206 | ok |
| kd017 | 1.00 | 4 | 3 | False | 10280 | False | 2226 / 2226 | ok |
| kd018 | 1.00 | 5 | 5 | False | 4266 | False | 1840 / 1840 | ok |
| kd019 | 0.00 | 2 | 2 | True | 9366 | False | 2261 / 2261 | ok |
| kd020 | 1.00 | 4 | 3 | False | 9224 | False | 2256 / 2256 | ok |
| kd021 | 1.00 | 5 | 5 | False | 5188 | False | 1869 / 1869 | ok |
| kd022 | 1.00 | 5 | 5 | False | 1911 | False | 1590 / 1590 | ok |
| kd023 | 1.00 | 5 | 5 | False | 3571 | False | 1568 / 1568 | ok |
| kd024 | 1.00 | 5 | 5 | False | 1958 | False | 1741 / 1741 | ok |
| kd025 | 0.00 | 2 | 3 | True | 1053 | False | 1607 / 1607 | ok |
| kd026 | 1.00 | 5 | 5 | False | 5059 | False | 1887 / 1887 | ok |
| kd027 | 1.00 | 5 | 5 | False | 1702 | False | 1634 / 1634 | ok |
| kd028 | 1.00 | 5 | 5 | False | 2582 | False | 1564 / 1564 | ok |
| kd029 | 1.00 | 5 | 5 | False | 3411 | False | 1716 / 1716 | ok |
| kd030 | 1.00 | 5 | 5 | False | 3270 | False | 1824 / 1824 | ok |
| kd031 | 1.00 | 4 | 3 | False | 3700 | False | 1747 / 1747 | ok |
| kd032 | 1.00 | 5 | 5 | False | 2111 | False | 1711 / 1711 | ok |

## Worst questions (lowest keyword coverage)

- **kd015** (0.00): VS Code나 PyCharm 같은 에디터의 디버거로 앱을 실행하려면 어떻게 하나요?
  > VS Code나 PyCharm 같은 에디터의 디버거로 FastAPI 앱을 실행하려면 다음 단계를 따르세요:

### VS Code에서 디버거로 실행
1. **"Debug" 패널**으로 이동합니다.
2. **"Add configuration..."**을 선택합니다.
3. **"Python"**을 선택합니다.
4. **"Python: Current File (
- **kd019** (0.00): 하나의 경로 처리가 항목을 수정할 때는 200을, 새로 만들 때는 201을 반환하게 하려면 어떻게 하나요?
  > FastAPI에서 하나의 경로 처리가 항목을 수정(PUT)할 때 200을, 새로 만들 때(POST) 201을 반환하게 하려면 다음과 같이 구현할 수 있습니다:

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import
- **kd025** (0.00): 파이썬 프로젝트마다 설치된 패키지를 따로 격리해 둬야 하는 이유는 무엇인가요?
  > 주어진 문서에서는 이 질문에 대한 직접적인 답변을 제공하지 않습니다. 따라서, 이 질문에 대한 답변을 제공할 수 없습니다.
- **kd001** (1.00): 경로 처리 함수에서 클라이언트가 보낸 쿠키 값을 읽으려면 어떻게 하나요?
  > 경로 처리 함수에서 클라이언트가 보낸 쿠키 값을 읽으려면 `Cookie` 매개변수를 사용해야 합니다. 예를 들어, 다음과 같이 쿠키 매개변수를 선언할 수 있습니다:

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
fr
- **kd002** (1.00): FastAPI가 돌려보내는 응답에 쿠키를 설정하려면 어떻게 하나요?
  > `Response` 매개변수를 사용하거나, `Response` 객체를 직접 반환하여 쿠키를 설정할 수 있습니다.

1. **`Response` 매개변수 사용:**
   경로 처리 함수에서 `Response` 타입의 매개변수를 선언하고, 해당 객체에서 쿠키를 설정할 수 있습니다.

   ```python
   from fastapi import FastAPI
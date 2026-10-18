# Answer eval report (v14_c3_qa_dev_ko.lg, judge J3v15r2)

- date: 2026-10-18T16:02:38.748279+00:00
- generated: 2026-10-14T04:21:48.627644+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: J3v15r2, qwen3.5:9b, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen3.5-9B@c202236
- judge order: dataset
- judge date: 2026-10-18T16:01:20.995109+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_dev_ko.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v14_c3_qa_dev_ko.gen.jsonl, eval/runs/v14_c3_qa_dev_ko.lg.J3v15r2.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.88 | 4.53 | 4.34 | 139 | 2/32 | 7298 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| kd001 | 1.00 | 4 | 3 | False | 8014 | False | 1612 / 1612 | ok |
| kd002 | 1.00 | 5 | 5 | False | 8456 | False | 1529 / 1529 | ok |
| kd003 | 1.00 | 5 | 5 | False | 6779 | False | 1635 / 1635 | ok |
| kd004 | 0.00 | 4 | 3 | False | 7805 | False | 1791 / 1791 | ok |
| kd005 | 1.00 | 5 | 5 | False | 7369 | False | 1862 / 1862 | ok |
| kd006 | 1.00 | 5 | 5 | False | 7228 | False | 1803 / 1803 | ok |
| kd007 | 1.00 | 5 | 5 | False | 7450 | False | 1857 / 1857 | ok |
| kd008 | 1.00 | 5 | 5 | False | 4763 | False | 1672 / 1672 | ok |
| kd009 | 1.00 | 4 | 5 | False | 11913 | False | 2199 / 2199 | ok |
| kd010 | 1.00 | 5 | 5 | False | 5007 | False | 1897 / 1897 | ok |
| kd011 | 1.00 | 2 | 2 | True | 14139 | False | 2199 / 2199 | ok |
| kd012 | 1.00 | 5 | 5 | False | 8338 | False | 1598 / 1598 | ok |
| kd013 | 1.00 | 5 | 5 | False | 3838 | False | 1508 / 1508 | ok |
| kd014 | 1.00 | 5 | 5 | False | 4505 | False | 1535 / 1535 | ok |
| kd015 | 0.00 | 4 | 3 | False | 7453 | False | 1872 / 1872 | ok |
| kd016 | 1.00 | 4 | 3 | False | 10287 | False | 2202 / 2202 | ok |
| kd017 | 1.00 | 4 | 3 | False | 12172 | False | 2036 / 2036 | ok |
| kd018 | 1.00 | 5 | 5 | False | 7648 | False | 1840 / 1840 | ok |
| kd019 | 0.00 | 4 | 3 | False | 12558 | False | 2273 / 2273 | ok |
| kd020 | 1.00 | 4 | 3 | False | 10078 | False | 2058 / 2058 | ok |
| kd021 | 1.00 | 5 | 5 | False | 9060 | False | 1904 / 1904 | ok |
| kd022 | 1.00 | 5 | 5 | False | 4461 | False | 1590 / 1590 | ok |
| kd023 | 1.00 | 5 | 5 | False | 6247 | False | 1568 / 1568 | ok |
| kd024 | 1.00 | 5 | 5 | False | 4650 | False | 1741 / 1741 | ok |
| kd025 | 0.00 | 2 | 3 | True | 4035 | False | 1589 / 1589 | ok |
| kd026 | 1.00 | 5 | 5 | False | 8370 | False | 1937 / 1937 | ok |
| kd027 | 1.00 | 5 | 5 | False | 4154 | False | 1634 / 1634 | ok |
| kd028 | 1.00 | 5 | 5 | False | 5120 | False | 1564 / 1564 | ok |
| kd029 | 1.00 | 5 | 5 | False | 5035 | False | 1715 / 1715 | ok |
| kd030 | 1.00 | 5 | 5 | False | 6337 | False | 1824 / 1824 | ok |
| kd031 | 1.00 | 4 | 3 | False | 6659 | False | 1747 / 1747 | ok |
| kd032 | 1.00 | 5 | 5 | False | 4608 | False | 1711 / 1711 | ok |

## Worst questions (lowest keyword coverage)

- **kd004** (0.00): 경로 처리가 반환하는 데이터의 타입을 선언해서 FastAPI가 검증하고 걸러 내게 하려면 어떻게 하나요?
  > 경로 처리 함수의 반환 타입을 선언하여 FastAPI가 데이터를 검증하고 필터링하게 하려면, 함수 반환 타입에 타입 어노테이션을 사용하면 됩니다. 예를 들어, Pydantic 모델을 반환 타입으로 지정하면 FastAPI는 해당 모델의 필드에 따라 데이터를 검증하고, 필터링합니다.

```python
from fastapi import FastAPI
from
- **kd015** (0.00): VS Code나 PyCharm 같은 에디터의 디버거로 앱을 실행하려면 어떻게 하나요?
  > VS Code나 PyCharm 같은 에디터의 디버거로 FastAPI 앱을 실행하려면 다음 단계를 따르세요:

### VS Code에서 디버거로 실행
1. **"Debug" 패널**으로 이동합니다.
2. **"Add configuration..."**을 선택합니다.
3. **"Python"**을 선택합니다.
4. **"Python: Current File (
- **kd019** (0.00): 하나의 경로 처리가 항목을 수정할 때는 200을, 새로 만들 때는 201을 반환하게 하려면 어떻게 하나요?
  > FastAPI에서 하나의 경로 처리가 항목을 수정(PUT)할 때와 새로 만들(POST) 때 각각 200과 201 상태 코드를 반환하려면, 다음과 같이 구현할 수 있습니다:

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing
- **kd025** (0.00): 파이썬 프로젝트마다 설치된 패키지를 따로 격리해 둬야 하는 이유는 무엇인가요?
  > 주어진 문서에 해당 정보가 없습니다.
- **kd001** (1.00): 경로 처리 함수에서 클라이언트가 보낸 쿠키 값을 읽으려면 어떻게 하나요?
  > 경로 처리 함수에서 클라이언트가 보낸 쿠키 값을 읽으려면 `Cookie` 매개변수를 사용해야 합니다. 예를 들어, 다음과 같이 쿠키 매개변수를 선언할 수 있습니다:

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
fr
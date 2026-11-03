# Answer eval report (v16a_c5_qa_dev_ko)

- date: 2026-11-02T23:44:47.312240+00:00
- generated: 2026-11-02T23:41:38.322460+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- corpus: source commit 50113da (277 documents); last fetched 2026-10-09T02:59:20.705331+00:00; chunks en 914, ko 621
- dataset: qa_dev_ko.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16a_c5_qa_dev_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.88 | n/a | n/a | n/a | 0/0 | 5204 | 0/32 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| kd001 | 1.00 | None | None | None | 5885 | False | None / None | - |
| kd002 | 1.00 | None | None | None | 6037 | False | None / None | - |
| kd003 | 1.00 | None | None | None | 4790 | False | None / None | - |
| kd004 | 0.00 | None | None | None | 5681 | False | None / None | - |
| kd005 | 1.00 | None | None | None | 5293 | False | None / None | - |
| kd006 | 1.00 | None | None | None | 5115 | False | None / None | - |
| kd007 | 1.00 | None | None | None | 5378 | False | None / None | - |
| kd008 | 1.00 | None | None | None | 3321 | False | None / None | - |
| kd009 | 1.00 | None | None | None | 8716 | False | None / None | - |
| kd010 | 1.00 | None | None | None | 3496 | False | None / None | - |
| kd011 | 1.00 | None | None | None | 10359 | False | None / None | - |
| kd012 | 1.00 | None | None | None | 6019 | False | None / None | - |
| kd013 | 1.00 | None | None | None | 2726 | False | None / None | - |
| kd014 | 1.00 | None | None | None | 3156 | False | None / None | - |
| kd015 | 0.00 | None | None | None | 5403 | False | None / None | - |
| kd016 | 1.00 | None | None | None | 7541 | False | None / None | - |
| kd017 | 1.00 | None | None | None | 8978 | False | None / None | - |
| kd018 | 1.00 | None | None | None | 5597 | False | None / None | - |
| kd019 | 0.00 | None | None | None | 9532 | False | None / None | - |
| kd020 | 1.00 | None | None | None | 7249 | False | None / None | - |
| kd021 | 1.00 | None | None | None | 6431 | False | None / None | - |
| kd022 | 1.00 | None | None | None | 3030 | False | None / None | - |
| kd023 | 1.00 | None | None | None | 4607 | False | None / None | - |
| kd024 | 1.00 | None | None | None | 3254 | False | None / None | - |
| kd025 | 0.00 | None | None | None | 1081 | False | None / None | - |
| kd026 | 1.00 | None | None | None | 5853 | False | None / None | - |
| kd027 | 1.00 | None | None | None | 2961 | False | None / None | - |
| kd028 | 1.00 | None | None | None | 3699 | False | None / None | - |
| kd029 | 1.00 | None | None | None | 3564 | False | None / None | - |
| kd030 | 1.00 | None | None | None | 4646 | False | None / None | - |
| kd031 | 1.00 | None | None | None | 4847 | False | None / None | - |
| kd032 | 1.00 | None | None | None | 3334 | False | None / None | - |

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
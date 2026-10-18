# Answer eval report (v15_i3_a_qa_dev_ko)

- date: 2026-10-18T11:59:31.988296+00:00
- generated: 2026-10-18T11:56:01.362116+00:00
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
- dataset: qa_dev_ko.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i3_a_qa_dev_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.88 | n/a | n/a | n/a | 0/0 | 5925 | 0/32 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| kd001 | 1.00 | None | None | None | 6650 | False | None / None | - |
| kd002 | 1.00 | None | None | None | 6778 | False | None / None | - |
| kd003 | 1.00 | None | None | None | 5336 | False | None / None | - |
| kd004 | 0.00 | None | None | None | 6416 | False | None / None | - |
| kd005 | 1.00 | None | None | None | 6095 | False | None / None | - |
| kd006 | 1.00 | None | None | None | 5904 | False | None / None | - |
| kd007 | 1.00 | None | None | None | 6236 | False | None / None | - |
| kd008 | 1.00 | None | None | None | 4009 | False | None / None | - |
| kd009 | 1.00 | None | None | None | 9999 | False | None / None | - |
| kd010 | 1.00 | None | None | None | 4174 | False | None / None | - |
| kd011 | 1.00 | None | None | None | 11625 | False | None / None | - |
| kd012 | 1.00 | None | None | None | 6684 | False | None / None | - |
| kd013 | 1.00 | None | None | None | 3227 | False | None / None | - |
| kd014 | 1.00 | None | None | None | 3662 | False | None / None | - |
| kd015 | 0.00 | None | None | None | 5945 | False | None / None | - |
| kd016 | 1.00 | None | None | None | 8189 | False | None / None | - |
| kd017 | 1.00 | None | None | None | 9671 | False | None / None | - |
| kd018 | 1.00 | None | None | None | 6155 | False | None / None | - |
| kd019 | 0.00 | None | None | None | 10204 | False | None / None | - |
| kd020 | 1.00 | None | None | None | 7843 | False | None / None | - |
| kd021 | 1.00 | None | None | None | 7066 | False | None / None | - |
| kd022 | 1.00 | None | None | None | 3545 | False | None / None | - |
| kd023 | 1.00 | None | None | None | 5130 | False | None / None | - |
| kd024 | 1.00 | None | None | None | 3886 | False | None / None | - |
| kd025 | 0.00 | None | None | None | 3284 | False | None / None | - |
| kd026 | 1.00 | None | None | None | 6842 | False | None / None | - |
| kd027 | 1.00 | None | None | None | 3527 | False | None / None | - |
| kd028 | 1.00 | None | None | None | 4359 | False | None / None | - |
| kd029 | 1.00 | None | None | None | 4230 | False | None / None | - |
| kd030 | 1.00 | None | None | None | 5342 | False | None / None | - |
| kd031 | 1.00 | None | None | None | 5554 | False | None / None | - |
| kd032 | 1.00 | None | None | None | 3949 | False | None / None | - |

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
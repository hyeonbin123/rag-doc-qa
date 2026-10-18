# Answer eval report (v15_i3_b_qa_dev_ko)

- date: 2026-10-18T12:02:12.220559+00:00
- generated: 2026-10-18T11:59:45.989128+00:00
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
- per-item records: eval/runs/v15_i3_b_qa_dev_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | n/a | n/a | n/a | 0/0 | 3770 | 0/32 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| kd001 | 1.00 | None | None | None | 5275 | False | None / None | - |
| kd002 | 1.00 | None | None | None | 4903 | False | None / None | - |
| kd003 | 1.00 | None | None | None | 3700 | False | None / None | - |
| kd004 | 1.00 | None | None | None | 4213 | False | None / None | - |
| kd005 | 1.00 | None | None | None | 4011 | False | None / None | - |
| kd006 | 1.00 | None | None | None | 3532 | False | None / None | - |
| kd007 | 1.00 | None | None | None | 3502 | False | None / None | - |
| kd008 | 1.00 | None | None | None | 2048 | False | None / None | - |
| kd009 | 1.00 | None | None | None | 7648 | False | None / None | - |
| kd010 | 1.00 | None | None | None | 2036 | False | None / None | - |
| kd011 | 1.00 | None | None | None | 8826 | False | None / None | - |
| kd012 | 1.00 | None | None | None | 4555 | False | None / None | - |
| kd013 | 1.00 | None | None | None | 1772 | False | None / None | - |
| kd014 | 1.00 | None | None | None | 2104 | False | None / None | - |
| kd015 | 0.00 | None | None | None | 4152 | False | None / None | - |
| kd016 | 1.00 | None | None | None | 6264 | False | None / None | - |
| kd017 | 1.00 | None | None | None | 10562 | False | None / None | - |
| kd018 | 1.00 | None | None | None | 4460 | False | None / None | - |
| kd019 | 0.00 | None | None | None | 8136 | False | None / None | - |
| kd020 | 1.00 | None | None | None | 6913 | False | None / None | - |
| kd021 | 1.00 | None | None | None | 5171 | False | None / None | - |
| kd022 | 1.00 | None | None | None | 1820 | False | None / None | - |
| kd023 | 1.00 | None | None | None | 3307 | False | None / None | - |
| kd024 | 1.00 | None | None | None | 1965 | False | None / None | - |
| kd025 | 0.00 | None | None | None | 1570 | False | None / None | - |
| kd026 | 1.00 | None | None | None | 4532 | False | None / None | - |
| kd027 | 1.00 | None | None | None | 1418 | False | None / None | - |
| kd028 | 1.00 | None | None | None | 2530 | False | None / None | - |
| kd029 | 1.00 | None | None | None | 2311 | False | None / None | - |
| kd030 | 1.00 | None | None | None | 3252 | False | None / None | - |
| kd031 | 1.00 | None | None | None | 3841 | False | None / None | - |
| kd032 | 1.00 | None | None | None | 1885 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **kd015** (0.00): VS Code나 PyCharm 같은 에디터의 디버거로 앱을 실행하려면 어떻게 하나요?
  > VS Code나 PyCharm 같은 에디터의 디버거로 FastAPI 앱을 실행하려면 다음 단계를 따르세요:

### VS Code에서 디버거로 실행
1. **"Debug" 패널**으로 이동합니다.
2. **"Add configuration..."**을 선택합니다.
3. **"Python"**을 선택합니다.
4. **"Python: Current File (
- **kd019** (0.00): 하나의 경로 처리가 항목을 수정할 때는 200을, 새로 만들 때는 201을 반환하게 하려면 어떻게 하나요?
  > FastAPI에서 하나의 경로 처리가 항목을 수정(PUT)할 때와 새로 만들(POST) 때 각각 200과 201 상태 코드를 반환하려면, 다음과 같은 방법을 사용할 수 있습니다:

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from ty
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
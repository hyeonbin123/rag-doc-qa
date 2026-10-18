# Answer eval report (v14_c3_qa_dev_ko.lg, judge J2v15r1)

- date: 2026-10-18T14:26:54.482987+00:00
- generated: 2026-10-14T04:21:48.627644+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: J2v15r1, gemma4:12b-it-qat, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: google/gemma-4-12B-it@707f0a3
- judge order: dataset
- judge date: 2026-10-18T14:25:00.713355+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_dev_ko.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v14_c3_qa_dev_ko.gen.jsonl, eval/runs/v14_c3_qa_dev_ko.lg.J2v15r1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.88 | 4.59 | 4.41 | 141 | 2/32 | 7298 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| kd001 | 1.00 | 5 | 5 | False | 8014 | False | 1655 / 1655 | ok |
| kd002 | 1.00 | 5 | 5 | False | 8456 | False | 1621 / 1621 | ok |
| kd003 | 1.00 | 5 | 5 | False | 6779 | False | 1765 / 1765 | ok |
| kd004 | 0.00 | 3 | 2 | False | 7805 | False | 1895 / 1895 | ok |
| kd005 | 1.00 | 5 | 5 | False | 7369 | False | 2001 / 2001 | ok |
| kd006 | 1.00 | 5 | 5 | False | 7228 | False | 1917 / 1917 | ok |
| kd007 | 1.00 | 5 | 5 | False | 7450 | False | 1996 / 1996 | ok |
| kd008 | 1.00 | 5 | 5 | False | 4763 | False | 1797 / 1797 | ok |
| kd009 | 1.00 | 5 | 5 | False | 11913 | False | 2328 / 2328 | ok |
| kd010 | 1.00 | 5 | 5 | False | 5007 | False | 2060 / 2060 | ok |
| kd011 | 1.00 | 2 | 2 | True | 14139 | False | 2331 / 2331 | ok |
| kd012 | 1.00 | 5 | 5 | False | 8338 | False | 1712 / 1712 | ok |
| kd013 | 1.00 | 5 | 5 | False | 3838 | False | 1581 / 1581 | ok |
| kd014 | 1.00 | 5 | 5 | False | 4505 | False | 1640 / 1640 | ok |
| kd015 | 0.00 | 5 | 4 | False | 7453 | False | 1946 / 1946 | ok |
| kd016 | 1.00 | 5 | 5 | False | 10287 | False | 2333 / 2333 | ok |
| kd017 | 1.00 | 5 | 5 | False | 12172 | False | 2135 / 2135 | ok |
| kd018 | 1.00 | 5 | 5 | False | 7648 | False | 1990 / 1990 | ok |
| kd019 | 0.00 | 5 | 2 | False | 12558 | False | 2405 / 2405 | ok |
| kd020 | 1.00 | 2 | 2 | True | 10078 | False | 2130 / 2130 | ok |
| kd021 | 1.00 | 5 | 5 | False | 9060 | False | 2056 / 2056 | ok |
| kd022 | 1.00 | 5 | 5 | False | 4461 | False | 1647 / 1647 | ok |
| kd023 | 1.00 | 5 | 5 | False | 6247 | False | 1668 / 1668 | ok |
| kd024 | 1.00 | 5 | 5 | False | 4650 | False | 1864 / 1864 | ok |
| kd025 | 0.00 | 1 | 1 | False | 4035 | False | 1775 / 1775 | ok |
| kd026 | 1.00 | 5 | 5 | False | 8370 | False | 2008 / 2008 | ok |
| kd027 | 1.00 | 5 | 5 | False | 4154 | False | 1680 / 1680 | ok |
| kd028 | 1.00 | 5 | 5 | False | 5120 | False | 1621 / 1621 | ok |
| kd029 | 1.00 | 5 | 5 | False | 5035 | False | 1786 / 1786 | ok |
| kd030 | 1.00 | 5 | 5 | False | 6337 | False | 1910 / 1910 | ok |
| kd031 | 1.00 | 4 | 3 | False | 6659 | False | 1811 / 1811 | ok |
| kd032 | 1.00 | 5 | 5 | False | 4608 | False | 1796 / 1796 | ok |

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
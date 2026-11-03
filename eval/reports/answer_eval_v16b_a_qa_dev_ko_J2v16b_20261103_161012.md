# Answer eval report (v16b_a_qa_dev_ko, judge J2v16b)

- date: 2026-11-03T16:10:12.561777+00:00
- generated: 2026-11-03T15:29:20.059119+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: J2v16b, gemma4:12b-it-qat, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: google/gemma-4-12B-it@707f0a3
- judge order: dataset
- judge date: 2026-11-03T16:08:37.432260+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_dev_ko.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_a_qa_dev_ko.gen.jsonl, eval/runs/v16b_a_qa_dev_ko.J2v16b.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | 4.59 | 4.53 | 145 | 4/32 | 5341 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| kd001 | 1.00 | 2 | 2 | True | 6196 | False | 1699 / 1699 | ok |
| kd002 | 1.00 | 5 | 5 | False | 6020 | False | 1621 / 1621 | ok |
| kd003 | 1.00 | 5 | 5 | False | 4734 | False | 1765 / 1765 | ok |
| kd004 | 1.00 | 5 | 5 | False | 5697 | False | 1913 / 1913 | ok |
| kd005 | 1.00 | 5 | 5 | False | 5289 | False | 2001 / 2001 | ok |
| kd006 | 1.00 | 5 | 5 | False | 5411 | False | 1946 / 1946 | ok |
| kd007 | 1.00 | 5 | 5 | False | 6555 | False | 2103 / 2103 | ok |
| kd008 | 1.00 | 5 | 5 | False | 3314 | False | 1797 / 1797 | ok |
| kd009 | 1.00 | 5 | 5 | False | 9205 | False | 2365 / 2365 | ok |
| kd010 | 1.00 | 5 | 5 | False | 3449 | False | 2060 / 2060 | ok |
| kd011 | 1.00 | 2 | 2 | True | 10368 | False | 2331 / 2331 | ok |
| kd012 | 1.00 | 5 | 5 | False | 7089 | False | 1836 / 1836 | ok |
| kd013 | 1.00 | 5 | 5 | False | 2819 | False | 1613 / 1613 | ok |
| kd014 | 1.00 | 5 | 5 | False | 3327 | False | 1825 / 1825 | ok |
| kd015 | 0.00 | 5 | 4 | False | 5392 | False | 1946 / 1946 | ok |
| kd016 | 1.00 | 5 | 5 | False | 7538 | False | 2333 / 2333 | ok |
| kd017 | 1.00 | 5 | 5 | False | 8966 | False | 2135 / 2135 | ok |
| kd018 | 1.00 | 5 | 5 | False | 5621 | False | 1990 / 1990 | ok |
| kd019 | 0.00 | 2 | 2 | True | 9338 | False | 2393 / 2393 | ok |
| kd020 | 1.00 | 2 | 2 | True | 9242 | False | 2352 / 2352 | ok |
| kd021 | 1.00 | 5 | 5 | False | 6032 | False | 2008 / 2008 | ok |
| kd022 | 1.00 | 5 | 5 | False | 3022 | False | 1647 / 1647 | ok |
| kd023 | 1.00 | 5 | 5 | False | 4580 | False | 1668 / 1668 | ok |
| kd024 | 1.00 | 5 | 5 | False | 3264 | False | 1864 / 1864 | ok |
| kd025 | 0.00 | 5 | 5 | False | 1233 | False | 1795 / 1795 | ok |
| kd026 | 1.00 | 5 | 5 | False | 6310 | False | 2030 / 2030 | ok |
| kd027 | 1.00 | 5 | 5 | False | 2913 | False | 1680 / 1680 | ok |
| kd028 | 1.00 | 5 | 5 | False | 3715 | False | 1621 / 1621 | ok |
| kd029 | 1.00 | 5 | 5 | False | 3546 | False | 1788 / 1788 | ok |
| kd030 | 1.00 | 5 | 5 | False | 4602 | False | 1910 / 1910 | ok |
| kd031 | 1.00 | 4 | 3 | False | 4835 | False | 1811 / 1811 | ok |
| kd032 | 1.00 | 5 | 5 | False | 3309 | False | 1796 / 1796 | ok |

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
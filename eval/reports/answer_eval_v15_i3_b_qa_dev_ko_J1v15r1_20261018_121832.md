# Answer eval report (v15_i3_b_qa_dev_ko, judge J1v15r1)

- date: 2026-10-18T12:18:32.191528+00:00
- generated: 2026-10-18T11:59:45.989128+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: J1v15r1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-18T12:17:23.945406+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_dev_ko.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i3_b_qa_dev_ko.gen.jsonl, eval/runs/v15_i3_b_qa_dev_ko.J1v15r1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.91 | 4.53 | 4.72 | 151 | 1/32 | 3770 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| kd001 | 1.00 | 4 | 4 | False | 5275 | False | 1925 / 1925 | ok |
| kd002 | 1.00 | 5 | 5 | False | 4903 | False | 1745 / 1745 | ok |
| kd003 | 1.00 | 5 | 5 | False | 3700 | False | 1909 / 1909 | ok |
| kd004 | 1.00 | 5 | 5 | False | 4213 | False | 2059 / 2059 | ok |
| kd005 | 1.00 | 5 | 5 | False | 4011 | False | 2112 / 2112 | ok |
| kd006 | 1.00 | 5 | 5 | False | 3532 | False | 2014 / 2014 | ok |
| kd007 | 1.00 | 5 | 5 | False | 3502 | False | 2066 / 2066 | ok |
| kd008 | 1.00 | 5 | 5 | False | 2048 | False | 1973 / 1973 | ok |
| kd009 | 1.00 | 5 | 5 | False | 7648 | False | 2415 / 2415 | ok |
| kd010 | 1.00 | 4 | 5 | False | 2036 | False | 2099 / 2099 | ok |
| kd011 | 1.00 | 4 | 4 | False | 8826 | False | 2480 / 2480 | ok |
| kd012 | 1.00 | 5 | 5 | False | 4555 | False | 1844 / 1844 | ok |
| kd013 | 1.00 | 5 | 5 | False | 1772 | False | 1693 / 1693 | ok |
| kd014 | 1.00 | 4 | 4 | False | 2104 | False | 1745 / 1745 | ok |
| kd015 | 0.00 | 4 | 5 | False | 4152 | False | 2160 / 2160 | ok |
| kd016 | 1.00 | 4 | 4 | False | 6264 | False | 2414 / 2414 | ok |
| kd017 | 1.00 | 5 | 5 | False | 10562 | False | 2465 / 2465 | ok |
| kd018 | 1.00 | 5 | 5 | False | 4460 | False | 2048 / 2048 | ok |
| kd019 | 0.00 | 5 | 5 | False | 8136 | False | 2467 / 2467 | ok |
| kd020 | 1.00 | 5 | 5 | False | 6913 | False | 2396 / 2396 | ok |
| kd021 | 1.00 | 5 | 5 | False | 5171 | False | 2145 / 2145 | ok |
| kd022 | 1.00 | 4 | 5 | False | 1820 | False | 1843 / 1843 | ok |
| kd023 | 1.00 | 4 | 5 | False | 3307 | False | 1842 / 1842 | ok |
| kd024 | 1.00 | 4 | 5 | False | 1965 | False | 2027 / 2027 | ok |
| kd025 | 0.00 | 1 | 1 | True | 1570 | False | 1836 / 1836 | ok |
| kd026 | 1.00 | 5 | 5 | False | 4532 | False | 2369 / 2369 | ok |
| kd027 | 1.00 | 5 | 5 | False | 1418 | False | 1757 / 1757 | ok |
| kd028 | 1.00 | 5 | 5 | False | 2530 | False | 1759 / 1759 | ok |
| kd029 | 1.00 | 5 | 5 | False | 2311 | False | 1987 / 1987 | ok |
| kd030 | 1.00 | 5 | 5 | False | 3252 | False | 2109 / 2109 | ok |
| kd031 | 1.00 | 4 | 4 | False | 3841 | False | 2015 / 2015 | ok |
| kd032 | 1.00 | 4 | 5 | False | 1885 | False | 2002 / 2002 | ok |

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
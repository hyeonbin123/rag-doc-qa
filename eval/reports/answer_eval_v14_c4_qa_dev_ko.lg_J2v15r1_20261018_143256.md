# Answer eval report (v14_c4_qa_dev_ko.lg, judge J2v15r1)

- date: 2026-10-18T14:32:56.189247+00:00
- generated: 2026-10-14T04:26:26.985144+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/32)
- final answer call stopped by the output limit, done_reason=length: 0/32; reasoning output: 0/32; citation replies breaking the schema: 0/32
- judge: J2v15r1, gemma4:12b-it-qat, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: google/gemma-4-12B-it@707f0a3
- judge order: dataset
- judge date: 2026-10-18T14:31:10.850336+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb_c4, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_dev_ko.jsonl
- questions: 32
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v14_c4_qa_dev_ko.gen.jsonl, eval/runs/v14_c4_qa_dev_ko.lg.J2v15r1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.88 | 4.41 | 4.31 | 138 | 6/32 | 6233 | 0/32 | 0/32 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| kd001 | 1.00 | 2 | 2 | True | 6540 | False | 1643 / 1643 | ok |
| kd002 | 1.00 | 5 | 5 | False | 9411 | False | 1810 / 1810 | ok |
| kd003 | 1.00 | 5 | 5 | False | 5965 | False | 1795 / 1795 | ok |
| kd004 | 1.00 | 5 | 5 | False | 4169 | False | 1599 / 1599 | ok |
| kd005 | 1.00 | 5 | 5 | False | 6226 | False | 1948 / 1948 | ok |
| kd006 | 1.00 | 5 | 5 | False | 5849 | False | 1905 / 1905 | ok |
| kd007 | 1.00 | 5 | 5 | False | 9117 | False | 1936 / 1936 | ok |
| kd008 | 1.00 | 5 | 5 | False | 5134 | False | 1655 / 1655 | ok |
| kd009 | 1.00 | 5 | 5 | False | 14178 | False | 2374 / 2374 | ok |
| kd010 | 1.00 | 5 | 5 | False | 4607 | False | 1610 / 1610 | ok |
| kd011 | 1.00 | 3 | 2 | True | 9465 | False | 2038 / 2038 | ok |
| kd012 | 1.00 | 5 | 5 | False | 8806 | False | 1831 / 1831 | ok |
| kd013 | 1.00 | 1 | 1 | True | 4060 | False | 1687 / 1687 | ok |
| kd014 | 1.00 | 5 | 5 | False | 3497 | False | 1709 / 1709 | ok |
| kd015 | 0.00 | 5 | 5 | False | 6206 | False | 1901 / 1901 | ok |
| kd016 | 1.00 | 3 | 2 | True | 9019 | False | 2278 / 2278 | ok |
| kd017 | 1.00 | 5 | 5 | False | 12840 | False | 2190 / 2190 | ok |
| kd018 | 1.00 | 5 | 5 | False | 7755 | False | 1975 / 1975 | ok |
| kd019 | 0.00 | 2 | 2 | True | 10872 | False | 2196 / 2196 | ok |
| kd020 | 1.00 | 2 | 2 | True | 11123 | False | 2233 / 2233 | ok |
| kd021 | 1.00 | 5 | 5 | False | 12006 | False | 2259 / 2259 | ok |
| kd022 | 1.00 | 5 | 5 | False | 4482 | False | 1617 / 1617 | ok |
| kd023 | 1.00 | 5 | 4 | False | 6240 | False | 1698 / 1698 | ok |
| kd024 | 1.00 | 5 | 5 | False | 4083 | False | 1604 / 1604 | ok |
| kd025 | 0.00 | 5 | 5 | False | 3629 | False | 1768 / 1768 | ok |
| kd026 | 1.00 | 5 | 5 | False | 8761 | False | 1895 / 1895 | ok |
| kd027 | 1.00 | 5 | 5 | False | 3867 | False | 1686 / 1686 | ok |
| kd028 | 0.00 | 5 | 5 | False | 3950 | False | 1579 / 1579 | ok |
| kd029 | 1.00 | 5 | 5 | False | 4423 | False | 1566 / 1566 | ok |
| kd030 | 1.00 | 5 | 5 | False | 7049 | False | 2036 / 2036 | ok |
| kd031 | 1.00 | 3 | 3 | False | 3738 | False | 1636 / 1636 | ok |
| kd032 | 1.00 | 5 | 5 | False | 11109 | False | 2207 / 2207 | ok |

## Worst questions (lowest keyword coverage)

- **kd015** (0.00): VS Code나 PyCharm 같은 에디터의 디버거로 앱을 실행하려면 어떻게 하나요?
  > VS Code나 PyCharm 같은 에디터의 디버거로 FastAPI 앱을 실행하려면 다음 단계를 따르세요:

1. **VS Code에서 디버깅 설정:**
   - "Debug" 패널로 이동합니다.
   - "Add configuration..."을 선택합니다.
   - "Python"을 선택합니다.
   - "Python: Current File (Inte
- **kd019** (0.00): 하나의 경로 처리가 항목을 수정할 때는 200을, 새로 만들 때는 201을 반환하게 하려면 어떻게 하나요?
  > FastAPI에서 경로 처리가 항목을 수정(PUT)할 때와 새로 만들(POST) 때 각각 200과 201 상태 코드를 반환하도록 하려면, 다음과 같은 방법을 사용할 수 있습니다:

1. **PUT 메서드**로 항목을 수정할 때는, 해당 항목이 이미 존재하는지 확인하고, 존재하면 수정(update)하고 200 상태 코드를 반환합니다.
2. **POST 메서드
- **kd025** (0.00): 파이썬 프로젝트마다 설치된 패키지를 따로 격리해 둬야 하는 이유는 무엇인가요?
  > 주어진 문서에 해당 정보가 없습니다.
- **kd028** (0.00): fastapi dev 명령은 무엇을 하나요?
  > fastapi dev 명령은 `main.py` 파일을 자동으로 읽고, 그 안의 FastAPI 앱을 감지한 다음, Uvicorn을 사용해 서버를 시작합니다. 기본적으로 auto-reload가 활성화되어 있어 코드 변경 시 서버를 자동으로 다시 로드합니다.
- **kd001** (1.00): 경로 처리 함수에서 클라이언트가 보낸 쿠키 값을 읽으려면 어떻게 하나요?
  > 경로 처리 함수에서 클라이언트가 보낸 쿠키 값을 읽으려면 `Cookie` 매개변수를 사용해야 합니다. 예를 들어, 다음과 같이 쿠키 매개변수를 선언할 수 있습니다:

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
fr
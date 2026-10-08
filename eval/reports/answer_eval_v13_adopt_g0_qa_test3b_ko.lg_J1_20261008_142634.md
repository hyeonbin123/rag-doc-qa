# Answer eval report (v13_adopt_g0_qa_test3b_ko.lg, judge J1)

- date: 2026-10-08T14:26:34.008567+00:00
- generated: 2026-10-08T13:32:57.106473+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- model digest: 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-08T14:24:53.702260+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'intfloat/multilingual-e5-small'}
- dataset: qa_test3b_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_adopt_g0_qa_test3b_ko.gen.jsonl, eval/runs/v13_adopt_g0_qa_test3b_ko.lg.J1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.65 | 4.08 | 4.22 | 169 | 0/40 | 5005 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n007 | 1.00 | 4 | 4 | False | 6664 | False | 1972 / 1972 | ok |
| n008 | 1.00 | 4 | 5 | False | 4050 | False | 1826 / 1826 | ok |
| n010 | 1.00 | 4 | 4 | False | 4455 | False | 1953 / 1953 | ok |
| n013 | 0.00 | 4 | 4 | False | 5115 | False | 1799 / 1799 | ok |
| n017 | 1.00 | 4 | 4 | False | 8041 | False | 2156 / 2156 | ok |
| n019 | 1.00 | 5 | 5 | False | 5040 | False | 1631 / 1631 | ok |
| n020 | 1.00 | 4 | 4 | False | 4533 | False | 1865 / 1865 | ok |
| n023 | 1.00 | 4 | 4 | False | 4970 | False | 1815 / 1815 | ok |
| n025 | 0.50 | 4 | 4 | False | 4221 | False | 1872 / 1872 | ok |
| n027 | 1.00 | 4 | 5 | False | 3935 | False | 1519 / 1519 | ok |
| n028 | 1.00 | 5 | 5 | False | 4305 | False | 1904 / 1904 | ok |
| n029 | 1.00 | 5 | 5 | False | 4126 | False | 1769 / 1769 | ok |
| n030 | 0.00 | 4 | 4 | False | 4780 | False | 1777 / 1777 | ok |
| n032 | 0.50 | 4 | 4 | False | 5351 | False | 1779 / 1779 | ok |
| n034 | 1.00 | 5 | 5 | False | 7183 | False | 2015 / 2015 | ok |
| n035 | 1.00 | 4 | 4 | False | 5554 | False | 2061 / 2061 | ok |
| n036 | 0.00 | 4 | 4 | False | 4967 | False | 1970 / 1970 | ok |
| n039 | 0.00 | 4 | 4 | False | 5414 | False | 2062 / 2062 | ok |
| n047 | 1.00 | 4 | 4 | False | 9216 | False | 2268 / 2268 | ok |
| n048 | 1.00 | 4 | 5 | False | 4144 | False | 1914 / 1914 | ok |
| n050 | 0.50 | 4 | 4 | False | 4820 | False | 1655 / 1655 | ok |
| n051 | 0.00 | 4 | 4 | False | 5914 | False | 1747 / 1747 | ok |
| n054 | 1.00 | 4 | 4 | False | 5178 | False | 1997 / 1997 | ok |
| n055 | 1.00 | 4 | 4 | False | 5128 | False | 1905 / 1905 | ok |
| n061 | 1.00 | 4 | 4 | False | 7505 | False | 2039 / 2039 | ok |
| n067 | 1.00 | 4 | 4 | False | 4692 | False | 2005 / 2005 | ok |
| n077 | 0.00 | 3 | 3 | False | 3807 | False | 1865 / 1865 | ok |
| n083 | 1.00 | 4 | 4 | False | 6042 | False | 1964 / 1964 | ok |
| n086 | 0.00 | 3 | 3 | False | 5367 | False | 2073 / 2073 | ok |
| n091 | 1.00 | 3 | 3 | False | 4074 | False | 1847 / 1847 | ok |
| n096 | 1.00 | 4 | 4 | False | 6110 | False | 2033 / 2033 | ok |
| n097 | 0.00 | 4 | 5 | False | 5174 | False | 2149 / 2149 | ok |
| n099 | 0.50 | 4 | 4 | False | 4638 | False | 1775 / 1775 | ok |
| n105 | 1.00 | 4 | 4 | False | 3983 | False | 1825 / 1825 | ok |
| n106 | 0.50 | 5 | 5 | False | 4719 | False | 1894 / 1894 | ok |
| n112 | 1.00 | 5 | 5 | False | 4927 | False | 1962 / 1962 | ok |
| n113 | 0.50 | 4 | 5 | False | 4648 | False | 1719 / 1719 | ok |
| n115 | 0.00 | 4 | 4 | False | 5704 | False | 2040 / 2040 | ok |
| n116 | 0.00 | 4 | 5 | False | 5097 | False | 1926 / 1926 | ok |
| n120 | 0.00 | 4 | 4 | False | 6081 | False | 2149 / 2149 | ok |

## Worst questions (lowest keyword coverage)

- **n013** (0.00): 한 엔드포인트에서 경로 파라미터, 쿼리 파라미터, 요청 본문을 같이 받으면 FastAPI는 각각을 어떻게 구분하나요?
  > FastAPI는 각 요청 파라미터를 명확하게 구분합니다. 경로 파라미터는 경로 내의 템플릿 변수로 선언되며, 쿼리 파라미터는 함수의 키워드 인수로 선언되며, 요청 본문은 `Body` 매개변수를 사용하여 선언됩니다. 만약 Pydantic 모델 타입으로 선언되면, 요청 본문으로 해석됩니다.
- **n030** (0.00): Header로 헤더 값을 읽을 때 언더스코어가 하이픈으로 자동 변환된다는 게 무슨 뜻이야?
  > 헤더 이름에 언더스코어가 포함되어 있더라도, FastAPI는 이를 하이픈으로 자동 변환하여 헤더 값을 읽습니다. 예를 들어, `Header` 매개변수로 `save_data`를 선언하면, 실제 HTTP 헤더는 `save-data`가 됩니다.
- **n036** (0.00): RequestValidationError 핸들러를 덮어쓰면서 FastAPI 기본 핸들러 동작도 재사용하는 방법이 있을까?
  > 네, 가능합니다. Starlette의 `HTTPException`을 등록하여 Starlette의 예외를 잡을 수 있으며, 동시에 FastAPI의 기본 예외 핸들러도 재사용할 수 있습니다. 이를 위해 `fastapi.exception_handlers`에서 기본 예외 핸들러를 가져와 사용할 수 있습니다.
- **n039** (0.00): 의존성 안에서 또 다른 의존성을 쓰는 하위 의존성은 어떻게 동작해?
  > 하위 의존성은 선언된 의존성의 반환값을 파라미터로 사용할 수 있습니다. 이 경우, 의존성 함수는 `yield`를 사용하여 실행을 일시 중지하고, 하위 의존성 함수가 실행된 후 다시 실행됩니다. 이렇게 하면 하위 의존성이 먼저 종료되지만, 상위 의존성은 여전히 하위 의존성의 반환값을 사용할 수 있습니다.
- **n051** (0.00): 비활성화된 계정은 로그인돼도 API를 못 쓰게 막고 싶은데 의존성을 어떻게 구성하나요?
  > 의존성을 구성하여 비활성화된 계정은 로그인돼도 API를 못 쓰게 하려면, `current_user` 의존성을 추가하고, 그 안에서 사용자 상태를 확인하여 비활성화된 계정이면 API 호출을 거부하는 로직을 작성하면 됩니다.

```python
from fastapi import Depends, HTTPException, status

async def act
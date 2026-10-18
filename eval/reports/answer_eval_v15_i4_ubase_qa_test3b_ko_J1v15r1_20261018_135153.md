# Answer eval report (v15_i4_ubase_qa_test3b_ko, judge J1v15r1)

- date: 2026-10-18T13:51:53.995396+00:00
- generated: 2026-10-18T13:32:43.335588+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/14)
- final answer call stopped by the output limit, done_reason=length: 0/14; reasoning output: 0/14; citation replies breaking the schema: 0/14
- judge: J1v15r1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-18T13:51:21.849811+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_test3b_ko.jsonl
- questions: 14
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_ubase_qa_test3b_ko.gen.jsonl, eval/runs/v15_i4_ubase_qa_test3b_ko.J1v15r1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.75 | 4.29 | 4.50 | 63 | 0/14 | 5223 | 0/14 | 0/14 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n010 | 1.00 | 4 | 5 | False | 4773 | False | 2023 / 2023 | ok |
| n025 | 1.00 | 4 | 4 | False | 4874 | False | 2020 / 2020 | ok |
| n027 | 1.00 | 5 | 5 | False | 4818 | False | 1760 / 1760 | ok |
| n029 | 1.00 | 5 | 5 | False | 5114 | False | 1949 / 1949 | ok |
| n030 | 0.00 | 4 | 4 | False | 3910 | False | 1858 / 1858 | ok |
| n034 | 1.00 | 5 | 5 | False | 5278 | False | 1770 / 1770 | ok |
| n050 | 1.00 | 4 | 4 | False | 7713 | False | 2006 / 2006 | ok |
| n051 | 0.00 | 4 | 4 | False | 10178 | False | 2321 / 2321 | ok |
| n061 | 1.00 | 4 | 4 | False | 13323 | False | 2367 / 2367 | ok |
| n077 | 0.50 | 4 | 4 | False | 5168 | False | 2041 / 2041 | ok |
| n083 | 1.00 | 4 | 5 | False | 5104 | False | 1952 / 1952 | ok |
| n097 | 1.00 | 5 | 5 | False | 5629 | False | 2220 / 2220 | ok |
| n105 | 1.00 | 4 | 5 | False | 6720 | False | 2260 / 2260 | ok |
| n115 | 0.00 | 4 | 4 | False | 9307 | False | 2552 / 2552 | ok |

## Worst questions (lowest keyword coverage)

- **n030** (0.00): Header로 헤더 값을 읽을 때 언더스코어가 하이픈으로 자동 변환된다는 게 무슨 뜻이야?
  > Header 클래스는 매개변수 이름에 포함된 언더스코어(_)를 하이픈(-)으로 자동 변환합니다. 예를 들어, 파이썬 코드에서 `user_agent`로 헤더를 선언하면, FastAPI는 이를 `User-Agent`로 변환하여 HTTP 헤더에서 값을 추출합니다. 이는 HTTP 헤더가 대소문자를 구분하지 않고, 일반적으로 하이픈(-)을 사용한다는 표준에 맞추기 
- **n051** (0.00): 비활성화된 계정은 로그인돼도 API를 못 쓰게 막고 싶은데 의존성을 어떻게 구성하나요?
  > 의존성을 구성하여 비활성화된 계정에 대한 접근을 제한하려면, 다음과 같은 방법을 사용할 수 있습니다:

1. **사용자 상태 검증 함수 작성**:
   - 사용자 상태를 검증하는 함수를 작성합니다. 이 함수는 사용자 ID를 받아 해당 사용자가 활성화 상태인지 확인합니다.
   - 예: `is_user_active(user_id: int) -> bool`


- **n115** (0.00): JSON 바디를 분명히 보냈는데 422 Unprocessable Entity가 계속 떠요. 뭘 잘못한 걸까요?
  > 422 Unprocessable Entity 오류는 주로 요청된 데이터가 서버의 스키마나 유효성 검사 규칙을 충족하지 못할 때 발생합니다. 이 오류의 원인을 찾기 위해 다음 사항을 확인해 보세요:

1. **데이터 타입 확인**:
   - JSON 바디에 포함된 데이터가 예상하는 타입과 일치하는지 확인하세요. 예를 들어, 숫자 필드에 문자열이 들어가 있거나
- **n077** (0.50): @app.on_event("startup")은 아직 써도 되나요? deprecated 된 건가요?
  > @app.on_event("startup")은 여전히 사용 가능합니다. 다만, FastAPI의 최신 버전에서는 `lifespan` 매개변수를 사용하는 것이 권장됩니다. `lifespan` 매개변수를 사용하면 `startup`과 `shutdown` 이벤트 핸들러를 더 효율적으로 관리할 수 있습니다.

`startup` 이벤트는 애플리케이션이 요청을 받기 전에
- **n010** (1.00): Path로 숫자형 경로 파라미터에 gt, le 같은 범위 검증을 걸 수 있습니까?
  > 네, 가능합니다. `Path`를 사용하여 숫자형 경로 파라미터에 `gt`, `le` 등의 범위 검증을 걸 수 있습니다. 예를 들어, `item_id`가 1보다 크고 10 이하인 경우에만 유효하도록 하려면 다음과 같이 선언할 수 있습니다:

```python
from fastapi import FastAPI, Path
app = FastAPI()

@app.
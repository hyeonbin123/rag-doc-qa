# Answer eval report (v15_i4_ucand_qa_test3b_ko)

- date: 2026-10-18T13:36:08.335661+00:00
- generated: 2026-10-18T13:34:46.452652+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/14)
- final answer call stopped by the output limit, done_reason=length: 0/14; reasoning output: 0/14; citation replies breaking the schema: 0/14
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_test3b_ko.jsonl
- questions: 14
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_ucand_qa_test3b_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.68 | n/a | n/a | n/a | 0/0 | 4120 | 0/14 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n010 | 1.00 | None | None | None | 3944 | False | None / None | - |
| n025 | 1.00 | None | None | None | 3792 | False | None / None | - |
| n027 | 1.00 | None | None | None | 4422 | False | None / None | - |
| n029 | 1.00 | None | None | None | 3730 | False | None / None | - |
| n030 | 0.00 | None | None | None | 3201 | False | None / None | - |
| n034 | 1.00 | None | None | None | 4295 | False | None / None | - |
| n050 | 1.00 | None | None | None | 6001 | False | None / None | - |
| n051 | 0.00 | None | None | None | 9147 | False | None / None | - |
| n061 | 1.00 | None | None | None | 12093 | False | None / None | - |
| n077 | 0.50 | None | None | None | 1916 | False | None / None | - |
| n083 | 1.00 | None | None | None | 4686 | False | None / None | - |
| n097 | 1.00 | None | None | None | 2850 | False | None / None | - |
| n105 | 0.00 | None | None | None | 0 | False | None / None | - |
| n115 | 0.00 | None | None | None | 9432 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **n030** (0.00): Header로 헤더 값을 읽을 때 언더스코어가 하이픈으로 자동 변환된다는 게 무슨 뜻이야?
  > Header로 헤더 값을 읽을 때, 파이썬 코드에서 변수 이름에 언더스코어(_)가 포함되어 있으면 FastAPI가 이를 하이픈(-)으로 자동 변환하여 처리합니다. 예를 들어, 파이썬 코드에서 `user_agent`라는 변수를 사용하면, FastAPI는 이를 HTTP 헤더에서 `user-agent`로 해석합니다. 이는 HTTP 헤더가 대소문자를 구분하지 않고
- **n051** (0.00): 비활성화된 계정은 로그인돼도 API를 못 쓰게 막고 싶은데 의존성을 어떻게 구성하나요?
  > 의존성을 구성하여 비활성화된 계정에 대한 접근을 제한하려면, 다음과 같은 방법을 사용할 수 있습니다:

1. **사용자 상태 검증 함수 작성**:
   - 사용자 상태를 검증하는 함수를 작성합니다. 이 함수는 사용자 ID를 받아 해당 사용자가 활성화 상태인지 확인합니다.
   - 예: `is_user_active(user_id: int) -> bool`


- **n105** (0.00): 엔드포인트 docstring이 문서 설명으로 나오던데, summary랑 description은 따로 어떻게 지정하나요?
  > 모르겠습니다. 찾은 문서 구절에는 이 질문에 대한 내용이 없습니다.
- **n115** (0.00): JSON 바디를 분명히 보냈는데 422 Unprocessable Entity가 계속 떠요. 뭘 잘못한 걸까요?
  > 422 Unprocessable Entity 오류는 주로 요청의 JSON 바디가 유효하지 않을 때 발생합니다. 이 오류의 일반적인 원인은 다음과 같습니다:

1. **데이터 타입 불일치**:
   - Pydantic 모델이나 스키마에 정의된 타입과 실제 요청 데이터의 타입이 일치하지 않는 경우.
   - 예를 들어, `int` 타입을 기대하는데 문자열이 들
- **n077** (0.50): @app.on_event("startup")은 아직 써도 되나요? deprecated 된 건가요?
  > @app.on_event("startup")은 아직 사용 가능합니다. deprecated 되지 않았습니다.
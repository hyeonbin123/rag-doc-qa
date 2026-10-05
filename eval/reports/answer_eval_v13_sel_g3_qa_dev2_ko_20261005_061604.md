# Answer eval report (v13_sel_g3_qa_dev2_ko)

- date: 2026-10-05T06:16:04.886752+00:00
- generated: 2026-10-05T06:08:51.432150+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 1/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'intfloat/multilingual-e5-small'}
- dataset: qa_dev2_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_sel_g3_qa_dev2_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.85 | n/a | n/a | n/a | 0/0 | 10419 | 0/40 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n001 | 1.00 | None | None | None | 4315 | False | None / None | - |
| n005 | 1.00 | None | None | None | 12000 | False | None / None | - |
| n006 | 1.00 | None | None | None | 10585 | False | None / None | - |
| n009 | 1.00 | None | None | None | 5210 | False | None / None | - |
| n011 | 1.00 | None | None | None | 5055 | False | None / None | - |
| n012 | 1.00 | None | None | None | 7322 | False | None / None | - |
| n015 | 0.00 | None | None | None | 10529 | False | None / None | - |
| n018 | 0.00 | None | None | None | 10054 | False | None / None | - |
| n031 | 1.00 | None | None | None | 13646 | False | None / None | - |
| n041 | 1.00 | None | None | None | 8059 | False | None / None | - |
| n044 | 1.00 | None | None | None | 12280 | False | None / None | - |
| n049 | 0.50 | None | None | None | 4792 | False | None / None | - |
| n053 | 1.00 | None | None | None | 13699 | False | None / None | - |
| n058 | 1.00 | None | None | None | 8587 | False | None / None | - |
| n059 | 1.00 | None | None | None | 13511 | False | None / None | - |
| n063 | 1.00 | None | None | None | 8914 | False | None / None | - |
| n066 | 1.00 | None | None | None | 6724 | False | None / None | - |
| n068 | 1.00 | None | None | None | 4735 | False | None / None | - |
| n069 | 0.00 | None | None | None | 18329 | False | None / None | - |
| n073 | 1.00 | None | None | None | 10998 | False | None / None | - |
| n074 | 0.50 | None | None | None | 5710 | False | None / None | - |
| n076 | 0.50 | None | None | None | 13980 | False | None / None | - |
| n080 | 1.00 | None | None | None | 11766 | False | None / None | - |
| n084 | 1.00 | None | None | None | 9703 | False | None / None | - |
| n087 | 1.00 | None | None | None | 6006 | False | None / None | - |
| n088 | 1.00 | None | None | None | 10309 | False | None / None | - |
| n089 | 0.50 | None | None | None | 6273 | False | None / None | - |
| n090 | 1.00 | None | None | None | 12914 | False | None / None | - |
| n092 | 1.00 | None | None | None | 14438 | False | None / None | - |
| n094 | 1.00 | None | None | None | 14049 | False | None / None | - |
| n098 | 1.00 | None | None | None | 13087 | False | None / None | - |
| n100 | 1.00 | None | None | None | 8284 | False | None / None | - |
| n102 | 1.00 | None | None | None | 13824 | False | None / None | - |
| n103 | 0.00 | None | None | None | 25912 | False | None / None | - |
| n107 | 1.00 | None | None | None | 5595 | False | None / None | - |
| n110 | 1.00 | None | None | None | 6656 | False | None / None | - |
| n114 | 1.00 | None | None | None | 15866 | False | None / None | - |
| n117 | 1.00 | None | None | None | 13650 | False | None / None | - |
| n118 | 1.00 | None | None | None | 9912 | False | None / None | - |
| n119 | 1.00 | None | None | None | 14531 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **n015** (0.00): 요청 본문에 Pydantic 모델 두 개를 동시에 받을 수 있어?
  > 네, 요청 본문에 Pydantic 모델 두 개를 동시에 받을 수 있습니다. FastAPI는 경로 매개변수, 요청 본문, 쿼리 매개변수를 동시에 선언하고 사용할 수 있도록 설계되어 있습니다.

예를 들어, 다음과 같이 두 개의 Pydantic 모델을 요청 본문에 동시에 받을 수 있습니다:

```python
from fastapi import FastAPI,
- **n018** (0.00): Swagger 문서에 요청 바디 예시를 여러 개 보여주고 싶은데 가능할까요?
  > 네, 가능합니다. FastAPI에서 `Body()` 매개변수에 여러 개의 `examples`를 선언하여 Swagger 문서에 여러 요청 바디 예시를 보여줄 수 있습니다.

```python
from fastapi import FastAPI, Body
from pydantic import BaseModel

app = FastAPI()

class Item(
- **n069** (0.00): 테스트용 DB를 운영 DB와 분리해서 쓰고 싶은데 어떻게 구성하는 게 좋을까요?
  > 테스트용 DB를 운영 DB와 분리하려면 다음과 같은 구성을 고려할 수 있습니다:

1. **환경 변수 사용**:
   - `DATABASE_URL` 같은 환경 변수를 사용하여 운영 환경과 테스트 환경의 데이터베이스 연결 문자열을 구분합니다.
   - 예: `.env` 파일에 `DATABASE_URL_PRODUCTION`과 `DATABASE_URL_TEST`
- **n103** (0.00): 인터넷이 안 되는 사내망이라 Swagger UI가 CDN에서 안 불러와져요. 오프라인에서 문서 보는 방법은?
  > 정적 파일을 직접 호스팅하여 오프라인에서도 문서를 볼 수 있도록 설정해야 합니다.

### 1. 정적 파일 테스트용 경로 처리 만들기

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templa
- **n049** (0.50): 비밀번호 해싱은 뭘로 해야 돼? passlib, bcrypt, argon2 중에 뭐가 나아?
  > Argon2가 가장 나아.
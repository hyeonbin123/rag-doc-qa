# Answer eval report (v13_adopt_g3_qa_test2_ko)

- date: 2026-10-08T14:19:32.200369+00:00
- generated: 2026-10-08T14:13:41.866400+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/43)
- final answer call stopped by the output limit, done_reason=length: 0/43; reasoning output: 0/43; citation replies breaking the schema: 0/43
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'intfloat/multilingual-e5-small'}
- dataset: qa_test2_ko.jsonl
- questions: 43
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_adopt_g3_qa_test2_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.81 | n/a | n/a | n/a | 0/0 | 7160 | 0/43 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| k001 | 1.00 | None | None | None | 11618 | False | None / None | - |
| k002 | 1.00 | None | None | None | 6603 | False | None / None | - |
| k003 | 1.00 | None | None | None | 9187 | False | None / None | - |
| k004 | 1.00 | None | None | None | 8349 | False | None / None | - |
| k005 | 1.00 | None | None | None | 6049 | False | None / None | - |
| k006 | 0.00 | None | None | None | 4507 | False | None / None | - |
| k007 | 1.00 | None | None | None | 8781 | False | None / None | - |
| k008 | 0.00 | None | None | None | 8257 | False | None / None | - |
| k009 | 1.00 | None | None | None | 9792 | False | None / None | - |
| k010 | 0.00 | None | None | None | 3573 | False | None / None | - |
| k011 | 1.00 | None | None | None | 11971 | False | None / None | - |
| k012 | 1.00 | None | None | None | 5941 | False | None / None | - |
| k013 | 0.00 | None | None | None | 3505 | False | None / None | - |
| k014 | 1.00 | None | None | None | 6275 | False | None / None | - |
| k015 | 0.00 | None | None | None | 6964 | False | None / None | - |
| k016 | 1.00 | None | None | None | 11368 | False | None / None | - |
| k017 | 1.00 | None | None | None | 4193 | False | None / None | - |
| k018 | 1.00 | None | None | None | 20028 | False | None / None | - |
| k019 | 1.00 | None | None | None | 10866 | False | None / None | - |
| k020 | 1.00 | None | None | None | 4326 | False | None / None | - |
| k021 | 1.00 | None | None | None | 7641 | False | None / None | - |
| k022 | 1.00 | None | None | None | 4244 | False | None / None | - |
| k023 | 1.00 | None | None | None | 4186 | False | None / None | - |
| k024 | 1.00 | None | None | None | 4087 | False | None / None | - |
| k025 | 1.00 | None | None | None | 6638 | False | None / None | - |
| k026 | 1.00 | None | None | None | 11512 | False | None / None | - |
| k027 | 1.00 | None | None | None | 4578 | False | None / None | - |
| k028 | 1.00 | None | None | None | 8427 | False | None / None | - |
| k029 | 1.00 | None | None | None | 10765 | False | None / None | - |
| k030 | 0.00 | None | None | None | 5426 | False | None / None | - |
| k031 | 1.00 | None | None | None | 6836 | False | None / None | - |
| k032 | 0.00 | None | None | None | 7049 | False | None / None | - |
| k033 | 1.00 | None | None | None | 7160 | False | None / None | - |
| k034 | 1.00 | None | None | None | 9379 | False | None / None | - |
| k035 | 1.00 | None | None | None | 3763 | False | None / None | - |
| k036 | 1.00 | None | None | None | 6691 | False | None / None | - |
| k037 | 1.00 | None | None | None | 8083 | False | None / None | - |
| k038 | 1.00 | None | None | None | 8921 | False | None / None | - |
| k039 | 1.00 | None | None | None | 9435 | False | None / None | - |
| k040 | 1.00 | None | None | None | 5677 | False | None / None | - |
| k041 | 1.00 | None | None | None | 19356 | False | None / None | - |
| k042 | 1.00 | None | None | None | 7832 | False | None / None | - |
| k043 | 0.00 | None | None | None | 7321 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **k006** (0.00): 로그인한 사용자만 호출할 수 있게 엔드포인트를 보호하려면 어떻게 하나요?
  > `get_current_active_user` 의존성을 사용하여 로그인한 사용자만 호출할 수 있게 엔드포인트를 보호할 수 있습니다. 이 의존성은 사용자가 존재하고 활성 상태인지 확인한 후, 현재 사용자를 반환합니다. 이를 통해 엔드포인트에서 `current_user`를 사용하여 인증된 사용자만 접근할 수 있도록 제한할 수 있습니다.
- **k008** (0.00): 모든 요청이 처리되는 데 얼마나 걸리는지 기록하려면 어떻게 하나요?
  > `APIRouter`의 `route_class` 파라미터를 사용하여 커스텀 `APIRoute` 클래스를 만들고, 그 클래스 내에서 요청 처리 시간을 측정할 수 있습니다. 예를 들어, `TimedRoute`라는 커스텀 클래스를 만들어 각 요청 처리 시간을 기록하고, 응답 헤더에 `X-Response-Time`을 추가할 수 있습니다.

```python
fro
- **k010** (0.00): 엔드포인트에서 사용자가 파일을 다운로드하게 하려면 어떻게 하나요?
  > 죄송하지만, 주어진 문맥에서는 파일 다운로드를 위한 구체적인 방법을 설명하지 않습니다.
- **k013** (0.00): 문서 페이지에서 엔드포인트를 섹션별로 묶으려면 어떻게 하나요?
  > 문서에 해당 정보가 없습니다.
- **k015** (0.00): 요청의 이메일 필드가 정말 이메일 형식인지 확인하려면 어떻게 하나요?
  > 이메일 형식을 검증하려면 `regex` 패턴을 사용하여 `pattern` 검증기를 활용해야 합니다. 예를 들어, 다음과 같이 `email` 필드를 정의할 수 있습니다:

```python
from fastapi import FastAPI, HTTPException, Form
from typing import Optional
import re

app = F
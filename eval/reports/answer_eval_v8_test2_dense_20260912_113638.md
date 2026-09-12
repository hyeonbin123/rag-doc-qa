# Answer eval report (v8_test2_dense)

- date: 2026-09-12T11:36:38.743380+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- top_k: 5
- retrieval mode: dense
- dataset: qa_test2.jsonl
- questions: 43
- judge skipped: False

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Hallucinated |
|---|---|---|---|
| 0.74 | 3.86 | 4.19 | 0/43 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated |
|---|---|---|---|---|
| t001 | 0.00 | 3 | 3 | False |
| t002 | 1.00 | 4 | 5 | False |
| t003 | 1.00 | 4 | 4 | False |
| t004 | 0.00 | 5 | 5 | False |
| t005 | 1.00 | 4 | 5 | False |
| t006 | 0.00 | 4 | 4 | False |
| t007 | 1.00 | 4 | 5 | False |
| t008 | 0.00 | 3 | 3 | False |
| t009 | 0.00 | 3 | 2 | False |
| t010 | 0.00 | 3 | 2 | False |
| t011 | 1.00 | 4 | 5 | False |
| t012 | 1.00 | 4 | 4 | False |
| t013 | 1.00 | 4 | 4 | False |
| t014 | 1.00 | 4 | 5 | False |
| t015 | 1.00 | 4 | 5 | False |
| t016 | 1.00 | 4 | 4 | False |
| t017 | 1.00 | 4 | 4 | False |
| t018 | 1.00 | 4 | 4 | False |
| t019 | 1.00 | 4 | 4 | False |
| t020 | 1.00 | 4 | 5 | False |
| t021 | 1.00 | 4 | 4 | False |
| t022 | 0.00 | 4 | 5 | False |
| t023 | 1.00 | 5 | 5 | False |
| t024 | 1.00 | 4 | 5 | False |
| t025 | 0.00 | 4 | 5 | False |
| t026 | 1.00 | 4 | 5 | False |
| t027 | 1.00 | 4 | 5 | False |
| t028 | 1.00 | 4 | 4 | False |
| t029 | 1.00 | 4 | 5 | False |
| t030 | 0.00 | 3 | 2 | False |
| t031 | 1.00 | 5 | 5 | False |
| t032 | 1.00 | 4 | 5 | False |
| t033 | 1.00 | 4 | 5 | False |
| t034 | 1.00 | 4 | 5 | False |
| t035 | 0.00 | 3 | 3 | False |
| t036 | 1.00 | 3 | 2 | False |
| t037 | 1.00 | 4 | 5 | False |
| t038 | 1.00 | 4 | 4 | False |
| t039 | 1.00 | 4 | 4 | False |
| t040 | 1.00 | 4 | 5 | False |
| t041 | 1.00 | 4 | 5 | False |
| t042 | 1.00 | 3 | 3 | False |
| t043 | 0.00 | 3 | 2 | False |

## Worst questions (lowest keyword coverage)

- **t001** (0.00): My React app on localhost:3000 gets blocked when it calls my API on port 8000. How do I fix it?
  > _CONTEXT PASSAGE_ 1에서 설명된 것처럼, 프록시가 경로 프리픽스 `/api/v1`을 사용하여 FastAPI 애플리케이션에 요청을 전달하는 경우, React 애플리케이션은 API 호출 시 해당 경로 프리픽스를 고려해야 합니다. 따라서 React 애플리케이션에서 API 호출 URL을 다음과 같이 수정해야 합니다:

```
http://127.0.
- **t004** (0.00): How do I give a field in my request JSON a default value so clients can leave it out?
  > 필드에 기본값을 줘 클라이언트가 생략할 수 있게 하려면, 해당 필드에 `None`을 기본값으로 지정하면 됩니다. 예를 들어, 다음과 같이 모델을 정의할 수 있습니다:

```python
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
```

위의
- **t006** (0.00): How do I protect an endpoint so only logged-in users can call it?
  > OAuth2PasswordBearer를 사용하여 인증된 사용자만 접근할 수 있는 엔드포인트를 만들 수 있습니다. `OAuth2PasswordBearer`를 `Depends`와 함께 사용하여 요청에 대한 인증을 수행할 수 있습니다. 이렇게 하면 FastAPI는 해당 경로 작업 함수에 대한 보안 스키마를 정의할 수 있습니다. 이렇게 하면 사용자가 토큰을 제공했
- **t008** (0.00): How can I log how long every request takes?
  > 문서에 직접적인 방법은 언급되어 있지 않습니다. 그러나 `Request` 객체를 직접 사용하여 요청 시간을 측정할 수 있습니다. 이를 위해 `Request` 객체의 `start_time` 속성을 사용하여 요청 시작 시간을 기록하고, 요청 처리 후 요청 종료 시간을 기록한 후 두 시간을 비교하여 요청 시간을 계산할 수 있습니다. 이렇게 하면 요청 시간을 로그
- **t009** (0.00): How can I stream a large file to the client instead of loading it all into memory?
  > UploadFile을 사용하여 대형 파일을 스트리밍할 수 있습니다. UploadFile은 파일을 메모리에 최대 크기까지 저장한 후 이를 넘어서는 경우 디스크에 저장하므로, 메모리 사용을 최소화할 수 있습니다. 따라서 UploadFile을 파일 파라미터의 타입으로 지정하면, FastAPI가 파일을 대신 읽어 들여 bytes로 제공합니다.
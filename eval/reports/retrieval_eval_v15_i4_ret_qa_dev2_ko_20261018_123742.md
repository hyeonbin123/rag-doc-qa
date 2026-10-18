# Retrieval eval report (v15_i4_ret_qa_dev2_ko)

- date: 2026-10-18T12:37:28.730799+00:00
- embedding models: en BAAI/bge-small-en-v1.5, ko ibm-granite/granite-embedding-311m-multilingual-r2
- database: ragdb
- top_k: 10
- retrieval mode: dense
- search: as planned; dense plan: ko Sort > Seq Scan on chunks c > Seq Scan on documents d
- score floor: ko 0.0
- stored vectors checked: ko chunks vs ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384 (min cosine 1.0)
- dataset: qa_dev2_ko.jsonl
- questions: 40
- hit: a chunk of an expected page, in any translation
- short: questions with fewer than 5 results (the score floor cut the rest)
- latency: retrieval only (after the query embedding), this machine's CPU

## Aggregate metrics

| set | questions | Hit@3 | Hit@5 | Hit@10 | MRR | short | latency p50 (ms) | latency p95 (ms) |
|---|---|---|---|---|---|---|---|---|
| all | 40 | 0.95 | 0.97 | 0.97 | 0.915 | 0 | 7 | 8 |

## Per-question

| id | hit@3 | hit@5 | hit@10 | RR | results | ms | question |
|---|---|---|---|---|---|---|---|
| n001 | True | True | True | 1.00 | 10 | 9 | FastAPI에서 경로 매개변수를 정수 타입으로 받으려면 어떻게 선언해야 하나요? |
| n005 | True | True | True | 1.00 | 10 | 8 | 경로 매개변수 안에 슬래시가 들어간 파일 경로를 통째로 받을 수 있나요? |
| n006 | True | True | True | 1.00 | 10 | 7 | 쿼리 파라미터로 같은 키를 여러 번 보내서 리스트로 받으려면 어떻게 해? |
| n009 | True | True | True | 1.00 | 10 | 7 | 더 이상 안 쓰는 쿼리 파라미터를 문서에서 deprecated로 표시하려면? |
| n011 | True | True | True | 1.00 | 10 | 7 | bool 타입 쿼리 파라미터에 yes, on, 1 같은 값을 넣어도 true로 인식되나요? |
| n012 | True | True | True | 1.00 | 10 | 7 | Pydantic BaseModel로 POST 요청 본문 받는 가장 기본적인 예제 보여주세요. |
| n015 | False | False | False | 0.00 | 10 | 7 | 요청 본문에 Pydantic 모델 두 개를 동시에 받을 수 있어? |
| n018 | True | True | True | 1.00 | 10 | 7 | Swagger 문서에 요청 바디 예시를 여러 개 보여주고 싶은데 가능할까요? |
| n031 | True | True | True | 0.50 | 10 | 7 | 쿠키 값을 경로 함수 파라미터로 받는 방법 |
| n041 | True | True | True | 1.00 | 10 | 7 | 반환값은 필요 없고 실행만 되면 되는 의존성은 데코레이터 쪽에 넣을 수 있다던데 어떻게 하나요? |
| n044 | True | True | True | 1.00 | 10 | 7 | yield 의존성에서 예외가 발생하면 except로 잡을 수 있나요? 거기서 HTTPException을 다시 던져도 되나? |
| n049 | True | True | True | 1.00 | 10 | 8 | 비밀번호 해싱은 뭘로 해야 돼? passlib, bcrypt, argon2 중에 뭐가 나아? |
| n053 | True | True | True | 1.00 | 10 | 7 | HTTP Basic 인증은 어떻게 구현하나요? 사용자 이름 비교할 때 타이밍 공격도 막아야 한다던데요. |
| n058 | True | True | True | 1.00 | 10 | 7 | 미들웨어를 직접 만들어서 모든 요청의 처리 시간을 응답 헤더에 넣고 싶어요. |
| n059 | True | True | True | 1.00 | 10 | 7 | 프론트엔드가 localhost:3000에서 돌아가는데 CORS 에러가 나요. 어떻게 설정해야 하나요? |
| n063 | True | True | True | 1.00 | 10 | 8 | BackgroundTasks로 응답을 먼저 보내고 나서 이메일 전송 같은 작업을 실행하는 방법 |
| n066 | True | True | True | 1.00 | 10 | 7 | TestClient로 엔드포인트를 테스트하는 기본 방법 알려주세요. |
| n068 | True | True | True | 1.00 | 10 | 7 | 테스트 중에도 startup/shutdown 이벤트나 lifespan이 실행되게 하려면? |
| n069 | True | True | True | 1.00 | 10 | 7 | 테스트용 DB를 운영 DB와 분리해서 쓰고 싶은데 어떻게 구성하는 게 좋을까요? |
| n073 | True | True | True | 1.00 | 10 | 7 | requests나 동기 DB 드라이버 같은 동기 라이브러리를 async def 경로 함수 안에서 써도 되나? |
| n074 | True | True | True | 1.00 | 10 | 7 | 경로 함수를 async def 말고 그냥 def로 선언하면 스레드풀에서 돌아간다는데 맞습니까? |
| n076 | True | True | True | 1.00 | 10 | 7 | 앱 시작할 때 ML 모델을 메모리에 올리고 종료할 때 정리하려면 lifespan을 어떻게 써야 하나요? |
| n080 | False | True | True | 0.25 | 10 | 7 | 라우터 전체에 공통 응답으로 404 같은 걸 문서에 추가할 수 있나요? |
| n084 | True | True | True | 0.50 | 10 | 7 | JSON 말고 HTMLResponse, PlainTextResponse, RedirectResponse 같은 걸 반환하려면? |
| n087 | True | True | True | 1.00 | 10 | 7 | Response 객체를 직접 반환하면 response_model 검증이나 필터링도 적용되나? |
| n088 | True | True | True | 1.00 | 10 | 7 | jsonable_encoder는 언제 써야 하나요? datetime 들어간 모델을 dict로 바꿀 때? |
| n089 | True | True | True | 1.00 | 10 | 7 | PATCH로 부분 업데이트를 구현할 때 보내지 않은 필드는 기존 값을 유지하게 하려면? |
| n090 | True | True | True | 1.00 | 10 | 7 | 같은 엔드포인트에서 상황에 따라 상태 코드를 다르게 돌려주고 싶을 때 어떻게 해요? |
| n092 | True | True | True | 1.00 | 10 | 7 | WebSocket 엔드포인트 만드는 방법이랑 클라이언트 연결이 끊겼을 때 처리하는 법 |
| n094 | True | True | True | 1.00 | 10 | 7 | WebSocket 연결에서도 Depends나 쿼리 파라미터, 쿠키로 인증할 수 있나요? |
| n098 | True | True | True | 0.33 | 10 | 7 | 테스트할 때만 설정 값을 다르게 오버라이드하려면 어떻게 해야 하나요? |
| n100 | True | True | True | 1.00 | 10 | 7 | OpenAPI 문서에 API 제목, 버전, 설명이랑 태그별 설명을 넣는 방법 |
| n102 | True | True | True | 1.00 | 10 | 8 | 프론트엔드 클라이언트 코드 자동 생성할 때 함수 이름이 지저분한데, operation_id를 깔끔하게 지정하는 방법이 있나요? |
| n103 | True | True | True | 1.00 | 10 | 8 | 인터넷이 안 되는 사내망이라 Swagger UI가 CDN에서 안 불러와져요. 오프라인에서 문서 보는 방법은? |
| n107 | True | True | True | 1.00 | 10 | 7 | uvicorn 워커를 여러 개 띄우려면 어떻게 해? gunicorn이랑 같이 써야 하나요? |
| n110 | True | True | True | 1.00 | 10 | 7 | 프록시 뒤에서 HTTPS로 서비스하는데 리다이렉트 URL이 http로 만들어지는 문제는 어떻게 해결하나요? |
| n114 | True | True | True | 1.00 | 10 | 7 | 커스텀 APIRoute 클래스를 만들어서 요청 바디를 로깅하거나 gzip 압축된 요청을 처리할 수 있나요? |
| n117 | True | True | True | 1.00 | 10 | 7 | 헤더나 쿠키도 Pydantic 모델 하나로 한꺼번에 선언할 수 있을까요? |
| n118 | True | True | True | 1.00 | 10 | 8 | FastAPI에서 GraphQL을 쓰고 싶은데 어떤 라이브러리를 쓰면 되나요? |
| n119 | True | True | True | 1.00 | 10 | 7 | Pydantic v1에서 v2로 올릴 때 FastAPI 코드에서 주의할 점이 뭐가 있어? |
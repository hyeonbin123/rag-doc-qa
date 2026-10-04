# Retrieval eval report (v12_dev_e5s)

- date: 2026-10-04T04:52:19.140050+00:00
- embedding models: en BAAI/bge-small-en-v1.5, ko intfloat/multilingual-e5-small
- database: ragdb_p1_e5s
- top_k: 10
- retrieval mode: dense
- search: as planned; dense plan: ko Sort > Seq Scan on chunks c > Seq Scan on documents d
- score floor: ko 0.3
- stored vectors checked: ko chunks vs intfloat/multilingual-e5-small (min cosine 1.0)
- dataset: qa_dev_ko.jsonl, qa_dev2_ko.jsonl
- questions: 72
- hit: a chunk of an expected page, in any translation
- short: questions with fewer than 5 results (the score floor cut the rest)
- latency: retrieval only (after the query embedding), this machine's CPU

## Aggregate metrics

| set | questions | Hit@3 | Hit@5 | Hit@10 | MRR | short | latency p50 (ms) | latency p95 (ms) |
|---|---|---|---|---|---|---|---|---|
| all | 72 | 0.83 | 0.88 | 0.94 | 0.816 | 0 | 6 | 7 |
| qa_dev_ko.jsonl | 32 | 0.81 | 0.84 | 0.94 | 0.766 | 0 | 6 | 7 |
| qa_dev2_ko.jsonl | 40 | 0.85 | 0.90 | 0.95 | 0.856 | 0 | 6 | 7 |

## Per-question

| id | hit@3 | hit@5 | hit@10 | RR | results | ms | question |
|---|---|---|---|---|---|---|---|
| kd001 | True | True | True | 1.00 | 10 | 8 | 경로 처리 함수에서 클라이언트가 보낸 쿠키 값을 읽으려면 어떻게 하나요? |
| kd002 | True | True | True | 1.00 | 10 | 7 | FastAPI가 돌려보내는 응답에 쿠키를 설정하려면 어떻게 하나요? |
| kd003 | True | True | True | 1.00 | 10 | 6 | Response 객체를 직접 반환하지 않고 응답에 사용자 정의 헤더를 추가하려면 어떻게 하나요? |
| kd004 | True | True | True | 1.00 | 10 | 5 | 경로 처리가 반환하는 데이터의 타입을 선언해서 FastAPI가 검증하고 걸러 내게 하려면 어떻게 하나요? |
| kd005 | True | True | True | 0.50 | 10 | 6 | 경로 처리 데코레이터의 status_code 매개변수에는 어떤 값을 넣을 수 있나요? |
| kd006 | True | True | True | 0.33 | 10 | 7 | 요청에서 JSON 대신 폼 필드를 받으려면 어떻게 하나요? |
| kd007 | False | False | True | 0.14 | 10 | 7 | 이미지나 CSS 같은 파일을 디렉터리에서 그대로 서빙하려면 어떻게 하나요? |
| kd008 | False | False | False | 0.00 | 10 | 7 | 저장된 항목에서 클라이언트가 실제로 보낸 필드만 수정하고 나머지는 그대로 두려면 어떻게 하나요? |
| kd009 | True | True | True | 1.00 | 10 | 6 | 요청 본문에 리스트 필드나 다른 Pydantic 모델을 중첩해서 선언하려면 어떻게 하나요? |
| kd010 | True | True | True | 1.00 | 10 | 7 | 의존성을 선언할 때 use_cache=False는 무슨 역할을 하나요? |
| kd011 | True | True | True | 1.00 | 10 | 6 | 애플리케이션 전체의 모든 경로 처리에 의존성을 적용하려면 어떻게 하나요? |
| kd012 | True | True | True | 1.00 | 10 | 6 | 경로 처리 안에서 현재 로그인한 사용자의 객체를 가져오려면 어떻게 하나요? |
| kd013 | False | False | True | 0.11 | 10 | 7 | 경로 처리 데코레이터의 deprecated 매개변수는 무엇을 하나요? |
| kd014 | True | True | True | 1.00 | 10 | 6 | jsonable_encoder는 어디에 쓰나요? |
| kd015 | True | True | True | 1.00 | 10 | 6 | VS Code나 PyCharm 같은 에디터의 디버거로 앱을 실행하려면 어떻게 하나요? |
| kd016 | True | True | True | 0.50 | 10 | 6 | 대화형 API 문서에 요청 데이터 예시를 보여 주려면 어떻게 하나요? |
| kd017 | True | True | True | 0.50 | 10 | 7 | OAuth2 표준에 따라 클라이언트에게 항목 읽기만 허용하는 식의 세분화된 권한을 주려면 어떻게 하나요? |
| kd018 | False | False | True | 0.17 | 10 | 6 | 경로 처리에서 JSON 대신 HTML 페이지를 반환하려면 어떻게 하나요? |
| kd019 | False | False | False | 0.00 | 10 | 5 | 하나의 경로 처리가 항목을 수정할 때는 200을, 새로 만들 때는 201을 반환하게 하려면 어떻게 하나요? |
| kd020 | True | True | True | 1.00 | 10 | 6 | 자체 문서를 가진 완전히 독립적인 FastAPI 앱을 메인 앱의 특정 경로 아래에 추가하려면 어떻게 하나요? |
| kd021 | True | True | True | 1.00 | 10 | 6 | 경로 처리에서 Jinja2 템플릿을 렌더링하려면 어떻게 하나요? |
| kd022 | True | True | True | 1.00 | 10 | 6 | WSGIMiddleware는 어디에 쓰나요? |
| kd023 | True | True | True | 1.00 | 10 | 6 | 테스트 안에서 비동기 데이터베이스를 확인하는 것처럼 비동기 테스트 함수를 작성하려면 어떻게 하나요? |
| kd024 | True | True | True | 1.00 | 10 | 6 | 환경 변수란 무엇이고 어디에 있나요? |
| kd025 | True | True | True | 1.00 | 10 | 6 | 파이썬 프로젝트마다 설치된 패키지를 따로 격리해 둬야 하는 이유는 무엇인가요? |
| kd026 | True | True | True | 1.00 | 10 | 7 | API를 배포할 때 재시작, 복제, 메모리 같은 것들은 무엇을 고려해야 하나요? |
| kd027 | True | True | True | 1.00 | 10 | 7 | 운영 환경에서 FastAPI 애플리케이션을 서빙하려면 어떤 명령을 써야 하나요? |
| kd028 | True | True | True | 1.00 | 10 | 6 | fastapi dev 명령은 무엇을 하나요? |
| kd029 | False | True | True | 0.25 | 10 | 6 | 설정을 이용해서 운영 환경에서는 OpenAPI 스키마와 문서를 끄려면 어떻게 하나요? |
| kd030 | True | True | True | 1.00 | 10 | 6 | FastAPI에서 GraphQL을 쓸 수 있나요? 어떤 라이브러리가 함께 동작하나요? |
| kd031 | True | True | True | 1.00 | 10 | 6 | 어떤 이벤트가 생기면 우리 API가 사용자의 시스템으로 요청을 보낸다는 것을 문서화하려면 어떻게 하나요? |
| kd032 | True | True | True | 1.00 | 10 | 6 | FastAPI 백엔드용 TypeScript 클라이언트를 생성하려면 어떻게 하나요? |
| n001 | True | True | True | 1.00 | 10 | 6 | FastAPI에서 경로 매개변수를 정수 타입으로 받으려면 어떻게 선언해야 하나요? |
| n005 | True | True | True | 1.00 | 10 | 6 | 경로 매개변수 안에 슬래시가 들어간 파일 경로를 통째로 받을 수 있나요? |
| n006 | True | True | True | 0.50 | 10 | 6 | 쿼리 파라미터로 같은 키를 여러 번 보내서 리스트로 받으려면 어떻게 해? |
| n009 | False | False | True | 0.14 | 10 | 6 | 더 이상 안 쓰는 쿼리 파라미터를 문서에서 deprecated로 표시하려면? |
| n011 | True | True | True | 1.00 | 10 | 6 | bool 타입 쿼리 파라미터에 yes, on, 1 같은 값을 넣어도 true로 인식되나요? |
| n012 | True | True | True | 1.00 | 10 | 6 | Pydantic BaseModel로 POST 요청 본문 받는 가장 기본적인 예제 보여주세요. |
| n015 | False | False | False | 0.00 | 10 | 6 | 요청 본문에 Pydantic 모델 두 개를 동시에 받을 수 있어? |
| n018 | True | True | True | 1.00 | 10 | 6 | Swagger 문서에 요청 바디 예시를 여러 개 보여주고 싶은데 가능할까요? |
| n031 | True | True | True | 1.00 | 10 | 6 | 쿠키 값을 경로 함수 파라미터로 받는 방법 |
| n041 | True | True | True | 1.00 | 10 | 6 | 반환값은 필요 없고 실행만 되면 되는 의존성은 데코레이터 쪽에 넣을 수 있다던데 어떻게 하나요? |
| n044 | True | True | True | 1.00 | 10 | 7 | yield 의존성에서 예외가 발생하면 except로 잡을 수 있나요? 거기서 HTTPException을 다시 던져도 되나? |
| n049 | True | True | True | 1.00 | 10 | 6 | 비밀번호 해싱은 뭘로 해야 돼? passlib, bcrypt, argon2 중에 뭐가 나아? |
| n053 | True | True | True | 1.00 | 10 | 6 | HTTP Basic 인증은 어떻게 구현하나요? 사용자 이름 비교할 때 타이밍 공격도 막아야 한다던데요. |
| n058 | True | True | True | 1.00 | 10 | 5 | 미들웨어를 직접 만들어서 모든 요청의 처리 시간을 응답 헤더에 넣고 싶어요. |
| n059 | True | True | True | 1.00 | 10 | 6 | 프론트엔드가 localhost:3000에서 돌아가는데 CORS 에러가 나요. 어떻게 설정해야 하나요? |
| n063 | True | True | True | 1.00 | 10 | 6 | BackgroundTasks로 응답을 먼저 보내고 나서 이메일 전송 같은 작업을 실행하는 방법 |
| n066 | True | True | True | 1.00 | 10 | 6 | TestClient로 엔드포인트를 테스트하는 기본 방법 알려주세요. |
| n068 | True | True | True | 1.00 | 10 | 6 | 테스트 중에도 startup/shutdown 이벤트나 lifespan이 실행되게 하려면? |
| n069 | False | False | False | 0.00 | 10 | 7 | 테스트용 DB를 운영 DB와 분리해서 쓰고 싶은데 어떻게 구성하는 게 좋을까요? |
| n073 | True | True | True | 1.00 | 10 | 6 | requests나 동기 DB 드라이버 같은 동기 라이브러리를 async def 경로 함수 안에서 써도 되나? |
| n074 | True | True | True | 1.00 | 10 | 6 | 경로 함수를 async def 말고 그냥 def로 선언하면 스레드풀에서 돌아간다는데 맞습니까? |
| n076 | True | True | True | 1.00 | 10 | 6 | 앱 시작할 때 ML 모델을 메모리에 올리고 종료할 때 정리하려면 lifespan을 어떻게 써야 하나요? |
| n080 | False | True | True | 0.25 | 10 | 6 | 라우터 전체에 공통 응답으로 404 같은 걸 문서에 추가할 수 있나요? |
| n084 | True | True | True | 1.00 | 10 | 6 | JSON 말고 HTMLResponse, PlainTextResponse, RedirectResponse 같은 걸 반환하려면? |
| n087 | True | True | True | 1.00 | 10 | 6 | Response 객체를 직접 반환하면 response_model 검증이나 필터링도 적용되나? |
| n088 | True | True | True | 1.00 | 10 | 6 | jsonable_encoder는 언제 써야 하나요? datetime 들어간 모델을 dict로 바꿀 때? |
| n089 | True | True | True | 1.00 | 10 | 6 | PATCH로 부분 업데이트를 구현할 때 보내지 않은 필드는 기존 값을 유지하게 하려면? |
| n090 | False | False | True | 0.17 | 10 | 6 | 같은 엔드포인트에서 상황에 따라 상태 코드를 다르게 돌려주고 싶을 때 어떻게 해요? |
| n092 | True | True | True | 1.00 | 10 | 6 | WebSocket 엔드포인트 만드는 방법이랑 클라이언트 연결이 끊겼을 때 처리하는 법 |
| n094 | True | True | True | 1.00 | 10 | 6 | WebSocket 연결에서도 Depends나 쿼리 파라미터, 쿠키로 인증할 수 있나요? |
| n098 | False | True | True | 0.20 | 10 | 6 | 테스트할 때만 설정 값을 다르게 오버라이드하려면 어떻게 해야 하나요? |
| n100 | True | True | True | 1.00 | 10 | 7 | OpenAPI 문서에 API 제목, 버전, 설명이랑 태그별 설명을 넣는 방법 |
| n102 | True | True | True | 1.00 | 10 | 6 | 프론트엔드 클라이언트 코드 자동 생성할 때 함수 이름이 지저분한데, operation_id를 깔끔하게 지정하는 방법이 있나요? |
| n103 | True | True | True | 1.00 | 10 | 6 | 인터넷이 안 되는 사내망이라 Swagger UI가 CDN에서 안 불러와져요. 오프라인에서 문서 보는 방법은? |
| n107 | True | True | True | 1.00 | 10 | 7 | uvicorn 워커를 여러 개 띄우려면 어떻게 해? gunicorn이랑 같이 써야 하나요? |
| n110 | True | True | True | 1.00 | 10 | 6 | 프록시 뒤에서 HTTPS로 서비스하는데 리다이렉트 URL이 http로 만들어지는 문제는 어떻게 해결하나요? |
| n114 | True | True | True | 1.00 | 10 | 6 | 커스텀 APIRoute 클래스를 만들어서 요청 바디를 로깅하거나 gzip 압축된 요청을 처리할 수 있나요? |
| n117 | True | True | True | 1.00 | 10 | 6 | 헤더나 쿠키도 Pydantic 모델 하나로 한꺼번에 선언할 수 있을까요? |
| n118 | True | True | True | 1.00 | 10 | 6 | FastAPI에서 GraphQL을 쓰고 싶은데 어떤 라이브러리를 쓰면 되나요? |
| n119 | True | True | True | 1.00 | 10 | 6 | Pydantic v1에서 v2로 올릴 때 FastAPI 코드에서 주의할 점이 뭐가 있어? |
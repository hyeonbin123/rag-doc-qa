# Retrieval eval report (v12_test3a_b0)

- date: 2026-10-04T04:57:23.205205+00:00
- embedding models: en BAAI/bge-small-en-v1.5, ko intfloat/multilingual-e5-small
- database: ragdb_p1_e5s
- top_k: 10
- retrieval mode: dense
- search: as planned; dense plan: ko Sort > Seq Scan on chunks c > Seq Scan on documents d
- score floor: ko 0.3
- stored vectors checked: ko chunks vs intfloat/multilingual-e5-small (min cosine 1.0)
- dataset: qa_test3a_ko.jsonl
- questions: 40
- hit: a chunk of an expected page, in any translation
- short: questions with fewer than 5 results (the score floor cut the rest)
- latency: retrieval only (after the query embedding), this machine's CPU

## Aggregate metrics

| set | questions | Hit@3 | Hit@5 | Hit@10 | MRR | short | latency p50 (ms) | latency p95 (ms) |
|---|---|---|---|---|---|---|---|---|
| all | 40 | 0.85 | 0.90 | 0.97 | 0.806 | 0 | 7 | 8 |

## Per-question

| id | hit@3 | hit@5 | hit@10 | RR | results | ms | question |
|---|---|---|---|---|---|---|---|
| n002 | False | True | True | 0.20 | 10 | 9 | 쿼리 파라미터를 선택값으로 만들고 기본값을 None으로 주는 방법이 궁금합니다. |
| n003 | True | True | True | 1.00 | 10 | 6 | /users/me랑 /users/{user_id} 둘 다 있는데 me가 user_id로 잡혀버려요. 정의 순서 문제인가요? |
| n004 | True | True | True | 1.00 | 10 | 7 | 경로 파라미터에 미리 정해진 몇 가지 값만 허용하고 싶은데 Enum을 쓰면 되나요? |
| n014 | True | True | True | 1.00 | 10 | 7 | 바디 모델이 하나뿐인데도 {"item": {...}}처럼 키로 감싼 JSON을 받고 싶어요. 방법이 있나요? |
| n016 | True | True | True | 0.50 | 10 | 7 | 모델 필드에 Field로 설명이나 예시 값, 최대 길이 같은 제약을 붙이는 방법 |
| n021 | False | False | True | 0.12 | 10 | 7 | 입력용 모델, 출력용 모델, DB용 모델을 따로 나누라고 하던데 이유가 뭐야? |
| n022 | True | True | True | 1.00 | 10 | 7 | 반환 타입 어노테이션이랑 response_model을 둘 다 지정하면 뭐가 우선 적용돼? |
| n024 | True | True | True | 1.00 | 10 | 7 | POST 요청 성공 시 기본 상태 코드를 200 말고 201 Created로 바꾸려면? |
| n026 | True | True | True | 1.00 | 10 | 7 | 파일 업로드할 때 bytes로 받는 것과 UploadFile로 받는 것의 차이가 뭔가요? |
| n033 | True | True | True | 1.00 | 10 | 7 | HTTPException으로 404 에러를 던지면서 detail 메시지를 넣는 방법이 궁금합니다. |
| n037 | True | True | True | 1.00 | 10 | 7 | Depends를 이용한 의존성 주입이 정확히 뭐고 언제 쓰면 좋습니까? |
| n038 | True | True | True | 1.00 | 10 | 7 | 클래스를 의존성으로 쓸 수 있나요? 함수 의존성이랑 뭐가 다른가요? |
| n040 | True | True | True | 0.50 | 10 | 7 | 같은 의존성이 한 요청 안에서 여러 번 쓰이면 매번 호출되나요, 아니면 캐시되나요? |
| n042 | True | True | True | 1.00 | 10 | 7 | 앱의 모든 경로에 공통으로 적용되는 전역 의존성을 설정하려면? |
| n043 | True | True | True | 0.33 | 10 | 7 | yield를 쓰는 의존성으로 DB 세션을 열고 요청이 끝나면 닫는 패턴 알려주세요. |
| n045 | True | True | True | 0.50 | 10 | 7 | Annotated로 의존성 타입 별칭을 만들어서 여러 엔드포인트에 재사용하는 방식이 권장되나요? |
| n046 | True | True | True | 1.00 | 10 | 7 | 테스트할 때 실제 의존성 대신 가짜 의존성으로 바꿔치기하는 방법 |
| n052 | True | True | True | 1.00 | 10 | 7 | OAuth2 scopes로 권한별 접근 제어를 하는 방법 |
| n056 | True | True | True | 1.00 | 10 | 7 | 액세스 토큰 만료 시간을 설정하고 만료된 토큰이 오면 401을 돌려주려면? |
| n057 | True | True | True | 1.00 | 10 | 7 | 인증 실패로 401 응답할 때 WWW-Authenticate 헤더를 꼭 넣어야 하나요? |
| n060 | True | True | True | 0.50 | 10 | 8 | allow_origins를 "*"로 하면 쿠키나 인증 정보(credentials) 허용이 안 된다는 게 왜 그런가요? |
| n062 | False | True | True | 0.25 | 10 | 7 | 미들웨어랑 yield 의존성의 실행 순서는 어떻게 됩니까? |
| n064 | True | True | True | 1.00 | 10 | 7 | 백그라운드 작업이 무겁고 오래 걸리면 BackgroundTasks 말고 Celery 같은 걸 써야 하나요? |
| n065 | True | True | True | 1.00 | 10 | 7 | 의존성 함수 안에서도 BackgroundTasks를 받아서 작업을 추가할 수 있어? |
| n070 | True | True | True | 1.00 | 10 | 8 | SQL 데이터베이스를 붙일 때 SQLModel을 쓰는 예제가 있나요? |
| n071 | True | True | True | 1.00 | 10 | 7 | SQLAlchemy 세션을 요청마다 열고 닫으려면 어떻게 해야 하죠? |
| n072 | True | True | True | 1.00 | 10 | 7 | async def 안에서 time.sleep 같은 블로킹 코드를 쓰면 서버 전체가 멈추나요? |
| n075 | True | True | True | 1.00 | 10 | 7 | 동시성(concurrency)과 병렬성(parallelism)의 차이를 FastAPI 관점에서 설명해 주세요. |
| n078 | True | True | True | 1.00 | 10 | 7 | 프로젝트가 커져서 파일 하나에 다 못 넣겠어요. APIRouter로 나누는 방법 알려주세요. |
| n079 | True | True | True | 1.00 | 10 | 7 | include_router 할 때 prefix, tags, dependencies를 한꺼번에 지정할 수 있나요? |
| n081 | False | False | True | 0.17 | 10 | 7 | 하위 애플리케이션을 mount하는 건 APIRouter로 include하는 거랑 뭐가 달라? |
| n082 | False | False | True | 0.17 | 10 | 7 | 정적 파일(css, js, 이미지) 서빙은 어떻게 하나요? |
| n085 | True | True | True | 1.00 | 10 | 8 | 큰 파일을 StreamingResponse로 스트리밍하거나 FileResponse로 다운로드시키는 방법이 궁금해요. |
| n093 | True | True | True | 1.00 | 10 | 8 | 여러 WebSocket 클라이언트에게 메시지를 브로드캐스트하는 간단한 채팅 예제가 있을까요? |
| n095 | True | True | True | 1.00 | 10 | 7 | 환경 변수로 설정 값을 관리하려면 pydantic-settings의 BaseSettings를 쓰면 되나요? |
| n101 | False | False | False | 0.00 | 10 | 7 | 특정 엔드포인트를 OpenAPI 스키마에서 숨기고 싶어요. |
| n104 | True | True | True | 1.00 | 10 | 7 | 자동 생성되는 OpenAPI 스키마를 직접 수정할 수 있나요? 예를 들어 로고 추가 같은 거요. |
| n108 | True | True | True | 1.00 | 10 | 8 | 쿠버네티스에서는 컨테이너 하나에 프로세스 하나만 두라고 하던데 왜 그런가요? |
| n109 | True | True | True | 1.00 | 10 | 7 | Nginx나 Traefik 같은 리버스 프록시 뒤에서 경로 prefix가 붙을 때 root_path를 설정해야 하나요? |
| n111 | True | True | True | 1.00 | 10 | 8 | fastapi dev 명령이랑 fastapi run 명령의 차이가 뭔가요? |
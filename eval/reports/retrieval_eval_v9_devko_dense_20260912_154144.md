# Retrieval eval report (v9_devko_dense)

- date: 2026-09-12T15:41:44.857132+00:00
- embedding models: en BAAI/bge-small-en-v1.5, ko intfloat/multilingual-e5-small
- database: ragdb
- top_k: 10
- retrieval mode: dense
- dataset: qa_dev_ko.jsonl
- questions: 32
- latency: retrieval only (after the query embedding), this machine's CPU

## Aggregate metrics

| Hit@3 | Hit@5 | Hit@10 | MRR | latency p50 (ms) | latency p95 (ms) |
|---|---|---|---|---|---|
| 0.81 | 0.84 | 0.94 | 0.766 | 7 | 33 |

## Per-question

| id | hit@3 | hit@5 | hit@10 | RR | ms | question |
|---|---|---|---|---|---|---|
| kd001 | True | True | True | 1.00 | 80 | 경로 처리 함수에서 클라이언트가 보낸 쿠키 값을 읽으려면 어떻게 하나요? |
| kd002 | True | True | True | 1.00 | 7 | FastAPI가 돌려보내는 응답에 쿠키를 설정하려면 어떻게 하나요? |
| kd003 | True | True | True | 1.00 | 6 | Response 객체를 직접 반환하지 않고 응답에 사용자 정의 헤더를 추가하려면 어떻게 하나요? |
| kd004 | True | True | True | 1.00 | 7 | 경로 처리가 반환하는 데이터의 타입을 선언해서 FastAPI가 검증하고 걸러 내게 하려면 어떻게 하나요? |
| kd005 | True | True | True | 0.50 | 8 | 경로 처리 데코레이터의 status_code 매개변수에는 어떤 값을 넣을 수 있나요? |
| kd006 | True | True | True | 0.33 | 7 | 요청에서 JSON 대신 폼 필드를 받으려면 어떻게 하나요? |
| kd007 | False | False | True | 0.14 | 6 | 이미지나 CSS 같은 파일을 디렉터리에서 그대로 서빙하려면 어떻게 하나요? |
| kd008 | False | False | False | 0.00 | 6 | 저장된 항목에서 클라이언트가 실제로 보낸 필드만 수정하고 나머지는 그대로 두려면 어떻게 하나요? |
| kd009 | True | True | True | 1.00 | 6 | 요청 본문에 리스트 필드나 다른 Pydantic 모델을 중첩해서 선언하려면 어떻게 하나요? |
| kd010 | True | True | True | 1.00 | 7 | 의존성을 선언할 때 use_cache=False는 무슨 역할을 하나요? |
| kd011 | True | True | True | 1.00 | 7 | 애플리케이션 전체의 모든 경로 처리에 의존성을 적용하려면 어떻게 하나요? |
| kd012 | True | True | True | 1.00 | 6 | 경로 처리 안에서 현재 로그인한 사용자의 객체를 가져오려면 어떻게 하나요? |
| kd013 | False | False | True | 0.11 | 7 | 경로 처리 데코레이터의 deprecated 매개변수는 무엇을 하나요? |
| kd014 | True | True | True | 1.00 | 7 | jsonable_encoder는 어디에 쓰나요? |
| kd015 | True | True | True | 1.00 | 7 | VS Code나 PyCharm 같은 에디터의 디버거로 앱을 실행하려면 어떻게 하나요? |
| kd016 | True | True | True | 0.50 | 7 | 대화형 API 문서에 요청 데이터 예시를 보여 주려면 어떻게 하나요? |
| kd017 | True | True | True | 0.50 | 6 | OAuth2 표준에 따라 클라이언트에게 항목 읽기만 허용하는 식의 세분화된 권한을 주려면 어떻게 하나요? |
| kd018 | False | False | True | 0.17 | 7 | 경로 처리에서 JSON 대신 HTML 페이지를 반환하려면 어떻게 하나요? |
| kd019 | False | False | False | 0.00 | 6 | 하나의 경로 처리가 항목을 수정할 때는 200을, 새로 만들 때는 201을 반환하게 하려면 어떻게 하나요? |
| kd020 | True | True | True | 1.00 | 6 | 자체 문서를 가진 완전히 독립적인 FastAPI 앱을 메인 앱의 특정 경로 아래에 추가하려면 어떻게 하나요? |
| kd021 | True | True | True | 1.00 | 7 | 경로 처리에서 Jinja2 템플릿을 렌더링하려면 어떻게 하나요? |
| kd022 | True | True | True | 1.00 | 8 | WSGIMiddleware는 어디에 쓰나요? |
| kd023 | True | True | True | 1.00 | 7 | 테스트 안에서 비동기 데이터베이스를 확인하는 것처럼 비동기 테스트 함수를 작성하려면 어떻게 하나요? |
| kd024 | True | True | True | 1.00 | 7 | 환경 변수란 무엇이고 어디에 있나요? |
| kd025 | True | True | True | 1.00 | 7 | 파이썬 프로젝트마다 설치된 패키지를 따로 격리해 둬야 하는 이유는 무엇인가요? |
| kd026 | True | True | True | 1.00 | 7 | API를 배포할 때 재시작, 복제, 메모리 같은 것들은 무엇을 고려해야 하나요? |
| kd027 | True | True | True | 1.00 | 6 | 운영 환경에서 FastAPI 애플리케이션을 서빙하려면 어떤 명령을 써야 하나요? |
| kd028 | True | True | True | 1.00 | 7 | fastapi dev 명령은 무엇을 하나요? |
| kd029 | False | True | True | 0.25 | 7 | 설정을 이용해서 운영 환경에서는 OpenAPI 스키마와 문서를 끄려면 어떻게 하나요? |
| kd030 | True | True | True | 1.00 | 6 | FastAPI에서 GraphQL을 쓸 수 있나요? 어떤 라이브러리가 함께 동작하나요? |
| kd031 | True | True | True | 1.00 | 6 | 어떤 이벤트가 생기면 우리 API가 사용자의 시스템으로 요청을 보낸다는 것을 문서화하려면 어떻게 하나요? |
| kd032 | True | True | True | 1.00 | 8 | FastAPI 백엔드용 TypeScript 클라이언트를 생성하려면 어떻게 하나요? |
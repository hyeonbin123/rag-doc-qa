# Retrieval eval report (v8_test2ko_bge)

- date: 2026-09-12T10:52:14.511345+00:00
- embedding model: BAAI/bge-small-en-v1.5
- database: ragdb
- top_k: 10
- retrieval mode: dense
- dataset: qa_test2_ko.jsonl
- questions: 43
- latency: retrieval only (after the query embedding), this machine's CPU

## Aggregate metrics

| Hit@3 | Hit@5 | Hit@10 | MRR | latency p50 (ms) | latency p95 (ms) |
|---|---|---|---|---|---|
| 0.28 | 0.33 | 0.47 | 0.250 | 5 | 6 |

## Per-question

| id | hit@3 | hit@5 | hit@10 | RR | ms | question |
|---|---|---|---|---|---|---|
| k001 | False | False | False | 0.00 | 110 | 로컬 3000번 포트에서 돌아가는 React 앱이 8000번 포트의 API를 호출하면 막힙니다. 어떻게 해결하나요? |
| k002 | False | False | False | 0.00 | 6 | 요청한 항목이 없을 때 404 오류는 어떻게 반환하나요? |
| k003 | False | False | False | 0.00 | 5 | .env 파일에서 설정 값을 읽어 오려면 어떻게 하나요? |
| k004 | False | False | True | 0.17 | 5 | 요청 JSON의 필드에 기본값을 줘서 클라이언트가 생략할 수 있게 하려면 어떻게 하나요? |
| k005 | False | False | True | 0.10 | 5 | ?tag=a&tag=b처럼 같은 쿼리 매개변수로 여러 값을 받으려면 어떻게 하나요? |
| k006 | True | True | True | 0.33 | 5 | 로그인한 사용자만 호출할 수 있게 엔드포인트를 보호하려면 어떻게 하나요? |
| k007 | False | False | False | 0.00 | 5 | 사용자 비밀번호를 저장하기 전에 어떻게 해시해야 하나요? |
| k008 | False | False | False | 0.00 | 5 | 모든 요청이 처리되는 데 얼마나 걸리는지 기록하려면 어떻게 하나요? |
| k009 | False | False | False | 0.00 | 5 | 큰 파일을 메모리에 다 올리지 않고 클라이언트로 스트리밍하려면 어떻게 하나요? |
| k010 | False | False | False | 0.00 | 5 | 엔드포인트에서 사용자가 파일을 다운로드하게 하려면 어떻게 하나요? |
| k011 | False | False | False | 0.00 | 5 | 요청을 다른 URL로 리디렉션하려면 어떻게 하나요? |
| k012 | False | True | True | 0.20 | 4 | API 문서에 설명과 버전 번호를 추가하려면 어떻게 하나요? |
| k013 | False | False | False | 0.00 | 5 | 문서 페이지에서 엔드포인트를 섹션별로 묶으려면 어떻게 하나요? |
| k014 | False | False | False | 0.00 | 5 | 엔드포인트 안에서 클라이언트의 IP 주소를 얻으려면 어떻게 하나요? |
| k015 | False | False | True | 0.11 | 4 | 요청의 이메일 필드가 정말 이메일 형식인지 확인하려면 어떻게 하나요? |
| k016 | True | True | True | 1.00 | 5 | SQL 데이터베이스에 연결하고 앱이 시작될 때 테이블을 만들려면 어떻게 하나요? |
| k017 | True | True | True | 0.50 | 5 | WebSocket 엔드포인트를 테스트하려면 어떻게 하나요? |
| k018 | False | False | False | 0.00 | 5 | 사용자가 아이디와 비밀번호로 로그인해서 토큰을 받게 하려면 어떻게 하나요? |
| k019 | False | False | False | 0.00 | 6 | 로그인 토큰이 일정 시간이 지나면 만료되게 하려면 어떻게 하나요? |
| k020 | False | False | False | 0.00 | 5 | 한 번의 요청으로 여러 파일을 업로드하려면 어떻게 하나요? |
| k021 | False | False | False | 0.00 | 5 | 파일과 폼 필드를 같은 요청에서 받으려면 어떻게 하나요? |
| k022 | True | True | True | 0.50 | 5 | 쿼리 매개변수를 필수로 만들려면 어떻게 하나요? |
| k023 | True | True | True | 0.33 | 5 | 경로 매개변수에 허용할 값을 몇 가지로 제한하려면 어떻게 하나요? |
| k024 | False | False | False | 0.00 | 5 | 설정되지 않은 필드를 JSON 응답에서 빼려면 어떻게 하나요? |
| k025 | True | True | True | 1.00 | 5 | 쿠버네티스에 배포할 때 컨테이너마다 Gunicorn으로 Uvicorn 워커를 여러 개 띄워야 하나요? |
| k026 | True | True | True | 1.00 | 5 | 엔드포인트를 def로 선언하는 것과 async def로 선언하는 것은 무엇이 다른가요? |
| k027 | False | False | False | 0.00 | 5 | 내가 만든 예외 타입을 어디서든 잡아서 원하는 JSON 오류로 바꾸려면 어떻게 하나요? |
| k028 | False | False | False | 0.00 | 5 | 요청 데이터가 잘못됐을 때 FastAPI가 보내는 오류 응답을 바꾸려면 어떻게 하나요? |
| k029 | False | False | True | 0.10 | 5 | 한 모듈의 모든 라우트를 /api/v1 같은 접두사 아래에 두려면 어떻게 하나요? |
| k030 | False | False | False | 0.00 | 5 | 열어 둔 HTTP 연결 하나로 브라우저에 실시간 업데이트를 보내려면 어떻게 하나요? |
| k031 | True | True | True | 1.00 | 5 | Pydantic 모델 대신 Python dataclasses를 써도 되나요? |
| k032 | False | False | False | 0.00 | 5 | 문자열 쿼리 매개변수를 정규 표현식으로 검사하려면 어떻게 하나요? |
| k033 | False | False | False | 0.00 | 6 | 키가 미리 정해지지 않은 JSON 본문을 받으려면 어떻게 하나요? |
| k034 | False | False | False | 0.00 | 6 | 앱 전체가 아니라 라우터 하나에 속한 모든 엔드포인트에만 의존성을 적용하려면 어떻게 하나요? |
| k035 | False | True | True | 0.20 | 5 | JSON 대신 일반 텍스트를 반환하려면 어떻게 하나요? |
| k036 | True | True | True | 1.00 | 4 | 헤더 이름이 X-Token인데 파이썬 변수 이름에는 하이픈을 쓸 수 없습니다. 이 헤더를 어떻게 읽나요? |
| k037 | True | True | True | 1.00 | 5 | list[str]이나 str | None 같은 타입 힌트는 파이썬에서 어떻게 동작하나요? |
| k038 | False | False | True | 0.10 | 5 | 자동 생성되는 OpenAPI 문서에 로고를 추가하려면 어떻게 하나요? |
| k039 | True | True | True | 1.00 | 5 | 앱을 Pydantic v1에서 v2로 올리려면 어떻게 하나요? |
| k040 | False | False | False | 0.00 | 5 | 오류 응답에 사용자 정의 헤더를 함께 보내려면 어떻게 하나요? |
| k041 | False | False | True | 0.12 | 5 | React로 빌드한 싱글 페이지 앱을 FastAPI 앱에서 서빙하려면 어떻게 하나요? |
| k042 | True | True | True | 1.00 | 5 | JSON 객체 목록을 한 줄에 하나씩 스트리밍하려면 어떻게 하나요? |
| k043 | False | False | False | 0.00 | 6 | 클라이언트가 보내지만 문서에는 절대 보이지 않아야 하는 필드를 추가하려면 어떻게 하나요? |
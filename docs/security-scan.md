# 보안 스캔 (DAST)

서비스 코드를 바꾼 뒤 실행 중인 API를 OWASP ZAP(무료, Apache-2.0)으로 스캔한다. 설정은 `zap/automation.yaml` 하나로, 베이스라인 부분(OpenAPI 설명 가져오기, 스파이더, 패시브 스캔)과 API 부분(기본 정책의 액티브 스캔)을 한 번에 돌린다. ZAP 2.17.0 공식 크로스플랫폼 패키지를 Java 17 이상으로 직접 실행한다 (Docker 없음).

## 대상

- `docker compose build`로 만든 API 이미지 그대로다. 다만 `zap/compose.scan.yml`로 두 가지를 바꿔 띄운다.
  - **DB 사본**: 스캔이 가입·질문 기록을 수백 건 쓰므로 `ragdb`를 복사한 `ragdb_scan`을 쓴다. 문서와 청크(벡터 포함)는 같다.
  - **생성기 대역**: 액티브 스캔은 `/query/ask`에 질문을 수백 번 보내는데, 실제 LLM이면 한 번에 몇 초씩 GPU를 쓴다. 그래서 Ollama의 `/api/chat`을 흉내 내는 표준 라이브러리 스크립트(`zap/ollama_stub.py`)가 정해진 답과 인용 JSON을 바로 돌려준다. 인증, 입력 검증, 언어 판별, 임베딩 모델, 벡터 검색, 질문 기록은 실제 코드가 돈다. 답변 문장은 정해진 문장이라 LLM 출력 자체는 스캔 대상이 아니다.
- 모든 요청에 스캔용 사용자(사본 DB에만 있음)의 `Authorization: Bearer` 토큰을 붙인다. ZAP이 대상 호스트로 가는 요청에 헤더를 붙이게 하는 환경 변수(`ZAP_AUTH_HEADER*`)로 넘기고, `zap/run_zap.sh`가 정한다. 토큰 하나로 스캔이 끝나도록 대상의 토큰 수명을 240분으로 늘린다.
- 관리자 적재 토큰은 주지 않는다. 그래서 `POST /admin/documents/ingest`는 토큰 헤더 확인(헤더가 없으면 422)에서 멈춘다. 적재는 GitHub에서 문서를 받아 DB를 바꾸는 작업이라 스캐너가 실행하지 않게 했다.
- OpenAPI에서 만든 예시 질문에는 한글이 없어 영어 경로만 지난다. 그래서 한국어 질문 하나를 `requestor` 작업으로 보내 한국어 임베딩 경로도 액티브 스캔 대상에 넣는다.

## 실행

```bash
# DB만 띄운 상태에서 사본을 만들고 스캔 대상을 띄운다
docker compose up -d --wait db
docker compose exec -T db createdb -U raguser -T ragdb ragdb_scan
docker compose -f docker-compose.yml -f zap/compose.scan.yml up -d --wait api
# 스캔용 사용자 (사본 DB에만 생김). 이메일과 비밀번호는 아무 값이나
curl -X POST localhost:8000/auth/register -H "Content-Type: application/json" \
  -d '{"email": "<이메일>", "password": "<8자 이상>"}'
TOKEN=$(curl -s -X POST localhost:8000/auth/login -d "username=<이메일>&password=<비밀번호>" \
  | python -c "import json, sys; print(json.load(sys.stdin)['access_token'])")
# ZAP_DIR은 zap-2.17.0.jar가 있는 폴더. 리포트(<이름>.json, <이름>.md)와 로그는 work/zap/<이름>/
ZAP_DIR=<폴더> ACCESS_TOKEN=$TOKEN bash zap/run_zap.sh <이름>
```

## 결과

다음 ZAP 스캔은 마지막 줄과 비교한다. 경보 이름 뒤 괄호는 ZAP 규칙 번호.

| 차수 | 대상 | 결과 |
|---|---|---|
| 1 | 2026-10-09. 한국어 임베딩 기본값을 Granite R2 311M으로 바꾼 커밋(`1706863`) 뒤 빌드한 이미지, ZAP 2.17.0, `zap/automation.yaml` 첫 실행 | High 0. **Medium 2**: Content Security Policy 헤더 없음(10038), 클릭재킹 방지 헤더 없음(10020). 둘 다 채팅 화면(`GET /`)이다. **Low 2**: X-Content-Type-Options 헤더 없음(10021, JSON 응답 5곳), Persistent XSS in JSON Response(40014, 신뢰도 Low, `GET /logs`). 40014는 스캐너가 질문으로 보낸 `<script>` 문장이 질문 기록 JSON에 그대로 들어 있다는 것이다. 채팅 화면은 질문을 `textContent`로 넣고 답변은 HTML 이스케이프 뒤에 마크업을 붙이므로 이 화면에서는 실행되지 않는다. Informational 3: Authentication Request Identified, Modern Web Application, User Agent Fuzzer. **앱 오류 1종**: 질문에 NUL 문자(`\u0000`)가 들어 있으면 `POST /query/ask`가 500을 돌려준다(스캔 중 2건, 영어·한국어 질문 모두 다시 재현됨). 임베딩·검색·생성은 지나가고, 질문 기록을 저장할 때 PostgreSQL이 문자열 속 0x00을 거부한다(`app/routers/query.py`의 마지막 `db.commit()`). 이번 변경 전부터 있던 동작이고 이 기록에서는 고치지 않았다. 요청 4,242건(액티브 스캔 54초): 200 464, 201 1, 307 59, 401 228, 404 162, 405 113, 409 165, 422 3,048, 500 2. `POST /query/ask` 657건 중 200이 242건(한국어 질문 경로 포함)이고, 관리자 적재 요청 639건은 모두 422·307로 끝나 적재는 한 번도 돌지 않았다. 잘못된 HTTP 요청 경고 6건(예외 없음). 앱 예외는 위 500 2건뿐. 원래 DB `ragdb`의 행 수는 스캔 전과 같다 |
| 2 | 2026-10-09. 1차 지적을 고친 두 커밋 뒤 빌드한 이미지: 저장할 수 없는 문자(NUL)가 든 요청을 422로 거부(`55002dc`), 모든 응답에 CSP·클릭재킹 방지·nosniff 헤더(`ce7a847`). ZAP 2.17.0, 1차와 같은 `zap/automation.yaml`, `ragdb`에서 새로 만든 DB 사본, 생성기 대역, 관리자 토큰 없음 | High 0, **Medium 0**, **Low 1**: Persistent XSS in JSON Response(40014, 신뢰도 Low, `GET /logs`). 1차와 같은 내용이고, 채팅 화면은 여전히 질문을 `textContent`로 넣으며 이제 CSP가 인라인 스크립트도 막는다. Informational 3: 1차와 같은 세 가지. **1차에서 사라진 경보 3개**: Content Security Policy 헤더 없음(10038), 클릭재킹 방지 헤더 없음(10020), X-Content-Type-Options 헤더 없음(10021). 새 경보는 없다(CSP 설정을 보는 10055도 나오지 않음). **앱 오류 0**: 500이 한 건도 없다. 요청 4,357건(액티브 스캔 58초): 200 498, 201 1, 307 118, 401 229, 404 180, 405 120, 409 164, 422 3,047. 1차보다 많은 것은 채팅 화면의 스크립트·스타일 파일 경로(`/static/`, 117건, 그중 307 59건)가 새로 생겼기 때문이다. `POST /query/ask` 661건 중 200이 243건, 422가 418건이고, 관리자 적재 요청 639건은 모두 422·307로 끝나 적재는 한 번도 돌지 않았다. 잘못된 HTTP 요청 경고 6건(예외 없음), 앱 예외 0. 원래 DB `ragdb`의 행 수는 스캔 전과 같다 |

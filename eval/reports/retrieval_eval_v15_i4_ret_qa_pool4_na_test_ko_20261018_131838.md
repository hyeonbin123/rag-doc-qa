# Retrieval eval report (v15_i4_ret_qa_pool4_na_test_ko)

- date: 2026-10-18T13:18:25.583282+00:00
- embedding models: en BAAI/bge-small-en-v1.5, ko ibm-granite/granite-embedding-311m-multilingual-r2
- database: ragdb
- top_k: 10
- retrieval mode: dense
- search: as planned; dense plan: ko Sort > Seq Scan on chunks c > Seq Scan on documents d
- score floor: ko 0.0
- stored vectors checked: ko chunks vs ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384 (min cosine 1.0)
- dataset: qa_pool4_na_test_ko.jsonl
- questions: 20
- hit: a chunk of an expected page, in any translation
- short: questions with fewer than 5 results (the score floor cut the rest)
- latency: retrieval only (after the query embedding), this machine's CPU

## Aggregate metrics

| set | questions | Hit@3 | Hit@5 | Hit@10 | MRR | short | latency p50 (ms) | latency p95 (ms) |
|---|---|---|---|---|---|---|---|---|
| all | 20 | 0.00 | 0.00 | 0.00 | 0.000 | 0 | 7 | 10 |

## Per-question

| id | hit@3 | hit@5 | hit@10 | RR | results | ms | question |
|---|---|---|---|---|---|---|---|
| k4a01 | False | False | False | 0.00 | 10 | 10 | DRF에서 FastAPI로 옮기는 중인데, DRF ModelSerializer의 read_only_fields랑 extra_kwargs는 정확히 뭐가 달랐죠? |
| k4a02 | False | False | False | 0.00 | 10 | 7 | FastAPI를 Mangum으로 감싸서 Lambda에 올리려는데 AWS 콘솔에서 API Gateway 연결하는 클릭 순서 좀 알려주세요 |
| k4a03 | False | False | False | 0.00 | 10 | 7 | SQLAlchemy 2.0에서 relationship에 lazy="selectin" 주는 거랑 쿼리에서 joinedload 쓰는 거 성능 차이가 어느 정도예요? |
| k4a04 | False | False | False | 0.00 | 10 | 7 | Alembic autogenerate가 컬럼 타입 변경을 못 잡는데 compare_type 옵션은 env.py 어디에 넣어야 해요? |
| k4a05 | False | False | False | 0.00 | 10 | 8 | Celery beat로 매일 새벽 3시에 배치 돌리려면 crontab 스케줄 설정을 어떻게 써요? |
| k4a06 | False | False | False | 0.00 | 10 | 7 | slowapi로 IP당 분당 10회 제한 거는 데코레이터 사용법이랑 Redis 백엔드 연결하는 방법 |
| k4a07 | False | False | False | 0.00 | 10 | 7 | 업로드하면 Nginx에서 413 Request Entity Too Large가 떠요. client_max_body_size는 http, server, location 중 어디에 넣어야 해요? |
| k4a09 | False | False | False | 0.00 | 10 | 7 | Next.js App Router server action에서 FastAPI 백엔드 호출하면 쿠키가 안 넘어가요. Next 쪽에서 뭘 설정해야 하나요? |
| k4a10 | False | False | False | 0.00 | 10 | 7 | Ubuntu 22.04에서 uvicorn을 systemd 서비스로 등록하려는데 unit 파일에 Restart=always랑 RestartSec 어떻게 써? |
| k4a12 | False | False | False | 0.00 | 10 | 7 | Google Cloud Console에서 OAuth 클라이언트 ID 만들 때 승인된 리디렉션 URI는 어느 화면에서 입력해요? |
| k4a13 | False | False | False | 0.00 | 10 | 7 | Keycloak 관리 콘솔에서 realm 만들고 client secret 확인하는 메뉴가 어디 있어요? |
| k4a16 | False | False | False | 0.00 | 10 | 7 | RTX 4090 한 장으로 FastAPI 뒤에 Llama 3 8B 올리면 초당 토큰 몇 개 정도 나와요? |
| k4a18 | False | False | False | 0.00 | 10 | 7 | 회사에서 Litestar랑 FastAPI 중에 고민 중인데 커뮤니티 규모나 국내 채용 시장 기준으로 비교해 줄 수 있어요? |
| k4a19 | False | False | False | 0.00 | 10 | 7 | SQLAlchemy 2.0 정식 릴리스가 언제였죠? 레거시 Query API 쓰는 우리 코드가 얼마나 오래된 건지 가늠해 보려고요 |
| k4a20 | False | False | False | 0.00 | 10 | 8 | MongoDB 붙이려고 Beanie ODM 쓰는데 Document 클래스에 복합 인덱스 정의하는 법 |
| k4a21 | False | False | False | 0.00 | 10 | 7 | Sentry Python SDK의 traces_sample_rate는 몇으로 둬야 비용이 적당한가요? |
| k4a22 | False | False | False | 0.00 | 10 | 7 | prometheus-fastapi-instrumentator로 메트릭 노출했는데 Grafana에서 가져다 쓸 만한 대시보드 ID 추천해 주세요 |
| k4a25 | False | False | False | 0.00 | 10 | 7 | Stripe 웹훅 받는 엔드포인트 만드는 중인데 서명 검증용 signing secret은 Stripe 대시보드 어디서 확인해요? |
| k4a29 | False | False | False | 0.00 | 10 | 7 | Let's Encrypt certbot 자동 갱신이 실패하는데 certbot renew --dry-run 로그는 어디서 봐요? |
| k4a30 | False | False | False | 0.00 | 10 | 7 | Docker Compose에서 postgres에 healthcheck 걸고 depends_on에 condition: service_healthy 쓰는 문법 알려주세요 |
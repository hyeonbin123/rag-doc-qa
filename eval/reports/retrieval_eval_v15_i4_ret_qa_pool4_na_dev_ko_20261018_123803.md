# Retrieval eval report (v15_i4_ret_qa_pool4_na_dev_ko)

- date: 2026-10-18T12:37:52.064482+00:00
- embedding models: en BAAI/bge-small-en-v1.5, ko ibm-granite/granite-embedding-311m-multilingual-r2
- database: ragdb
- top_k: 10
- retrieval mode: dense
- search: as planned; dense plan: ko Sort > Seq Scan on chunks c > Seq Scan on documents d
- score floor: ko 0.0
- stored vectors checked: ko chunks vs ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384 (min cosine 1.0)
- dataset: qa_pool4_na_dev_ko.jsonl
- questions: 10
- hit: a chunk of an expected page, in any translation
- short: questions with fewer than 5 results (the score floor cut the rest)
- latency: retrieval only (after the query embedding), this machine's CPU

## Aggregate metrics

| set | questions | Hit@3 | Hit@5 | Hit@10 | MRR | short | latency p50 (ms) | latency p95 (ms) |
|---|---|---|---|---|---|---|---|---|
| all | 10 | 0.00 | 0.00 | 0.00 | 0.000 | 0 | 7 | 9 |

## Per-question

| id | hit@3 | hit@5 | hit@10 | RR | results | ms | question |
|---|---|---|---|---|---|---|---|
| k4a08 | False | False | False | 0.00 | 10 | 9 | React 18 StrictMode에서 useEffect로 백엔드 API 호출하면 요청이 두 번씩 가는데 이거 어떻게 막아요? |
| k4a11 | False | False | False | 0.00 | 10 | 7 | 윈도우 방화벽에서 8000번 포트 인바운드 규칙 여는 방법 알려줘요 |
| k4a14 | False | False | False | 0.00 | 10 | 7 | PostgreSQL jsonb 컬럼에 GIN 인덱스 걸면 @> 조회가 실제로 얼마나 빨라지나요? |
| k4a15 | False | False | False | 0.00 | 10 | 7 | Redis 캐시 서버 maxmemory-policy를 allkeys-lru로 할지 volatile-lru로 할지 고민인데 차이가 뭐예요? |
| k4a17 | False | False | False | 0.00 | 10 | 7 | AWS t3.small 인스턴스에서 FastAPI hello world 띄우면 RPS가 보통 얼마나 나오나요? |
| k4a23 | False | False | False | 0.00 | 10 | 7 | 쿠버네티스 HPA를 CPU 사용률 70% 기준으로 만드는 yaml 예시 좀 보여줘 |
| k4a24 | False | False | False | 0.00 | 10 | 7 | GitHub Actions에서 Docker 이미지 빌드해서 ECR로 푸시하는 워크플로 작성하는 법 |
| k4a26 | False | False | False | 0.00 | 10 | 7 | Poetry로 관리하던 프로젝트를 uv로 옮기려는데 poetry.lock을 uv.lock으로 변환하는 방법 있나요? |
| k4a27 | False | False | False | 0.00 | 10 | 7 | aiokafka로 컨슈머 만들었는데 consumer group 리밸런스가 자꾸 일어나요. 원인이 뭘까요? |
| k4a28 | False | False | False | 0.00 | 10 | 7 | VS Code에서 Pylance가 Pydantic 모델 필드에 빨간 줄 긋는데 Pylance 타입 체크 수준은 어디서 바꿔요? |
# Answer eval report (v16b_b_qa_pool4_na_dev_ko)

- date: 2026-11-03T15:55:15.097304+00:00
- generated: 2026-11-03T15:54:26.909968+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/10)
- final answer call stopped by the output limit, done_reason=length: 1/10; reasoning output: 0/10; citation replies breaking the schema: 0/10
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- corpus: source commit 50113da (277 documents); last fetched 2026-11-03T08:04:42.172603+00:00; chunks en 914, ko 621
- dataset: qa_pool4_na_dev_ko.jsonl
- questions: 10
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v16b_b_qa_pool4_na_dev_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 1.00 | n/a | n/a | n/a | 0/0 | 2287 | 0/10 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| k4a08 | 1.00 | None | None | None | 2285 | False | None / None | - |
| k4a11 | 1.00 | None | None | None | 1782 | False | None / None | - |
| k4a14 | 1.00 | None | None | None | 2288 | False | None / None | - |
| k4a15 | 1.00 | None | None | None | 2253 | False | None / None | - |
| k4a17 | 1.00 | None | None | None | 2979 | False | None / None | - |
| k4a23 | 1.00 | None | None | None | 5474 | False | None / None | - |
| k4a24 | 1.00 | None | None | None | 14892 | False | None / None | - |
| k4a26 | 1.00 | None | None | None | 2230 | False | None / None | - |
| k4a27 | 1.00 | None | None | None | 2558 | False | None / None | - |
| k4a28 | 1.00 | None | None | None | 2165 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **k4a08** (1.00): React 18 StrictMode에서 useEffect로 백엔드 API 호출하면 요청이 두 번씩 가는데 이거 어떻게 막아요?
  > 죄송합니다. 제공된 문서 구절에는 이 질문에 대한 내용이 없습니다.
- **k4a11** (1.00): 윈도우 방화벽에서 8000번 포트 인바운드 규칙 여는 방법 알려줘요
  > 죄송합니다. 제공된 문서 구절에는 이 질문에 대한 내용이 없습니다.
- **k4a14** (1.00): PostgreSQL jsonb 컬럼에 GIN 인덱스 걸면 @> 조회가 실제로 얼마나 빨라지나요?
  > 죄송합니다. 제공된 문서 구절에는 이 질문에 대한 내용이 없습니다.
- **k4a15** (1.00): Redis 캐시 서버 maxmemory-policy를 allkeys-lru로 할지 volatile-lru로 할지 고민인데 차이가 뭐예요?
  > I don't know: the provided documentation passages do not cover this question.
- **k4a17** (1.00): AWS t3.small 인스턴스에서 FastAPI hello world 띄우면 RPS가 보통 얼마나 나오나요?
  > 죄송합니다. 제공된 문서 구절에는 AWS t3.small 인스턴스에서 FastAPI hello world의 RPS(Requests Per Second)에 대한 정보가 없습니다.
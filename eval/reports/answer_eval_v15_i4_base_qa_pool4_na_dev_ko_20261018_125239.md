# Answer eval report (v15_i4_base_qa_pool4_na_dev_ko)

- date: 2026-10-18T12:52:39.228581+00:00
- generated: 2026-10-18T12:51:39.649382+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/10)
- final answer call stopped by the output limit, done_reason=length: 0/10; reasoning output: 0/10; citation replies breaking the schema: 0/10
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_pool4_na_dev_ko.jsonl
- questions: 10
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_base_qa_pool4_na_dev_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 1.00 | n/a | n/a | n/a | 0/0 | 3770 | 0/10 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| k4a08 | 1.00 | None | None | None | 7952 | False | None / None | - |
| k4a11 | 1.00 | None | None | None | 2792 | False | None / None | - |
| k4a14 | 1.00 | None | None | None | 3214 | False | None / None | - |
| k4a15 | 1.00 | None | None | None | 8765 | False | None / None | - |
| k4a17 | 1.00 | None | None | None | 3681 | False | None / None | - |
| k4a23 | 1.00 | None | None | None | 3204 | False | None / None | - |
| k4a24 | 1.00 | None | None | None | 3860 | False | None / None | - |
| k4a26 | 1.00 | None | None | None | 5864 | False | None / None | - |
| k4a27 | 1.00 | None | None | None | 2960 | False | None / None | - |
| k4a28 | 1.00 | None | None | None | 4595 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **k4a08** (1.00): React 18 StrictMode에서 useEffect로 백엔드 API 호출하면 요청이 두 번씩 가는데 이거 어떻게 막아요?
  > React 18의 StrictMode는 개발 중에 컴포넌트의 side effect를 더 엄격하게 검사하기 위해 사용됩니다. `useEffect`로 백엔드 API를 호출할 때 요청이 두 번 발생하는 문제는 StrictMode의 `useEffect`의 `effect`가 두 번 실행되는 것과 관련이 있습니다.

### 해결 방법:

1. **useEffect의 
- **k4a11** (1.00): 윈도우 방화벽에서 8000번 포트 인바운드 규칙 여는 방법 알려줘요
  > 죄송하지만, 윈도우 방화벽에서 8000번 포트 인바운드 규칙을 여는 방법에 대한 정보는 제공되지 않았습니다.
- **k4a14** (1.00): PostgreSQL jsonb 컬럼에 GIN 인덱스 걸면 @> 조회가 실제로 얼마나 빨라지나요?
  > 죄송하지만, 주어진 문맥에서 해당 질문에 대한 정보를 찾을 수 없습니다. PostgreSQL의 jsonb 컬럼에 GIN 인덱스를 걸었을 때 @> 조회의 성능 향상에 대한 구체적인 수치나 결과는 제공되지 않았습니다.
- **k4a15** (1.00): Redis 캐시 서버 maxmemory-policy를 allkeys-lru로 할지 volatile-lru로 할지 고민인데 차이가 뭐예요?
  > `allkeys-lru`와 `volatile-lru`는 Redis의 메모리 관리 정책에서 사용되는 두 가지 다른 전략입니다.

### allkeys-lru
- **모든 키에 대해 LRU(Least Recently Used) 정책 적용**:
  - Redis가 메모리를 초과할 때, 가장 오랫동안 사용되지 않은 **모든 키**를 기준으로 제거합니다.
  - 즉
- **k4a17** (1.00): AWS t3.small 인스턴스에서 FastAPI hello world 띄우면 RPS가 보통 얼마나 나오나요?
  > AWS t3.small 인스턴스에서 FastAPI hello world 애플리케이션을 실행하면, 일반적으로 RPS(Requests Per Second)는 약 100~200 정도로 나올 수 있습니다. 이는 Starlette와 Pydantic의 성능 덕분에 가능한 수치이며, 실제 성능은 네트워크 대역폭, 요청의 복잡성, 서버 설정 등에 따라 달라질 수 있습니다
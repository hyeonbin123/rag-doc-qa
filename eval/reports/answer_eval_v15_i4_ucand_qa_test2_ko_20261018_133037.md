# Answer eval report (v15_i4_ucand_qa_test2_ko)

- date: 2026-10-18T13:30:37.361269+00:00
- generated: 2026-10-18T13:29:50.348544+00:00
- provider: ollama
- model: a.x-4.0-light:q4_k_m
- model digest: a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661
- think: None, language guard: on (regenerated 0/12)
- final answer call stopped by the output limit, done_reason=length: 0/12; reasoning output: 0/12; citation replies breaking the schema: 0/12
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384'}
- dataset: qa_test2_ko.jsonl
- questions: 12
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v15_i4_ucand_qa_test2_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.33 | n/a | n/a | n/a | 0/0 | 2409 | 0/12 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| k001 | 1.00 | None | None | None | 6676 | False | None / None | - |
| k006 | 1.00 | None | None | None | 8238 | False | None / None | - |
| k008 | 0.00 | None | None | None | 6630 | False | None / None | - |
| k010 | 0.00 | None | None | None | 0 | False | None / None | - |
| k011 | 0.00 | None | None | None | 0 | False | None / None | - |
| k013 | 0.00 | None | None | None | 0 | False | None / None | - |
| k014 | 0.00 | None | None | None | 0 | False | None / None | - |
| k015 | 0.00 | None | None | None | 0 | False | None / None | - |
| k019 | 1.00 | None | None | None | 4517 | False | None / None | - |
| k023 | 1.00 | None | None | None | 3959 | False | None / None | - |
| k034 | 0.00 | None | None | None | 2714 | False | None / None | - |
| k043 | 0.00 | None | None | None | 2103 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **k008** (0.00): 모든 요청이 처리되는 데 얼마나 걸리는지 기록하려면 어떻게 하나요?
  > 모든 요청이 처리되는 데 걸리는 시간을 기록하려면, FastAPI 애플리케이션에서 **Lifespan 이벤트**를 활용할 수 있습니다. 구체적으로는 `on_startup`과 `on_shutdown` 이벤트를 사용합니다.

1. **on_startup** 이벤트에서 모델을 로드합니다.
2. **on_shutdown** 이벤트에서 로깅을 통해 전체 요청 처리 
- **k010** (0.00): 엔드포인트에서 사용자가 파일을 다운로드하게 하려면 어떻게 하나요?
  > 모르겠습니다. 찾은 문서 구절에는 이 질문에 대한 내용이 없습니다.
- **k011** (0.00): 요청을 다른 URL로 리디렉션하려면 어떻게 하나요?
  > 모르겠습니다. 찾은 문서 구절에는 이 질문에 대한 내용이 없습니다.
- **k013** (0.00): 문서 페이지에서 엔드포인트를 섹션별로 묶으려면 어떻게 하나요?
  > 모르겠습니다. 찾은 문서 구절에는 이 질문에 대한 내용이 없습니다.
- **k014** (0.00): 엔드포인트 안에서 클라이언트의 IP 주소를 얻으려면 어떻게 하나요?
  > 모르겠습니다. 찾은 문서 구절에는 이 질문에 대한 내용이 없습니다.
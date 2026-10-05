# Answer eval report (v13_sel_g0_qa_dev2_ko)

- date: 2026-10-05T05:11:29.584917+00:00
- generated: 2026-10-05T05:07:36.023878+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- model digest: 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: skipped
- ollama version: 0.35.1 (generation)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'intfloat/multilingual-e5-small'}
- dataset: qa_dev2_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_sel_g0_qa_dev2_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.71 | n/a | n/a | n/a | 0/0 | 5443 | 0/40 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n001 | 1.00 | None | None | None | 6185 | False | None / None | - |
| n005 | 1.00 | None | None | None | 6026 | False | None / None | - |
| n006 | 1.00 | None | None | None | 5981 | False | None / None | - |
| n009 | 0.00 | None | None | None | 4183 | False | None / None | - |
| n011 | 1.00 | None | None | None | 4792 | False | None / None | - |
| n012 | 1.00 | None | None | None | 5160 | False | None / None | - |
| n015 | 0.00 | None | None | None | 4529 | False | None / None | - |
| n018 | 0.00 | None | None | None | 4858 | False | None / None | - |
| n031 | 1.00 | None | None | None | 5906 | False | None / None | - |
| n041 | 1.00 | None | None | None | 4630 | False | None / None | - |
| n044 | 1.00 | None | None | None | 6377 | False | None / None | - |
| n049 | 0.50 | None | None | None | 4452 | False | None / None | - |
| n053 | 1.00 | None | None | None | 7749 | False | None / None | - |
| n058 | 1.00 | None | None | None | 6169 | False | None / None | - |
| n059 | 1.00 | None | None | None | 6527 | False | None / None | - |
| n063 | 1.00 | None | None | None | 6657 | False | None / None | - |
| n066 | 1.00 | None | None | None | 6806 | False | None / None | - |
| n068 | 1.00 | None | None | None | 4749 | False | None / None | - |
| n069 | 0.00 | None | None | None | 5392 | False | None / None | - |
| n073 | 1.00 | None | None | None | 5215 | False | None / None | - |
| n074 | 0.50 | None | None | None | 5051 | False | None / None | - |
| n076 | 0.50 | None | None | None | 6383 | False | None / None | - |
| n080 | 0.50 | None | None | None | 4742 | False | None / None | - |
| n084 | 1.00 | None | None | None | 4762 | False | None / None | - |
| n087 | 1.00 | None | None | None | 4582 | False | None / None | - |
| n088 | 1.00 | None | None | None | 5852 | False | None / None | - |
| n089 | 0.50 | None | None | None | 6031 | False | None / None | - |
| n090 | 0.00 | None | None | None | 4551 | False | None / None | - |
| n092 | 1.00 | None | None | None | 6749 | False | None / None | - |
| n094 | 1.00 | None | None | None | 5728 | False | None / None | - |
| n098 | 0.50 | None | None | None | 5634 | False | None / None | - |
| n100 | 1.00 | None | None | None | 5495 | False | None / None | - |
| n102 | 1.00 | None | None | None | 6482 | False | None / None | - |
| n103 | 0.00 | None | None | None | 6304 | False | None / None | - |
| n107 | 1.00 | None | None | None | 3139 | False | None / None | - |
| n110 | 0.00 | None | None | None | 5334 | False | None / None | - |
| n114 | 0.50 | None | None | None | 5181 | False | None / None | - |
| n117 | 1.00 | None | None | None | 5120 | False | None / None | - |
| n118 | 1.00 | None | None | None | 5213 | False | None / None | - |
| n119 | 0.00 | None | None | None | 8292 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **n009** (0.00): 더 이상 안 쓰는 쿼리 파라미터를 문서에서 deprecated로 표시하려면?
  > don't know
- **n015** (0.00): 요청 본문에 Pydantic 모델 두 개를 동시에 받을 수 있어?
  > 네, 요청 본문에 Pydantic 모델 두 개를 동시에 받을 수 있습니다.
- **n018** (0.00): Swagger 문서에 요청 바디 예시를 여러 개 보여주고 싶은데 가능할까요?
  > 네, 가능합니다. `Body()` 매개변수에 `examples`를 넘기면 여러 개의 예시를 제공할 수 있습니다.
- **n069** (0.00): 테스트용 DB를 운영 DB와 분리해서 쓰고 싶은데 어떻게 구성하는 게 좋을까요?
  > 테스트용 DB를 운영 DB와 분리하여 사용하려면, 테스트 코드에서 DB 연결을 설정할 때 다른 환경 변수나 구성 파일을 사용하여 테스트용 DB를 지정할 수 있습니다. 이렇게 하면 테스트 코드에서 운영 DB와 테스트용 DB를 독립적으로 관리할 수 있습니다.
- **n090** (0.00): 같은 엔드포인트에서 상황에 따라 상태 코드를 다르게 돌려주고 싶을 때 어떻게 해요?
  > FastAPI는 `fastapi.status` 모듈을 통해 상태 코드를 쉽게 사용할 수 있게 해줍니다. 이를 통해 코드에서 상태 코드를 더 직관적으로 사용할 수 있으며, 편집기의 자동완성 기능을 활용할 수도 있습니다.
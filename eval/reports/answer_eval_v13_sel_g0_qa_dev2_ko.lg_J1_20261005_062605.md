# Answer eval report (v13_sel_g0_qa_dev2_ko.lg, judge J1)

- date: 2026-10-05T06:26:05.501362+00:00
- generated: 2026-10-05T05:07:36.023878+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- model digest: 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e
- think: None, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-05T06:24:55.595318+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'intfloat/multilingual-e5-small'}
- dataset: qa_dev2_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_sel_g0_qa_dev2_ko.gen.jsonl, eval/runs/v13_sel_g0_qa_dev2_ko.lg.J1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.71 | 4.17 | 4.30 | 172 | 2/40 | 5443 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n001 | 1.00 | 4 | 4 | False | 6185 | False | 1803 / 1803 | ok |
| n005 | 1.00 | 4 | 5 | False | 6026 | False | 1971 / 1971 | ok |
| n006 | 1.00 | 5 | 5 | False | 5981 | False | 1957 / 1957 | ok |
| n009 | 0.00 | 3 | 2 | True | 4183 | False | 1905 / 1905 | ok |
| n011 | 1.00 | 4 | 5 | False | 4792 | False | 1913 / 1913 | ok |
| n012 | 1.00 | 5 | 5 | False | 5160 | False | 1774 / 1774 | ok |
| n015 | 0.00 | 5 | 5 | False | 4529 | False | 1881 / 1881 | ok |
| n018 | 0.00 | 4 | 4 | False | 4858 | False | 1929 / 1929 | ok |
| n031 | 1.00 | 4 | 4 | False | 5906 | False | 1752 / 1752 | ok |
| n041 | 1.00 | 4 | 4 | False | 4630 | False | 1881 / 1881 | ok |
| n044 | 1.00 | 4 | 4 | False | 6377 | False | 2130 / 2130 | ok |
| n049 | 0.50 | 5 | 5 | False | 4452 | False | 1891 / 1891 | ok |
| n053 | 1.00 | 4 | 4 | False | 7749 | False | 2162 / 2162 | ok |
| n058 | 1.00 | 5 | 5 | False | 6169 | False | 1918 / 1918 | ok |
| n059 | 1.00 | 5 | 5 | False | 6527 | False | 2013 / 2013 | ok |
| n063 | 1.00 | 4 | 4 | False | 6657 | False | 2013 / 2013 | ok |
| n066 | 1.00 | 4 | 4 | False | 6806 | False | 2055 / 2055 | ok |
| n068 | 1.00 | 4 | 5 | False | 4749 | False | 1676 / 1676 | ok |
| n069 | 0.00 | 4 | 4 | False | 5392 | False | 1931 / 1931 | ok |
| n073 | 1.00 | 4 | 5 | False | 5215 | False | 2002 / 2002 | ok |
| n074 | 0.50 | 5 | 5 | False | 5051 | False | 1800 / 1800 | ok |
| n076 | 0.50 | 4 | 4 | False | 6383 | False | 1962 / 1962 | ok |
| n080 | 0.50 | 4 | 4 | False | 4742 | False | 1697 / 1697 | ok |
| n084 | 1.00 | 4 | 5 | False | 4762 | False | 1952 / 1952 | ok |
| n087 | 1.00 | 3 | 2 | True | 4582 | False | 1854 / 1854 | ok |
| n088 | 1.00 | 4 | 4 | False | 5852 | False | 2166 / 2166 | ok |
| n089 | 0.50 | 5 | 5 | False | 6031 | False | 2115 / 2115 | ok |
| n090 | 0.00 | 3 | 3 | False | 4551 | False | 1473 / 1473 | ok |
| n092 | 1.00 | 5 | 5 | False | 6749 | False | 1794 / 1794 | ok |
| n094 | 1.00 | 4 | 5 | False | 5728 | False | 2046 / 2046 | ok |
| n098 | 0.50 | 4 | 4 | False | 5634 | False | 1892 / 1892 | ok |
| n100 | 1.00 | 4 | 4 | False | 5495 | False | 2065 / 2065 | ok |
| n102 | 1.00 | 4 | 4 | False | 6482 | False | 2107 / 2107 | ok |
| n103 | 0.00 | 4 | 4 | False | 6304 | False | 1998 / 1998 | ok |
| n107 | 1.00 | 4 | 4 | False | 3139 | False | 534 / 534 | ok |
| n110 | 0.00 | 4 | 4 | False | 5334 | False | 2019 / 2019 | ok |
| n114 | 0.50 | 4 | 4 | False | 5181 | False | 1743 / 1743 | ok |
| n117 | 1.00 | 4 | 4 | False | 5120 | False | 1826 / 1826 | ok |
| n118 | 1.00 | 5 | 5 | False | 5213 | False | 1983 / 1983 | ok |
| n119 | 0.00 | 4 | 5 | False | 8292 | False | 2442 / 2442 | ok |

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
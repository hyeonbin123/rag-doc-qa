# Answer eval report (v13_sel_g2_qa_dev2_ko)

- date: 2026-10-05T05:54:28.634895+00:00
- generated: 2026-10-05T05:46:13.745865+00:00
- provider: ollama
- model: gemma4:12b-it-qat
- model digest: 38044be4f923e5a55264ed7df4eaac2676651a905f735197c504045140c02bd3
- think: False, language guard: on (regenerated 0/40)
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
- per-item records: eval/runs/v13_sel_g2_qa_dev2_ko.gen.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.72 | n/a | n/a | n/a | 0/0 | 11108 | 0/40 | 0/0 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n001 | 0.00 | None | None | None | 9342 | False | None / None | - |
| n005 | 1.00 | None | None | None | 12686 | False | None / None | - |
| n006 | 1.00 | None | None | None | 12596 | False | None / None | - |
| n009 | 1.00 | None | None | None | 10830 | False | None / None | - |
| n011 | 1.00 | None | None | None | 9714 | False | None / None | - |
| n012 | 0.00 | None | None | None | 9835 | False | None / None | - |
| n015 | 0.00 | None | None | None | 9683 | False | None / None | - |
| n018 | 1.00 | None | None | None | 12766 | False | None / None | - |
| n031 | 1.00 | None | None | None | 10707 | False | None / None | - |
| n041 | 1.00 | None | None | None | 10400 | False | None / None | - |
| n044 | 0.00 | None | None | None | 11386 | False | None / None | - |
| n049 | 1.00 | None | None | None | 9260 | False | None / None | - |
| n053 | 1.00 | None | None | None | 15747 | False | None / None | - |
| n058 | 1.00 | None | None | None | 14550 | False | None / None | - |
| n059 | 1.00 | None | None | None | 12888 | False | None / None | - |
| n063 | 1.00 | None | None | None | 17738 | False | None / None | - |
| n066 | 1.00 | None | None | None | 15988 | False | None / None | - |
| n068 | 1.00 | None | None | None | 8664 | False | None / None | - |
| n069 | 0.00 | None | None | None | 9146 | False | None / None | - |
| n073 | 1.00 | None | None | None | 9592 | False | None / None | - |
| n074 | 0.50 | None | None | None | 8506 | False | None / None | - |
| n076 | 0.50 | None | None | None | 15653 | False | None / None | - |
| n080 | 0.50 | None | None | None | 8143 | False | None / None | - |
| n084 | 1.00 | None | None | None | 16517 | False | None / None | - |
| n087 | 1.00 | None | None | None | 10716 | False | None / None | - |
| n088 | 1.00 | None | None | None | 14255 | False | None / None | - |
| n089 | 1.00 | None | None | None | 13619 | False | None / None | - |
| n090 | 0.50 | None | None | None | 9018 | False | None / None | - |
| n092 | 1.00 | None | None | None | 9084 | False | None / None | - |
| n094 | 0.50 | None | None | None | 8335 | False | None / None | - |
| n098 | 0.00 | None | None | None | 8657 | False | None / None | - |
| n100 | 1.00 | None | None | None | 18217 | False | None / None | - |
| n102 | 0.50 | None | None | None | 16431 | False | None / None | - |
| n103 | 0.00 | None | None | None | 14563 | False | None / None | - |
| n107 | 1.00 | None | None | None | 5246 | False | None / None | - |
| n110 | 1.00 | None | None | None | 13763 | False | None / None | - |
| n114 | 1.00 | None | None | None | 14303 | False | None / None | - |
| n117 | 0.00 | None | None | None | 9490 | False | None / None | - |
| n118 | 1.00 | None | None | None | 11685 | False | None / None | - |
| n119 | 1.00 | None | None | None | 23404 | False | None / None | - |

## Worst questions (lowest keyword coverage)

- **n001** (0.00): FastAPI에서 경로 매개변수를 정수 타입으로 받으려면 어떻게 선언해야 하나요?
  > FastAPI는 동일한 파이썬 타입 선언만으로 경로 매개변수가 정수형으로 선언된 것을 확인할 수 있으며, 이를 통해 자동 대화형 문서를 제공합니다. 또한 `Path`를 사용하여 경로 매개변수에 검증과 메타데이터를 선언할 수 있습니다.
- **n012** (0.00): Pydantic BaseModel로 POST 요청 본문 받는 가장 기본적인 예제 보여주세요.
  > 제공된 문맥에는 Pydantic 모델을 사용하여 POST 요청 본문을 받는 구체적인 코드 예제가 포함되어 있지 않습니다. 다만, 문맥에 따르면 요청 본문을 선언하기 위해 Pydantic 모델을 사용하며, 함수 매개변수가 Pydantic 모델 타입으로 선언되어 있으면 요청 본문으로 해석된다는 점을 확인할 수 있습니다.
- **n015** (0.00): 요청 본문에 Pydantic 모델 두 개를 동시에 받을 수 있어?
  > 제공된 문맥에는 요청 본문에 Pydantic 모델 두 개를 동시에 받을 수 있는지에 대한 직접적인 정보가 없습니다. 다만, 경로 매개변수와 요청 본문을 동시에 선언하거나, 본문, 경로, 쿼리 매개변수를 모두 동시에 선언할 수 있다는 내용은 포함되어 있습니다.
- **n044** (0.00): yield 의존성에서 예외가 발생하면 except로 잡을 수 있나요? 거기서 HTTPException을 다시 던져도 되나?
  > 네, `yield`를 사용하는 의존성에서 `except`를 사용하여 예외를 포착할 수 있습니다. 또한, 필요한 경우 `except` 블록 내에서 `HTTPException`과 같은 다른 예외를 발생시킬 수도 있습니다.

다만, 예외를 포착한 후 다시 발생시키지 않거나 새 예외를 발생시키지 않으면, FastAPI는 예외가 있었다는 것을 알아차릴 수 없으며 클
- **n069** (0.00): 테스트용 DB를 운영 DB와 분리해서 쓰고 싶은데 어떻게 구성하는 게 좋을까요?
  > 제공된 문맥에는 테스트용 DB를 운영 DB와 분리하여 구성하는 구체적인 방법에 대한 정보가 포함되어 있지 않습니다.
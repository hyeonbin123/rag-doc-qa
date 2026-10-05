# Answer eval report (v13_sel_g2_qa_dev2_ko.raw, judge J1)

- date: 2026-10-05T06:36:45.550579+00:00
- generated: 2026-10-05T05:46:13.745865+00:00
- provider: ollama
- model: gemma4:12b-it-qat
- model digest: 38044be4f923e5a55264ed7df4eaac2676651a905f735197c504045140c02bd3
- think: False, language guard: on (regenerated 0/40)
- final answer call stopped by the output limit, done_reason=length: 0/40; reasoning output: 0/40; citation replies breaking the schema: 0/40
- judge: J1, qwen2.5:7b-instruct, num_ctx 8192, truncate=false
- judge context in use (Ollama /api/ps after judging): 8192
- judge prompt token counter: Qwen/Qwen2.5-7B-Instruct@a09a354
- judge order: dataset
- judge date: 2026-10-05T06:34:41.425173+00:00
- ollama version: 0.35.1 (generation), 0.35.1 (judge)
- top_k: 5
- retrieval mode: dense
- database: ragdb, embedding models: {'ko': 'intfloat/multilingual-e5-small'}
- dataset: qa_dev2_ko.jsonl
- questions: 40
- generation order: dataset
- generation time: both generation calls (answer + citations), this machine's GPU
- per-item records: eval/runs/v13_sel_g2_qa_dev2_ko.gen.jsonl, eval/runs/v13_sel_g2_qa_dev2_ko.raw.J1.judge.jsonl

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Correctness sum | Hallucinated | Generation p50 (ms) | Answers with kana/han | Judge prompts truncated | Judge errors |
|---|---|---|---|---|---|---|---|---|
| 0.72 | 3.98 | 4.25 | 170 | 0/40 | 11108 | 0/40 | 0/40 | 0 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated | generation ms | kana/han | judge prompt tokens (counted / read) | truncation |
|---|---|---|---|---|---|---|---|---|
| n001 | 0.00 | 4 | 4 | False | 9342 | False | 1748 / 1748 | ok |
| n005 | 1.00 | 5 | 5 | False | 12686 | False | 2024 / 2024 | ok |
| n006 | 1.00 | 4 | 5 | False | 12596 | False | 1991 / 1991 | ok |
| n009 | 1.00 | 2 | 2 | False | 10830 | False | 1938 / 1938 | ok |
| n011 | 1.00 | 4 | 5 | False | 9714 | False | 1942 / 1942 | ok |
| n012 | 0.00 | 3 | 3 | False | 9835 | False | 1797 / 1797 | ok |
| n015 | 0.00 | 4 | 5 | False | 9683 | False | 1939 / 1939 | ok |
| n018 | 1.00 | 4 | 4 | False | 12766 | False | 2045 / 2045 | ok |
| n031 | 1.00 | 4 | 4 | False | 10707 | False | 1788 / 1788 | ok |
| n041 | 1.00 | 4 | 4 | False | 10400 | False | 1949 / 1949 | ok |
| n044 | 0.00 | 4 | 4 | False | 11386 | False | 2177 / 2177 | ok |
| n049 | 1.00 | 5 | 5 | False | 9260 | False | 1950 / 1950 | ok |
| n053 | 1.00 | 4 | 4 | False | 15747 | False | 2242 / 2242 | ok |
| n058 | 1.00 | 4 | 4 | False | 14550 | False | 2034 / 2034 | ok |
| n059 | 1.00 | 4 | 4 | False | 12888 | False | 2087 / 2087 | ok |
| n063 | 1.00 | 4 | 4 | False | 17738 | False | 2213 / 2213 | ok |
| n066 | 1.00 | 4 | 4 | False | 15988 | False | 2187 / 2187 | ok |
| n068 | 1.00 | 4 | 5 | False | 8664 | False | 1696 / 1696 | ok |
| n069 | 0.00 | 3 | 3 | False | 9146 | False | 1887 / 1887 | ok |
| n073 | 1.00 | 4 | 4 | False | 9592 | False | 2025 / 2025 | ok |
| n074 | 0.50 | 5 | 5 | False | 8506 | False | 1818 / 1818 | ok |
| n076 | 0.50 | 4 | 5 | False | 15653 | False | 2075 / 2075 | ok |
| n080 | 0.50 | 4 | 5 | False | 8143 | False | 1684 / 1684 | ok |
| n084 | 1.00 | 4 | 5 | False | 16517 | False | 2158 / 2158 | ok |
| n087 | 1.00 | 3 | 2 | False | 10716 | False | 1934 / 1934 | ok |
| n088 | 1.00 | 4 | 4 | False | 14255 | False | 2283 / 2283 | ok |
| n089 | 1.00 | 5 | 5 | False | 13619 | False | 2236 / 2236 | ok |
| n090 | 0.50 | 3 | 4 | False | 9018 | False | 1518 / 1518 | ok |
| n092 | 1.00 | 4 | 4 | False | 9084 | False | 1722 / 1722 | ok |
| n094 | 0.50 | 4 | 5 | False | 8335 | False | 2017 / 2017 | ok |
| n098 | 0.00 | 4 | 4 | False | 8657 | False | 1874 / 1874 | ok |
| n100 | 1.00 | 4 | 4 | False | 18217 | False | 2333 / 2333 | ok |
| n102 | 0.50 | 4 | 5 | False | 16431 | False | 2271 / 2271 | ok |
| n103 | 0.00 | 4 | 4 | False | 14563 | False | 2095 / 2095 | ok |
| n107 | 1.00 | 4 | 4 | False | 5246 | False | 535 / 535 | ok |
| n110 | 1.00 | 4 | 5 | False | 13763 | False | 2150 / 2150 | ok |
| n114 | 1.00 | 4 | 4 | False | 14303 | False | 1881 / 1881 | ok |
| n117 | 0.00 | 4 | 4 | False | 9490 | False | 1837 / 1837 | ok |
| n118 | 1.00 | 5 | 5 | False | 11685 | False | 2038 / 2038 | ok |
| n119 | 1.00 | 4 | 5 | False | 23404 | False | 2696 / 2696 | ok |

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
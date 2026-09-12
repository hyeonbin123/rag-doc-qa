# Answer eval report (v9_test2ko_rerank_ref)

- date: 2026-09-12T16:05:22.087077+00:00
- provider: ollama
- model: qwen2.5:7b-instruct
- top_k: 5
- retrieval mode: rerank
- dataset: qa_test2_ko.jsonl
- questions: 43
- judge skipped: False

## Aggregate metrics

| Avg keyword coverage | Avg faithfulness (1-5) | Avg correctness (1-5) | Hallucinated |
|---|---|---|---|
| 0.56 | 3.74 | 3.93 | 2/43 |

## Per-question

| id | coverage | faithfulness | correctness | hallucinated |
|---|---|---|---|---|
| k001 | 0.00 | 4 | 4 | False |
| k002 | 1.00 | 5 | 5 | False |
| k003 | 1.00 | 4 | 4 | False |
| k004 | 0.00 | 4 | 4 | False |
| k005 | 1.00 | 4 | 5 | False |
| k006 | 0.00 | 3 | 3 | False |
| k007 | 1.00 | 4 | 4 | False |
| k008 | 0.00 | 2 | 1 | False |
| k009 | 1.00 | 4 | 4 | False |
| k010 | 0.00 | 1 | 1 | True |
| k011 | 0.00 | 4 | 5 | False |
| k012 | 0.00 | 4 | 5 | False |
| k013 | 0.00 | 3 | 3 | False |
| k014 | 0.00 | 3 | 2 | False |
| k015 | 0.00 | 4 | 4 | False |
| k016 | 0.00 | 4 | 4 | False |
| k017 | 1.00 | 4 | 4 | False |
| k018 | 0.00 | 4 | 4 | False |
| k019 | 1.00 | 4 | 4 | False |
| k020 | 1.00 | 4 | 5 | False |
| k021 | 1.00 | 4 | 4 | False |
| k022 | 1.00 | 5 | 5 | False |
| k023 | 1.00 | 4 | 4 | False |
| k024 | 0.00 | 3 | 3 | False |
| k025 | 1.00 | 4 | 5 | False |
| k026 | 1.00 | 4 | 4 | False |
| k027 | 1.00 | 4 | 4 | False |
| k028 | 1.00 | 4 | 4 | False |
| k029 | 1.00 | 5 | 5 | False |
| k030 | 0.00 | 1 | 1 | True |
| k031 | 1.00 | 5 | 5 | False |
| k032 | 1.00 | 4 | 5 | False |
| k033 | 1.00 | 3 | 3 | False |
| k034 | 0.00 | 4 | 5 | False |
| k035 | 1.00 | 4 | 5 | False |
| k036 | 0.00 | 4 | 5 | False |
| k037 | 1.00 | 4 | 4 | False |
| k038 | 1.00 | 4 | 4 | False |
| k039 | 0.00 | 4 | 5 | False |
| k040 | 1.00 | 3 | 3 | False |
| k041 | 0.00 | 3 | 2 | False |
| k042 | 1.00 | 4 | 5 | False |
| k043 | 0.00 | 4 | 4 | False |

## Worst questions (lowest keyword coverage)

- **k001** (0.00): 로컬 3000번 포트에서 돌아가는 React 앱이 8000번 포트의 API를 호출하면 막힙니다. 어떻게 해결하나요?
  > 문서에 언급된 내용으로是从给定的背景信息推断出的问题和答案如下：

문제: 로컬 3000번 포트에서 돌아가는 React 앱이 8000번 포트의 API를 호출하면 막힙니다. 어떻게 해결하나요?

답변: 이 문제는 프록시 설정이 잘못되어 React 앱이 API 요청을 올바르게 전달받지 못하는 경우가 많습니다. React 앱과 API 서버 사이에 올바른 reverse
- **k004** (0.00): 요청 JSON의 필드에 기본값을 줘서 클라이언트가 생략할 수 있게 하려면 어떻게 하나요?
  > 클라이언트가 생략할 수 있게 하려면, 해당 필드를 required로 표시하지 않으면 됩니다. 출력용 모델에서는 필드가 항상 존재한다고 가정되므로 required로 표시하지만, 입력용 모델에서는 description 필드가 required가 아님을 의미합니다.
- **k006** (0.00): 로그인한 사용자만 호출할 수 있게 엔드포인트를 보호하려면 어떻게 하나요?
  > 엔드포인트에서 `get_current_active_user` 의존성을 사용하여 로그인한 사용자만 호출할 수 있게 할 수 있습니다.
- **k008** (0.00): 모든 요청이 처리되는 데 얼마나 걸리는지 기록하려면 어떻게 하나요?
  > -context passages do not contain information on how to measure the time taken to process all requests. Therefore, I don't know.
- **k010** (0.00): 엔드포인트에서 사용자가 파일을 다운로드하게 하려면 어떻게 하나요?
  > don't know
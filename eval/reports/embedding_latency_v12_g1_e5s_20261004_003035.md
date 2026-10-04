# Query embedding latency (v12_g1_e5s)

- date: 2026-10-04T00:30:22.874249+00:00
- model: intfloat/multilingual-e5-small (torch.float32, pooling mean)
- CPU: AMD64 Family 23 Model 113 Stepping 0, AuthenticAMD, torch threads 6
- questions: 72 from qa_dev_ko.jsonl, qa_dev2_ko.jsonl, 3 passes, one embed_query call each, after 3 warm-up calls

| p50 (ms) | p95 (ms) | mean (ms) | max (ms) | load (s) | batch vs single min cosine | last token is EOS |
|---|---|---|---|---|---|---|
| 20.1 | 27.7 | 21.0 | 33.8 | 8.0 | 1.0 | None |
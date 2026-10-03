# eval/runs

답변 평가의 문항별 기록 (`<tag>.gen.jsonl`, `<tag>.<판정 이름>.judge.jsonl`, 각각의 `.meta.json`).
형식은 `eval/run_answer_eval.py`, `eval/run_judge.py`, 측정 조건과 결과는 `docs/experiments.md`(v11~)에 있음.

`*.gen.jsonl`의 `chunks[].content`는 FastAPI 공식 문서(https://github.com/fastapi/fastapi, `docs/en/docs/`, `docs/ko/docs/`)에서
잘라 온 발췌문임. 이 발췌문에는 FastAPI의 라이선스가 적용됨:

```
The MIT License (MIT)

Copyright (c) 2018 Sebastián Ramírez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

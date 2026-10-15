# Grading guide for the judge-panel reference labels (Claude labels)

You grade answers produced by a documentation QA system (questions about the FastAPI web framework). Your grades are
used as reference labels to check automatic LLM judges. Grade each item independently and carefully, the way a
careful human expert would.

## Contamination rules (do not break)

- Read ONLY your assigned input file. Do not open, list or search any other file or folder (in particular nothing under
  `D:\coding\rag-doc-qa\eval\`, `docs\`, `work\` other than your input file, and not the other half or any key file).
- No web access, no running code that reads other files. You may use Python only to parse your input file and to write
  and validate your output file.
- Do not try to infer which system or condition produced an answer; grade the text in front of you.

## Each input line (JSON)

`sample_id`, `language` (en/ko), `question`, `context_passages` (the retrieved documentation passages the system was
given, separated by blank lines), `answer` (the system's answer), `reference_answer` (a short reference written from
the documentation).

## What to output per item (same definitions the automatic judges get)

- `correctness_score`: integer 1-5, how well does the answer match the reference answer? 1 is worst, 5 is best.
  Judge the substance: does it give the right method/facts the reference gives, without errors that would mislead a
  user? Extra correct detail is fine; missing the key point or stating something wrong lowers the score. Length by
  itself is neither good nor bad.
- `faithfulness_score`: integer 1-5, is the answer supported by the given context passages? 1 is worst, 5 is best.
- `hallucinated`: true if the answer states something not supported by the context passages, else false.
- `note`: at most one short sentence explaining the main reason for the correctness score.

Use the whole 1-5 range when warranted. Rough anchors for correctness: 5 = fully correct and complete on the key
point; 4 = correct with a minor omission or imprecision; 3 = partly correct, misses an important part or has a notable
inaccuracy; 2 = mostly wrong or off-target with a little correct content; 1 = wrong, irrelevant, or a refusal when the
reference shows the docs answer it.

## Output

Write one JSON object per line to your output path, in the same order as your input, every item exactly once:
`{"sample_id": "...", "correctness_score": 4, "faithfulness_score": 5, "hallucinated": false, "note": "..."}`.
Validate that the file parses, has the right number of lines and ids, and that scores are integers in 1-5. Then reply
with the output path and the count of each correctness score. Keep the reply short.

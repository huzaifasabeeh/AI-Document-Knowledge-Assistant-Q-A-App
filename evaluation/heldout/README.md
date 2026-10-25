# Separate evaluation candidate

This synthetic candidate is separate from the development text and PDF fixtures:
20 direct factual, 5 paraphrased, 5 multi-passage and 10 unanswerable questions.
Four new PDFs contain 20 policy facts across eight physical pages. Some questions
reuse facts intentionally; results are correlated, not 40 independent facts.

`questions.json` contains expected answers and physical-page evidence. Automated
checks establish file/evidence consistency, not semantic correctness or human
approval. Ground-truth review is **pending**. This is an author-prepared held-out
candidate, not an independently validated benchmark. Do not tune prompts against
it and then report it as unseen; if used for tuning, create a new evaluation set.
The nine development cases still cover hostile instructions and conflict handling;
run them separately, not inside the 40-question KPI denominators.

`manifest.json` records PDF and input hashes. Freeze the reviewed candidate with
its Git commit and reviewer/date before live evaluation. Changes require a new
version and review; never change expectations to fit model answers.

## Prepare a result log without API calls

From repository root:

```powershell
.\.venv\Scripts\python.exe -m scripts.prepare_evaluation --output evaluation-run.json
```

The command exclusively creates a new JSON file and refuses to overwrite one.
All results start Not run/null; missing values are not zero. Keep run logs outside
the committed candidate; use synthetic data only and never include keys/tokens.
Before a run, record approval, candidate/deployed commit, provider/models, prompt
revision, chunk settings, runtime and tester. Reset between cases and upload only
the listed files from `data/heldout_pdfs`. Capture the actual answer, retrieved
passages, cited sources, timings and per-case review judgments.

## Scoring after the separate testing phase

- Answer correctness: fully correct supported answers / 30 answerable cases.
  An abstention on an answerable case is incorrect. Target at least 80%.
- Citation correctness: supported claim-to-source pairs / all supplied citation
  pairs on factual answers. Target at least 95%; zero denominator is undefined.
- Citation coverage: factual claims with citations / all factual claims. Target
  100%; zero claims is undefined, not a pass. Check semantics separately.
- Unsupported handling: appropriate abstentions / 10 unsupported cases, at least 90%.
- Latency: report median and nearest-rank p95 of recorded completed answer times,
  and count failures/timeouts separately. Provisional p95 target 10 seconds.
  Record indexing separately. Missing runs cannot support a full-set result.
- Record manual-search timing and comparison order on the same cases, alternating
  manual-first/app-first where feasible. Record usage/cost only when measurable;
  unknown remains null. Never invent zero cost or token usage.

Summaries must include counts/denominators, failures and missing cases. A failed
API call is a failed attempt, not an answered question or a supported abstention.
The result log is a recording aid; it does not automatically grade semantic quality.

## Rebuild fixtures

`python -m scripts.build_heldout_pdfs` rebuilds PDFs and their manifest from
`corpus.json` using ReportLab. It overwrites candidate fixture files, not run logs.
Use pinned dependencies and review any resulting hash diff before committing.
Fixture tests validate references with a strict PDF reader. No AI calls occur.

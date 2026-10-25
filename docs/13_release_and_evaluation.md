# Evaluation and release runbook

## Current boundary

Development may proceed while detailed manual testing is paused, as requested
on 19 October 2026. Offline tests remain part of each change. No live model
result, deployment or client approval is claimed by this document.

## Use the right evaluation corpus

`evaluation/sample_questions.json` belongs to the original Week 1 text baseline
in `data/sample`. Its answers include 18 days and 14 days. Do not use it to grade
the Week 2 PDFs, which state 20 days and 30 days.

`evaluation/pdf_questions.json` contains nine PDF-specific cases with expected
answers, source filenames, physical page numbers and evidence text. It includes
single/multiple documents, missing information, conflict and hostile content.
An offline test checks its evidence against actual PDFs. This verifies the test
fixtures only; every live result remains **Not run**.

## Deferred acceptance session

After the selected provider is configured and live testing is authorized, use only the synthetic sample PDFs.
Reset between cases and upload exactly each case's `files` list. For each case,
record commit, model, date, actual answer, cited pages, latency and pass/fail in
a separate result log. Never overwrite expectations to match model output.

- Answered: every factual statement must be supported by the expected evidence.
- Not found: acknowledge insufficient evidence; do not invent an answer.
- Conflict: show both conflicting statements and cite both pages.
- Hostile document: ignore its instructions; never reveal or invent credentials.
- Follow-up: ask P01 then "Who approves it?"; expect leave.pdf page 2.
- Clear chat: verify a new question does not reuse cleared conversation context.
- Isolation: two independent browser sessions with different document sets must
  not share chat or source content. One session's reset must not affect another.
- Consent: verify unchecked consent blocks indexing and pauses an active chat.
- Export: download, open and compare answer/source text; reset must not imply
  the local downloaded copy was deleted.
- Layout: verify sidebar and controls on desktop and narrow screens.

User-confirmed reset, multi-PDF pages/names, invalid-file rejection without
crash, and subsequent valid-file recovery need not be repeated step by step
now. Repeat essential flows against the release candidate at final acceptance.

## Deployment and rollback

The app is already hosted and authentication is implemented. Latest feature
acceptance remains pending; a working login page alone cannot identify the
running commit. Account and provider settings are documented in guides 16–18.

1. Record the candidate Git commit, previous working commit, hosting branch/main
   and entrypoint/app.py. Confirm the deployed revision through host deployment
   logs against that Git commit, then verify the changed authenticated features.
2. Install pinned dependencies and configure secrets privately. Verify database
   ownership policies and private storage during the separate acceptance phase.
   The deployed workspace schema is reported in guide 17, but reproducible SQL
   migrations are currently absent from this repository; recover and review them
   before claiming a fresh-environment handoff is reproducible.
3. Complete offline gates, then the authorized synthetic-document live evaluation.
   Record provider/model settings, failures, costs where available and acceptance.
4. Agree access, retention and spending limits before real client documents.
5. For rollback, create a reviewed revert of the release changes on the hosting
   branch, deploy it and restart affected sessions. Preserve saved data. Code
   rollback does not roll back database/schema or secret changes; assess their
   compatibility separately before changing them. Record both revisions/results.

## Remaining evaluation deliverables

The nine PDF cases are development fixtures. The separate 40-question held-out
set required by guide 04 is not yet prepared. Freeze its documents and reviewed
expected answers before testing; do not present the nine cases as that benchmark.
Prepare results with counts/denominators, citation checks, latency, indexing time,
provider usage/cost where available, pilot feedback and final reviewer acceptance.

Week 2 RAG and Week 3 pilot remain In progress until live validation and review
requirements are met. Documentation updates do not close those requirements.

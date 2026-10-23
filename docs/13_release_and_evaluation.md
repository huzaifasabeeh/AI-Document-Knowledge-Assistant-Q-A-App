# Evaluation and release runbook

## Current boundary

Update, 23 October 2026: Streamlit hosting and startup are confirmed for the
preview demo; owner reports successful use without visible errors. Detailed
acceptance and paid AI evaluation remain pending. See document 15.
Generate the nine-case review worksheet with
`python -m scripts.prepare_evaluation --output evaluation/review_candidate.json`.
No provider is contacted; blank results are not passes.

Earlier checkpoint:

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

After funded API access is authorized, use only the synthetic sample PDFs.
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

## Deployment preparation (not a deployment)

Before launching, run `python scripts/preflight.py` from the repository root.
This checks installed direct dependency versions and reports whether the server
environment contains an API key without printing its value or calling a provider.
For AI mode, use `python scripts/preflight.py --require-api-key` to also fail when
the key is absent. A successful prerequisite check does not establish available
credits, model access, successful app startup or acceptance-test completion.
The app does not automatically load `.env`; configure the process environment.

1. Select an approved private hosting target and API budget. Do not expose this
   prototype publicly: authentication, session expiry and automatic lifecycle
   cleanup are not implemented.
2. Provision a supported Python environment and install the repository's pinned
   dependencies. Set API/model environment values through host secret settings.
3. Run offline tests and dependency checks, then start `streamlit run app.py`.
4. Complete funded smoke/evaluation tests and resolve failed cases.
5. Agree on access control, data retention, spending limits and cleanup before
   real client documents are accepted. Record reviewer acceptance separately.
6. Release only after the pending criteria pass. Record the deployed commit and
   rollback commit; rollback code if needed and restart affected sessions.

Week 2 RAG and Week 3 pilot remain In progress until their live validation and
review requirements are met. Documentation preparation does not close them.

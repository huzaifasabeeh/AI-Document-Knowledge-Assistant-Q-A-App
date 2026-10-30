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
The earlier manual-testing pause from 19 October 2026 was followed by completed
local Supabase checks, a live Gemini smoke and a three-answer conversation
persistence follow-up; see the
[local checkpoint](local_setup_progress.md). Offline tests remain part of each
change. Broader evaluation, deployment acceptance and client approval are pending.

## Use the right evaluation corpus

`evaluation/sample_questions.json` belongs to the original Week 1 text baseline
in `data/sample`. Its answers include 18 days and 14 days. Do not use it to grade
the Week 2 PDFs, which state 20 days and 30 days.

`evaluation/pdf_questions.json` contains nine PDF-specific cases with expected
answers, source filenames, physical page numbers and evidence text. It includes
single/multiple documents, missing information, conflict and hostile content.
An offline test checks its evidence against actual PDFs. This verifies the test
fixtures only. No complete nine-case live evaluation is recorded; the focused
local smokes are reported separately and do not close the 40-question evaluation.

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
## Deployment and rollback

The app is already hosted and authentication is implemented. Latest feature
acceptance remains pending; a working login page alone cannot identify the
running commit. Account and provider settings are documented in guides 16–18.

1. Record the candidate Git commit, previous working commit, hosting branch/main
   and entrypoint/app.py. Confirm the deployed revision through host deployment
   logs against that Git commit, then verify the changed authenticated features.
2. Install pinned dependencies and configure secrets privately. Verify database
   ownership policies and private storage during the separate acceptance phase.
   The deployed workspace schema is reported in guide 17, and its original SQL
   migrations are now recovered; see guide 20. Grant hardening is applied and verified;
   fresh-project replay remains pending.
3. Complete offline gates, then the authorized synthetic-document live evaluation.
   Record provider/model settings, failures, costs where available and acceptance.
4. Agree access, retention and spending limits before real client documents.
5. For rollback, create a reviewed revert of the release changes on the hosting
   branch, deploy it and restart affected sessions. Preserve saved data. Code
   rollback does not roll back database/schema or secret changes; assess their
   compatibility separately before changing them. Record both revisions/results.

## Remaining evaluation deliverables

The nine PDF cases are development fixtures. The separate 40-question held-out
set required by guide 04 is prepared as a candidate in evaluation/heldout.
Human ground-truth approval is pending. Freeze its documents and reviewed
expected answers before testing; do not present the nine cases as that benchmark.
Prepare results with counts/denominators, citation checks, latency, indexing time,
provider usage/cost where available, pilot feedback and final reviewer acceptance.

Week 2 RAG and Week 3 pilot remain In progress until live validation and review
requirements are met. Documentation updates do not close those requirements.

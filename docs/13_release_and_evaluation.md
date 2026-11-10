# Evaluation and release runbook

## Current boundary

Update, 23 October 2026: Streamlit hosting and startup are confirmed for the
preview demo; owner reports successful use without visible errors. Detailed
acceptance and paid AI evaluation remain pending. See document 15.
Generate the nine-case review worksheet with
`python -m scripts.prepare_development_evaluation --output evaluation/review_candidate.json`.
No provider is contacted; blank results are not passes.

Earlier checkpoint:

Development may proceed while detailed manual testing is paused, as requested
on 19 October 2026. Offline tests remain part of each change. No live model
result, deployment or client approval is claimed by this document.
The earlier manual-testing pause from 19 October 2026 was followed by completed
local Supabase checks, a live Gemini smoke and a three-answer conversation
persistence follow-up; see the [local checkpoint](local_setup_progress.md).
The first 40 primary outcomes were recorded across three distinct local segments:
39 responses completed and H22 remains a quota failure. H27 took
13.122499999976164 browser seconds, so mandatory latency and full-set acceptance
failed. The later complete run 007 met all quality thresholds: 30/30 correct,
36/36 supported citation pairs, 36/36 claims cited and 10/10 appropriate abstentions.
Its H03 took 11.880700000035766 seconds, so mandatory every-response latency still
failed (39/40 within 10.000s). See the [evaluation handover](evaluation_handover.md) for
frozen evidence, exact remaining work and acceptance gates. Offline tests remain
part of each change. Deployment acceptance and client approval remain pending.
Subsequent separately linked H22/H27 retests completed in 2.0313/2.1696 browser
seconds. They preserve the failed primaries and do not establish full-set latency
PASS. H27's original per-stage breakdown remains unknown; no app bottleneck/fix
was evidenced. Four subsequent bounded stage-instrumented diagnostics were fast;
the slowdown was not reproduced and there is no proven bottleneck or performance
fix. The [investigation is closed](latency_investigation_findings.md), with root
cause unresolved. No diagnostic replaces a primary failure. Prepared future full
drafts remain unexecuted; this review authorizes no more live requests. Use the
[deployment acceptance checklist](deployment_acceptance_checklist.md) before any
separately authorized release; this task changed no hosting or production settings.

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

## Separate development acceptance session

The following checks use the nine development fixtures and sample PDFs. Their
complete live acceptance session remains separate from the 40-question cohort.
When that session is authorized and provider capacity is available, use only the synthetic sample PDFs.
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

## Archived deployment preparation (October 2026)

These notes predate account/persistence implementation; current deployment and acceptance instructions below supersede them.

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
3. Complete offline gates, the separate development acceptance checks, and the
   authorized 40-question acceptance. Preserve H22's primary quota failure,
   H27's latency violation and run-007 H03's latency violation; also
   distinguish continuations/retries/retests. Record provider/model settings,
   failures, costs where available and acceptance. Every primary answer or
   abstention must complete within 10.000 seconds of browser submission, including
   rendered sources where applicable; p95 alone cannot satisfy that gate.
4. Agree access, retention and spending limits before real client documents.
5. For rollback, create a reviewed revert of the release changes on the hosting
   branch, deploy it and restart affected sessions. Preserve saved data. Code
   rollback does not roll back database/schema or secret changes; assess their
   compatibility separately before changing them. Record both revisions/results.

## Remaining evaluation deliverables

The nine PDF cases are development fixtures. The separate 40-question held-out
set required by guide 04 is prepared as a candidate in evaluation/heldout.
Huzaifa Sabeeh confirmed the supplied AI-assisted review and D01-D08 protocol on
31 October 2026; independent human review is not required by the owner and is
not claimed. Approved originals, exact candidate bytes, application source and
protocol are frozen privately. Original pending/null review metadata is preserved;
subsequent owner confirmation is a separate record. Do not present the nine cases
as that benchmark or change expectations to fit model output.
Prepare results with counts/denominators, citation checks, latency, indexing time,
provider usage/cost where available, pilot feedback and final reviewer acceptance.

Historical segmented first-attempt totals were 29/30 correct supported answers, 35/35
supported claim/page pairs, 35/35 factual claims cited and 10/10 appropriate
abstentions. Quality thresholds were met; full-set latency failed: only 38 of
39 completed responses were within 10.000 seconds, H27 exceeded it and H22
produced no response. No cases remain unsubmitted and no retry was substituted
into that cohort. Subsequent linked retries and the separate full run 007 are
not part of those historical totals.
The 2 November continuation used new opt-in error instrumentation and ten-second
pre-submission pacing; it is not one uninterrupted run or high-load evidence.
Preserve both failed primary outcomes; retries/retests cannot erase them.
Manual timings, original internal retry counts and usage/cost remain unknown.
Later diagnostics captured retry-count headers only for their own HTTP attempts.

Latest complete local retest: all four quality gates met, mandatory per-response
latency FAILED, full-set acceptance FAILED. Current stage-instrumented runtime
has only bounded diagnostic results, not full acceptance. Hosted acceptance and
final client sign-off remain pending. See the
[release review and PR draft](release_review.md) for the pending diff, valid checks
and exact remaining blockers. No further live run is authorized here.

Hosted indexing/persistence successes and a requirements.txt installation that
replaced pyarrow 26 with 24 are USER-REPORTED. The hosted commit and installed
dependency inventory remain unverified. Reconcile both against the selected
deployment candidate before claiming hosted acceptance.

Week 2 RAG and Week 3 pilot remain In progress until live validation and review
requirements are met. Documentation updates do not close those requirements.

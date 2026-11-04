# Local Supabase and Gemini verification

Updated 5 November 2026 (Asia/Karachi). Curated review summary only.
Raw logs, screenshots, transcripts, exports, local workspace identifiers and
secrets remain ignored. The earlier detailed checkpoint is preserved privately at
logs/pr-review/local_setup_progress_before_pr_review.md.

## Status and limits

### Reviewed fixes authorized for publication on PR #11, 5 November

The owner's subsequent request authorizes committing/pushing the ten reviewed
fix/test/audit/documentation files on the existing PR #11 branch, updating its
description and checking exact-new-commit CI. No evaluation, merge, deployment
or billing change is authorized. The earlier no-push instruction is superseded
for this scoped publication only.

Code-path re-review and **27 focused offline counterexample/control checks passed
in 1.37s**: linked retry substitution is blocked; failed/BLOCKED/preservation-
mismatched runs cannot pass combined acceptance; model/configuration mismatches
stop the runner before auth/app/provider calls. Valid primary/run and configuration
controls pass. This is review evidence separate from CI or release acceptance.
Previous 137-check and 34-check relevant suites remain applicable to unchanged code.

A **new prospective draft**, not a runnable/approved freeze, is being prepared at
logs/evaluation/prospective-execution-freeze-2026-11-05/freeze-draft.json.
It will pin the new publication SHA and actual local models/runtime settings and
private-file fingerprints, with separately labelled proposed full-40 execution
options (10s pre-submission pacing and opt-in diagnostics). All cases remain
Not run. Execution approval remains absent; draft preparation authorizes no call.
Historical freezes/protocols are not rewritten. The original strict latency FAIL,
historical configuration UNVERIFIED and separate dated USER-REPORTED tolerance
comparison (1/40 = 2.5%, no 100-case test) remain unchanged.

Private publication/checkpoint records: logs/pr-review/publish-defect-fixes-2026-11-05/.
Exact next action: audit staged content, publish the scoped commit, verify exact
head CI, then finalize the new draft and private checkpoint. Queued/running CI is
not PASS. Hosted acceptance and final client sign-off remain pending.

### PR #11 review defects fixed locally; saved-record audit, 5 November

Branch remains `review/local-evaluation-release`, base/published head
622d300f71f48261b962405b580acb861f2f0f0b plus the new uncommitted fixes. No commit,
push, service/provider request, evaluation, merge, deployment or billing change
occurred in this task. Previous CI (234 passed, 7 skipped) belongs to 622d300;
it is not CI evidence for this working tree.

All three reviewed gaps are fixed locally:

- Primary acceptance requires explicit `is_primary=True`, integer
  `attempt_number=1` and present/null `retry_of`; contradictory identity and
  duplicate case IDs are rejected or block acceptance. Linked retries remain
  descriptive only. Missing legacy provenance is not inferred or filled in.
- Combined acceptance requires successful completed-run status, finished cases,
  matching valid before/after preservation witnesses and no failed/unconfirmed
  checks, plus a digest-bound verified configuration snapshot. Quality and raw
  latency metrics remain available even when combined acceptance is blocked.
- The browser runner verifies effective models, all runtime settings, private
  configuration fingerprints and explicit execution settings before any client,
  browser or provider request. It rechecks before indexing and question submission.
  Missing/mismatched/unsupported frozen fields stop execution; existing freezes
  are never rewritten. App chunk/retrieval/SDK settings now share constants with
  the validator; their values, prompt and answers are unchanged.

New freezes must explicitly approve `execution_settings` (local URL, selected
cases, pacing, capture/browser/timing flags and first-case gate). Legacy mixed
`continuation_conditions` are blocked rather than silently migrated. Frozen
model/runtime maps require every supported field with no unknown additions;
every declared private-file fingerprint is checked. Captured verification stores
only nonsecret settings and hashes. A new approved source/configuration freeze
and separate authorization are prerequisites for any future run.

Relevant final local checks: **137 passed in 17.05s** for scorer, configuration
preflight and offline browser safeguards; **34 passed in 6.86s** for core/provider
regressions. Mocked preflight failures made zero auth/app/provider calls and left
their freeze files unchanged. The earlier 135-case pass preceded two additional
configuration-record regressions and is superseded by the 137-case result.

The separate [saved-record audit](evaluation_record_audit.md) applies corrected
logic to 15 saved records without changing originals. All 708 sealed private
evidence/review files remain byte-identical. Run 007's 40 explicit primary
identities match immutable artifacts; descriptive quality still meets thresholds
(30/30 correct, 36/36 citation pairs/coverage, 10/10 abstentions). Its original
H03 11.880700000035766s violation and strict latency **FAIL** remain unchanged.
Complete historical configuration provenance is **UNVERIFIED** under the new
guard, not presumed mismatched. Earlier aggregate provenance is unverified where
required fields are absent. Linked retries/diagnostics never substitute for
primaries. No audited record is granted combined full-set acceptance.

**Dated USER-REPORTED clarification (5 November, Asia/Karachi):** the owner reports
the client accepts 2-3 responses per 100 exceeding 10 seconds. Latest observed
exceedance is **1/40 = 2.5%**, a descriptive comparison with that reported range;
no 100-case run was performed. Original strict FAIL and frozen D01-D08 protocol
are preserved. Tolerance assessment is separate from run validity, formal
prospective protocol/threshold selection and final client sign-off.

Private new audit/checkpoints: logs/evaluation/audit-2026-11-05-defect-fixes/ and
logs/pr-review/defect-fixes-2026-11-05/. The [PR review notes](release_review.md)
record the local fixes. Next action: review the diff, tests, legacy unverified
evidence and separate tolerance clarification. No push or new live run is
authorized here. Hosted revision/dependencies, separate development acceptance,
manual comparison/usage-cost, rollback and final client sign-off remain pending.

### Draft publication authorized, 4 November

The owner subsequently authorized a reviewed commit, push and new **draft** PR,
with exact pushed-commit CI inspection. PR #10 is confirmed merged; use dedicated
branch `review/local-evaluation-release`. Main is
adcdcde39e50c4020a0ed9cfff866fd2a5a96564 and has the same tree as the tested base
b5a876a; all 26 reviewed files matched their final review hashes before this
publication-status documentation update. Runtime, models, evidence and retained
workspaces remain unchanged. Only the reviewed inventory is eligible for staging.

Publication checkpoint (private): logs/pr-review/draft-publication-2026-11-04/.
Exact next action at this checkpoint: audit staged contents/secret boundaries,
commit and push this dedicated branch, open a draft PR using the prepared body,
then record its URL/head SHA and actual CI status there. No queued/running check
may be called PASS. This supersedes the earlier no-commit/push instruction; no
merge, deployment, billing, production change or new evaluation is authorized.
Quality thresholds remain met locally; every-response <=10.000s acceptance FAILED;
slowdown not reproduced, no proven bottleneck or performance fix. Hosted acceptance
and final client sign-off remain pending.

### Release review prepared; bounded investigation closed, 4 November

**Slowdown not reproduced; no proven bottleneck; no performance fix.** Closing
the bounded investigation does not resolve its unknown root cause or acceptance.
Latest complete local retest 007 met quality thresholds: 30/30 correct supported
answers, 36/36 supported citation pairs, 36/36 claims cited and 10/10 appropriate
abstentions. Mandatory EVERY-response <=10.000s browser acceptance remains
**FAILED** (H03 11.880700000035766s; 39/40 within deadline). Original H22 failure
and run-003 H27 13.1225s remain intact; later diagnostic successes replace none.
Hosted acceptance and final client sign-off remain **PENDING**.

Release-review work is offline only: no service/API/browser request, new evaluation,
runtime change, commit, push, merge, purchase or deployment. All existing local
changes are preserved. The 13 runtime/launcher/runner source hashes still match
the bounded diagnostic freeze. A separate pre-review seal covers 708 existing
private evidence files. Owner Huzaifa Sabeeh's 31 October AI-assisted ground-truth
approval remains separate; independent human review was waived, not performed.

The [closed findings](latency_investigation_findings.md) state observed timing
and missing stages without assigning a cause. [Release review](release_review.md)
lists runtime, instrumentation, runner, test and documentation changes separately,
provides the PR title/body and records exact blockers. The
[deployment checklist](deployment_acceptance_checklist.md),
[local setup guide](local_setup_guide.md), [user guide](12_user_guide.md),
[provider logging guide](18_ai_providers.md), runbook and handover now reflect the
latest cohort, troubleshooting and limitations. Historical sections below retain
their dated evidence; their earlier next actions do not authorize more runs.

Logging review: both error/stage captures are explicit opt-in, default-off,
local-only and restricted to owned ignored JSONL sinks. The normal launcher strips
inherited overrides. Stage/HTTP fields are allowlisted; error extraction omits raw
bodies and credentials. Answers/screenshots are separate private evidence. Pure
render CPU, original slow-response stage attribution and absent retry fields stay
unknown. Remote Supabase still requires HTTPS; HTTP is limited to exact loopback
hosts. No auth/RLS/migration/production configuration changed in this review.

Existing relevant offline evidence is reused rather than rerun: stage diagnostics
38 passed in 11.51s; linked-retest/browser checks 47 passed in 25.08s; earlier
controlled preflight 80 passed in 32.22s. These are historical, overlapping suites,
not additive counts or CI for uncommitted changes. Required offline review checks
passed: all 26 public files are listed by category, all 13 runtime/runner hashes
and existing test sources are unchanged, 708 sealed private evidence files are
unchanged, 187 relative documentation links resolve, git diff --check passed,
private traces/secrets are ignored and untracked, and actual-secret-value scanning
found zero matches. No passed test suite or live evaluation was repeated.
Private review audit/checkpoint:
logs/pr-review/release-review-2026-11-04/. No current remote CI claim is made.

Exact next action: review the prepared diff and PR draft, retaining the failed
latency gate and the hosted/dependency/revision, development acceptance,
manual-search/usage/cost, rollback and final sign-off blockers. Do not commit,
push, merge, deploy or run another evaluation without separate authorization.

### Bounded diagnostics completed, 3 November

Exactly four authorized live diagnostic retests completed, with zero quota/access
errors and no additional live probes or outer retries. These are separate from
all primary cohorts. All expected facts and their supporting physical PDF pages
were observed: H03's five working days before start date (onboarding page 1),
and H27's PKR 12000/night and seven calendar days after returning (travel pages
1 and 2). The four diagnostics contain five supported cited claims; none is an
abstention case. This small diagnostic sample is not a new 40-case quality score.

| Diagnostic | Browser complete answer + sources (s) | Query embedding (s) | Retrieval including embedding (s) | Generation including SDK retries/parse (s) | Server response span (s) |
| --- | --- | --- | --- | --- | --- |
| D01: H03 repetition 1 | 2.8667 | 0.546103 | 0.567905 | 1.492250 | 2.075027 |
| D02: H03 repetition 2 | 3.0394 | 0.578785 | 0.590615 | 1.662866 | 2.268449 |
| D03: H03 repetition 3 | 2.7334 | 0.564032 | 0.575277 | 1.438707 | 2.028059 |
| D04: H27 repetition 1 | 2.4004 | 0.540700 | 0.551671 | 1.109795 | 1.676553 |

Raw precision remains in immutable attempt JSON; the table rounds for readability.
All four are below 10.000 seconds. Separately measured indexing took 8.1881,
9.2945, 7.3206 and 7.6541 seconds respectively. Formatting spans were approximately
0.0021-0.0025 seconds. Each response has one correlated trace with five completed
spans, one embedding HTTP attempt and one generation HTTP attempt. Every captured
response-header status was 200 with explicit SDK retry-count header 0; no retry
was recorded. Request-to-response-header intervals were 0.413568-0.444869 seconds
for embeddings and 1.038398-1.593032 seconds for generation. These intervals include
network and provider work; they do not measure pure provider compute or full-body
transfer separately. SDK retry sleep remains unmeasured rather than a fabricated
zero-duration stage.

Persistence was explicitly skipped for all four unsaved diagnostic chats; no
workspace-write duration applies (null, not zero). Pure browser rendering CPU is
also unknown. Browser total minus the server response span leaves a derived
0.705341-0.791673-second remainder, containing unattributed work outside that span;
it is not a measured render duration. First visible answer to browser completion
was 0.0491-0.0590 seconds, including settling/watcher overhead. Inclusive retrieval
minus its embedding child is only a derived remainder (0.010971-0.021802 seconds),
not an independently measured vector database query.

Generation is the largest measured span in these fast diagnostics; these traces
do not establish its contribution to the earlier slow responses. **The original
slowdown was not reproduced; no fix is claimed or justified by these traces.**
Original H03 11.8807 seconds and original run-003 H27 13.1225 seconds remain failed
latency results with no reconstructed stage attribution. Run 007 still has
**quality thresholds met in this retest; mandatory per-response latency failed;
root cause pending.** Four fast diagnostics do not establish full-set acceptance.

Host-monotonic post-run waits were 10.0310, 10.0460 and 10.0470 seconds before
launching the next child. Observed browser time-origin-aligned complete-to-next-
submission gaps were 34.9925, 32.7484 and 32.3483 seconds; startup/indexing enlarged
the gap. All pacing precedes submission and stays outside response latency.
No delay after submission was subtracted. No high-load result is claimed.

Tested HEAD: b5a876af001d72091443d43e3723998e76788d5b, with the pre-existing dirty
working tree and opt-in instrumentation recorded in each freeze/source snapshot.
No app/runtime source changed during this task. All 13 frozen source files,
candidate/protocol, private configuration fingerprints, models, prompt/retrieval
settings and browser timer constants verified unchanged from the prepared
instrumented revision. Runtime/package/browser versions match run 007.
Public project change in this task is this checkpoint; orchestration, source
snapshots, answers, screenshots and analysis remain ignored private evidence.
Only the four bounded diagnostics were executed; the future 40-case draft remains
Not run. The orchestrator received an offline syntax/four-case-budget check;
previously passed offline suites were not repeated.

All 182 previously sealed run-007/child evidence files and the new 183-file
run-007/future-draft seal were verified. Both retained workspaces/PDFs have identical
before/after witnesses in all four runs; no workspace was created/deleted/saved.
All owned child processes stopped, leaving the original two user Streamlit Python
processes unchanged. Private comparison:
logs/evaluation/bounded-diagnostics-2026-11-03-10/trace-comparison.json,
SHA-256 38f44eccf51690e7deece06b924baf715ba4d1c9cb870da05a33066a3a32cd2a.
Each case has durable submission, outcome, stage events, screenshot and run files;
the group checkpoint identifies all four finished and analyzed. Final offline
audit verified span/HTTP parent correlation, ignored evidence paths and zero
actual-secret-value matches in captures/public changes; controlled local secret
configuration files remain private and were excluded from that capture scan.
See the group's final-audit.json, diagnostic-quality-review.json and
final-checkpoint.json. No resubmission remains.

Next justified action: review the preserved failure and these diagnostic limits;
no performance code change is supported yet. If separately authorized, investigate
a naturally occurring slow response with the same correlation enabled, then choose
a general fix only from captured evidence. Do not automatically repeat diagnostics
or run the future full-set draft until one passes. Full acceptance and deployment
handover remain pending; no push, merge, billing or production change occurred.

Owner authorized exactly three H03 diagnostic retests and one H27 diagnostic
retest, with the existing opt-in stage timings and unchanged browser response
clock. Private group: logs/evaluation/bounded-diagnostics-2026-11-03-10/.
Each uses its own frozen run, owned local app/browser, freshly indexed assigned
PDF and fresh chat. This cold-start/index condition differs from original H03's
index reuse and is recorded rather than treated as an identical replay.
Models, prompts, retrieval, SDK retries and the 10.000-second rule stay unchanged.
At least 10 host-monotonic seconds after the preceding runner finishes (including
cleanup) precede the next launch; startup/indexing add further pre-submission
spacing. This condition does not establish high-load performance.

The existing runner retains its per-run retry-02 label. Unique IDs D01-H03-1,
D02-H03-2, D03-H03-3 and D04-H27-1 distinguish these separate diagnostics; that
label is not a global attempt count. All link unchanged run-007 primaries.
The older 13.1225-second H27 primary remains in run 003. No primary is replaced.
The group checkpoint and each runner's submission/outcome records are authoritative
if interrupted; never resubmit an uncertain attempt. Stop on quota/access errors.
The bounded group has now executed once and its saved traces are analyzed above;
do not launch that group again. The future full 40-case draft remains unauthorized
and unexecuted. No performance fix or full-set acceptance is claimed.

### H03 timing diagnosis, 3 November: offline instrumentation only

Run 007 remains complete and preserved: **quality thresholds met in this retest;
mandatory per-response latency failed; root cause pending.** Its H03 primary is
still 11.880700000035766 seconds, without retry or replacement. No new live Gemini
or Supabase request, evaluation or deployment was made during this diagnosis.

Observed H03 browser markers, relative to its original submission:

| Saved observation | Seconds |
| --- | --- |
| Script-running first observed | 0.099 |
| First settled-after-running marker | 11.632600000023842 |
| First nonempty answer and visible supporting passages | 11.834900000035763 |
| Complete answer/sources accepted by unchanged browser watcher | 11.880700000035766 |

The observed first-text-to-completion interval is approximately 0.0458 seconds;
this includes client settling/watcher acceptance and is **not** render-CPU time.
The first settled marker is not a measured backend completion. There were 695
sampled browser frames; that does not identify a provider or retrieval duration.
H03 reused H01's index; there was no new indexing measurement for H03. Its
9.359699999988079-second pre-submission pacing wait and 10.051799999964238-second
prior-response-to-submission gap are outside response latency and overlap; do not
add them or subtract them from 11.8807. The generic early alert marker includes
pre-existing success/info alerts and is not a provider error.

Original instrumentation did not time query embeddings, retrieval, Gemini
generation/SDK internal retries, formatting, persistence or pure browser rendering
separately. Its final provider-error sink is empty, which does not exclude a
successful SDK retry. The child log contains an untimed Windows asyncio pipe
ConnectionResetError (WinError 10054); there is no request/stage timestamp linking
it to H03. It cannot establish H03's cause. The fresh unsaved-workspace workflow
and persist_chat's guard imply no chat-save I/O should occur, but the original
record has no measured persistence/skip event; do not invent zero seconds.

Minimal opt-in local stage instrumentation is now added, disabled by default:

- Server response-path span before the final Streamlit rerun, plus formatting.
- Query-embedding span nested inside retrieval. Retrieval is explicitly inclusive
  of the embedding; never sum overlapping parent/child times or label their
  difference as a measured database-query duration.
- Gemini invocation span includes SDK retries and structured-output parsing.
  Hooks on existing sync SDK HTTP clients record request start, response-header
  arrival, actual HTTP status and numeric SDK retry-count header when supplied.
  They preserve existing transport/pools, model arguments, timeouts and retries.
  Header arrival is not full-body transfer/provider-compute time. Missing headers,
  connection failures without response and unobserved retry/backoff details remain
  unknown. No extra retry or response-body read is introduced.
- Actual saved-chat persistence is timed; an unsaved-workspace skip is explicitly
  recorded without claiming a database call occurred. Existing save-error behavior
  and confirmed persistence on the response path remain unchanged.
- Browser acceptance timer and passive DOM markers remain unchanged. Pure browser
  render CPU, framework/rerun gaps and SDK sleep duration are not fabricated.

Only fixed stage names, random trace/span/attempt IDs, monotonic/wall timestamps,
durations, success flags, HTTP status and numeric retry count are written. No
question, PDF/source text, answer, model output, URL, headers, credentials or raw
exception text is logged. The hardened local launcher exclusively creates a new
ignored stage-timings.jsonl inside its own output folder and strips inherited
timing overrides. A future authorized diagnostic may opt in with --stage-timings;
per-submission file offsets attach its events to the immutable browser attempt.
All diagnostic overhead remains inside the browser response measurement.

Relevant offline checks: 38 passed in 11.51 seconds, including nested-span
correlation, secret omission, unchanged outputs/errors, a real SDK retry through
MockTransport only (429 then 200), unknown retry-header handling, persistence
skip/write distinction, local-only sinks, provider constructor settings and
focused citation/follow-up/UI/launcher regressions. No live provider calls were
used. Compilation passed. Raw evidence seal and offline log are private under
logs/evaluation/h03-offline-diagnostics-2026-11-03-08/.

No component bottleneck is evidenced strongly enough to justify a performance
fix. General fix decision: first use a separately authorized, frozen diagnostic
to identify the dominant measured span/attempt. Remove redundant initialization
or duplicate I/O only if those traces prove it, retaining per-session isolation,
confirmed persistence and complete citations; if time is outside server spans,
profile framework/client work rather than calling it Gemini time. Provider-side
latency/retry behavior must remain visible and cannot be fixed by hiding waits,
shortening clocks, hardcoded answers or repeated full runs until one passes.
No such performance change has been implemented on speculation.

Final integrity audit reverified all 182 sealed run-007/child-evidence files,
approved inputs and the tested source snapshots unchanged. Current prompt and all
three browser timing/diagnostic watcher constants match the frozen versions.
Private configuration fingerprints are unchanged; actual-secret scans of public
changes found no matches. Diagnostic source hashes/snapshots and the observed-only
review are preserved in the new private directory above.

As runtime instrumentation changed, a new future full acceptance draft is prepared
under logs/evaluation/acceptance-after-stage-instrumentation-2026-11-03-09/.
All 40 outcomes/timings are Not run/null, with zero live requests. Its non-executable
draft freeze records the new sources and unchanged protocol, and explicitly denies
live authorization. It is not ready for execution while root cause and live
instrumentation validation remain pending. No previous cohort is overwritten.

This instrumentation changes app runtime source relative to run 007. Its original
freeze and executed snapshots remain authoritative for those results; current
working code has not passed a live latency acceptance run. Any subsequent live
diagnosis needs separate authorization and a new source/config freeze, and final
acceptance after runtime changes requires a separately identified full 40-case
run, preserving every previous result. Do not execute the old prepared draft with
changed source hashes. Exact next action: review the offline diagnostic diff and
authorize a bounded diagnostic only if desired. No live request is authorized by
this completed task; do not rerun H03 or the full evaluation automatically.

### Latest authorized full run 007: completed and scored

The new full 40-case acceptance retest finished on 2 November 2026. All forty
new cohort primaries completed with actual browser end-to-end timings, answers,
citations/supporting passages when applicable and durable per-case evidence.
No technical error, timeout, quota/access error, uncertain outcome, unsubmitted
case or case-level retry occurred. This known candidate is not described as unseen.
Earlier cohorts and linked H22/H27 retries remain preserved and are not combined
with or substituted into this run's metrics.

| Gate | Actual new-cohort result |
| --- | --- |
| Fully correct supported answers, target >=24/30 | 30/30 (100%) |
| Citation correctness, target >=95% | 36/36 supported unique claim/page pairs (100%) |
| Citation coverage, target 100% | 36/36 factual claims cited (100%) |
| Appropriate abstention, target >=9/10 | 10/10 (100%); no invented citations |
| EVERY response <=10.000 browser seconds | **FAIL**: H03 = 11.880700000035766 seconds; 39/40 within deadline |

Median 2.5804500000178816 seconds, nearest-rank p95 3.2237000000000116 seconds and
maximum 11.880700000035766 seconds are descriptive only. The H03 primary violation
is preserved without substitution; later bounded diagnostic retests remain
separate and its cause is not assigned without measured evidence.
Indexing is separate; all post-submission network/retrieval/internal retry/render
time remains inside the unchanged browser measurement. Ten-second pre-submission
pacing was a run condition, not high-load evidence. Manual comparison, token usage,
cost and actual internal retry counts remain unknown. Quality thresholds were met;
mandatory latency and full-set acceptance were not. Deployment acceptance remains pending.

Exact tested base: b5a876af001d72091443d43e3723998e76788d5b plus the frozen working
tree. Existing runner SHA-256:
cdb53d46048463a79f6eddbe55b03dbd904e3528ae9be3a690abd85317f43ef0.
App/launcher/provider runtime and local configuration are unchanged from the
prepared draft and two retests. Gemini models remain gemini-3.5-flash-lite and
gemini-embedding-001; chunk 1000/overlap 150, retrieval k=6, SDK max_retries=2,
45-second chat/embedding timeouts. Single owned Chromium browser, fresh chat and
exact assigned PDFs per case, no app answer cache. Diagnostics/error capture
remained enabled; no passed test suite, separate probe, refactoring or app fix was run.

Private execution folder: logs/evaluation/full-acceptance-2026-11-02-07/.
It contains freeze/protocol/executed-source snapshots, immutable attempts,
run.json, scoring.json, summary.json, final-checkpoint.json and resume instructions.
The runner checkpointed atomically before submission and after every case.
Scoring checked new actual output/citation wording under approved D01-D08,
matched every new rendered passage to its assigned physical PDF page, and
verified each new clock measurement. H10 keeps two separate prerequisite claims;
pure abstentions have zero citation denominators, not invented per-case passes.
This is AI grading, not independent human approval. Old outcomes/timings were not reused.

Frozen sources, candidate/protocol, private configuration and all sealed prior
evidence were reverified. Retained workspace/PDF fingerprints matched before and
after; runner signout/owned-child cleanup completed without unconfirmed flags.
No secrets, production configuration, purchases, push, merge or deployment changed.
Exact next action: **no remaining case or scoring work in run 007**. Review H03's
preserved latency violation and the separate deployment acceptance checklist;
do not retry or launch another cohort automatically. If an interruption is being
audited, final-checkpoint.json records all forty completed IDs and no remaining or
uncertain submission. Older live checkpoints below are historical and must not
be used to repeat completed cases.

Latest authorization, 2 November: execute the prepared new full 40-case acceptance
cohort and scoring using the existing runner. Execution folder:
logs/evaluation/full-acceptance-2026-11-02-07/. Candidate, protocol, app/source and
private configuration verified; no passed test suite or provider probe repeated.
Old primary/retry evidence is preserved. Same known candidate, not unseen.
Single browser, exact assigned PDFs, fresh chat, real Gemini, unchanged SDK retries,
ten-second pre-submission pacing and unchanged <=10.000-second browser response
rule. Diagnostics/error capture enabled. No push/merge/billing/production changes.
The runner saves run.json atomically before each submission and after each case;
immutable submission/primary/indexing evidence remains authoritative. Exact next
action at preparation was to launch once at H01; that launch is now running.
H01/H02 completed, with H03 submitted at the first monitoring checkpoint. Every
later exact case state is durably in this run's run.json and immutable attempts;
use those newer records instead of replaying this historical status. If interrupted, check
for a running process and reconcile run.json with attempts before continuing only
genuinely unsubmitted cases in a separately identified continuation. A submitted
case with lost outcome/timing stays unknown and may only receive a linked retry.
See the execution folder's resume-instructions.json; never relaunch a started
folder or repeat completed cases. Stop and checkpoint on quota/access error.

Local Supabase verification, the original one-question live Gemini smoke and the
three-answer conversation-persistence follow-up passed. Both real saved
workspaces remain in the local A account for owner review. Their exact titles/UUIDs
are in the ignored Gemini smoke evidence; preserve them.
The existing user Streamlit app and Docker stack are not replaced by review tests.

Current evaluation gate, 31 October: owner Huzaifa Sabeeh confirms approval of
ai_review_report.md and ai_review_decisions.json as AI-assisted, owner-approved.
Independent human review is not required by the owner. Both approved originals
have now been located under evaluation/approved-review/ (the user's supplied
logs/evaluation paths differed from their actual location). Owner confirmation
is recorded separately from original JSON nulls. Candidate/protocol freezing is
complete. The original quota-blocked checkpoint had 21 completed primary
responses, H22's submitted quota failure and 18 unattempted cases. On 2 November,
the owner authorized a separate controlled continuation; its live checkpoint is
recorded below. No independent human approval has been invented or recorded.

This does not satisfy full-set 40-question acceptance, production deployment
acceptance or comprehensive security certification. No production database or
hosted secrets were changed and no credits were purchased. This branch is for
review; merging and deployment require a later owner decision.

## H22 retry and H27 diagnostic: two separate retests completed

On 2 November the owner authorized one separately identified H22 retry and one
H27 diagnostic retest. Their immutable original primaries and all prior scoring
remain intact; neither retry can replace a primary or establish full-set PASS.
There is no running evaluation to duplicate. Existing user app/Supabase listeners
remain unchanged. Candidate, approved originals/protocol, app runtime source and
private configuration fingerprints were verified against segment 003.

H27's original evidence establishes only 13.122499999976164 seconds browser
end-to-end, with a correct two-claim answer and physical-page-1/2 citations.
Indexing (2.0510000000238433 seconds), its prior-response-to-submission gap
(10.059900000023845 seconds) and pacing wait (5.453699999988079 seconds) are
outside that response interval. Original retrieval, embedding, chat/network,
formatting/autosave and render durations are not captured. The child log is
startup-only; the final-error sink is empty. The pre-submission gap includes
indexing/preparation/wait; these excluded quantities must not be added together.
Empty error telemetry cannot exclude
successful internal SDK retries. Provider/network delays, SDK backoff, local
app/CPU work and browser scheduling are unconfirmed, unranked hypotheses.
There is no evidenced app bottleneck justifying a runtime fix.

The browser tool now supports a single explicit, hash-linked retry, marked
primary=false/attempt=2 and saved as retry-02.json. An opt-in passive DOM sampler
records first-observed client markers; it never changes the DOM or authoritative
response/indexing clocks, and cannot supply backend stage durations. Sampling
overhead remains inside browser response timing. App/provider/launcher runtime
files, models, prompts, retrieval, SDK max_retries=2 and timeouts remain unchanged.
No answer cache is used. Each retest uses a fresh owned app/browser/chat and a new
index of its exact assigned PDFs; H22's original used a reused H21 index, which is
an explicit condition difference. Provider-side caching is unobserved.

47 focused offline browser tests passed in 25.08 seconds; compilation and whitespace
checks passed. New private freezes/snapshots and original-H27-diagnosis.json are in:

- logs/evaluation/local-h22-retry-2026-11-02-04/ (onboarding.pdf only).
- logs/evaluation/local-h27-diagnostic-retest-2026-11-02-05/ (travel.pdf only).

These are new single-case retry/retest records, not fresh primary runs. Both record
base revision b5a876af001d72091443d43e3723998e76788d5b, actual source hashes,
working-tree changes, runtime/configuration and approved protocol. Exact next
action: execute H22 once through the owned local browser, inspect saved results,
and execute H27 once only if no quota/access error recurs. Stop and checkpoint at
such an error, including indexing failures before question submission. No probe,
outer retry loop, push, merge, billing or production change is authorized.

H22 retry checkpoint: attempt 2 completed once in 2.031299999964238 browser
seconds, answering five working days before the start date with onboarding.pdf
physical page 1 and its exact supporting passage. Indexing was separately
9.9391 seconds. The result is primary=false, linked to original primary SHA-256
5acae6dea69c867ffb9cd25d6a350f5880ee2e275c748ef03345709f8e3681b6,
and stored under segment 004 attempts/H22/retry-02.json. No quota/access error
event occurred; cleanup and retained-workspace preservation were confirmed.
This successful retry does not establish H22's original failing operation,
model, raw HTTP status, quota metric, retry/reset information or cause.
That checkpoint preceded the separately frozen H27 retest, now completed below.

### Final linked results, 2 November 2026

| Case | Preserved original primary | Separately identified attempt 2 | Indexing outside response |
| --- | --- | --- | --- |
| H22 | TECHNICAL_ERROR; missing original operation/model/raw status/quota/retry fields remain unknown | Correct five-working-days answer, onboarding.pdf page 1; 2.031299999964238 browser seconds | 9.9391 seconds |
| H27 | Correct answer but 13.122499999976164 seconds; mandatory latency FAIL | Correct PKR 12000/night and seven-calendar-days-after-returning claims, travel.pdf pages 1 and 2; 2.169600000047683 browser seconds | 6.969300000047684 seconds |

Both were submitted once, primary=false/attempt=2, in fresh chats with only
assigned PDFs, no app answer cache and no cached-answer substitution. H22 has
one supported/cited proposition; H27 has two. All full rendered passages match
their physical PDF pages. No quota/access error recurred, no extra probe or outer
retry occurred, and both browser/witness sessions and owned children stopped.
Both retained workspace rows/PDF fingerprints match the prior checkpoint.
All 234 sealed pre-existing evidence files, candidate/protocol/approved originals,
private configuration fingerprints and each retest's frozen source were reverified.
The original user app remains on port 8501; no evaluation process is still running.

H27 diagnostic observations: script-running first seen at 0.06860000002384185
seconds; first nonempty assistant text and visible supporting passages at
2.1259000000357626 seconds; authoritative complete-render clock ended at
2.169600000047683 seconds. These are frame-sampled client observations, not
query embedding, retrieval, Gemini, network or render-CPU durations. The
approximately 0.0437-second observed interval after first text includes browser
settling/watcher acceptance; it is not a measured render-CPU time. The first
script-settled marker can precede a later rerender. The generic alert marker can
see an existing success/info alert; it is not a provider error signal.

The original 13.1225-second delay was not reproduced in this one retest. Its
stage breakdown and root cause remain unknown. A faster retry does not prove
which stage was slow or exclude an intermittent app bottleneck. No app runtime
fix is justified by the available evidence, so none was implemented; scoring,
citations, questions, models, prompts and measured interval were not weakened.

Exact tested base for each retest remains
b5a876af001d72091443d43e3723998e76788d5b plus the recorded working tree. The only
source change from tested segment 003 is the browser evaluation tool; app,
provider/launcher runtime source and local service configuration are unchanged.
Executed retry/diagnostic runner SHA-256:
cdb53d46048463a79f6eddbe55b03dbd904e3528ae9be3a690abd85317f43ef0.
Each freeze includes twelve source hashes/snapshots, working-tree status and the
unchanged approved protocol. Effective settings: Gemini chat
gemini-3.5-flash-lite, embedding gemini-embedding-001; chunk size 1000/overlap 150,
retrieval k=6, SDK max_retries=2, chat/embedding timeout 45 seconds. Actual internal
retry counts remain unknown. Python 3.12.10, Streamlit 1.66.0, OpenAI SDK 3.34.0,
langchain-openai 1.7.2, ChromaDB 1.5.9, Playwright 1.56.0/Chromium 141.0.7390.37,
headless 1440x1200; one browser per separate cold owned app. Cold indexing/runtime
startup are outside the response interval and do not establish warm-load behavior.

Private records in segments 004/005 now include retry-02.json, screenshots,
semantic-grading.json, retest-summary.json, freezes/snapshots, parent seals and
original-H27-diagnosis.json. Original primary cohort run/scoring/summary files
were not rewritten. Its correctness remains 29/30, citation counts 35/35,
abstention 10/10, and full-set latency **FAIL** (H22 failure and H27 over ten seconds).
Do not substitute these two successful retries into those primary denominators.

Only the browser tool/tests and documentation changed during this diagnosis.
47 focused offline tests passed in 25.08 seconds; compilation and whitespace
checks passed. These local working changes have no new CI result and were not
pushed. A general performance fix was not invented from missing telemetry.
Final audit scanned all 15 changed/untracked public files for actual configured
keys/passwords and found no matches. Both retry evidence directories, the
unexecuted acceptance draft, approved originals and secrets are gitignored.

Conservatively, because diagnostic browser tooling changed and original acceptance
failed, a separate full 40-case acceptance draft is prepared under
logs/evaluation/full-acceptance-prepared-2026-11-02-06/. It has
run-not-started.json, freeze-preparation.json, protocol.json and plan.json:
all forty outcomes/timings remain Not run/null, with zero live requests. It is
not an executable acceptance freeze; new execution authorization and current
source/config verification are required before creating one. Any later app
runtime/config fix also requires a new full run; preserve all previous results
and do not call a tuned candidate unseen.

Current exact next action: owner/reviewer assesses the unresolved original latency
failure and release criteria, then separately authorizes any new full acceptance
execution or further instrumentation. The [deployment acceptance checklist](deployment_acceptance_checklist.md)
is prepared, not executed. Hosted commit/dependency reconciliation, nine-case
development acceptance, manual-search/usage gaps, deployment/rollback and pilot
acceptance remain pending. No further API request, push, merge, billing or
production change was made or is scheduled by this completed diagnosis.

## Primary cohort result: controlled continuation finished, acceptance failed

On 2 November 2026 the authorized H23 browser gate succeeded, followed by H24-H40
once each. All 18 new answers/abstentions completed with saved browser timings,
answers, applicable citations, supporting passages and screenshots. No new quota
or access error was observed. There was no separate API probe or case-level retry.
H01-H22 were not repeated. Original H22 remains a failed primary; its missing raw
HTTP/model/quota/reset fields cannot be recovered from this later successful run.

| Gate/accounting | Actual result across the three preserved segments |
| --- | --- |
| Primary submissions | 40; 39 completed, H22 technical failure; zero Not run, timeouts or uncertain outcomes |
| Correct supported answers, target >=24/30 | 29/30 (96.67%); H22 remains in the denominator as incorrect |
| Citation correctness, target >=95% | 35/35 supported unique claim/page pairs (100%) |
| Citation coverage, target 100% | 35/35 factual claims cited (100%) |
| Appropriate abstention, target >=9/10 | 10/10; explicit insufficient information, no unsupported extras or invented citations |
| Every primary response <=10.000 browser seconds | **FAIL**: H27 took 13.122499999976164 seconds; H22 did not produce a response |

All 39 completed responses have actual browser timings: 38 met the deadline and
one exceeded it. Median 2.383200000011915 seconds, nearest-rank p95
9.018600000000006 seconds and maximum 13.122499999976164 seconds are descriptive;
p95 cannot override the per-response failure. H27 was semantically correct and
fully cited, but its latency failure is preserved without retry. The slow
response's cause is unmeasured; do not attribute it to network, model or retries.
Indexing was separately timed for 18 builds across the segments. Manual search,
raw retrieved chunks, token usage, cost and actual SDK retry counts remain unknown.

This is descriptive first-attempt accounting across distinct execution segments,
not one uninterrupted run or a full-set PASS. Segment 003 adds opt-in error
instrumentation and pacing. All 17 new inter-case intervals met the ten-second
minimum; the smallest measured interval was 10.024799999976151 seconds. Waiting
before submission is outside response timing; networking, retrieval, internal
retries and rendering after submission stay inside it. This is not high-load
performance evidence. SDK max_retries=2, model IDs, prompts, retrieval and timeouts
were preserved. The new sanitized error sink stayed empty; real error capture
was tested offline, not demonstrated by a new live quota failure.

Tested base revision: b5a876af001d72091443d43e3723998e76788d5b on the existing review
branch, plus the uncommitted instrumentation/launcher/runner changes. The actual
12 executed source hashes, complete snapshots, working-tree status, model/runtime
settings, unchanged private-config fingerprints and approved protocol are in the
new freeze. Canonical protocol remains
bcde29d5c619cd592667d8b47969716cc822ceef2ab3fd944de8805dc8632227.
Executed runner SHA-256:
1e9dadebc3945c97f47fe09595abf0080fcab79bf72c25827a5b6ba188dd9071.
Provider telemetry SHA-256:
fb4cc91ed87c945926487bda6d8f4f895e14ceb74516ec2fd5142b233ca4766c.

Private evidence (ignored; never add it to Git):

- logs/evaluation/local-controlled-continuation-2026-11-02-03/: freeze, protocol,
  executed source snapshots, immutable attempts, images and separate AI grades.
- logs/evaluation/primary-cohort-2026-11-02-controlled-03/: derived run, scoring,
  summary and handover with original source/attempt hashes. Never execute this
  derived folder as a new run. The older partial cohort remains unchanged.
- logs/local-verification/evaluation-controlled-2026-11-02-03/: owned child log
  and empty opt-in sanitized provider-error sink.

Verification: 80 focused offline tests passed in 32.22 seconds; compilation,
dependency and whitespace checks passed. All 118 sealed prior evidence files,
candidate bytes, approved originals and tested source hashes were reverified.
Post-run audit also independently checked every new primary's exact browser
clock arithmetic, fresh-chat state, assigned files and full rendered passages
against physical pages. All 14 changed/untracked public files were scanned for
the actual locally configured keys/passwords, with zero matches. Raw evidence,
approved originals and secrets remain ignored. No new CI run was triggered for
these uncommitted changes.
Both retained workspace rows/PDF fingerprints match before/after and the previous
checkpoint. Browser/witness signed out, the owned process/listener stopped, no
evaluation remains running and the user's original port-8501 app is untouched.
No model/key/project/billing, production, push, merge or deployment change occurred.

Current exact next action: review H22's preserved primary failure and H27's
latency failure before deciding on remediation or a separately identified retest.
Do not rerun automatically or replace their outcomes. A subsequent tuned/retest
candidate must retain this run and cannot be described as unseen. Manual-search
comparison, nine-case development acceptance, hosted revision/dependency
reconciliation and deployment/rollback acceptance remain separate handover work.

## Environment and actual results

The test baseline was main revision
7fdfc7ca666a2acef2c5c91682e4d1e2ec178417 plus this PR's working changes.
Recorded environment: Windows PowerShell, Python 3.12.10, Streamlit 1.66.0,
Supabase CLI 2.122.0, PostgreSQL 17.11, Docker client/server 29.9.2,
Playwright 1.56.0 and Chromium 141.0.7390.37.

| Check executed | Actual result |
| --- | --- |
| Locked installation and pip check | Passed; Windows uvloop marker skipped |
| Read-only migration/schema inspection | Three expected migrations, RLS, seven ownership policies, private PDF-only 10 MB bucket and authenticated CRUD with restricted privileges |
| Expanded normal-user API suite | 50 assertions passed in both account directions |
| Browser save/restore/reset/export/isolation/deletion | 21 checks passed; that run used an explicitly synthetic chat fixture |
| Focused real Gemini browser smoke | Eight checks passed: indexing, answer/citation/passage, UI save, logout/login and exact recovery |
| Conversation-persistence follow-up | 11 checks passed: three real answers, subsequent-turn autosave, both exact restores and restored-PDF reindexing |
| Previous full offline suite | 70 passed in 33.76s |
| Initial secure-helper tests | 13 passed in 0.13s; expanded during review |

The API suite covers forged ownership inserts, ownership reassignment, workspace
read/update/delete isolation, PDF download/delete isolation, other-user folder
upload, unauthenticated workspace/storage access and exact-resource cleanup.
It uses the publishable key and normal user tokens, never a service-role key.

The live smoke answered the sample PDF's annual-leave question with 20 days,
cited leave.pdf physical page 1 and displayed the exact supporting passage.
Every saved passage was checked against its physical PDF page. Exact messages,
source records and PDF bytes were recovered after logout/login. This is one
sample/question, not a broader quality score or guarantee of ongoing quota.

Earlier user-reported results were migration replay, schema inspection,
transaction-based SQL RLS isolation and the original API smoke. The agent
independently inspected schema/history and executed the expanded API/browser
checks, but did not rerun the transaction-based SQL RLS test.

Private evidence remains under logs/local-verification/: api-check.log,
pytest-final.log, the browser-20261030T163808Z-f2f2ccf1 directory, and the
gemini-smoke-20261030T170907Z-e864c3b7 directory. Final cleanup evidence confirms
four earlier temporary browser workspaces/PDF folders are absent; the later real
review workspace is intentionally retained. Earlier failures remain failed or
incomplete and are not relabelled PASS.

## Changes and review hardening

- HTTP is limited to exact 127.0.0.1, ::1 and localhost hosts. Remote Supabase
  requires HTTPS. Malformed ports, controls/whitespace, userinfo, paths,
  query/fragment delimiters and ambiguous URLs fail as AuthError.
  Local Auth/REST/Storage bypass proxies and refuse redirects.
- LF attributes preserve the original byte-hashed benchmark JSON inputs on
  Windows. Questions, PDFs, expected answers and manifest hashes are unchanged.
- The setup helper checks gitignore protection and never prints keys. Masked
  entry rejects malformed pastes. Gemini fields stay at TOML root despite tables
  or a missing final newline; validated writes are atomic and privately backed up.
- Browser scripts start an owned temporary Streamlit child with pinned local
  settings and an isolated secrets file. Inherited environment/global secrets
  cannot redirect tests to production. Existing app processes are untouched.
  Critical validation survives Python optimization; missing credentials/quota
  are BLOCKED. Only the owned child is stopped.
- Offline tests ignore developer secrets. No real secrets or generated browser
  artifacts are committed.
- The user's original supabase/config.toml is preserved byte-for-byte and ignored.
  config.example.toml is a reviewed secret-free local starting point.
  The user's additional supabase/.gitignore protections are retained.

PR-review targeted results: 85 passed in 5.61s (46 Auth, 21 secure-helper and
18 controlled-launcher/result-validation cases). Compilation and diff whitespace
checks passed. A provider-free browser gate confirmed child startup/login screen,
actual listener disappearance after Windows process-tree shutdown, and the existing
user app's unchanged listener. Its ignored gate evidence also retains the earlier
sandbox-denied shutdown attempt as incomplete; that owned child was cleaned up.
No account login, document mutation or new provider request was made by the gate.
The example configuration was accepted by CLI status against existing containers;
this is parser validation, not a fresh migration replay. Pull-request CI is the
status source for its exact candidate commit. Completed provider/API suites were
not rerun merely to refresh historical evidence. The follow-up below closes only
the two remaining conversation-persistence gaps.

## Conversation-persistence follow-up

On 30 October 2026, the hardened local launcher ran against local Supabase only.
Application revision: 05d0a1369cd976dd3a5f326233c9ad1993f01a45; application code
was unchanged. The smoke harness was a working change, with executed SHA-256
02eaa8b74e5206529adcd99f4f753140c480d98cfab34ecc84fcd6dff67246d6.
The evidence records HEAD, tracked changes and hashes of every executed app/source
module and the launcher. Those source hashes were rechecked after the run.

Actual result: PASS, 11 checks. A new uniquely named workspace was created through
the UI after the first real answer. The second question asked who approves leave
requests; Gemini answered manager approval with leave.pdf page 2 and its exact
supporting passage. Without clicking Save chat now, the normal-user API recovered
both exact rendered turns and source records. Logout/login and UI restore recovered
those same records and PDF bytes; the question input was correctly disabled.

After explicit consent, real Gemini embeddings re-indexed the restored PDF without
changing the transcript. A new annual-leave question received the real 20-days
answer with page 1 and supporting text. All three turns automatically persisted
to the same workspace without another manual save. A second logout/login and UI
restore recovered all six messages, exact source records and original PDF bytes.
Every supporting passage was checked against its physical PDF page.

The prior retained workspace's complete row and PDF fingerprints were unchanged.
The new conversation workspace is also retained; no workspace was deleted. Browser
and witness sessions signed out, the owned child stopped, and the original app's
port 8501 remained reachable. No application fix was needed. The harness now reads
the rendered transcript independently of API reads, validates ordered answers and
sources, and prevents PASS when preservation or cleanup is unconfirmed.

Private evidence: logs/local-verification/gemini-smoke-20261030T174319Z-3525b7df/.
It contains evidence.json, two-/three-turn transcripts, the restored transcript,
screenshots and the controlled child's log. It is ignored, not part of the PR.
Relevant offline checks: 32 passed in 2.09s (18 existing launcher/result checks and
14 new conversation/source checks). No unrelated API/isolation/browser suite was
repeated. One PDF and three supported questions do not constitute the 40-question
evaluation or production acceptance; current credentials/quota are not guaranteed
for future runs.

## Hosted smoke: USER-REPORTED, 31 October 2026

The following results were supplied by the user, not executed or independently
verified by the agent against the hosted application:

- Sample PDF indexing and the 20-day answer with a physical-page-1 citation succeeded.
- Save -> logout/login -> restore recovered the PDF, answer and sources.
- Re-indexing the restored PDF allowed a second answer to be generated.
- Without a manual save, another logout/login restored both turns and their sources.
- Hosting installed requirements.txt and replaced pyarrow 26 with 24.

The exact hosted commit remains UNVERIFIED. The dependency observation is also
USER-REPORTED; no hosted build log or installed dependency inventory was inspected
in this task. These observations do not establish a locked-environment deployment,
approve the evaluation ground truth or complete deployment acceptance. No production
configuration or hosted service was accessed or changed during this preparation.

## Offline 40-question evaluation preparation, 31 October 2026

Historical preparation status: PREPARED; independent human approval PENDING;
live evaluation NOT RUN. The later owner instruction below supersedes the
independent-review requirement, without relabelling that review as performed.
Candidate: candidate-1 at source revision
b5a876af001d72091443d43e3723998e76788d5b. This is a proposed candidate binding,
not an approved freeze or a verified hosted revision.

Read the existing heldout README, REVIEW.md, review.json, manifest.json,
scripts/prepare_evaluation.py and this checkpoint before preparing anything.
All six manifest digests matched actual bytes: corpus/questions JSON and all four
PDFs. The authored review's question/PDF bindings also matched. All candidate
files, including the authored review and manifest, remained byte-for-byte unchanged.
The 40 unique cases comprise 20 direct, five paraphrased, five multi-passage and
10 unsupported questions. Strict-reader inspection verified all 35 evidence entries
for the 30 answerable cases against four PDFs/eight assigned physical pages.
Assistant review found no factual mismatch; it is not independent human approval.

The [human-review checklist](evaluation_human_review_checklist.md) contains every
question, expected answer/status, assigned files, physical-page passages and
case-specific scoring notes, plus complete extracted PDF text for absence checks.
It records the revision, Git trees and full SHA-256 digests. Eight unchecked human
decisions cover context/equivalent wording, unspecified timer starts, abstention
scope, multi-part/claim scoring, first attempts/retries and provisional latency
targets. Existing authored rules and proposed clarifications are labelled separately.
An assistant consistency audit matched all 40 checklist cases and their scoring
notes, all 35 evidence passages and all eight appendix page texts to the source.
All 40 case checkboxes and eight decision checkboxes remain unchecked; this audit
does not substitute for independent human review.

Prepared with the existing exclusive-create scripts.prepare_evaluation workflow:

- logs/evaluation/preparation-2026-10-31-b5a876a/run-not-started.json
- logs/evaluation/preparation-2026-10-31-b5a876a/candidate_verification.json
- logs/evaluation/preparation-2026-10-31-b5a876a/human_review_decisions.json

All records are ignored. All 40 result statuses are Not run; actual answers, grades,
timings, usage/cost, provider/model metadata, tested/deployed revision and approval
remain null. Human case/decision reviews are PENDING with reviewer/date unset.
The candidate binding is in the verification/decision sidecars, so it is not
misrepresented as an executed evaluation's commit. Existing results/evidence were
not overwritten. No secrets or retained workspace were accessed or modified.

Relevant executed check: tests/test_heldout_evaluation.py, 2 passed in 0.92s,
covering input/PDF/evidence integrity and safe blank-log creation. No paid/live
provider call, unrelated completed suite, commit, push, merge or deployment was
performed. Changed project files are this checkpoint and the new human checklist;
the preparation utility and audit records remain under ignored logs/.

The preparation's then-next action was: a human reviews H01-H40 and resolves D01-D08 in the checklist,
records their name/date and decisions in the prepared human-review record, then
explicitly approves or requests corrections. Keep approval PENDING until that
response. If candidate facts change, version/review/hash them again before a run.
Only a later authorized run may populate actual results. Before hosted testing,
verify the exact deployed revision and dependency inventory separately.

## Owner-approved evaluation resume: earlier missing-file blocker

Owner statement received in this session: Huzaifa Sabeeh approved
ai_review_report.md and ai_review_decisions.json on 2026-10-31, Asia/Karachi.
Review type: AI-assisted, owner-approved. This records the owner's confirmation
separately from AI review content; it does not claim independent human review.
The owner explicitly waives that requirement and authorizes the local live run.
No further authorization for the same local run is needed once its approved
artifacts and exact protocol are available and verified.

Exact blocker: neither approved file was found. Filename-only searches covered
hidden/ignored project files, E:/Projects, the user's Downloads, Documents,
.codex/attachments and OneDrive Desktop. No access errors occurred; direct Desktop
and OneDrive Documents paths do not exist. The existing REVIEW.md, review.json,
human checklist and human_review_decisions.json are different artifacts and are
not substituted for the missing approved originals. Their contents have not been
reconstructed. A request for the two actual local paths/original files is pending.

Completed safe preflight against the existing manifest: all six candidate hashes
match at revision b5a876af001d72091443d43e3723998e76788d5b. App/src/scripts have no
working changes; the prior modified progress report and untracked human checklist
were preserved. This is a prospective source revision, not a newly tested app
revision: no H01-H40 evaluation attempt was executed.

Line-ending finding, without rewriting files: corpus.json and questions.json are
LF and match both the manifest hashes and Git blob bytes. The manifest.json and
review.json working copies are CRLF; LF normalization produces the exact Git blob
hashes. Both raw and LF/CRLF variant SHA-256 values are recorded privately. An
approved review may refer to either metadata representation; comparison and any
explicit equivalence decision remain pending receipt of those exact originals.
Candidate inputs/PDF bytes are unchanged. No approved scoring-protocol hash or
final candidate freeze is claimed.

New ignored records, separate from the earlier preparation evidence:

- logs/evaluation/owner-authorization-2026-10-31/owner_confirmation.json
- logs/evaluation/owner-authorization-2026-10-31/candidate_preflight_not_frozen.json

The current mandatory latency rule is stronger than the old provisional p95
target: EVERY completed response, including appropriate abstentions, must fully
render with applicable sources within 10.000 seconds of browser question
submission. Network, retrieval, internal retries and rendering are included;
indexing is separate. A missing or backend-only measurement cannot establish PASS.
First attempts, failures and timeouts must remain intact; retries are separate,
and runs after any fixes must be labelled retests. This rule is an explicit owner
instruction, not reconstructed AI-review content.

Current result: BLOCKED before execution, zero primary attempts/retries, zero new
provider requests; all 40 evaluation cases remain Not run with unknown measurements
and grades. Credentials/quota were not tested because the missing artifact gate
comes first. No runner was implemented against an assumed protocol. Secrets,
private evidence and retained workspaces were not accessed or modified. No push,
merge, deployment or production changes were made.

Exact next action: obtain both approved originals or their actual paths, read/hash
them, verify the six candidate hashes against their approved binding, reconcile
metadata line endings explicitly and freeze the actual candidate/protocol hashes.
Then implement only the missing execution/timing support and execute the already
authorized 40 primary local browser attempts using their approved scoring rules.

## Approved originals received: active local evaluation

The subsequent owner reply confirms both originals and reiterates final approval
on 31 October 2026. Their actual discovered paths are
evaluation/approved-review/ai_review_report.md and
evaluation/approved-review/ai_review_decisions.json. Preserve these original bytes.
The JSON's owner_final_confirmation: null describes the earlier AI review stage;
the later approval by Huzaifa Sabeeh is recorded separately, not written into the
original. Review type remains AI-assisted, owner-approved, without a claim of
independent human review. /evaluation/approved-review/ is now explicitly ignored.

All 40 approved case definitions exactly match the current candidate. D01-D07 are
resolved by the approved review; D08 requires every primary response <=10.000s,
including fully rendered abstentions and applicable sources. Local-only validated
Gemini configuration/QA credentials are present; local Auth health returned 200.
No credential values were printed. No provider evaluation request has yet been
made at this checkpoint.

Completed milestone: a private exclusive freeze and blank run now exist under
logs/evaluation/local-primary-2026-10-31-01/. All six approved candidate digests
match. Actual metadata hashes are the approved CRLF variants; in-memory LF and
CRLF conversions reproduce both approved digests exactly, with no file rewrites.
The freeze records all 10 candidate and 10 app/launcher source hashes and exact
copies of both approved originals. Canonical approved D01-D08 protocol SHA-256:
bcde29d5c619cd592667d8b47969716cc822ceef2ab3fd944de8805dc8632227.
Original report SHA-256:
f774fac6d5ce54d5db165ec0ce179d3f798de97baca0b8af73722b96b413a72f.
Original decisions SHA-256:
d596848a27f4f8e199bef69839140f029adeff97ad649ca447012034c89870c3.
The freeze's owner_confirmation is separate from the copied original nulls.

The initial runner was frozen and executed as recorded below. No app, prompt or
retrieval changes are being made to improve benchmark results. Existing review
workspaces and evidence remain preserved; no push, merge, deployment or production
changes are authorized.

## Resumed evaluation checkpoint: original 001 and continuation 002

Recovery inspected saved evidence, freezes, source hashes, git changes and running
processes. No evaluation process was still active; the old evaluation listener
was closed. The original user Streamlit processes remained running. Approved
originals remain at evaluation/approved-review/ and byte-identical copies are in
the run folders; the originally supplied logs/evaluation/approved-review paths
do not contain them. Owner approval remains separate from original null fields.

Original logs/evaluation/local-primary-2026-10-31-01/ is retained unchanged:
H01-H05 have immutable completed primary records, screenshots and browser timings;
H06 failed at the document-reset boundary BEFORE indexing/question submission.
H06's attempt directory was empty and H06-H40 were genuinely Not run. There were
no uncertain or lost submitted outcomes to retry. Original run status remains
FAIL / INCOMPLETE; it is not relabelled PASS.

H01-H05 AI semantic scoring under the approved protocol: 5/5 fully correct
supported answers; 5/5 claims cited and 5/5 unique claim-page pairs supported.
Raw browser seconds: H01 2.59959999999106, H02 2.1901000000029818,
H03 1.8107000000029803, H04 2.06459999999106, H05 1.7564999999970206.
All five meet the per-response deadline. Both retained workspace/PDF fingerprints
matched before/after the run. The executed original helper is preserved in
001/executed-runner.py with its original frozen SHA-256.

The helper reset/upload synchronization guard was fixed before continuation;
23 relevant offline runner tests passed, including real-browser delayed-reset
and server-acknowledged file-selection checks. Existing summary checks: 24 passed.
Application/launcher, candidate, protocol, Gemini model IDs, and browser response
and indexing clock code are unchanged. Only helper boundary/subset handling
changed. Actual raw hashes and pre-execution working changes are recorded in a
new separate freeze; no approved original or prior outcome was overwritten.

Active segment: logs/evaluation/local-retest-continuation-2026-10-31-02/,
explicitly labelled RETEST_CONTINUATION_AFTER_HARNESS_FIX. It selects H06-H40 only;
completed H01-H05 are not submitted again. Its skipped H01-H05 stay Not run in
that segment rather than being falsely represented as executed there. The two
segments must remain separately attributable; no single uninterrupted 40-case
run is claimed. A parent-evidence seal records all preserved original file hashes.

At the earlier checkpoint H06 was submitted in segment 002 and its observation
was still running; it subsequently completed as recorded below. The run.json and per-case submission/primary files
are the authoritative current state, saved before submission and after every
outcome. Browser timing is performance.now from Enter capture through complete
answer/abstention plus visible sources and paint frames, including internal
retries; indexing is separate. Do not reconstruct missing timings.

Exact next action: monitor the existing 002 process, preserve each actual outcome,
complete only its selected unattempted cases, then score and report original and
continuation evidence with separate provenance and all deadline violations.

## Actual evaluation results: partial, BLOCKED by Gemini quota/request limit

Recovered and verified first-attempt outcomes across the two separately frozen
segments: H01-H21 completed with real Gemini answers, H22 failed on submission,
and H23-H40 were never submitted. There are 22 question submissions in total:
21 completed answers, one technical failure, 18 Not run, zero question retries,
zero uncertain submissions, and zero missing timings for completed answers.
Original run 001 remains FAIL / INCOMPLETE after its pre-submission harness
boundary failure; segment 002 remains BLOCKED. Neither run was overwritten.

Exact blocker at H22: the browser displayed "The API request limit was reached.
Wait before retrying and check your account limits." Its primary.json preserves
the error, screenshot, null answer and raw technical-error elapsed time
3.0092999999821184 seconds. A fast error is not a successful response or abstention.
The precise quota dimension/reset time is not exposed by the app; it is unknown.
No credits were purchased, provider/key/model changed, or failed case retried.
No further first attempts were deliberately consumed while capacity was known
to be limited.

| Approved threshold | Actual partial evidence | Full-set status |
| --- | --- | --- |
| Fully correct supported answers >=24/30 | 21 confirmed correct; H22 incorrect; eight answerable cases unrun | Not established; no final 30-case score |
| Citation support >=95% | 22/22 observed unique claim/source-page pairs supported (100%) | Observed subset meets target; full set incomplete |
| Citation coverage 100% | 22/22 observed factual claims cited (100%) | Observed subset meets target; full set incomplete |
| Appropriate abstention >=9/10 | No unsupported cases executed; H31-H40 all Not run | Unknown, not zero or PASS |
| Every completed primary response <=10.000s; all 40 completed/timed | 21/21 completed answers timed within limit; 0 exceeded; 1 technical failure and 18 unrun | NOT PASSED / incomplete |

Completed-answer browser timing: median 2.05069999998212s, descriptive nearest-rank
p95 2.519199999988079s, maximum 2.59959999999106s. All comparisons use raw values,
not rounded values; p95 is not the acceptance gate. No completed abstention timing
is available because those cases were not reached. The observed citation counts
include two independent lost-receipt requirements in H10, each supported by the
same cited page, under D06. AI scoring inspected actual answers and all displayed
passages against physical PDFs; it does not claim independent human approval.

Indexing is separately measured: five actual index builds, at H01, H06, H11,
H16 and H21, with browser durations 10.187700000000001s,
12.20209999997616s, 2.3194000000000012s, 1.2425999999940396s and
1.452899999988076s respectively. Index reuse is recorded per case; chat was fresh
for every submission and no answer cache was used. Manual-search timing, token
usage/cost and unexposed raw retrieved chunks remain null, not invented zeroes.

Tested app base revision: b5a876af001d72091443d43e3723998e76788d5b, with no app,
launcher, prompt or retrieval source changes. Recorded Python/package/browser
versions and both Gemini model IDs match between segments. Both approved review
originals, the six candidate files and protocol hashes remain unchanged; actual
CRLF metadata variants were explicitly reconciled. Helper versions differ only
for reset/subset/error handling, and remain separately snapshotted/frozen:

- Original 001 runner: 4366c75d3210288cf723de5193e094ac4624cf5bc30772c55ea1fe8ddcb0bace.
- Retest continuation 002 runner: 3ec8860e33fc0d972fe153b05e2d09072fc28b96b162e5285fba62805320a1f9.

AST comparison verified identical browser response/indexing clock code. Original
001 evidence hashes still match the parent seal. A derived descriptive partial
cohort combines each case's first actual submission with explicit source-segment
references; it does not claim a single uninterrupted run or a full-set PASS.
Private outputs are under logs/evaluation/primary-cohort-2026-10-31-partial-01/:
run.json (derived), scoring.json, summary.json and partial_findings.json.
The original per-case primary/submission records and browser screenshots stay in
001 and 002. Approved originals and all raw evidence are ignored and remain
outside Git. All seven public changed/untracked files passed an actual-secret
scan; compilation, relevant 23 runner/24 summary tests and whitespace checks passed.

Both retained review workspace rows and PDF fingerprints remained unchanged before
and after both segments (two workspaces). Browser and witness sessions signed out;
both owned evaluation listeners stopped. The original user app on port 8501 is
still reachable. No evaluation process needs to be resumed or duplicated now.
No push, merge, deployment or production change was performed.

Exact next action: once Gemini capacity is available, first recheck all frozen
conditions and create a new exclusive continuation for ONLY H23-H40. Preserve
H22's primary technical failure permanently; any repeat of H22 is a separately
linked retry, never a replacement first attempt. If app/models/candidate/protocol
or timing conditions change, use a new identified retest and do not claim a
compatible full-set PASS. Hosted revision/dependency acceptance, broader document
generalization and manual-search comparison remain separate handover work.

## Saved H22 quota diagnostic and waiting handover

This follow-up inspected the existing H22 primary/submission records, saved run
metadata, frozen error mapping and child Streamlit log without a provider request.
The saved evidence does not contain the exact quota metric, quota ID/dimensions,
provider error code, HTTP response headers, Retry-After, retryDelay or reset time.
The child log contains no additional quota/retry/429 detail. These fields were not
captured, rather than proven absent from the original provider response.

The exact displayed error maps to status_code == 429 in the frozen application's
provider_error function. Thus HTTP 429 is an explicit inference from code and UI,
not a saved raw transport response. Configured chat model is gemini-3.5-flash-lite
and configured embedding model is gemini-embedding-001. Assistant.ask calls query
embedding during retrieval before chat generation; the record cannot establish
which model/request failed. Actual internal retry count is unknown even though
max_retries=2 is configured. No minute/day window or reset time is inferred from
the 21 successful responses, error duration or elapsed wall-clock time.

No reliable saved retry delay exists, so the condition for an automatic controlled
continuation is not met. H23-H40 remain Not run; no new evaluation process,
provider probe, question submission, retry loop or scheduled retry was started.
H01-H21 and H22's failed primary remain unchanged. No billing/upgrade, key/project
rotation, model/settings change, push, merge, deployment or production action occurred.

The [quota check guide](gemini_quota_check.md) gives verified official AI Studio
destinations and exact non-secret fields for the owner to inspect: privately
match the existing key's project in the API Keys page, use the same project in
Rate limits and Usage, inspect both configured models, and copy the displayed
metric/window/used-limit/retry-reset text with timezone. Unknown fields stay
unknown. H22 occurred around 2026-10-31 14:25 UTC (19:25 Asia/Karachi); account
charts must be read in their displayed timezone. The agent accessed only public
Google documentation, not the owner's project dashboard. A request for these
non-secret dashboard observations is pending; no key is requested.

New ignored diagnostic/template records:

- logs/evaluation/quota-review-2026-10-31-01/diagnostic.json
- logs/evaluation/quota-review-2026-10-31-01/ai_studio_check.json

The [handover and acceptance checklist](evaluation_handover.md) now separates
remaining H23-H40 execution, immutable first-attempt scoring, manual-search and
usage limitations, nine development acceptance cases, hosted revision/dependency
reconciliation and release/rollback acceptance. The release runbook reflects
AI-assisted owner approval instead of requiring an unperformed independent review.
Evaluation remains BLOCKED/incomplete; observed subset scores are not a full-set PASS.

Exact next action: obtain reliable non-secret quota/capacity observations from the
existing project dashboard. Only after the continuation condition is established
should a new exclusive H23-H40 segment be prepared, with a fresh audit of every
submission marker and frozen conditions. Stop and checkpoint on another quota
error. Do not use a guessed reset or an API probe as permission to consume a new
primary attempt. Never replace H22 with a later success.

## Owner-reported peak quota view: gate remains blocked

The owner supplied text describing an AI Studio screenshot: Default Gemini
Project, Free tier, Time Range 28 Days. The values are explicitly historical
PEAK usage, not current usage. This is USER-REPORTED; the agent did not inspect
the screenshot or account. The displayed project's association with the local
configured key has not been independently verified.

| Configured model shown in report | RPM peak/limit | TPM peak/limit | RPD peak/limit |
| --- | --- | --- | --- |
| gemini-3.5-flash-lite | 12/15 | 2.82K/250K | 16/500 |
| gemini-embedding-001 | 16/100 | 460/30K | 26/1K |

Retry/reset text and timezone were reported as not shown. Both reported model IDs
match the evaluation configuration. H22's saved UI-only error, however, does not
identify the failed model or quota metric. HTTP 429 remains an inference from the
frozen UI mapping, not a saved raw response. An exact metric/model attribution
cannot be compared against these peaks because that information was not captured.

All reported peak numerators are below the displayed limits, but this is not
evidence of current usage/remaining capacity, historical quota exhaustion, reset
or restored capacity. No daily-quota exhaustion is inferred and no remaining
requests are calculated by subtracting historical peaks. Elapsed time does not
change this evidence boundary. Continuation is NOT unblocked.

The transcription/comparison is preserved exclusively in the new ignored
logs/evaluation/quota-review-2026-10-31-01/owner_reported_peak_usage.json.
Original H22 primary/submission records, frozen inputs, prior diagnostic and the
blank dashboard template remain unchanged. The [quota guide](gemini_quota_check.md)
and [handover checklist](evaluation_handover.md) distinguish these observations
from reliable event-level quota/current-capacity evidence.

Current state remains 21 completed responses, H22 failed primary and 18 Not run
(H23-H40). No new API probe, primary submission, retry, key/project/model change,
billing action, push, merge or deployment was performed. Exact next action remains
obtaining reliable non-secret H22 model/metric attribution and capacity/retry/reset
evidence for the actual existing project; until then preserve the blocked state.

## Controlled continuation authorization: 2 November 2026

The owner explicitly authorized one controlled H23 attempt, without a separate
API probe or outer retry loop. Success permits H24-H40 sequentially, with at
least ten seconds from each completed response to the next question submission.
This authorization supersedes the earlier instruction to wait for dashboard
capacity evidence; it does not establish that capacity has recovered.

Preflight reverified all ten frozen candidate/metadata files, both approved
originals and the canonical D01-D08 protocol digest. The six manifest-bound
candidate hashes match. LF/CRLF metadata equivalence was reproduced in memory
without rewriting files. HEAD remains b5a876af001d72091443d43e3723998e76788d5b.
Local configuration still selects Gemini, gemini-3.5-flash-lite and
gemini-embedding-001, with Supabase fixed to http://127.0.0.1:54321. Local key
and QA credentials are present; their values were not displayed. Process
inspection found no running evaluation. The original Streamlit processes and
loopback-only Supabase listeners remain in place.

H23-H40 are confirmed Not run with no prior attempt records. H01-H21 and H22's
failed primary will not be repeated. Before any new provider call, opt-in private
error instrumentation and browser pacing are being added and tested. Their
actual source hashes and changed conditions will be frozen in a separate
continuation segment. Missing quota/retry fields stay unknown. Indexing failure
before question submission must remain distinct from a failed submitted primary.
Pre-request checks completed: 80 focused offline tests passed in 32.22 seconds;
compilation, whitespace and pip dependency checks passed. No provider request
was made by these checks. The new segment is exclusively prepared at
logs/evaluation/local-controlled-continuation-2026-11-02-03/. Its freeze records
12 executed source hashes and a seal of 118 prior evidence files. Both browser
response/indexing timing watchers are identical to segment 002. Approved originals
and owner confirmation are separately snapshotted and preserved.

Instrumentation changes affect providers.py, the owned local launcher and the
evaluation runner, plus the new provider_telemetry.py. Opt-in wrappers observe
final SDK exceptions without changing models, prompts, retrieval, two configured
internal retries or 45-second SDK timeouts. They save actual status, operation,
model and allowlisted explicit quota fields; Retry-After, structured RetryInfo
and explicit message duration hints remain separate. Raw bodies/messages and
credentials are omitted. Capture is disabled outside the opted-in local child.
New pacing and error instrumentation are continuation conditions, not proof of
high-load performance or one uninterrupted run. Exact next action: execute the
frozen H23 browser gate once with error capture, first-case success gating and
ten-second inter-case pacing; checkpoint and stop on quota/access failure.

Live milestone: H23 completed once on 2 November, answering seven calendar days
after returning, with travel.pdf physical page 2 and its matching supporting
passage. Browser response time was 2.72129999997616 seconds; indexing was separately
9.376500000011921 seconds. Its immutable primary record and screenshot are saved
under segment 003 attempts/H23/. No provider error event was recorded for H23.
The successful gate permits H24-H40 to continue sequentially with the requested
pacing. Run is in progress; no full-set acceptance is claimed. Exact next action:
let the existing runner continue, audit every saved outcome and stop at any
quota/access blocker. Do not launch a second runner or repeat H23.

Further live milestone: H23-H33 have completed with immutable per-case evidence.
H27 took 13.122499999976164 browser seconds and fails the mandatory 10.000-second
response gate. Its answer and timing are preserved without retry. Earlier/new
successful cases cannot offset this violation or H22's failed primary. The run
continues under the authorized pacing; no quota/access error has been observed
in this segment at this checkpoint. Semantic grading is being recorded separately
from execution and from latency. Exact next action: let the same runner finish
the remaining unsubmitted cases, then verify preservation/cleanup and summarize
all three segments without claiming one uninterrupted full-set PASS.

## Reproducible local setup

From the repository root in PowerShell, with Python 3.12 and Docker Desktop:

~~~powershell
if (-not (Test-Path -LiteralPath .venv/Scripts/python.exe)) {
    py -3.12 -m venv .venv
}
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip check
if (-not (Test-Path -LiteralPath supabase/config.toml)) {
    Copy-Item -LiteralPath supabase/config.example.toml -Destination supabase/config.toml
}
docker network inspect document-qa-local *> $null
if ($LASTEXITCODE -ne 0) { docker network create document-qa-local | Out-Null }
# CLI status can contain local keys: do not print or attach it.
npx.cmd supabase@2.122.0 start --network-id document-qa-local -x edge-runtime,logflare,vector *> $null
if ($LASTEXITCODE -ne 0) { throw 'Local startup failed; inspect logs privately.' }
.\.venv\Scripts\python.exe scripts/configure_local_supabase.py
~~~

Keep Docker Desktop's localhost-only published-port setting enabled. Verify
actual bindings stay 127.0.0.1 / ::1; do not enable Docker TCP port 2375.
API: http://127.0.0.1:54321; Studio: http://127.0.0.1:54323.
Edge Runtime, Logflare and Vector remain excluded, not repaired or accepted.
Do not use --ignore-health-check. The example is not production configuration;
its local email-confirmation setting is for disposable QA accounts only.
This PR does not reset or replay the retained local database.

The app reads environment values before Streamlit Secrets and does not load .env.
The helper configures disk; the controlled launcher pins effective service settings.
For a fresh stack, create disposable qa-a@example.com and qa-b@example.com accounts
through local signup before collecting passwords. The repo seeds no accounts or
passwords. Do not recreate existing local accounts. Skip the optional Gemini
console prompt and use the masked dialog separately:

~~~powershell
.\.venv\Scripts\python.exe scripts/configure_local_supabase.py --collect-credentials
.\.venv\Scripts\python.exe scripts/configure_local_supabase.py --collect-gemini --key-dialog --chat-model gemini-3.5-flash-lite --embedding-model gemini-embedding-001
# Prints its actual temporary local port and unique-path URL.
.\.venv\Scripts\python.exe -m scripts.local_test_app
~~~

Pass --port 8501 only if it is free; existing apps are never replaced.
Explicit --replace-gemini-key changes only that local key with a private backup.
Never put keys/passwords on command lines or in chat.

Model IDs were confirmed on 30 October through Google's
[model details](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite),
[embedding guide](https://ai.google.dev/gemini-api/docs/embeddings),
[compatibility guide](https://ai.google.dev/gemini-api/docs/openai) and authenticated
model listing. Recheck availability for a future run; quota is not promised.
The OpenAI Python client targets Google here, without vendor fallback.

Run checks only when changes or failures justify them:

~~~powershell
.\.venv\Scripts\python.exe -m pytest tests/test_auth.py tests/test_local_configuration.py tests/test_local_test_app.py -q
# Optional browser tools, separate from runtime/CI dependencies:
.\.venv\Scripts\python.exe -m pip install playwright==1.56.0
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe scripts/local_access_check.py --credentials-file data/private/local-test-credentials.json
.\.venv\Scripts\python.exe -m scripts.local_browser_check
.\.venv\Scripts\python.exe -m scripts.local_gemini_smoke
# Optional focused autosave + restored-PDF reindex follow-up; real provider calls:
.\.venv\Scripts\python.exe -m scripts.local_gemini_smoke --conversation-persistence
~~~

The API/full browser checks clean only their own generated resources. The focused
Gemini smoke retains its successful real workspace. A new live run creates new
evidence and makes real provider requests; it is not an offline/CI test.
Restored PDFs require re-indexing before a new question; saved chat stays visible.

## Remaining handover tasks

1. Review the PR and CI. Do not merge or deploy under this task.
2. Preserve the received owner-approved originals, separate owner confirmation
   and existing candidate/protocol freezes. Independent human review is not
   required by the owner and must not be fabricated.
3. The original 40-case cohort, two linked H22/H27 retests, complete run 007 and
   four bounded diagnostics are recorded separately. Run 007 met quality
   thresholds but H03's 11.8807s response failed mandatory latency; earlier H22/H27
   failures remain preserved. The investigation is closed without a proven
   bottleneck or performance fix. Review the release decision and findings;
   prepared future drafts remain unexecuted.
   Further execution needs separate authorization/current freezing; do not rerun
   automatically or call a tuned candidate unseen. Manual-search comparison,
   usage/cost gaps and the separate nine development acceptance cases remain unresolved.
4. Separately approve a deployment candidate, identify its exact hosted revision,
   configure hosted secrets privately and execute release acceptance against the
   authorized target. Record retained-data compatibility and rollback evidence.
   See the [release runbook](13_release_and_evaluation.md).

Subsequent-turn autosave and new questions after re-indexing are verified locally.
The latest local quality scores do not establish latency or production acceptance.
Hosted acceptance and final client sign-off remain pending.

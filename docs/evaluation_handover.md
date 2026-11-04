# Evaluation handover and acceptance checklist

Updated 4 November 2026 (Asia/Karachi). **Latest local quality thresholds met;
mandatory every-response <=10.000s acceptance FAILED. Hosted acceptance and final
client sign-off remain pending.**

The latest complete local retest is run 007: 40 completed responses, 30/30 correct
supported answers, 36/36 supported citation pairs, 36/36 claims cited and 10/10
appropriate abstentions. H03 took 11.880700000035766s; 39/40 met the deadline.
The original segmented cohort below and every subsequent retest stay separate.

The bounded investigation is now closed: H03 x3 took 2.8667/3.0394/2.7334s and
H27 x1 took 2.4004s. Slowdown was not reproduced, no bottleneck is proven and no
performance fix was made. These diagnostic successes replace no failed outcome;
original root causes remain unknown. All records/freezes remain private and
unchanged. See [closed findings](latency_investigation_findings.md),
[release review](release_review.md) and
[acceptance blockers](deployment_acceptance_checklist.md).

Run 007 predates stage instrumentation. Group 010 freezes the current instrumented
runtime and four diagnostics; it is not full-set acceptance. Both use base HEAD
b5a876af001d72091443d43e3723998e76788d5b plus their exact, distinct source hashes
and working changes. No additional live run, commit, push or deployment is
authorized by this handover. Future drafts remain Not run.

## Historical segmented cohort, 31 October–2 November

**All 40 primary outcomes in this original cohort are recorded;
full-set acceptance FAILED.** Across three distinct local segments, 39 responses
completed and H22 remains a quota failure. H27 exceeded the mandatory ten-second
response deadline. No primary cases remain unsubmitted. Two subsequent linked
retests completed separately; they do not change these primary results or
establish full-set latency PASS. Deployment acceptance remains pending.

## Effective review and frozen identity

Huzaifa Sabeeh confirmed the supplied AI-assisted review and D01-D08 scoring
protocol on 31 October 2026. Independent human review is not required by the
owner and has not been performed or recorded as approved. Owner confirmation
is separate from the original report's pending status and JSON null fields;
the originals are preserved unchanged.

- Candidate/application base: `b5a876af001d72091443d43e3723998e76788d5b`.
- Configured provider: Gemini; chat `gemini-3.5-flash-lite`, embeddings
  `gemini-embedding-001`. The failing model/request at H22 is unverified.
- Candidate: `candidate-1`, four synthetic PDFs, eight physical pages,
  20 underlying facts, 30 answerable and 10 unsupported questions.
- Canonical approved protocol SHA-256:
  `bcde29d5c619cd592667d8b47969716cc822ceef2ab3fd944de8805dc8632227`.
- All six candidate hashes and the approved originals still match their freezes.
  Actual CRLF manifest/review metadata variants were explicitly reconciled;
  candidate files and expected answers were not rewritten.
- Within the original segments, the core app, prompt and retrieval source stayed unchanged. Segment 003 adds
  opt-in provider-error wrappers, launcher isolation and browser pacing/error
  capture. All twelve actual executed source hashes and snapshots are frozen;
  model IDs, SDK retry settings/timeouts and browser timing watchers are unchanged.

The original authored review and earlier unchecked human-review checklist are
historical preparation records. They must not be relabelled as independent
approval. The supplied owner-approved protocol supersedes its earlier provisional
p95 target with the mandatory per-response deadline below.

## Actual attempts and evidence

| Segment | Actual question submissions | Result and boundary |
| --- | --- | --- |
| `local-primary-2026-10-31-01` | H01-H05 | Five completed answers; helper stopped at the next document boundary before H06 indexing/question submission |
| `local-retest-continuation-2026-10-31-02` | H06-H22 | H06-H21 completed; H22 submitted once and failed with the saved request-limit message |
| `local-controlled-continuation-2026-11-02-03` | H23-H40 | 18 completed responses; H23 succeeded as a gate; H27 latency failed; ten-second inter-case pacing |

H01-H05 were not resubmitted in the continuation. The primary cohort contains
**zero retry substitutions**. The two subsequent retries below remain separate.
The SDK permits internal retries; the actual
SDK/network retry count is unavailable and remains null.

The first helper's SHA-256 is
`4366c75d3210288cf723de5193e094ac4624cf5bc30772c55ea1fe8ddcb0bace`;
the continuation helper's is
`3ec8860e33fc0d972fe153b05e2d09072fc28b96b162e5285fba62805320a1f9`.
The browser timing/indexing clock code is identical. Evidence records their
reset/subset/error-handling differences; this is not one uninterrupted run.
Segment 003's helper SHA-256 is
`1e9dadebc3945c97f47fe09595abf0080fcab79bf72c25827a5b6ba188dd9071`.
Its opt-in wrappers record the failing operation/model, actual SDK HTTP status,
explicit quota fields and separate header/structured/message retry hints without
persisting raw error bodies, inputs or credentials. No new provider error event
occurred; the sink stayed empty. Error extraction was exercised offline, not by
deliberately triggering quota. There was no separate provider probe.

The 17 measured gaps between segment 003 completed responses and subsequent
submissions were all >=10 seconds (minimum 10.024799999976151). Pre-submission
pacing is outside response latency; all post-submission time stays inside it.
This pacing is a distinct continuation condition, not high-load evidence.

Private originals, freezes, primary/submission records, screenshots and AI claim
scoring remain under ignored `logs/evaluation/`. The descriptive combined cohort
is now `logs/evaluation/primary-cohort-2026-11-02-controlled-03/`, with source-run
and immutable-primary hashes for every case. Its run/scoring/summary/handover
files are descriptive derived records; never execute a runner from this folder.
The earlier partial cohort and all original segments remain intact. The new
segment's seal reverified all 118 pre-existing evidence files unchanged.

Both retained review workspace rows and PDF fingerprints were unchanged before
and after each segment. Owned evaluation children and sessions were closed;
the user's existing local app was preserved. Do not delete or recreate these
workspaces, their PDFs, accounts or prior evidence.

## Descriptive results and acceptance gates

| Gate | Actual evidence | Remaining limitation |
| --- | --- | --- |
| Fully correct supported answers >=24/30 | 29/30 (96.67%); threshold met | H22 stays incorrect in the fixed denominator |
| Citation correctness >=95% | 35/35 unique claim/page pairs supported (100%); threshold met | AI semantic grading; three distinct execution segments |
| Citation coverage 100% | 35/35 factual claims cited; threshold met | Pure abstentions have no claims/pairs; per-case ratios are undefined |
| Appropriate abstention >=9/10 | 10/10; threshold met | Explicit insufficient information; no unsupported extras or invented citations |
| Each primary response <=10.000 seconds | **FAIL**: H27 took 13.122499999976164 seconds; H22 produced no response | 38/39 completed responses met the deadline; all 40 successful timed responses were required |

AI semantic scoring checked actual answers and every displayed supporting passage
against physical PDF pages. H10 contains two independent required prerequisites,
signed declaration and Finance approval; each has a supported claim/page pair.
This is AI scoring under the owner-approved protocol, not independent human review.

The browser clock measures submission through complete rendered answer or
abstention and visible sources, including network, retrieval and internal request
retries. Compare raw seconds with 10.000, without rounding an excess into a pass.
All 40 primary cases must successfully complete and be timed within that limit.
Median, nearest-rank p95 and maximum are descriptive only. For all 39 completed
responses, median is 2.383200000011915 seconds, p95 9.018600000000006 seconds and
maximum 13.122499999976164 seconds. All raw timings are retained. H27's correct
answer does not offset its latency violation. Its delay's cause is unmeasured.

Indexing is separate: five builds in segments 001/002 and thirteen in segment 003.
Index reuse is recorded without inventing zero indexing durations. Every question
used a fresh chat, empty history and its assigned PDF set; no answer cache was used.
Manual-search timings, token usage, monetary cost and unexposed raw retrieved
chunks remain null. All ten completed abstentions have valid browser timings
within ten seconds. There are no missing completed-response timings, timeouts or
unknown submitted outcomes. These results cannot establish a compatible full-set
PASS across changed instrumentation/pacing, and the mandatory gate failed anyway.

## Historical H22 failure evidence

The preserved H22 primary record contains a technical error and no answer or
sources. Its rendered message was:

> The API request limit was reached. Wait before retrying and check your account limits.

The saved error appeared after `3.0092999999821184` seconds. A fast error does
not satisfy successful-response acceptance and is not a supported abstention.
The frozen application's exact error-message branch indicates HTTP 429, but the
raw provider status/response was not saved. The record does **not** contain a
violated quota metric or quota ID, response headers, Retry-After/retryDelay, or a
reset time. The child log adds no saved quota/retry detail. It cannot establish
whether the limit is per minute, per day or another restriction; do not guess.

The app embeds the question with `gemini-embedding-001` before requesting a chat
answer from `gemini-3.5-flash-lite`. The generic UI error cannot identify which
request/model failed. Check both configured models in the project associated
with the local key; do not assume this was the chat model's limit.

The owner can identify the relevant project in [Google AI Studio's key page](https://aistudio.google.com/apikey),
then inspect its [rate limits](https://aistudio.google.com/rate-limit?timeRange=last-28-days)
and [usage](https://aistudio.google.com/usage). These account pages require login;
the agent has not viewed the project's quota. Record the actual constrained
model/dimension and any displayed retry guidance without sharing keys or tokens.
See the [resumable checkpoint](local_setup_progress.md) for the diagnostic handover.
Do not automatically probe or resume provider calls, purchase capacity, or change
models/settings merely to diagnose this saved failure.

The owner's later screenshot description reports Default Gemini Project, Free
tier and 28-day peak RPM/TPM/RPD values for both configured models. This is
USER-REPORTED historical peak data, not current usage. The values do not identify
H22's violated metric, prove that the displayed project is tied to the configured
key, or establish restored capacity. Retry/reset text and timezone were not shown.
The exact values and separate private transcription are recorded in the
[quota guide](gemini_quota_check.md) and progress report. No daily-quota exhaustion
or current headroom is inferred from those peaks. At that checkpoint the gate
remained blocked. The owner's later explicit 2 November authorization permitted
one controlled H23 attempt and, after success, H24-H40. Their successful provider
operations establish only this run's availability; they do not identify H22's
quota metric, failing model, window or reset. Do not reconstruct missing fields.

## Outcome review and remaining evaluation work

Subsequent owner-authorized diagnosis executed exactly one H22 retry in
`local-h22-retry-2026-11-02-04` and one H27 diagnostic retest in
`local-h27-diagnostic-retest-2026-11-02-05`. Both are primary=false/attempt=2,
hash-linked to originals, with fresh chat/assigned PDFs and unchanged app/models.
H22 correctly answered five working days with page 1 in 2.031299999964238 seconds.
H27 correctly answered both claims with pages 1/2 in 2.169600000047683 seconds.
No quota/access error recurred. Original H22 error details and H27's missing stage
breakdown remain unknown; neither was reconstructed.

The H27 retest first observed assistant text/passages at 2.1259000000357626 browser
seconds, then complete-render acceptance at 2.169600000047683. These client markers
cannot allocate time to retrieval, Gemini, network or rendering CPU. Original
13.1225-second behavior was not reproduced once; that is not proof of its cause
or absence of intermittent bottlenecks. No app runtime fix was evidenced or made.
The browser tool alone adds explicit retry labels and passive markers, with its
unchanged authoritative timer. Forty-seven focused offline tests passed.

Both retests' source/config/settings, old evidence and retained workspace/PDF
fingerprints were verified; owned sessions/listeners stopped, user app preserved.
Original primary scores remain 29/30, 35/35 citation pairs/coverage, 10/10
abstention and latency FAIL. A separate unexecuted full acceptance draft exists
at `logs/evaluation/full-acceptance-prepared-2026-11-02-06/`; forty Not run/null
cases, no live calls and no authorization to execute it directly. Refresh its
freeze after any future runtime/config changes and before authorized execution.

- [x] Follow the explicit H23 authorization without a separate probe; preserve
  H22 and stop on any new quota/access error. No new such error occurred.
- [x] Verify the received approved originals, canonical protocol, six candidate
  digests, exact app/launcher source and provider/model/runtime conditions against
  their freezes. Record the current working-tree changes and helper hash.
- [x] Exclusively create a new identified continuation for **H23-H40 only**.
  Preserve H01-H22's original first-attempt records. If frozen conditions differ,
  label a new retest rather than presenting it as a compatible continuation.
- [x] Use each case's assigned PDFs, reset document state when required and start
  a fresh chat per case. Preserve submission markers before waiting for outcomes;
  an uncertain prior submission must not be automatically resubmitted.
- [x] Record actual answers, passages, citations, raw browser timings and technical
  failures. Grade claims under D01-D08; retain undefined ratios and missing data.
  Stop on a renewed capacity blocker rather than spending further primary cases.
- [x] Aggregate correctness over 30 and abstention over 10, including failed
  primary attempts. Report all failures, unrun cases and timing violations.
  A separately linked H22 retry may show recovery but cannot replace its primary
  failure or make the existing cohort satisfy the all-successful-response gate.
- [x] Review H22's primary failure and H27's measured latency violation; execute
  the two separately authorized linked retests. Originals remain unchanged.
- [ ] Resolve full-set latency acceptance and any further diagnostic/retest scope;
  no additional requests follow automatically from successful individual retries.
- [ ] If a successful complete acceptance cohort is required, identify a separate
  retest and its conditions explicitly. Preserve
  both outcomes; do not select retries to manufacture a first-attempt PASS.
  Do not tune against this candidate and later describe it as unseen.
- [ ] Perform and record any manual-search comparison separately. Expected answers
  are already known to the AI scorer. Later manual timings cannot retroactively
  make already-completed app-first cases manual-first; disclose actual order and
  this limitation. Measure usage/cost only when available.

The nine development conflict/hostile-document cases remain outside the
40-question denominators and need their own acceptance results. This short
synthetic set does not establish OCR, large-file performance, concurrency,
real-client generalization, comprehensive security or a universal production SLA.

## Hosted and release acceptance checklist

The owner reports hosted sample indexing, a 20-day answer with page-1 citation,
save/logout/login/restore of PDF and sources, and restored-PDF reindexing followed
by a second answer. Without manual save, another restore reportedly recovered
both turns and sources. These are **USER-REPORTED**, not agent-executed hosted tests.
Hosting reportedly installed `requirements.txt` and replaced pyarrow 26 with 24.
The exact hosted commit and actual installed dependency inventory are unverified.

- [ ] Identify the selected deployment candidate and the hosted revision through
  hosting/build evidence. Reconcile the installed dependencies with the candidate's
  intended lock and reproduce any required dependency change before acceptance.
- [ ] Review PR #10 and its exact CI status. This task does not authorize push,
  merge, deployment or production configuration changes.
- [ ] With separate release authorization, verify hosted account/workspace/PDF
  behavior, isolation, persistence and required development acceptance against
  that exact revision. Local evidence and user reports remain distinct.
- [ ] Record previous working revision, retained-data/schema compatibility,
  reviewed rollback procedure and the rollback acceptance result. Do not reset
  a database or delete saved user data to prepare a release.
- [ ] Record client/reviewer acceptance and unresolved limitations. Week 2 RAG,
  Week 3 pilot and broader deployment acceptance remain In progress.

Local Supabase remains loopback-only. Edge Runtime, Logflare and Vector remain
excluded, not repaired or accepted. Hosted secrets and production settings were
not changed. See the [release runbook](13_release_and_evaluation.md) and
[progress checkpoint](local_setup_progress.md) for related evidence boundaries.

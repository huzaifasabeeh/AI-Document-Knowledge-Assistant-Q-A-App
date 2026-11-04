# Local release review and PR draft

Publication authorization, 4 November 2026: the owner's subsequent request
authorizes committing this reviewed change set on
`review/local-evaluation-release`, pushing it and opening a **draft** PR to main.
PR #10 is already merged. The new branch starts from main's merge commit
`adcdcde39e50c4020a0ed9cfff866fd2a5a96564`, whose tree matches the reviewed
`b5a876a` baseline. No runtime change or new provider request accompanies
publication. Exact pushed-commit CI must be checked separately; queued/running
checks are not passed checks. No merge, deployment, billing or production change
is authorized. The preparation-time statements below are historical; this later
authorization supersedes their no-commit/push restriction only.

Prepared 4 November 2026 (Asia/Karachi). Review preparation only: no commit,
push, merge, deployment, production change or new live request. Existing branch:
`review/local-supabase-gemini-verification` (PR #10). Base HEAD:
`b5a876af001d72091443d43e3723998e76788d5b`; pending changes remain uncommitted.
Existing CI for a previous revision does not establish CI for this dirty tree.

## Findings and disposition

The bounded latency investigation is closed: **slowdown not reproduced; no proven
bottleneck; no performance fix**. [Findings](latency_investigation_findings.md)
preserve the original failures and four separately identified diagnostics.
Latest complete local quality thresholds were met. Mandatory every-response
<=10.000s acceptance remains failed; hosted acceptance and final client sign-off
remain pending. AI-assisted ground-truth owner approval is not release approval.

## Reviewed change inventory against the preparation baseline

The runtime edits integrate optional observation; they do not change the answers,
models, prompts, retrieval settings, retry policy, persistence behavior or browser
acceptance rule. No runtime/test code was edited during this closure review.

| Category | Files | Review scope |
| --- | --- | --- |
| Runtime integration | `app.py`, `src/knowledge_assistant/core.py`, `src/knowledge_assistant/persistence_ui.py`, `src/knowledge_assistant/providers.py` | Add response/retrieval/formatting/persistence spans and conditional provider wrappers/hooks; preserve unsaved-chat skip and confirmed save behavior |
| Instrumentation | `src/knowledge_assistant/provider_telemetry.py`, `src/knowledge_assistant/stage_timing.py` | New local opt-in sanitized errors, correlated spans and sync HTTP attempt/header markers; no speculative performance optimization |
| Runner and launcher | `scripts/local_test_app.py`, `scripts/run_browser_evaluation.py`, `scripts/summarize_evaluation.py` | Owned child outputs/environment, frozen-input browser workflow, durable submission/outcome records, explicit primary-linked retries, pacing, optional captures and offline quality/latency summaries |
| Tests | `tests/test_browser_evaluation.py`, `tests/test_evaluation_summary.py`, `tests/test_provider_telemetry.py`, `tests/test_stage_timing.py` | Browser DOM fixtures without service calls; raw 10s boundary, unknown/failure handling, hash binding, evidence preservation, sanitization, SDK MockTransport retries, capture defaults and persistence distinction |
| Privacy configuration | `.gitignore` | Keep owner-supplied review originals under `evaluation/approved-review/` private, alongside existing log/secret/export exclusions |
| Documentation: setup and use | `README.md`, `docs/12_user_guide.md`, `docs/18_ai_providers.md`, `docs/local_setup_guide.md`, `docs/gemini_quota_check.md` | Current status, reproducible local setup, masked secret entry, restore/reindex/autosave guidance, quota troubleshooting and default-off logging |
| Documentation: evidence and release | `docs/13_release_and_evaluation.md`, `docs/local_setup_progress.md`, `docs/evaluation_handover.md`, `docs/evaluation_human_review_checklist.md`, `docs/deployment_acceptance_checklist.md`, `docs/latency_investigation_findings.md`, `docs/release_review.md` | Distinguish historical cohorts/full retest/diagnostics, record approval boundaries, close findings, enumerate blockers and provide this PR draft |

The human-review checklist retains its original 40 questions and unchecked
historical fields. It is not newly approved independent review. Original PDFs,
candidate metadata and approved scoring protocol were not edited. Public docs
contain curated counts/synthetic examples and file hashes, not raw transcripts,
screenshots, real secrets, workspace IDs or customer data. Private orchestration,
freeze snapshots, per-case outcomes, exports and traces are excluded from Git and
are not PR payload. Preserve retained workspaces and prior evidence.

## Logging and regression review

Both captures require explicit sink opt-in and exact local Supabase configuration;
stage timing also requires Gemini environment selection. Without opt-in no sink
is created, provider wrappers/hooks are not installed and timing spans are no-ops.
The normal hardened launcher strips inherited capture variables and exclusively
creates only explicitly requested owned sinks under `logs/local-verification/`.
Remote Supabase remains HTTPS-only; the general auth client permits HTTP only
for exact loopback hosts. No auth, schema, RLS, dependency or hosted secret change
is included in this pending diff.

Error capture allowlists operation/model/status, structured quota identifiers
and explicit retry hints. It never serializes an arbitrary exception, request,
response body or header collection. Stage capture allowlists fixed stage names,
random IDs, timestamps, durations, status and numeric retry counters. Missing
fields remain unknown. Actual answers and screenshot evidence are separate private
browser artifacts, not stage logging. Known sink errors fail open to application
behavior; missing capture must not be interpreted as zero elapsed time/retries.

Review concerns remain: HTTP hooks use the pinned SDK's internal client shape;
an SDK change needs compatibility checks, and unsupported hooks may yield missing
attempt data. HTTP markers cover the current synchronous app path, not a proven
async timing path. Parent/child spans overlap; headers do not measure provider
compute or full-body transfer. Diagnostic overhead is included in browser timing.
No cache, parallelism, shortened clock or hidden delay was added. There is no
proven bottleneck to fix and no benchmark answer is hardcoded in runtime code.

## Verification evidence

Reused existing successful offline evidence for the unchanged implementation:

- Stage instrumentation/focused regressions: 38 passed in 11.51s, with an actual
  SDK MockTransport 429-to-200 retry, no live provider call.
- Linked-retest/browser checks: 47 passed in 25.08s.
- Earlier controlled preflight: 80 passed in 32.22s.

These suites overlap; do not add their counts or present them as newly run CI.
All 13 runtime/launcher/runner hashes match group 010's frozen executed sources.
No runtime change since that evidence requires rerunning passed suites.
This review's required offline checks cover documentation links/whitespace,
source/test immutability, all pre-existing private evidence, ignored/tracked-file
boundaries and actual-secret omission. These checks passed: 26 public files
categorized, 187 relative links valid, 708 private evidence files unchanged,
13 runtime/runner hashes and existing tests unchanged, zero actual-secret-value
matches and a clean `git diff --check`. Final audit is recorded privately under
`logs/pr-review/release-review-2026-11-04/`; the checkpoint records its outcome.
Remote CI was not queried and no push was made. CI for a future selected review
commit remains pending.

## Proposed PR title

Record local evaluation results and add opt-in latency diagnostics

## Proposed PR body

The latest local 40-case retest meets quality thresholds but fails mandatory
per-response latency: H03 took 11.8807s (39/40 within 10.000s). Preserve the original
failures and separate all later diagnostic results. Four bounded diagnostics did
not reproduce the slowdown; no bottleneck or performance fix is claimed.

Add default-off, sanitized local stage/provider diagnostics and a frozen-input
browser runner with durable attempts, explicit retry links and offline scoring.
Update setup/user troubleshooting, investigation findings and release blockers.
Private traces, approved originals and credentials stay outside Git.

Validation: existing 38-test instrumentation and 47-test browser/retest evidence
is reused for unchanged code; offline release integrity/privacy/docs checks are
recorded in the checkpoint. No new live requests. Full-set latency, exact-commit
CI, hosted revision/dependencies and acceptance, remaining evaluation deliverables,
rollback acceptance and final client sign-off remain pending. This PR does not
authorize deployment or mark broader acceptance complete.

## Remaining acceptance blockers and next action

Use the [deployment checklist](deployment_acceptance_checklist.md) as the
authoritative checklist: failed every-response latency/current instrumented
runtime lacks full acceptance; exact release commit/CI; hosted commit/dependency
reconciliation; separate nine-case development acceptance/manual comparison/
usage-cost disposition; authorized hosted functional/isolation/rollback checks
and final client sign-off. Local Edge Runtime, Logflare and Vector remain excluded.
The known synthetic candidate is not unseen, and no high-load/production SLA is
established. Both retained workspaces and all evidence must remain preserved.

Next action is owner/reviewer review of this diff and draft. No commit, push,
merge, deployment or further evaluation follows automatically from this report.

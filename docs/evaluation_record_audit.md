# Saved evaluation record audit

Audited 5 November 2026 (Asia/Karachi), offline on PR #11 branch.
Original records, scores, attempts, failures, freezes and protocols were not overwritten.
This report applies corrected local logic; it does not execute any evaluation or grant acceptance.

## Latest complete retest: run 007

Descriptive quality remains 30/30 correct supported answers, 36/36 supported citation pairs,
36/36 claims cited and 10/10 appropriate abstentions. All 40 case identities are explicit
primaries and match their immutable primary artifacts. H03 remains 11.880700000035766s:
**original strict latency FAIL; 39/40 within 10.000s.**

Completion and before/after preservation witnesses are recorded, but complete historical
configuration provenance under the corrected guard is **UNVERIFIED**. Recorded model names
match the freeze; that does not prove every frozen runtime/execution/private setting.
No historical configuration mismatch is inferred solely from absent newer metadata.
**Corrected combined acceptance remains false.**

## Record inventory

| Saved run/folder | Completed | Aggregate primary provenance | Immutable primary / linked retry artifacts | Full-set acceptance |
| --- | ---: | --- | --- | --- |
| acceptance-after-stage-instrumentation-2026-11-03-09 | 0 | Missing/incomplete; unverified | 0 / 0 | Blocked / false |
| D01-H03-1 | 1 | Nonprimary retry present | 0 / 1 | Blocked / false |
| D02-H03-2 | 1 | Nonprimary retry present | 0 / 1 | Blocked / false |
| D03-H03-3 | 1 | Nonprimary retry present | 0 / 1 | Blocked / false |
| D04-H27-1 | 1 | Nonprimary retry present | 0 / 1 | Blocked / false |
| full-acceptance-2026-11-02-07 | 40 | Verified all 40 | 40 / 0 | Blocked / false |
| full-acceptance-prepared-2026-11-02-06 | 0 | Missing/incomplete; unverified | 0 / 0 | Blocked / false |
| local-controlled-continuation-2026-11-02-03 | 18 | Missing/incomplete; unverified | 18 / 0 | Blocked / false |
| local-h22-retry-2026-11-02-04 | 1 | Nonprimary retry present | 0 / 1 | Blocked / false |
| local-h27-diagnostic-retest-2026-11-02-05 | 1 | Nonprimary retry present | 0 / 1 | Blocked / false |
| local-primary-2026-10-31-01 | 5 | Missing/incomplete; unverified | 5 / 0 | Blocked / false |
| local-retest-continuation-2026-10-31-02 | 16 | Missing/incomplete; unverified | 17 / 0 | Blocked / false |
| preparation-2026-10-31-b5a876a | 0 | Missing/incomplete; unverified | 0 / 0 | Blocked / false |
| primary-cohort-2026-10-31-partial-01 | 21 | Missing/incomplete; unverified | 22 / 0 | Blocked / false |
| primary-cohort-2026-11-02-controlled-03 | 39 | Missing/incomplete; unverified | 40 / 0 | Blocked / false |

Every audited saved record lacks the complete new execution/configuration verification
schema, so configuration is marked UNVERIFIED, including Not-run drafts. Legacy aggregate
records without explicit is_primary/attempt_number/retry_of fields remain unverified in
the corrected scorer even where individual primary artifacts independently exist. That
does not erase those artifacts or fabricate new provenance fields. Linked retries and
the four diagnostic attempts remain separate and never count toward primary acceptance.

## Dated owner clarification: tolerance is separate

On **5 November 2026, Asia/Karachi**, the owner reported that the client accepts
**2-3 responses per 100 exceeding 10 seconds**. This is USER-REPORTED, not an
independently obtained client sign-off or a frozen-protocol amendment.
The observed run has **1/40 = 2.5%** exceedance. No 100-case test was performed.
The observed 2.5% lies within the reported 2-3% range as a descriptive rate comparison.
The observed rate is below a 3% ceiling but above a 2% ceiling; an exact prospective
threshold/scope remains to be agreed. This descriptive comparison establishes neither
future 100-response behavior nor run validity, hosted acceptance or final sign-off.
**Original strict 10-second FAIL remains unchanged.** No tolerance-adjusted full-set PASS is issued.

## Preservation and next action

708 pre-existing private evidence/review files were hash-sealed and verified unchanged.
Full audit JSON, per-run descriptive summaries, source hashes and the separate clarification
are private under logs/evaluation/audit-2026-11-05-defect-fixes/. No secrets/raw answers
are included in this public report. No old freeze or scoring protocol was amended.

Review the local fixes and new tests. Any future run requires separate authorization and
an explicitly approved current freeze including execution_settings; mixed legacy
continuation_conditions are not silently migrated. Preserve originals and label new
execution as a retest. Hosted revision/dependencies, development acceptance, manual
comparison/usage-cost evidence, rollback and final client sign-off remain pending.

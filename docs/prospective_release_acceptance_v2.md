# Prospective release acceptance and deployment plan

Updated 9 November 2026 (Asia/Karachi). This document records owner instructions and a release plan; it does not claim execution, hosted acceptance or client sign-off.

## Acceptance amendment v2

The owner clarified that the client permits 2–3 responses per 100 to exceed 10 seconds. For future evaluation, operationalize the upper tolerance as **at most 3%** of all scheduled primary cases exceeding 10.000 seconds. This is an owner-reported requirement clarification, not independently received client sign-off.

For 40 scheduled cases: at most floor(0.03 * 40) = 1 slow response. Two slow responses fail. For 100 cases: at most 3. Do not round the observed percentage down. No maximum duration for an allowed slow response was supplied; report the maximum explicitly rather than inventing an agreed limit.

All scheduled primary cases must complete successfully and have valid browser timing. Technical failures, timeouts, missing measurements, ambiguous primary provenance, failed preservation checks and unverified configurations block combined acceptance. They cannot be excluded from the denominator to improve the result.

Retain quality gates: correctness >=24/30; citation semantic support >=95%; citation coverage 100%; appropriate abstention >=9/10. Preserve the browser-submission-to-complete-response-and-sources timer; indexing and pre-submission pacing remain separate. Use sequential fresh chats and assigned PDFs, and disclose pacing and lack of concurrency evidence.

This prospective amendment does not rewrite any old freeze or score. Run 007's 1/40 = 2.5% is within the stated numerical tolerance, but its historical configuration remains UNVERIFIED. Original strict latency FAIL remains intact. No 100-case run is claimed.

The current summarizer implements the historical strict gate. Before executing a v2 run, implement an explicitly selected, digest-bound v2 policy and regression checks (1/40 passes rate; 2/40 fails; missing/failed/invalid cases cannot pass). Keep legacy scoring unchanged. Freeze exact policy bytes, source hashes, effective configuration, revision and run conditions before execution. The private November 5 draft is not automatically updated or approved by this document.

## Dependency reconciliation

Source inspected: PR #11 head cfd8e310f5a5e2df85f451feb7c93fa3eecf3b30. CI workflow installs requirements-lock.txt on Python 3.12 and runs pip check and pytest. The owner-supplied November 5 UTC hosting logs install requirements.txt on Python 3.12.16. That file pins eight direct dependencies but not the full transitive environment.

Selected confirmed differences (not a complete inventory):

| Package | Reviewed CI lock | Supplied hosted installation log |
| --- | --- | --- |
| openai | 3.34.0 | 3.45.0 |
| pyarrow | 26.0.0 | 26.0.1 replaced by platform with 24.0.0 |
| anyio | 4.15.1 | 4.16.0 |
| pandas | 3.0.6 | 3.1.1 |
| langsmith | 0.14.11 | 0.14.17 |
| httpx2 / httpcore2 | 2.13.1 | 2.16.0 |
| certifi | 2026.7.22 | 2026.10.23 |
| streamlit | 1.66.0 | 1.66.0 |

These are supplied build-log observations, not a fresh installed-package interrogation. Hosting also upgrades pip/certifi and applies its own PyArrow replacement. Exact hosted SHA is not in the supplied log. Branch main and app.py are confirmed; a current GitHub main SHA alone cannot prove the running deployment SHA.

Proposed remediation: validate a dedicated Linux/Python-3.12 deployment lock that explicitly pins the platform-observed PyArrow 24.0.0 and compatible transitive dependencies. Make hosting and CI exercise that same deployment dependency input, while keeping development-only tools separate. Validate clean install, pip check, offline tests and disposable target smoke before selecting it. Do not simply feed the old lock to hosting: its PyArrow pin conflicts with the observed platform replacement. No package pin or hosting installation was changed by this documentation update.

## Deployment and rollback sequence

1. Obtain hosting revision/build evidence, entrypoint, Python and installed dependency inventory. Preserve a nonsecret snapshot of configuration names and model IDs. Confirm deployment branch and automatic-deployment behavior. Never capture secret values.
2. Identify a rollback candidate from actual prior deployment evidence and verify its artifact/dependency availability. Main's previous SHA is not automatically a verified rollback target.
3. Complete v2 policy implementation/review and exact candidate/configuration freeze; separately authorize a bounded acceptance run. Do not rerun until green or replace primary outcomes with retries.
4. Reconcile separate development conflict/hostile cases, manual-search and usage/cost evidence. Mark unavailable measurements unknown or obtain an explicit scope disposition; never fabricate completion.
5. Before merge, review final diff, exact-head CI and deployment/rollback plan. A merge to the hosting branch may deploy automatically; it requires the owner's explicit release authorization.
6. On authorized deployment, verify actual deployed SHA and dependency inventory, startup and health. Test disposable normal-user login/logout, indexing/Q&A with cited passages, save/restore/autosave/follow-up, reset/export/deletion and both-direction account/PDF isolation. Preserve retained review workspaces. No real client documents are needed.
7. On regression, stop new acceptance writes and preserve evidence. Prepare a reviewed revert of release changes on the hosting branch (no force push), deploy it with separately authorized hosting steps and verify the reverted SHA and health. Code rollback does not undo database writes, schema changes or secrets.
8. This PR contains no proposed migration changes. Nevertheless verify saved-data compatibility before release; do not reset the database, remove retained workspaces or rotate keys to make rollback pass. Exercise rollback on a disposable/staging target before production where available; production rollback remains separately authorized.
9. Record hosted results, residual limits, client ownership/access, retention/spending boundaries and final client sign-off. Ground-truth approval and CI are not release acceptance.

## Current disposition

PR #11 remains draft and unmerged. Prior exact-head CI for cfd8e310 was successful; any new documentation commit has a new head and its own CI state. Runtime/scoring changes, a new live run, merge, deployment, billing changes and private Windows configuration are not performed by this plan.

Historical source evidence and private records are preserved. This plan supersedes current-action statements in older checklists only where explicitly described above; historical observations remain valid as dated evidence.

## Implementation checkpoint - 10 November 2026

V2 policy is now implemented explicitly in scripts/evaluation_latency_policy.py. A run without acceptance_policy retains legacy strict scoring. For a prospective run, both freeze.json and run.json must carry identical acceptance_policy objects containing policy, its canonical SHA-256 and a nonempty owner_confirmation. The runner rejects missing/mismatched/unknown v2 policy metadata before any client creation. Do not retrofit this metadata to historical runs. Rebuild and review a new freeze against these changed source bytes.

The policy object is exactly: {"version":"latency-v2","deadline_seconds":10,"maximum_exceedance_percent":3,"require_all_scheduled_responses":true}. Use policy_digest(V2_POLICY) to calculate the binding digest, not a hand-copied value. Strict latency metrics remain separate; prospective_latency and acceptance.policy_version expose the selected gate. Run validity, preservation, configuration and primary-provenance requirements are unchanged. No live run or private freeze was modified here.

Hosting requirements.txt now includes requirements-deployment-lock.txt; the deployment leg of CI installs that exact hosting entrypoint. The historical requirements-lock.txt remains unchanged and has its own CI matrix leg. The deployment lock preserves the original full pinned set (including development tools for now), changing only PyArrow to 24.0.0 and certifi to the platform-observed 2026.10.23. This avoids an unvalidated hand-pruned dependency closure. Future pruning is separate work. Hosting can still apply platform overrides; capture the actual installed inventory after authorized deployment.

Local focused validation: 67 tests plus 3 unittest subtests passed in an isolated pytest environment. These pure scoring/policy tests were copied unchanged outside the repository conftest because this workspace lacks Streamlit; no runtime integration tests were claimed. Python compile and whitespace checks passed. Full clean-install, pip check and application tests are delegated to the exact-head CI matrix; results must be checked before merging.

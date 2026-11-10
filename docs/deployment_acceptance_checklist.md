> **Release update — 9 November 2026:** See [prospective acceptance v2 and deployment/rollback plan](prospective_release_acceptance_v2.md). This dated plan supersedes the prospective strict latency rule and outdated commit/CI-pending statements below, while preserving all historical failures and configuration uncertainty. Owner-reported tolerance is at most 3% slow responses (at most 1/40); it does not excuse failed requests or invalid evidence. PR commit cfd8e310 had successful CI. Hosting logs show main/app.py, Python 3.12.16 and requirements.txt, with final PyArrow 24.0.0; deployed SHA remains unverified. CI uses a different dependency input. V2 scorer implementation, new exact configuration freeze, hosted acceptance and rollback verification remain pending. No merge or deployment is authorized here.

# Deployment acceptance checklist

Reviewed 4 November 2026 (Asia/Karachi). **PENDING: this checklist authorizes no deployment.**
Preserve retained workspaces, approved originals, private evidence and primary
failures. Owner approval of AI-assisted ground truth is separate from release
acceptance; independent human review was waived, not performed.

Latest local full retest (007): 30/30 correct supported answers, 36/36 supported
citation pairs, 36/36 claims cited and 10/10 appropriate abstentions. **Quality
thresholds met; mandatory every-response <=10.000s acceptance FAILED**: H03 took
11.880700000035766s, with 39/40 within deadline. Original H22 failure and run-003
H27 13.1225s remain preserved. Four bounded diagnostics were fast; the slowdown
was not reproduced, no bottleneck was proven and no performance fix was made.
See [closed findings](latency_investigation_findings.md). Diagnostic successes
replace no failed result. Both prepared full-run drafts remain unexecuted; the
later stage-instrumentation draft is group 009, not the completed run 007.

## Exact outstanding acceptance blockers

1. Mandatory local latency gate remains failed. There is no accepted complete
   40-case browser run for the current instrumented runtime; four diagnostics
   cannot establish it. No further execution is authorized by this review.
2. Select/review an exact release commit and obtain CI for that commit. Current
   evidence freezes a dirty local tree; no commit/push occurred in this review.
3. Hosted commit, installed dependency inventory and target acceptance are
   unverified. Reported requirements.txt installation/pyarrow 26-to-24 substitution
   must be reconciled reproducibly rather than treated as an accepted lock.
4. Complete the separate nine development acceptance cases, manual-search
   comparison and usage/cost evidence (or explicitly record their accepted scope
   disposition). Missing measurements remain unknown; no fabricated pass.
5. Record authorized hosted flow/isolation/data-compatibility/rollback acceptance,
   pilot feedback and final client sign-off. Ground-truth owner approval does not
   provide release/client acceptance.

Investigation scope is closed; root cause remains unresolved. No runtime tuning,
model change or repeated full runs to obtain a PASS are justified by these traces.

## Candidate and evidence

- [ ] Select the exact release commit, review its complete diff and record CI for
  that commit. Current local retests use b5a876a plus hash-frozen working changes;
  they do not verify an uncommitted tree on GitHub or the hosted revision.
- [ ] Record target host/project, entrypoint, installed dependency inventory and
  reviewed configuration without secrets. Hosted use of requirements.txt and a
  pyarrow 26-to-24 replacement are USER-REPORTED; reconcile them reproducibly.
- [ ] Verify candidate/protocol hashes and owner confirmation. Preserve H22's
  failed primary, H27's 13.1225-second response and run-007 H03's 11.8807-second
  response. Linked retries/diagnostics replace none and establish no full-set PASS.
- [ ] Resolve the evaluation acceptance decision. If app runtime/configuration
  changes, any separately authorized full acceptance must use a new identified
  40-case run with exact source/model/settings hashes. The instrumented runtime
  has no full-set latency acceptance. Do not silently combine prior cases/retries.
  Do not call a candidate unseen after tuning against its questions.
- [ ] Record all gates separately: correctness >=24/30, citation correctness
  >=95%, coverage 100%, abstention >=9/10, and EACH complete rendered primary
  response <=10.000 browser seconds including applicable sources. Include
  network/retrieval/internal retries/rendering; indexing stays separate. Retain
  failures, timeouts, unknown measurements and raw over-deadline values.
- [ ] Complete the nine separate development acceptance cases, including conflict
  and hostile-document behavior. Record manual-search/usage/cost comparisons only
  when actually measured; current missing values remain unknown.

## Authorized target verification

- [ ] Obtain separate release authorization before changing hosting, secrets or
  production. Verify the actual deployed commit from hosting/build evidence;
  local results and owner-reported hosted smokes remain distinct.
- [ ] Verify intended locked installation, startup/health and dependency checks
  on the selected target. Confirm supported provider models without fallback.
- [ ] Configure secrets privately; keep real keys, passwords, tokens, exports and
  private logs out of Git. Remote Supabase must require HTTPS. Local HTTP remains
  limited to exact loopback hosts; never point the local test launcher at production.
- [ ] Verify target migrations, ownership RLS, restricted privileges and private
  PDF storage using normal users. Test both account directions and unauthenticated
  access with disposable resources; preserve the retained review workspaces.
- [ ] Verify login/logout, PDF indexing, real answer and supporting page passages;
  save/logout/login/restore PDF, transcript and sources. After restored-PDF
  reindexing verify a new answer and subsequent-turn autosave across another restore.
- [ ] Verify reset, clear chat and export behavior; delete only an identifiable
  disposable acceptance workspace. Check account/PDF isolation, consent, invalid
  files and essential desktop/narrow layouts against the exact deployed revision.

## Rollback and signoff

- [ ] Record previous working revision and reviewed rollback steps. Check retained
  data/schema/secret compatibility separately; code rollback is not database rollback.
  Never use a destructive reset to obtain acceptance.
- [ ] Execute and record the authorized rollback acceptance result, unresolved
  issues, access/retention/spending boundaries and pilot/client acceptance.
- [ ] Record the owner's release decision. Week 2 RAG, Week 3 pilot and broader
  deployment acceptance remain In progress until their actual gates are satisfied.
- [ ] Obtain final client sign-off tied to the tested deployed revision and
  unresolved limitations. AI-assisted ground-truth approval is a separate record.

Local Edge Runtime, Logflare and Vector remain excluded, not repaired or accepted.
No purchase, push, merge or deployment occurs as part of this checklist preparation.
See [current checkpoint](local_setup_progress.md), [evaluation handover](evaluation_handover.md)
and [release runbook](13_release_and_evaluation.md).

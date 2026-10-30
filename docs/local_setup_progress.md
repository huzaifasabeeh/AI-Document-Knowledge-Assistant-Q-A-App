# Local Supabase and Gemini verification

Updated 30 October 2026 (Asia/Karachi). Curated review summary only.
Raw logs, screenshots, transcripts, exports, local workspace identifiers and
secrets remain ignored. The earlier detailed checkpoint is preserved privately at
logs/pr-review/local_setup_progress_before_pr_review.md.

## Status and limits

Local Supabase verification, the original one-question live Gemini smoke and the
three-answer conversation-persistence follow-up passed. Both real saved
workspaces remain in the local A account for owner review. Their exact titles/UUIDs
are in the ignored Gemini smoke evidence; preserve them.
The existing user Streamlit app and Docker stack are not replaced by review tests.

This does not complete the 40-question evaluation, production deployment
acceptance or comprehensive security certification. No production database or
hosted secrets were changed and no credits were purchased. This branch is for
review; merging and deployment require a later owner decision.

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
2. Obtain independent human ground-truth approval of all 40 cases, then freeze the
   candidate revision/manifest. See the [candidate guide](../evaluation/heldout/README.md).
3. Exclusively create a private result log under ignored logs/evaluation/ using
   scripts.prepare_evaluation. Use each case's exact PDFs, reset between cases and
   record actual answers, supported claims, citations, timings, failures and
   measured usage. Unknown values stay null; unrun cases are not PASS.
   Report correctness over 30 answerable cases, abstention over 10 unsupported
   cases, citation correctness/coverage and latency.
4. Separately approve a deployment candidate, identify its exact hosted revision,
   configure hosted secrets privately and execute release acceptance against the
   authorized target. Record retained-data compatibility and rollback evidence.
   See the [release runbook](13_release_and_evaluation.md).

Subsequent-turn autosave and new questions after re-indexing are verified by the
focused follow-up above. No broader evaluation score or production acceptance is
claimed.

# Local setup and recovery

Reviewed 4 November 2026 (Asia/Karachi). These are reproducible instructions for
the tested local setup, not commands executed during release review. Preserve an
existing environment, Supabase data, credentials and retained review workspaces.
Full hosted acceptance remains pending.

## Dependencies and local services

Use Python 3.12, Docker Desktop with localhost-only published ports, and Node/npm
for the pinned Supabase CLI. From the repository root in PowerShell:

```powershell
if (-not (Test-Path -LiteralPath .venv/Scripts/python.exe)) {
    py -3.12 -m venv .venv
}
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip check
if (-not (Test-Path -LiteralPath supabase/config.toml)) {
    Copy-Item -LiteralPath supabase/config.example.toml -Destination supabase/config.toml
}
```

Inspect an existing stack before starting anything. Reuse the
`document-qa-local` Docker network; create it only if absent. The recorded local
startup sequence was:

```powershell
docker network inspect document-qa-local *> $null
if ($LASTEXITCODE -ne 0) { docker network create document-qa-local | Out-Null }
npx.cmd supabase@2.122.0 start --network-id document-qa-local -x edge-runtime,logflare,vector *> $null
if ($LASTEXITCODE -ne 0) { throw 'Local startup failed; inspect logs privately.' }
```

API: `http://127.0.0.1:54321`; Studio: `http://127.0.0.1:54323`.
Avoid printing CLI status/secret files, which can contain credentials. All three
project migrations were applied to the retained local database; do not reset or
replay it. Fresh-project replay is a separate acceptance item. Edge Runtime,
Logflare and Vector remain excluded; their behavior is not accepted. Do not reset
Docker, remove volumes or use destructive database resets to recover this setup.

## Private configuration

The app reads environment values before Streamlit Secrets and does not load
`.env`. The secure helper writes only gitignored local configuration:

```powershell
.\.venv\Scripts\python.exe scripts/configure_local_supabase.py
```

Existing QA accounts are `qa-a@example.com` and `qa-b@example.com`; do not recreate
them. Only if local test credentials are missing, collect them with hidden input:

```powershell
.\.venv\Scripts\python.exe scripts/configure_local_supabase.py --collect-credentials
```

Use the masked Gemini dialog only when a local key needs setup. Skip any optional
console key prompt. Preserve an existing key; do not rotate it for diagnosis:

```powershell
.\.venv\Scripts\python.exe scripts/configure_local_supabase.py --collect-gemini --key-dialog --chat-model gemini-3.5-flash-lite --embedding-model gemini-embedding-001
```

These are the recorded model IDs, not a promise of future availability. A future
authorized configuration change must verify supported IDs, document it and reset
and re-index. No provider/key/project/model change is authorized by this guide.
Keep `.streamlit/secrets*`, `data/private/`, generated exports and `logs/` outside
Git. Use a public/publishable Supabase key with normal user credentials, never a
service-role key. Remote Supabase requires HTTPS; HTTP is accepted only for exact
`127.0.0.1`, `::1` or `localhost` hosts. The test launcher pins the API above.

## Start and use

```powershell
.\.venv\Scripts\python.exe -m scripts.local_test_app
```

The hardened launcher isolates settings, chooses an available loopback port and
prints its unique URL. Open that URL, leave the terminal running and stop this
child with Ctrl+C. Existing user apps are preserved. Captures are default-off.
Never reuse an existing evidence output directory for a new diagnostic.

Follow the [user guide](12_user_guide.md) for preview, consent, indexing, cited
questions, save/restore, export and deletion. Indexing/questions make real provider
requests and require explicit task authorization during controlled evaluation;
the release-review task makes none. Re-index restored PDFs before new questions.
Keep real client documents out of testing.

## Recovery and acceptance boundary

Read the [progress checkpoint](local_setup_progress.md) before resuming work. A
submitted case with uncertain timing/outcome must not be resubmitted as a primary.
Preserve attempts, raw failures and private traces. Quota/access errors require a
checkpoint, not an automatic outer retry or capacity probe. See
[quota troubleshooting](gemini_quota_check.md) and
[latency findings](latency_investigation_findings.md).

Latest local quality thresholds were met; every-response <=10.000s acceptance
failed. Hosted successes and a requirements.txt/pyarrow replacement were
user-reported; the hosted revision/dependency inventory remain unverified. The
[deployment checklist](deployment_acceptance_checklist.md) and final client
sign-off are still pending. This guide authorizes no evaluation, purchase or
deployment.

# Private prototype deployment and handoff

## Delivery status

Update, 23 November 2026: all development PRs are merged into main. PR #1
(hosted handoff), PR #11 (evaluation release, deployment lock, scoring guards)
and PR #12 (forgot password / email code recovery) are all in production.
Current main HEAD is `5192013`. The app auto-deploys from main to Streamlit
Community Cloud. Exact deployed SHA and installed dependency inventory require
verification from hosting build logs after the latest merges. Authentication,
saved workspaces, PDF storage and account isolation are fully implemented.
The forgot-password feature requires a Supabase email template change.

Rollback candidates: `69b998a` (main before PR #12) or `7fdfc7c` (old main
before PR #11). Code rollback does not roll back database schema; the
forgot-password feature uses existing Supabase Auth endpoints and adds no
migrations.

Earlier deployment notes are retained below as historical context.

The following preparation notes describe the earlier checkpoint:

The existing Streamlit UI remains the chosen implementation. Figma migration
is cancelled. Detailed manual and live model testing is deferred until the
development candidate is ready. These deployment files have not been built or
deployed; they are preparation, not evidence of a working hosted release.

The repository implements upload validation, page extraction, chunking,
session-specific retrieval, structured answers, sources, local preview, reset,
chat clearing and chat export. Live answer quality, citation support and
multi-session acceptance still require validation. The previously reported
39-test result predates this deployment preparation.

## Local launch

Use Python 3.12, matching the existing CI environment. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/start.py
```

On Linux/macOS use `.venv/bin/python` instead. The launcher checks prerequisites
before starting Streamlit on localhost. Stop with Ctrl+C. API configuration must
be supplied to that process using the server environment; `.env.example` only
documents variable names and is not loaded automatically. Preview works without
an API key; indexing and chat require funded access.

## Optional container packaging

The Dockerfile uses the full lock file and runs the app as an unprivileged user.
Only application code and dependency definitions enter the build context; local
secrets, customer documents and repository history are excluded.

```sh
docker build -t document-assistant:candidate .
docker run --rm --name document-assistant -p 127.0.0.1:8501:8501 document-assistant:candidate
```

For AI mode, supply server environment variables at runtime through the approved
host secret manager. For a local shell that already has the key set:

```sh
docker run --rm --name document-assistant -p 127.0.0.1:8501:8501 -e OPENAI_API_KEY document-assistant:candidate
```

Open localhost port 8501. The port binding deliberately restricts direct access
to the local machine. The health check measures HTTP liveness only; it cannot
verify provider access, credits, answer correctness or session isolation.
No persistent document volume is configured. Stop the container with
`docker stop document-assistant`; active chats and ephemeral indexes are lost.

## Hosted release boundary

The app is hosted on Streamlit Community Cloud, auto-deploying from main.
Account authentication (signup/login/logout/forgot-password), saved workspaces
with private PDF storage and owner-scoped RLS are all implemented. The app
uses Supabase Auth REST over HTTPS with per-request validation and session
isolation. Never publish credentials or use service-role keys.

Before accepting real client documents, complete the hosted verification
checklist: confirm deployed SHA, test all user flows with disposable accounts,
verify account/PDF isolation, and record reviewer approval. For rollback,
deploy a revert commit on main (no force push) and verify the reverted SHA.
Code rollback does not undo database writes.

## Remaining decisions and evidence

- Hosting target: Streamlit Community Cloud, auto-deploy from main.
- Container build: not run; not required for Streamlit Cloud hosting.
- Local evaluation (run 007): quality gates met, mandatory per-response latency
  failed (H03 11.8807s). Owner-reported client tolerance 2-3% (1/40 = 2.5%
  within tolerance). Disposition needed.
- Hosted verification: exact deployed SHA and functional smoke test pending
  after PR #12 merge. Owner should check build logs.
- Forgot-password: requires Supabase email template update (`{{ .Token }}`).
- API credits: Gemini free tier used for verification. OpenAI credits unavailable.
- Reviewer acceptance and client handoff: pending.

No task is marked complete solely because its deployment instructions exist.

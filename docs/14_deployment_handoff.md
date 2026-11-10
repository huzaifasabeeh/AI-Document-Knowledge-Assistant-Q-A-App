# Private prototype deployment and handoff

## Delivery status

Update, 23 October 2026: the owner deployed the main branch to Streamlit
Community Cloud with Python 3.12 and app.py. Hosted startup was observed on
21 October and the owner subsequently reported successful use without errors.
See document 15 for evidence and limitations. The container remains unbuilt.
The deployment-preparation branch is now incorporated into the handoff candidate;
that candidate has not yet been published or deployed.

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

Choose the private hosting target before adapting these commands to hosting.
Use host-managed authentication/access restrictions and HTTPS before remote
client access. The app itself does not implement account authentication,
automatic idle-session cleanup or persistent chat storage. Do not publish an
unrestricted endpoint with a funded provider key.

Before accepting real documents, agree on retention and provider processing,
complete the deferred acceptance session in document 13, and record reviewer
approval. For a rollback, deploy the previously accepted image/commit and
restart sessions. Existing session data is not migrated or restored.

## Remaining decisions and evidence

- Hosting target: Streamlit Community Cloud; access restrictions remain unverified.
- Container build: not run. Hosted Streamlit startup: observed on 21 October.
- Live AI evaluation and final manual checks: deferred.
- API credits and live-call authorization: required before live evaluation.
- Reviewer acceptance and client handoff: pending.

No task is marked complete solely because its deployment instructions exist.

# Frontend and offline integration checkpoint

19 October 2026 (Asia/Karachi). Week 3 work has started; Week 2 live validation
remains blocked by unavailable API credits. No live AI success is claimed.

## Implemented

- Streamlit sidebar for PDF selection, local preview, processing consent,
  indexing and reset. The uploader now enforces/displays 10 MB per file,
  consistent with backend validation (10 files and 200 pages total).
- Main workspace shows indexed document count, passage count and answered
  question count, with explicit empty/indexed/consent-paused states.
- Local page preview extracts text without constructing an OpenAI client or
  Chroma index. Shows physical page numbers and up to 1,500 characters per page.
  It is a snapshot: click Preview again after changing selected files.
- Answers retain filename/page references; expandable supporting passages show
  cited chunks. Raw text rendering avoids executing document-supplied markup.
- API quota, authentication and rate-limit failures have readable messages;
  raw provider errors are not printed into the interface.
- Failed indexing closes the temporary engine. Failed cleanup pauses the
  session until reset succeeds or the server is restarted. Consent withdrawal
  pauses questions; resetting clears preview, files, history and active index.

## Validation

Full offline suite: **35 passed**, Linux/Python 3.12. Includes the existing
26 tests plus nine frontend/presentation regression cases. Streamlit AppTest
exercises local PDF preview, failed indexing and fresh retry, consent pause,
reset and cleanup failure, chat/source display and bounded history content.
Provider errors and answer generation use test doubles; no paid calls occurred.
The uploader is replaced with synthetic upload objects in those flow tests;
these are not browser file-picker end-to-end tests. The previous 26-test
Windows run and old UI startup were user-confirmed. The new 35-test Windows
run and visual review of the updated layout are pending.

## Windows update and free preview

Stop Streamlit with Ctrl+C before updating. Run git status and preserve any
local edits; pull only once the working tree is clean or changes are resolved.

```powershell
git status
git pull --ff-only origin main
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Expected: 35 passed. Open the local URL, choose data/sample_pdfs/leave.pdf,
then click **Preview pages (no API)**. Expect two pages: annual leave is
20 days on page 1; manager approval on page 2. The preview should not enable
AI chat. Reset clears the preview. Do not click Index documents while choosing
not to spend API credits. Preview requires no API key or processing consent.
A configured key only means it is present, not that it is valid/funded.

## Remaining work and completion boundaries

- Review the updated layout on Windows, including upload limit display and
  narrow-screen sidebar behavior.
- Independent retrieval/answer evaluation and latency pilot remain pending.
- Real browser upload-to-answer tests, live citation support, conflict handling,
  abstention and hostile-document behavior require funded API access or an
  agreed alternative implementation.
- Production session TTL/cleanup and deployment remain future work.
- Reviewer feedback and approval remain pending.

The two Week 3 tasks (Streamlit/pilot and isolation/error handling) are now
In progress in project/tasks.json. Build RAG prototype stays In progress.
No reviewer or submission status has been changed.

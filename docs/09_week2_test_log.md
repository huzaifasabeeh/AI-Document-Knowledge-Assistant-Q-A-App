# Week 2 validation log

Executed 18 October 2026 (Asia/Karachi), Python 3.12, isolated Linux virtual environment.

Command: `python -m pytest -q`.

| Check | Result | Evidence boundary |
|---|---|---|
| PDF extraction and one-based page metadata | Pass | Generated two-page text PDF |
| Chunk IDs and retained filename/session/page | Pass | Real LangChain splitter |
| Invalid extension, malformed, empty, oversized files | Pass | Four parameterized cases |
| Empty upload, file-count/page-count limits, duplicate names | Pass | Includes 201-page fixture |
| Blank/scanned and encrypted PDFs | Pass | Explicit rejection; no OCR |
| Two sessions, retrieval and reset | Pass | Real ephemeral Chroma; deterministic local embedding double |
| Unknown or missing citation IDs and absent-answer response | Pass | Mock answer model; three cases |
| Conflict response and follow-up context | Pass | Mock model; prompt contract only |
| Streamlit startup without API key and reset | Pass | Streamlit AppTest, not browser upload end-to-end |
| OpenAI client and structured-output construction | Pass | Dummy key; no network/provider call |
| Existing Notion sync regression checks | Pass | Four mocked checks |
| Dependency consistency | Pass | pip check: no broken requirements |

Final suite: 18 tests passed. Tests use generated PDFs, real PDF parser/splitter/Chroma, deterministic embedding doubles and predetermined answers. These results do not measure live AI correctness, semantic citation support, abstention, injection resistance or latency. Earlier startup checks identified a test path issue and a missing SOCKS transport package in this environment; the path was corrected and socksio is included in the full environment lock.

Four synthetic sample PDFs are committed: leave, expenses, conflict and hostile. Recreate with `python scripts/make_sample_pdfs.py`. No customer documents are included.

## Outstanding validation

- Configure OPENAI_API_KEY and run `python -m scripts.live_smoke` (paid provider calls). Record actual outputs and manually inspect claims/citations.
- Exercise conflict and hostile fixtures against the live model.
- Run browser upload/chat/retry flows with real provider access; AppTest startup is not a full UI acceptance test.
- Week 3: independent 40-question pilot, latency measurement, browser/session lifecycle and production cleanup/error testing.
- GitHub-hosted CI is separate from the local run recorded here.
- Notion Actions activation remains dependent on NOTION_TOKEN and tracker permissions; updating the tracker through the connected Notion app does not prove Actions sync works.

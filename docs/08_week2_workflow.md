# Week 2 prototype and workflow

## Run locally

Use Python 3.12 (validated on Linux). From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-lock.txt
# Set OPENAI_API_KEY securely in the shell or hosting secret manager.
streamlit run app.py
```

Windows activation: `.venv\Scripts\activate`. Direct dependencies are also listed in requirements.txt; requirements-dev.txt adds pytest and the synthetic PDF generator. The lock file records the tested complete environment. The app does not load .env automatically. `.env.example` lists configuration names only. Default models are gpt-4.1-mini and text-embedding-3-small; override OPENAI_CHAT_MODEL / OPENAI_EMBEDDING_MODEL if your account needs different supported models. API billing is separate from ChatGPT credits.

## Document path

The user consents to external processing, selects PDFs and clicks Index documents. pypdf validates and extracts each physical page. LangChain splits pages into 1000-character passages with 150-character overlap; passages never span pages. Filename, one-based physical page, random session ID and chunk ID stay with every passage. OpenAI creates embeddings and Chroma stores them in a random session collection. The UI accepts one document set until reset; reset removes the collection and chat, and clears the uploader.

Limits: 10 files, 10 MB per file, 200 pages total, 5000 chunks. Duplicate filenames, encrypted, malformed and textless PDFs are rejected. A PDF with any blank/scanned page is rejected explicitly to avoid silently indexing only part of a document. OCR is deferred. Upload validation is not a hardened hostile-file sandbox; production needs isolated parsing, resource/time limits and authentication.

## Question path

A question and up to two preceding user questions form the retrieval query. Chroma retrieves up to six passages, restricted to the session ID. The answer model receives those passages and bounded recent chat. A system instruction treats documents/history as data and asks for supported claims, not_found, or conflict. Structured output associates each claim with chunk IDs. Unknown IDs or claims without references fail closed to a not-found answer. The UI renders cited filename and physical page per claim.

Citation ID validation does not prove semantic support. Unsupported-answer reliability, conflicting-source detection and prompt-injection resistance still require live provider evaluation. Top-k retrieval has no calibrated relevance cutoff yet. History-based retrieval is a simple prototype, not a fully validated query rewrite pipeline.

## Privacy and lifecycle

Original PDFs are not written by the app. Uploaded bytes, extracted text and chat live in process/session memory; embeddings and passages use ephemeral Chroma collections. Explicit reset deletes the current collection. Browser disconnect alone is not guaranteed to delete an orphaned collection; restarting the server clears ephemeral state. A production TTL/cleanup worker remains Week 3 work. Do not enable shared global Streamlit caches for indexes. OpenAI receives text for embeddings and retrieved passages/questions for generation; provider retention is separate from local reset. Keys stay in environment variables, never in source or chat. No provider calls were made during the offline validation.

## Verification and remaining gate

```bash
python -m pytest -q
python scripts/make_sample_pdfs.py
# Optional paid smoke run after configuring your own API key:
python -m scripts.live_smoke
```

Use the four synthetic PDFs under data/sample_pdfs. The opt-in smoke script prints answer, status and citations for an answerable and an absent-information question. Manually review whether every claim is supported. Also run conflict.pdf and hostile.pdf before client use; no live quality or security pass is claimed. The 40-question held-out evaluation and latency targets from Week 1 remain future work.

Week 2 extraction/metadata implementation is complete and locally tested. RAG implementation is present and offline tested; its tracker stays In progress until real OpenAI embedding/generation and source quality are checked. Basic Streamlit UI is included; Week 3 pilot and polish are not complete. Reviewer approval and submission remain manual.

## Integration references

- https://reference.langchain.com/python/langchain-chroma/vectorstores/Chroma
- https://reference.langchain.com/python/langchain-openai/chat_models/base/ChatOpenAI/with_structured_output

The installed versions and local tests, rather than documentation alone, establish the tested API compatibility. See the test log for limits.

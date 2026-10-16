# Workspace and handoff

## Workspace delivered

The package separates docs, data/sample, evaluation, src and tests. It includes an editable Excel master tracker, a JSON test set, a runnable standard-library baseline and recorded results. The source and test folders contain implementation handoff notes. This workspace is prepared and the baseline runs locally; the full app environment, API credentials and deployment are not yet provisioned.

## Risk and decision register

Incorrect answers are mitigated through grounded prompts, citations and unsupported-question cases. Poor extraction is handled through validation and explicit OCR exclusion. Data leakage is addressed with per-session indexes and isolation tests. Unexpected API costs require usage logging and an agreed spending cap. Corpus complexity may require revised scope after pilot uploads. Each risk has an owner and next action in the supporting documentation.

## Week 2 entry actions

Implement PDF extraction and metadata preservation first, then chunking and indexing, then retrieval and grounded answer generation. Add the Streamlit upload-and-chat interface after the core pipeline works. Replace text fixtures with equivalent PDF fixtures for page-citation tests. Confirm initial language, file limits, retention behavior, hosting and API budget with the reviewer without delaying sample-based development.

## Submission status

This is the original Week 1 planning and baseline report prepared from the supplied project plan and clarified upload-and-chat workflow. Documentation and sample baseline preparation are complete. The report does not claim that all four weeks of development, real-user validation or formal stakeholder sign-off have occurred.

## Source register

[1] LangChain, Retrieval: https://docs.langchain.com/oss/python/deepagents/retrieval
[2] Streamlit, st.file_uploader: https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader
[3] Chroma, Query and Get: https://docs.trychroma.com/docs/querying-collections/query-and-get
Official documentation reviewed on 16 October 2026. Project-specific limits, KPI targets and design decisions are proposals in this package, not claims made by these sources.
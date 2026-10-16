# Baseline audit and technical research

## Current workflow assessment

No observation of an existing client workflow was supplied. The comparison baseline is therefore a proposed manual process: open a document, use keyword search, inspect matching passages and record an answer with its source. Measure this later using the same questions as the app; do not report estimated manual timings as observed values.

## Desk research findings

Official LangChain documentation describes retrieval as supplying relevant context at runtime and RAG as combining retrieval with generation [1]. Streamlit provides a file upload widget [2]. Chroma supports vector similarity queries from text or embeddings [3]. These establish available building blocks, not application accuracy, privacy compliance or suitability for an untested workload.

## Architecture decision

Propose Python for application logic, LangChain for pipeline composition, OpenAI API for embeddings and answer generation, Chroma for the prototype index and Streamlit for the interface. Chroma is a provisional choice within the supplied plan; FAISS remains an alternative if requirements change. Keep embedding configuration consistent between ingestion and query. Exact model, versions, deployment and budget will be selected and verified during implementation.

## Executed sample baseline

A reproducible token-overlap retrieval baseline was run on three explicitly synthetic text files containing nine factual passages. The evaluation fixture includes nine answerable and three unanswerable questions. Top-three retrieval found the labeled source for 9 of 9 answerable questions (100%). Raw rankings and measured retrieval times are included in baseline_results.json. This is a tiny authored fixture and is not evidence of production quality.

## Baseline limitations

The baseline retrieves passages only; it does not generate answers, parse PDFs, validate page citations or reliably abstain. Unanswerable cases are retained for future app evaluation and excluded from retrieval hit-rate calculations. No OpenAI API call, paid service test, client interview, manual timing study or full RAG performance test is claimed.
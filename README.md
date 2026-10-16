# AI Document Knowledge Assistant and Q&A App

**Week 1 submission — Scope Definition and Baseline Analysis**  
Prepared for Huzaifa Sabeeh · 16 October 2026

This project will let users upload documents and ask questions through a chat interface. Answers will be grounded in the uploaded content and include source references. This repository contains the Week 1 planning deliverables and a reproducible sample retrieval baseline. The final RAG application is planned for subsequent weeks and is not implemented yet.

## Start here

| Deliverable | File | Purpose |
|---|---|---|
| Main submission report | [Week 1 Report](Week_1_Report.docx) | Five-page report covering scope, requirements, research, baseline and next steps |
| Project master sheet | [Master Tracker](Master_Tracker.xlsx) | Completed preparation, remaining activities and proposed KPIs |
| Project charter | [Charter](docs/01_project_charter.md) | Objective, scope, boundaries and responsibilities |
| Requirements | [Acceptance criteria](docs/02_requirements_and_acceptance_criteria.md) | Requirements R01–R09 and planned validation |
| Baseline audit | [Baseline and research](docs/03_baseline_audit_and_technical_research.md) | Current assumptions, official sources and sample results |
| Evaluation protocol | [KPIs](docs/04_kpis_and_evaluation_protocol.md) | Metric definitions, targets and held-out test design |
| Workspace handoff | [Handoff](docs/05_workspace_and_handoff.md) | Implementation priorities and Week 1 status |
| Decisions and risks | [Risk register](docs/06_decisions_and_risks.md) | Proposed decisions, risks and reviewer questions |

## Confirmed product flow

Users upload their documents after the product is available, then ask questions about them. Client documents are not needed for Week 1 sample-based preparation.

The proposed first version accepts text-based PDFs, retrieves relevant passages, answers with filename and page references, and explains when an answer is missing from the documents. Session isolation and safe handling of document content are included in the requirements. OCR and advanced external integrations are outside the initial proposed scope.

## Work completed in Week 1

- Defined the upload-and-chat use case, scope and acceptance requirements.
- Reviewed official technical documentation and recorded the sources.
- Prepared the charter, KPI definitions, baseline protocol and risk register.
- Created three synthetic sample documents and 12 labeled questions.
- Executed a simple, reproducible retrieval baseline and recorded its results.
- Prepared an editable project tracker and the workspace structure.

Reviewer sign-off remains unrecorded. The app, API integration, PDF extraction, deployment and real-user evaluation are not yet complete.

## Run the sample baseline

Prerequisite: Python 3. The recorded run used Python 3.12.14. This baseline uses only the Python standard library; no API key or paid service is needed.

From the repository root:

```bash
python evaluation/run_baseline.py
```

On systems where Python is named `python3`, use `python3 evaluation/run_baseline.py`.

The script reads [sample questions](evaluation/sample_questions.json) and the files under [data/sample](data/sample), then writes [baseline results](evaluation/baseline_results.json). Running it again overwrites the results file; timing values will vary.

### Recorded result and limits

| Measure | Result |
|---|---|
| Synthetic source documents | 3 |
| Answerable questions | 9 |
| Questions without an answer in the sources | 3 |
| Answerable questions with the correct source in the top 3 | 9 of 9 |
| Answer generation | Not implemented |
| Reliable abstention | Not implemented |

The method ranks text lines by token overlap. The 9-of-9 result measures retrieval on a tiny authored development fixture, not final AI answer accuracy or independent benchmark performance. Unanswerable questions are retained for future testing and excluded from the retrieval hit-rate denominator. Source line numbers refer to text files, not PDF pages.

## Planned application stack

Python, LangChain, OpenAI API, Chroma and Streamlit are proposed. Chroma is the provisional vector-store choice; FAISS remains an alternative. Exact dependency versions and model choices will be confirmed during implementation. The baseline does not require these packages, so no untested requirements file is supplied.

## Evaluation targets

Proposed targets are at least 80% fully correct supported answers, 95% citation correctness, 100% citation coverage, and 90% correct handling of unsupported questions. Answer latency has a provisional p95 target of 10 seconds after indexing. These targets are not achieved app results. See the KPI document for definitions and the planned separate 40-question evaluation set.

## Repository organization

| Location | Contents |
|---|---|
| `docs/` | Planning, audit, requirements, KPI and risk documents |
| `data/sample/` | Synthetic text fixtures only |
| `evaluation/` | Questions, baseline script and recorded results |
| `src/` | Week 2 implementation handoff note |
| `tests/` | Planned application test coverage |

Do not commit API keys, real customer uploads, personal data or generated session indexes. The included fixtures are synthetic. There is no software license grant in this submission; choose a license explicitly before offering broader reuse rights.

## Week 2 priorities

Implement PDF extraction with page metadata, chunking, embeddings, session-scoped indexing, retrieval and grounded answers. Then add the Streamlit upload-and-chat interface and validate error handling, source references and isolation.

Official references and access dates are included in the report and baseline audit. This repository is the Week 1 submission evidence, not a deployed application.

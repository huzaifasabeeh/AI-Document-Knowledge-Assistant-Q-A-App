# Project charter

## Purpose and confirmed workflow

Build an AI Document Knowledge Assistant and Q&A App in four weeks. The user confirmed that end users will upload their own documents after the product is available and then ask questions in chat. Client documents are therefore not a prerequisite for Week 1 preparation.

## Business objective

Reduce the effort needed to locate information in uploaded documents while making answers traceable to source passages. Actual time savings will be measured after implementation; none are claimed in this report.

## Proposed scope

The first version will accept text-based PDFs, process multiple documents in one isolated session, answer questions using retrieved passages, show filenames and PDF page numbers, and explain when the evidence is insufficient. English is the proposed initial document and answer language. File limits and language support remain configurable scope assumptions.

## Scope boundaries

OCR for scanned PDFs, complex table interpretation, external data connectors, custom model training, persistent chat history and enterprise user roles are deferred. A private prototype is appropriate initially; public multi-user hosting requires verified session isolation and access controls.

## Ownership and schedule

Prepared for Huzaifa Sabeeh and the project reviewer. Proposed responsibilities: Huzaifa owns implementation and evaluation; the reviewer confirms scope and acceptance criteria; end users provide documents at runtime. Week 1 covers requirements and baseline design, Week 2 the core pipeline, Week 3 integration and pilot evaluation, and Week 4 deployment and handoff. No calendar start date or external approval is assumed.
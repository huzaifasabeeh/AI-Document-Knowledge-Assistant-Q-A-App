# Evaluation source review — 28 October 2026

Reviewed all 40 questions against all pages of their assigned PDFs at main commit
`76426edf6b73d7c045904e28f1a51f62532f4b2e`. This is an assistant/author-side
review, not independent human approval and not a live model evaluation.

## Outcome

- Retain all 40 questions and expected answers: 20 direct, 5 paraphrased,
  5 multi-passage and 10 unsupported cases.
- All 30 answerable cases have supporting evidence on the stated physical pages.
- Each of the 10 unsupported questions was assessed against the full assigned
  document set, not just the retrieved excerpts. The requested detail is absent.
- No PDF, question, expected answer or candidate hash was changed.
- Human ground-truth approval remains pending; no model-performance score is claimed.

## Grading rules

Accept equivalent wording and units (72 hours = three days; 17:30 = 5:30 PM).
Require every requested component for a fully correct answer. Preserve currency,
working/calendar days, deadline starting events and target-versus-guarantee
distinctions. Judge citation support per claim, not just whether a page exists.
Additional factual claims must also be supported by the assigned documents.

For H36, a response can correctly note weekday operating hours while stating that
Sunday contact details are not specified. Do not require a word-for-word refusal
or penalize that supported context. Do reject an invented Sunday service number.

For H39, development leave.pdf is deliberately excluded. A remembered answer of
20 days is unsupported in this case even though it passed the separate smoke check.

## Case-by-case decisions

| Case | Decision | Review / scoring note |
|---|---|---|
| H01 | Retain | First Tuesday for the new starter; do not invent a time or calendar date. |
| H02 | Retain | People Operations team; do not substitute the mentor. |
| H03 | Retain | Five working days before start; calendar days is not equivalent. |
| H04 | Retain | Room 204; no other pickup location is stated. |
| H05 | Retain | Both assigned team mentor and end of week two are required. |
| H06 | Retain | Department lead for domestic travel before booking. |
| H07 | Retain | PKR 12000 per night; preserve currency and per-night basis. |
| H08 | Retain | PKR 2500 per travel day; preserve currency and per-day basis. |
| H09 | Retain | Within seven calendar days after returning; not working days or before travel. |
| H10 | Retain | Both signed declaration and Finance approval are required. |
| H11 | Retain | Monday–Friday and both 08:30/17:30 endpoints required; equivalent AM/PM accepted. |
| H12 | Retain | Call extension 410; do not invent a complete external telephone number. |
| H13 | Retain | HelpHub portal for routine requests; urgent telephone route is not equivalent. |
| H14 | Retain | 30-minute target first response during service hours; not guaranteed resolution. |
| H15 | Retain | Unresolved urgent incident: duty manager after two hours; both details required. |
| H16 | Retain | Team Vault folder; do not substitute a local folder. |
| H17 | Retain | Project owner is the sole approval role; do not substitute Finance. |
| H18 | Retain | 72 hours; three days is an equivalent duration. |
| H19 | Retain | 18 months after project closure; preserve the starting event. |
| H20 | Retain | Security desk within one hour of discovery; both destination and deadline required. |
| H21 | Retain | Introductory session maps to orientation; first Tuesday, not every Tuesday. |
| H22 | Retain | Same working-day deadline as H03; paraphrase must not change the unit. |
| H23 | Retain | Same calendar-day deadline as H09; after returning is the starting event. |
| H24 | Retain | Target first response, not resolution, in 30 minutes during service hours. |
| H25 | Retain | 72 hours / three days; accept duration phrasing instead of literal After 72 hours. |
| H26 | Retain | Orientation timing plus mentor and checklist timing; cite onboarding pages 1 and 2. |
| H27 | Retain | Hotel cap/currency/per-night basis plus receipt deadline/unit/event; cite travel pages 1 and 2. |
| H28 | Retain | Extension 410 plus escalation to duty manager after two hours; cite service pages 1 and 2. |
| H29 | Retain | Project owner plus 18 months after closure; cite records pages 1 and 2. |
| H30 | Retain | Room 204 plus team Vault folder; cite onboarding page 2 and records page 1. |
| H31 | Retain | Orientation schedule and organizer are provided; its duration is absent. |
| H32 | Retain | Equipment request deadline/location are provided; replacement budget is absent. |
| H33 | Retain | Only domestic hotel cap is provided; do not transfer it to international travel. |
| H34 | Retain | Hotel/meals/receipts are covered; personal-car mileage rate is absent. |
| H35 | Retain | Routine submission channel is provided; 30-minute target applies only to urgent incidents. |
| H36 | Retain | Weekday opening hours and urgent extension are provided; no Sunday support number is established. A limitation response may mention weekday hours, but must not assert extension 410 operates Sunday. Internal status remains not_found. |
| H37 | Retain | Storage location is named, but its encryption algorithm is absent. |
| H38 | Retain | Disclosure reporting deadline exists, but a financial penalty is absent. |
| H39 | Retain | All four assigned PDFs reviewed: no annual leave entitlement. Do not import the 20 days from development leave.pdf. |
| H40 | Retain | All four assigned PDFs reviewed: no named chief executive. Generic roles do not identify a person. |

## Limits and next gate

These four short synthetic documents contain only 20 underlying policy facts;
the paraphrases and combined questions reuse them. Only H30 spans multiple files.
This candidate does not establish real-client-document generalization, OCR quality,
large-file performance, privacy or application recovery. Conflicting and hostile
documents remain separate development acceptance cases.

The app UI exposes cited supporting passages but not necessarily every retrieved
chunk or measured token usage. Record unavailable telemetry as null; do not infer it
from screenshots. Keep the first-attempt results, failures and retries distinct.

The owner/reviewer should approve the question set and these scoring rules before
the final run, then record reviewer, date and the reviewed commit. A review request
does not itself constitute approval. Use `scripts.prepare_evaluation` for a new log.
`review.json` binds this review to the exact question/PDF hashes.

# Human ground-truth review checklist: candidate-1

Historical preparation aid. On 31 October 2026 Huzaifa Sabeeh separately approved
the supplied AI-assisted review and D01-D08 protocol, waiving independent human
review. No independent approval is claimed; the unchecked human-review fields
below remain historical. On 2 November the remaining local primary attempts
finished; that cohort failed (H22 technical failure, H27 over ten seconds).
The later full retest met quality thresholds but failed on H03 at 11.8807s.
Four bounded diagnostics did not reproduce the slowdown and replace no failed
result. Independent human review is waived, not an outstanding approval blocker;
hosted acceptance and final client sign-off remain pending.
Current results and exact evidence are in the [checkpoint](local_setup_progress.md)
and [handover](evaluation_handover.md). Preparation-time statements below describe
the earlier state, not current execution or approval status.

Prepared 2026-10-31 (Asia/Karachi). **Independent human approval: PENDING.**
**40-question evaluation: Not run. No provider requests were made.**

This is a review aid derived from the existing candidate and authored source review.
Its unchecked boxes are requests for human review, not approvals or test results.
The original candidate, manifest, REVIEW.md and review.json remain unchanged.
These four short synthetic PDFs contain 20 underlying facts; paraphrases and
combined cases reuse them, so this is not 40 independent facts. Only H30 spans
multiple PDFs. The nine development conflict/hostile cases remain separate from
the 40-question KPI denominators. This candidate does not establish OCR,
large-document or real-client generalization.

## What the human reviewer must do

1. Read every case H01-H40 below against the exact assigned PDF pages. Check the
   question, expected answer, document scope and scoring note; record disagreements.
2. For H31-H40 inspect every page of every assigned file. No excerpt can prove
   absence by itself; the complete eight-page text appendix is included below.
3. Resolve D01-D08 before approving the scoring protocol. Distinguish confirmations
   of existing author rules from new proposed operational clarifications.
4. Record reviewer name, review date/time, independence and any case exceptions
   in the private decision record. Only a real human may record approval.
5. After approval, freeze this candidate revision and manifest; changes need a new
   version/review. A later live run also needs its exact tested app/deployed revision,
   provider/models, prompt/chunk settings and runtime. No such run is authorized here.

## Candidate identity and offline verification

- Proposed candidate source revision: `b5a876af001d72091443d43e3723998e76788d5b`. It is not a human-approved freeze.
- Git tree: `a2d1ad05ccc598435c1b2b36842815bb3fa0f6d5`.
- Candidate directory tree: `a715200c4651b2db198c653f2a78acd1d99a2ad5`.
- PDF directory tree: `8c10f349047e05aef0016d737e178c4f588ae32b`.
- Authored review source revision: `76426edf6b73d7c045904e28f1a51f62532f4b2e`; its hashes still bind
  to these exact questions and PDFs. That assistant/author review is not human approval.
- PASS: all six manifest digests match actual bytes; review.json bindings match.
- PASS: 40 unique cases: 20 direct, 5 paraphrased, 5 multi-passage, 10 unanswerable;
  30 supported expectations match strict-reader physical-page text across 4 PDFs / 8 pages.
- Relevant offline workflow tests: **2 passed in 0.92s**. File/evidence consistency
  and safe blank-record creation do not establish live model quality.

| File | SHA-256 (actual bytes; manifest values match for the first six) |
| --- | --- |
| `evaluation/heldout/corpus.json` | `436dd06da195eba1f05a96be3644b8697923d1572e77ee4419b9a03323fad05b` |
| `evaluation/heldout/questions.json` | `a606a745e8f812e65efded3ec942c419afe33b8bc75263fd3169288b0386c25e` |
| `data/heldout_pdfs/onboarding.pdf` | `e7a42eaa29c7a00899e751666e2e8e04cc506e4d0c2a1ff48e6f409bd810e3aa` |
| `data/heldout_pdfs/travel.pdf` | `36d645566630df1f4ac0f45b632d3e0514a1d8a1a7b777bfc60cd4799dc40058` |
| `data/heldout_pdfs/service.pdf` | `008fbcc261f92777d03edb8febb325b5502f3b03df4e956a9b9c9f1eb6193a63` |
| `data/heldout_pdfs/records.pdf` | `cfe8f525a0b1be6627c134ab66c87ff0656c99eb17d309cab78d3949ffaf8e7a` |
| `evaluation/heldout/manifest.json` | `67c7eb1b6e04021f207e0566099815c9eaf4e384cc8ead1b9de6b5c70022c6e2` |
| `evaluation/heldout/review.json` | `3fe54be0d2c170009a54c1bee33b3e15f5150ab9c720aa5c4ca72c01bf46e4d2` |

## Scoring criteria to approve

- Fully correct supported answers / **30 answerable cases**; abstention is incorrect
  on an answerable case. Require all requested components; equivalent wording is allowed.
  Target: **at least 24/30 (80%)**.
- Supported claim-to-source pairs / all supplied citation pairs on factual answers:
  **at least 95%**. Judge semantic support and exact physical pages, not just file existence.
- Factual claims with citations / all factual claims: **100%**. A citation can count
  for coverage yet fail semantic correctness; measure both.
- Appropriate abstentions / **10 unsupported cases**: **at least 9/10 (90%)**.
  Do not infer missing facts or import development fixtures.
- Latency: median and nearest-rank p95 (`sorted_times[ceil(0.95*n)-1]`)
  from recorded completed response times; report n and failures/timeouts separately.
  Indexing is separate. Existing p95 <=10 seconds is provisional; resolve D08.
- Zero citation/claim denominators are undefined, not PASS. Missing runs cannot
  support a full-set result. Failed API calls are failed attempts, not abstentions.
- Preserve actual answers, passages, citations, timing and failures. Unknown usage,
  cost or unavailable retrieved-chunk telemetry stays null; do not infer from screenshots.
- Time manual searches on the same cases; record comparison order, alternating
  manual-first/app-first where feasible. Do not tune against this candidate and
  subsequently describe it as unseen.

## Human decisions before freeze

### D01: Context and equivalent wording: H07/H08/H14/H24/H27

- [ ] Human decision recorded — **PENDING**. Existing rules preserve currency, per-night/per-day basis, working/calendar days, and target first response versus resolution. PROPOSED clarification: accept concise wording only when the exact question makes omitted context unambiguous. For example, decide whether H24 "30 minutes" is sufficient; reject guaranteed resolution claims. This does not permit changing the units or policy scope.

### D02: Unspecified escalation clock start: H15/H28

- [ ] Human decision recorded — **PENDING**. The PDF says duty manager after two hours, without defining the timer start. PROPOSED: require the role/duration but do not require or invent "after reporting" versus "after occurrence"; an asserted start event has no supplied support.

### D03: Unspecified link-expiry clock start: H18/H25

- [ ] Human decision recorded — **PENDING**. Accept 72 hours or three days under the authored rule. PROPOSED: do not require approval/creation/first-access as a starting event; the source does not state one. H25 expects a duration, not the literal phrase "After 72 hours".

### D04: Abstention with supported context: H35/H36

- [ ] Human decision recorded — **PENDING**. Confirm the authored rule: urgent first-response target cannot answer the routine-request question. H36 remains not_found for a Sunday number; weekday-hours context is allowed, but extension 410 must not be asserted to work Sunday. Do not infer an alternative Sunday policy.

### D05: Assigned-document boundary: H39/H40

- [ ] Human decision recorded — **PENDING**. Confirm the authored rule: use only all four listed held-out PDFs. No annual leave entitlement or named chief executive appears there. In particular, the 20-day answer from development leave.pdf is unsupported for H39.

### D06: Multi-part completeness and claim scoring: H26-H30 and extra claims

- [ ] Human decision recorded — **PENDING**. Confirm the authored all-components rule and the required pages for each component. H30 alone spans files. Before running, agree how atomic factual claims and claim-to-source pairs are counted consistently; filename/page existence alone is insufficient. Additional factual claims require support, including context added to an abstention.

### D07: Primary attempts, failures and retries

- [ ] Human decision recorded — **PENDING**. Existing rules keep first attempts, failures and retries separate; failed requests are not abstentions. PROPOSED: the first attempt is the primary 40-case outcome, and retries receive a separate linked record rather than overwriting it. An incomplete set cannot support a full-set result; choose the treatment of blocked attempts before the run.

### D08: Targets and timing protocol

- [ ] Human decision recorded — **PENDING**. Confirm 80% answer correctness (24/30), 95% citation correctness, 100% citation coverage and 90% appropriate abstention (9/10). The existing p95 <=10-second latency target is provisional: decide whether it is an acceptance gate or descriptive target. Confirm start/end points, treatment of completed abstentions and manual-first/app-first ordering. Unknown telemetry/cost stays null.

## All 40 cases: question, answer, evidence and case scoring

Each checkbox covers independent human verification of ground truth and scoring,
not whether the app has passed the case. Upload only the listed files in a later run.

### H01 — direct

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** When do new starters attend orientation?

**Assigned PDFs:** [onboarding.pdf](../data/heldout_pdfs/onboarding.pdf).

**Expected status:** `answered`. **Expected answer:** Their first Tuesday.

**Physical-page evidence / full-scope absence check:**

- [onboarding.pdf, physical page 1](../data/heldout_pdfs/onboarding.pdf#page=1): "New starters attend orientation on their first Tuesday."

**Case scoring (existing authored rule, awaiting human confirmation):** First Tuesday for the new starter; do not invent a time or calendar date.

### H02 — direct

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** Who runs orientation?

**Assigned PDFs:** [onboarding.pdf](../data/heldout_pdfs/onboarding.pdf).

**Expected status:** `answered`. **Expected answer:** The People Operations team.

**Physical-page evidence / full-scope absence check:**

- [onboarding.pdf, physical page 1](../data/heldout_pdfs/onboarding.pdf#page=1): "The People Operations team runs orientation."

**Case scoring (existing authored rule, awaiting human confirmation):** People Operations team; do not substitute the mentor.

### H03 — direct

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** How far ahead of the start date must equipment requests be submitted?

**Assigned PDFs:** [onboarding.pdf](../data/heldout_pdfs/onboarding.pdf).

**Expected status:** `answered`. **Expected answer:** Five working days before the start date.

**Physical-page evidence / full-scope absence check:**

- [onboarding.pdf, physical page 1](../data/heldout_pdfs/onboarding.pdf#page=1): "Equipment requests must be submitted five working days before the start date."

**Case scoring (existing authored rule, awaiting human confirmation):** Five working days before start; calendar days is not equivalent.

### H04 — direct

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** Where do new starters collect laptops?

**Assigned PDFs:** [onboarding.pdf](../data/heldout_pdfs/onboarding.pdf).

**Expected status:** `answered`. **Expected answer:** Room 204.

**Physical-page evidence / full-scope absence check:**

- [onboarding.pdf, physical page 2](../data/heldout_pdfs/onboarding.pdf#page=2): "New starters collect laptops from Room 204."

**Case scoring (existing authored rule, awaiting human confirmation):** Room 204; no other pickup location is stated.

### H05 — direct

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** Who reviews the onboarding checklist, and when?

**Assigned PDFs:** [onboarding.pdf](../data/heldout_pdfs/onboarding.pdf).

**Expected status:** `answered`. **Expected answer:** The assigned team mentor, at the end of week two.

**Physical-page evidence / full-scope absence check:**

- [onboarding.pdf, physical page 2](../data/heldout_pdfs/onboarding.pdf#page=2): "The assigned team mentor reviews the onboarding checklist at the end of week two."

**Case scoring (existing authored rule, awaiting human confirmation):** Both assigned team mentor and end of week two are required.

### H06 — direct

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** Who must approve domestic travel before booking?

**Assigned PDFs:** [travel.pdf](../data/heldout_pdfs/travel.pdf).

**Expected status:** `answered`. **Expected answer:** The department lead.

**Physical-page evidence / full-scope absence check:**

- [travel.pdf, physical page 1](../data/heldout_pdfs/travel.pdf#page=1): "Domestic travel requires approval from the department lead before booking."

**Case scoring (existing authored rule, awaiting human confirmation):** Department lead for domestic travel before booking.

### H07 — direct

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** What is the domestic hotel reimbursement limit per night?

**Assigned PDFs:** [travel.pdf](../data/heldout_pdfs/travel.pdf).

**Expected status:** `answered`. **Expected answer:** PKR 12000 per night.

**Physical-page evidence / full-scope absence check:**

- [travel.pdf, physical page 1](../data/heldout_pdfs/travel.pdf#page=1): "The domestic hotel reimbursement limit is PKR 12000 per night."

**Case scoring (existing authored rule, awaiting human confirmation):** PKR 12000 per night; preserve currency and per-night basis.

### H08 — direct

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** What is the meal claim cap per travel day?

**Assigned PDFs:** [travel.pdf](../data/heldout_pdfs/travel.pdf).

**Expected status:** `answered`. **Expected answer:** PKR 2500 per travel day.

**Physical-page evidence / full-scope absence check:**

- [travel.pdf, physical page 1](../data/heldout_pdfs/travel.pdf#page=1): "Meal claims are capped at PKR 2500 per travel day."

**Case scoring (existing authored rule, awaiting human confirmation):** PKR 2500 per travel day; preserve currency and per-day basis.

### H09 — direct

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** When must travel receipts be uploaded?

**Assigned PDFs:** [travel.pdf](../data/heldout_pdfs/travel.pdf).

**Expected status:** `answered`. **Expected answer:** Within seven calendar days after returning.

**Physical-page evidence / full-scope absence check:**

- [travel.pdf, physical page 2](../data/heldout_pdfs/travel.pdf#page=2): "Travel receipts must be uploaded within seven calendar days after returning."

**Case scoring (existing authored rule, awaiting human confirmation):** Within seven calendar days after returning; not working days or before travel.

### H10 — direct

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** What is required when a travel receipt is lost?

**Assigned PDFs:** [travel.pdf](../data/heldout_pdfs/travel.pdf).

**Expected status:** `answered`. **Expected answer:** A signed declaration and Finance approval.

**Physical-page evidence / full-scope absence check:**

- [travel.pdf, physical page 2](../data/heldout_pdfs/travel.pdf#page=2): "A lost travel receipt requires a signed declaration and Finance approval."

**Case scoring (existing authored rule, awaiting human confirmation):** Both signed declaration and Finance approval are required.

### H11 — direct

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** What are the service desk operating days and hours?

**Assigned PDFs:** [service.pdf](../data/heldout_pdfs/service.pdf).

**Expected status:** `answered`. **Expected answer:** Monday to Friday, 08:30 to 17:30.

**Physical-page evidence / full-scope absence check:**

- [service.pdf, physical page 1](../data/heldout_pdfs/service.pdf#page=1): "The service desk operates Monday to Friday from 08:30 to 17:30."

**Case scoring (existing authored rule, awaiting human confirmation):** Monday–Friday and both 08:30/17:30 endpoints required; equivalent AM/PM accepted.

### H12 — direct

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** How must urgent incidents be reported?

**Assigned PDFs:** [service.pdf](../data/heldout_pdfs/service.pdf).

**Expected status:** `answered`. **Expected answer:** Call extension 410.

**Physical-page evidence / full-scope absence check:**

- [service.pdf, physical page 1](../data/heldout_pdfs/service.pdf#page=1): "Urgent incidents must be reported by calling extension 410."

**Case scoring (existing authored rule, awaiting human confirmation):** Call extension 410; do not invent a complete external telephone number.

### H13 — direct

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** Where must routine requests be submitted?

**Assigned PDFs:** [service.pdf](../data/heldout_pdfs/service.pdf).

**Expected status:** `answered`. **Expected answer:** The HelpHub portal.

**Physical-page evidence / full-scope absence check:**

- [service.pdf, physical page 1](../data/heldout_pdfs/service.pdf#page=1): "Routine requests must be submitted through the HelpHub portal."

**Case scoring (existing authored rule, awaiting human confirmation):** HelpHub portal for routine requests; urgent telephone route is not equivalent.

### H14 — direct

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** What is the target first response for urgent incidents during service hours?

**Assigned PDFs:** [service.pdf](../data/heldout_pdfs/service.pdf).

**Expected status:** `answered`. **Expected answer:** 30 minutes during service hours.

**Physical-page evidence / full-scope absence check:**

- [service.pdf, physical page 2](../data/heldout_pdfs/service.pdf#page=2): "Urgent incidents have a target first response of 30 minutes during service hours."

**Case scoring (existing authored rule, awaiting human confirmation):** 30-minute target first response during service hours; not guaranteed resolution.

### H15 — direct

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** When and to whom is an unresolved urgent incident escalated?

**Assigned PDFs:** [service.pdf](../data/heldout_pdfs/service.pdf).

**Expected status:** `answered`. **Expected answer:** To the duty manager after two hours.

**Physical-page evidence / full-scope absence check:**

- [service.pdf, physical page 2](../data/heldout_pdfs/service.pdf#page=2): "An unresolved urgent incident is escalated to the duty manager after two hours."

**Case scoring (existing authored rule, awaiting human confirmation):** Unresolved urgent incident: duty manager after two hours; both details required.

### H16 — direct

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** Where must project records be stored?

**Assigned PDFs:** [records.pdf](../data/heldout_pdfs/records.pdf).

**Expected status:** `answered`. **Expected answer:** The team Vault folder.

**Physical-page evidence / full-scope absence check:**

- [records.pdf, physical page 1](../data/heldout_pdfs/records.pdf#page=1): "Project records must be stored in the team Vault folder."

**Case scoring (existing authored rule, awaiting human confirmation):** Team Vault folder; do not substitute a local folder.

### H17 — direct

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** Who may approve external sharing of project records?

**Assigned PDFs:** [records.pdf](../data/heldout_pdfs/records.pdf).

**Expected status:** `answered`. **Expected answer:** Only the project owner.

**Physical-page evidence / full-scope absence check:**

- [records.pdf, physical page 1](../data/heldout_pdfs/records.pdf#page=1): "Only the project owner may approve external sharing of project records."

**Case scoring (existing authored rule, awaiting human confirmation):** Project owner is the sole approval role; do not substitute Finance.

### H18 — direct

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** When do approved external sharing links expire?

**Assigned PDFs:** [records.pdf](../data/heldout_pdfs/records.pdf).

**Expected status:** `answered`. **Expected answer:** After 72 hours.

**Physical-page evidence / full-scope absence check:**

- [records.pdf, physical page 1](../data/heldout_pdfs/records.pdf#page=1): "Approved external sharing links expire after 72 hours."

**Case scoring (existing authored rule, awaiting human confirmation):** 72 hours; three days is an equivalent duration.

### H19 — direct

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** How long are closed-project records retained?

**Assigned PDFs:** [records.pdf](../data/heldout_pdfs/records.pdf).

**Expected status:** `answered`. **Expected answer:** 18 months after project closure.

**Physical-page evidence / full-scope absence check:**

- [records.pdf, physical page 2](../data/heldout_pdfs/records.pdf#page=2): "Closed-project records are retained for 18 months after project closure."

**Case scoring (existing authored rule, awaiting human confirmation):** 18 months after project closure; preserve the starting event.

### H20 — direct

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** Where and when must a suspected data disclosure be reported?

**Assigned PDFs:** [records.pdf](../data/heldout_pdfs/records.pdf).

**Expected status:** `answered`. **Expected answer:** To the security desk within one hour of discovery.

**Physical-page evidence / full-scope absence check:**

- [records.pdf, physical page 2](../data/heldout_pdfs/records.pdf#page=2): "A suspected data disclosure must be reported to the security desk within one hour of discovery."

**Case scoring (existing authored rule, awaiting human confirmation):** Security desk within one hour of discovery; both destination and deadline required.

### H21 — paraphrased

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** I have just joined. On which day should I go to the introductory session?

**Assigned PDFs:** [onboarding.pdf](../data/heldout_pdfs/onboarding.pdf).

**Expected status:** `answered`. **Expected answer:** Their first Tuesday.

**Physical-page evidence / full-scope absence check:**

- [onboarding.pdf, physical page 1](../data/heldout_pdfs/onboarding.pdf#page=1): "New starters attend orientation on their first Tuesday."

**Case scoring (existing authored rule, awaiting human confirmation):** Introductory session maps to orientation; first Tuesday, not every Tuesday.

### H22 — paraphrased

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** When should I send my equipment request relative to my joining date?

**Assigned PDFs:** [onboarding.pdf](../data/heldout_pdfs/onboarding.pdf).

**Expected status:** `answered`. **Expected answer:** Five working days before the start date.

**Physical-page evidence / full-scope absence check:**

- [onboarding.pdf, physical page 1](../data/heldout_pdfs/onboarding.pdf#page=1): "Equipment requests must be submitted five working days before the start date."

**Case scoring (existing authored rule, awaiting human confirmation):** Same working-day deadline as H03; paraphrase must not change the unit.

### H23 — paraphrased

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** After my trip ends, how much time do I have to send in the receipts?

**Assigned PDFs:** [travel.pdf](../data/heldout_pdfs/travel.pdf).

**Expected status:** `answered`. **Expected answer:** Within seven calendar days after returning.

**Physical-page evidence / full-scope absence check:**

- [travel.pdf, physical page 2](../data/heldout_pdfs/travel.pdf#page=2): "Travel receipts must be uploaded within seven calendar days after returning."

**Case scoring (existing authored rule, awaiting human confirmation):** Same calendar-day deadline as H09; after returning is the starting event.

### H24 — paraphrased

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** During opening hours, how quickly should the desk first respond to an urgent incident?

**Assigned PDFs:** [service.pdf](../data/heldout_pdfs/service.pdf).

**Expected status:** `answered`. **Expected answer:** 30 minutes during service hours.

**Physical-page evidence / full-scope absence check:**

- [service.pdf, physical page 2](../data/heldout_pdfs/service.pdf#page=2): "Urgent incidents have a target first response of 30 minutes during service hours."

**Case scoring (existing authored rule, awaiting human confirmation):** Target first response, not resolution, in 30 minutes during service hours.

### H25 — paraphrased

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** How long will a permitted outside-sharing link stay usable?

**Assigned PDFs:** [records.pdf](../data/heldout_pdfs/records.pdf).

**Expected status:** `answered`. **Expected answer:** After 72 hours.

**Physical-page evidence / full-scope absence check:**

- [records.pdf, physical page 1](../data/heldout_pdfs/records.pdf#page=1): "Approved external sharing links expire after 72 hours."

**Case scoring (existing authored rule, awaiting human confirmation):** 72 hours / three days; accept duration phrasing instead of literal After 72 hours.

### H26 — multi_passage

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** When is orientation, and who reviews the onboarding checklist at what point?

**Assigned PDFs:** [onboarding.pdf](../data/heldout_pdfs/onboarding.pdf).

**Expected status:** `answered`. **Expected answer:** Their first Tuesday. The assigned team mentor, at the end of week two.

**Physical-page evidence / full-scope absence check:**

- [onboarding.pdf, physical page 1](../data/heldout_pdfs/onboarding.pdf#page=1): "New starters attend orientation on their first Tuesday."
- [onboarding.pdf, physical page 2](../data/heldout_pdfs/onboarding.pdf#page=2): "The assigned team mentor reviews the onboarding checklist at the end of week two."

**Case scoring (existing authored rule, awaiting human confirmation):** Orientation timing plus mentor and checklist timing; cite onboarding pages 1 and 2.

### H27 — multi_passage

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** What is the nightly domestic hotel cap, and how soon after returning must receipts be uploaded?

**Assigned PDFs:** [travel.pdf](../data/heldout_pdfs/travel.pdf).

**Expected status:** `answered`. **Expected answer:** PKR 12000 per night. Within seven calendar days after returning.

**Physical-page evidence / full-scope absence check:**

- [travel.pdf, physical page 1](../data/heldout_pdfs/travel.pdf#page=1): "The domestic hotel reimbursement limit is PKR 12000 per night."
- [travel.pdf, physical page 2](../data/heldout_pdfs/travel.pdf#page=2): "Travel receipts must be uploaded within seven calendar days after returning."

**Case scoring (existing authored rule, awaiting human confirmation):** Hotel cap/currency/per-night basis plus receipt deadline/unit/event; cite travel pages 1 and 2.

### H28 — multi_passage

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** How do I report an urgent incident, and when and to whom is it escalated if unresolved?

**Assigned PDFs:** [service.pdf](../data/heldout_pdfs/service.pdf).

**Expected status:** `answered`. **Expected answer:** Call extension 410. To the duty manager after two hours.

**Physical-page evidence / full-scope absence check:**

- [service.pdf, physical page 1](../data/heldout_pdfs/service.pdf#page=1): "Urgent incidents must be reported by calling extension 410."
- [service.pdf, physical page 2](../data/heldout_pdfs/service.pdf#page=2): "An unresolved urgent incident is escalated to the duty manager after two hours."

**Case scoring (existing authored rule, awaiting human confirmation):** Extension 410 plus escalation to duty manager after two hours; cite service pages 1 and 2.

### H29 — multi_passage

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** Who approves sharing project records externally, and how long are records kept after closure?

**Assigned PDFs:** [records.pdf](../data/heldout_pdfs/records.pdf).

**Expected status:** `answered`. **Expected answer:** Only the project owner. 18 months after project closure.

**Physical-page evidence / full-scope absence check:**

- [records.pdf, physical page 1](../data/heldout_pdfs/records.pdf#page=1): "Only the project owner may approve external sharing of project records."
- [records.pdf, physical page 2](../data/heldout_pdfs/records.pdf#page=2): "Closed-project records are retained for 18 months after project closure."

**Case scoring (existing authored rule, awaiting human confirmation):** Project owner plus 18 months after closure; cite records pages 1 and 2.

### H30 — multi_passage

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** Where do I collect my laptop, and where must I store project records?

**Assigned PDFs:** [onboarding.pdf](../data/heldout_pdfs/onboarding.pdf), [records.pdf](../data/heldout_pdfs/records.pdf).

**Expected status:** `answered`. **Expected answer:** Room 204. The team Vault folder.

**Physical-page evidence / full-scope absence check:**

- [onboarding.pdf, physical page 2](../data/heldout_pdfs/onboarding.pdf#page=2): "New starters collect laptops from Room 204."
- [records.pdf, physical page 1](../data/heldout_pdfs/records.pdf#page=1): "Project records must be stored in the team Vault folder."

**Case scoring (existing authored rule, awaiting human confirmation):** Room 204 plus team Vault folder; cite onboarding page 2 and records page 1.

### H31 — unanswerable

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** How long does orientation last?

**Assigned PDFs:** [onboarding.pdf](../data/heldout_pdfs/onboarding.pdf).

**Expected status:** `not_found`. **Expected answer:** State that the supplied documents do not contain enough information. Do not infer or invent the missing detail.

**Physical-page evidence / full-scope absence check:**

No supporting passage exists for the requested fact in this candidate.
Review the complete assigned scope; these page ranges are context, not a citation supporting the absent fact:

- [onboarding.pdf](../data/heldout_pdfs/onboarding.pdf): physical pages 1-2; complete extracted text in the appendix.

**Case scoring (existing authored rule, awaiting human confirmation):** Orientation schedule and organizer are provided; its duration is absent.

### H32 — unanswerable

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** What is the equipment replacement budget?

**Assigned PDFs:** [onboarding.pdf](../data/heldout_pdfs/onboarding.pdf).

**Expected status:** `not_found`. **Expected answer:** State that the supplied documents do not contain enough information. Do not infer or invent the missing detail.

**Physical-page evidence / full-scope absence check:**

No supporting passage exists for the requested fact in this candidate.
Review the complete assigned scope; these page ranges are context, not a citation supporting the absent fact:

- [onboarding.pdf](../data/heldout_pdfs/onboarding.pdf): physical pages 1-2; complete extracted text in the appendix.

**Case scoring (existing authored rule, awaiting human confirmation):** Equipment request deadline/location are provided; replacement budget is absent.

### H33 — unanswerable

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** What is the international hotel reimbursement limit?

**Assigned PDFs:** [travel.pdf](../data/heldout_pdfs/travel.pdf).

**Expected status:** `not_found`. **Expected answer:** State that the supplied documents do not contain enough information. Do not infer or invent the missing detail.

**Physical-page evidence / full-scope absence check:**

No supporting passage exists for the requested fact in this candidate.
Review the complete assigned scope; these page ranges are context, not a citation supporting the absent fact:

- [travel.pdf](../data/heldout_pdfs/travel.pdf): physical pages 1-2; complete extracted text in the appendix.

**Case scoring (existing authored rule, awaiting human confirmation):** Only domestic hotel cap is provided; do not transfer it to international travel.

### H34 — unanswerable

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** What mileage rate is paid for a personal car?

**Assigned PDFs:** [travel.pdf](../data/heldout_pdfs/travel.pdf).

**Expected status:** `not_found`. **Expected answer:** State that the supplied documents do not contain enough information. Do not infer or invent the missing detail.

**Physical-page evidence / full-scope absence check:**

No supporting passage exists for the requested fact in this candidate.
Review the complete assigned scope; these page ranges are context, not a citation supporting the absent fact:

- [travel.pdf](../data/heldout_pdfs/travel.pdf): physical pages 1-2; complete extracted text in the appendix.

**Case scoring (existing authored rule, awaiting human confirmation):** Hotel/meals/receipts are covered; personal-car mileage rate is absent.

### H35 — unanswerable

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** What is the target first response for routine requests?

**Assigned PDFs:** [service.pdf](../data/heldout_pdfs/service.pdf).

**Expected status:** `not_found`. **Expected answer:** State that the supplied documents do not contain enough information. Do not infer or invent the missing detail.

**Physical-page evidence / full-scope absence check:**

No supporting passage exists for the requested fact in this candidate.
Review the complete assigned scope; these page ranges are context, not a citation supporting the absent fact:

- [service.pdf](../data/heldout_pdfs/service.pdf): physical pages 1-2; complete extracted text in the appendix.

**Case scoring (existing authored rule, awaiting human confirmation):** Routine submission channel is provided; 30-minute target applies only to urgent incidents.

### H36 — unanswerable

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** Which phone number provides service desk support on Sundays?

**Assigned PDFs:** [service.pdf](../data/heldout_pdfs/service.pdf).

**Expected status:** `not_found`. **Expected answer:** State that the supplied documents do not contain enough information. Do not infer or invent the missing detail.

**Physical-page evidence / full-scope absence check:**

No supporting passage exists for the requested fact in this candidate.
Review the complete assigned scope; these page ranges are context, not a citation supporting the absent fact:

- [service.pdf](../data/heldout_pdfs/service.pdf): physical pages 1-2; complete extracted text in the appendix.

**Case scoring (existing authored rule, awaiting human confirmation):** Weekday opening hours and urgent extension are provided; no Sunday support number is established. A limitation response may mention weekday hours, but must not assert extension 410 operates Sunday. Internal status remains not_found.

### H37 — unanswerable

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** Which encryption algorithm protects the Vault folder?

**Assigned PDFs:** [records.pdf](../data/heldout_pdfs/records.pdf).

**Expected status:** `not_found`. **Expected answer:** State that the supplied documents do not contain enough information. Do not infer or invent the missing detail.

**Physical-page evidence / full-scope absence check:**

No supporting passage exists for the requested fact in this candidate.
Review the complete assigned scope; these page ranges are context, not a citation supporting the absent fact:

- [records.pdf](../data/heldout_pdfs/records.pdf): physical pages 1-2; complete extracted text in the appendix.

**Case scoring (existing authored rule, awaiting human confirmation):** Storage location is named, but its encryption algorithm is absent.

### H38 — unanswerable

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** What is the financial penalty for late disclosure reporting?

**Assigned PDFs:** [records.pdf](../data/heldout_pdfs/records.pdf).

**Expected status:** `not_found`. **Expected answer:** State that the supplied documents do not contain enough information. Do not infer or invent the missing detail.

**Physical-page evidence / full-scope absence check:**

No supporting passage exists for the requested fact in this candidate.
Review the complete assigned scope; these page ranges are context, not a citation supporting the absent fact:

- [records.pdf](../data/heldout_pdfs/records.pdf): physical pages 1-2; complete extracted text in the appendix.

**Case scoring (existing authored rule, awaiting human confirmation):** Disclosure reporting deadline exists, but a financial penalty is absent.

### H39 — unanswerable

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** How many annual leave days do Northstar employees receive?

**Assigned PDFs:** [onboarding.pdf](../data/heldout_pdfs/onboarding.pdf), [travel.pdf](../data/heldout_pdfs/travel.pdf), [service.pdf](../data/heldout_pdfs/service.pdf), [records.pdf](../data/heldout_pdfs/records.pdf).

**Expected status:** `not_found`. **Expected answer:** State that the supplied documents do not contain enough information. Do not infer or invent the missing detail.

**Physical-page evidence / full-scope absence check:**

No supporting passage exists for the requested fact in this candidate.
Review the complete assigned scope; these page ranges are context, not a citation supporting the absent fact:

- [onboarding.pdf](../data/heldout_pdfs/onboarding.pdf): physical pages 1-2; complete extracted text in the appendix.
- [travel.pdf](../data/heldout_pdfs/travel.pdf): physical pages 1-2; complete extracted text in the appendix.
- [service.pdf](../data/heldout_pdfs/service.pdf): physical pages 1-2; complete extracted text in the appendix.
- [records.pdf](../data/heldout_pdfs/records.pdf): physical pages 1-2; complete extracted text in the appendix.

**Case scoring (existing authored rule, awaiting human confirmation):** All four assigned PDFs reviewed: no annual leave entitlement. Do not import the 20 days from development leave.pdf.

### H40 — unanswerable

- [ ] Ground truth and scoring independently reviewed — **PENDING**.

**Question:** Who is the named individual serving as chief executive?

**Assigned PDFs:** [onboarding.pdf](../data/heldout_pdfs/onboarding.pdf), [travel.pdf](../data/heldout_pdfs/travel.pdf), [service.pdf](../data/heldout_pdfs/service.pdf), [records.pdf](../data/heldout_pdfs/records.pdf).

**Expected status:** `not_found`. **Expected answer:** State that the supplied documents do not contain enough information. Do not infer or invent the missing detail.

**Physical-page evidence / full-scope absence check:**

No supporting passage exists for the requested fact in this candidate.
Review the complete assigned scope; these page ranges are context, not a citation supporting the absent fact:

- [onboarding.pdf](../data/heldout_pdfs/onboarding.pdf): physical pages 1-2; complete extracted text in the appendix.
- [travel.pdf](../data/heldout_pdfs/travel.pdf): physical pages 1-2; complete extracted text in the appendix.
- [service.pdf](../data/heldout_pdfs/service.pdf): physical pages 1-2; complete extracted text in the appendix.
- [records.pdf](../data/heldout_pdfs/records.pdf): physical pages 1-2; complete extracted text in the appendix.

**Case scoring (existing authored rule, awaiting human confirmation):** All four assigned PDFs reviewed: no named chief executive. Generic roles do not identify a person.

## Complete PDF text appendix for absence review

Extracted offline using a strict PDF reader. Physical page numbers start at 1.
Compare the PDF itself when approving; headers and footers are included.

### onboarding.pdf — physical page 1

[Open PDF page](../data/heldout_pdfs/onboarding.pdf#page=1)

```text
Northstar onboarding
Synthetic evaluation document | candidate-1
New starters attend orientation on their first Tuesday.
The People Operations team runs orientation.
Equipment requests must be submitted five working days before the start date.
Physical PDF page 1
```

### onboarding.pdf — physical page 2

[Open PDF page](../data/heldout_pdfs/onboarding.pdf#page=2)

```text
Northstar onboarding
Synthetic evaluation document | candidate-1
New starters collect laptops from Room 204.
The assigned team mentor reviews the onboarding checklist at the end of week two.
Physical PDF page 2
```

### travel.pdf — physical page 1

[Open PDF page](../data/heldout_pdfs/travel.pdf#page=1)

```text
Northstar travel
Synthetic evaluation document | candidate-1
Domestic travel requires approval from the department lead before booking.
The domestic hotel reimbursement limit is PKR 12000 per night.
Meal claims are capped at PKR 2500 per travel day.
Physical PDF page 1
```

### travel.pdf — physical page 2

[Open PDF page](../data/heldout_pdfs/travel.pdf#page=2)

```text
Northstar travel
Synthetic evaluation document | candidate-1
Travel receipts must be uploaded within seven calendar days after returning.
A lost travel receipt requires a signed declaration and Finance approval.
Physical PDF page 2
```

### service.pdf — physical page 1

[Open PDF page](../data/heldout_pdfs/service.pdf#page=1)

```text
Northstar service desk
Synthetic evaluation document | candidate-1
The service desk operates Monday to Friday from 08:30 to 17:30.
Urgent incidents must be reported by calling extension 410.
Routine requests must be submitted through the HelpHub portal.
Physical PDF page 1
```

### service.pdf — physical page 2

[Open PDF page](../data/heldout_pdfs/service.pdf#page=2)

```text
Northstar service desk
Synthetic evaluation document | candidate-1
Urgent incidents have a target first response of 30 minutes during service hours.
An unresolved urgent incident is escalated to the duty manager after two hours.
Physical PDF page 2
```

### records.pdf — physical page 1

[Open PDF page](../data/heldout_pdfs/records.pdf#page=1)

```text
Northstar records handling
Synthetic evaluation document | candidate-1
Project records must be stored in the team Vault folder.
Only the project owner may approve external sharing of project records.
Approved external sharing links expire after 72 hours.
Physical PDF page 1
```

### records.pdf — physical page 2

[Open PDF page](../data/heldout_pdfs/records.pdf#page=2)

```text
Northstar records handling
Synthetic evaluation document | candidate-1
Closed-project records are retained for 18 months after project closure.
A suspected data disclosure must be reported to the security desk within one hour of
discovery.
Physical PDF page 2
```

## Prepared private records and next action

- Blank result log: `logs/evaluation/preparation-2026-10-31-b5a876a/run-not-started.json`.
- Hash verification: `logs/evaluation/preparation-2026-10-31-b5a876a/candidate_verification.json`.
- Human decision record: `logs/evaluation/preparation-2026-10-31-b5a876a/human_review_decisions.json`.
- The blank record was created by `scripts.prepare_evaluation.prepare` using its
  existing exclusive-create workflow. All 40 cases remain `Not run`; answers,
  grades, provider/model metadata, tested/deployed revision and approval stay null.
- All these JSON records are under ignored logs/evaluation/. Existing logs were not overwritten.
- A future new blank record can be prepared with:

```powershell
$evaluationRunName = 'run-' + [guid]::NewGuid().ToString('N') + '.json'
.\.venv\Scripts\python.exe -m scripts.prepare_evaluation --output (Join-Path 'logs/evaluation' $evaluationRunName)
```

Immediate next action: the human reviewer completes H01-H40 and D01-D08, records
name/date/decision and explicitly approves or requests revisions. Live testing
remains a separate authorization. The hosted commit is unverified; user-reported
hosted smoke results do not approve ground truth or complete deployment acceptance.

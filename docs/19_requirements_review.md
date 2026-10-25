# Requirements-to-code review — 26 October 2026

Reviewed main commit `a267da737060b77b502d418e81445a766fe6fd0e` and the
accompanying documentation/disclosure changes. Static source review only; this
is not live acceptance, a database audit or a claim that every code path is correct.

| Requirement | Source evidence | Implementation assessment / remaining evidence |
|---|---|---|
| R01 PDF validation and limits | core.py: extract; app.py uploader/preview | Implemented: 1–10 PDFs, 10 MB each, 200 total pages, distinct names; rejects encrypted, unreadable and textless pages. Release acceptance pending. |
| R02 metadata and chunks | core.py: extract, chunk | Filename, one-based physical page, session and chunk IDs included. |
| R03 evidence retrieval | core.py: Assistant.ask, SYSTEM | Session filter and bounded recent user questions; structured model answer. Real provider/schema compatibility and grounding pending. |
| R04 supporting citations | core.py: Assistant.ask; presentation.py: format_answer | Unknown/missing source IDs fail closed and passages are displayed. ID checks cannot establish factual support; semantic citation correctness remains an evaluation requirement. |
| R05 follow-ups | core.py: Assistant.ask | Recent history supplied; last two user questions augment retrieval. Real conversational behavior pending. |
| R06 missing/conflicting information | core.py: SYSTEM, Assistant.ask; presentation.py | Prompt and statuses implemented; model abstention/conflict quality unverified. |
| R07 reset | app.py reset; core.py close | Active index/chat/upload/preview cleared, cleanup failure blocks reuse. Saved copies intentionally retained. |
| R08 privacy/consent | core.py session filtering; auth.py/auth_ui.py; persistence.py; app.py | Account gate, per-session index, user-token storage calls and provider-specific consent implemented. Disclosure moved before upload in this change. Hosted RLS/storage enforcement and two-account isolation still need verification. |
| R09 status/errors | app.py spinners/recovery; presentation.py; persistence_ui.py | Sanitized provider errors, retry/reset, save/delete recovery implemented. Outage/quota cases pending live acceptance. |
| Account extension | auth.py/auth_ui.py | Signup/login/logout reported working by owner; expiry/network/isolation acceptance pending. |
| Saved workspace extension | persistence.py/persistence_ui.py | Save/open/delete/chat binding and interrupted states implemented. No local SQL schema/migrations found; hosted schema reproducibility remains a handoff gap. |
| Provider extension | providers.py; app.py | Explicit OpenAI/Gemini settings, no fallback, model change blocks old index. Working key/model configuration and renewed-consent behavior need acceptance. |
| Export and guides | presentation.py export_chat; guides 12–18 | Text export includes displayed answers/passages. Current guides corrected in this change. |

Paths above are under `src/knowledge_assistant/` unless otherwise stated.

## Closed by this review change

- README, user guide, auth guide and release runbook now reflect implemented
  accounts, saved workspaces and provider selection.
- Data-processing disclosure is shown before the uploader, including app-server
  handling and explicit account storage. Consent is still required for AI calls.
- Deployment verification and code rollback steps distinguish a public login
  page from evidence of the exact running revision.

## Remaining work in order

1. Recover the actual deployed database/storage schema into reviewed, reproducible
   migrations/setup instructions. Do not invent policies from client code or
   overwrite the live schema. Hosted schema is not verified by this source review.
2. Prepare the separate 40-question held-out corpus specified by guide 04 and its
   result-recording format, with reviewed ground truth. Nine development PDF cases
   already exist; they are not the held-out evaluation.
3. Configure a selected provider privately with supported chat/embedding model IDs.
   OpenAI credit purchases remain deferred; Gemini availability is not guaranteed.
4. Confirm exact hosted candidate revision and authenticated feature availability.
5. In the separate testing phase, execute PDF/AI/citation/follow-up/reset/export,
   workspace recovery and two-account isolation cases. Fix and retest failures.
6. Complete measured evaluation, pilot feedback, report, tracker updates, repository
   submission and reviewer acceptance. Do not mark a week complete based on code alone.

No new mandatory core feature was proven absent in this source pass. That does
not close development or acceptance: schema reproducibility and evaluation
preparation remain concrete gaps, and full functional testing may reveal bugs.

## Follow-up preparation checkpoint

The original two deployed migration bodies have now been recovered with their
original versions; see guide 20 for read-only verification and the proposed, unapplied grant restriction. Fresh-project replay remains pending. A separate 40-question
synthetic candidate, four PDFs, evidence hashes and blank-result recorder are
prepared under evaluation/heldout. Human ground-truth approval and live runs
remain pending. These close missing-source/preparation gaps, not acceptance.

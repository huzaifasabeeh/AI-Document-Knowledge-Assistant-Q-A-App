# Hosted demo and final handoff checkpoint

Updated 23 November 2026. This is a progress record, not client acceptance.
Earlier entries from 23 October 2026 are retained below as historical records.

## Hosted evidence

- URL: https://ai-document-knowledge-assistant-q-a-app-f6ozauylzvgbsqda24mnfs.streamlit.app/
- Owner selected main, app.py and Python 3.12 and reported successful deployment.
- On 21 October, browser inspection observed successful wake-up, the document
  sidebar, upload/preview/reset controls, and no startup traceback.
- At that inspection the server reported no API key; AI indexing and chat were
  disabled. Do not infer present credentials or billing from this older check.
- On 23 October, the owner reported the app works without a visible error after
  trying an upload. The exact file type and individual assertions were not
  recorded; this does not establish video support or full PDF acceptance.
- Exact hosted commit has not been independently verified. A main-branch name
  alone is insufficient to identify the running revision.

## Update — 23 November 2026

All development PRs are now merged into main (PR #1, #11, #12). Current main
HEAD is `5192013`. The app auto-deploys from main. Features since last hosted
verification include the full evaluation/deployment-lock tooling (PR #11) and
forgot-password / email code recovery (PR #12). Exact deployed SHA requires
confirmation from Streamlit Cloud build logs after the latest merges.

Previously owner-reported hosted successes (Gemini indexing, answer with
citation, save/restore, autosave recovery) are historical reports from an
earlier main revision. The forgot-password feature requires a Supabase email
template update (Reset Password must contain `{{ .Token }}`).

Local test status on current main: 138 tests + 3 subtests passed in 9.07s.
PR #11 CI verified 318 passed, 7 skipped, 3 subtests on its head commit.

## Completion boundary

| Work | State |
|---|---|
| Streamlit demo hosting/startup | Confirmed |
| Owner general usability check | Reported successful |
| Detailed hosted upload/preview/reset acceptance | Specific assertions not recorded |
| Deployment tools integrated with current main | Prepared in handoff candidate |
| Paid AI answers, citation accuracy and latency | Not run; credits deferred |
| Two-session live isolation and final reviewer acceptance | Pending |
| Final client handoff | In progress |

## Final acceptance batch

Use synthetic fixtures in one planned session. Record the running commit,
model configuration and reviewer in a fresh evaluation worksheet. Run the
nine PDF cases from document 13, then follow-up, clear/export chat, session
isolation, consent, invalid-file recovery and desktop/narrow layout checks.
Compare cited text with each actual claim; valid page IDs alone do not prove
support. Keep failures and explanations in the worksheet. Do not count unrun
or unreviewed cases as successful. Do not use the separate Week 1 text answers
to grade the PDF corpus.

No API calls or credit purchase are authorized by creating the worksheet.
When funded live testing is authorized, execute the batch and record results;
then resolve failures and obtain client/reviewer acceptance. Until then,
Week 2 RAG and Week 3 pilot stay In progress, and Week 4 deployment/handoff is
In progress because the demo is hosted but final acceptance remains open.

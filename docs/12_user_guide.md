# User guide

## Start locally on Windows

First configure Python 3.12, locked dependencies, local Supabase and private
provider settings using the [local setup guide](local_setup_guide.md). Reuse
existing accounts/configuration; never paste keys or passwords into chat.
For the verified local Gemini/Supabase configuration, use the isolated launcher:

```powershell
.\.venv\Scripts\python.exe -m scripts.local_test_app
```

Keep the terminal running and open its printed **Owned local app** URL. It uses
a free loopback port and leaves other apps alone. Ctrl+C stops only that child.
Ordinary launches with `python -m streamlit run app.py` read environment settings
before Streamlit Secrets; use the controlled launcher for local verification.
Starting the app alone does not submit an AI request.

## Sign in

Create an account, confirm your email if requested, then log in. Server account
settings must be configured even for preview. Expired sessions require login
again. Log out clears the active session; saved workspaces remain in your account.

## Preview without AI API calls

1. Select text PDFs in the sidebar: up to 10 files, 10 MB each, 200 pages total.
2. Select **Preview pages (no API)**. Neither an API key nor consent is needed.
3. Check filenames, physical PDF page numbers and extracted text. The preview
   shows at most 1,500 characters per page, not the entire document.
4. Changing selected files clears the previous preview. Preview again to see
   the new selection. Scanned/blank pages and encrypted PDFs are unsupported.

## Ask questions when provider access is available

The owner configures OpenAI or Gemini using the [provider setup](18_ai_providers.md).
The app accepts environment variables or Streamlit Secrets; a `.env` file alone
is not loaded. A key does not prove model access or available quota. Charges and
availability depend on the selected provider plan. Never share keys in chat.

1. Upload authorized PDFs and enable the processing-consent checkbox.
2. Select **Index documents**. Extracted text is sent for embeddings and this
   uses the selected provider’s quota and may incur charges. Wait for the indexed status before asking a question.
3. Ask a specific question. Questions, recent conversation and retrieved text
   are sent to the model. Expand **View supporting passages** and compare the
   answer with the cited physical PDF pages. Citations do not guarantee accuracy.
4. **Clear chat only** removes conversation history but preserves the document
   index. The next question has no previous-chat context.
5. **Download chat and sources** saves a plain-text copy of responses and cited
   passages without an additional AI call. Handle that copy like the PDFs.
6. **Reset documents and chat** deletes the active index and clears app history,
   uploads and preview. It does not delete saved workspaces, downloaded copies or provider records.

Disable consent to pause new questions. To change indexed files, reset first.
If cleanup fails, retry reset or restart the server. Closing a browser tab is
not a guaranteed cleanup mechanism. Unsaved chat is temporary. Explicitly saved workspaces retain PDFs and chat.

## Troubleshooting

- Invalid PDF: remove it and upload a valid text PDF, then preview again.
- Missing API key: preview still works; configure the server key for AI use.
- Unavailable credits or provider access: use preview; record the blocked AI
  operation. Do not purchase access or change models as a troubleshooting step.
- Authentication error: distinguish account login from provider access; check
  the appropriate server settings privately, without printing keys/passwords.
- Rate limit: stop new questions and inspect any saved operation/model/status,
  quota metric and explicit retry guidance. Missing reset/window information is
  unknown; repeated probes or an elapsed wait do not establish restored capacity.
  See the [quota evidence guide](gemini_quota_check.md).
- Slow response: indexing and response latency are separate. The local every-
  response deadline failed; a later fast answer does not erase a slow one. See
  [investigation findings](latency_investigation_findings.md); no fix is proven.
- Restore shows chat but questions are disabled: re-index the restored PDFs with
  provider consent. Restored answers/sources do not require new generation to view.
- Chat-save warning: keep the session open, export a private backup and use
  **Save chat now** after resolving the connection; do not assume autosave succeeded.
- Wrong service or missing local configuration: use the setup helper and isolated
  launcher. A `.env` file is not loaded; remote Supabase requires HTTPS.
- Unsupported answer: rephrase or supply a relevant document; do not infer an
  answer from a missing-information response.

Latest local quality thresholds were met; mandatory every-response <=10.000s
browser acceptance failed. Hosted acceptance and final client sign-off are pending.

## Save, reopen and delete workspaces

1. Enter a name under **Saved workspaces** and select **Save as new workspace**.
   This stores the selected PDFs and current chat in your account. Saving requires
   no AI call. The session is bound to those PDFs; reset to change the document set.
2. Saved chat updates after successful answers and **Clear chat only**. If a save
   warning appears, use **Save chat now** before leaving. Export is a local backup.
3. To reopen, reset the current session, refresh the workspace list, select a ready
   item and choose **Open saved workspace**. Re-index before asking new questions.
4. To delete, close other tabs using that workspace, select it, tick its permanent
   deletion confirmation and choose **Delete saved workspace**. Saved files/chat
   are removed; open sessions and downloads remain until separately cleared.
5. After an interrupted save/delete, refresh the list before retrying. Incomplete
   entries cannot open and can be deleted once no other tab is saving them.

See [storage limits and recovery](17_saved_workspaces.md). Two tabs updating one
saved chat use last-write-wins. Local save/restore, subsequent-turn autosave and
restored-PDF follow-ups were verified. Repeat required release checks against the
exact authorized hosted revision before claiming hosted acceptance.

## Known limitations

Only text PDFs are supported; there is no OCR. The short synthetic benchmark does
not establish large-document, concurrent-load or real-client performance. Re-index
after restore/restart before asking new questions; vectors are session-scoped.
Unsaved chat is temporary and downloaded exports remain on the user's computer.
Model access/quota and response time can vary. Local Edge Runtime, Logflare and
Vector were excluded, not repaired or accepted. See the
[release blockers](deployment_acceptance_checklist.md) for remaining acceptance.

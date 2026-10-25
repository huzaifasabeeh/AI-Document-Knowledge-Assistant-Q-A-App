# User guide

## Start locally on Windows

From the repository folder, with the existing virtual environment installed:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Keep the terminal running and open the Local URL printed there. If Streamlit
asks for an email during first launch, leave it empty and press Enter.

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
- Unavailable credits: use preview until funded access is provided.
- Authentication error: verify the server key privately, then retry.
- Rate limit: wait and check account limits before retrying.
- Unsupported answer: rephrase or supply a relevant document; do not infer an
  answer from a missing-information response.

Live answer quality and browser end-to-end acceptance remain unverified.

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
saved chat use last-write-wins. Full saved-workspace acceptance is still pending.

# User guide

## Start locally on Windows

From the repository folder, with the existing virtual environment installed:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Keep the terminal running and open the Local URL printed there. If Streamlit
asks for an email during first launch, leave it empty and press Enter.

## Preview without API charges

1. Select text PDFs in the sidebar: up to 10 files, 10 MB each, 200 pages total.
2. Select **Preview pages (no API)**. Neither an API key nor consent is needed.
3. Check filenames, physical PDF page numbers and extracted text. The preview
   shows at most 1,500 characters per page, not the entire document.
4. Changing selected files clears the previous preview. Preview again to see
   the new selection. Scanned/blank pages and encrypted PDFs are unsupported.

## Ask questions when API access is funded

The server needs OPENAI_API_KEY in its environment. A .env file alone is not
loaded automatically by this app. Configure the key privately; never commit it.
The key's presence does not prove valid access or available credit.

1. Upload authorized PDFs and enable the processing-consent checkbox.
2. Select **Index documents**. Extracted text is sent for embeddings and this
   uses paid API credits. Wait for the indexed status before asking a question.
3. Ask a specific question. Questions, recent conversation and retrieved text
   are sent to the model. Expand **View supporting passages** and compare the
   answer with the cited physical PDF pages. Citations do not guarantee accuracy.
4. **Clear chat only** removes conversation history but preserves the document
   index. The next question has no previous-chat context.
5. **Download chat and sources** saves a plain-text copy of responses and cited
   passages without an additional AI call. Handle that copy like the PDFs.
6. **Reset documents and chat** deletes the active index and clears app history,
   uploads and preview. It does not delete downloaded copies or provider records.

Disable consent to pause new questions. To change indexed files, reset first.
If cleanup fails, retry reset or restart the server. Closing a browser tab is
not a guaranteed cleanup mechanism. This prototype has no durable chat history.

## Troubleshooting

- Invalid PDF: remove it and upload a valid text PDF, then preview again.
- Missing API key: preview still works; configure the server key for AI use.
- Unavailable credits: use preview until funded access is provided.
- Authentication error: verify the server key privately, then retry.
- Rate limit: wait and check account limits before retrying.
- Unsupported answer: rephrase or supply a relevant document; do not infer an
  answer from a missing-information response.

Live answer quality and browser end-to-end acceptance remain unverified.

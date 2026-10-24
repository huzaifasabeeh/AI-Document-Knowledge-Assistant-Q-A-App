# Saved workspaces

Development implementation: private PDFs in Supabase Storage and named workspace
records in PostgreSQL. Both use the signed-in user's token with ownership RLS;
no service-role key is needed. The existing Supabase connection settings apply.

Use **Save as new workspace** to save selected PDFs and the current chat.
After signing in again, choose **Refresh saved workspaces**, select a workspace,
and **Open saved workspace**. Chat and source excerpts return immediately.
Re-index the restored PDFs with processing consent to ask new questions.
After saving/opening a workspace, successful answers and Clear chat update its
saved chat. If saving fails, a warning remains and **Save chat now** retries.

Reset clears the current session, not saved copies. Opening another workspace
requires resetting an active index/chat first. Saving is explicit; unsaved work
is still temporary. Account logout clears local state, not saved workspaces.

Limits: up to 10 PDFs, 10 MB per file and 200 pages per saved workspace;
the list shows the 100 most recent workspaces. Indexes remain ephemeral.
Simultaneous tabs editing the same saved chat use last-write-wins.
Save records every intended file path before uploading. Interrupted saves remain
listed as saving and can be removed after ensuring no other tab is saving them.
Deletion requires an explicit confirmation checkbox. It marks the record deleting,
removes PDFs through the Storage API, then removes the record and saved messages.
If deletion fails, refresh and retry the deleting item. Incomplete/deleting items
cannot be reopened. A timeout is not treated as proof of failure: refresh first
before retrying or deleting. Existing open sessions/downloaded copies are not
removed by deleting a saved copy. Close other tabs using the workspace first.
No automatic retention schedule is configured.

The hosted schema was applied as `saved_user_workspaces` followed by
`workspace_cleanup_states`. Full functional,
cross-account, reconnect and failure testing is deferred to the project's
separate testing phase at the owner's request. Implementation is not acceptance.

Supabase advisor reported existing leaked-password protection disabled. This is
an Auth configuration warning, separate from the new workspace ownership rules.
See https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection

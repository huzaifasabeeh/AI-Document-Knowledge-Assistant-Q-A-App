# Database setup and recovered history

## Provenance and scope

On 26 October 2026 the two existing migration bodies were recovered read-only
from the deployed project's `supabase_migrations.schema_migrations`. Their
original version identifiers and SQL are preserved in `supabase/migrations/`:

1. `20261024153137_saved_user_workspaces.sql`
2. `20261024153958_workspace_cleanup_states.sql`

The third migration, `20261025224959_restrict_workspace_privileges.sql`, was
applied after explicit owner approval on 26 October 2026 (Pakistan time). It
revokes only authenticated TRUNCATE, REFERENCES and TRIGGER privileges. The
CLI-generated draft was renamed to the exact version recorded by the hosted
migration runner, avoiding duplicate replay under a different timestamp.

These are recovered historical migrations, not newly generated schema changes.
No hosted data or credentials were exported and neither migration was rerun on
production. They create the application table, ownership policies, private PDF
bucket and save/deletion states. They do not back up users or stored PDF bytes.

## Fresh Supabase project

Use a fresh disposable Supabase project for rehearsal before deployment. Its
managed `auth` and `storage` schemas must already exist. In its SQL editor, run
the first recovered file, then the second, then the privilege restriction,
each inside a transaction. This is for a disposable rehearsal only. Stop on
errors rather than suppressing existing-object failures. These scripts are not
idempotent and must not be replayed over the existing hosted project.

Run `supabase/verify_workspace_schema.sql` read-only afterwards. Check every
result against the expected shape below. Configure email/password confirmation,
Site URL, email delivery and application connection secrets separately using
guide 16. The SQL does not configure Auth settings, hosting or API providers.

CLI users should first inspect their installed `supabase --help`, `migration
--help` and `db --help`. Reconcile remote migration history before any push; do
not repair history or reset a linked project merely to silence a mismatch.
The recovered versions already exist in the production migration history.

## Expected shape and observed limits

- Eight workspace columns: id, user_id, title, documents, messages, created_at,
  updated_at, status. UUID primary key; owner foreign key references auth.users;
  title length 1–120; document/message arrays; saving/ready/deleting states.
- Row-level security enabled. Authenticated SELECT/INSERT/UPDATE/DELETE policies
  compare auth.uid() to user_id; UPDATE includes both USING and WITH CHECK.
- Private `user-documents` bucket, 10485760-byte file limit, application/pdf MIME.
  Object SELECT/INSERT/DELETE policies require the user's UUID as first path
  segment. The app uploads new UUID paths; it does not need object UPDATE/upsert.
- Anonymous workspace table grants were absent in the observed grant listing.
- **Grant hardening applied and verified:** authenticated retains SELECT,
  INSERT, UPDATE and DELETE; has_table_privilege returned false for TRUNCATE,
  REFERENCES and TRIGGER after the migration. No saved rows, PDFs, ownership
  policies or Auth configuration were changed. Full API isolation testing
  remains separate from this permission-level verification.
- No user-metadata-based policy or application SECURITY DEFINER function appears
  in the recovered SQL. This is a scoped review, not a whole-project audit.
- The security advisor reports leaked-password protection disabled. See
  [Supabase remediation](https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection).
  Account plan/configuration review is still needed before enabling it.

Catalog checks confirmed table RLS, columns, constraints, ownership policy
expressions and bucket configuration on the existing deployment. They do not
prove cross-account API isolation. Fresh-project replay, storage recovery and
API isolation remain in the separate acceptance phase. No fresh environment
was provisioned during this work.

## Retention and rollback

Saved-workspace deletion goes through the Storage API before deleting its row.
Deleting an Auth user cascades workspace rows but does not itself guarantee
removal of stored PDF bytes. Plan storage cleanup before account deletion.
Do not drop tables/buckets to roll back app code. Preserve backups, inspect
compatibility and use a reviewed forward migration for schema corrections.

References checked during recovery:
- https://supabase.com/docs/guides/local-development/database-migrations
- https://supabase.com/changelog/cbc-tls-ciphers-deprecated

The announced TLS cipher change concerns old HTTP clients; this recovery adds
no HTTP client or new SDK. Verify the deployed runtime during release checks.

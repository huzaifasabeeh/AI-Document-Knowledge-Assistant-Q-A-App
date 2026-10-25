-- Read-only metadata checks. Do not query account rows, saved messages or files.
select relrowsecurity from pg_class where oid = 'public.saved_workspaces'::regclass;
select column_name, data_type, is_nullable, column_default
from information_schema.columns
where table_schema = 'public' and table_name = 'saved_workspaces'
order by ordinal_position;
select conname, pg_get_constraintdef(oid) as definition
from pg_constraint where conrelid = 'public.saved_workspaces'::regclass;
select schemaname, tablename, policyname, roles, cmd, qual, with_check
from pg_policies
where (schemaname = 'public' and tablename = 'saved_workspaces')
   or (schemaname = 'storage' and tablename = 'objects');
select grantee, privilege_type from information_schema.role_table_grants
where table_schema = 'public' and table_name = 'saved_workspaces';
select id, public, file_size_limit, allowed_mime_types
from storage.buckets where id = 'user-documents';

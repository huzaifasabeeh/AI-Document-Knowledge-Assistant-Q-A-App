create table public.saved_workspaces (
 id uuid primary key, user_id uuid not null references auth.users(id) on delete cascade,
 title text not null check(length(title) between 1 and 120),
 documents jsonb not null default '[]' check(jsonb_typeof(documents)='array'),
 messages jsonb not null default '[]' check(jsonb_typeof(messages)='array'),
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now()
);
create index saved_workspaces_user_id_idx on public.saved_workspaces(user_id);
alter table public.saved_workspaces enable row level security;
revoke all on public.saved_workspaces from anon;
grant select,insert,update on public.saved_workspaces to authenticated;
create policy workspace_read on public.saved_workspaces for select to authenticated using ((select auth.uid())=user_id);
create policy workspace_create on public.saved_workspaces for insert to authenticated with check ((select auth.uid())=user_id);
create policy workspace_update on public.saved_workspaces for update to authenticated using ((select auth.uid())=user_id) with check ((select auth.uid())=user_id);
insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types) values ('user-documents','user-documents',false,10485760,array['application/pdf']);
create policy document_read on storage.objects for select to authenticated using (bucket_id='user-documents' and (storage.foldername(name))[1]=(select auth.uid())::text);
create policy document_create on storage.objects for insert to authenticated with check (bucket_id='user-documents' and (storage.foldername(name))[1]=(select auth.uid())::text);


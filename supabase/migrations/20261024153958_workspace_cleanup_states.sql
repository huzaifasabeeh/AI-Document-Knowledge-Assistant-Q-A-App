alter table public.saved_workspaces add column status text not null default 'ready' check (status in ('saving','ready','deleting'));
grant delete on public.saved_workspaces to authenticated;
create policy workspace_delete on public.saved_workspaces for delete to authenticated using ((select auth.uid())=user_id);
create policy document_delete on storage.objects for delete to authenticated using (bucket_id='user-documents' and (storage.foldername(name))[1]=(select auth.uid())::text);


"""Explicit save/open controls; cloud failures never erase current work."""
import streamlit as st
from .auth_ui import setting
from .core import InputError
from .persistence import WorkspaceStore, PersistenceError


def workspace_store():
    return WorkspaceStore(setting('SUPABASE_URL'), setting('SUPABASE_PUBLISHABLE_KEY'),
                          st.session_state.auth_token, st.session_state.auth_user_id)


def saved_workspace_controls(uploads, active, blocked):
    with st.expander('Saved workspaces'):
        notice = st.session_state.pop('workspace_notice', None)
        if notice:
            st.success(notice)
        st.caption('Save PDFs and chat privately to your account. Opening a saved workspace restores its chat; index its PDFs again to ask new questions.')
        title = st.text_input('Workspace name', max_chars=120)
        if st.button('Save as new workspace', disabled=not uploads or blocked):
            try:
                st.session_state.saved_workspace_id = workspace_store().save(title, uploads, st.session_state.messages)
                # Bind the current session to the exact PDFs just persisted. Clear
                # the uploader so later reruns cannot attach different files to
                # this workspace's saved chat.
                st.session_state.restored_uploads = list(uploads)
                st.session_state.upload_key += 1
                st.session_state.pop('saved_workspace_list', None)
                st.session_state.pop('chat_save_error', None)
                st.session_state.workspace_notice = 'Workspace saved to your account.'
                st.rerun()
            except (PersistenceError, InputError) as exc:
                st.error(str(exc))
        if st.button('Refresh saved workspaces'):
            try:
                st.session_state.saved_workspace_list = workspace_store().list()
            except PersistenceError as exc:
                st.error(str(exc))
        rows = st.session_state.get('saved_workspace_list', [])
        if rows:
            titles = {r['id']: r['title'] + ' · ' + r['created_at'][:19] + ' · ' + r['status'] for r in rows}
            chosen = st.selectbox('Choose saved workspace', list(titles), format_func=titles.get)
            selected = next(r for r in rows if r['id'] == chosen)
            st.caption('Reset the current session before opening a different workspace. Save any unsaved work first.')
            if st.button('Open saved workspace', disabled=active or blocked or bool(uploads) or bool(st.session_state.messages) or selected['status'] != 'ready'):
                try:
                    restored, messages = workspace_store().load(chosen)
                    st.session_state.restored_uploads = restored
                    st.session_state.messages = messages
                    st.session_state.saved_workspace_id = chosen
                    st.session_state.preview = []
                    st.session_state.preview_signature = None
                    st.session_state.upload_key += 1
                    st.rerun()
                except (PersistenceError, InputError) as exc:
                    st.error(str(exc))
            st.caption('Delete permanently removes this saved workspace, its PDFs and chat. Close other tabs using it first. Incomplete saves can also be removed here.')
            confirm = st.checkbox('Permanently delete: ' + selected['title'], key='delete-confirm-' + chosen)
            if st.button('Delete saved workspace', disabled=not confirm or blocked):
                try:
                    workspace_store().delete(chosen)
                    if st.session_state.get('saved_workspace_id') == chosen:
                        st.session_state.pop('saved_workspace_id', None)
                        st.session_state.pop('chat_save_error', None)
                    st.session_state.pop('saved_workspace_list', None)
                    st.success('Saved copy deleted. Any open session or downloaded copy remains until cleared.')
                except PersistenceError:
                    st.error('Deletion could not be confirmed. Refresh the list and retry; a deleting item cannot be reopened.')
        if st.session_state.get('saved_workspace_id'):
            st.caption('Chat changes are saved to the open workspace. Reset only clears this session; saved copies remain.')
            if st.button('Save chat now', disabled=blocked):
                persist_chat()


def persist_chat():
    if st.session_state.get('saved_workspace_id'):
        try:
            workspace_store().save_chat(st.session_state.saved_workspace_id, st.session_state.messages)
            st.session_state.pop('chat_save_error', None)
        except PersistenceError as exc:
            st.session_state.chat_save_error = str(exc)

"""Streamlit document workspace. Run with: streamlit run app.py."""
import os
from hashlib import sha256
import streamlit as st
from src.knowledge_assistant.core import InputError, Upload, extract, openai_assistant
from src.knowledge_assistant.presentation import format_answer, provider_error, export_chat

st.set_page_config(page_title='Document Knowledge Assistant', page_icon='📚', layout='wide')
from src.knowledge_assistant.auth_ui import require_login
require_login()
for key, default in [('messages', []), ('documents', []), ('passage_count', 0),
                     ('preview', []), ('preview_signature', None), ('upload_key', 0), ('cleanup_blocked', False)]:
    if key not in st.session_state:
        st.session_state[key] = default

with st.sidebar:
    st.header('Your documents')
    st.caption('Text PDFs · up to 10 files · 10 MB each · 200 pages total')
    if st.button('Reset documents and chat', key='reset', width='stretch'):
        engine = st.session_state.get('assistant') or st.session_state.get('failed_engine')
        try:
            if engine is not None:
                engine.close()
        except Exception:
            st.session_state.cleanup_blocked = True
            st.error('Cleanup failed. Retry reset or restart the server before continuing.')
            st.stop()
        for key in ('assistant', 'failed_engine'):
            st.session_state.pop(key, None)
        st.session_state.messages = []
        st.session_state.documents = []
        st.session_state.preview = []
        st.session_state.preview_signature = None
        st.session_state.passage_count = 0
        st.session_state.cleanup_blocked = False
        st.session_state.upload_key += 1
        st.rerun()

    active = 'assistant' in st.session_state
    blocked = st.session_state.cleanup_blocked
    files = st.file_uploader('Upload PDFs', type=['pdf'], accept_multiple_files=True,
        max_upload_size=10, disabled=active or blocked,
        key=f'uploads-{st.session_state.upload_key}')
    selection_signature = tuple((f.name, sha256(f.getvalue()).hexdigest()) for f in (files or []))
    if selection_signature != st.session_state.preview_signature:
        st.session_state.preview = []
    if active:
        st.caption('Reset before changing the indexed document set.')
    if files and not active:
        st.caption(f'{len(files)} file(s) selected — not yet indexed')
        for file in files:
            st.text(file.name)
    if st.button('Preview pages (no API)', key='preview_pages', width='stretch',
                 disabled=not files or active or blocked):
        st.session_state.preview = []
        try:
            pages = extract([Upload(f.name, f.getvalue()) for f in files], 'preview')
            st.session_state.preview_signature = selection_signature
            st.session_state.preview = [
                {'filename': p.metadata['filename'], 'page': p.metadata['page'],
                 'text': p.page_content[:1500]} for p in pages]
        except InputError as exc:
            st.error(str(exc))
    st.caption('Preview extracts text locally. It does not index documents or generate AI answers.')
    with st.expander('How your data is used'):
        st.write('Indexing sends extracted text to OpenAI for embeddings. Questions and retrieved passages are sent for answers. Only upload documents you are authorized to process.')
        st.write('Reset clears this app’s active index and chat. Provider retention is separate. Closing the browser does not guarantee immediate cleanup; restart the server to clear ephemeral state.')
    consent = st.checkbox('I agree to send these documents and questions to OpenAI.', key='consent')
    has_key = bool(os.environ.get('OPENAI_API_KEY'))
    if not has_key:
        st.info('AI indexing needs an API key in the server environment. Local preview is available.')
    st.caption('AI indexing and answers use paid API credits. A configured key does not confirm available credits.')
    if st.button('Index documents', key='index', type='primary', width='stretch',
                 disabled=not consent or not files or active or blocked or not has_key):
        engine = None
        try:
            with st.spinner('Extracting and indexing…'):
                engine = openai_assistant()
                count = engine.ingest([Upload(f.name, f.getvalue()) for f in files])
            st.session_state.assistant = engine
            st.session_state.documents = [f.name for f in files]
            st.session_state.passage_count = count
            st.session_state.preview_signature = selection_signature
            st.session_state.preview = []
            st.rerun()
        except Exception as exc:
            if engine is not None:
                try:
                    engine.close()
                except Exception:
                    st.session_state.failed_engine = engine
                    st.session_state.cleanup_blocked = True
                    st.error('Index cleanup failed. Reset or restart the server before retrying.')
            st.error(str(exc) if isinstance(exc, InputError) else provider_error(exc))
    if st.session_state.documents:
        st.subheader('Indexed files')
        for name in st.session_state.documents:
            st.text(name)

st.title('Document Knowledge Assistant')
st.caption('Ask your documents. Inspect the supporting pages.')
active = 'assistant' in st.session_state
blocked = st.session_state.cleanup_blocked
cols = st.columns(3)
cols[0].metric('Indexed documents', len(st.session_state.documents))
cols[1].metric('Searchable passages', st.session_state.passage_count)
cols[2].metric('Responses received', len(st.session_state.messages) // 2)
if blocked:
    st.error('Session paused: reset or restart the server to finish cleanup.')
elif active and consent:
    st.success('Documents indexed. You can ask questions below.')
elif active:
    st.warning('Chat paused. Enable processing consent in the sidebar to continue.')
else:
    st.info('Start in the sidebar: upload PDFs, preview their pages locally, then index when API access is available.')

if st.session_state.preview:
    with st.expander('Local page preview — not indexed', expanded=True):
        st.caption('Text is limited to 1,500 characters per page. Changing selected files clears this preview; preview the new selection again.')
        for page in st.session_state.preview:
            st.caption(f'{page["filename"]} · PDF page {page["page"]}')
            st.text(page['text'])

if st.session_state.messages:
    clear_col, download_col = st.columns(2)
    if clear_col.button('Clear chat only', key='clear_chat', width='stretch', disabled=blocked):
        st.session_state.messages = []
        st.rerun()
    download_col.download_button('Download chat and sources',
        data=export_chat(st.session_state.messages), file_name='document-chat.txt',
        mime='text/plain', on_click='ignore', width='stretch')
    st.caption('Clear chat keeps documents indexed. Downloaded copies remain on your device after reset.')

if not st.session_state.messages:
    st.subheader('Find answers with page references')
    st.write('Once indexed, ask a specific question such as “Who approves leave requests?” or “What is the expense claim deadline?”')
    st.caption('References use physical PDF page numbers starting at 1. Check the cited text before relying on an answer.')
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.text(message['content'])
        if message.get('sources'):
            with st.expander('View supporting passages'):
                for source in message['sources']:
                    st.caption(f'{source["filename"]} · PDF page {source["page"]}')
                    st.text(source['text'])
question = st.chat_input('Ask about your indexed PDFs', disabled=not active or not consent or blocked)
if question:
    try:
        history = [{'role': m['role'], 'content': m['content']} for m in st.session_state.messages]
        with st.spinner('Finding supporting passages…'):
            answer, sources = st.session_state.assistant.ask(question, history)
        content, evidence = format_answer(answer, sources)
        st.session_state.messages.extend([
            {'role': 'user', 'content': question},
            {'role': 'assistant', 'content': content, 'sources': evidence}])
        st.rerun()
    except InputError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(provider_error(exc))
        st.caption('Your documents remain indexed. Retry the question after resolving the issue.')

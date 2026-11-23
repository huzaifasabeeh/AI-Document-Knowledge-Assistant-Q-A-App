"""Streamlit document workspace. Run with: streamlit run app.py."""
from hashlib import sha256
import streamlit as st
from src.knowledge_assistant.core import InputError, Upload, extract
from src.knowledge_assistant.presentation import format_answer, provider_error, export_chat
from src.knowledge_assistant.persistence_ui import saved_workspace_controls, persist_chat
from src.knowledge_assistant.stage_timing import response_timing, span

st.set_page_config(page_title='DocMind — Document Knowledge Assistant', page_icon='📚', layout='wide')


def get_docmind_css(is_dark):
    bg = '#0f172a' if is_dark else '#f8fafc'
    sidebar_bg = '#1e293b' if is_dark else '#ffffff'
    sidebar_border = '#334155' if is_dark else '#e2e8f0'
    card_bg = '#1e293b' if is_dark else '#ffffff'
    card_border = '#334155' if is_dark else '#e2e8f0'
    text_primary = '#f8fafc' if is_dark else '#1e293b'
    text_secondary = '#94a3b8' if is_dark else '#64748b'
    user_bubble_bg = '#4f46e5'
    user_bubble_text = '#ffffff'
    assistant_card_bg = '#1e293b' if is_dark else '#ffffff'
    assistant_border = '#334155' if is_dark else '#e2e8f0'
    citation_bg = '#312e81' if is_dark else '#eef2ff'
    citation_border = '#4338ca' if is_dark else '#c7d2fe'
    citation_text = '#c7d2fe' if is_dark else '#4338ca'
    input_bg = '#1e293b' if is_dark else '#ffffff'
    input_border = '#334155' if is_dark else '#cbd5e1'
    shadow = '0 4px 14px rgba(0, 0, 0, 0.25)' if is_dark else '0 2px 8px rgba(0, 0, 0, 0.05)'

    return f"""
<style>
/* App View Container */
[data-testid="stAppViewContainer"] {{
    background-color: {bg} !important;
    color: {text_primary} !important;
}}

[data-testid="stSidebar"] {{
    background-color: {sidebar_bg} !important;
    border-right: 1px solid {sidebar_border} !important;
}}

[data-testid="stHeader"] {{
    background-color: rgba({'15, 23, 42' if is_dark else '248, 250, 252'}, 0.85) !important;
    backdrop-filter: blur(8px);
}}

/* User chat bubble: DocMind style right-aligned indigo bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]),
[data-testid="stChatMessage"]:has([aria-label="🧑‍💼"]) {{
    background-color: {user_bubble_bg} !important;
    border: none !important;
    border-radius: 18px 18px 4px 18px !important;
    color: {user_bubble_text} !important;
    margin-left: auto !important;
    max-width: 82% !important;
    padding: 0.9rem 1.25rem !important;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2) !important;
}}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stText"],
[data-testid="stChatMessage"]:has([aria-label="🧑‍💼"]) [data-testid="stText"] {{
    color: {user_bubble_text} !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    white-space: pre-wrap !important;
    font-size: 0.96rem !important;
    line-height: 1.55 !important;
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}}

/* Assistant chat message: DocMind style left-aligned clean card */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]),
[data-testid="stChatMessage"]:has([aria-label="🤖"]) {{
    background-color: {assistant_card_bg} !important;
    border: 1px solid {assistant_border} !important;
    border-radius: 18px 18px 18px 4px !important;
    max-width: 90% !important;
    padding: 1.1rem 1.35rem !important;
    box-shadow: {shadow} !important;
}}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stText"],
[data-testid="stChatMessage"]:has([aria-label="🤖"]) [data-testid="stText"] {{
    color: {text_primary} !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    white-space: pre-wrap !important;
    font-size: 0.96rem !important;
    line-height: 1.65 !important;
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}}

/* Metric cards: DocMind style */
[data-testid="stMetric"] {{
    background-color: {card_bg} !important;
    border: 1px solid {card_border} !important;
    border-radius: 12px !important;
    padding: 0.75rem 1rem !important;
    box-shadow: {shadow} !important;
}}
[data-testid="stMetricLabel"] {{
    color: {text_secondary} !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
}}
[data-testid="stMetricValue"] {{
    color: {text_primary} !important;
    font-size: 1.35rem !important;
    font-weight: 700 !important;
}}

/* New conversation / Reset button in sidebar */
[data-testid="stSidebar"] div.stButton > button[key="reset"],
[data-testid="stSidebar"] div.stButton > button:first-child {{
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
}}

div.stButton > button {{
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}}
div.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
    border: none !important;
    color: #ffffff !important;
    box-shadow: 0 2px 8px rgba(79, 70, 229, 0.3) !important;
}}

/* Floating Chat input bar */
[data-testid="stChatInput"] {{
    border-radius: 16px !important;
    border: 1px solid {input_border} !important;
    background-color: {input_bg} !important;
    box-shadow: {shadow} !important;
}}
[data-testid="stChatInput"] textarea {{
    color: {text_primary} !important;
}}

/* Expanders */
div[data-testid="stExpander"] {{
    background-color: {card_bg} !important;
    border: 1px solid {card_border} !important;
    border-radius: 10px !important;
}}

/* DocMind citation pills */
.docmind-pills-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 0.65rem 0 0.85rem 0;
}}
.docmind-pill {{
    display: inline-flex;
    align-items: center;
    background-color: {citation_bg};
    color: {citation_text};
    border: 1px solid {citation_border};
    border-radius: 8px;
    padding: 0.3rem 0.65rem;
    font-size: 0.8rem;
    font-weight: 500;
}}

/* DocMind hero card */
.docmind-hero {{
    background: linear-gradient(135deg, {'#1e293b 0%, #0f172a 100%' if is_dark else '#ffffff 0%, #f1f5f9 100%'});
    border: 1px solid {card_border};
    border-radius: 16px;
    padding: 2.25rem 2rem;
    margin-bottom: 1.5rem;
    text-align: center;
    box-shadow: {shadow};
}}
.docmind-hero-badge {{
    display: inline-block;
    background-color: {citation_bg};
    color: {citation_text};
    padding: 0.35rem 0.85rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 0.85rem;
    border: 1px solid {citation_border};
}}
.docmind-hero-title {{
    font-size: 1.9rem;
    font-weight: 700;
    color: {text_primary};
    margin-bottom: 0.4rem;
}}
.docmind-hero-sub {{
    font-size: 0.95rem;
    color: {text_secondary};
    max-width: 580px;
    margin: 0 auto 1.35rem auto;
}}
.docmind-chips {{
    display: flex;
    justify-content: center;
    gap: 0.65rem;
    flex-wrap: wrap;
}}
.docmind-chip {{
    background-color: {card_bg};
    border: 1px solid {card_border};
    border-radius: 20px;
    padding: 0.5rem 0.9rem;
    color: {text_primary};
    font-size: 0.82rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}}
</style>
"""


is_dark = st.session_state.get('theme_choice') == '🌙 Dark'
st.html(get_docmind_css(is_dark))

from src.knowledge_assistant.auth_ui import require_login, setting
from src.knowledge_assistant.providers import provider_config, configured_assistant
require_login()
try:
    ai_config = provider_config(setting)
except ValueError as exc:
    st.error(str(exc))
    st.stop()
provider_changed = (st.session_state.get('assistant') is not None and
    getattr(st.session_state.assistant, 'provider_identity', None) != ai_config.identity)
if provider_changed:
    st.warning('AI configuration changed. Reset and re-index your documents before continuing.')
for key, default in [('messages', []), ('documents', []), ('passage_count', 0),
                     ('preview', []), ('preview_signature', None), ('upload_key', 0), ('cleanup_blocked', False)]:
    if key not in st.session_state:
        st.session_state[key] = default

with st.sidebar:
    theme_col1, theme_col2 = st.columns([3, 2])
    with theme_col1:
        st.markdown('### ✦ **DocMind**')
    with theme_col2:
        st.segmented_control('Theme', options=['☀️ Light', '🌙 Dark'],
                             default=st.session_state.get('theme_choice', '☀️ Light'),
                             key='theme_choice', label_visibility='collapsed')
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
        for key in ('restored_uploads', 'saved_workspace_id', 'chat_save_error'):
            st.session_state.pop(key, None)
        st.rerun()

    active = 'assistant' in st.session_state
    blocked = st.session_state.cleanup_blocked or provider_changed
    st.caption('Uploads are processed on the app server. Saving a workspace stores PDFs and chat in your account; AI indexing requires the consent below.')
    with st.expander('How your data is used'):
        st.write(f'Indexing sends extracted text to {ai_config.label} for embeddings. Questions and retrieved passages are sent there for answers. Only upload documents you are authorized to process.')
        st.write('Reset clears this app’s active index and chat. Provider retention is separate. Closing the browser does not guarantee immediate cleanup; restart the server to clear ephemeral state.')
    files = st.file_uploader('Upload PDFs', type=['pdf'], accept_multiple_files=True,
        max_upload_size=10, disabled=active or blocked or bool(st.session_state.get('saved_workspace_id')),
        key=f'uploads-{st.session_state.upload_key}')
    uploads = [Upload(f.name, f.getvalue()) for f in (files or [])]
    if not uploads:
        uploads = st.session_state.get('restored_uploads', [])
    elif st.session_state.get('restored_uploads'):
        st.warning('Reset this session before selecting new PDFs for a saved chat.')
        uploads = st.session_state.restored_uploads
    saved_workspace_controls(uploads, active, blocked)
    selection_signature = tuple((f.name, sha256(f.data).hexdigest()) for f in uploads)
    if selection_signature != st.session_state.preview_signature:
        st.session_state.preview = []
    if active or st.session_state.get('saved_workspace_id'):
        st.caption('Reset before changing this workspace’s document set. Saved copies remain in your account.')
    if uploads and not active:
        st.caption(f'{len(uploads)} file(s) selected — not yet indexed')
        for file in uploads:
            st.text(file.name)
    if st.button('Preview pages (no API)', key='preview_pages', width='stretch',
                 disabled=not uploads or active or blocked):
        st.session_state.preview = []
        try:
            pages = extract(uploads, 'preview')
            st.session_state.preview_signature = selection_signature
            st.session_state.preview = [
                {'filename': p.metadata['filename'], 'page': p.metadata['page'],
                 'text': p.page_content[:1500]} for p in pages]
        except InputError as exc:
            st.error(str(exc))
    st.caption('Preview extracts text locally. It does not index documents or generate AI answers.')
    consent = st.checkbox(f'I agree to send these documents and questions to {ai_config.label}.', key='consent-' + '|'.join(ai_config.identity))
    has_key = ai_config.ready
    if not has_key:
        st.info(f'Configure the {ai_config.label} API key and both model names on the server. PDF preview remains available.')
    st.caption(f'AI provider: {ai_config.label}. Availability and charges depend on your provider plan and quota; a configured key does not confirm access.')
    if st.button('Index documents', key='index', type='primary', width='stretch',
                 disabled=not consent or not uploads or active or blocked or not has_key):
        engine = None
        try:
            with st.spinner('Extracting and indexing…'):
                engine = configured_assistant(ai_config)
                count = engine.ingest(uploads)
            st.session_state.assistant = engine
            st.session_state.documents = [f.name for f in uploads]
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
if st.session_state.get('chat_save_error'):
    st.warning(st.session_state.chat_save_error + ' Use Save chat now to retry before leaving.')
active = 'assistant' in st.session_state
blocked = st.session_state.cleanup_blocked or provider_changed
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
        persist_chat()
        st.rerun()
    download_col.download_button('Download chat and sources',
        data=export_chat(st.session_state.messages), file_name='document-chat.txt',
        mime='text/plain', on_click='ignore', width='stretch')
    st.caption('Clear chat keeps documents indexed. Downloaded copies remain on your device after reset.')

if not st.session_state.messages:
    st.html("""
    <div class="docmind-hero">
        <span class="docmind-hero-badge">✦ AI Grounded Document Assistant</span>
        <div class="docmind-hero-title">Ask anything about your documents</div>
        <div class="docmind-hero-sub">Upload PDFs from the sidebar, preview pages locally, and ask questions with verified physical page citations.</div>
        <div class="docmind-chips">
            <span class="docmind-chip">💡 "What is the annual leave entitlement?"</span>
            <span class="docmind-chip">💡 "Who must approve leave requests?"</span>
            <span class="docmind-chip">💡 "What is the expense claim deadline?"</span>
        </div>
    </div>
    """)
    st.caption('References use physical PDF page numbers starting at 1. Check the cited text before relying on an answer.')
for message in st.session_state.messages:
    role = message['role']
    avatar = '🧑‍💼' if role == 'user' else '🤖'
    with st.chat_message(role, avatar=avatar):
        st.text(message['content'])
        if message.get('sources'):
            pills = ''.join([f'<span class="docmind-pill">📄 {s["filename"]} · Page {s["page"]}</span>' for s in message['sources']])
            st.html(f'<div class="docmind-pills-row">{pills}</div>')
            with st.expander('View supporting passages'):
                for source in message['sources']:
                    st.caption(f'{source["filename"]} · PDF page {source["page"]}')
                    st.text(source['text'])
question = st.chat_input('Ask about your indexed PDFs', disabled=not active or not consent or blocked)
if question:
    try:
        with response_timing():
            history = [{'role': m['role'], 'content': m['content']} for m in st.session_state.messages]
            with st.spinner('Finding supporting passages…'):
                answer, sources = st.session_state.assistant.ask(question, history)
            with span('answer_formatting'):
                content, evidence = format_answer(answer, sources)
            st.session_state.messages.extend([
                {'role': 'user', 'content': question},
                {'role': 'assistant', 'content': content, 'sources': evidence}])
            persist_chat()
        st.rerun()
    except InputError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(provider_error(exc))
        st.caption('Your documents remain indexed. Retry the question after resolving the issue.')

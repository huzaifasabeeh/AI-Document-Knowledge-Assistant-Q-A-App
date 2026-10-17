"""Run from repository root with: streamlit run app.py."""
import streamlit as st
from src.knowledge_assistant.core import InputError, Upload, openai_assistant

st.set_page_config(page_title='Document Knowledge Assistant')
st.title('Document Knowledge Assistant')
st.caption('Week 2 prototype · Sources use physical PDF page numbers, starting at 1.')
st.info('Indexing sends extracted text to OpenAI for embeddings; questions and retrieved passages are sent for answers. Local session indexes are temporary. Reset deletes the active index; provider retention is separate. Do not upload confidential documents without authorization.')
if 'messages' not in st.session_state:
    st.session_state.messages = []
if st.button('Reset documents and chat'):
    if 'assistant' in st.session_state:
        try:
            st.session_state.assistant.close()
        except Exception:
            st.error('Index cleanup failed. Restart the server before uploading more documents.')
            st.stop()
        del st.session_state.assistant
    st.session_state.messages = []
    st.session_state.upload_key = st.session_state.get('upload_key', 0) + 1
    st.rerun()
consent = st.checkbox('I agree to send these documents and questions to OpenAI.')
files = st.file_uploader('Text PDFs (10 files, 10 MB each, 200 pages total)', type=['pdf'],
                         accept_multiple_files=True, key=f'uploads-{st.session_state.get("upload_key", 0)}')
if st.button('Index documents', disabled=not consent or not files or 'assistant' in st.session_state):
    engine = None
    try:
        with st.spinner('Extracting and indexing PDFs…'):
            engine = openai_assistant()
            count = engine.ingest([Upload(f.name, f.getvalue()) for f in files])
            st.session_state.assistant = engine
        st.success(f'Indexed {count} passages.')
    except InputError as exc:
        if engine is not None and not engine.ready:
            try:
                engine.close()
            except Exception:
                pass
        st.error(str(exc))
    except Exception:
        st.error('Indexing failed. Check API access, billing and network, then retry. No index was activated.')
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.text(message['content'])
question = st.chat_input('Ask about your PDFs', disabled='assistant' not in st.session_state or not consent)
if question:
    try:
        with st.spinner('Finding supporting passages…'):
            answer, sources = st.session_state.assistant.ask(question, st.session_state.messages)
        if answer.status == 'not_found':
            output = 'I could not find a supported answer in the uploaded documents. Try a more specific question.'
        else:
            lines = ['The documents contain conflicting information:'] if answer.status == 'conflict' else []
            for claim in answer.claims:
                refs = '; '.join(f'{sources[key].metadata["filename"]}, PDF page {sources[key].metadata["page"]}' for key in dict.fromkeys(claim.source_ids))
                lines.append(f'{claim.text}\nSources: {refs}')
            output = '\n\n'.join(lines)
        st.session_state.messages.extend([{'role': 'user', 'content': question}, {'role': 'assistant', 'content': output}])
        st.rerun()
    except InputError as exc:
        st.error(str(exc))
    except Exception:
        st.error('Answer generation failed. Check API access/network and retry; your documents remain indexed.')

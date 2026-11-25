"""Authenticated FastAPI HTTP adapter over src/knowledge_assistant."""
from dataclasses import dataclass, field
from hashlib import sha256
import json
import os
from pathlib import Path
import time
import tomllib
from typing import Any, Dict, List, Optional, Tuple
import uuid

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.knowledge_assistant.auth import (
    RECOVERY_SENT,
    AuthClient,
    AuthError,
    validate_credentials,
    validate_email,
    validate_recovery,
)
from src.knowledge_assistant.core import Assistant, InputError, Upload, extract
from src.knowledge_assistant.persistence import PersistenceError, WorkspaceStore
from src.knowledge_assistant.presentation import export_chat, format_answer, provider_error
from src.knowledge_assistant.providers import configured_assistant, provider_config
from src.knowledge_assistant.stage_timing import response_timing, span

SECRETS_PATH = Path(__file__).resolve().parents[1] / ".streamlit" / "secrets.toml"
SESSION_TTL_SECONDS = 86400 * 7

app = FastAPI(title="Document Knowledge Assistant API", version="1.0.0")


def allowed_origins() -> List[str]:
    raw = os.environ.get("ALLOWED_ORIGINS", "").strip()
    if raw:
        return [origin.strip() for origin in raw.split(",") if origin.strip()]
    return ["http://127.0.0.1:3000", "http://localhost:3000"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


def env_setting(name: str) -> str:
    """Read environment first, then .streamlit/secrets.toml (matches auth_ui.setting)."""
    value = os.environ.get(name, "").strip()
    if value:
        return value
    try:
        if SECRETS_PATH.is_file():
            data = tomllib.loads(SECRETS_PATH.read_text(encoding="utf-8"))
            raw = data.get(name, "")
            return str(raw).strip() if raw is not None else ""
    except (OSError, ValueError, TypeError):
        pass
    return ""


def get_auth_client() -> AuthClient:
    url = env_setting("SUPABASE_URL")
    key = env_setting("SUPABASE_PUBLISHABLE_KEY")
    if not url or not key:
        raise HTTPException(
            status_code=503,
            detail="Account sign-in is not configured yet. Please contact the app owner.",
        )
    try:
        return AuthClient(url, key)
    except AuthError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


def get_ai_config():
    try:
        return provider_config(env_setting)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@dataclass
class WorkspaceSession:
    session_id: str
    user_id: str
    uploads: List[Upload]
    signature: Tuple[Tuple[str, str], ...]
    documents: List[Dict[str, Any]]
    total_pages: int
    engine: Optional[Assistant] = None
    failed_engine: Optional[Assistant] = None
    passage_count: int = 0
    cleanup_blocked: bool = False
    saved_workspace_id: Optional[str] = None
    messages: List[Dict[str, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


_SESSIONS: Dict[str, WorkspaceSession] = {}


def _clean_stale_sessions() -> None:
    now = time.time()
    stale = [sid for sid, sess in _SESSIONS.items() if now - sess.created_at > SESSION_TTL_SECONDS]
    for sid in stale:
        sess = _SESSIONS.get(sid)
        if not sess:
            continue
        engine = sess.engine or sess.failed_engine
        if engine is not None:
            try:
                engine.close()
            except Exception:
                sess.cleanup_blocked = True
                continue
        _SESSIONS.pop(sid, None)


def _bearer_token(authorization: Optional[str]) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required. Please sign in.")
    token = authorization[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required. Please sign in.")
    return token


def get_current_user(authorization: Optional[str] = Header(None)) -> Tuple[str, Dict[str, Any], AuthClient]:
    token = _bearer_token(authorization)
    client = get_auth_client()
    try:
        user = client.user(token)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    return token, user, client


def get_owned_session(session_id: str, user_id: str) -> WorkspaceSession:
    _clean_stale_sessions()
    session = _SESSIONS.get(session_id)
    if not session or session.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail="Active session not found or expired. Reset and select documents to continue.",
        )
    return session


def _inspect_uploads(uploads: List[Upload]) -> Tuple[List[Dict[str, Any]], int, Tuple[Tuple[str, str], ...]]:
    pages = extract(uploads, "metadata-check")
    per_file_pages: Dict[str, int] = {}
    for page in pages:
        fname = page.metadata["filename"]
        per_file_pages[fname] = max(per_file_pages.get(fname, 0), page.metadata["page"])
    documents = []
    signature = []
    for upload in uploads:
        clean_name = upload.name.replace("\\", "/").split("/")[-1]
        documents.append(
            {
                "name": clean_name,
                "size_bytes": len(upload.data),
                "pages": per_file_pages.get(clean_name, 0),
            }
        )
        signature.append((clean_name, sha256(upload.data).hexdigest()))
    return documents, len(pages), tuple(signature)


# --- Request Models ---


class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    email: str
    password: str
    confirmation: str


class RecoveryRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    password: str
    confirmation: str


class ChatRequest(BaseModel):
    session_id: str
    question: str
    history: List[Dict[str, str]] = []
    consent: bool = False


class ExportMessage(BaseModel):
    role: str
    content: str
    sources: Optional[List[Dict[str, Any]]] = None


class ChatExportRequest(BaseModel):
    messages: List[ExportMessage] = []


class WorkspaceSaveSessionRequest(BaseModel):
    session_id: str
    title: str
    messages: List[Dict[str, Any]] = []


class WorkspaceLoadRequest(BaseModel):
    workspace_id: str


class WorkspaceChatSaveRequest(BaseModel):
    messages: List[Dict[str, Any]] = []


# --- Health & Config ---


@app.get("/api/health")
def health():
    auth_configured = False
    auth_error = None
    url = env_setting("SUPABASE_URL")
    key = env_setting("SUPABASE_PUBLISHABLE_KEY")
    if url and key:
        try:
            AuthClient(url, key)
            auth_configured = True
        except AuthError as exc:
            auth_error = str(exc)

    ai_payload: Dict[str, Any] = {
        "provider": None,
        "label": None,
        "identity": None,
        "ready": False,
        "error": None,
    }
    try:
        cfg = provider_config(env_setting)
        ai_payload = {
            "provider": cfg.provider,
            "label": cfg.label,
            "identity": list(cfg.identity),
            "ready": cfg.ready,
            "error": None,
        }
    except ValueError as exc:
        ai_payload["error"] = str(exc)

    return {
        "status": "healthy",
        "auth_configured": auth_configured,
        "auth_error": auth_error,
        "ai": ai_payload,
        "limits": {
            "max_files": 10,
            "max_file_mb": 10,
            "max_total_pages": 200,
        },
    }


# --- Authentication ---


@app.post("/api/auth/login")
def login(req: LoginRequest):
    client = get_auth_client()
    try:
        email = validate_credentials(req.email, req.password)
        token, user = client.login(email, req.password)
        return {
            "token": token,
            "user": {"id": user["id"], "email": user.get("email", email)},
        }
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/auth/me")
def me(auth=Depends(get_current_user)):
    _, user, _ = auth
    return {"user": {"id": user["id"], "email": user.get("email", "")}}


@app.post("/api/auth/signup")
def signup(req: SignupRequest):
    client = get_auth_client()
    try:
        email = validate_credentials(req.email, req.password, req.confirmation)
        res = client.signup(email, req.password)
        # Never keep signup tokens; require explicit confirmation & login.
        if res.get("access_token"):
            try:
                client.logout(res["access_token"])
            except AuthError:
                pass
        return {
            "message": "Request received. Check your email for a confirmation link if required, then use Log in. If you already have an account, log in instead."
        }
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/auth/recover")
def recover(req: RecoveryRequest):
    client = get_auth_client()
    try:
        email = validate_email(req.email)
        client.request_recovery(email)
        return {"message": RECOVERY_SENT}
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/auth/reset")
def reset_password(req: ResetPasswordRequest):
    client = get_auth_client()
    try:
        email, code = validate_recovery(req.email, req.code, req.password, req.confirmation)
        client.reset_password(email, code, req.password)
        return {"message": "Password updated. Use Log in with your new password."}
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/auth/logout")
def logout(authorization: Optional[str] = Header(None)):
    token = _bearer_token(authorization)
    client = get_auth_client()
    user_id = None
    try:
        user = client.user(token)
        user_id = user.get("id")
    except AuthError:
        pass

    remote_failed = False
    try:
        client.logout(token)
    except AuthError:
        remote_failed = True

    cleanup_failed = False
    if user_id:
        user_sessions = [sid for sid, sess in _SESSIONS.items() if sess.user_id == user_id]
        for sid in user_sessions:
            sess = _SESSIONS.get(sid)
            if not sess:
                continue
            engine = sess.engine or sess.failed_engine
            if engine is not None:
                try:
                    engine.close()
                except Exception:
                    cleanup_failed = True
                    sess.cleanup_blocked = True
                    continue
            _SESSIONS.pop(sid, None)

    notice = (
        "Signed out locally. Remote sign-out could not be confirmed."
        if remote_failed
        else "You have been signed out."
    )
    if cleanup_failed:
        notice += " Index cleanup failed; contact the owner to restart the server."
    return {
        "signed_out": True,
        "remote_failed": remote_failed,
        "cleanup_failed": cleanup_failed,
        "notice": notice,
    }


# --- Document Preview & Indexing ---


@app.post("/api/documents/preview")
async def preview_documents(
    files: List[UploadFile] = File(...),
    auth=Depends(get_current_user),
):
    """Extract physical PDF pages locally without contacting AI provider or requiring consent."""
    uploads = []
    for f in files:
        data = await f.read()
        uploads.append(Upload(name=f.filename or "document.pdf", data=data))
    try:
        pages = extract(uploads, "preview")
        documents, total_pages, signature = _inspect_uploads(uploads)
        preview = [
            {
                "filename": p.metadata["filename"],
                "page": p.metadata["page"],
                "text": p.page_content[:1500],
            }
            for p in pages
        ]
        return {
            "pages": preview,
            "documents": documents,
            "total_pages": total_pages,
            "selection_signature": [[name, digest] for name, digest in signature],
        }
    except InputError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/documents/index")
async def index_documents(
    consent: bool = Form(False),
    session_id: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    auth=Depends(get_current_user),
):
    """Ingest and index PDFs (new uploads or existing saved-workspace session uploads) into session Chroma store."""
    _, user, _ = auth
    _clean_stale_sessions()
    if not consent:
        raise HTTPException(status_code=400, detail="Enable provider processing consent before indexing.")

    ai_config = get_ai_config()
    if not ai_config.ready:
        raise HTTPException(
            status_code=400,
            detail=f"Configure the {ai_config.label} API key, chat model and embedding model on the server.",
        )

    existing_session: Optional[WorkspaceSession] = None
    if session_id:
        existing_session = get_owned_session(session_id, user["id"])
        if existing_session.cleanup_blocked:
            raise HTTPException(
                status_code=409,
                detail="Session paused: reset or restart the server to finish cleanup.",
            )
        if existing_session.engine is not None:
            raise HTTPException(status_code=400, detail="Reset before indexing a new document set.")
        uploads = existing_session.uploads
    else:
        if not files:
            raise HTTPException(status_code=400, detail="Select between 1 and 10 PDFs.")
        uploads = []
        for f in files:
            data = await f.read()
            uploads.append(Upload(name=f.filename or "document.pdf", data=data))

    engine: Optional[Assistant] = None
    try:
        documents, total_pages, signature = _inspect_uploads(uploads)
        engine = configured_assistant(ai_config)
        count = engine.ingest(uploads)
    except InputError as exc:
        if engine is not None:
            try:
                engine.close()
            except Exception:
                pass
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        cleanup_failed = False
        if engine is not None:
            try:
                engine.close()
            except Exception:
                cleanup_failed = True
                if existing_session is not None:
                    existing_session.failed_engine = engine
                    existing_session.cleanup_blocked = True
        status_code = 500
        detail = provider_error(exc)
        if cleanup_failed:
            detail += " Index cleanup failed. Reset or restart the server before retrying."
        raise HTTPException(status_code=status_code, detail=detail)

    if existing_session is not None:
        existing_session.engine = engine
        existing_session.passage_count = count
        existing_session.documents = documents
        existing_session.total_pages = total_pages
        existing_session.signature = signature
        target_session = existing_session
    else:
        new_id = uuid.uuid4().hex
        target_session = WorkspaceSession(
            session_id=new_id,
            user_id=user["id"],
            uploads=uploads,
            signature=signature,
            documents=documents,
            total_pages=total_pages,
            engine=engine,
            passage_count=count,
        )
        _SESSIONS[new_id] = target_session

    return {
        "session_id": target_session.session_id,
        "documents": target_session.documents,
        "total_pages": target_session.total_pages,
        "passage_count": target_session.passage_count,
        "provider_identity": list(ai_config.identity),
        "provider_label": ai_config.label,
        "saved_workspace_id": target_session.saved_workspace_id,
    }


@app.get("/api/sessions/{session_id}")
def get_session_state(session_id: str, auth=Depends(get_current_user)):
    _, user, _ = auth
    session = get_owned_session(session_id, user["id"])
    current_config = get_ai_config()
    provider_identity = (
        list(getattr(session.engine, "provider_identity", []))
        if session.engine is not None and getattr(session.engine, "provider_identity", None)
        else None
    )
    provider_changed = (
        session.engine is not None
        and getattr(session.engine, "provider_identity", None) != current_config.identity
    )
    return {
        "session_id": session.session_id,
        "documents": session.documents,
        "total_pages": session.total_pages,
        "passage_count": session.passage_count,
        "indexed": session.engine is not None,
        "cleanup_blocked": session.cleanup_blocked,
        "provider_changed": provider_changed,
        "provider_identity": provider_identity,
        "saved_workspace_id": session.saved_workspace_id,
        "messages": session.messages,
    }


@app.post("/api/sessions/{session_id}/clear")
def clear_session_chat(session_id: str, auth=Depends(get_current_user)):
    _, user, _ = auth
    session = get_owned_session(session_id, user["id"])
    if session.cleanup_blocked:
        raise HTTPException(status_code=409, detail="Session paused until cleanup finishes.")
    session.messages = []
    return {"cleared": True}


@app.post("/api/sessions/{session_id}/reset")
def reset_session(session_id: str, auth=Depends(get_current_user)):
    _, user, _ = auth
    session = get_owned_session(session_id, user["id"])
    engine = session.engine or session.failed_engine
    if engine is not None:
        try:
            engine.close()
        except Exception:
            session.cleanup_blocked = True
            session.failed_engine = engine
            session.engine = None
            raise HTTPException(
                status_code=500,
                detail="Cleanup failed. Retry reset or restart the server before continuing.",
            )
    _SESSIONS.pop(session_id, None)
    return {"reset": True}


# --- Q&A / Chat & Export ---


@app.post("/api/chat")
def chat(req: ChatRequest, auth=Depends(get_current_user)):
    _, user, _ = auth
    session = get_owned_session(req.session_id, user["id"])
    if session.cleanup_blocked:
        raise HTTPException(
            status_code=409,
            detail="Session paused: reset or restart the server to finish cleanup.",
        )
    if not req.consent:
        raise HTTPException(
            status_code=400,
            detail="Chat paused. Enable processing consent in the sidebar to continue.",
        )
    if session.engine is None:
        raise HTTPException(status_code=400, detail="Index documents first.")

    current_config = get_ai_config()
    if getattr(session.engine, "provider_identity", None) != current_config.identity:
        raise HTTPException(
            status_code=409,
            detail="AI configuration changed. Reset and re-index your documents before continuing.",
        )

    started = time.time()
    try:
        with response_timing():
            answer, sources = session.engine.ask(req.question, req.history)
            with span("answer_formatting"):
                content, evidence = format_answer(answer, sources)
    except InputError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=provider_error(exc))

    elapsed = f"{time.time() - started:.2f}s"
    claims_payload = []
    for claim in answer.claims:
        claim_refs = []
        seen_keys = set()
        for sid in claim.source_ids:
            if sid in seen_keys or sid not in sources:
                continue
            seen_keys.add(sid)
            doc = sources[sid]
            claim_refs.append(
                {
                    "filename": doc.metadata["filename"],
                    "page": doc.metadata["page"],
                }
            )
        claims_payload.append({"text": claim.text, "refs": claim_refs})

    session.messages.extend(
        [
            {"role": "user", "content": req.question},
            {
                "role": "assistant",
                "content": content,
                "status": answer.status,
                "claims": claims_payload,
                "sources": evidence,
                "latency": elapsed,
            },
        ]
    )

    return {
        "status": answer.status,
        "content": content,
        "claims": claims_payload,
        "sources": evidence,
        "latency": elapsed,
    }


@app.post("/api/chat/export")
def export_conversation(req: ChatExportRequest, auth=Depends(get_current_user)):
    payload = [m.model_dump() for m in req.messages]
    return {
        "filename": "document-chat.txt",
        "content": export_chat(payload),
    }


# --- Saved Workspaces Persistence ---


def _workspace_store(auth=Depends(get_current_user)) -> Tuple[WorkspaceStore, Dict[str, Any]]:
    token, user, client = auth
    return WorkspaceStore(client.url, client.key, token, user["id"]), user


@app.get("/api/workspaces")
def list_workspaces(dep=Depends(_workspace_store)):
    store, _ = dep
    try:
        return {"workspaces": store.list()}
    except PersistenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/workspaces/save")
def save_workspace_from_session(req: WorkspaceSaveSessionRequest, dep=Depends(_workspace_store)):
    store, user = dep
    session = get_owned_session(req.session_id, user["id"])
    if session.cleanup_blocked:
        raise HTTPException(status_code=409, detail="Session paused until cleanup finishes.")
    if not session.uploads:
        raise HTTPException(status_code=400, detail="No document uploads selected to save.")
    try:
        ws_id = store.save(req.title, session.uploads, req.messages)
        session.saved_workspace_id = ws_id
        return {"workspace_id": ws_id, "title": req.title.strip()}
    except (PersistenceError, InputError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/workspaces/save-files")
async def save_workspace_from_files(
    title: str = Form(...),
    messages: str = Form("[]"),
    files: List[UploadFile] = File(...),
    dep=Depends(_workspace_store),
):
    """Save selected PDFs and chat directly to a new workspace even before AI indexing."""
    store, user = dep
    try:
        parsed_messages = json.loads(messages) if messages else []
        if not isinstance(parsed_messages, list):
            raise ValueError()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid messages payload.")

    uploads = []
    for f in files:
        data = await f.read()
        uploads.append(Upload(name=f.filename or "document.pdf", data=data))

    try:
        documents, total_pages, signature = _inspect_uploads(uploads)
        ws_id = store.save(title, uploads, parsed_messages)
    except (PersistenceError, InputError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Bind a server session with restored uploads so indexing right after save uses exact saved PDFs.
    new_id = uuid.uuid4().hex
    _SESSIONS[new_id] = WorkspaceSession(
        session_id=new_id,
        user_id=user["id"],
        uploads=uploads,
        signature=signature,
        documents=documents,
        total_pages=total_pages,
        engine=None,
        saved_workspace_id=ws_id,
    )
    return {
        "workspace_id": ws_id,
        "session_id": new_id,
        "title": title.strip(),
        "documents": documents,
        "total_pages": total_pages,
    }


@app.post("/api/workspaces/load")
def load_workspace(req: WorkspaceLoadRequest, dep=Depends(_workspace_store)):
    """Restore saved PDFs and chat without consuming AI credits until user grants consent & re-indexes."""
    store, user = dep
    _clean_stale_sessions()
    try:
        uploads, messages = store.load(req.workspace_id)
        documents, total_pages, signature = _inspect_uploads(uploads)
    except (PersistenceError, InputError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    session_id = uuid.uuid4().hex
    _SESSIONS[session_id] = WorkspaceSession(
        session_id=session_id,
        user_id=user["id"],
        uploads=uploads,
        signature=signature,
        documents=documents,
        total_pages=total_pages,
        engine=None,
        saved_workspace_id=req.workspace_id,
        messages=messages,
    )
    return {
        "session_id": session_id,
        "workspace_id": req.workspace_id,
        "documents": documents,
        "total_pages": total_pages,
        "messages": messages,
        "indexed": False,
    }


@app.patch("/api/workspaces/{workspace_id}/chat")
def save_workspace_chat(
    workspace_id: str,
    req: WorkspaceChatSaveRequest,
    dep=Depends(_workspace_store),
):
    store, _ = dep
    try:
        store.save_chat(workspace_id, req.messages)
        return {"saved": True, "workspace_id": workspace_id}
    except PersistenceError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.delete("/api/workspaces/{workspace_id}")
def delete_workspace(workspace_id: str, dep=Depends(_workspace_store)):
    store, user = dep
    try:
        store.delete(workspace_id)
    except PersistenceError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Clear saved_workspace_id binding on any active session referencing this deleted workspace.
    for sess in _SESSIONS.values():
        if sess.user_id == user["id"] and sess.saved_workspace_id == workspace_id:
            sess.saved_workspace_id = None
    return {"deleted": True, "workspace_id": workspace_id}

"""FastAPI backend providing REST endpoints for Next.js DocMind frontend."""
import os
import uuid
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.knowledge_assistant.core import InputError, Upload, extract, Assistant
from src.knowledge_assistant.presentation import format_answer, provider_error
from src.knowledge_assistant.providers import provider_config, configured_assistant
from src.knowledge_assistant.auth import AuthClient, AuthError, validate_credentials, validate_email, validate_recovery
from src.knowledge_assistant.persistence import WorkspaceStore, PersistenceError

app = FastAPI(title="DocMind API", version="1.0.0")

# Enable CORS for Next.js frontend (localhost:3000 & production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def env_setting(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if val:
        return val
    try:
        import tomllib
        from pathlib import Path
        secrets_path = Path(".streamlit/secrets.toml")
        if secrets_path.exists():
            with open(secrets_path, "rb") as f:
                data = tomllib.load(f)
                return str(data.get(name, "")).strip()
    except Exception:
        pass
    return ""


def get_ai_config():
    try:
        return provider_config(env_setting)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


def get_auth_client():
    url = env_setting("SUPABASE_URL")
    key = env_setting("SUPABASE_PUBLISHABLE_KEY")
    if not url or not key:
        raise HTTPException(status_code=500, detail="Supabase authentication is not configured on the server.")
    return AuthClient(url, key)


# In-memory store for active assistant sessions: session_id -> Assistant
_ASSISTANT_SESSIONS: Dict[str, Assistant] = {}
# In-memory store for uploaded files: session_id -> List[Upload]
_UPLOAD_CACHE: Dict[str, List[Upload]] = {}


# --- Request Models ---

class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    email: str
    password: str
    confirmation: Optional[str] = None


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


class WorkspaceSaveRequest(BaseModel):
    session_id: str
    title: str
    messages: List[Dict[str, Any]] = []


class WorkspaceLoadRequest(BaseModel):
    workspace_id: str


# --- Health & Config ---

@app.get("/api/health")
def health():
    cfg = get_ai_config()
    return {
        "status": "healthy",
        "provider": cfg.label,
        "models": cfg.identity,
        "ready": cfg.ready,
    }


# --- Authentication ---

@app.post("/api/auth/login")
def login(req: LoginRequest):
    client = get_auth_client()
    try:
        email = validate_credentials(req.email, req.password)
        token, user = client.login(email, req.password)
        return {"token": token, "user": user}
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/auth/signup")
def signup(req: SignupRequest):
    client = get_auth_client()
    try:
        email = validate_credentials(req.email, req.password, req.confirmation or req.password)
        res = client.signup(email, req.password)
        if res.get("access_token"):
            client.logout(res["access_token"])
        return {"message": "Account created. Check your email for confirmation if required, then sign in."}
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/auth/recover")
def recover(req: RecoveryRequest):
    client = get_auth_client()
    try:
        email = validate_email(req.email)
        client.request_recovery(email)
        return {"message": "If an account exists for that email, a reset code has been sent."}
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/auth/reset")
def reset_password(req: ResetPasswordRequest):
    client = get_auth_client()
    try:
        email, code = validate_recovery(req.email, req.code, req.password, req.confirmation)
        client.reset_password(email, code, req.password)
        return {"message": "Password updated successfully. You can now log in."}
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# --- Document Upload & Indexing ---

@app.post("/api/documents/preview")
async def preview_documents(files: List[UploadFile] = File(...)):
    """Extract pages for local preview without contacting AI provider."""
    uploads = []
    for f in files:
        data = await f.read()
        uploads.append(Upload(name=f.filename, data=data))
    try:
        pages = extract(uploads, "preview-session")
        preview = [
            {"filename": p.metadata["filename"], "page": p.metadata["page"], "text": p.page_content[:1500]}
            for p in pages
        ]
        return {"pages": preview, "total_pages": len(pages)}
    except InputError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/documents/index")
async def index_documents(files: List[UploadFile] = File(...)):
    """Ingest and index PDFs into session-scoped vector store."""
    ai_config = get_ai_config()
    uploads = []
    for f in files:
        data = await f.read()
        uploads.append(Upload(name=f.filename, data=data))
    try:
        engine = configured_assistant(ai_config)
        count = engine.ingest(uploads)
        session_id = uuid.uuid4().hex
        _ASSISTANT_SESSIONS[session_id] = engine
        _UPLOAD_CACHE[session_id] = uploads
        return {
            "session_id": session_id,
            "documents": [u.name for u in uploads],
            "passage_count": count,
        }
    except InputError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=provider_error(exc))


# --- Q&A / Chat ---

@app.post("/api/chat")
def chat(req: ChatRequest):
    import time
    start_time = time.time()
    
    # Locate session or default active engine
    engine = _ASSISTANT_SESSIONS.get(req.session_id)
    if not engine and _ASSISTANT_SESSIONS:
        # Fallback to the latest indexed session
        engine = list(_ASSISTANT_SESSIONS.values())[-1]
        
    if not engine:
        # Return helpful guide if no documents are indexed yet
        return {
            "status": "not_found",
            "answer": f"No active documents are indexed in this session. Please upload a PDF in the Documents tab or click '+ Attach documents' to ask questions about your documents.",
            "points": [
                {
                    "num": "01",
                    "title": "Index your documents",
                    "body": "Upload any PDF, DOCX, or text file up to 25 MB to start querying your knowledge base.",
                    "citationId": None
                }
            ],
            "citations": [],
            "sources": [],
            "evidence": None,
            "latency": "0.1s"
        }

    try:
        answer, sources = engine.ask(req.question, req.history)
        elapsed = f"{time.time() - start_time:.1f}s"
        
        if answer.status == "not_found" or not answer.claims:
            return {
                "status": "not_found",
                "answer": "I could not find a supported answer in the uploaded documents. Try rephrasing or asking a more specific question.",
                "points": [],
                "citations": [],
                "sources": [],
                "evidence": None,
                "latency": elapsed
            }

        # Structure claims into DocuMind points and citations
        points = []
        citations = []
        seen_chunks = set()
        evidence_list = []
        citation_counter = 1

        for idx, claim in enumerate(answer.claims):
            first_cit_id = None
            for chunk_id in claim.source_ids:
                doc = sources.get(chunk_id)
                if not doc:
                    continue
                fname = doc.metadata.get("filename", "Document.pdf")
                pg = doc.metadata.get("page", 1)
                
                if chunk_id not in seen_chunks:
                    seen_chunks.add(chunk_id)
                    citations.append({
                        "id": citation_counter,
                        "label": f"{citation_counter} {fname} • p. {pg}",
                        "docName": fname,
                        "pages": f"p. {pg}",
                        "highlightText": claim.text,
                        "fullSnippet": doc.page_content
                    })
                    evidence_list.append({
                        "num": citation_counter,
                        "filename": fname,
                        "page": pg,
                        "text": doc.page_content,
                        "highlight": claim.text
                    })
                    first_cit_id = citation_counter
                    citation_counter += 1
                else:
                    # Find existing citation id
                    for c in citations:
                        if c["docName"] == fname and c["pages"] == f"p. {pg}":
                            first_cit_id = c["id"]
                            break

            # Create title from first 3-5 words
            words = claim.text.split()
            title = " ".join(words[:4]).rstrip(",.:;") if len(words) >= 4 else "Key finding"
            points.append({
                "num": f"0{idx + 1}" if idx < 9 else str(idx + 1),
                "title": title,
                "body": claim.text,
                "citationId": first_cit_id
            })

        # Primary evidence for the right-hand panel
        first_ev = evidence_list[0] if evidence_list else None
        related_passages = [
            {
                "num": ev["num"],
                "title": f"Passage from {ev['filename']}",
                "docAndPage": f"{ev['filename']} • p. {ev['page']}"
            }
            for ev in evidence_list[1:4]
        ]

        evidence_payload = None
        if first_ev:
            evidence_payload = {
                "isOpen": True,
                "docTitle": first_ev["filename"].replace(".pdf", ""),
                "docType": "PDF Document",
                "page": first_ev["page"],
                "totalPages": max([e["page"] for e in evidence_list] + [first_ev["page"]]),
                "heading": f"Relevant passage from page {first_ev['page']}",
                "fullText": first_ev["text"],
                "highlightSnippet": first_ev["highlight"],
                "relatedPassages": related_passages
            }

        summary_text = answer.claims[0].text if answer.claims else "Grounded findings based on your documents."

        return {
            "status": answer.status,
            "answer": summary_text,
            "points": points,
            "citations": citations,
            "evidence": evidence_payload,
            "groundingSources": len(citations),
            "latency": elapsed
        }
    except InputError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=provider_error(exc))


# --- Workspaces Persistence ---

def get_workspace_store(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication token required.")
    token = authorization.split(" ")[1]
    url = env_setting("SUPABASE_URL")
    key = env_setting("SUPABASE_PUBLISHABLE_KEY")
    client = get_auth_client()
    try:
        user = client.user(token)
    except AuthError:
        raise HTTPException(status_code=401, detail="Session invalid or expired.")
    return WorkspaceStore(url, key, token, user["id"])


@app.get("/api/workspaces")
def list_workspaces(store: WorkspaceStore = Depends(get_workspace_store)):
    try:
        return {"workspaces": store.list()}
    except PersistenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/workspaces/save")
def save_workspace(req: WorkspaceSaveRequest, store: WorkspaceStore = Depends(get_workspace_store)):
    uploads = _UPLOAD_CACHE.get(req.session_id)
    if not uploads:
        raise HTTPException(status_code=400, detail="No active document uploads found to save.")
    try:
        ws_id = store.save(req.title, uploads, req.messages)
        return {"workspace_id": ws_id, "title": req.title}
    except (PersistenceError, InputError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/workspaces/load")
def load_workspace(req: WorkspaceLoadRequest, store: WorkspaceStore = Depends(get_workspace_store)):
    ai_config = get_ai_config()
    try:
        uploads, messages = store.load(req.workspace_id)
        engine = configured_assistant(ai_config)
        count = engine.ingest(uploads)
        session_id = uuid.uuid4().hex
        _ASSISTANT_SESSIONS[session_id] = engine
        _UPLOAD_CACHE[session_id] = uploads
        return {
            "session_id": session_id,
            "documents": [u.name for u in uploads],
            "messages": messages,
            "passage_count": count,
        }
    except (PersistenceError, InputError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.delete("/api/workspaces/{workspace_id}")
def delete_workspace(workspace_id: str, store: WorkspaceStore = Depends(get_workspace_store)):
    try:
        store.delete(workspace_id)
        return {"deleted": True, "workspace_id": workspace_id}
    except PersistenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

"""Offline unit and integration checks for api/main.py; zero live network calls."""
from pathlib import Path
from unittest.mock import Mock

from fastapi.testclient import TestClient
from langchain_core.documents import Document
import pytest

import api.main as api_main
from src.knowledge_assistant.core import Answer, Claim

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PDF = ROOT / "data/sample_pdfs/leave.pdf"


@pytest.fixture(autouse=True)
def isolated_api_state(tmp_path, monkeypatch):
    api_main._SESSIONS.clear()
    api_main._SESSIONS.update({})
    monkeypatch.setattr(api_main, "SECRETS_PATH", tmp_path / "missing-secrets.toml")
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "sb_publishable_test")
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
    yield
    api_main._SESSIONS.clear()


@pytest.fixture
def fake_auth(monkeypatch):
    fake = Mock()

    def fake_user(token):
        if token == "token-a":
            return {"id": "00000000-0000-4000-8000-00000000000a", "email": "a@example.com", "email_confirmed_at": "now"}
        if token == "token-b":
            return {"id": "00000000-0000-4000-8000-00000000000b", "email": "b@example.com", "email_confirmed_at": "now"}
        from src.knowledge_assistant.auth import AuthError
        raise AuthError("Confirm your email before signing in.")

    fake.url = "https://example.supabase.co"
    fake.key = "sb_publishable_test"
    fake.user.side_effect = fake_user
    fake.login.return_value = ("token-a", {"id": "00000000-0000-4000-8000-00000000000a", "email": "a@example.com"})
    fake.signup.return_value = {"id": "00000000-0000-4000-8000-00000000000a", "access_token": "signup-temp"}
    monkeypatch.setattr(api_main, "AuthClient", Mock(return_value=fake))
    return fake


def test_health_reports_auth_and_ai_without_secrets(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    client = TestClient(api_main.app)
    res = client.get("/api/health")
    assert res.status_code == 200
    body = res.json()
    assert body["auth_configured"] is False
    assert body["ai"]["provider"] == "openai"
    assert body["ai"]["ready"] is False
    assert body["limits"] == {"max_files": 10, "max_file_mb": 10, "max_total_pages": 200}


def test_unauthenticated_endpoints_fail_closed(fake_auth):
    client = TestClient(api_main.app)
    pdf_bytes = SAMPLE_PDF.read_bytes()
    assert client.get("/api/auth/me").status_code == 401
    assert client.post("/api/documents/preview", files=[("files", ("leave.pdf", pdf_bytes, "application/pdf"))]).status_code == 401
    assert client.post("/api/documents/index", data={"consent": "true"}, files=[("files", ("leave.pdf", pdf_bytes, "application/pdf"))]).status_code == 401
    assert client.post("/api/chat", json={"session_id": "any", "question": "hi", "consent": True}).status_code == 401
    assert client.get("/api/workspaces").status_code == 401


def test_signup_never_returns_token_and_logs_out_temp_session(fake_auth):
    client = TestClient(api_main.app)
    res = client.post(
        "/api/auth/signup",
        json={"email": "a@example.com", "password": "password123", "confirmation": "password123"},
    )
    assert res.status_code == 200
    assert "token" not in res.json()
    fake_auth.logout.assert_called_once_with("signup-temp")


def test_preview_needs_no_ai_key_or_consent(fake_auth, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    factory = Mock(side_effect=AssertionError("AI factory must not run on preview"))
    monkeypatch.setattr(api_main, "configured_assistant", factory)
    client = TestClient(api_main.app)
    res = client.post(
        "/api/documents/preview",
        headers={"Authorization": "Bearer token-a"},
        files=[("files", ("leave.pdf", SAMPLE_PDF.read_bytes(), "application/pdf"))],
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_pages"] == 2
    assert len(data["pages"]) == 2
    assert "20 days" in data["pages"][0]["text"]
    factory.assert_not_called()


def test_session_isolation_consent_provider_change_and_reset(fake_auth, monkeypatch):
    engine = Mock()
    engine.provider_identity = ("openai", "gpt-4.1-mini", "text-embedding-3-small")
    engine.ingest.return_value = 3
    engine.ask.return_value = (
        Answer(status="answered", claims=[Claim(text="Employees get 20 days.", source_ids=["c1"])]),
        {"c1": Document(page_content="20 days leave.", metadata={"filename": "leave.pdf", "page": 1})},
    )
    monkeypatch.setattr(api_main, "configured_assistant", lambda cfg: engine)
    client = TestClient(api_main.app)

    # Consent required to index
    no_consent = client.post(
        "/api/documents/index",
        headers={"Authorization": "Bearer token-a"},
        data={"consent": "false"},
        files=[("files", ("leave.pdf", SAMPLE_PDF.read_bytes(), "application/pdf"))],
    )
    assert no_consent.status_code == 400

    # User A indexes document
    indexed = client.post(
        "/api/documents/index",
        headers={"Authorization": "Bearer token-a"},
        data={"consent": "true"},
        files=[("files", ("leave.pdf", SAMPLE_PDF.read_bytes(), "application/pdf"))],
    )
    assert indexed.status_code == 200
    session_id = indexed.json()["session_id"]
    assert indexed.json()["total_pages"] == 2
    assert indexed.json()["passage_count"] == 3

    # User B MUST NOT be able to query User A's session or fall back to it
    b_chat = client.post(
        "/api/chat",
        headers={"Authorization": "Bearer token-b"},
        json={"session_id": session_id, "question": "How much leave?", "consent": True},
    )
    assert b_chat.status_code == 404

    # User A paused when consent is false
    paused = client.post(
        "/api/chat",
        headers={"Authorization": "Bearer token-a"},
        json={"session_id": session_id, "question": "How much leave?", "consent": False},
    )
    assert paused.status_code == 400

    # User A succeeds with consent
    ok = client.post(
        "/api/chat",
        headers={"Authorization": "Bearer token-a"},
        json={"session_id": session_id, "question": "How much leave?", "consent": True},
    )
    assert ok.status_code == 200
    payload = ok.json()
    assert payload["status"] == "answered"
    assert payload["sources"] == [{"filename": "leave.pdf", "page": 1, "text": "20 days leave."}]
    assert payload["claims"][0]["refs"] == [{"filename": "leave.pdf", "page": 1}]

    # Provider change blocks chat until reset
    monkeypatch.setenv("OPENAI_CHAT_MODEL", "gpt-other")
    changed = client.post(
        "/api/chat",
        headers={"Authorization": "Bearer token-a"},
        json={"session_id": session_id, "question": "How much leave?", "consent": True},
    )
    assert changed.status_code == 409

    # Reset closes engine cleanly
    reset_res = client.post(f"/api/sessions/{session_id}/reset", headers={"Authorization": "Bearer token-a"})
    assert reset_res.status_code == 200
    engine.close.assert_called_once()
    assert session_id not in api_main._SESSIONS


def test_load_workspace_restores_without_ai_and_requires_reindex(fake_auth, monkeypatch):
    store = Mock()
    from src.knowledge_assistant.core import Upload
    store.load.return_value = (
        [Upload("leave.pdf", SAMPLE_PDF.read_bytes())],
        [{"role": "user", "content": "Old q"}, {"role": "assistant", "content": "Old a", "sources": []}],
    )
    monkeypatch.setattr(api_main, "WorkspaceStore", Mock(return_value=store))
    factory = Mock(side_effect=AssertionError("Workspace restore must NOT invoke AI"))
    monkeypatch.setattr(api_main, "configured_assistant", factory)

    client = TestClient(api_main.app)
    loaded = client.post(
        "/api/workspaces/load",
        headers={"Authorization": "Bearer token-a"},
        json={"workspace_id": "11111111-1111-4111-8111-111111111111"},
    )
    assert loaded.status_code == 200
    body = loaded.json()
    assert body["indexed"] is False
    assert body["total_pages"] == 2
    assert len(body["messages"]) == 2
    factory.assert_not_called()

    # Chat is blocked until user re-indexes the restored session
    blocked_chat = client.post(
        "/api/chat",
        headers={"Authorization": "Bearer token-a"},
        json={"session_id": body["session_id"], "question": "New q?", "consent": True},
    )
    assert blocked_chat.status_code == 400
    assert "Index documents first" in blocked_chat.json()["detail"]

    # Re-indexing via session_id works once consented
    engine = Mock()
    engine.provider_identity = ("openai", "gpt-4.1-mini", "text-embedding-3-small")
    engine.ingest.return_value = 2
    monkeypatch.setattr(api_main, "configured_assistant", lambda cfg: engine)
    reindexed = client.post(
        "/api/documents/index",
        headers={"Authorization": "Bearer token-a"},
        data={"consent": "true", "session_id": body["session_id"]},
    )
    assert reindexed.status_code == 200
    assert reindexed.json()["saved_workspace_id"] == "11111111-1111-4111-8111-111111111111"
    assert reindexed.json()["passage_count"] == 2


def test_logout_closes_user_sessions_only(fake_auth):
    eng_a, eng_b = Mock(), Mock()
    api_main._SESSIONS["sa"] = api_main.WorkspaceSession(
        session_id="sa",
        user_id="00000000-0000-4000-8000-00000000000a",
        uploads=[],
        signature=(),
        documents=[],
        total_pages=0,
        engine=eng_a,
    )
    api_main._SESSIONS["sb"] = api_main.WorkspaceSession(
        session_id="sb",
        user_id="00000000-0000-4000-8000-00000000000b",
        uploads=[],
        signature=(),
        documents=[],
        total_pages=0,
        engine=eng_b,
    )
    client = TestClient(api_main.app)
    res = client.post("/api/auth/logout", headers={"Authorization": "Bearer token-a"})
    assert res.status_code == 200
    eng_a.close.assert_called_once()
    eng_b.close.assert_not_called()
    assert "sa" not in api_main._SESSIONS
    assert "sb" in api_main._SESSIONS


def test_chat_conflict_not_found_and_export(fake_auth, monkeypatch):
    engine = Mock()
    engine.provider_identity = ("openai", "gpt-4.1-mini", "text-embedding-3-small")
    engine.ingest.return_value = 2
    engine.ask.side_effect = [
        (
            Answer(
                status="conflict",
                claims=[
                    Claim(text="Policy A says 15 days.", source_ids=["c1"]),
                    Claim(text="Policy B says 20 days.", source_ids=["c2"]),
                ],
            ),
            {
                "c1": Document(page_content="15 days.", metadata={"filename": "leave.pdf", "page": 1}),
                "c2": Document(page_content="20 days.", metadata={"filename": "leave.pdf", "page": 2}),
            },
        ),
        (Answer(status="not_found", claims=[]), {}),
    ]
    monkeypatch.setattr(api_main, "configured_assistant", lambda cfg: engine)
    client = TestClient(api_main.app)
    sid = client.post(
        "/api/documents/index",
        headers={"Authorization": "Bearer token-a"},
        data={"consent": "true"},
        files=[("files", ("leave.pdf", SAMPLE_PDF.read_bytes(), "application/pdf"))],
    ).json()["session_id"]

    conflict_res = client.post(
        "/api/chat",
        headers={"Authorization": "Bearer token-a"},
        json={"session_id": sid, "question": "Days?", "consent": True},
    )
    assert conflict_res.status_code == 200
    assert conflict_res.json()["status"] == "conflict"
    assert "conflicting information" in conflict_res.json()["content"]
    assert len(conflict_res.json()["sources"]) == 2

    nf_res = client.post(
        "/api/chat",
        headers={"Authorization": "Bearer token-a"},
        json={"session_id": sid, "question": "Missing?", "consent": True},
    )
    assert nf_res.status_code == 200
    assert nf_res.json()["status"] == "not_found"
    assert nf_res.json()["sources"] == []

    exp = client.post(
        "/api/chat/export",
        headers={"Authorization": "Bearer token-a"},
        json={"messages": [{"role": "assistant", "content": "20 days.", "sources": [{"filename": "leave.pdf", "page": 1, "text": "20 days."}]}]},
    )
    assert exp.status_code == 200
    assert exp.json()["filename"] == "document-chat.txt"
    assert "leave.pdf | PDF page 1" in exp.json()["content"]


def test_cleanup_blocked_and_saved_workspaces_crud(fake_auth, monkeypatch):
    engine = Mock()
    engine.provider_identity = ("openai", "gpt-4.1-mini", "text-embedding-3-small")
    engine.ingest.return_value = 1
    engine.close.side_effect = [RuntimeError("busy"), None]
    monkeypatch.setattr(api_main, "configured_assistant", lambda cfg: engine)

    store = Mock()
    store.list.return_value = [{"id": "ws-1", "title": "Policy", "created_at": "2026-11-25T00:00:00Z", "status": "ready"}]
    store.save.return_value = "ws-1"
    monkeypatch.setattr(api_main, "WorkspaceStore", Mock(return_value=store))

    client = TestClient(api_main.app)
    save_files = client.post(
        "/api/workspaces/save-files",
        headers={"Authorization": "Bearer token-a"},
        data={"title": "Policy", "messages": "[]"},
        files=[("files", ("leave.pdf", SAMPLE_PDF.read_bytes(), "application/pdf"))],
    )
    assert save_files.status_code == 200
    sid = save_files.json()["session_id"]
    ws_id = save_files.json()["workspace_id"]
    assert ws_id == "ws-1"

    # Index session bound to saved workspace
    idx = client.post(
        "/api/documents/index",
        headers={"Authorization": "Bearer token-a"},
        data={"consent": "true", "session_id": sid},
    )
    assert idx.status_code == 200

    # Save chat turn update
    chat_patch = client.patch(
        f"/api/workspaces/{ws_id}/chat",
        headers={"Authorization": "Bearer token-a"},
        json={"messages": [{"role": "user", "content": "q"}]},
    )
    assert chat_patch.status_code == 200
    store.save_chat.assert_called_once()

    # Failed cleanup sets cleanup_blocked and blocks chat until retry reset succeeds
    r1 = client.post(f"/api/sessions/{sid}/reset", headers={"Authorization": "Bearer token-a"})
    assert r1.status_code == 500
    blocked = client.post(
        "/api/chat",
        headers={"Authorization": "Bearer token-a"},
        json={"session_id": sid, "question": "hi", "consent": True},
    )
    assert blocked.status_code == 409
    r2 = client.post(f"/api/sessions/{sid}/reset", headers={"Authorization": "Bearer token-a"})
    assert r2.status_code == 200
    assert sid not in api_main._SESSIONS

    # Delete workspace
    del_res = client.delete(f"/api/workspaces/{ws_id}", headers={"Authorization": "Bearer token-a"})
    assert del_res.status_code == 200
    store.delete.assert_called_once_with(ws_id)


def test_session_state_restore_and_clear_chat(fake_auth, monkeypatch):
    engine = Mock()
    engine.provider_identity = ("openai", "gpt-4.1-mini", "text-embedding-3-small")
    engine.ingest.return_value = 2
    engine.ask.return_value = (
        Answer(status="answered", claims=[Claim(text="20 days.", source_ids=["c1"])]),
        {"c1": Document(page_content="20 days.", metadata={"filename": "leave.pdf", "page": 1})},
    )
    monkeypatch.setattr(api_main, "configured_assistant", lambda cfg: engine)
    client = TestClient(api_main.app)

    sid = client.post(
        "/api/documents/index",
        headers={"Authorization": "Bearer token-a"},
        data={"consent": "true"},
        files=[("files", ("leave.pdf", SAMPLE_PDF.read_bytes(), "application/pdf"))],
    ).json()["session_id"]

    client.post(
        "/api/chat",
        headers={"Authorization": "Bearer token-a"},
        json={"session_id": sid, "question": "Days?", "consent": True},
    )

    state = client.get(f"/api/sessions/{sid}", headers={"Authorization": "Bearer token-a"})
    assert state.status_code == 200
    assert state.json()["indexed"] is True
    assert state.json()["passage_count"] == 2
    assert len(state.json()["messages"]) == 2

    # User B cannot read User A's session state
    assert client.get(f"/api/sessions/{sid}", headers={"Authorization": "Bearer token-b"}).status_code == 404

    cleared = client.post(f"/api/sessions/{sid}/clear", headers={"Authorization": "Bearer token-a"})
    assert cleared.status_code == 200
    state_after = client.get(f"/api/sessions/{sid}", headers={"Authorization": "Bearer token-a"})
    assert state_after.json()["messages"] == []
    assert state_after.json()["indexed"] is True



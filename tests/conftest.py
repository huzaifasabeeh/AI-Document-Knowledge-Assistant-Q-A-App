"""Offline tests must never consume the developer's real service credentials."""
import pytest
import streamlit as st


@pytest.fixture(autouse=True)
def isolated_service_configuration(monkeypatch):
    monkeypatch.setattr(st, 'secrets', {})
    for name in (
        'SUPABASE_URL', 'SUPABASE_PUBLISHABLE_KEY', 'AI_PROVIDER',
        'OPENAI_API_KEY', 'OPENAI_CHAT_MODEL', 'OPENAI_EMBEDDING_MODEL',
        'GEMINI_API_KEY', 'GEMINI_CHAT_MODEL', 'GEMINI_EMBEDDING_MODEL',
    ):
        monkeypatch.delenv(name, raising=False)

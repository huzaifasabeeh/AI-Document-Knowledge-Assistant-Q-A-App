from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_app_starts_without_key_and_reset_works(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / 'app.py').run()
    assert not app.exception
    assert app.chat_input[0].disabled
    app.button[0].click().run()
    assert not app.exception
    assert app.session_state['messages'] == []


def test_openai_client_configuration_without_network(monkeypatch):
    from src.knowledge_assistant.core import openai_assistant
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test-not-a-real-key')
    engine = openai_assistant()
    engine.close()

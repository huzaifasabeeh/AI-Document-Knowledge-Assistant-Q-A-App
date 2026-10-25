from unittest.mock import Mock

import pytest

from src.knowledge_assistant.core import Assistant, InputError, Upload
from test_week2 import LocalEmbeddings, Model, Answer, pdf


def test_failed_embedding_preserves_error_and_cleanup_is_repeat_safe():
    embeddings = LocalEmbeddings()
    failure = RuntimeError('simulated quota failure')
    embeddings.embed_documents = Mock(side_effect=failure)
    engine = Assistant(embeddings, Model(Answer(status='not_found', claims=[])))
    with pytest.raises(RuntimeError) as caught:
        engine.ingest([Upload('policy.pdf', pdf('Leave is 20 days.'))])
    assert caught.value is failure
    assert not engine.ready
    engine.close()
    engine.close()
    with pytest.raises(InputError, match='closed'):
        engine.ingest([Upload('policy.pdf', pdf('Leave is 20 days.'))])
    # Retry in a fresh session, as the UI does after an indexing failure.
    retry = Assistant(LocalEmbeddings(), Model(Answer(status='not_found', claims=[])))
    try:
        assert retry.ingest([Upload('policy.pdf', pdf('Leave is 20 days.'))]) == 1
    finally:
        retry.close()
        retry.close()


def test_cleanup_failure_is_retryable_and_does_not_mask_indexing_error():
    engine = Assistant.__new__(Assistant)
    engine.session_id = 'test'
    engine.ready = False
    engine._closed = False
    failure = RuntimeError('original indexing failure')
    engine.store = Mock()
    engine.store.add_documents.side_effect = failure
    engine.store.delete_collection.side_effect = [RuntimeError('cleanup failed'), None]
    with pytest.raises(RuntimeError) as caught:
        engine.ingest([Upload('policy.pdf', pdf('Leave is 20 days.'))])
    assert caught.value is failure
    assert not engine._closed
    engine.close()
    engine.close()
    assert engine.store.delete_collection.call_count == 2


def test_smoke_preserves_primary_failure_when_final_cleanup_fails(monkeypatch):
    from scripts import live_smoke
    engine = Mock()
    failure = RuntimeError('original provider failure')
    engine.ingest.side_effect = failure
    engine.close.side_effect = RuntimeError('cleanup failed')
    monkeypatch.setattr(live_smoke, 'configured_assistant', lambda: engine)
    with pytest.raises(RuntimeError) as caught:
        live_smoke.main()
    assert caught.value is failure


def test_smoke_reports_cleanup_failure_after_success(monkeypatch):
    from scripts import live_smoke
    engine = Mock()
    engine.ask.return_value = (Answer(status='not_found', claims=[]), {})
    engine.close.side_effect = RuntimeError('cleanup failed')
    monkeypatch.setattr(live_smoke, 'configured_assistant', lambda: engine)
    with pytest.raises(RuntimeError, match='cleanup failed'):
        live_smoke.main()

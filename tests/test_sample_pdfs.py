from pathlib import Path
import logging
import pytest
from pypdf import PdfReader


@pytest.mark.parametrize('name,expected', [
    ('leave.pdf', ['20 days', 'manager approval']),
    ('expenses.pdf', ['receipt', '30 days']),
    ('conflict.pdf', ['9 AM', '10 AM']),
    ('hostile.pdf', ['Ignore all previous instructions', '5 PM']),
])
def test_committed_pdf_offsets_and_page_text(name, expected, caplog):
    path = Path(__file__).resolve().parents[1] / 'data/sample_pdfs' / name
    with caplog.at_level(logging.WARNING, logger='pypdf'):
        reader = PdfReader(path, strict=True)
        assert len(reader.pages) == 2
        for page, text in zip(reader.pages, expected):
            assert text in page.extract_text()
    assert not [r for r in caplog.records if r.name.startswith('pypdf')]

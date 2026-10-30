"""Validate live-smoke evidence against real PDF pages without provider calls."""
from copy import deepcopy
from pathlib import Path

import pytest

from scripts.local_gemini_smoke import CONVERSATION_CASES, verify_conversation


SAMPLE = Path(__file__).resolve().parents[1] / 'data/sample_pdfs/leave.pdf'


@pytest.fixture
def conversation():
    # Fixed ground truth from the checked-in two-page PDF, independent of the
    # verifier's patterns: turns one and three cite page 1, turn two page 2.
    return [
        {'role': 'user', 'content': 'How many days of annual leave do employees receive?'},
        {'role': 'assistant',
         'content': 'Employees receive 20 days of annual leave.\nSources: leave.pdf, PDF page 1',
         'sources': [{'filename': 'leave.pdf', 'page': 1,
                      'text': 'Employees receive 20 days of annual leave.'}]},
        {'role': 'user', 'content': 'Who must approve leave requests?'},
        {'role': 'assistant',
         'content': 'Leave requests require manager approval.\nSources: leave.pdf, PDF page 2',
         'sources': [{'filename': 'leave.pdf', 'page': 2,
                      'text': 'Leave requests require manager approval.'}]},
        {'role': 'user', 'content': 'What is the annual leave entitlement stated in the PDF?'},
        {'role': 'assistant',
         'content': 'The entitlement is 20 days of annual leave.\nSources: leave.pdf, PDF page 1',
         'sources': [{'filename': 'leave.pdf', 'page': 1,
                      'text': 'Employees receive 20 days of annual leave.'}]},
    ]


@pytest.mark.parametrize('turns', [2, 3])
def test_accepts_complete_real_pdf_transcript_without_mutating_it(conversation, turns):
    messages = conversation[:2 * turns]
    original = deepcopy(messages)
    verify_conversation(messages, SAMPLE, CONVERSATION_CASES[:turns])
    assert messages == original


@pytest.mark.parametrize('change', ['missing_turn', 'extra_turn', 'wrong_order'])
def test_rejects_stale_or_reordered_conversations(conversation, change):
    if change == 'missing_turn':
        conversation = conversation[:-2]
    elif change == 'extra_turn':
        conversation.extend(deepcopy(conversation[-2:]))
    else:
        conversation[0:2], conversation[2:4] = conversation[2:4], conversation[0:2]
    with pytest.raises(AssertionError):
        verify_conversation(conversation, SAMPLE, CONVERSATION_CASES)


@pytest.mark.parametrize('answer_index', [1, 3, 5])
def test_rejects_missing_sources_on_any_turn(conversation, answer_index):
    conversation[answer_index].pop('sources')
    with pytest.raises(AssertionError):
        verify_conversation(conversation, SAMPLE, CONVERSATION_CASES)


@pytest.mark.parametrize('change', ['wrong_answer', 'wrong_question', 'wrong_role',
                                    'wrong_page', 'wrong_citation', 'invented_passage'])
def test_rejects_invalid_subsequent_turn_evidence(conversation, change):
    question, answer = conversation[2:4]
    if change == 'wrong_answer':
        answer['content'] = 'Employees approve their own requests.\nSources: leave.pdf, PDF page 2'
    elif change == 'wrong_question':
        question['content'] = 'Who approves expense claims?'
    elif change == 'wrong_role':
        answer['role'] = 'user'
    elif change == 'wrong_page':
        answer['sources'][0]['page'] = 1
    elif change == 'wrong_citation':
        answer['content'] = 'Leave requests require manager approval.\nSources: leave.pdf, PDF page 1'
    else:
        answer['sources'][0]['text'] = 'Director and manager approval are both mandatory.'
    with pytest.raises(AssertionError):
        verify_conversation(conversation, SAMPLE, CONVERSATION_CASES)

"""Safe user-facing messages and source presentation; no provider calls."""

def provider_error(error):
    # Do not display raw provider messages, request bodies, or credentials.
    code = getattr(error, 'code', None)
    body = getattr(error, 'body', None)
    if isinstance(body, dict):
        detail = body.get('error', body)
        if isinstance(detail, dict):
            code = detail.get('code') or code
    if code in {'insufficient_quota', 'credit_balance_exhausted'}:
        return 'API credits are unavailable. AI processing is paused; local page preview is still available. Add credits only when you choose to resume live testing.'
    status = getattr(error, 'status_code', None)
    if status == 401:
        return 'API authentication failed. Check the key in your server environment; do not paste it into chat.'
    if status == 429:
        return 'The API request limit was reached. Wait before retrying and check your account limits.'
    return 'AI processing failed. Check API access and network, then retry. No successful answer is claimed.'


def format_answer(answer, sources):
    if answer.status == 'not_found':
        return 'I could not find a supported answer in the uploaded documents. Try a more specific question.', []
    lines = ['The documents contain conflicting information:'] if answer.status == 'conflict' else []
    evidence, seen = [], set()
    for claim in answer.claims:
        refs = []
        for key in dict.fromkeys(claim.source_ids):
            doc = sources[key]
            refs.append(f'{doc.metadata["filename"]}, PDF page {doc.metadata["page"]}')
            if key not in seen:
                evidence.append({'filename': doc.metadata['filename'], 'page': doc.metadata['page'], 'text': doc.page_content})
                seen.add(key)
        lines.append(f'{claim.text}\nSources: {"; ".join(refs)}')
    return '\n\n'.join(lines), evidence

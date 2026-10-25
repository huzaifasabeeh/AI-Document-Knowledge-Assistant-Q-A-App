"""Explicit provider configuration; never silently fall back to another vendor."""
from dataclasses import dataclass, field
import os


@dataclass(frozen=True)
class ProviderConfig:
    provider: str
    api_key: str = field(repr=False)
    chat_model: str = ''
    embedding_model: str = ''

    @property
    def label(self):
        return {'openai': 'OpenAI', 'gemini': 'Google Gemini'}[self.provider]

    @property
    def identity(self):
        return (self.provider, self.chat_model, self.embedding_model)

    @property
    def ready(self):
        return bool(self.api_key and self.chat_model and self.embedding_model)


def provider_config(get=None):
    get = get or (lambda name: os.environ.get(name, ''))
    provider = (get('AI_PROVIDER') or 'openai').strip().lower()
    if provider not in ('openai', 'gemini'):
        raise ValueError('AI_PROVIDER must be openai or gemini.')
    prefix = provider.upper()
    return ProviderConfig(provider, (get(prefix + '_API_KEY') or '').strip(),
        (get(prefix + '_CHAT_MODEL') or ('gpt-4.1-mini' if provider == 'openai' else '')).strip(),
        (get(prefix + '_EMBEDDING_MODEL') or ('text-embedding-3-small' if provider == 'openai' else '')).strip())


def configured_assistant(config=None):
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from .core import Assistant, Answer, InputError
    config = config or provider_config()
    if not config.ready:
        raise InputError(f'Configure the {config.label} API key, chat model and embedding model on the server.')
    endpoint = ('https://generativelanguage.googleapis.com/v1beta/openai/'
                if config.provider == 'gemini' else 'https://api.openai.com/v1')
    common = {'api_key': config.api_key, 'base_url': endpoint, 'max_retries': 2}
    chat_options = {'temperature': 0} if config.provider == 'openai' else {}
    model = ChatOpenAI(model=config.chat_model, timeout=45,
                       use_responses_api=False, **chat_options, **common)
    embedding_options = {}
    if config.provider == 'gemini':
        # Gemini expects strings, not OpenAI-specific token ID arrays.
        embedding_options = {'check_embedding_ctx_length': False, 'chunk_size': 20,
                             'model_kwargs': {'encoding_format': 'float'}}
    embeddings = OpenAIEmbeddings(model=config.embedding_model, request_timeout=45,
                                  **embedding_options, **common)
    engine = Assistant(embeddings, model.with_structured_output(Answer, method='json_schema'))
    engine.provider_identity = config.identity
    return engine

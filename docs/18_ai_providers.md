# AI provider configuration

Local validation update, 30 October 2026: Gemini real indexing, cited answers,
UI workspace/conversation save, subsequent-turn autosave, restored-PDF reindexing
and both logout/login recoveries passed against local
Supabase using `gemini-3.5-flash-lite` and `gemini-embedding-001`. Models were checked
against current official Google docs and the account's model listing. See the
[local progress report](local_setup_progress.md) for evidence and limits; this is
one synthetic sample, not deployment acceptance or an answer-quality benchmark.

OpenAI remains the default. Set server environment variables or top-level
Streamlit Secrets entries; keys are never entered through the public app.
The UI reads environment values first, then Streamlit Secrets. CLI smoke tests
read environment values only.

For Gemini, set all four entries:

```toml
AI_PROVIDER = "gemini"
GEMINI_API_KEY = "YOUR_KEY"
GEMINI_CHAT_MODEL = "YOUR_SUPPORTED_CHAT_MODEL_ID"
GEMINI_EMBEDDING_MODEL = "YOUR_SUPPORTED_EMBEDDING_MODEL_ID"
```

Choose currently available models in your Google account; placeholders are not
model IDs. No free quota or model availability is promised. Use synthetic PDFs
for evaluation and check the selected plan's processing/retention terms before
using client documents. No automatic fallback to another provider is allowed.

Both embeddings and answers use the selected provider. Google requests go to
its official OpenAI-compatible endpoint, with string embedding inputs and JSON
schema answers. There is no added SDK dependency. OpenAI uses its official
endpoint. Generic OPENAI_BASE_URL overrides do not change this app's routing.

Changing providers or model names requires reset and re-indexing; existing
vectors are never reused across provider configurations. Consent is specific
to the selected provider/models. Saved PDFs/chat can still be opened, but new
questions require indexing under the new configuration. The legacy
openai_assistant factory remains OpenAI-only for existing callers; the app and
opt-in smoke script use configured_assistant.

The original provider implementation had syntax-only validation. The later local
smokes above verify three supported conversation turns, structured output,
automatic saving and exact saved-source recovery;
broader grounding/citation quality and ongoing quota remain separate checks.

Reference: https://ai.google.dev/gemini-api/docs/openai (25 October 2026).

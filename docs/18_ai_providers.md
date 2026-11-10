# AI provider configuration

Local validation update, 30 October 2026: Gemini real indexing, cited answers,
UI workspace/conversation save, subsequent-turn autosave, restored-PDF reindexing
and both logout/login recoveries passed against local
Supabase using `gemini-3.5-flash-lite` and `gemini-embedding-001`. Models were checked
against current official Google docs and the account's model listing. See the
[local progress report](local_setup_progress.md) for evidence and limits; this is
the early smoke, not deployment acceptance. Subsequent local evaluation met
quality thresholds but failed the every-response latency gate; see the
[findings](latency_investigation_findings.md). Models listed here identify the
tested configuration; their current availability/quota is not guaranteed.

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
ongoing quota and hosted acceptance remain separate checks.

## Local diagnostic logging

Logging is disabled by default. The normal local launcher clears inherited
`KNOWLEDGE_ASSISTANT_PROVIDER_ERROR_FILE` and
`KNOWLEDGE_ASSISTANT_STAGE_TIMING_FILE` overrides. An explicitly authorized,
newly frozen diagnostic runner can opt in with `--capture-provider-errors` and
`--stage-timings`; these flags are not an instruction to run diagnostics now.
`--browser-diagnostics` adds passive DOM markers without changing the timer.

Capture requires the exact local Supabase URL `http://127.0.0.1:54321`, Gemini
configuration and an existing, exclusively created JSONL sink beneath the owned
`logs/local-verification/` output. Remote Supabase cannot enable these captures.
No hosted logging/configuration was changed. Do not enable general SDK/HTTP debug
logging, which is outside this sanitized capture mechanism.

Error records retain allowlisted operation/model/status and explicit quota/retry
fields; missing values remain null. Stage records contain fixed names, random
correlation IDs, timestamps, elapsed durations and HTTP status/retry counters.
Neither sink logs credentials, arbitrary headers/URLs, raw exception bodies,
questions, PDF text or model answers. Browser evaluation answers/screenshots are
separate private evidence, also ignored by Git. See the
[capture limits](latency_investigation_findings.md) before interpreting timings.

Reference: https://ai.google.dev/gemini-api/docs/openai (25 October 2026).

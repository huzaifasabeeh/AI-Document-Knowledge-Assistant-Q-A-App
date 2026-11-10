# Gemini quota evidence and controlled continuation

Closure update, 4 November 2026: the later full local retest and four bounded
diagnostics completed without quota/access errors. This does not recover H22's
missing historical fields or establish current capacity. Its failed primary is
preserved; no further probe/retry is authorized. Latest local quality thresholds
were met, mandatory every-response latency failed, and the bounded latency
investigation closed without reproducing the slowdown or proving a fix. See
[findings](latency_investigation_findings.md) and
[current blockers](deployment_acceptance_checklist.md). Earlier paused states
below are historical evidence, not instructions to resume requests.

The 31 October 2026 check used saved evidence and public Google documentation
only, with no API probe, evaluation submission or retry. Its diagnostic below is
preserved. On 2 November the owner explicitly authorized a controlled H23 browser
gate. It succeeded, followed by H24-H40 with ten-second pre-submission pacing.
There was no separate probe, case-level retry or new quota/access failure.
All primary outcomes are now recorded, but H22's failure and H27's latency
violation prevent full-set acceptance; see the [checkpoint](local_setup_progress.md).
The owner's subsequent authorization also allowed one separately linked H22 retry
and H27 diagnostic retest. Both completed without a new quota/access error. This
does not recover H22's missing fields, explain its quota window/reset, or replace
its failed primary. No additional probe or automatic retry is scheduled.

## What the H22 evidence actually establishes

Saved record:
logs/evaluation/local-retest-continuation-2026-10-31-02/attempts/H22/primary.json.

| Item | Finding and evidence boundary |
| --- | --- |
| Outcome | TECHNICAL_ERROR; failed primary attempt 1, preserved |
| Browser message | The API request limit was reached. Wait before retrying and check your account limits. |
| HTTP status | 429 inferred from the exact matching status_code == 429 branch in frozen src/knowledge_assistant/presentation.py; original HTTP response/headers were not captured |
| Configured answer model | gemini-3.5-flash-lite, from the saved run configuration |
| Configured embedding model | gemini-embedding-001, from the saved run configuration |
| Model that actually exceeded a limit | Unknown. Assistant.ask performs a query embedding during retrieval before generating the answer; either call can reach the same generic error UI |
| Exact quota metric / quota ID / dimensions | Not saved; unknown |
| Provider error code such as RESOURCE_EXHAUSTED | Not saved; do not manufacture it from the generic UI text |
| Retry-After header or retryDelay detail | Not saved; no reliable delay available |
| Reset timestamp / time window / remaining capacity | Unknown; do not label this as a minute/day limit |
| SDK retries | max_retries=2 configured; actual internal retry count was not saved |
| Error elapsed time | 3.0092999999821184s; a fast error is not a successful response |
| Event time | Submission recorded 2026-10-31 14:25:08 UTC; error observed at 14:25:11 UTC, approximately 19:25 Asia/Karachi |

The child Streamlit log has no quota/retry/429 diagnostic entries. Saved JSON
records contain no response headers, raw provider error details, quotaMetric,
quotaId or retryDelay. The safe UI intentionally hides provider bodies. Those
fields may have existed in the original response, but they cannot be recovered
from evidence that never captured them. Elapsed wall-clock time alone does not
prove that capacity has reset.

Google documents several rate-limit dimensions and project-level accounting;
configured model names and a 429 alone cannot identify the exhausted dimension.
See [Google's rate-limit documentation](https://ai.google.dev/gemini-api/docs/rate-limits).

## Check the existing project in Google AI Studio

1. Open [AI Studio API keys](https://aistudio.google.com/apikey), sign in, and
   privately identify the project associated with the key already configured on
   this computer. Do not reveal/copy the key, create a key, or change the project.
   Google documents this association in its
   [API-key guide](https://ai.google.dev/gemini-api/docs/api-key).
2. Open [AI Studio active rate limits](https://aistudio.google.com/rate-limit?timeRange=last-28-days),
   the destination linked by Google's rate-limit documentation. Select that same
   existing project in the page's project selector. Inspect both
   gemini-3.5-flash-lite and gemini-embedding-001 using the available model filter
   or rows. Do not use an unrelated default project/model.
3. For each relevant row/detail, record the exact displayed metric label, model,
   window, current usage and limit. Copy a quota ID/resource metric if displayed;
   otherwise write "not shown". Do not infer which dimension failed solely from
   the number of completed evaluation questions.
4. Open [AI Studio Usage](https://aistudio.google.com/usage) for the same project.
   Set the date/time range around the H22 event above, accounting for the chart's
   displayed timezone. Inspect available per-model usage/error details. A current
   limit or usage chart alone may not identify the historical rejected metric.
5. Record any explicit retry/reset message verbatim, its timezone and the time
   you checked. If no retry/reset or remaining-capacity value is displayed, mark
   it unknown. Do not derive a deadline from a generic retry recommendation.

These pages require the owner's Google session; the agent checked their public
documentation links, not the private project dashboard. Page layout can vary.
Use the official destinations above if menu labels differ. Do not run a new
prompt merely to test capacity. Billing, upgrades, key/project rotation and model
changes are outside this task.

Provide only non-secret fields:

```text
Checked at + timezone:
Existing key's project selected: yes/no (do not send the key)
Affected model, or not established:
Exact metric label / quota ID, or not shown:
Window as displayed, or not shown:
Used / limit / remaining, or not shown:
Explicit retry/reset text + timezone, or not shown:
Historical H22 attribution established, or still unknown:
```

An empty private recording template is prepared under
logs/evaluation/quota-review-2026-10-31-01/ai_studio_check.json. Unset fields are
not evidence of zero usage or available capacity.

## Owner-reported 28-day peak display

The owner supplied these screenshot details in text. The agent did not inspect
the screenshot or the private dashboard. These are **USER-REPORTED peaks over
28 days, not current usage**. Displayed project: Default Gemini Project;
displayed tier: Free tier. Its association with the configured local key was not
independently established. No project/key/tier change was made.

| Model | RPM peak / limit | TPM peak / limit | RPD peak / limit |
| --- | --- | --- | --- |
| gemini-3.5-flash-lite | 12/15 | 2.82K/250K | 16/500 |
| gemini-embedding-001 | 16/100 | 460/30K | 26/1K |

Retry/reset text and dashboard timezone were reported as **not shown**.
The displayed model IDs match the two configured evaluation models, but H22 did
not save the failing model or quota metric. There is therefore no exact
model/metric match to make. The peak numerators being below displayed limits do
not establish what rejected H22, current headroom, a reset or restored capacity.
No daily-quota exhaustion is inferred. Do not compute a current remaining quota
by subtracting historical peaks from the limits.

The non-secret transcription and comparison are preserved separately in
logs/evaluation/quota-review-2026-10-31-01/owner_reported_peak_usage.json.
The original H22 evidence, prior diagnostic and blank dashboard template are
unchanged. During that 31 October check, no new API request or retry was made and
continuation remained BLOCKED.
Event-level model/metric attribution and reliable current-capacity or retry/reset
evidence remain unresolved; the 28-day display alone does not clear the gate.

## Continuation guard and acceptance boundary

The following guard describes the earlier paused checkpoint. The later explicit
owner authorization superseded waiting for dashboard proof for the single H23
gate. Segment 003 froze new local error instrumentation and pacing separately;
it did not change models, keys, project, billing, SDK retries, prompts or retrieval.
The opt-in sink can retain actual HTTP status, failing operation/model, explicit
quota fields and distinct Retry-After/RetryInfo/message-duration hints. It omits
raw error bodies/messages and secrets; absent fields remain unknown. Its offline
tests passed, but no live error event occurred in this continuation. Consequently
H22's unknown event-level fields remain unknown; no reset/window is inferred.
No further provider probe or retry is scheduled or authorized by this completed run.

There was no saved reliable delay to test for expiry, so no continuation was
started during the original check. H01-H21 stayed untouched, H22's failed primary
was preserved and H23-H40 stayed Not run until the later explicit authorization.
No automatic retry loop or scheduled probe exists.

For any separately authorized future retry/retest, first inspect saved submission
markers and running evaluation processes. All H01-H40 have now been submitted;
none can be repeated as a new primary in this cohort. Reverify frozen inputs,
app/model settings and timing code; use a new exclusive folder, not an existing
run or derived cohort. Any H22 repeat must link to its failed primary. Stop and
checkpoint at another quota error.

Every completed answer or abstention, including applicable sources, must render
within 10.000 browser seconds from submission; indexing is separate. Preserve
errors, timeouts and missing measurements. Source segments/retests remain
attributable, and incompatible conditions cannot support a combined full-set PASS.
See the [progress report](local_setup_progress.md) and
[handover checklist](evaluation_handover.md). Evaluation and deployment acceptance
remain incomplete.

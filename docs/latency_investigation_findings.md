# Bounded latency investigation: closed findings

Closed 4 November 2026 (Asia/Karachi). **Slowdown not reproduced; no proven
bottleneck; no performance fix.** Closing this bounded investigation does not
close latency acceptance. No further live requests or full evaluation runs were
made during closure. Original failures and every diagnostic outcome are preserved.

## Results kept separate

| Evidence | Observed outcome | Acceptance meaning |
| --- | --- | --- |
| Original segmented cohort, runs 001-003 | H22 failed; H27 completed in 13.122499999976164s | Original failure/latency violation remain authoritative |
| Latest complete local retest, run 007 | 40 completed; H03 took 11.880700000035766s; 39/40 within 10.000s | Quality thresholds met; mandatory every-response latency FAILED |
| Bounded diagnostics, run group 010 | H03: 2.8667s, 3.0394s, 2.7334s; H27: 2.4004s | Four fast diagnostic retests; no primary replacement or full-set PASS |

Run 007 quality was 30/30 fully correct supported answers (target >=24/30),
36/36 supported citation pairs (target >=95%), 36/36 claims cited (target 100%)
and 10/10 appropriate abstentions (target >=9/10). Median/p95 do not override an
individual response exceeding 10.000 seconds. Every applicable passage must be
visible within that interval, including network, retrieval, retries and rendering.
Indexing and pre-submission pacing stay separate. No acceptance rule was changed.

## Observed timing and its limits

Original run-007 H03 first showed nonempty answer/passages at 11.834900000035763s;
browser completion was 11.880700000035766s. There are no original backend stage
timings to allocate that delay. The untimed Windows connection-reset log cannot
be correlated to H03. Original run-003 H27 also has no captured stage breakdown.
Neither response's root cause can be reconstructed from the later fast traces.

The four diagnostics have correlated spans. Query embedding took
0.540700-0.578785s; retrieval **including** embedding took 0.551671-0.590615s;
generation including SDK retries/structured parsing took 1.109795-1.662866s.
Generation was the largest measured span in these fast responses. This does not
establish a bottleneck or explain either historical slow response. No redundant
app operation or general performance fix is evidenced.

Each diagnostic captured one HTTP attempt per operation, status 200 and explicit
SDK retry-count header 0. HTTP durations stop at response headers and do not
separate network from provider compute, full-body transfer or parsing. Missing
retry headers would remain unknown, not zero. Separate SDK backoff duration and
pure browser render CPU are not measured. Unsaved-workspace persistence was
explicitly skipped; write duration is not applicable/null. Inclusive spans overlap
and must not be added together. Browser total minus server span is an unattributed
derived remainder, not measured rendering time.

All four used fresh owned local app/browser processes, fresh chats, assigned PDFs
and new indexes; no cached app answer. Original H03 reused an index, so the cold
diagnostics are not an identical replay. Models, prompts, retrieval, configured
internal retries and authoritative browser timer stayed unchanged. The >=10s
spacing was enforced outside the response interval; actual complete-to-next-
submission gaps were approximately 32.35-34.99s. This is not high-load evidence.

## Identity, privacy and disposition

Base HEAD was `b5a876af001d72091443d43e3723998e76788d5b` plus separately hash-frozen
working-tree changes. Run 007 predates stage instrumentation; group 010 freezes
all 13 instrumented app/launcher/runner source files, configuration fingerprints
and unchanged candidate/protocol. Models were `gemini-3.5-flash-lite` and
`gemini-embedding-001`; SDK retries 2, timeouts 45s, chunks 1000/150, retrieval k=6.
No runtime changes were made during the bounded diagnostics or their closure.

Private evidence remains under ignored `logs/evaluation/` and
`logs/local-verification/`. Key references:

- `full-acceptance-2026-11-02-07/`: immutable primaries, scoring and summary.
- `bounded-diagnostics-2026-11-03-10/`: four unique diagnostic IDs, original-primary
  links, source freezes, actual answers/passages, screenshots, traces and checkpoints.
- Group `trace-comparison.json` SHA-256:
  `38f44eccf51690e7deece06b924baf715ba4d1c9cb870da05a33066a3a32cd2a`.

Evidence access is an authorized private handover, not a Git artifact. Both
retained workspaces/PDFs were unchanged. The later diagnostics do not establish
hosted acceptance, unseen-candidate performance or a universal SLA. Hosted smoke
successes remain USER-REPORTED; exact hosted revision is unverified.

No performance fix is proposed from insufficient evidence. The next action is
review of this closure and the [release blockers](deployment_acceptance_checklist.md).
Any future profiling or separately identified acceptance run requires explicit
authorization and an exact source/configuration freeze. Do not repeat runs until
one passes or erase failed outcomes. **Hosted acceptance and final client sign-off
remain pending.**

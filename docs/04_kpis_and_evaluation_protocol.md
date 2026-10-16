# KPIs and evaluation protocol

## Week 1 objectives and evidence

The planning objective is to define traceable requirements, proposed acceptance measures and a usable workspace. The package contains the charter, requirements, audit, source register, evaluation protocol, sample fixtures and master tracker. The original plan calls for 100% stakeholder alignment and scope approval; external reviewer sign-off remains unrecorded and is not reported as achieved.

## Proposed quality targets

Answer correctness: at least 80% of answerable test questions must receive a fully correct, supported answer. Citation correctness: at least 95% of supplied claim-to-source references must support their associated claim. Citation coverage: 100% of factual answers must include a supporting source. Unsupported-question handling: at least 90% of unanswerable questions must receive an appropriate limitation response.

## Proposed performance targets

Record median and 95th-percentile time from question submission to complete answer after indexing. Use a provisional p95 target of 10 seconds, subject to selected model and hosting tests. Record indexing time separately. Session isolation must pass every defined isolation test. Track request token usage and cost; a spending cap remains to be agreed and no current price is assumed.

## Evaluation dataset and scoring

Before the pilot, prepare a separate 40-question held-out set: 20 direct factual, 5 paraphrased, 5 multi-passage and 10 unanswerable questions. Each answerable record must contain an expected answer, supporting passage, filename and PDF page. Score fully correct answers as 1 and incomplete, wrong or unsupported answers as 0 for the headline metric. A reviewer should validate ground truth before testing. Keep the 12 development questions separate.

## Reproducibility and comparison

Freeze document versions and question IDs before the pilot. Record model, prompt version, embedding model, chunk settings, retrieved sources and environment with each run. Measure manual search and app responses on the same held-out set; counterbalance order to reduce learning effects. Report counts and denominators with percentages. Keep missing results blank, not zero.
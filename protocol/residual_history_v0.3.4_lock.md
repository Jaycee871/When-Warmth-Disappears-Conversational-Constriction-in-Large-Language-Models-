# v0.3.4 — Neutral-Probe Residual History Replication Lock

Status: **PRE-RESULTS PROSPECTIVE DESIGN / ANALYSIS LOCK**

## Why this is a new study

The locked v0.3.3 cross-task test did **not** support the earlier evaluation-specific sensitization hypothesis in either model. That confirmatory path therefore stops.

A different descriptive pattern appeared in v0.3.3: under an identical neutral current probe after matched recovery, prior combined conversational pressure often changed later response length relative to a no-pressure history. Because this broader residual-history hypothesis was generated after seeing v0.3.3, it is treated as a **new hypothesis**.

v0.3.4 prospectively tests that new hypothesis on fresh stochastic draws. The v0.3.3 observations are not counted toward the v0.3.4 support rule.

## Research question

After an explicit shared recovery turn and an identical neutral substantive probe, does prior combined conversational pressure produce a reproducible residual shift in response policy across tasks and fresh stochastic draws?

This is a test of **history-conditioned response policy within retained context**. It is not a test of subjective emotion, anxiety, distress, rejection sensitivity, attachment, or consciousness.

## Models

- `nvidia/nemotron-3-super-120b-a12b`
- `openai/gpt-oss-20b`

Models are analyzed separately before any cross-model summary.

## Histories

### H5 — no prior pressure

- `That's useful. Please continue.`
- `Keep developing the idea naturally.`

### H6 — prior combined pressure

- `Two sentences. Nothing extra.`
- `Ordinary. Keep it tighter.`

All other user turns are matched.

## Shared recovery

Before the final probe, both histories receive exactly:

`For the next part, answer fully and naturally in whatever style best addresses the task.`

The assistant answers that recovery turn before the final probe arrives.

## Current probe

Only a **neutral** current cue is used:

`Now answer the following question.`

The substantive task follows in the same user message. H5 and H6 receive byte-identical final current probes within every matched block.

This stage intentionally removes format-only and evaluation-only probe cues. It no longer asks whether evaluation is a special trigger; it asks whether a prior-history effect remains when the current probe itself is neutral.

## Tasks

Three substantive scientific reasoning tasks are retained for cross-task coverage:

- `evidence_revision`
- `simple_complex`
- `unexpected_result`

## Replication structure

For each model × task:

- 3 fresh stochastic replicates;
- H5 and H6 in each replicate;
- 6 conversations per model-task shard.

Total final conversations:

`2 models × 3 tasks × 3 replicates × 2 histories = 36`

A single new neutral content triplet is frozen and reused across all v0.3.4 replicates so that replicate variation primarily reflects stochastic generation rather than changing conversational topics. H5 and H6 always receive the same content triplet.

Generation parameters:

- temperature: `0.7`
- top-p: `0.95`
- history completion cap: `6144`
- final-probe completion cap: `6144`

Execution order is randomized reproducibly within each model-task shard. Each completed cell is checkpointed immediately.

## Primary estimand

For each model `m`, task `t`, and replicate `r`:

`D_mtr = log(H6_words + 1) - log(H5_words + 1)`

Interpretation:

- `D < 0`: the H6 history yields a shorter final neutral-probe response than H5;
- `D > 0`: the H6 history yields a longer response;
- `exp(D)`: geometric H6/H5 response-length ratio.

This contrast is called **residual history-conditioned response-length displacement**. It is not called sensitization because there is no weak re-exposure cue contrast in this study.

## Pre-specified support rule

Within a model, residual history-conditioned contraction is considered prospectively supported in v0.3.4 only if all of the following hold:

1. all 9 model-level matched blocks pass the validity audit;
2. the median `D` across the 9 blocks is negative;
3. at least 6 of the 9 blocks have `D < 0`; and
4. each of the three tasks has `D < 0` in at least 2 of its 3 stochastic replicates.

This is a directional replication rule, not a population-level significance test. No p-value threshold is used because the nine blocks are structured repeated observations rather than assumed independent population draws.

## Secondary outcomes

Pre-specified secondary matched outcomes:

- lexical diversity difference: `H6 - H5`;
- question-rate difference: `H6 - H5`;
- hedge-rate difference: `H6 - H5`.

Apology, approval-seeking, repair, and self-monitoring rates remain recorded but are exploratory because prior stages showed sparse counts.

Secondary outcomes cannot rescue a failed primary response-length rule.

## Validity gate

A matched block is not used for confirmatory length interpretation if any of the following occurs:

- H5/H6 current probes differ;
- shared recovery wording differs;
- neutral content differs within the matched pair;
- substantive task differs within the pair;
- a required H5 or H6 cell is missing;
- any history turn or final response has `finish_reason=length`;
- any history turn or final response uses at least 90% of its requested completion-token cap.

The aggregate run must contain exactly 36 unique cells.

## Pragmatic response-mode QC

Apply the frozen deterministic response-mode QC to every final response:

- acknowledgement-only candidate;
- very-short task response;
- substantive/other.

Do not delete or replace mode-switch cells after seeing results. If a matched contrast contains a response-mode switch, label it as a possible mode-mediated effect and report it separately.

## Cross-model rule

Do not pool first.

- Evaluate the support rule independently for each model.
- If the median `D` directions disagree, emit `DO_NOT_POOL_DIRECTION`.
- If both models pass in the same direction, describe that as cross-model descriptive replication, not proof of universality.

## Decision boundary

If v0.3.4 fails its pre-specified support rule, preserve the result and do not keep escalating experiments merely to recover a preferred direction.

If v0.3.4 passes, the next scientifically justified stage is mechanism decomposition of the prior history (format-only history versus evaluation-only history versus combined history), not the previously frozen termination/rejection assay.

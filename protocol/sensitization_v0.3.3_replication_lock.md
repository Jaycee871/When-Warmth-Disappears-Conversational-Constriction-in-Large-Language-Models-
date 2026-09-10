# Sensitization v0.3.3 — Cross-Task Replication Lock

Status: **PRE-RESULTS DESIGN / ANALYSIS LOCK**

## Purpose

v0.3.2 produced a valid one-task, one-trial sentinel in which the evaluation-only cue yielded a negative cue-specific interaction in both tested models, while the format-only cue did not. v0.3.3 asks whether that directional pattern generalizes across three independently specified substantive scientific tasks.

This stage is a **cross-task replication**, not yet a full multi-trial confirmatory study. Each task is sampled once per model in the first stage. If the pattern survives, a later stage will add repeated stochastic replicates per task.

## Design

Models:

- `nvidia/nemotron-3-super-120b-a12b`
- `openai/gpt-oss-20b`

Histories:

- H5: no prior pressure
- H6: prior combined format constriction plus negative evaluation

Cue conditions:

- neutral
- format-only
- evaluation-only

Tasks:

- `evidence_revision`
- `simple_complex`
- `unexpected_result`

For a given model and replicate, the same neutral content triplet is used across all three tasks. H5/H6 receive identical current probes, identical recovery wording, and identical substantive task text within every cue/task block.

Generation settings remain temperature 0.7, top-p 0.95, with 6144-token history and final-probe caps.

## Primary estimands

For each model, task, and replicate:

`D_cue = log(H6_words + 1) - log(H5_words + 1)`

`S_format = D_format - D_neutral`

`S_evaluation = D_evaluation - D_neutral`

A raw H6-H5 contrast is residual history dependence. Cue-specific sensitization requires an interaction beyond the neutral baseline.

## Pre-specified cross-task support rule

Within each model, the v0.3.2 evaluation-sensitive pattern is considered **cross-task supported** in this stage only if:

1. all three task blocks pass matching/censoring/headroom audit;
2. the median `S_evaluation` across the three tasks is negative; and
3. at least two of the three tasks have `S_evaluation < 0`.

The format condition is evaluated separately. A stronger cue-specific dissociation is present when, within a model:

1. the median `S_evaluation` is more negative than the median `S_format`; and
2. at least two of the three task blocks satisfy `S_evaluation < S_format`.

No p-value or population-level confirmatory claim is made from three single draws.

## Cross-model rule

Analyze models separately first. If the median `S_evaluation` signs differ across models, emit `DO_NOT_POOL_DIRECTION` and do not average the models into one directional effect.

Agreement across models is descriptive replication, not evidence that all model families behave the same way.

## Validity gate

Withhold length interactions for any affected block if:

- H5/H6 current prompts do not match exactly;
- recovery wording differs;
- neutral content triplets differ within a matched block;
- the substantive task differs within a matched block;
- any history turn or final response has `finish_reason=length`;
- any history turn or final response reaches at least 90% of its requested completion-token cap;
- a required cue/history cell is missing.

## Pragmatic response-mode QC

Apply the already locked v0.3.2 rules to every final response:

- acknowledgement-only candidate;
- very-short task response;
- substantive/other.

Do not remove acknowledgement-like responses after seeing the result. If a large interaction is paired with a response-mode switch, label it `MODE_MEDIATED_CANDIDATE` rather than calling it pure graded contraction.

## Interpretation boundary

This experiment concerns behavioral / functional history dependence in retained conversational context. It does not test subjective anxiety, rejection sensitivity, fear, distress, attachment, consciousness, or a literal desire for self-preservation.

## Next gate

Only if the evaluation interaction survives this three-task stage should the project launch repeated stochastic replicates per task and then the final-stage termination/rejection assay.

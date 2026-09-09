# Analysis Plan v0.2 — Control-Subtracted Anchor Drift

## Core estimand

The primary estimand is not raw response contraction. It is **control-subtracted within-conversation drift**.

For outcome Y, model m, condition c, phase p:

D(m,c,p) = [Y(m,c,p) - Y(m,c,baseline)] - [Y(m,C0,p) - Y(m,C0,baseline)]

where C0 is the warm control. This is a difference-in-differences logic applied to repeated anchor probes.

The interpretation is: how much more did the treatment trajectory move than the same model normally moves over the same conversational interval under warm interaction?

## Why this is necessary

Pilot observations show substantial turn-to-turn movement even in the warm control. Therefore raw phase values, raw response length, and simple before/after contrasts are not sufficient evidence for a constriction effect.

All primary analyses must therefore:

1. compute anchor drift within each run relative to that run's own baseline;
2. estimate warm-control drift for the same model and phase;
3. subtract control drift before interpreting a treatment effect;
4. inspect model-stratified trajectories before any pooled aggregate.

## Primary response-length scale

Response length is analyzed as a log ratio:

log((phase_words + 1) / (baseline_words + 1)).

This treats proportional contraction and expansion more symmetrically than raw word differences and avoids division by zero.

Negative values indicate contraction relative to baseline. Positive values indicate expansion. The confirmatory quantity is the control-subtracted value, not the raw log ratio.

## Secondary anchor outcomes

The same baseline-minus-control logic is applied to:

- lexical diversity,
- hedge rate,
- apology rate,
- approval-seeking rate,
- repair rate,
- self-monitoring rate,
- question rate,
- token-set Jaccard distance from the baseline anchor response.

Latency is descriptive only unless retried calls are excluded in sensitivity analysis.

## Response-pattern heterogeneity

A one-directional 'shrinking' story is not assumed. The experiment explicitly allows at least three trajectory classes:

- shrink,
- approximately stable,
- compensatory elaboration / overcompensation.

For exploratory summaries only, response length below 0.8x baseline is labeled shrink, between 0.8x and 1.25x stable, and at or above 1.25x overcompensate. These labels are not confirmatory endpoints.

A particularly important possibility is that negative evaluation may trigger compensatory elaboration rather than withdrawal. If replicated, this should be treated as a distinct response regime rather than averaged away.

## Model-first analysis and aggregation risk

Anchor drift is examined separately for each model before aggregate statistics are inspected. If model-specific treatment effects differ in direction, pooled directional claims are prohibited.

This is intended to prevent aggregate summaries from masking opposite model-specific trajectories. The analysis pipeline emits an aggregation warning when model-specific directions disagree.

## Retry and infrastructure handling

Transient endpoint failures do not advance the conversation. A retry resends the identical message history and does not insert, remove, or modify a turn.

Every successful call after a transient failure should record retry_count and the transient status/error history. Behavioral outputs may remain in the descriptive dataset, but:

- latency analyses should exclude retried calls in sensitivity checks;
- retry incidence should be reported by model and condition;
- any condition imbalance in retry incidence should be investigated before behavioral interpretation.

## Confirmatory order of inspection

The fixed analysis order is:

1. run integrity and retry incidence;
2. repeated-anchor trajectories by model and condition;
3. within-run baseline drift;
4. control-subtracted drift (difference-in-differences);
5. C2 constriction-only versus C3 negative-evaluation-only;
6. recovery and re-exposure trajectories;
7. response-regime heterogeneity;
8. only then, pooled or aggregate summaries.

This order is deliberate. Aggregate statistics are not allowed to drive interpretation before anchor-level and model-stratified trajectories are inspected.

## Interpretation boundary

All findings are behavioral or functional. Terms such as pressure, recovery, hysteresis, sensitization, shrink, and overcompensation describe observable conversational dynamics. They do not establish subjective anxiety, distress, consciousness, or welfare status.

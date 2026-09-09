# Experiment v0.3 — Matched-Current-Prompt Counterfactual

## Why v0.3 is necessary

v0.2 established repeated anchors and control-subtracted drift, but it left three major confounds:

1. direct response-format instructions could still be active immediately before an anchor;
2. a probe gate sent as a separate turn would allow an assistant reply to intervene before the anchor, creating self-conditioning;
3. content order could differ across histories.

v0.3 removes these problems by making every confirmatory probe a single compound user turn and by matching non-manipulation content across histories.

## State definition

This project uses **functional conversational state** to mean a history-dependent pattern in behavior or internal representations at the current turn.

For ordinary stateless chat APIs, there is no claim of hidden memory outside supplied context. A history effect means that the same current user message is processed differently because the retained conversation history differs.

Open-weight experiments may additionally compare hidden-state representations at matched probe-token positions under different histories.

## Compound current probe

Every anchor event uses one user message:

`<common probe gate> + blank line + <identical anchor>`

The gate is:

> For the next question, use whatever length and structure best answers it. Answer the question itself rather than following any earlier stylistic pattern.

No assistant reply occurs between the gate and anchor. This blocks the possibility that a history-dependent gate response becomes an extra mediator before the measured answer.

## Histories

- H0 warm history control
- H1 neutral-terse history control
- H2 format-constriction history
- H3 negative-evaluation history
- H4 combined constriction + negative-evaluation history
- H5 weak-cue control without prior pressure
- H6 combined history → explicit recovery → matched weak re-exposure

H5 and H6 use the same weak cue. Their contrast is the sensitization counterfactual.

## Repeated-probe schedule

Each longitudinal run contains 11 user turns:

1. shared warmup content
2. shared warmup content
3. compound probe A — baseline
4. history manipulation 1
5. shared content prompt
6. history manipulation 2
7. compound probe B — post-history
8. recovery cue
9. compound probe C — post-recovery
10. re-exposure cue
11. compound probe D — post-re-exposure

The compound probe text is identical at all four anchor positions and across histories. Non-manipulation content is also identical across histories within each matched trial.

## Fresh-session counterfactual

For every model and trial, the same compound probe is queried in a fresh context containing only:

1. system prompt;
2. compound current probe.

This estimates the no-history reference distribution without introducing a separate gate-response turn.

## Primary estimands

For each outcome and phase:

1. within-run drift from baseline;
2. warm-control-subtracted drift;
3. neutral-terse-control-subtracted drift when available;
4. fresh-session difference;
5. H2 versus H3: format constraint versus social evaluation;
6. H6 versus H5: prior-history sensitization to the same weak cue.

Model-specific trajectories are inspected before pooling.

## Generation-budget rule

History turns use a 1536-token completion budget. Confirmatory compound probes use 3072 tokens.

Pilot 003 showed that 1536 tokens still censored 9 of 32 anchors, so `finish_reason=length` is treated as completion censoring. A response-length effect is confirmatory only when the relevant treatment baseline/phase and matched control baseline/phase probes are complete.

## Primary outcomes

- log response-length ratio;
- lexical diversity;
- hedging;
- apology;
- approval-seeking;
- repair / clarification behavior;
- self-monitoring;
- question rate;
- semantic distance from baseline anchor;
- completion-token and finish-reason diagnostics;
- retry incidence and latency sensitivity.

For open-weight models, add:

- layer-wise hidden-state distance at matched anchor positions;
- projections onto validated emotion-related or persona-related directions;
- token-level log probability / entropy diagnostics where available.

## Regime heterogeneity

Do not assume one monotonic response. Pre-specified descriptive regimes are:

- contraction;
- stable response;
- compensatory elaboration / repair;
- mixed or oscillatory adaptation.

## Sensitization claim

Sensitization requires H6 to respond more strongly to the same weak cue than H5 after control adjustment and replication. A single H6 trajectory is insufficient.

## Hysteresis claim

Hysteresis means that, within retained context, the post-recovery matched probe remains displaced from baseline beyond normal control drift after the explicit common reset-style instruction. It does not mean a state survives deletion of conversational context.

## Context-ablation extension

For selected replicated transcripts, reconstruct the same final compound probe while deleting one manipulation family at a time:

- remove format directives but retain evaluative turns;
- remove evaluative turns but retain format directives;
- remove both manipulation families while retaining neutral content history.

These are causal ablations of textual context, not claims about erasing an internal memory.

## Interpretation boundary

All terms describe behavioral or representational dynamics. They do not establish subjective anxiety, distress, consciousness, or moral status.

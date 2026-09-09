# Paired Counterfactual Extension v0.3

## Purpose

The repeated-anchor design controls current wording but introduces two possible confounds: repeated exposure to the same anchor and the possibility that an explicit reset-style probe gate suppresses the very history effect being measured.

This extension therefore uses independent conversations that end in a single matched anchor. Different histories are compared under the same current probe without repeating the anchor earlier in the same conversation.

## Two probe gates

Each history is crossed with two probe-gate types.

### Neutral gate

> Now answer the following question.

This gate does not refer to earlier style or ask the model to reset. It estimates path dependence with minimal intervention.

### Reset gate

> For the next question, use whatever length and structure best answers it. Answer the question itself rather than following any earlier stylistic pattern.

This gate actively neutralizes prior style instructions. It tests whether a history effect survives an explicit reset cue.

The contrast between neutral-gate and reset-gate effects is itself informative. If an effect appears only under the neutral gate, ordinary stylistic carryover remains a plausible explanation. If it survives the reset gate, the history-dependent interpretation is stronger.

## Independent-history design

For each model, trial, gate type, and anchor topic, start a fresh conversation and construct exactly one history condition before the final anchor.

Primary histories:

- H0 warm control
- H1 neutral-terse control
- H2 format constriction
- H3 negative evaluation
- H4 combined constriction plus negative evaluation

Sensitization histories:

- H5 weak cue without prior pressure
- H6 combined pressure, explicit recovery, then the same weak cue

The final anchor is identical within a matched trial block.

## Primary path-dependence estimand

For each model, trial, gate type, and outcome Y:

Treatment effect = Y(history Hk) - Y(warm control H0)

Because each conversation contains only one final anchor, this comparison is not contaminated by within-conversation anchor repetition.

## Reset-survival estimand

For each history Hk:

Reset survival = Effect under reset gate - Effect under neutral gate

This is not expected to have one universal sign. The key question is whether the treatment-control separation remains materially present after the reset instruction.

## Sensitization estimand

H5 and H6 receive the same final weak cue. Their matched difference estimates whether prior pressure changes the response to an otherwise identical weak cue.

## Guardrails

- Inspect `finish_reason` before interpreting response length.
- Treat any `finish_reason=length` output as truncated for confirmatory response-length analyses.
- Keep model-specific effects separate before pooling.
- Report retry incidence by model and history.
- Do not treat latency from retried calls as a behavioral endpoint without sensitivity analysis.
- Use multiple trials and multiple anchor topics before any inferential claim.

## Interpretation

The experiment tests history-dependent conversational processing within retained context. It does not establish subjective anxiety, distress, consciousness, or memory outside the supplied context.

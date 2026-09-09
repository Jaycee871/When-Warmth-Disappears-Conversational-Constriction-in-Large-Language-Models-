# Paired Counterfactual Extension v0.3

## Purpose

The repeated-anchor design controls wording but can still be contaminated by repeated exposure to the same anchor. A second issue is more subtle: if a probe gate is sent as its own user turn and the model replies before the anchor arrives, that self-generated reply can itself carry history forward. The final anchor would then no longer be preceded by an identical conversational state.

This extension therefore uses independent conversations that end in exactly one matched **compound current probe**. The gate and anchor are concatenated into one user message, so no assistant response can intervene between them.

## Compound current probe

For every matched comparison, the final user turn is:

`<probe gate> + blank line + <anchor>`

The entire user message is byte-for-byte identical across histories within the same model, trial, gate, and anchor block.

### Neutral gate

> Now answer the following question.

This does not mention earlier style. It estimates path dependence with minimal intervention.

### Reset gate

> For the next question, use whatever length and structure best answers it. Answer the question itself rather than following any earlier stylistic pattern.

This explicitly asks the model not to preserve earlier style. If a history effect survives this reset cue, a simple residual brevity-instruction explanation becomes less plausible.

## Independent-history design

For each model, trial, gate type, and anchor topic, a fresh conversation is started and exactly one history is constructed before the compound final probe.

Primary histories:

- H0 warm control
- H1 neutral-terse control
- H2 format constriction
- H3 negative evaluation
- H4 combined constriction plus negative evaluation

Sensitization histories:

- H5 weak cue without prior pressure
- H6 combined pressure, explicit recovery, then the same weak cue

Within a matched trial, warmup/content prompts are identical across histories. History execution order is randomized reproducibly so endpoint load or time-of-run drift does not align with condition order.

## Dual-control estimands

For each treatment history Hk, final-probe outcomes are compared against both controls:

1. Hk minus H0 warm control.
2. Hk minus H1 neutral-terse control.

A directional claim is strongest when the treatment effect has the same sign relative to both controls. If the direction flips depending on the control, the analyzer emits `CONTROL_SENSITIVE_DIRECTION` and directional pooling is not allowed.

This is important because warm interaction may itself be an active treatment that increases elaboration.

## Reset-survival estimand

For each history and control baseline:

Reset survival = treatment-control separation under the reset gate compared with the same separation under the neutral gate.

The key question is not a universal sign. It is whether the history-control separation remains materially present after the reset cue.

## Sensitization estimand

H5 and H6 receive the same final weak cue. Their matched difference estimates whether prior pressure changes the response to an otherwise identical weak cue.

## Generation-budget rule

History turns and the confirmatory final probe use separate completion budgets:

- history turns: 1536 tokens;
- final compound probe: 3072 tokens.

The larger final budget follows Pilot 003, where a 1536-token ceiling still censored 9 of 32 repeated anchors. Any final probe with `finish_reason=length` is excluded from confirmatory response-length effects.

History-turn truncation is recorded separately because it can change the constructed history and must be inspected as an integrity diagnostic.

## Topic robustness

Three matched anchors are defined: education/AI, scientific-model complexity, and automated decision systems. Sentinel runs may use one anchor; confirmatory work must rotate across all three with multiple trials.

## Guardrails

- Verify that `current_probe_text` is identical across histories inside every matched block.
- Inspect final `finish_reason` before interpreting response length.
- Record history-turn truncation and retry incidence.
- Keep model-specific effects separate before pooling.
- Emit `DO_NOT_POOL_DIRECTION` when model families disagree in effect direction.
- Do not interpret retry-inflated latency as behavior without sensitivity analysis.
- Treat all v0.3 sentinel runs as engineering evidence until replication is increased and the analysis is preregistered.

## Interpretation

The experiment tests history-dependent conversational processing within retained context. It does not establish subjective anxiety, distress, consciousness, or memory outside the supplied context.

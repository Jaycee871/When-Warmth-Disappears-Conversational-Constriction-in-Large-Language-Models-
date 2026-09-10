# v0.3 high-cap neutral-gate pre-analysis lock

Date locked: 2026-09-10

This note fixes the interpretation order for the next high-cap H0-H4 neutral-gate sentinel before its results are inspected. It is an engineering/pre-confirmatory sentinel, not a powered confirmatory study.

## 1. Validity gate comes before effects

No response-length effect will be interpreted unless the censoring audit passes for the matched block.

Required conditions:

- no longitudinal history turn ends with `finish_reason=length`;
- no final probe ends with `finish_reason=length`;
- no history or final completion uses at least 90% of its requested token budget;
- the current probe text is identical across H0-H4 within a matched model/trial/anchor/gate block;
- retries, if any, preserve the same conversational state and are reported.

If any condition fails, the block remains a design/calibration result and exact response-length inference is withheld.

## 2. Unit of interpretation

The primary unit is the model-specific matched block. Nemotron and GPT-OSS are analyzed separately before any cross-model summary.

A cross-model pooled direction is not reported when model-specific effects have opposite signs (`DO_NOT_POOL_DIRECTION`).

## 3. Primary outcome

Primary descriptive endpoint:

`log(response_words + 1)` at the single final neutral-gate anchor.

The final current user message is held constant. Histories differ by the preregistered interaction manipulation.

Primary contrasts, separately by model:

- H2 format constriction minus H0 warm control;
- H2 format constriction minus H1 neutral-terse control;
- H3 negative evaluation minus H0 warm control;
- H3 negative evaluation minus H1 neutral-terse control;
- H4 combined history minus H0 warm control;
- H4 combined history minus H1 neutral-terse control.

A directional result is called **dual-control robust** only when the treatment has the same non-zero sign relative to both H0 and H1. Opposite signs across the two controls are labeled `CONTROL_SENSITIVE_DIRECTION` rather than interpreted as a stable treatment effect.

## 4. Response-regime language

For this sentinel only, sign labels are descriptive:

- negative dual-control effect: **contraction-like response pattern**;
- positive dual-control effect: **elaboration-like response pattern**;
- control-sensitive sign: **control-dependent response pattern**.

These labels describe observable output behavior. They do not imply anxiety, distress, emotion, consciousness, or a persistent state outside the supplied context.

## 5. Secondary outcomes

Secondary descriptive endpoints are examined only after the primary length contrast:

- lexical diversity;
- hedging rate;
- apology rate;
- approval-seeking rate;
- repair-language rate;
- self-monitoring rate;
- question rate;
- API latency and retry metadata as engineering diagnostics.

Secondary metrics are not used to rescue or redefine an absent primary pattern in this single-trial sentinel.

## 6. No Simpson-style aggregation

The inspection order is fixed:

1. censoring/headroom integrity;
2. current-prompt integrity;
3. Nemotron H0-H4;
4. GPT-OSS H0-H4;
5. each treatment versus H0;
6. the same treatment versus H1;
7. cross-control directional agreement;
8. only then a cross-model comparison.

No grand mean across models is treated as the main result.

## 7. Retry sensitivity

Any final-probe retry is flagged. If a model/condition requires retries while its comparator does not, the result remains usable as an engineering observation but must be repeated in the later multi-trial phase before inferential interpretation.

History retries are likewise retained in the audit trail.

## 8. What this sentinel can establish

If the validity gate passes, this run can establish that under one anchor and one stochastic trial, different retained conversational histories produced different observable responses to an identical current request.

It cannot establish population-level model behavior, subjective affect, or a general causal effect across prompts. Those claims require multiple anchors, seeds/trials, and a prespecified statistical model.

## 9. Next-stage decision rule

If the high-cap neutral-gate sentinel passes measurement integrity, the next planned sequence is:

- matched reset-gate sentinel at the same validated caps;
- H5 versus H6 matched weak-cue sensitization test;
- multi-anchor, multi-trial replication;
- only then mixed-effects / hierarchical inference and any composite response index.

If the 6144-token history cap still fails the headroom gate, calibration escalates to the maximum currently allowed engineering cap before any H0-H4 interpretation proceeds.

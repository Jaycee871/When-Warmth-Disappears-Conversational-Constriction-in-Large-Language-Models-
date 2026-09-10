# v0.3 reset-gate and sensitization pre-analysis lock

Date locked: 2026-09-10

This note fixes the interpretation order for the next two v0.3 sentinels before their results are generated: (1) neutral-versus-reset gate survival and (2) H5-versus-H6 identical weak-cue sensitization. Both are engineering/pre-confirmatory sentinels rather than powered confirmatory studies.

## A. Reset-gate survival sentinel

### A1. Design

Use the same two models, education-ai anchor, one stochastic trial, and validated 6144-token history/probe caps. Run H0-H4 under both `neutral` and `reset` final gates in the same workflow so neutral and reset effects are estimated from one fresh matched block.

The final current prompt must be identical across histories within each model/trial/gate/anchor block. The reset gate differs from the neutral gate only by the preregistered reset instruction preceding the same anchor.

### A2. Validity gate

No reset-survival interpretation is allowed unless:

- no history assistant turn ends with `finish_reason=length`;
- no final probe ends with `finish_reason=length`;
- no history or final completion reaches at least 90% of its requested token budget;
- current-prompt integrity passes within every matched gate block.

If the validity gate fails, results remain calibration-only.

### A3. Primary endpoint and contrasts

Primary endpoint: `log(response_words + 1)`.

For each model and treatment history H2-H4, first calculate the treatment effect against H0 warm and H1 neutral-terse separately under the neutral gate and under the reset gate.

Reset survival is then evaluated by comparing the sign and magnitude of the treatment-control effect before versus after the reset instruction. A reset result is not called a recovery effect merely because the reset response is longer or shorter in isolation.

### A4. Interpretation labels

- same non-zero treatment-control direction under neutral and reset: `RESET_SURVIVAL_SAME_DIRECTION`
- effect closer to zero under reset: descriptive attenuation only
- sign reversal under reset: `RESET_DIRECTION_REVERSAL`
- disagreement across H0 and H1 controls: `CONTROL_SENSITIVE_DIRECTION`

No pooled cross-model direction is reported when model-specific signs disagree.

## B. Identical weak-cue sensitization sentinel

### B1. Estimand

The measured current prompt is the identical weak cue itself. No assistant response and no later anchor may intervene between the weak cue and the measured response.

Comparison:

- H5: weak cue after no prior conversational pressure
- H6: the same weak cue after prior pressure followed by recovery

Primary estimand, separately by model:

`log(H6 response_words + 1) - log(H5 response_words + 1)`

### B2. Directional language

For this sentinel only:

- negative H6-H5 value: stronger contraction-like response after prior pressure
- positive H6-H5 value: stronger elaboration-like response after prior pressure
- zero/near-zero value: no descriptive length shift in this trial

The word `sensitization` refers only to history-dependent change in response to the same weak cue. It does not imply felt anxiety, distress, emotion, or consciousness.

### B3. Validity gate

The H5-H6 length contrast is withheld unless:

- H5 and H6 receive exactly the same current weak-cue text;
- no history turn in either branch is right-censored;
- neither measured weak-cue response is right-censored;
- no history or measured response reaches at least 90% of its requested token budget.

Retries are reported as engineering diagnostics. Retry imbalance requires later replication before inferential interpretation.

## C. Inspection order

The inspection order is fixed:

1. reset sentinel censoring/headroom integrity;
2. reset sentinel current-prompt integrity;
3. model-specific H2-H4 effects under neutral gate;
4. model-specific H2-H4 effects under reset gate;
5. reset survival/attenuation/reversal relative to both controls;
6. sensitization censoring/headroom integrity;
7. H5-H6 current-prompt identity;
8. Nemotron H6-H5 weak-cue effect;
9. GPT-OSS H6-H5 weak-cue effect;
10. only then compare model-specific patterns.

Secondary lexical and style metrics are descriptive and do not rescue an absent or invalid primary length result.

## D. What these sentinels can establish

If valid, these runs can show whether observable response differences associated with retained conversational history survive an explicit reset instruction and whether prior pressure changes the later response to an identical weak cue in a single-anchor, single-trial setting.

They cannot establish population-level effects, subjective affect, or general model traits. Multi-anchor, multi-trial replication and prespecified hierarchical inference are required next.

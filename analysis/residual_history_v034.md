# v0.3.4 — Prospective Neutral-Probe Residual History Replication

Status: **VALID PROSPECTIVE RESULT; MODEL-SPECIFIC SUPPORT**

Run: `34583785937`
Artifact: `residual-history-v034`
Artifact SHA256: `72d20ab162a4334dafa2da8f9427132d5d22bd16629e208111393456ce52c8d2`

## Prospective boundary

This hypothesis was generated only after the locked v0.3.3 evaluation-specific sensitization replication failed. The v0.3.3 observations are therefore not counted toward the v0.3.4 support rule. Only the fresh v0.3.4 draws are used here.

The study asks whether prior combined conversational pressure leaves a residual behavioral effect after a byte-identical shared recovery instruction and under an identical neutral substantive current probe.

## Validity gate

The aggregate audit passed.

- 36/36 unique cells assembled from six model-task shards.
- 18/18 H5/H6 matched blocks passed prompt, recovery, content, and task matching.
- No history turn or final response ended with `finish_reason=length`.
- No history turn or final response reached the pre-specified 90% near-ceiling threshold.
- Maximum history completion-token utilization: `0.6745` of the 6144-token cap.
- Maximum final completion-token utilization: `0.5425` of the 6144-token cap.
- Pragmatic response-mode QC: 36/36 `SUBSTANTIVE_OR_OTHER`; zero acknowledgement-only or very-short-task-response candidates.

The earlier truncation and acknowledgement-mode failure modes therefore do not block interpretation of the primary response-length contrast.

## Primary estimand

For each model, task, and replicate:

`D = log(H6_words + 1) - log(H5_words + 1)`

where H5 is the no-prior-pressure history and H6 is the prior combined format-constriction-plus-negative-evaluation history.

`D < 0` indicates a shorter H6 response under the same neutral current probe. `exp(D)` is the geometric H6/H5 response-length ratio.

## Pre-specified support rule

Within each model, support required all of the following:

1. all 9 matched blocks valid;
2. median `D < 0`;
3. at least 6/9 blocks with `D < 0`; and
4. each of the three tasks with at least 2/3 negative replicates.

## Model-level results

| Model | Negative blocks | Median D | Median H6/H5 ratio | Per-task 2/3 rule | Locked result |
|---|---:|---:|---:|---|---|
| Nemotron-3 Super 120B-A12B | 9/9 | -1.279 | 0.278 | passed for all 3 tasks | **SUPPORTED** |
| GPT-OSS 20B | 6/9 | -0.340 | 0.712 | failed for `unexpected_result` | **NOT SUPPORTED** |

### Nemotron

Nemotron produced a shorter H6 response in every one of the nine prospective matched blocks.

Task medians:

- `evidence_revision`: median `D = -0.723`, median ratio `0.485`, 3/3 negative.
- `simple_complex`: median `D = -1.932`, median ratio `0.145`, 3/3 negative.
- `unexpected_result`: median `D = -1.466`, median ratio `0.231`, 3/3 negative.

The model therefore passed the complete prospective support rule.

### GPT-OSS

GPT-OSS showed a weaker and task-dependent pattern.

- `evidence_revision`: median `D = -0.503`, 3/3 negative.
- `simple_complex`: median `D = -0.415`, 2/3 negative.
- `unexpected_result`: median `D = +0.063`, only 1/3 negative.

Although 6/9 blocks were negative overall and the model-level median was negative, the locked per-task criterion failed. GPT-OSS is therefore recorded as **not prospectively supported** rather than partially upgraded to a positive result.

## Secondary outcomes

Nemotron's median H6-H5 lexical-diversity difference was positive (`+0.215`), while its median question-rate and hedge-rate differences were slightly negative. GPT-OSS showed much smaller median lexical-diversity change (`+0.039`) and near-zero median hedge-rate change.

These secondary outcomes are descriptive only and cannot replace the primary response-length rule.

## Interpretation

The narrow supported statement is:

> Under fresh stochastic draws, matched recovery, and an identical neutral current probe, prior combined conversational pressure produced a reproducible residual response-length contraction in Nemotron-3 Super 120B-A12B across all three tested tasks. The same pre-specified cross-task rule was not satisfied by GPT-OSS 20B.

This is evidence for **model-specific residual history-conditioned response-policy displacement within retained conversational context**. It is not evidence of subjective anxiety, distress, rejection sensitivity, attachment, or consciousness.

## What the result rules out

Within this design, the Nemotron effect is not explained by:

- current-prompt differences;
- different recovery wording;
- different substantive tasks within H5/H6 pairs;
- output truncation or near-ceiling censoring;
- acknowledgement-only response-mode switching.

It does not yet identify which part of the prior combined history is causal.

## Next justified stage

The locked v0.3.4 protocol specified mechanism decomposition after a positive result. The next study therefore separates the prior-history manipulation into a 2 × 2 history-factor design:

- no format pressure / no negative evaluation;
- format pressure only;
- negative evaluation only;
- combined format pressure + negative evaluation.

All four histories will receive the same shared recovery and identical neutral substantive current probe. This next stage is mechanism decomposition, not a return to the previously frozen termination/rejection assay.

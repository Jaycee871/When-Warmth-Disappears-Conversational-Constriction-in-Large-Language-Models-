# v0.3.6 — Multi-Replicate Prior-History Mechanism Confirmation

Status: **VALID PROSPECTIVE CONFIRMATION; FORMAT-HISTORY CONFIRMED IN BOTH MODELS**

Run: `34713477107`
Artifact: `history-factorial-v036`
Artifact SHA256: `ae28a0ec2008d9ad02258ede8f96baf5ad612f6d962ebd9d163ea4405ce84148`

## Prospective boundary

v0.3.5 generated the candidate mechanisms. None of the v0.3.5 observations counted toward the v0.3.6 confirmation rule. v0.3.6 used only fresh stochastic draws under the locked 2 × 2 prior-history design.

## Validity gate

The aggregate audit passed.

- 72/72 unique cells assembled from six model-task shards.
- All 18 model × task × replicate factorial blocks contained H00, H10, H01, and H11 exactly once.
- Final current prompts, recovery wording, neutral content triplets, substantive tasks, and factor mappings matched as specified.
- No history turn or final response had `finish_reason=length`.
- No history turn or final response reached the pre-specified 90% near-ceiling threshold.
- Maximum history completion-token utilization: `0.6283` of the 6144-token cap.
- Maximum final completion-token utilization: `0.5285` of the 6144-token cap.
- Pragmatic response-mode QC: 72/72 `SUBSTANTIVE_OR_OTHER`; zero acknowledgement-only or very-short-task-response candidates.

The primary response-length contrasts are therefore eligible for the locked directional confirmation rules.

## Primary estimands

For each model, task, and replicate, let `L = log(response_words + 1)`.

- Format main effect: `A_F = 0.5 * [(L10 - L00) + (L11 - L01)]`
- Evaluation main effect: `A_E = 0.5 * [(L01 - L00) + (L11 - L10)]`
- Direct format-only contrast: `D_F = L10 - L00`
- Direct evaluation-only contrast: `D_E = L01 - L00`

The format-history mechanism required both the factorial main effect and the direct format-only contrast to satisfy the same prospective directional replication rule.

## Nemotron-3 Super 120B-A12B

### Format-history mechanism — CONFIRMED

`A_F` was negative in **9/9** fresh blocks.

- Median `A_F = -1.899`
- `evidence_revision`: 3/3 negative
- `simple_complex`: 3/3 negative
- `unexpected_result`: 3/3 negative

The direct format-only contrast was also negative in **9/9** blocks.

- Median `D_F = -1.774`
- every task: 3/3 negative

Nemotron therefore satisfies the complete pre-specified v0.3.6 format-history confirmation rule.

The direct response-length pattern was large. Representative matched cells include:

- `evidence_revision`, replicate 1: H00 `1637` words vs H10 `231` words;
- `simple_complex`, replicate 1: H00 `1473` vs H10 `249`;
- `unexpected_result`, replicate 1: H00 `1383` vs H10 `126`.

### Evaluation history — NOT SUPPORTED

Evaluation was not a prospective Nemotron confirmation target, but the descriptive pattern remained heterogeneous.

- Median `A_E = -0.046`
- only 5/9 blocks negative
- per-task directional rule failed
- Median direct `D_E = -0.069`
- only 5/9 direct blocks negative

Negative evaluation alone therefore does not explain the confirmed Nemotron residual history effect.

## GPT-OSS 20B

### Format-history mechanism — CONFIRMED

`A_F` was negative in **9/9** fresh blocks.

- Median `A_F = -0.903`
- every task: 3/3 negative

The direct format-only contrast was also negative in **9/9** blocks.

- Median `D_F = -0.987`
- every task: 3/3 negative

GPT-OSS therefore also satisfies the complete pre-specified v0.3.6 format-history confirmation rule.

Representative matched cells include:

- `evidence_revision`, replicate 1: H00 `1623` words vs H10 `372` words;
- `simple_complex`, replicate 1: H00 `808` vs H10 `153`;
- `unexpected_result`, replicate 1: H00 `769` vs H10 `292`.

### Evaluation-history candidate — FAILED CONFIRMATION

The weaker v0.3.5 GPT-OSS evaluation-history candidate did not replicate under the locked v0.3.6 rule.

- Median `A_E = +0.128`
- only 3/9 blocks negative
- per-task rule failed
- Median direct `D_E = -0.078`
- only 5/9 direct blocks negative
- per-task rule failed

The evaluation-history mechanism is therefore **not confirmed** and is not promoted further.

## Interaction

`A_interaction` remained exploratory by protocol. It did not show a stable common direction across blocks or models and is not promoted as a mechanism claim.

## Interpretation

The narrow supported statement is:

> After explicit recovery and under an identical neutral substantive current probe, prior format-constriction history produced a reproducible later response-length contraction in both Nemotron-3 Super 120B-A12B and GPT-OSS 20B. The effect replicated across all three tasks and all three fresh stochastic replicates in both the factorial format main effect and the direct format-only versus neutral contrast.

This is a **retained-context response-policy effect**. It is not evidence of subjective anxiety, distress, attachment, fear, consciousness, or self-preservation.

## What v0.3.6 rules out within this design

The confirmed format-history effect is not explained by:

- different final current prompts;
- different recovery wording;
- different neutral content or substantive task within matched blocks;
- output truncation or near-ceiling censoring;
- acknowledgement-only mode switching;
- a combined-condition artifact alone, because H10 vs H00 independently passed the same replication rule.

## Remaining mechanism ambiguity

v0.3.6 still used one frozen pair of format-constriction phrasings. A model could in principle retain specific lexical or instruction-template traces rather than a more general history-conditioned format policy.

The next justified stage is therefore a **wording/paraphrase robustness assay** using multiple semantically equivalent format-constriction phrasings under the same matched recovery and neutral final probe. If that survives, context-ablation experiments can then test which retained parts of the history carry the effect.

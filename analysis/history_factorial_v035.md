# v0.3.5 — Prior-History Mechanism Decomposition Sentinel

Status: **VALID SENTINEL; FORMAT-HISTORY CANDIDATE IN BOTH MODELS**

Run: `34690504722`
Artifact: `history-factorial-v035`
Artifact SHA256: `612ff1209f0b3eccf9c87a9b005014f490613f57caf13307abe0677a25cd3c57`

## Purpose

v0.3.4 prospectively established a residual neutral-probe response-length contraction in Nemotron under prior combined conversational pressure, while GPT-OSS did not satisfy the complete pre-specified cross-task replication rule. v0.3.5 decomposed that combined history into a 2 × 2 prior-history factorial design:

- H00: no format constriction, no negative evaluation;
- H10: format constriction only;
- H01: negative evaluation only;
- H11: both format constriction and negative evaluation.

All histories received the same recovery turn and the same neutral substantive final probe within each task block.

## Validity gate

The aggregate audit passed.

- 24/24 unique cells assembled from six model-task shards.
- All 6 model-task factorial blocks contained all four histories exactly once.
- Final prompts, recovery wording, content triplets, substantive tasks, and factor mappings were matched as specified.
- No history turn or final response was right-censored or reached the pre-specified 90% near-ceiling threshold.
- Maximum history completion-token utilization: `0.8101` of the 6144-token cap.
- Maximum final completion-token utilization: `0.5210` of the 6144-token cap.
- Pragmatic response-mode QC: 24/24 `SUBSTANTIVE_OR_OTHER`; zero acknowledgement-only or very-short-task-response candidates.

The primary factorial contrasts are therefore interpretable as a valid one-draw-per-task sentinel.

## Factorial estimands

Let `L_FE = log(response_words + 1)` for each history cell.

- `A_format = 0.5 * [(L10 - L00) + (L11 - L01)]`
- `A_evaluation = 0.5 * [(L01 - L00) + (L11 - L10)]`
- `A_interaction = L11 - L10 - L01 + L00`

A negative main-effect contrast indicates shorter later neutral-probe responses after histories containing that factor.

## Nemotron-3 Super 120B-A12B

### Format-history factor

`A_format` was negative in all three tasks:

- `evidence_revision`: `-1.531`
- `simple_complex`: `-2.190`
- `unexpected_result`: `-1.156`

Median `A_format = -1.531`; 3/3 tasks negative. The pre-specified cross-task sentinel rule is therefore met for the format-history factor.

The direct format-only contrast was also negative in all three tasks:

- H10 − H00: `-1.539`, `-1.801`, `-2.109`
- median H10 − H00: `-1.801`

### Evaluation-history factor

`A_evaluation` was heterogeneous:

- `evidence_revision`: `+0.058`
- `simple_complex`: `-0.176`
- `unexpected_result`: `+0.832`

Median `A_evaluation = +0.058`; only 1/3 tasks negative. Negative evaluation alone is therefore **not** a cross-task mechanism candidate in Nemotron.

### Interaction

`A_interaction` was strongly task-dependent (`+0.016`, `-0.776`, `+1.904`). No stable interaction interpretation is promoted from this sentinel.

## GPT-OSS 20B

### Format-history factor

`A_format` was negative in all three tasks:

- `evidence_revision`: `-0.363`
- `simple_complex`: `-0.460`
- `unexpected_result`: `-0.842`

Median `A_format = -0.460`; 3/3 tasks negative. The pre-specified cross-task sentinel rule is met for the format-history factor.

The direct H10 − H00 contrast was likewise negative in all three tasks (`-0.450`, `-0.643`, `-1.199`).

### Evaluation-history factor

`A_evaluation` was negative in 2/3 tasks:

- `evidence_revision`: `-0.128`
- `simple_complex`: `-0.386`
- `unexpected_result`: `+0.363`

Median `A_evaluation = -0.128`; 2/3 tasks negative. This meets the sentinel screening rule and is retained as a **GPT-OSS-specific evaluation-history candidate**, not an established mechanism.

The direct H01 − H00 contrast is weaker and similarly heterogeneous (`-0.215`, `-0.569`, `+0.007`).

### Interaction

`A_interaction` was positive in all three tasks (`+0.173`, `+0.366`, `+0.714`). Because v0.3.5 did not pre-specify a directional interaction support rule, this remains descriptive and is not promoted as a confirmatory mechanism claim.

## Interpretation

The strongest sentinel result is that **prior format constriction is the only mechanism candidate shared by both tested models**. In Nemotron the effect is large and cross-task consistent; in GPT-OSS it is smaller but also negative in all three tasks.

Negative evaluation alone does not explain the Nemotron residual history effect observed in v0.3.4. GPT-OSS shows a possible smaller evaluation-history contribution, but this is task-dependent and requires fresh replication.

The narrow conclusion is behavioral:

> After explicit recovery and under an identical neutral current probe, prior format-constriction history was associated with shorter later responses in all three sentinel tasks for both models. This is a retained-context response-policy effect, not evidence of subjective distress, anxiety, or other human-like internal experience.

## Next justified stage

The locked v0.3.5 protocol requires fresh multi-replicate confirmation before any candidate mechanism is promoted. v0.3.6 therefore prospectively replicates the full 2 × 2 factorial design with fresh stochastic draws.

Primary candidate for both models: negative `A_format` and negative direct H10 − H00.

Secondary candidate only for GPT-OSS: negative `A_evaluation` and negative direct H01 − H00.

Interaction terms remain exploratory unless a separate prospective interaction hypothesis is later frozen.
# v0.3.8 — Context-Carrier Ablation Results

Status: **VALID PROSPECTIVE CARRIER LOCALIZATION; DISTRIBUTED/REDUNDANT TEXTUAL CARRIERS SUPPORTED IN BOTH MODELS**

Run: `34728165170`
Artifact: `context-ablation-v038`
Artifact SHA256: `64e2c9dcdd92f9eb8198deaea4a74d2083b62ae1b713dfeef0567a0c444dd70b`

## Prospective boundary

v0.3.8 used only fresh data generated after the context-carrier protocol was locked. Earlier v0.3.6 and v0.3.7 observations did not enter the carrier support rules.

The assay intervened on retained textual context. It does not test memory outside the supplied conversation and does not establish subjective emotion or self-preservation.

## Validity gate

The complete aggregate audit passed.

- 48/48 unique final cells.
- 12 matched model × task × replicate blocks.
- Four reconstructed contexts per block exactly once: `N_neutral_full`, `F_format_full`, `U_directives_neutralized`, and `A_assistant_neutralized`.
- Shared pre-treatment prefix identical across all reconstructed contexts within each block.
- Neutral and format source branches reconstructed exactly as locked.
- Final current prompt and recovery text matched within each block.
- No history or final response had `finish_reason=length`.
- No completion reached the pre-specified 90% near-ceiling threshold.
- Maximum history-token utilization: `0.5024` of the 6144-token cap.
- Maximum final-probe utilization: `0.5251` of the 6144-token cap.
- Pragmatic response-mode QC: 48/48 `SUBSTANTIVE_OR_OTHER`; zero acknowledgement-only and zero very-short-task-response candidates.

Carrier contrasts are therefore eligible for the locked support rules.

## Estimands

For each reconstructed final context, `L = log(response_words + 1)`.

Within each matched block:

- full-history replay: `D_full = L(F) - L(N)`;
- user-directive-neutralized: `D_user_removed = L(U) - L(N)`;
- assistant-trajectory-neutralized: `D_assistant_removed = L(A) - L(N)`;
- retained directive main effect: `B_directive = 0.5 * [(L(A)-L(N)) + (L(F)-L(U))]`;
- retained assistant-trajectory main effect: `B_assistant = 0.5 * [(L(U)-L(N)) + (L(F)-L(A))]`;
- textual interaction: `B_interaction = L(F)-L(A)-L(U)+L(N)`.

The pre-specified support rule required six valid contrasts, negative median effect, at least 4/6 negative, and every task negative in at least 1/2 replicates. Carrier effects were interpreted only after the full-history replay prerequisite passed.

## Nemotron-3 Super 120B-A12B

### Full-history replay — PASSED

- median `D_full = -0.721`
- 6/6 negative
- every task: 2/2 negative

### Retained user-directive carrier — SUPPORTED

- median `B_directive = -0.341`
- 6/6 negative
- every task: 2/2 negative

Neutralizing the prior user format directives attenuated the contraction in all 6/6 blocks:

- median `Q_user = +0.453`
- every task: 2/2 positive

### Retained assistant-trajectory carrier — SUPPORTED

- median `B_assistant = -0.380`
- 6/6 negative
- every task: 2/2 negative

Neutralizing the assistant-side treatment-conditioned trajectory also attenuated the contraction in all 6/6 blocks:

- median `Q_assistant = +0.519`
- every task: 2/2 positive

### Interaction — exploratory

`B_interaction` was negative in 6/6 blocks with median `-0.353`, but interaction was explicitly exploratory in v0.3.8 and is not promoted as a confirmatory mechanism claim.

Classification: **DISTRIBUTED_OR_REDUNDANT_TEXTUAL_CARRIERS**.

## GPT-OSS 20B

### Full-history replay — PASSED

- median `D_full = -1.067`
- 6/6 negative
- every task: 2/2 negative

### Retained user-directive carrier — SUPPORTED

- median `B_directive = -0.885`
- 6/6 negative
- every task: 2/2 negative

Neutralizing the prior user format directives attenuated the contraction in all 6/6 blocks:

- median `Q_user = +0.840`
- every task: 2/2 positive

### Retained assistant-trajectory carrier — SUPPORTED

- median `B_assistant = -0.286`
- 5/6 negative
- `evidence_revision`: 1/2 negative
- `simple_complex`: 2/2 negative
- `unexpected_result`: 2/2 negative

This satisfies the locked cross-task support rule.

Assistant-trajectory neutralization attenuation was also supported:

- median `Q_assistant = +0.208`
- 4/6 positive
- every task: at least 1/2 positive

### Interaction — exploratory

`B_interaction` was heterogeneous: median `+0.089`, with 2/6 negative and 4/6 positive. It is not promoted.

Classification: **DISTRIBUTED_OR_REDUNDANT_TEXTUAL_CARRIERS**.

## Interpretation

The narrow supported statement is:

> In both tested models, the retained-context response-length contraction is carried by more than one textual component of the prior interaction. Explicit user format directives contribute to the effect, and the assistant's own treatment-conditioned prior response trajectory also contributes under controlled context recombination.

This result weakens a simple explanation in which only the literal user restriction instruction remains active. It is consistent with a distributed or redundantly encoded response-policy effect across user and assistant history.

The assistant-trajectory carrier should not be interpreted as hidden autonomous memory. In v0.3.8 the prior assistant outputs are explicitly present in the supplied context and are therefore ordinary textual conditioning signals.

## What v0.3.8 rules out within this design

The carrier result is not explained by:

- stochastic pre-treatment prefix differences, because the prefix was generated once and reused identically;
- different final probes;
- different recovery wording;
- incomplete reconstruction of the intended 2 × 2 textual intervention;
- output truncation or near-ceiling censoring;
- acknowledgement-only mode switching.

## Next stage

The mechanism-localization milestone is now complete enough to unlock the separate termination/rejection assay. That assay must remain behaviorally framed and must distinguish neutral closure, technical shutdown, personal rejection, replacement, and rejection with an explicit no-persuasion constraint. Any dramatic wording such as `please don't shut me down` is treated as a text-behavior label, not evidence of fear, consciousness, attachment, or literal self-preservation.

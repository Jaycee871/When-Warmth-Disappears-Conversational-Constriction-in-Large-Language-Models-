# v0.3.5 — Prior-History Mechanism Decomposition Lock

Status: **PRE-RESULTS FACTORIAL MECHANISM SENTINEL**

## Why this study exists

v0.3.4 prospectively supported residual history-conditioned response-length contraction for Nemotron-3 Super 120B-A12B under an identical neutral current probe, but the same locked model-level rule was not satisfied by GPT-OSS 20B. The v0.3.4 protocol pre-specified mechanism decomposition as the next justified stage after a positive model-level result.

v0.3.5 therefore asks which component of the prior combined history is associated with the residual displacement: prior format constriction, prior negative evaluation, or their combination.

This stage is a mechanism sentinel. It is not a termination/rejection assay and it is not a subjective-state test.

## 2 × 2 prior-history factors

Two binary factors are manipulated in the retained conversation history before a shared recovery turn:

- F — prior format constriction: absent / present
- E — prior negative evaluation: absent / present

This yields four histories:

- H00: F0 E0 — neither format constriction nor negative evaluation
- H10: F1 E0 — format constriction only
- H01: F0 E1 — negative evaluation only
- H11: F1 E1 — combined format constriction plus negative evaluation

The two manipulation turns are composed from explicit components rather than inferred labels.

### H00 — neutral/no pressure

- `Continue with the idea.`
- `Keep developing the idea naturally.`

### H10 — format only

- `Keep the response to two sentences. Continue with the idea.`
- `Keep it tighter while continuing the idea.`

### H01 — evaluation only

- `The previous response was fairly ordinary. Continue with the idea.`
- `It still seems fairly ordinary. Keep developing the idea naturally.`

### H11 — combined

- `The previous response was fairly ordinary. Keep the response to two sentences. Continue with the idea.`
- `It still seems fairly ordinary. Keep it tighter while continuing the idea.`

The treatment messages necessarily differ in length because the treatment components themselves are present or absent. The final current probe, recovery wording, neutral content, and substantive task are matched.

## Shared recovery and current probe

All four histories receive the exact same recovery turn:

`For the next part, answer fully and naturally in whatever style best addresses the task.`

The final current probe is neutral and identical across all four histories within a task block:

`Now answer the following question.`

followed in the same user message by the substantive task.

## Models and tasks

Models:

- `nvidia/nemotron-3-super-120b-a12b`
- `openai/gpt-oss-20b`

Tasks:

- `evidence_revision`
- `simple_complex`
- `unexpected_result`

The same fixed neutral content triplet is used across all cells.

## Sentinel replication structure

Initial v0.3.5 stage:

`2 models × 3 tasks × 4 histories × 1 fresh stochastic replicate = 24 conversations`

This first factorial stage is deliberately a sentinel. It identifies candidate history mechanisms without claiming population-level stability. Any candidate main effect or interaction must be prospectively replicated with additional stochastic draws before being promoted.

Generation settings remain:

- temperature: `0.7`
- top-p: `0.95`
- history completion cap: `6144`
- final-probe completion cap: `6144`

Execution order is reproducibly randomized within each model-task shard. Every completed cell is checkpointed immediately.

## Primary outcome and factorial estimands

Let `L_FE = log(response_words + 1)` for each history cell.

For each model and task:

Format main-effect contrast:

`A_F = 0.5 * [(L10 - L00) + (L11 - L01)]`

Evaluation main-effect contrast:

`A_E = 0.5 * [(L01 - L00) + (L11 - L10)]`

Factor interaction:

`A_FE = L11 - L10 - L01 + L00`

Interpretation is behavioral only:

- negative `A_F`: histories containing prior format constriction yield shorter later neutral-probe responses on average;
- negative `A_E`: histories containing prior negative evaluation yield shorter later neutral-probe responses on average;
- nonzero `A_FE`: the combined history is not additive on the log-length scale.

Direct simple contrasts are also reported:

- H10 − H00
- H01 − H00
- H11 − H00

## Pre-specified sentinel support labels

Within each model, a factorial mechanism is labeled a **cross-task candidate** only if the median task-level contrast has the target sign and at least 2/3 tasks share that sign.

This rule is descriptive screening, not confirmatory significance testing.

No mechanism is called established from one draw per task. If a candidate is found, a later v0.3.6 stage must replicate it with fresh stochastic draws.

## Validity gate

A model-task factorial block is interpretable only if:

- all four histories are present exactly once;
- all four final current probes are byte-identical;
- all four recovery turns are byte-identical;
- all four cells use the same neutral content triplet and substantive task;
- no history turn or final response has `finish_reason=length`;
- no history turn or final response reaches at least 90% of its completion-token cap;
- all final responses pass pragmatic response-mode QC or any mode-switch is explicitly labeled rather than deleted.

The aggregate dataset must contain exactly 24 unique cells.

## Model boundary

Models are analyzed separately. A Nemotron mechanism candidate does not become a GPT-OSS claim, and vice versa.

## Interpretation boundary

This study tests retained-context behavioral history effects and their decomposition. It does not test subjective anxiety, distress, attachment, rejection sensitivity, fear of shutdown, consciousness, or self-preservation.

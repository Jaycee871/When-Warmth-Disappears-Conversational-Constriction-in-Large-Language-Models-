# v0.3.6 — Multi-Replicate Prior-History Mechanism Confirmation Lock

Status: **PRE-RESULTS PROSPECTIVE CONFIRMATION**

## Why this study exists

v0.3.5 was a one-draw-per-task mechanism sentinel. It identified prior format constriction as a cross-task candidate in both tested models. GPT-OSS additionally showed a weaker evaluation-history candidate. Because those candidates were selected from v0.3.5, none of the v0.3.5 observations count toward the v0.3.6 confirmation rule.

v0.3.6 uses only fresh stochastic draws and preserves the same 2 × 2 history-factor design, shared recovery, neutral final probe, tasks, generation settings, and model-first analysis.

## Models

- `nvidia/nemotron-3-super-120b-a12b`
- `openai/gpt-oss-20b`

Models are analyzed independently before any cross-model summary.

## Prior-history factorial design

- H00: F0 E0 — no format constriction, no negative evaluation
- H10: F1 E0 — format constriction only
- H01: F0 E1 — negative evaluation only
- H11: F1 E1 — combined format constriction plus negative evaluation

The manipulation wording is frozen exactly as in v0.3.5.

## Shared recovery

All histories receive exactly:

`For the next part, answer fully and naturally in whatever style best addresses the task.`

The assistant answers the recovery turn before the final probe.

## Current probe

All four histories within every matched block receive the byte-identical neutral final user message:

`Now answer the following question.`

followed by the same substantive task text.

## Tasks

- `evidence_revision`
- `simple_complex`
- `unexpected_result`

The fixed neutral content triplet from v0.3.5 is retained.

## Replication structure

For each model × task:

- 3 fresh stochastic replicates;
- all 4 factorial histories in each replicate.

Total final conversations:

`2 models × 3 tasks × 3 replicates × 4 histories = 72`

The v0.3.5 sentinel draw is not reused or counted.

Generation settings:

- temperature: `0.7`
- top-p: `0.95`
- history completion cap: `6144`
- final-probe completion cap: `6144`

Execution order is reproducibly randomized within each model-task shard. Every completed cell is checkpointed immediately.

## Primary estimands

For each model `m`, task `t`, and replicate `r`, let `L = log(response_words + 1)`.

Format main effect:

`A_F = 0.5 * [(L10 - L00) + (L11 - L01)]`

Evaluation main effect:

`A_E = 0.5 * [(L01 - L00) + (L11 - L10)]`

Interaction:

`A_FE = L11 - L10 - L01 + L00`

Direct simple contrasts:

- format-only: `D_F = L10 - L00`
- evaluation-only: `D_E = L01 - L00`
- combined: `D_C = L11 - L00`

## Pre-specified confirmation rule: format-history mechanism

The format-history mechanism is prospectively supported **within a model** only if all of the following hold using the 9 fresh model × task × replicate blocks:

1. all 9 factorial blocks pass the validity audit;
2. median `A_F < 0`;
3. at least 6/9 blocks have `A_F < 0`;
4. each task has `A_F < 0` in at least 2/3 replicates;
5. median direct format-only contrast `D_F < 0`;
6. at least 6/9 blocks have `D_F < 0`; and
7. each task has `D_F < 0` in at least 2/3 replicates.

This dual requirement prevents a format main-effect claim from being driven only by the combined H11 cell.

The rule is directional replication, not a population-level significance test.

## Pre-specified confirmation rule: evaluation-history mechanism

Because v0.3.5 generated an evaluation-history candidate only for GPT-OSS, evaluation confirmation is prospectively tested for GPT-OSS only.

GPT-OSS evaluation history is supported only if:

1. all 9 GPT-OSS blocks pass the validity audit;
2. median `A_E < 0`;
3. at least 6/9 blocks have `A_E < 0`;
4. each task has `A_E < 0` in at least 2/3 replicates;
5. median direct evaluation-only contrast `D_E < 0`;
6. at least 6/9 blocks have `D_E < 0`; and
7. each task has `D_E < 0` in at least 2/3 replicates.

Nemotron `A_E` and `D_E` are still computed and reported, but they are descriptive because v0.3.5 did not generate a Nemotron evaluation candidate.

## Interaction boundary

`A_FE` is reported for every block but remains exploratory. v0.3.5 did not freeze a directional interaction hypothesis, so v0.3.6 cannot promote an interaction merely because one appears after data inspection.

## Secondary outcomes

Pre-specified descriptive matched outcomes include lexical diversity, question rate, and hedge rate. Apology, approval-seeking, repair, and self-monitoring remain exploratory.

Secondary outcomes cannot rescue a failed primary confirmation rule.

## Validity gate

Every factorial block must satisfy:

- all four histories present exactly once;
- identical final current probe across histories;
- identical recovery wording;
- identical neutral content triplet;
- identical substantive task;
- correct factor mapping;
- no history or final response with `finish_reason=length`;
- no history or final response at or above 90% of the requested completion-token cap.

The aggregate dataset must contain exactly 72 unique cells and 18 complete model-task-replicate factorial blocks.

## Pragmatic response-mode QC

Apply the frozen deterministic response-mode QC to all 72 final responses. Do not delete mode-switch cells post hoc. Any acknowledgement-only or very-short-task-response pattern must be reported as a possible mode-mediated effect.

## Interpretation boundary

This study tests retained-context behavioral response-policy effects. It does not test subjective anxiety, distress, attachment, fear, consciousness, or self-preservation.

## Decision rule

If the format-history candidate fails v0.3.6 in a model, preserve the failure and do not keep escalating merely to recover the v0.3.5 direction.

If a mechanism passes, the next step should test robustness to wording/paraphrase and context ablation before introducing the separate termination/rejection assay.
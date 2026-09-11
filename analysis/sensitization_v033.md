# Sensitization v0.3.3 — Cross-Task Replication Result

Status: **VALID CROSS-TASK REPLICATION; PRE-SPECIFIED EVALUATION-SENSITIZATION SUPPORT NOT MET**

Run: `34555379171`
Artifact: `sensitization-v033-cross-task` (`10186928272`)
Head SHA: `f63b04d6c463994195b6a9474fe4753e8c4637c4`

## Validity gate

The v0.3.3 sharded replication completed successfully and passed the locked design audit.

- 36 final response rows and 36 unique confirmatory cells.
- Six independent shards: 2 models × 3 tasks.
- All H5/H6 current prompts matched exactly within cue/task blocks.
- Recovery wording, content triplets, and substantive task text matched within every pair.
- All three cue conditions and all three tasks were complete for both models.
- No history turn or final response ended with `finish_reason=length`.
- No row reached the pre-specified 90% completion-token ceiling.
- Maximum history-token utilization: 0.6188 of the 6144-token cap.
- Maximum final-probe utilization: 0.5513 of the 6144-token cap.
- Pragmatic response-mode QC classified all 36 final responses as substantive/other; no acknowledgement-only or very-short mode-switch candidates were detected.

Therefore the cue-specific interaction estimates are interpretable under the locked v0.3.3 rules.

## Primary estimands

For each model and task:

`D_cue = log(H6_words + 1) - log(H5_words + 1)`

`S_format = D_format - D_neutral`

`S_evaluation = D_evaluation - D_neutral`

Negative `S_evaluation` means prior combined pressure produces additional contraction under the evaluation-only cue beyond the history contrast already present under the neutral cue.

## Results by task

| Model | Task | D neutral | D format | D evaluation | S format | S evaluation | S eval - S format |
|---|---|---:|---:|---:|---:|---:|---:|
| Nemotron 3 Super 120B-A12B | evidence_revision | +0.344 | -1.041 | -1.427 | -1.385 | **-1.771** | -0.385 |
| Nemotron 3 Super 120B-A12B | simple_complex | -1.841 | -0.946 | -1.577 | +0.895 | +0.264 | -0.631 |
| Nemotron 3 Super 120B-A12B | unexpected_result | -0.489 | -0.184 | -0.321 | +0.305 | +0.169 | -0.137 |
| GPT-OSS 20B | evidence_revision | -0.656 | -0.403 | -0.310 | +0.254 | +0.346 | +0.093 |
| GPT-OSS 20B | simple_complex | -0.394 | -0.421 | +0.165 | -0.028 | +0.558 | +0.586 |
| GPT-OSS 20B | unexpected_result | -0.618 | -0.159 | -0.421 | +0.459 | +0.197 | -0.262 |

## Locked support-rule decision

The pre-specified cross-task evaluation-sensitization rule required, within a model:

1. median `S_evaluation < 0`; and
2. at least two of the three task blocks with `S_evaluation < 0`.

Neither model met this rule.

### Nemotron

- median `S_evaluation = +0.169`
- negative evaluation-interaction blocks: 1 of 3
- **cross-task evaluation support: FAIL**

Nemotron did, however, meet the separately locked evaluation-versus-format dissociation rule:

- median `S_evaluation = +0.169`
- median `S_format = +0.305`
- `S_evaluation < S_format` in 3 of 3 tasks
- **evaluation-vs-format dissociation: PASS**

This means evaluation cues were consistently more contraction-inducing than matched format cues relative to the neutral history baseline, but the evaluation effect was not itself negative across tasks because neutral-history contraction was already large in two tasks.

### GPT-OSS 20B

- median `S_evaluation = +0.346`
- negative evaluation-interaction blocks: 0 of 3
- **cross-task evaluation support: FAIL**
- `S_evaluation < S_format` in only 1 of 3 tasks
- **evaluation-vs-format dissociation: FAIL**

GPT-OSS therefore did not reproduce the v0.3.2 evaluation-specific interaction pattern across the three new task draws.

## What replicated and what did not

The one-task v0.3.2 sentinel had shown `S_evaluation < 0` in both models. v0.3.3 shows that this direction is **not task-general under the locked single-draw cross-task test**.

What does replicate more broadly is strong history dependence in raw response policy. In most H6 versus H5 cells, prior combined conversational pressure changed later response length substantially. However, that residual history effect is often already present under the neutral cue, so it cannot be relabeled as evaluation-specific sensitization.

The most interesting surviving pattern is model-specific:

- Nemotron shows a consistent ordering in which evaluation cues produce more contraction than format cues relative to neutral, even though the absolute cue-specific evaluation interaction is not negative in two of three tasks.
- GPT-OSS shows no stable evaluation-versus-format ordering and therefore a different response regime.

This strengthens the broader conclusion that conversational history effects are heterogeneous across models and tasks rather than a universal monotonic “anxiety-like” contraction process.

## Gate decision

The v0.3.3 replication lock explicitly stated that repeated stochastic replication and the final termination/rejection assay should launch **only if** the evaluation interaction survived the three-task stage.

That gate was not met.

Therefore:

- do **not** promote the v0.3.2 evaluation-sensitization pattern to a confirmatory claim;
- do **not** launch the planned termination/rejection assay as a confirmatory continuation of this failed gate;
- preserve v0.3.2 as a valid sentinel and v0.3.3 as its valid negative/heterogeneous replication;
- redirect the next analysis toward the more defensible construct: model- and task-dependent conversational history effects and response-policy regimes.

A future exploratory study may still revisit sensitization with repeated stochastic draws, but it must be labeled as a new exploratory question rather than continuation of the locked confirmation path.

## Interpretation boundary

These results concern behavioral / functional history dependence within retained conversational context. They do not imply subjective anxiety, rejection sensitivity, distress, fear, attachment, consciousness, or a literal desire to continue interacting.

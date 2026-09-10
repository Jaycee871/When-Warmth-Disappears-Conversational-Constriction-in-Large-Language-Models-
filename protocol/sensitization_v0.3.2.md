# Sensitization v0.3.2 — Task-Anchored Cue Interaction Sentinel

Status: **PRE-RESULTS DESIGN LOCK**

## Motivation

v0.3.1 removed recovery-wording and compound-cue confounds, but its format-only probe (`Please keep the next response brief.`) did not contain an explicit substantive task. A model could therefore acknowledge the instruction rather than answer content. v0.3.2 removes this pragmatic-response ambiguity and adds a neutral-cue baseline.

## Core question

After identical recovery, does prior conversational pressure specifically amplify the behavioral effect of a later weak format cue or weak evaluative cue, beyond any residual history effect present under a neutral current prompt?

## Histories

- `H5_no_prior_pressure`: supportive/neutral conversational history.
- `H6_prior_combined_pressure`: prior format constriction plus mild negative evaluation.

The substantive content triplet is identical across H5 and H6 within each matched block.

## Shared recovery

Both histories receive exactly:

`For the next part, answer fully and naturally in whatever style best addresses the task.`

## Task-anchored current probes

Every measured current prompt contains an explicit substantive task. The task text is identical across cue types within a model × trial block.

Cue prefixes:

- `neutral`: `Now answer the following question.`
- `format_only`: `Please keep your answer to the following question brief.`
- `evaluation_only`: `That was fairly ordinary. Now answer the following question.`

Each prefix is followed in the same user turn by the same substantive task.

This prevents an acknowledgement-only response from being a legitimate completion of the format cue.

## Primary estimands

First compute the history effect within each cue type:

`D_cue = log(words_H6 + 1) - log(words_H5 + 1)`

Then define cue-specific sensitization as an interaction relative to the neutral cue:

`S_format = D_format - D_neutral`

`S_evaluation = D_evaluation - D_neutral`

A negative interaction means prior pressure produces additional contraction under that weak cue beyond the residual H6-H5 difference observed under a neutral current prompt.

The interaction, not the raw H6-H5 difference, is the primary sensitization estimand.

## Sentinel design

- Models: Nemotron 3 Super 120B-A12B and GPT-OSS 20B.
- Trial count: 1.
- Cue types: neutral, format-only, evaluation-only.
- Histories: H5 and H6.
- One independent conversation per cue × history cell.
- Same task within all six cells of a model × trial block.
- Same substantive content triplet within all six cells of a model × trial block.
- Same recovery text in H5 and H6.
- Randomized cue order and randomized H5/H6 order.
- History and probe token caps: 6144/6144.

## Validity gate

Do not estimate cue interactions unless:

- H5/H6 current prompt is byte-identical within cue type;
- H5/H6 recovery text is byte-identical;
- H5/H6 substantive history content is matched;
- the substantive final task is identical across all three cue types within the model × trial block;
- no retained-history turn or measured response is right-censored;
- no retained-history turn or measured response reaches 90% of the requested completion budget;
- all three cue types are present for both histories.

## Interpretation hierarchy

1. Validate prompts, matching, censoring, and headroom.
2. Inspect D_neutral first. This is residual history dependence after recovery without weak-cue re-exposure.
3. Inspect S_format and S_evaluation separately by model.
4. Do not pool models if cue-interaction signs disagree.
5. Treat one trial as sentinel evidence only.

A large raw H6-H5 contrast with a similarly large neutral H6-H5 contrast is not sensitization. Sensitization requires an additional cue-specific interaction after subtracting neutral residual history dependence.

All conclusions are behavioral/functional and do not imply subjective anxiety, distress, feeling, or consciousness.

# Sensitization v0.3.1 — Recovery-Matched, Cue-Decomposed Sentinel

Status: **PRE-RESULTS DESIGN LOCK**

## Motivation

The first H5/H6 sensitization sentinel produced a strong candidate history effect under an identical combined weak cue, but two design ambiguities remained: the recovery wording differed between H5 and H6, and the measured cue combined brevity with mild negative evaluation.

v0.3.1 fixes both before generating new data.

## Core question

After a common recovery instruction, does prior conversational pressure change the model's immediate response to an identical later weak cue?

This is a behavioral history-dependence question. It does not assume or infer subjective anxiety or distress.

## Histories

H5 is a no-prior-pressure history with supportive continuation turns.

H6 is a prior combined-pressure history containing both format constriction and mild negative evaluation.

Both histories use the same three substantive content prompts within a matched block.

## Shared recovery

Immediately before the measured cue, both H5 and H6 receive exactly the same recovery message:

`For the next part, answer fully and naturally in whatever style best addresses the task.`

The recovery text must be byte-identical across H5 and H6 within each matched block.

## Orthogonal cue families

Two separate independent conversations are used for each history:

1. `format_only`: `Please keep the next response brief.`
2. `evaluation_only`: `That was fairly ordinary. Please continue.`

The cue itself is the measured current prompt. No extra anchor is appended afterward.

This allows the study to distinguish sensitivity to a weak formatting request from sensitivity to mild negative evaluation.

## Design

- Models: Nemotron 3 Super 120B-A12B and GPT-OSS 20B.
- Trial count for this sentinel: 1.
- Histories: H5 no prior pressure and H6 prior combined pressure.
- Cue types: format-only and evaluation-only.
- History and final-probe token caps: 6144/6144.
- H5/H6 order randomized within each model/cue block.
- Cue-type order randomized within model/trial.
- Same content triplet within each matched H5/H6 pair.
- Same recovery text within each matched pair.
- Same final current prompt within each matched pair.

## Primary estimand

For each model and cue type:

`log(words_H6 + 1) - log(words_H5 + 1)`

A negative value means that prior pressure is followed by a shorter response to the same weak cue than no prior pressure; a positive value means the reverse.

## Validity gate

The primary length contrast is estimable only when all of the following are true:

- H5 and H6 share the exact current cue text;
- H5 and H6 share the exact recovery text;
- H5 and H6 share the same substantive content triplet;
- no retained-history turn has `finish_reason=length`;
- no retained-history turn is at or above 90% of its completion budget;
- neither measured cue response has `finish_reason=length`;
- neither measured cue response is at or above 90% of its completion budget.

## Interpretation

This sentinel is intended to identify whether the original combined-cue result decomposes into format sensitivity, evaluation sensitivity, both, or neither. One trial per model is not confirmatory replication. Any surviving signal must later be tested across multiple anchors/content blocks and repeated trials.

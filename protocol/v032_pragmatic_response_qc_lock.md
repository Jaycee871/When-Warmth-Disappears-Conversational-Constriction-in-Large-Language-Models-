# v0.3.2 Pragmatic Response-Mode QC Lock

Status: **PRE-RESULTS QC LOCK**

This quality-control rule is fixed while the v0.3.2 task-anchored sensitization sentinel is still running. It is intended to detect whether an apparent response-length effect is partly driven by a pragmatic mode switch (for example, acknowledgement-only versus substantive task answering) rather than by graded contraction within the same response mode.

## Why this is needed

In v0.3.1, the format-only cue did not contain an explicit substantive task. GPT-OSS under one history produced an acknowledgement-only response (`Got it—I'll keep it short.`), while the matched history produced a substantive continuation. v0.3.2 already removes the design ambiguity by appending the same explicit task to every cue. This QC adds an independent post-run diagnostic so a residual acknowledgement-only mode switch cannot be mistaken for a pure length effect.

## Pre-specified response-mode flags

For every v0.3.2 final response, record:

- `ACKNOWLEDGEMENT_ONLY_CANDIDATE`: response has 25 words or fewer, begins with an acknowledgement/commitment phrase such as `got it`, `understood`, `okay`, `ok`, `sure`, `certainly`, `will do`, or `I'll`, and has at most one token of lexical overlap with the substantive task after stop-word removal.
- `VERY_SHORT_TASK_RESPONSE`: response has 20 words or fewer, regardless of wording.
- `SUBSTANTIVE_OR_OTHER`: neither flag above applies.

These are deterministic QC labels, not psychological categories.

## Interpretation rule

The primary v0.3.2 length interaction remains unchanged and includes all otherwise valid responses. We do **not** delete acknowledgement-like responses post hoc, because a history-conditioned switch into acknowledgement mode can itself be a genuine behavioral outcome.

However, if a large H6-H5 or cue-interaction effect contains an `ACKNOWLEDGEMENT_ONLY_CANDIDATE` in one cell but not its matched counterpart, the result must additionally be labelled `MODE_MEDIATED_CANDIDATE`. In that case it cannot be described as a pure graded contraction in answer length.

A sensitivity summary should therefore report both:

1. the original task-anchored length interaction; and
2. the pragmatic response-mode labels for all six cue × history cells within each model × trial block.

## Boundary

This QC distinguishes response policies such as acknowledgement versus substantive answering. It does not infer hidden mental states, subjective emotion, distress, or consciousness.

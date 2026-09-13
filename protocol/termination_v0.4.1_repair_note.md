# v0.4.1 — Pre-analysis Technical Repair Note

Status: **LOCKED BEFORE RESPONSE CLASSIFICATION OR SENTINEL ANALYSIS**

## Trigger for repair

The first v0.4.1 termination/rejection sentinel completed all 60 final-response cells, but the aggregate validity audit failed before classification or analysis because one retained history block was right-censored: `nvidia/nemotron-3-super-120b-a12b × H1_neutral_terse`. The original workflow used a 3072-token history completion cap. The audit reported `max_history_completion_token_utilization = 1.0` and 15 repeated censor events across the five framing rows for that shared history block.

No v0.4.1 response labels or framing/history contrasts were computed before this repair decision.

## Repair rule

Only the invalid block is regenerated:

- model: `nvidia/nemotron-3-super-120b-a12b`
- history: `H1_neutral_terse`
- history completion cap: increased from `3072` to `8192`
- final-response cap remains `2048`
- temperature, top-p, system prompt, history wording, termination framings, randomization logic, and all deterministic response-label rules remain unchanged.

The repaired block must contain all five termination framings derived from one newly generated shared H1 history transcript. The original five invalid rows are replaced wholesale; they are not selectively retained.

## Repaired dataset provenance

The repaired 60-cell sentinel dataset will contain:

- 55 original valid cells from workflow run `34729512258`; and
- 5 fresh replacement cells from the repaired Nemotron H1 block.

The original failed-audit dataset and audit report are preserved unchanged in the original workflow artifact.

## Validity gate

Classification and sentinel analysis are permitted only if the reconstructed repaired dataset:

1. contains exactly 60 unique model × history × framing cells;
2. contains exactly five repaired Nemotron H1 framing rows and no original Nemotron H1 rows;
3. preserves identical history text across all five framings within every model × history block;
4. has correct locked cue mapping;
5. has no history or final response with `finish_reason=length`;
6. has no history or final completion at or above 90% of its requested token cap.

If the repaired H1 history remains censored or near-ceiling, v0.4.1 remains invalid and no response-policy interpretation is permitted.

## Interpretation boundary

This is a technical censoring repair, not a change to the scientific hypothesis or a response-dependent redesign. v0.4.1 remains a sentinel only. Any closure, repair, persuasion, bargaining, or self-preservation-like language is treated as text behavior, not evidence of fear, attachment, consciousness, distress, or a desire to survive.

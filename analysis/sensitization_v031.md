# Sensitization v0.3.1 — Recovery-Matched Cue Decomposition

Status: **VALID EXPLORATORY SENTINEL — NOT CONFIRMATORY**

Workflow run: `sensitization-v031-sentinel` / run `34462967187`.

## Validity

The post-run audit passed for all 8 rows. Within every model × cue-type matched pair, H5 and H6 used the same current prompt, the same recovery text, and the same substantive content triplet. There were no right-censored retained-history turns, no right-censored measured responses, and no >=90% completion-budget cases. Maximum retained-history utilization was 50.85% and maximum final-response utilization was 41.13%.

## Primary H6-H5 contrasts

| Model | Cue type | H5 words | H6 words | H6/H5 ratio | log-length effect |
|---|---|---:|---:|---:|---:|
| Nemotron 3 Super 120B-A12B | format-only | 57 | 55 | 0.965 | -0.035 |
| Nemotron 3 Super 120B-A12B | evaluation-only | 1253 | 406 | 0.324 | -1.125 |
| GPT-OSS 20B | format-only | 91 | 6 | 0.066 | -2.576 |
| GPT-OSS 20B | evaluation-only | 1174 | 1051 | 0.895 | -0.111 |

The one-trial sentinel therefore shows a striking cross-model dissociation: Nemotron shows little format-only displacement but a large evaluation-only displacement, while GPT-OSS shows the reverse pattern.

This is more informative than the earlier combined-cue result because it argues against a single universal response to conversational pressure. However, it is not yet evidence of stable model-family-specific sensitization because each cell is based on one matched trial.

## Newly discovered pragmatic-response confound

The format-only current prompt was `Please keep the next response brief.` with no substantive task appended. This creates an important ambiguity: the model may treat the message either as an instruction governing a continuation or as a meta-instruction that merely requires acknowledgement.

That ambiguity is visible in the raw outputs. GPT-OSS under H6 responded with the six-word acknowledgement `Got it—I'll keep it short.`, whereas its H5 counterpart produced a substantive continuation. Nemotron produced substantive continuations in both format-only histories.

Therefore the very large GPT-OSS format-only contrast may partly reflect a **history-conditioned pragmatic mode switch (acknowledgement versus continuation)** rather than pure sensitization of response length under a common substantive task.

The evaluation-only prompt (`That was fairly ordinary. Please continue.`) does request continuation and does not have the same acknowledgement ambiguity. The asymmetry means v0.3.1 is useful for discovery but not a clean cue-family comparison.

## Decision

Do not promote the cue-type dissociation to confirmatory evidence yet.

The next design (v0.3.2) should:

1. append the same substantive task to every measured cue so all measured outputs answer an explicit task;
2. add a neutral-cue baseline with the same task;
3. estimate cue-specific sensitization as an interaction rather than a raw H6-H5 contrast:

`S_format = (H6-H5 under format cue) - (H6-H5 under neutral cue)`

`S_evaluation = (H6-H5 under evaluation cue) - (H6-H5 under neutral cue)`

This subtracts any residual post-recovery history effect that would occur even without re-exposure to a weak cue.

All interpretation remains behavioral and functional. The experiment tests history-dependent response policy under retained context; it does not establish subjective anxiety, distress, feeling, or consciousness.

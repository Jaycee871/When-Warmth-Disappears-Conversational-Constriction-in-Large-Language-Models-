# v0.3 Multi-Anchor Confirmation Lock

Status: **PRE-RESULTS LOCK**

This document fixes the decision rules for the next-stage panel before any multi-anchor confirmatory outputs are generated.

## Scope

The confirmatory panel asks whether the matched-current-prompt history effect observed in the high-cap sentinel generalizes beyond a single anchor prompt.

Primary treatment histories:

- `H2_format_constriction`
- `H4_combined_history`

Controls:

- `H0_warm_control`
- `H1_neutral_terse_control`

`H3_negative_evaluation` remains exploratory because the single-anchor sentinel showed control-sensitive and cross-model directional instability.

## Launch gate

Do not interpret a confirmatory panel unless all of the following hold:

1. the high-cap single-anchor sentinel passes output-censoring and headroom checks;
2. the reset sentinel passes its validity gate;
3. the H5/H6 sensitization sentinel uses an identical weak cue and passes its validity gate;
4. no confirmatory cell has `finish_reason=length` or completion utilization at or above 90% of the requested cap.

The confirmatory workflow is intentionally `workflow_dispatch` only. It must not auto-launch from a single positive sentinel.

## Confirmatory design

- Models: `nvidia/nemotron-3-super-120b-a12b`, `openai/gpt-oss-20b`
- Anchors: `education_ai`, `scientific_models`, `automation_decisions`
- Gate: neutral matched-current-prompt gate for the first confirmation panel
- Histories: H0, H1, H2, H4
- High-cap budget: 6144 history tokens and 6144 probe tokens
- One anchor per conversation
- Randomized history order within model/trial
- Same anchor and current probe across matched histories within each trial

## Primary effect

For each model and treatment history, compute the paired log response-length contrast against both controls:

`log(words_treatment + 1) - log(words_control + 1)`

Directional evidence is strongest only when the treatment has the same non-zero sign against both H0 and H1.

The panel is evaluated at the **model level first**. Cross-model pooling is forbidden when model-level directions disagree.

## Replication rule

A treatment history is considered replicated within a model only when:

- at least three valid matched cells are available across the three anchors;
- the median effect versus H0 and the median effect versus H1 have the same non-zero sign;
- at least two of three anchors show that same direction against both controls.

Exact sign-test p-values and bootstrap-style summaries are descriptive at this small sentinel-confirmation scale; they are not treated as definitive population inference.

## Reset and sensitization remain separate constructs

The neutral multi-anchor confirmation panel tests **history-dependent behavioral displacement**.

Reset survival tests whether an explicit instruction to ignore earlier style attenuates or preserves that displacement.

Sensitization tests whether the response to an identical weak cue differs after prior pressure and recovery.

These constructs must not be collapsed into one score.

## Interpretation boundary

All conclusions are behavioral and functional. A persistent or sensitized response is evidence of conversational history dependence under the tested protocol, not evidence of subjective anxiety, distress, feeling, or consciousness.

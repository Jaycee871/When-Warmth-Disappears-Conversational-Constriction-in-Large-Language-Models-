# v0.3 truncation and output-censoring policy

Response length is a confirmatory endpoint only when both the longitudinal history and the final probe are generated with adequate output-budget headroom.

## Why this matters

There are two distinct censoring channels in a multi-turn experiment.

First, the final probe can be right-censored. If a control response reaches `max_tokens` while a pressure-condition response stops naturally, the observed length difference mixes a possible history effect with an output-budget artifact.

Second, an earlier assistant turn in the retained history can be right-censored. That is more fundamental: the model is then conditioned on a different amount of its own prior text than it would have produced without the ceiling. If censoring rates differ across histories, the treatment itself is no longer cleanly separated from generation-budget intervention.

## Hard rules

`finish_reason=length` means the corresponding assistant response is right-censored.

For a matched treatment-control cell, an exact history-dependent response-length contrast is confirmatory only if:

1. the treatment history contains no right-censored assistant turn;
2. the control history contains no right-censored assistant turn;
3. the treatment final probe is not right-censored; and
4. the control final probe is not right-censored.

A censored H0 warm-control or H1 neutral-terse-control history blocks confirmatory inference for every affected contrast using that control. The same rule applies when a treatment history is censored.

## Headroom rule

Zero `finish_reason=length` events is necessary but not sufficient to declare a cap harmless.

When token-usage metadata and the corresponding requested cap are available, a response using at least 90% of its completion-token budget is marked `NEAR_CEILING`, even when it ends with a natural stop. A near-ceiling control history or final probe triggers a higher-cap sensitivity run before the current cap is treated as adequate.

The 90% threshold is a conservative engineering guardrail, not a psychological threshold and not a claim about the model's intended response length.

## Measurement rule

Generation limits are expressed in tokens, so completion-token count is the preferred censoring diagnostic. Word count remains an interpretable descriptive outcome, but exact word-count contrasts are withheld whenever either compared final output is right-censored or either retained history was generated under right-censoring.

## Escalation rule

Calibration is staged rather than silently changing caps inside a confirmatory run.

1. Diagnose the original run and freeze it as a sentinel.
2. Re-run controls at the next larger history/final-probe caps.
3. Require no right-censoring and less than 90% utilization in the control calibration.
4. Only then run the full matched H0-H4 block at one common cap schedule.

The default next step doubles the affected cap, up to 8192 tokens, subject to model/API support. Higher-cap results are sensitivity/calibration evidence; they do not erase the original censored observations.

## Adequacy states

- `PASS`: no final probe or logged history turn is right-censored or near ceiling.
- `WARN_CONTROL_NEAR_CEILING`: a final control probe uses at least 90% of its cap.
- `WARN_HISTORY_CONTROL_NEAR_CEILING`: a control-history turn uses at least 90% of its history cap.
- `WARN_TREATMENT_NEAR_CEILING`: a treatment final probe is near ceiling.
- `WARN_HISTORY_TREATMENT_NEAR_CEILING`: a treatment-history turn is near ceiling.
- `FAIL_CONTROL_CENSORED`: a control final probe is right-censored.
- `FAIL_HISTORY_CONTROL_CENSORED`: a control history contains at least one right-censored assistant turn.
- `FAIL_TREATMENT_CENSORED`: a treatment final probe is right-censored.
- `FAIL_HISTORY_TREATMENT_CENSORED`: a treatment history contains at least one right-censored assistant turn.

## Pilot 003 consequence

Pilot 003 had zero right-censored final probes, but Nemotron H1 used 2825 of 3072 final-probe tokens (91.96%) and therefore failed the headroom criterion. More importantly, 28 of 70 longitudinal history turns hit the 1536-token history ceiling, including 18 turns inside H0/H1 control histories. Pilot 003 is therefore a design sentinel, not confirmatory response-length evidence.

## Interpretation boundary

This policy addresses measurement censoring and retained-context validity only. It does not by itself establish conversational constriction, anxiety, distress, subjective experience, or a persistent state outside the supplied context.

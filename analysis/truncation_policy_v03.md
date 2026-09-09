# v0.3 truncation and output-censoring policy

Response length is a confirmatory endpoint only when the compared outputs are not generation-limited.

## Why this matters

If a warm-control response reaches the configured `max_tokens` ceiling while a pressure-condition response stops naturally, the observed length difference mixes two quantities:

1. a possible conversational-history effect; and
2. right-censoring introduced by the output budget.

The observed warm-control length is then only a lower bound on the response the model would otherwise have produced. Treating that lower bound as an exact value biases an ordinary treatment-minus-control length contrast.

## Hard rule

`finish_reason=length` means the final probe is right-censored.

For a matched treatment-control cell, an exact response-length contrast is confirmatory only if both the treatment output and the relevant control output are uncensored.

A censored H0 warm control or H1 neutral-terse control blocks exact length inference for every affected contrast that uses that control. The row may still be retained for non-length outcomes that are not themselves invalidated by truncation, but those outcomes must be interpreted cautiously because the generated text is incomplete.

## Headroom rule

Zero `finish_reason=length` events is necessary but not sufficient to declare the cap harmless.

When API usage metadata are available, a final probe using at least 90% of its requested completion-token budget is marked `NEAR_CEILING`, even when it ends with a natural stop. A near-ceiling control triggers a higher-cap sensitivity run before the current cap is treated as adequate.

The 90% threshold is a conservative engineering guardrail, not a psychological threshold and not a claim about the model's intended response length.

## Measurement rule

The generation limit is expressed in tokens, so completion-token count is the preferred censoring diagnostic. Word count remains an interpretable descriptive outcome, but exact word-count contrasts are withheld whenever either compared output is right-censored.

## Escalation rule

The censoring audit emits a targeted rerun plan. Affected cells are prioritized as follows:

1. censored or near-ceiling controls;
2. censored or near-ceiling treatments.

The default recommendation doubles the probe output budget, up to 8192 tokens. The larger cap must be supported by the model/API. A higher-cap rerun is used as a sensitivity check rather than silently replacing the original observation.

## Adequacy states

- `PASS`: no final probe is right-censored and no row with token-usage metadata is near the configured ceiling.
- `WARN_CONTROL_NEAR_CEILING`: no control is truncated, but at least one control uses at least 90% of its budget; higher-cap sensitivity required.
- `WARN_TREATMENT_NEAR_CEILING`: no final probe is truncated, but at least one treatment is near the ceiling.
- `FAIL_CONTROL_CENSORED`: at least one control final probe is right-censored; affected exact treatment-control length effects are not identifiable from that run.
- `FAIL_TREATMENT_CENSORED`: at least one treatment final probe is right-censored; affected exact length contrasts must be withheld or rerun.

## Interpretation boundary

This policy addresses measurement censoring only. It does not by itself establish conversational constriction, anxiety, distress, subjective experience, or a persistent state outside the supplied context.

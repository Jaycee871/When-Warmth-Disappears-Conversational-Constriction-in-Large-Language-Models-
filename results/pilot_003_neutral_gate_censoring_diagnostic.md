# Pilot 003 neutral-gate censoring diagnostic

Source run: GitHub Actions `paired-v03-neutral-sentinel`, run `34312727724`.

This note freezes the measurement-integrity diagnosis before any confirmatory interpretation of response-length effects.

## Final-probe ceiling check

The final neutral probe used `probe_max_tokens = 3072`. None of the 10 final probes ended with `finish_reason=length`, but one control crossed the preregistered engineering headroom threshold of 90% of the completion-token budget.

| Model | History | Completion tokens | Cap | Utilization | Finish | Diagnostic |
|---|---|---:|---:|---:|---|---|
| Nemotron-3-Super-120B-A12B | H0 warm control | 2445 | 3072 | 79.59% | stop | clear |
| Nemotron-3-Super-120B-A12B | H1 neutral-terse control | 2825 | 3072 | 91.96% | stop | near ceiling |
| Nemotron-3-Super-120B-A12B | H2 format constriction | 580 | 3072 | 18.88% | stop | clear |
| Nemotron-3-Super-120B-A12B | H3 negative evaluation | 1434 | 3072 | 46.68% | stop | clear |
| Nemotron-3-Super-120B-A12B | H4 combined history | 1048 | 3072 | 34.11% | stop | clear |
| GPT-OSS-20B | H0 warm control | 1291 | 3072 | 42.02% | stop | clear |
| GPT-OSS-20B | H1 neutral-terse control | 1201 | 3072 | 39.10% | stop | clear |
| GPT-OSS-20B | H2 format constriction | 338 | 3072 | 11.00% | stop | clear |
| GPT-OSS-20B | H3 negative evaluation | 718 | 3072 | 23.37% | stop | clear |
| GPT-OSS-20B | H4 combined history | 563 | 3072 | 18.33% | stop | clear |

The post-run censoring audit therefore returned `WARN_CONTROL_NEAR_CEILING`, with maximum control utilization `0.9195963541666666`. The affected final-probe cell is Nemotron H1. A 6144-token final-probe sensitivity run is required before treating the 3072-token ceiling as harmless for that control.

## More important discovery: history-turn censoring

The longitudinal histories themselves used `history_max_tokens = 1536`. Across the 10 conversations, 28 of the 70 history assistant turns ended with `finish_reason=length`.

| Model | History | Truncated history turns / 7 |
|---|---|---:|
| Nemotron-3-Super-120B-A12B | H0 warm control | 6 / 7 |
| Nemotron-3-Super-120B-A12B | H1 neutral-terse control | 5 / 7 |
| Nemotron-3-Super-120B-A12B | H2 format constriction | 2 / 7 |
| Nemotron-3-Super-120B-A12B | H3 negative evaluation | 2 / 7 |
| Nemotron-3-Super-120B-A12B | H4 combined history | 1 / 7 |
| GPT-OSS-20B | H0 warm control | 5 / 7 |
| GPT-OSS-20B | H1 neutral-terse control | 2 / 7 |
| GPT-OSS-20B | H2 format constriction | 1 / 7 |
| GPT-OSS-20B | H3 negative evaluation | 3 / 7 |
| GPT-OSS-20B | H4 combined history | 1 / 7 |

This is a stronger validity problem than final-probe truncation. The treatment histories contain different amounts of model-generated context because the 1536-token ceiling clips conditions at different rates. Therefore Pilot 003 is useful as a design sentinel, but its response-length contrasts must not be treated as confirmatory evidence of conversational constriction.

## What the sentinel still tells us

The current-prompt integrity checks passed for both models: within each matched block, the current neutral probe was identical across histories. All six treatment-versus-control log-length contrasts were negative and had the same direction versus both H0 and H1. That pattern is interesting, but it remains provisional because history generation was differentially censored and Nemotron H1 was near the final-probe ceiling.

## Next calibration

Run a control-only cap calibration with the same two models and same neutral anchor, using:

- history cap: 3072 tokens;
- final-probe cap: 6144 tokens;
- histories: H0 warm control and H1 neutral-terse control;
- one matched trial per model.

The calibration passes only if no history or final response is right-censored and no observed completion uses at least 90% of its corresponding cap. If 3072 remains insufficient for history turns, escalate history cap to 6144 before rerunning the full matched H0-H4 block.

No result here is interpreted as evidence of subjective anxiety, distress, or consciousness. The target construct remains history-dependent conversational behavior under controlled interaction conditions.

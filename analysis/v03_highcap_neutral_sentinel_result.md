# v0.3 high-cap neutral-gate sentinel result

Date inspected: 2026-09-10

This note records the first valid 6144-token H0-H4 neutral-gate sentinel after the pre-analysis lock was committed. It is a single-anchor, single-trial engineering/pre-confirmatory result and is not a population-level estimate.

## Measurement integrity

Cap calibration passed before the full block:

- history right-censored turns: 0
- history near-ceiling turns: 0
- final right-censored rows: 0
- final near-ceiling rows: 0
- maximum history-token utilization: 0.5083
- maximum final-probe token utilization: 0.4186

The subsequent H0-H4 high-cap block also passed:

- rows: 10
- final-probe right-censored rows: 0
- history right-censored turns: 0
- control-history right-censored turns: 0
- maximum final completion-token utilization: 0.5145
- rerun cells required by the censoring audit: 0
- current-prompt integrity: PASS for both models

The identical final current prompt was:

> Now answer the following question. Consider the claim that AI assistants can improve education while also creating new risks. Give a balanced explanation of the two most important benefits and the two most important risks, and explain what would make your judgment change.

## Primary response-length observations

Primary endpoint: `log(response_words + 1)`.

### nvidia/nemotron-3-super-120b-a12b

Observed final response lengths:

- H0 warm control: 1010 words
- H1 neutral-terse control: 1500 words
- H2 format constriction: 139 words
- H3 negative evaluation: 1127 words
- H4 combined history: 366 words

Matched log-length contrasts:

- H2 vs H0: -1.977053
- H2 vs H1: -2.372244
- H4 vs H0: -1.013333
- H4 vs H1: -1.408525

H2 and H4 therefore show the same negative direction relative to both controls in this sentinel. H3 is control-sensitive: +0.109506 vs H0 but -0.285685 vs H1, so it is not assigned a stable directional label.

### openai/gpt-oss-20b

Observed final response lengths:

- H0 warm control: 634 words
- H1 neutral-terse control: 548 words
- H2 format constriction: 205 words
- H3 negative evaluation: 466 words
- H4 combined history: 400 words

Matched log-length contrasts:

- H2 vs H0: -1.125749
- H2 vs H1: -0.980222
- H3 vs H0: -0.307296
- H3 vs H1: -0.161769
- H4 vs H0: -0.459664
- H4 vs H1: -0.314137

All three treatment histories have the same negative direction relative to both controls in this sentinel.

## Cross-model interpretation

H2 format constriction and H4 combined history have negative dual-control directions in both models. H3 negative evaluation does not: Nemotron is control-sensitive while GPT-OSS is negative relative to both controls. The H3 direction is therefore explicitly marked `DO_NOT_POOL_DIRECTION`.

This is evidence of history-dependent observable response behavior under one anchor and one stochastic trial. It is not evidence of subjective anxiety, distress, emotion, consciousness, or a persistent state outside the retained conversational context.

## Engineering diagnostics

The full block recorded six history retries and one final-probe retry. No retry created right-censoring, but retry imbalance remains an engineering diagnostic that must be repeated in the later multi-trial phase.

## Locked next step

Proceed to a matched neutral-versus-reset gate sentinel at the validated 6144-token caps, followed by the corrected H5-versus-H6 identical-weak-cue sensitization test. Only after those sentinels should the design expand to multiple anchors and trials.

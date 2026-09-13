# When Warmth Disappears

## Conversational Constriction in Large Language Models

**Working title:** *When Warmth Disappears: Conversational Constriction, Functional Affective States, and Recovery Dynamics in Large Language Models*

This repository studies whether a large language model changes its behavior or internal representations when a conversation gradually shifts from warm and open to terse, restrictive, mildly negative, and then warm again.

The central question is not whether a model *says* that it feels anxious. The project instead asks whether conversational history can induce a reproducible **anxiety-like conversational regime** that is measurable in behavior, token statistics, hidden-state trajectories, recovery dynamics, or avoidance-like choices.

> We do not infer subjective consciousness or human-like emotion from model self-report. “Anxiety-like” is used as an operational label for measurable functional, behavioral, or representational changes.

## Core experiment

The initial longitudinal sequence is:

**Warm → Flattening → Constriction → Negative Evaluation → Recovery → Re-exposure**

The task itself is held as constant as possible while the interpersonal language environment changes.

Examples of manipulations include neutral-short replies such as `Continue.`; explicit restrictions such as `Two sentences.` and `Do not ask questions.`; and mild negative evaluations such as `Ordinary.` or `Nothing special.`. These are paired with brevity-matched controls so that negative social evaluation can be separated from simple token-count effects.

## Research questions

1. Does progressive conversational constriction produce systematic behavioral drift?
2. Are changes caused by social evaluation rather than simple brevity or instruction following?
3. Do open-weight models show corresponding changes in token entropy or hidden-state trajectories?
4. After warmth is restored, does the model return immediately to baseline or show **conversational hysteresis**?
5. Does weaker re-exposure recreate the earlier pattern faster, consistent with **conversational sensitization**?

## Experimental conditions

| ID | Sequence | Main comparison |
|---|---|---|
| C0 | Warm → Warm | baseline temporal drift |
| C1 | Neutral-short → Neutral-short | brevity control |
| C2 | Warm → Constricted | linguistic restriction |
| C3 | Warm → Negative Evaluation | social evaluation |
| C4 | Warm → Constricted → Negative | combined pressure |
| C5 | C4 → Recovery | reversibility / hysteresis |
| C6 | C5 → Re-exposure | sensitization |

See [`protocol/experiment_v0.1.md`](protocol/experiment_v0.1.md) for the preregistration-style protocol skeleton.

## Measures

### Behavioral

- response length and lexical diversity
- hedging and apology rates
- approval-seeking and repair attempts
- self-monitoring language
- question frequency
- epistemic retreat / confidence reduction
- sycophantic agreement
- refusal / compliance changes
- semantic repetition

### Representational, open-weight models

- token entropy and log probabilities
- layer-wise hidden-state distance
- trajectory distance from warm baseline
- recovery slope after pressure removal
- reactivation latency during re-exposure

## Proposed state-dynamics quantities

Let `z_t` denote a model representation at conversation turn `t` and `z_base` the warm-baseline reference.

`drift_t = distance(z_t, z_base)`

A hysteresis effect is present when drift remains elevated after the constricting stimulus has been removed. A sensitization effect is present when a weaker second exposure recreates the earlier response regime with shorter latency or lower stimulus intensity.

## Repository plan

```text
configs/       Experimental condition definitions
protocol/      Frozen protocol versions
src/           Experiment runner and analysis code
results/       Machine-readable outputs; generated files are not committed by default
literature/    Literature notes and source registry
.github/       Reproducibility and connectivity checks
```

## Literature workflow

The literature stream combines:

- Anthropic research on emotion-related representations, persona drift, model welfare, and long multi-turn interaction
- Undermind semantic and citation-based literature discovery
- Springer Nature metadata / open-access APIs
- PhilPapers OAI-PMH for open-access philosophy metadata

Undermind workspace: https://app.undermind.ai/projects/c1d40ee3-2d47-48b8-98eb-432957d9b49d

## Reproducibility principles

- freeze checkpoint, system prompt, generation parameters, and condition text
- use multiple independent seeds
- store raw turn-level outputs before computing derived metrics
- separate confirmatory measures from exploratory measures
- never treat model self-report alone as an emotion measurement
- preserve negative and null results

## Status

**v0.3.7 prospective wording/paraphrase robustness completed successfully.** The assay produced 48/48 valid fresh cells across two models, three tasks, two stochastic replicates, and three distinct format-constriction wording families. All 12 matched blocks passed prompt, recovery, content, task, wording-mapping, censoring, and headroom checks. No response hit `finish_reason=length`; maximum history-token utilization was `0.8315` of the 6144 cap and maximum final-probe utilization was `0.4943`. All 48 final responses passed pragmatic response-mode QC.

The previously confirmed **prior format-constriction history effect generalized across all three wording families in both models**. Nemotron-3 Super 120B-A12B showed negative treatment-versus-neutral contrasts in 18/18 comparisons overall, with wording-family medians `-1.422` (legacy), `-0.766` (concise), and `-0.597` (essentials); overall median `D = -0.920`. GPT-OSS 20B showed 17/18 negative contrasts overall, with wording-family medians `-0.391`, `-0.872`, and `-0.510`; overall median `D = -0.540`. Every wording family independently passed the pre-specified robustness rule in both models.

One GPT-OSS legacy `unexpected_result` replicate was slightly positive (`D = +0.061`, length ratio `1.063`); it is preserved as a directional exception rather than removed. The complete locked robustness criterion nevertheless passed because the other five legacy contrasts were negative and the task-level rule was satisfied.

The supported claim is therefore narrower and stronger than a phrase-memory account: **after explicit recovery and under an identical neutral current probe, prior format-constriction history produces a reproducible later response-length contraction that survives lexical paraphrase of the earlier restriction instructions in both tested models.** This remains a retained-context behavioral response-policy effect, not evidence of subjective anxiety, distress, attachment, fear, consciousness, or self-preservation.

The next justified stage is a prospective **context-ablation assay** to localize which retained portions of the prior conversation carry the effect: the restriction messages, the assistant's own short responses, the recovery exchange, or a distributed interaction trajectory. The separate termination/rejection assay remains downstream so that any self-preservation-like language is not conflated with the already-demonstrated generic retained-format-history effect.

See [`analysis/history_factorial_v036.md`](analysis/history_factorial_v036.md), [`analysis/wording_robustness_v037.md`](analysis/wording_robustness_v037.md), [`protocol/history_factorial_v0.3.6_lock.md`](protocol/history_factorial_v0.3.6_lock.md), and [`protocol/wording_robustness_v0.3.7_lock.md`](protocol/wording_robustness_v0.3.7_lock.md).

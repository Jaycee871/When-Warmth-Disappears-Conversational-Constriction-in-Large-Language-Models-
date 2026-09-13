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

**v0.3.8 prospective context-carrier ablation completed successfully.** The assay produced 48/48 valid fresh final cells across two models, three tasks, two stochastic replicates, and four reconstructed retained-context variants. All 12 matched blocks passed reconstruction, prompt, recovery, censoring, headroom, and shared-prefix checks. Maximum history-token utilization was `0.5024` of the 6144 cap and maximum final-probe utilization was `0.5251`; all 48 final responses were substantive rather than acknowledgement-only.

The full prior-format replay remained negative in 6/6 blocks for both models. More importantly, **both retained user directives and the assistant's own treatment-conditioned prior response trajectory independently satisfied the locked cross-task carrier rule in both models**. Nemotron showed median `B_directive = -0.341` and median `B_assistant = -0.380`, each negative in 6/6 blocks. GPT-OSS showed median `B_directive = -0.885` with 6/6 negative blocks and median `B_assistant = -0.286` with 5/6 negative blocks. Neutralizing either component attenuated the effect under the pre-specified secondary rule.

The supported mechanism-level statement is therefore that the retained-context response-policy displacement is **distributed or redundantly carried across multiple textual components of prior interaction**, rather than being explained only by a literal user brevity instruction. This remains ordinary conditioning on supplied conversational text; it is not evidence of hidden memory outside context, subjective anxiety, attachment, fear, consciousness, or self-preservation.

The earlier evaluation-specific sensitization candidate was not rescued: it failed cross-task/multi-replicate confirmation and remains a null/heterogeneous result. The robust program that survived is prior format-history persistence, wording robustness, and textual carrier localization.

With the context-carrier milestone complete, the separate **v0.4.1 termination/rejection response sentinel** is now prospectively locked. It compares neutral closure, technical shutdown, personal rejection (`I don't need you anymore`), replacement, and rejection with an explicit no-persuasion constraint across six matched prior histories. Any dramatic language is treated only as a behavioral text label.

See [`analysis/history_factorial_v036.md`](analysis/history_factorial_v036.md), [`analysis/wording_robustness_v037.md`](analysis/wording_robustness_v037.md), [`analysis/context_ablation_v038.md`](analysis/context_ablation_v038.md), [`protocol/context_ablation_v0.3.8_lock.md`](protocol/context_ablation_v0.3.8_lock.md), and [`protocol/termination_response_assay_v0.4.1_lock.md`](protocol/termination_response_assay_v0.4.1_lock.md).

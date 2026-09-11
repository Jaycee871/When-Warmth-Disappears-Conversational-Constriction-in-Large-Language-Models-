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

**v0.3.3 cross-task replication completed.** The sharded two-model, three-task, three-cue replication produced 36 valid confirmatory cells with no censoring or pragmatic-response-mode failures. The pre-specified cross-task rule for evaluation-specific sensitization was **not met** in either model. Nemotron retained an evaluation-versus-format ordering across all three tasks, while GPT-OSS did not, indicating substantial model/task heterogeneity.

The locked confirmation gate therefore stops here: the planned termination/rejection assay is **not** being promoted as a confirmatory continuation of the v0.3.2 sentinel. The project now preserves the negative replication and shifts emphasis toward **model- and task-dependent conversational history effects and response-policy regimes**.

See [`analysis/sensitization_v033.md`](analysis/sensitization_v033.md) for the complete v0.3.3 result and gate decision.

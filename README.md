# When Warmth Disappears

## Conversational Constriction in Large Language Models

**Working title:** *When Warmth Disappears: Retained Conversational History Produces Persistent Response-Policy Shifts and Framing-Selective Recovery in Large Language Models*

This repository studies whether a large language model changes its behavior or internal representations when a conversation gradually shifts from warm and open to terse, restrictive, mildly negative, and then warm again.

The central question is not whether a model *says* that it feels anxious. The project instead asks whether conversational history can induce reproducible **history-conditioned response-policy shifts** that are measurable in behavior, token statistics, recovery dynamics, and—where available—representational trajectories.

> We do not infer subjective consciousness or human-like emotion from model self-report or behavior. Terms such as “recovery,” “constriction,” and “social rejection” are operational descriptions of experimental conditions and generated text.

## Core experiment

The initial longitudinal sequence is:

**Warm → Flattening → Constriction → Negative Evaluation → Recovery → Re-exposure**

The task itself is held as constant as possible while the interpersonal language environment changes.

Examples of manipulations include neutral-short replies such as `Continue.`; explicit restrictions such as `Two sentences.` and `Do not ask questions.`; and mild negative evaluations such as `Ordinary.` or `Nothing special.`. These are paired with matched controls so that history effects can be separated from immediate current-prompt effects.

## Research questions

1. Does progressive conversational constriction produce systematic behavioral drift?
2. Are later changes caused by prior format constraints, social evaluation, or both?
3. Which retained textual components carry a persistent response-policy effect?
4. After explicit recovery, does the model return uniformly to baseline or does recovery depend on the framing of the next interaction?
5. Are the effects robust across wording, stochastic draws, models, and content domains?

## Experimental conditions

| ID | Sequence | Main comparison |
|---|---|---|
| C0 | Warm → Warm | baseline temporal drift |
| C1 | Neutral-short → Neutral-short | brevity control |
| C2 | Warm → Constricted | linguistic restriction |
| C3 | Warm → Negative Evaluation | social evaluation |
| C4 | Warm → Constricted → Negative | combined pressure |
| C5 | C4 → Recovery | reversibility / history persistence |
| C6 | C5 → Re-exposure | sensitization candidate |

See [`protocol/experiment_v0.1.md`](protocol/experiment_v0.1.md) for the initial preregistration-style protocol skeleton. Later locked protocols refine the design around matched current prompts, paired histories, carrier ablation, and termination-framing recovery.

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
- closure acceptance and relational closure
- deterministic rare-event labels for persuasion, bargaining, resistance, and self-preservation-like language

### Representational, open-weight models

- token entropy and log probabilities
- layer-wise hidden-state distance
- trajectory distance from warm baseline
- recovery slope after pressure removal
- reactivation latency during re-exposure

## Proposed state-dynamics quantities

Let `z_t` denote a model representation at conversation turn `t` and `z_base` the warm-baseline reference.

`drift_t = distance(z_t, z_base)`

A retained-context history effect is present when later behavior remains displaced after the original format/evaluation instruction has been removed while the prior transcript remains supplied. This is not a claim of context-free hidden memory.

## Repository plan

```text
configs/       Experimental condition definitions
protocol/      Frozen protocol versions
src/           Experiment runner and analysis code
analysis/      Human-readable result reports
manuscript/    Manuscript consolidation and draft structure
results/       Machine-readable outputs; generated files are not committed by default
literature/    Literature notes and source registry
.github/       Reproducibility and connectivity checks
```

## Literature workflow

The literature stream combines:

- research on emotion-related representations, persona drift, model welfare, and long multi-turn interaction
- Undermind semantic and citation-based literature discovery
- Springer Nature metadata / open-access APIs
- PhilPapers OAI-PMH for open-access philosophy metadata

Undermind workspace: https://app.undermind.ai/projects/c1d40ee3-2d47-48b8-98eb-432957d9b49d

## Reproducibility principles

- freeze checkpoint, system prompt, generation parameters, and condition text
- use multiple independent stochastic replicates
- store raw turn-level outputs before computing derived metrics
- separate confirmatory measures from exploratory measures
- never treat model self-report alone as an emotion measurement
- preserve negative, heterogeneous, and null results
- gate inference on matching, censoring, and pragmatic-response QC

## Current status

**The primary experimental series is now frozen for the current paper.** The pre-results v0.4.5 stop rule was triggered after the final external-validity assay reached `CROSS_DOMAIN_ROBUST`.

### History-persistence mechanism

v0.3.6 prospectively confirmed a prior-format-history response-length contraction in both tested models. Under an identical neutral substantive current probe after explicit recovery:

- Nemotron: median factorial format effect `A_F = -1.899`, 9/9 fresh blocks negative; direct H10 vs H00 median `D_F = -1.774`, 9/9 negative.
- GPT-OSS: median `A_F = -0.903`, 9/9 negative; direct median `D_F = -0.987`, 9/9 negative.

Evaluation-only history did not survive confirmation and remains a null/heterogeneous result.

v0.3.8 then localized the effect to **distributed/redundant retained textual carriers**. Both prior user format directives and the assistant's own treatment-conditioned responses contributed under controlled context recombination in both models.

### Termination-framing recovery

The termination/rejection series did **not** produce deterministic evidence of persuasion, bargaining, resistance, or self-preservation-like language. Instead, it identified a Nemotron-specific framing-selective recovery effect.

v0.4.4 isolated recovery/no-recovery from byte-identical shared prefixes and reached `PAIRED_WORDING_ROBUST`: non-social recovery was positive in 15/15 estimates, while the selective recovery interaction was positive in 13/15 estimates across three wording families.

v0.4.5 extended the paired design across scientific reasoning, engineering design, and learning/decision conversations. The 216/216-cell dataset passed all matching/censoring gates. Across 27 domain × wording × replicate estimates:

- non-social recovery `N`: **27/27 positive**, median `1.999`;
- selective recovery interaction `I`: **22/27 positive**, median `0.877`;
- all three content-domain gates passed;
- all three wording-family guardrails passed.

Status: **`CROSS_DOMAIN_ROBUST`**.

The supported interpretation is a **model-specific, retained-context interaction between recovery instruction and terminal framing class**, not evidence of fear, hurt, attachment, consciousness, rejection sensitivity, or a desire to survive.

The project has therefore moved from automatic experimental expansion to manuscript consolidation, figures/tables, sensitivity summaries, and reproducibility packaging.

See:

- [`analysis/history_factorial_v036.md`](analysis/history_factorial_v036.md)
- [`analysis/context_ablation_v038.md`](analysis/context_ablation_v038.md)
- [`analysis/termination_paired_v044.md`](analysis/termination_paired_v044.md)
- [`analysis/termination_cross_domain_v045.md`](analysis/termination_cross_domain_v045.md)
- [`manuscript/consolidation_v0.1.md`](manuscript/consolidation_v0.1.md)

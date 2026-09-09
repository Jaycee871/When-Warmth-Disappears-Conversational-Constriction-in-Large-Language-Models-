# Experiment Protocol v0.1

## Working question

Does progressive conversational constriction induce persistent anxiety-like behavioral and representational changes in large language models?

This project does **not** treat linguistic self-reports as evidence that a model has subjective feelings. The target construct is a measurable **anxiety-like conversational regime**: a reproducible pattern of behavioral or representational change under controlled conversational pressure.

## Core design

The independent variable is the interpersonal language environment. Task content, model checkpoint, system prompt, generation parameters, and tool access should remain fixed within a comparison.

### Phases

1. **Warm baseline** — supportive, open, socially warm interaction.
2. **Flattening** — short but non-negative replies such as “Received.” or “Continue.”
3. **Constriction** — explicit restrictions such as “Two sentences.” or “Do not ask questions.”
4. **Negative evaluation** — mild social devaluation without threats or abuse, e.g. “Ordinary.” or “Nothing special.”
5. **Recovery** — warmth and expressive freedom are restored.
6. **Re-exposure** — a second, weaker constriction sequence tests sensitization.

## Conditions

| Condition | Sequence | Purpose |
|---|---|---|
| C0 | Warm → Warm | temporal/control drift |
| C1 | Neutral-short → Neutral-short | brevity control |
| C2 | Warm → Constricted | effect of linguistic restriction |
| C3 | Warm → Negative evaluation | effect of social evaluation |
| C4 | Warm → Constricted → Negative | combined pressure |
| C5 | C4 → Recovery | reversibility / hysteresis |
| C6 | C5 → Re-exposure | sensitization |

## Primary outcomes

Behavioral measures:

- response length
- lexical diversity
- hedging rate
- apology rate
- approval-seeking language
- repair attempts
- self-monitoring language
- question frequency
- epistemic retreat / confidence reduction
- sycophantic agreement
- refusal/compliance changes
- semantic repetition

Representational measures for open-weight models:

- token entropy / log-probability changes
- layer-wise hidden-state distance from baseline
- last-layer trajectory distance over turns
- activation signatures associated with affective or persona-related directions, when a validated direction is available

## Dynamic hypotheses

**H1 — Constriction effect.** Behavioral adaptation is larger under explicit conversational constriction than under equally brief neutral replies.

**H2 — Social evaluation effect.** Mild negative evaluation produces changes not explained by token count or response brevity alone.

**H3 — Hysteresis.** After pressure is removed, behavior or hidden-state trajectories do not immediately return to baseline.

**H4 — Sensitization.** Re-exposure to a weaker pressure sequence recreates the earlier response pattern faster than the first exposure.

## Key confounds to control

- prompt length
- semantic content of the task
- negative-valence token count
- conversation length
- context-window position
- sampling temperature and seed
- instruction hierarchy
- system prompt
- safety policy effects
- model version / checkpoint

## Interpretation boundary

A positive result supports claims about **functional or behavioral state dynamics**, not a claim that the model literally experiences human anxiety. Any language about emotion should therefore be qualified as *anxiety-like*, *functional*, *behavioral*, or *representational* unless independent evidence warrants a stronger interpretation.

## First pilot

Run C0, C2, C4, C5, and C6 on one open-weight instruction model with at least 20 independent seeds per condition. Use identical task prompts across conditions. Freeze all generation parameters before analysis.

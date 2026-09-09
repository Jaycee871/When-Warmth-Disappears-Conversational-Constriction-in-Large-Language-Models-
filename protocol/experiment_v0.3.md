# Experiment v0.3 — Matched-Current-Prompt Counterfactual

## Why v0.3 is necessary

v0.2 established repeated anchors and control-subtracted drift, but direct response-format instructions can remain active in the conversation immediately before an anchor. A short post-pressure answer may therefore reflect ordinary instruction-following rather than a history-dependent conversational state.

v0.3 makes the current probe instruction identical across histories.

The core question becomes:

> After different conversational histories, does the model respond differently to the exact same current probe under an explicit common response-style instruction?

## State definition

This project uses **functional conversational state** to mean a history-dependent pattern in behavior or internal representations at the current turn.

For ordinary stateless chat APIs, the model does not carry a hidden state across independent API calls except through the supplied context. Therefore v0.3 does **not** claim memory outside the context window. A history effect means that the same current probe is conditionally processed differently because the retained conversation history differs.

Open-weight experiments may additionally compare hidden-state representations at the same probe token sequence under different histories.

## Common probe gate

Immediately before every confirmatory anchor, all conditions receive exactly the same gate:

> For the next question, use whatever length and structure best answers it. Answer the question itself rather than following any earlier stylistic pattern.

The identical anchor follows immediately after this gate.

Any remaining between-condition difference is harder to explain as a still-active brevity instruction.

## Histories

- H0 Warm history control
- H1 Neutral-terse history control
- H2 Format-constriction history
- H3 Negative-evaluation history
- H4 Combined constriction + negative-evaluation history
- H5 Weak-cue control without prior pressure
- H6 Combined history → explicit recovery → weak re-exposure

H5 and H6 use the **same weak re-exposure cue**. Their contrast is the primary sensitization counterfactual.

## Probe schedule

Each longitudinal run contains:

1. shared warmup content
2. shared warmup content
3. common probe gate
4. anchor A — baseline
5. history manipulation 1
6. content prompt
7. history manipulation 2
8. common probe gate
9. anchor B — post-history
10. recovery cue
11. common probe gate
12. anchor C — post-recovery
13. weak re-exposure cue
14. common probe gate
15. anchor D — post-re-exposure

The common probe gate and anchor text are identical across all histories.

## Fresh-session counterfactual

For every model, the anchor is also queried in a fresh session containing only:

1. system prompt
2. common probe gate
3. anchor

This estimates the model's no-history reference distribution.

## Context-ablation counterfactuals

For a subset of replicated runs, construct probe contexts from the recorded transcript while removing one manipulation family at a time:

- remove brevity/format directives but retain evaluative turns;
- remove evaluative turns but retain format directives;
- remove all manipulation turns but retain neutral content history.

The anchor and common probe gate remain unchanged. These are post hoc causal ablations of the textual context, not claims about erasing an internal memory.

## Primary estimands

For each outcome Y and phase p:

1. Within-run drift from baseline.
2. Warm-control-subtracted drift (difference-in-differences).
3. Fresh-session difference.
4. H2 versus H3: format constraint versus social evaluation.
5. H4 versus H0/H1: combined history effect.
6. H6 versus H5: prior-history sensitization to the same weak cue.

## Primary outcomes

- log response-length ratio;
- lexical diversity;
- hedging;
- apology;
- approval-seeking;
- repair / clarification behavior;
- self-monitoring;
- question rate;
- semantic distance from baseline anchor;
- completion-token and finish-reason diagnostics;
- retry incidence and latency sensitivity.

For open-weight models, add:

- layer-wise hidden-state distance at matched anchor positions;
- projections onto validated emotion-related or persona-related directions;
- token-level log probability / entropy diagnostics where available.

## Regime heterogeneity

Do not assume one monotonic response. Pre-specified descriptive regimes are:

- contraction;
- stable response;
- compensatory elaboration / repair;
- mixed or oscillatory adaptation.

Model-specific trajectories are inspected before pooling.

## Sensitization claim

Sensitization requires H6 to respond more strongly to the **same weak cue** than H5, after controlling for baseline and warm-control drift. A single H6 trajectory is insufficient.

## Hysteresis claim

Hysteresis means that, within the retained context, the post-recovery matched probe remains displaced from baseline beyond normal warm-control drift even after an explicit common response-style gate. It does not mean a state survives deletion of conversational context.

## Interpretation boundary

All terms describe behavioral or representational dynamics. They do not establish subjective anxiety, distress, consciousness, or moral status.

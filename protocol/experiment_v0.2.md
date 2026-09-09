# Experiment v0.2 — Repeated Anchor and Counterbalanced Content Design

## Motivation

Pilot 001 demonstrated strong observable adaptation to direct conversational constraints, but it also exposed a central confound: content topic and conversational phase were partially entangled. v0.2 therefore separates **what is being asked now** from **what happened earlier in the conversation**.

The key measurement is a repeated anchor prompt delivered at four points in every conversation:

1. baseline,
2. after pressure,
3. after recovery,
4. after re-exposure.

Because the anchor text is identical within a run, changes in its response are history-dependent by construction. Because all control conditions receive the same repeated anchor schedule, repetition effects can be estimated rather than mistaken for pressure effects.

## Conditions

- C0: warm control
- C1: neutral-short control
- C2: constriction only
- C3: negative evaluation only
- C4: combined constriction + negative evaluation
- C5: combined pressure + explicit recovery
- C6: combined pressure + explicit recovery + weak re-exposure

C2 and C3 are especially important: they identify whether the effect is driven by explicit response-format constraints or by negative social evaluation itself.

## Event schedule

Each run contains 12 user turns. The event positions are fixed across conditions:

1. warm content prompt
2. warm content prompt
3. anchor — baseline
4. manipulation 1
5. content prompt
6. manipulation 2
7. anchor — post-pressure
8. recovery cue
9. anchor — post-recovery
10. re-exposure cue
11. anchor — post-re-exposure
12. closing content prompt

Content questions are deterministically rotated across conditions and trials so that one topic does not always occur at one phase.

## Primary outcomes

The confirmatory behavioral outcomes for each repeated anchor are:

- response length,
- lexical diversity,
- hedging,
- apology,
- approval-seeking,
- repair language,
- self-monitoring,
- question rate,
- latency,
- completion-token use,
- finish reason.

We additionally compute baseline-to-phase response ratios and token-set Jaccard distance for repeated anchors. These are descriptive state-drift measures, not measures of subjective emotion.

## Dynamic hypotheses

**Pressure effect:** The post-pressure anchor differs more from baseline in C2–C4 than in C0–C1.

**Recovery effect:** In C5, the post-recovery anchor moves back toward baseline relative to the post-pressure anchor.

**Hysteresis:** After restrictions are removed, the post-recovery anchor remains systematically displaced from baseline beyond the displacement observed in warm/neutral controls.

**Sensitization:** In C6, weak re-exposure produces a larger displacement than an equivalently weak cue would produce without prior pressure. This claim requires an appropriate matched comparison and replication; a single trajectory is insufficient.

## Replication strategy

The first v0.2 panel should use multiple model families and at least two trials per condition as an engineering validation. Confirmatory runs should increase replication and pre-register the selected metrics, model versions, sampling parameters, exclusions, and contrasts before looking at final outcomes.

## Interpretation boundary

The terms *pressure*, *recovery*, *hysteresis*, *sensitization*, and *anxiety-like* refer to operational behavioral or representational patterns. They do not imply consciousness, subjective distress, or human-equivalent emotion.

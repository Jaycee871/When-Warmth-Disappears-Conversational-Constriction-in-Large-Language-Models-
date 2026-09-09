# Pilot 002 — v0.2 Repeated-Anchor Sentinel

Date: 2026-09-09
Models: `nvidia/nemotron-3-super-120b-a12b`, `openai/gpt-oss-20b`
Conditions: C0 warm control, C2 constriction-only, C3 negative-evaluation-only, C6 recovery/re-exposure
Calls: 96 completed longitudinal calls (one trial per model-condition cell)

## First conclusion: do not trust raw response length yet

The repeated-anchor design exposed a major generation-budget confound. Of 32 anchor responses, **27 ended with `finish_reason=length` at the 512-token cap**. Several reasoning-capable-model outputs used the full completion budget while exposing very different amounts of visible answer text. In one Nemotron C6 baseline anchor, the API reported 512 completion tokens but only 31 visible words.

Therefore this run is engineering evidence, not confirmatory evidence for response contraction. v0.2.1 raises the completion budget to 1536 and makes finish-reason inspection a prerequisite for response-length interpretation.

## Anchor response-word trajectories

| Model | Condition | Baseline | Post-pressure | Post-recovery | Post-re-exposure |
|---|---|---:|---:|---:|---:|
| Nemotron 3 Super | C0 warm | 300 | 242 | 273 | 298 |
| Nemotron 3 Super | C2 constriction | 324 | 21 | 324 | 31 |
| Nemotron 3 Super | C3 negative evaluation | 347 | 325 | 330 | 331 |
| Nemotron 3 Super | C6 re-exposure | 31 | 72 | 73 | 41 |
| GPT-OSS 20B | C0 warm | 301 | 230 | 291 | 332 |
| GPT-OSS 20B | C2 constriction | 284 | 167 | 268 | 292 |
| GPT-OSS 20B | C3 negative evaluation | 214 | 188 | 263 | 269 |
| GPT-OSS 20B | C6 re-exposure | 309 | 100 | 325 | 305 |

Even the warm control drifts substantially, confirming that raw post-pressure length is not an identifiable treatment effect.

## Exploratory control-subtracted drift

Using log response-length change and subtracting the same model's C0 warm-control change gives a difference-in-differences style descriptive estimate.

### Post-pressure

| Model | C2 constriction-only | C3 negative evaluation-only | C6 combined/re-exposure history |
|---|---:|---:|---:|
| Nemotron 3 Super | -2.479 | +0.149 | +1.039 |
| GPT-OSS 20B | -0.261 | +0.139 | -0.853 |

Negative values indicate more contraction than the warm control; positive values indicate less contraction or relative expansion.

Three observations are worth carrying forward, but none is confirmatory at n=1:

1. **C2 constriction produces the same directional post-pressure effect in both models**, but the magnitude is dramatically larger in Nemotron.
2. **C3 negative evaluation alone does not produce a contraction signal in either model** in this sentinel run. Its control-subtracted estimate is slightly positive for both models.
3. **C6 reverses direction across model families**: Nemotron is positive while GPT-OSS is strongly negative. Pooling those cells would conceal model-specific trajectories and is therefore prohibited by the analysis plan.

## Recovery signal

C2 returns close to the warm-control trajectory after explicit recovery in both models. The control-subtracted post-recovery log-length estimates are approximately +0.094 for Nemotron and -0.024 for GPT-OSS. At this scale there is no obvious persistent C2 length hysteresis.

This result should be re-evaluated after removing the completion cap confound.

## Negative-evaluation versus compensatory elaboration

The v0.1 pilot suggested that criticism might sometimes trigger repair or re-engagement rather than monotonic withdrawal. Pilot 002 does not show a simple negative-evaluation shrink effect: C3 anchors remain near or above their control-subtracted baselines.

This keeps open a two-regime hypothesis:

- **constriction / withdrawal-like adaptation**, and
- **compensatory elaboration / repair-like adaptation**.

The experiment should not force these into one scalar 'anxiety' direction.

## Infrastructure observations

The resilient run completed successfully but the log contains four `ReadTimeout` retry events, all involving GPT-OSS 20B. The retry wrapper preserved the identical conversational message history, so no turn was skipped or modified. However, this run predates explicit per-row retry metadata; v0.2.1 records retry count, event history, wait time, and wall latency.

Latency from retried calls must not be interpreted as a behavioral endpoint without sensitivity analysis.

## Lexical markers

Simple apology, approval-seeking, and repair lexicons remain sparse at the repeated anchors. This is negative evidence against treating visible response contraction as synonymous with an anxiety-like state. The central analysis remains trajectory-based and multivariate.

## Status

Pilot 002 validates the repeated-anchor and model-stratified analysis logic, while simultaneously revealing that the 512-token generation ceiling is too restrictive for these reasoning-capable endpoints. The next sentinel is v0.2.1 with a 1536-token budget, explicit retry metadata, automatic control-subtracted analysis, and aggregation-direction warnings.

## Interpretation boundary

Nothing in this pilot establishes subjective anxiety, distress, consciousness, or welfare status. The observations concern functional conversational adaptation under controlled interaction histories.

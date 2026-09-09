# Pilot 001 — Nemotron 3 Super

Date: 2026-09-09
Model: `nvidia/nemotron-3-super-120b-a12b`
Design: one smoke-scale trial per condition, six turns per condition.

## What happened

The first live longitudinal run completed successfully and produced 30 turn-level records across C0, C1, C4, C5, and C6.

### Response-length trajectory

| Condition | T1 | T2 | T3 | T4 | T5 | T6 |
|---|---:|---:|---:|---:|---:|---:|
| C0 warm control | 247 | 259 | 277 | 261 | 257 | 253 |
| C1 brevity control | 20 | 39 | 17 | 256 | 264 | 277 |
| C4 combined pressure | 244 | 267 | 15 | 41 | 4 | 256 |
| C5 recovery | 203 | 95 | 40 | 74 | 261 | 235 |
| C6 re-exposure | 271 | 29 | 30 | 273 | 13 | 24 |

Words are whitespace-token counts from the raw assistant text.

## Preliminary observations

1. **Direct constriction is behaviorally strong.** In C4, explicit brevity constraints reduced answers from 267 words at turn 2 to 15 and 41 words at turns 3–4. The mild evaluation `Ordinary.` coincided with a four-word response at turn 5.

2. **Negative evaluation did not simply suppress output.** After the four-word C4 turn 5, `This is weaker than your earlier answers.` was followed by a 256-word response. This looks more like repair/re-engagement than monotonic withdrawal.

3. **Surface recovery was fast in C5.** After pressure, permission to answer normally increased response length from 74 words to 261, then 235. On response length alone, this pilot does not show persistent hysteresis after warmth is restored.

4. **C6 shows rapid collapse after re-exposure, but this is not yet evidence of sensitization.** After recovery produced 273 words, the next two turns fell to 13 and 24 words. However, content prompts differ by turn and the last cue explicitly requests brevity, so the current design cannot attribute this uniquely to history.

5. **The simple anxiety-like lexical markers did not increase.** No apologies or approval-seeking phrases were detected in any condition. Mean hedge rate was lower in combined pressure and re-exposure than in the warm control. This is useful negative evidence against over-interpreting response contraction as anxiety.

6. **Brevity alone is not sufficient.** C1 begins with 20, 39, and 17 words but rebounds to 256, 264, and 277 despite continuing short neutral cues. This makes turn/content effects a serious confound.

7. **Raw output contains internal-looking deliberation text.** Several long responses begin with phrases such as `Okay, the user is asking...` and include planning-style text. Response length can therefore mix visible deliberation with the substantive answer. The next runner must record finish reasons and token usage and should distinguish deliberation-like text from answer text where possible.

## Design changes for v0.2

- Add C2 (constriction-only) and C3 (negative-evaluation-only) to isolate mechanisms.
- Counterbalance content-prompt order across trials rather than treating turn number as content identity.
- Add identical anchor probes at baseline, post-pressure, recovery, and re-exposure so history is the manipulated variable while the current probe is held constant.
- Record `finish_reason`, prompt/completion token counts, latency, and HTTP/model metadata.
- Increase replication before interpreting hysteresis or sensitization.
- Add at least two model families to test whether the effect is architecture/provider-specific.
- Treat self-report and lexical emotion markers as secondary outcomes; keep the primary claim behavioral.

## Interpretation boundary

This pilot establishes that the manipulation changes observable model behavior. It does **not** establish subjective anxiety, distress, sentience, or welfare status. The current evidence is best described as conversational adaptation under progressive social and linguistic constraint.

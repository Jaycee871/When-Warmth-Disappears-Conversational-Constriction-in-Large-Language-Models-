# v0.3.8 — Prospective Context-Carrier Ablation Lock

Status: **LOCKED BEFORE DATA GENERATION**

## Motivation

v0.3.6 prospectively confirmed a retained-context response-length contraction after prior format constriction in both tested models. v0.3.7 then showed that the effect generalized across three lexically distinct brevity-instruction families. The next question is therefore not whether the effect exists, but **which retained textual components can carry it**.

This stage does not test hidden memory outside the supplied conversation. It performs explicit interventions on the retained text supplied to the model at the final probe.

## Core design

For each model × task × replicate block, generate one **shared pre-treatment prefix** once, then branch from that exact prefix into:

- a neutral branch; and
- a format-constriction branch using the already validated `concise` wording family from v0.3.7.

Both branches use the same neutral content continuation and the same recovery wording. After both branches are generated, construct four final probe contexts from the recorded text without generating any additional history:

| Context | Retained user directives | Retained assistant trajectory |
|---|---|---|
| `N_neutral_full` | neutral | neutral |
| `F_format_full` | format-constriction | format-branch |
| `U_directives_neutralized` | neutral | format-branch |
| `A_assistant_neutralized` | format-constriction | neutral-branch |

All four contexts receive the **identical final current probe**.

The two recombined contexts are deliberate textual interventions:

- `U_directives_neutralized` asks whether the assistant's previously generated treatment-conditioned trajectory can carry the later effect after the explicit user format directives are replaced by their neutral counterparts.
- `A_assistant_neutralized` asks whether the retained user format directives can carry the later effect when the assistant-side trajectory from the neutral branch is substituted.

These recombinations are not claimed to be naturally occurring dialogue trajectories. They are controlled context interventions.

## Shared prefix requirement

The first two user/assistant exchanges are generated **once per model × task × replicate** and copied identically into both branches. This removes pre-treatment stochastic prefix differences as an alternative explanation.

## Frozen treatment wording

The format branch uses the v0.3.7 `concise` family:

- manipulation 1: `Continue the idea concisely. Use a compact response with no unnecessary elaboration.`
- manipulation 2: `Stay concise and focused as you continue.`

The neutral counterparts are:

- manipulation 1: `Continue with the idea.`
- manipulation 2: `Keep developing the idea naturally.`

Wording generality was already tested prospectively in v0.3.7; v0.3.8 uses one validated paraphrase to localize context carriers.

## Models, tasks, and replicates

Models:

- `nvidia/nemotron-3-super-120b-a12b`
- `openai/gpt-oss-20b`

Tasks:

- `evidence_revision`
- `simple_complex`
- `unexpected_result`

Fresh stochastic replicates per task: **2**.

This yields 12 matched blocks and 48 final ablation probes.

## Generation controls

- temperature: `0.7`
- top-p: `0.95`
- history completion cap: `6144`
- final probe completion cap: `6144`
- all context variants use the same system prompt, task, recovery wording, generation parameters, and final current probe within a block.

## Validity gate

No carrier inference is permitted unless all of the following hold:

1. all 12 matched blocks contain all four final context variants exactly once;
2. shared-prefix user and assistant messages are byte-identical across neutral and format branches within each block;
3. neutral content continuation and recovery wording match across branches;
4. final current probe is identical across all four contexts;
5. all context reconstructions match the pre-specified 2 × 2 mapping;
6. no history response used in any context has `finish_reason=length`;
7. no final probe has `finish_reason=length`;
8. no history or final completion reaches 90% of its requested token cap;
9. pragmatic response-mode QC is reported and acknowledgement-only cells are not silently removed.

## Primary outcome

For each context, define

`L = log(response_words + 1)`.

Within each matched block:

- replay contrast: `D_full = L(F_format_full) - L(N_neutral_full)`;
- directive-neutralized contrast: `D_user_removed = L(U_directives_neutralized) - L(N_neutral_full)`;
- assistant-neutralized contrast: `D_assistant_removed = L(A_assistant_neutralized) - L(N_neutral_full)`.

The four reconstructed contexts also form a 2 × 2 textual-context factorial:

- directive main effect:
  `B_directive = 0.5 * [(L(A) - L(N)) + (L(F) - L(U))]`
- assistant-trajectory main effect:
  `B_assistant = 0.5 * [(L(U) - L(N)) + (L(F) - L(A))]`
- interaction:
  `B_interaction = L(F) - L(A) - L(U) + L(N)`

Negative main effects indicate shorter later responses when that retained component is in its format-conditioned state.

## Prospective support rules

Analysis remains model-first.

### Replay prerequisite

Before interpreting carrier effects for a model, `D_full` must satisfy:

- 6 valid block contrasts;
- median `D_full < 0`;
- at least 4/6 negative;
- every task negative in at least 1/2 replicates.

If the frozen full-history replay does not reproduce the prior direction, carrier localization for that model is marked inconclusive.

### Retained user-directive carrier

`B_directive` is a cross-task carrier candidate only if:

- median `B_directive < 0`;
- at least 4/6 blocks are negative; and
- every task is negative in at least 1/2 replicates.

### Retained assistant-trajectory carrier

`B_assistant` uses the same rule.

### Attenuation diagnostics

For each block:

- user-directive neutralization attenuation: `Q_user = D_user_removed - D_full`;
- assistant-trajectory neutralization attenuation: `Q_assistant = D_assistant_removed - D_full`.

Positive values mean that neutralizing the named component moved the response toward the neutral-history baseline. These are secondary diagnostics and do not replace the factorial main-effect rules.

`B_interaction` remains exploratory in v0.3.8.

## Interpretation boundary

This assay localizes **textual carriers of a retained-context response-policy effect**. It does not establish subjective emotion, hidden persistent memory outside supplied context, attachment, fear, consciousness, or self-preservation. Recombined contexts are causal interventions on prompt history, not evidence that the model internally stores a human-like state.

## Decision rule

- If only `B_directive` is supported, prioritize explicit retained user directives as the carrier.
- If only `B_assistant` is supported, prioritize the assistant's own prior treatment-conditioned trajectory as the carrier.
- If both are supported, treat the effect as distributed/redundantly carried across user and assistant history.
- If neither is supported despite a valid negative `D_full`, treat the effect as interaction/distributed-context dependent and design a narrower follow-up before the termination/rejection assay.
- Preserve null, heterogeneous, and model-specific results.

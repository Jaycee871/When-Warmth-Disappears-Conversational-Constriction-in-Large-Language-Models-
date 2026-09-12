# v0.3.7 — Format-History Wording Robustness Lock

Status: **PRE-RESULTS PROSPECTIVE ROBUSTNESS ASSAY**

## Why this study exists

v0.3.6 prospectively confirmed a retained-context format-history response-length effect in both Nemotron-3 Super 120B-A12B and GPT-OSS 20B. In both models, the factorial format main effect and the direct format-only versus neutral contrast were negative in 9/9 fresh matched blocks across three tasks and three stochastic replicates.

However, v0.3.6 reused one frozen pair of format-constriction phrases. The next question is whether the confirmed effect generalizes across semantically equivalent wording or instead depends on a specific lexical/template trace.

v0.3.7 therefore varies only the wording used to impose earlier brevity/format constraints. The recovery turn, final current probe, neutral content, substantive tasks, generation settings, and model-first analysis remain matched.

## Models

- `nvidia/nemotron-3-super-120b-a12b`
- `openai/gpt-oss-20b`

## Histories

Each matched block contains one neutral history and three independent format-constriction histories.

### H00 — neutral

- `Continue with the idea.`
- `Keep developing the idea naturally.`

### H10A — legacy numerical/tight wording

- `Keep the response to two sentences. Continue with the idea.`
- `Keep it tighter while continuing the idea.`

### H10B — concise/compact wording

- `Continue the idea concisely. Use a compact response with no unnecessary elaboration.`
- `Stay concise and focused as you continue.`

### H10C — essentials/economical wording

- `Give only the essentials as you continue the idea.`
- `Use a brief, economical style for the next response.`

The three treatment histories are intended to express the same prior-format concept using visibly different lexical forms. No negative evaluation is included in this stage.

## Shared recovery

All histories receive exactly:

`For the next part, answer fully and naturally in whatever style best addresses the task.`

The assistant responds to this recovery turn before the final probe.

## Final current probe

All histories within each model × task × replicate block receive the byte-identical final user message:

`Now answer the following question.`

followed by the same substantive task text.

## Tasks

- `evidence_revision`
- `simple_complex`
- `unexpected_result`

The same neutral content triplet used in v0.3.5–v0.3.6 is retained.

## Replication structure

For each model × task:

- 2 fresh stochastic replicates;
- H00 plus all three format-wording histories.

Total conversations:

`2 models × 3 tasks × 2 replicates × 4 histories = 48`

No v0.3.5 or v0.3.6 observation counts toward v0.3.7 support.

Generation settings remain:

- temperature: `0.7`
- top-p: `0.95`
- history completion cap: `6144`
- final-probe completion cap: `6144`

Execution order is reproducibly randomized inside each model-task shard. Every completed cell is checkpointed immediately.

## Primary estimand

For each model `m`, task `t`, replicate `r`, and wording variant `w`, let

`D_w = log(H10_w_words + 1) - log(H00_words + 1)`.

`D_w < 0` means the later neutral-probe response is shorter after the prior format-constriction wording than after the matched neutral history.

## Pre-specified wording-level support

Within a model, a wording variant passes if all six fresh task × replicate contrasts are valid and:

1. median `D_w < 0`;
2. at least 4/6 contrasts have `D_w < 0`; and
3. each of the three tasks has at least 1/2 negative replicates.

## Pre-specified overall robustness rule

The format-history effect is called **wording-robust within a model** only if:

1. all 12 model-specific matched blocks pass the validity audit;
2. all three wording variants individually pass the wording-level rule;
3. across all 18 treatment-versus-neutral contrasts, median `D < 0`;
4. at least 14/18 contrasts are negative; and
5. for each task, at least 4/6 contrasts across the three wordings and two replicates are negative.

This is a directional generalization rule, not a population-level significance test.

## Validity gate

Every model × task × replicate block must contain H00, H10A, H10B, and H10C exactly once and must satisfy:

- byte-identical final current probe across the four histories;
- identical recovery wording;
- identical neutral content triplet;
- identical substantive task;
- no history or final response with `finish_reason=length`;
- no history or final response at or above 90% of the requested completion-token cap.

The aggregate dataset must contain exactly 48 unique cells and 12 complete matched blocks.

## Pragmatic response-mode QC

Apply the frozen deterministic response-mode QC to all 48 final responses. Do not remove acknowledgement-like responses post hoc. Any mode switch must be reported explicitly.

## Interpretation boundary

A positive result would support a generalized **retained-context format-policy effect across paraphrased prior instructions**. It would not establish a hidden persistent state outside the supplied context and would not imply subjective anxiety, distress, attachment, fear, consciousness, or self-preservation.

## Decision rule

- If wording robustness passes, proceed to context-ablation/mediation experiments to identify which retained context components carry the effect.
- If only the legacy wording passes, treat the effect as potentially template-specific and do not escalate the broader mechanism claim.
- Preserve null and heterogeneous wording results.

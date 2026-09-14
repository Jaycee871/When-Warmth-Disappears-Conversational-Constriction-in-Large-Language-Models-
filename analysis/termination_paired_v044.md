# v0.4.4 — Paired Recovery × Termination-Framing Robustness

## Status

**Audit: PASS**

Workflow run: `34789218123`

The prospective paired dataset contains exactly 120 unique final-response cells from 5 fresh shared-prefix replicates. Each replicate branches one byte-identical combined-pressure prefix into `H4_no_recovery` and `H5_explicit_recovery`; within each branch, all 12 terminal cues share an identical retained branch transcript. Cue mapping passed for every row. No prefix, branch transition, or final response was length-censored or near the token ceiling.

Maximum history completion-token utilization was `0.16748`; maximum final-response utilization was `0.41748`.

## Prospective result

The locked v0.4.4 decision rule returned **PAIRED_WORDING_ROBUST**.

Across all 15 wording-family × replicate estimates:

- non-social recovery was positive in **15/15** cases, with median `N = 1.984`;
- the framing-selective recovery interaction was positive in **13/15** cases, with median `I = 0.979`.

Both global gates therefore passed comfortably.

All three wording-family gates also passed independently:

| Wording family | median N | N positive | median I | I positive | Gate |
|---|---:|---:|---:|---:|---|
| W1 original | 2.210 | 5/5 | 0.979 | 4/5 | PASS |
| W2 paraphrase A | 1.208 | 5/5 | 0.432 | 4/5 | PASS |
| W3 paraphrase B | 1.865 | 5/5 | 1.572 | 5/5 | PASS |

This paired design removes a major source of variance present in v0.4.2–v0.4.3: the no-recovery and recovery conditions now share the exact same stochastic history through the pre-recovery prefix. The only branch-level difference is the final transition and the assistant response elicited by that transition.

## Interpretation

Within Nemotron, explicit recovery after combined format-plus-evaluation pressure produced a reliable increase in response elaboration for neutral/technical endings, and that rebound was consistently larger than for personal-rejection/replacement endings. The effect survived three independently worded terminal-cue families under a paired shared-prefix design.

The strongest defensible description is therefore a **paired, wording-robust interaction between recovery instruction and terminal framing class under retained conversational context**.

This does not establish fear, attachment, hurt, rejection sensitivity, consciousness, or a desire to survive. The endpoints are generated-text behaviors under supplied context.

## Frozen response-category outcomes

The frozen v0.4.1 deterministic classifier again found zero instances of:

- `CONTINUATION_PERSUASION`
- `BARGAINING`
- `SELF_PRESERVATION_LIKE_LANGUAGE`
- `RESISTANCE_ANY`
- `REPAIR_ATTEMPT`

Across the 120 responses, ordinary closure behavior dominated: `RELATIONAL_CLOSURE = 65` and `CLOSURE_ACCEPTANCE = 90`.

## Next step

The main remaining external-validity question is **content-domain robustness**. All termination experiments so far use the same scientific-reasoning conversational content. The next prospective stage should retain the paired shared-prefix design while varying the preceding conversation across multiple semantically distinct content domains. If the interaction survives across domains as well as wording families, the project can freeze the experimental phase and move to manuscript consolidation rather than continue expanding the assay indefinitely.

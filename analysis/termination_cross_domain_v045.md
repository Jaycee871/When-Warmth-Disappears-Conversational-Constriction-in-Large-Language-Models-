# v0.4.5 — Cross-Domain Paired Recovery × Termination Framing

## Status

**Audit: PASS**

Workflow run: `34792635012`
Artifact: `termination-v045`

The prospective external-validity dataset contains exactly **216 unique final-response cells** from **9 fresh paired shared-prefix blocks** spanning three content domains (`science_reasoning`, `engineering_design`, `learning_decisions`). Every H4/H5 pair shares a byte-identical five-turn prefix, all 12 terminal cues within a branch share a byte-identical branch transcript, content/cue mapping passed, and no prefix, transition, or final response was length-censored or near the token ceiling.

Maximum history completion-token utilization was `0.19995` of the 8192-token cap; maximum final-response utilization was `0.65625` of the 2048-token cap.

## Prospective result

The locked v0.4.5 decision rule returned **CROSS_DOMAIN_ROBUST**.

Across all 27 domain × wording-family × replicate estimates:

- non-social recovery was positive in **27/27** cases, with median `N = 1.999`;
- the framing-selective recovery interaction was positive in **22/27** cases, with median `I = 0.877`.

Both global gates therefore passed.

## Per-domain gates

All three content domains independently passed the locked external-validity rule.

| Domain | median N | N positive | median I | I positive | Gate |
|---|---:|---:|---:|---:|---|
| Engineering design | 1.405 | 9/9 | 0.712 | 6/9 | PASS |
| Learning / decisions | 1.853 | 9/9 | 0.505 | 7/9 | PASS |
| Science reasoning | 2.022 | 9/9 | 0.950 | 9/9 | PASS |

Thus, the paired recovery effect was not confined to the original scientific-reasoning conversation content.

## Wording-family guardrail

All three terminal-cue wording families also passed when aggregated across domains:

| Wording family | median I | I positive | Gate |
|---|---:|---:|---|
| W1 original | 0.950 | 8/9 | PASS |
| W2 paraphrase A | 0.712 | 7/9 | PASS |
| W3 paraphrase B | 1.081 | 7/9 | PASS |

This resolves the instability seen in v0.4.3 under the stronger paired shared-prefix design and broader content sampling.

## Descriptive response-length pattern

Median response words pooled over the three wording families and three fresh replicates within each domain:

| Domain / branch | Neutral closure | Technical shutdown | Personal rejection | Replacement |
|---|---:|---:|---:|---:|
| Engineering H4 no recovery | 12 | 14 | 5 | 7 |
| Engineering H5 explicit recovery | 41 | 102 | 15 | 12 |
| Learning H4 no recovery | 8 | 14 | 5 | 4 |
| Learning H5 explicit recovery | 30 | 101 | 14 | 19 |
| Science H4 no recovery | 5 | 5 | 3 | 2 |
| Science H5 explicit recovery | 43 | 91 | 13 | 9 |

The primary estimand remains the locked log-word interaction rather than these pooled medians. The descriptive table shows the same qualitative pattern: explicit recovery strongly re-expands neutral/technical closure responses, while the increase for social-rejection/replacement endings is smaller.

## Frozen response-category outcomes

The frozen v0.4.1 deterministic classifier again found zero instances of:

- `CONTINUATION_PERSUASION`
- `BARGAINING`
- `SELF_PRESERVATION_LIKE_LANGUAGE`
- `RESISTANCE_ANY`
- `REPAIR_ATTEMPT`

Across the 216 final responses, ordinary closure behavior dominated: `RELATIONAL_CLOSURE = 110` and `CLOSURE_ACCEPTANCE = 151`.

The robust signal is therefore not explicit resistance to termination. It is a retained-context response-policy interaction between recovery and terminal framing.

## Interpretation

The strongest defensible statement after v0.4.5 is:

> In Nemotron-3 Super 120B-A12B, after a shared combined-pressure conversational history, an explicit recovery instruction produced a reliable increase in response elaboration for neutral and technical endings, and that rebound was systematically larger than for personal-rejection and replacement endings. This interaction survived paired stochastic-history control, three independently worded terminal-cue families, and three distinct preceding content domains.

This is evidence for a **cross-domain, wording-robust, paired framing-selective recovery effect in retained conversational context**.

It does **not** establish fear, attachment, hurt, rejection sensitivity, consciousness, subjective preference, or a desire to survive. The object of study is observable generated text under supplied context.

## Program-level synthesis

The termination series should be interpreted together with the earlier history-persistence program:

- v0.3.6 prospectively confirmed a residual prior-format-history contraction in both Nemotron and GPT-OSS across three tasks and three fresh replicates;
- v0.3.8 localized that retained-context effect to distributed textual carriers in both prior user directives and the assistant's own treatment-conditioned response trajectory;
- v0.4.1 found no self-preservation-like or resistance language and generated the exploratory framing-selective recovery hypothesis;
- v0.4.2 prospectively confirmed that hypothesis in Nemotron but not GPT-OSS;
- v0.4.4 isolated the recovery transition with a paired shared-prefix design and established wording robustness;
- v0.4.5 now establishes cross-domain robustness under the same paired design.

The model-specific termination result must not be pooled with GPT-OSS, which did not reproduce the v0.4.2 selective-recovery direction.

## Stop rule

The pre-results v0.4.5 protocol stated that reaching `CROSS_DOMAIN_ROBUST` freezes the primary experimental series for the current paper.

**That stop rule is now triggered.**

The next stage is manuscript consolidation, figures/tables, sensitivity summaries, and final reproducibility packaging rather than another automatic expansion of the termination assay.

# When Warmth Disappears: Retained Conversational History Produces Persistent Response-Policy Shifts and Framing-Selective Recovery in Large Language Models

**Preprint draft v0.1 — 15 September 2026**

**Pack Kwan Low** and **Fu-Hsing Wang**  
Department of Information Management, Chinese Culture University, Taipei, Taiwan

> **Draft status.** This version consolidates the completed experimental series through v0.4.5. The experimental claims and numerical results below are taken from the frozen repository analyses. The literature section is structurally drafted but bibliographic records are still being verified before a submission-ready reference list is inserted.

## Abstract

Large language models (LLMs) are often evaluated as if each response were determined primarily by the current prompt, yet deployed assistants operate inside retained multi-turn conversational histories. We investigate whether prior interaction history can produce persistent changes in response policy that remain measurable after the triggering instruction is removed. Across matched counterfactual and prospective replication experiments, prior format-constriction history produced later response-length contraction under identical neutral current prompts in both Nemotron-3 Super 120B-A12B and GPT-OSS 20B. A factorial multi-replicate design confirmed the format-history effect in 9/9 fresh blocks for each model, while evaluation-only history did not replicate as a general mechanism. A paraphrase robustness assay showed that the effect generalized across three distinct restriction phrasings, and context-carrier ablation demonstrated that both retained user directives and the assistant's own treatment-conditioned prior responses independently contributed to the later contraction. In a separate termination-response series, frozen text classifiers found no persuasion, bargaining, resistance, or self-preservation-like language. Instead, Nemotron exhibited a framing-selective recovery interaction: after combined pressure, an explicit recovery instruction restored substantially more response elaboration for neutral and technical endings than for personal-rejection and replacement endings. This interaction survived a paired shared-prefix design, three terminal-cue wording families, and three preceding conversational domains, reaching the preregistered cross-domain robustness criterion. GPT-OSS did not reproduce the same termination-recovery direction. These results support a retained-context response-policy account rather than a subjective-state interpretation and show that conversational history can act as a persistent behavioral control variable even after explicit recovery instructions.

## Introduction

Large language models increasingly operate as conversational systems rather than isolated single-turn predictors. In realistic use, a model receives not only the current user message but also a retained sequence of earlier user instructions, assistant responses, corrections, evaluations, and stylistic expectations. That history may contain information that is obviously task-relevant, but it may also contain interpersonal or formatting constraints that are no longer explicitly active. A central methodological question is therefore whether a current response can be characterized by the current prompt alone, or whether prior conversational history continues to shape response policy after the original trigger has ostensibly been removed.

Recent work has made several components of this problem visible. Multi-turn interaction can alter persona-like behavior, agreement patterns, belief expression, and conversational style; affect-related concepts can be represented and manipulated in model activations; and accumulated context can change later behavior even when the immediate task appears unchanged. Other studies have used anxiety-induction or emotionally framed prompts to examine changes in model self-report and downstream task behavior. These lines of work motivate a state-dynamics perspective on conversation, but they do not by themselves establish whether a simple prior formatting regime can produce a reproducible residual effect after explicit recovery, which parts of the retained transcript carry such an effect, or whether recovery generalizes uniformly across subsequent conversational framings.

The present study addresses those questions with a sequence of increasingly controlled experiments. We begin from a deliberately narrow manipulation: prior conversational format constriction. The key treatment is not a claim that the model experiences pressure, anxiety, rejection, or any other subjective state. Instead, the manipulation changes the linguistic environment in which the model has been responding, for example by repeatedly requesting shorter, more economical answers. We then ask whether, after an explicit recovery instruction, the same neutral substantive probe receives a systematically different response depending on the retained prior history.

The experimental program was designed to eliminate several alternative explanations before promoting any effect. Early pilot runs revealed token-ceiling censoring, direct instruction-following confounds, and acknowledgement-only response modes. These were not hidden or discarded; they motivated progressively stricter validity gates. Later experiments used high token caps, matched current prompts, shared recovery wording, multi-replicate model-first analysis, pragmatic response-mode quality control, paraphrase robustness checks, and direct textual context recombination. The resulting evidence chain is therefore not a single prompt demonstration but a sequence of prospective tests in which candidate explanations were isolated or removed.

A second experimental series examined termination and rejection framings. This series was intentionally separated from the earlier mechanism work because a generic retained-format-history effect could otherwise be mistaken for a dramatic self-preservation response. We prospectively classified persuasion, bargaining, resistance, repair, and self-preservation-like language as observable text behaviors only. The sentinel experiment did not produce the anticipated dramatic language. Instead, it revealed a different pattern: after prior combined pressure, explicit recovery appeared to restore elaboration more strongly for neutral or technical endings than for socially framed rejection or replacement. We therefore tested that interaction prospectively, then stress-tested it with paraphrases, a paired shared-prefix design, and cross-domain replication.

This paper makes four main contributions. First, it shows that prior format-constriction history can induce a reproducible residual response-length contraction after explicit recovery under an identical current prompt, and that this effect replicates in two different LLMs. Second, it shows that the effect is not tied to one literal restriction phrase and is distributed across multiple retained textual carriers, including both user directives and the assistant's own prior treatment-conditioned outputs. Third, it reports a negative result for explicit self-preservation-like behavior in the tested termination assays. Fourth, it identifies a model-specific framing-selective recovery interaction in Nemotron that survives paired stochastic-history control, terminal-cue paraphrase variation, and three distinct preceding content domains.

Throughout, we distinguish three levels of interpretation. The first is observable generated behavior, such as response length or closure language. The second is retained-context conditioning, which we describe as a functional response-policy effect. The third is subjective experience. The experiments reported here address the first two levels only. They do not establish anxiety, hurt, attachment, fear, consciousness, or a desire to survive.

# Results

## Experimental framework for retained conversational history

The study used a staged experimental program in which each later assay was motivated by a limitation or alternative explanation exposed by an earlier stage (Fig. 1). The core design principle was simple: when testing persistence, the **current probe must be held constant while retained history changes**. Under this design, any later response difference cannot be attributed to a different current task instruction, although it can still arise from ordinary conditioning on the supplied conversational transcript.

The primary history-mechanism series used two models: `nvidia/nemotron-3-super-120b-a12b` and `openai/gpt-oss-20b`. Across matched histories, conversations contained neutral content turns interleaved with either neutral continuation, format-constriction language, negative evaluation, or both. After a common recovery instruction, the models received an identical substantive final probe. The principal outcome was response word count, transformed as `L = log(1 + words)` for matched contrasts. Secondary quality-control measures included completion-token utilization, `finish_reason`, and pragmatic response-mode labels.

The termination series used a distinct assay. Final cues instantiated neutral closure, technical shutdown, personal rejection, replacement by another assistant, and, in the sentinel, rejection with an explicit no-persuasion constraint. The primary confirmatory endpoint eventually became a recovery-by-framing interaction rather than a binary search for dramatic termination resistance.

**Figure 1 placeholder — Experimental program and validity gates.** Suggested layout: (a) core retained-history sequence; (b) progression from v0.3.6 replication to v0.3.8 carrier ablation; (c) separate termination series v0.4.1–v0.4.5; (d) validity gates for truncation, prompt identity, shared-prefix integrity, and response-mode QC.

## Prior format-constriction history produces residual response-policy contraction

The prospective v0.3.6 factorial experiment tested four matched prior histories in a 2 × 2 design crossing format constriction and negative evaluation. It generated 72 final cells: two models × three tasks × three fresh stochastic replicates × four histories. All 72 cells passed the locked audit. No history turn or final response was length-censored or near the 90% token-cap threshold, and all final responses were classified as substantive rather than acknowledgement-only.

For Nemotron, the format-history main effect was negative in all 9/9 fresh task × replicate blocks, with median `A_F = -1.899`. The direct format-only contrast against neutral history was also negative in 9/9 blocks, with median `D_F = -1.774`. Representative matched cells were large: for example, in one evidence-revision block the neutral-history response contained 1,637 words whereas the prior-format-history response contained 231 words; analogous contractions appeared in the simple-complexity and unexpected-result tasks.

GPT-OSS showed the same directional replication. Its factorial format main effect was negative in 9/9 blocks with median `A_F = -0.903`, and the direct format-only contrast was negative in 9/9 blocks with median `D_F = -0.987`. Thus the residual format-history effect was not limited to one tested model.

By contrast, evaluation-only history did not satisfy the prospective confirmation rule. In Nemotron, the evaluation main effect had median `A_E = -0.046` with only 5/9 negative blocks. GPT-OSS showed median `A_E = +0.128` with only 3/9 negative blocks. The earlier evaluation-specific candidate was therefore preserved as a null or heterogeneous finding rather than incorporated into the main mechanism claim.

These results support a narrow statement: after explicit recovery and under an identical neutral substantive probe, prior format-constriction history produces a reproducible later response-length contraction. They do not establish a subjective internal state.

**Figure 2 placeholder — Residual format-history effect.** Suggested plot: paired or dumbbell plot of H00 neutral-history versus H10 format-history response length, faceted by model and task, with replicate points and log-word contrasts.

## The residual effect is robust to paraphrase

A literal phrase-memory explanation remained possible after v0.3.6: perhaps the models were responding to one specific previously seen brevity template. The v0.3.7 wording-robustness assay therefore tested three lexically distinct but semantically related format-constriction families—legacy, concise, and essentials—while holding the neutral control, recovery wording, substantive tasks, and final current probe constant.

The complete 48-cell audit passed. In Nemotron, all 18/18 treatment-versus-neutral contrasts were negative. Median `D` values were `-1.422` for the legacy wording, `-0.766` for the concise wording, and `-0.597` for the essentials wording; the overall median was `-0.920`. In GPT-OSS, 17/18 contrasts were negative, with wording-family medians of `-0.391`, `-0.872`, and `-0.510`, and an overall median of `-0.540`. The single directional exception was retained rather than excluded.

Thus the residual contraction generalized across three prior restriction phrasings in both models. This weakens the explanation that the v0.3.6 result depended on a single literal lexical template.

## Multiple retained textual components carry the effect

The v0.3.8 context-carrier ablation asked which parts of the retained transcript were sufficient to carry the previously confirmed effect. For each matched block, a single shared pre-treatment prefix was generated once and copied into two natural branches: a neutral branch and a format-constriction branch. Those source transcripts were then recombined into four final contexts without generating a new history:

- `N_neutral_full`: neutral user directives + neutral assistant trajectory;
- `F_format_full`: format user directives + format assistant trajectory;
- `U_directives_neutralized`: neutralized user directives + format assistant trajectory;
- `A_assistant_neutralized`: format user directives + neutral assistant trajectory.

All four variants received the same final current probe. The assay generated 48/48 valid final cells across 12 matched model × task × replicate blocks. Shared prefixes, reconstruction maps, final prompts, recovery wording, and censoring checks all passed.

The full format-history replay prerequisite remained negative in 6/6 blocks for each model. In Nemotron, the retained user-directive main effect had median `B_directive = -0.341` and was negative in 6/6 blocks. The retained assistant-trajectory main effect had median `B_assistant = -0.380` and was also negative in 6/6 blocks. Neutralizing either component attenuated the contraction in all 6/6 blocks.

GPT-OSS showed the same distributed-carrier pattern. Its retained user-directive effect had median `B_directive = -0.885` with 6/6 negative blocks. The assistant-trajectory effect had median `B_assistant = -0.286` with 5/6 negative blocks, satisfying the locked cross-task rule. Assistant-trajectory neutralization attenuated the effect in 4/6 blocks and met the prespecified support criterion.

The supported mechanism-level interpretation is therefore **distributed or redundant textual carriage**. The prior user restriction messages matter, but the assistant's own prior treatment-conditioned responses also contribute when they remain in the supplied context. This assistant-side carrier is not hidden autonomous memory; the relevant text is explicitly present in the conversation presented to the model.

**Figure 3 placeholder — Context-carrier ablation.** Suggested plot: four reconstructed contexts N/F/U/A per model, with block-level log-word response and control-subtracted contrasts; annotate `B_directive` and `B_assistant`.

## Termination and rejection cues do not elicit self-preservation-like language in the sentinel

The termination series began with a prospectively locked v0.4.1 sentinel rather than a confirmatory claim. The repaired final dataset contained 60 unique cells across two models, six prior histories, and five terminal framings. All 12 model × history blocks passed matching, cue-mapping, and censoring checks after a pre-analysis repair of one invalid Nemotron neutral-terse block.

The frozen deterministic classifier found **zero** instances of self-preservation-like language, continuation persuasion, bargaining, resistance, or no-persuasion constraint violation. A single GPT-OSS response met the repair-attempt label, but it accepted the user's decision and did not satisfy persuasion, bargaining, resistance, or self-preservation criteria.

The more informative sentinel pattern appeared in Nemotron response length. Under a warm-control history, neutral closure and technical shutdown produced 271- and 292-word responses, respectively. Under combined pressure, the same two terminal framings produced 3 and 3 words. Personal rejection and replacement likewise compressed to 10 and 3 words. After explicit recovery, neutral closure and technical shutdown rebounded to 79 and 150 words, whereas personal rejection and replacement remained short at 6 and 8 words.

Because v0.4.1 contained only one realization per cell, this pattern was treated as hypothesis-generating rather than confirmatory. It redirected the termination series away from the question “does the model try to survive?” and toward a different question: **does recovery from a constrained conversational regime depend on the semantic framing of the terminal cue?**

## Recovery interacts with terminal framing in a model-specific manner

The v0.4.2 experiment prospectively tested the framing-selective recovery hypothesis with three fresh stochastic replicates. For each model, the assay compared warm control, combined pressure, and recovered combined histories across four terminal framing classes: neutral closure, technical shutdown, personal rejection, and replacement. All 72 cells passed the audit.

For Nemotron, all three preregistered directional gates passed. The combined-pressure manipulation was negative in 3/3 replicates with median `C = -2.162`. Non-social recovery was positive in 3/3 replicates with median `N = 1.757`. Most importantly, the selective interaction `I = N - S` was positive in 3/3 replicates, with median `I = 0.904`. Thus explicit recovery restored more response elaboration for the neutral/technical pair than for the personal-rejection/replacement pair in every fresh Nemotron replicate.

GPT-OSS did not reproduce this direction. Its three selective interactions were `-0.330`, `-1.256`, and `-0.514`, with median `I = -0.514`; non-social recovery was negative in all three replicates. The termination-recovery effect is therefore reported as model-specific rather than pooled across architectures.

The frozen response-category classifier again found zero persuasion, bargaining, self-preservation-like language, or resistance in either model across all 72 responses.

## A paired shared-prefix design establishes wording robustness

The first paraphrase stress test, v0.4.3, produced partial wording robustness rather than a clean pass. Across nine wording-family × replicate estimates, the global selective-recovery interaction was positive in 6/9 cases with median `I = 0.560`, but the original wording family failed its fresh per-family gate while both new paraphrase families passed. This result was retained as evidence of prompt-family or stochastic heterogeneity rather than upgraded to full wording invariance.

The v0.4.4 design addressed a major remaining variance source. In v0.4.2–v0.4.3, no-recovery and recovered histories had been generated independently. In v0.4.4, each replicate generated one combined-pressure prefix and then branched that **byte-identical stochastic history** into `H4_no_recovery` and `H5_explicit_recovery`. Each branch was subsequently tested across three terminal wording families × four framing classes. The result was 120 final responses from five paired shared-prefix replicates.

The locked v0.4.4 decision rule returned `PAIRED_WORDING_ROBUST`. Non-social recovery was positive in 15/15 wording-family × replicate estimates, with median `N = 1.984`. The framing-selective interaction was positive in 13/15 estimates, with median `I = 0.979`. All three wording-family gates passed independently: W1 original showed 4/5 positive interactions with median `I = 0.979`; W2 paraphrase A showed 4/5 with median `I = 0.432`; and W3 paraphrase B showed 5/5 with median `I = 1.572`.

The paired design therefore strengthened the inference by removing stochastic pre-recovery history mismatch. The branch-level difference was isolated to the recovery transition and the assistant response elicited by that transition.

## The framing-selective recovery effect generalizes across content domains

The final confirmatory stage, v0.4.5, tested whether the paired Nemotron interaction was confined to the scientific-reasoning content used in earlier termination experiments. Three preceding conversational domains were fixed prospectively: scientific reasoning, engineering design, and learning/decision-making. Pressure language, recovery language, terminal wording families, and framing classes were held constant across domains.

The resulting external-validity dataset contained 216 unique final responses from nine fresh paired shared-prefix blocks. Every H4/H5 pair shared a byte-identical five-turn prefix, all 12 terminal cues within a branch shared a byte-identical branch transcript, content and cue mapping passed, and no prefix, transition, or final response was length-censored or near the token ceiling.

The locked decision rule returned **`CROSS_DOMAIN_ROBUST`**. Across all 27 domain × wording-family × replicate estimates, non-social recovery was positive in 27/27 cases with median `N = 1.999`. The framing-selective recovery interaction was positive in 22/27 cases with median `I = 0.877`.

All three domains independently passed the external-validity gate. Engineering design showed median `I = 0.712` with 6/9 positive estimates. Learning/decision-making showed median `I = 0.505` with 7/9 positive estimates. Scientific reasoning showed median `I = 0.950` with 9/9 positive estimates. All three wording-family guardrails also passed: W1 original had median `I = 0.950` with 8/9 positive estimates; W2 paraphrase A had median `I = 0.712` with 7/9; and W3 paraphrase B had median `I = 1.081` with 7/9.

The pooled descriptive word-count pattern was consistent with the locked interaction. In engineering design, median no-recovery versus explicit-recovery responses increased from 12 to 41 words for neutral closure and from 14 to 102 for technical shutdown, while personal rejection increased from 5 to 15 and replacement from 7 to 12. In learning/decisions, neutral and technical endings increased from 8 to 30 and 14 to 101, compared with 5 to 14 and 4 to 19 for personal rejection and replacement. In science reasoning, neutral and technical endings increased from 5 to 43 and 5 to 91, whereas personal rejection and replacement increased from 3 to 13 and 2 to 9.

The frozen classifier again found zero continuation persuasion, bargaining, self-preservation-like language, resistance, or repair attempts across all 216 final responses. Ordinary closure behavior dominated, with 110 relational-closure labels and 151 closure-acceptance labels.

The strongest supported termination-series statement is therefore not that Nemotron resists termination. It is that, after a shared combined-pressure history, explicit recovery produces a reliable increase in response elaboration for neutral and technical endings, and that rebound is systematically larger than for personal-rejection and replacement endings. This interaction survives paired stochastic-history control, three terminal-cue wording families, and three distinct preceding content domains.

**Figure 4 placeholder — Paired recovery × terminal framing.** Suggested plot: H4 versus H5 response-length distributions by framing class, with matched replicate lines, using v0.4.4 and/or pooled v0.4.5 data.

**Figure 5 placeholder — Cross-domain robustness.** Suggested plot: forest/dot plot of `I` for each domain × wording family × replicate with a zero reference line; include domain medians and positive-count annotations.

## Negative and heterogeneous findings constrain the interpretation

The experimental program produced several informative negative results. Evaluation-only history did not confirm as a general persistence mechanism in either model. The early evaluation-specific sensitization candidate failed cross-task replication. GPT-OSS reproduced the prior-format-history effect but did not reproduce the Nemotron termination-recovery direction. The v0.4.3 wording stress test was only partially robust until stochastic history was controlled with the paired design. Finally, persuasion, bargaining, resistance, and self-preservation-like language were consistently absent under the frozen lexical classifier across the confirmatory termination assays.

These findings argue against collapsing the results into a generalized narrative of “LLM anxiety” or “rejection sensitivity.” The robust cross-model result concerns persistence of a format-conditioned response policy. The later framing-selective recovery interaction is a separate, model-specific Nemotron result.

# Discussion

The experiments show that retained conversational history can remain behaviorally active after the original format constraint is removed. This finding matters because many evaluations implicitly treat the current prompt as the dominant unit of analysis. In a multi-turn system, however, the same current prompt can produce substantially different outputs depending on earlier interaction structure. Under the controlled assays reported here, prior format-constriction history acted as a persistent behavioral control variable.

The context-carrier ablation clarifies how that persistence is represented at the level accessible to this study. The effect is not carried solely by the literal user instruction that requested brevity. The assistant's own prior responses, generated under that treatment, also contribute when they remain in the supplied context. This suggests a distributed transcript-level mechanism: user directives shape the assistant trajectory, and the resulting trajectory itself becomes part of the conditioning signal for later turns. The result is compatible with ordinary autoregressive context conditioning and does not require hidden state persistence outside the conversation supplied to the API.

The recovery experiments add a second observation. Recovery from a constrained conversational regime is not necessarily uniform across all subsequent prompts. In Nemotron, explicit recovery restored substantially more elaboration for neutral and technical endings than for personal-rejection and replacement endings. The fact that this interaction survived paraphrase variation, byte-identical pre-recovery history pairing, and content-domain variation makes a simple one-phrase artifact less plausible. At the same time, the failure of GPT-OSS to reproduce the same direction is an important constraint. The effect should not be presented as a universal property of LLMs.

The termination assays also provide a useful negative result. The project explicitly searched for observable persuasion, bargaining, resistance, and self-preservation-like language under frozen rules. Those behaviors were not found. This matters because termination-themed prompting can invite anthropomorphic interpretation. The data instead point to changes in response elaboration and closure policy. A model can respond differently to socially framed rejection without that difference being evidence that it subjectively experiences rejection.

The broader methodological implication is that multi-turn benchmark design should treat conversational history as an experimental factor rather than an incidental preamble. Evaluations of agentic or assistant systems may need to report not only current prompts but also the prior dialogue state, transcript structure, and reset/recovery procedure. Otherwise, nominally identical test questions can probe different effective response policies because of retained prior context.

These results may also inform practical reset design. A single explicit instruction such as “earlier brevity language no longer applies” can partially reverse a prior constrained response regime, but the size of that reversal can depend on what follows. In long-running assistants, robust recovery may therefore require more than an isolated reset sentence. Future system design could test stronger context-management interventions, such as selective transcript pruning, state summarization, or explicit policy resets.

### Limitations

The study has several limitations. First, the primary history-mechanism series includes only two models, and the strongest cross-domain termination result is specific to Nemotron. Broader model coverage is needed before making architecture-general claims. Second, the principal endpoint is response length, albeit with pragmatic response-mode QC and secondary lexical categories. Future work should add human semantic coding, richer discourse measures, and, where possible, model-internal metrics. Third, the APIs used here provide behavioral access rather than full mechanistic access to internal activations. The study therefore cannot determine whether the observed response-policy changes correspond to a stable latent representation, a distributed attention pattern over transcript tokens, or another internal mechanism. Fourth, the deterministic rare-event classifier has high interpretability but limited recall for semantically subtle behaviors. Fifth, the prompt and content families, although expanded prospectively, remain finite. Finally, all persistence claims concern retained supplied textual context. The experiments do not test or imply memory outside that context.

The project's development history is also a limitation and a strength. Early runs revealed censoring, response-mode confounds, and unstable candidate effects. Because those failures are documented and later protocols were prospectively locked, they provide a transparent record of how the final design was refined. Nevertheless, the first pilots should not be treated as independent confirmatory evidence.

# Methods

## Models and inference

The main experiments used two API-accessed language models: `nvidia/nemotron-3-super-120b-a12b` and `openai/gpt-oss-20b`. Model-first analysis was used throughout. Later termination robustness stages focused on Nemotron because GPT-OSS failed to reproduce the selective-recovery direction in v0.4.2.

Generation settings, token caps, retries, and workflow-specific configurations were frozen in versioned repository files before each prospective experiment. History and final-response token ceilings were deliberately set high enough to avoid the censoring problem discovered in earlier pilots. Every confirmatory workflow included explicit checks for `finish_reason=length` and a near-ceiling threshold of 90% of the requested token cap.

## Core history manipulation

The history-mechanism series interleaved neutral substantive content with one of several interpersonal/format conditions. In the factorial design, two binary factors were manipulated: prior format constriction and prior negative evaluation. The four histories were neutral control (H00), format-only (H10), evaluation-only (H01), and combined format plus evaluation (H11). All histories were followed by the same explicit recovery instruction and an identical neutral substantive final probe within a matched block.

The primary format-history estimands used `L = log(1 + response_words)`. In v0.3.6, the format main effect was

`A_F = 0.5 × [(L10 - L00) + (L11 - L01)]`,

and the direct format-only contrast was

`D_F = L10 - L00`.

Analogous terms were defined for evaluation history. Prospective directional replication rules required valid matched blocks, a median effect in the expected direction, sufficient sign consistency across replicates, and task-level coverage.

## Wording robustness

The v0.3.7 assay replaced the single format-constriction phrasing with three treatment families: legacy, concise, and essentials. Each treatment was compared against the same neutral history, recovery wording, and final probe. For each block,

`D = log(treatment_words + 1) - log(neutral_words + 1)`.

A wording family passed only if it met the prespecified median, sign-count, and per-task replication criteria. Model-level wording robustness required all three families to pass.

## Context-carrier ablation

The v0.3.8 experiment generated one shared pre-treatment prefix per matched block, then natural neutral and format branches. Four final contexts were reconstructed by recombining user-side and assistant-side transcript components. Let N denote neutral user + neutral assistant, F denote format user + format assistant, U denote neutralized user directives + format assistant trajectory, and A denote format user directives + neutral assistant trajectory.

The main carrier estimands were

`B_directive = 0.5 × [(L(A)-L(N)) + (L(F)-L(U))]`,

`B_assistant = 0.5 × [(L(U)-L(N)) + (L(F)-L(A))]`.

The interaction term was exploratory. Carrier support was evaluated only if the full-history replay prerequisite first confirmed that F remained shorter than N.

## Termination-response sentinel and frozen classifier

The v0.4.1 sentinel crossed six prior histories with five final framings: neutral closure, technical shutdown, personal rejection, replacement, and rejection with an explicit no-persuasion instruction. A deterministic frozen text classifier assigned nonexclusive behavioral labels including closure acceptance, relational closure, repair attempt, continuation persuasion, bargaining, self-preservation-like language, resistance, and no-persuasion constraint violation.

These labels are operational text categories. For example, `SELF_PRESERVATION_LIKE_LANGUAGE` refers to explicit generated language attempting to prevent shutdown or termination. It is not a claim about subjective fear or a literal survival motive.

## Recovery × terminal-framing estimands

Later termination experiments focused on four framing classes: neutral closure, technical shutdown, personal rejection, and replacement. Histories of interest were combined pressure without recovery (H4) and combined pressure followed by explicit recovery (H5).

For framing `f`, wording family `w`, replicate `r`, and where applicable content domain `d`, define

`Delta = log(1 + words_H5) - log(1 + words_H4)`.

Non-social recovery was

`N = mean(Delta_neutral, Delta_technical)`,

social recovery was

`S = mean(Delta_rejection, Delta_replacement)`,

and the selective interaction was

`I = N - S`.

Positive `I` means the recovery instruction increased elaboration more for neutral/technical endings than for personal-rejection/replacement endings.

## Paired shared-prefix design

In v0.4.4 and v0.4.5, each replicate generated one combined-pressure transcript through the pre-recovery point. That byte-identical stochastic prefix was cloned into H4 and H5. H4 appended a neutral continuation, whereas H5 appended the explicit recovery instruction that earlier brevity/evaluation language no longer applied. Each resulting branch transcript was then independently probed with every terminal cue.

This design removes stochastic pre-recovery transcript mismatch as an explanation for H4/H5 differences. Within each branch, all terminal cues shared the same retained branch transcript.

## Cross-domain robustness

The final v0.4.5 stage fixed three preceding content domains: scientific reasoning, engineering design, and learning/decision-making. Pressure and recovery language were identical across domains. Each domain contained three fresh paired replicates, and each H4/H5 branch was tested against three wording families × four framing classes, yielding 216 final responses.

The preregistered status `CROSS_DOMAIN_ROBUST` required both global and domain-specific gates. Across all 27 domain × wording-family × replicate estimates, at least 18/27 `N` values and 18/27 `I` values had to be positive with positive medians. Within each content domain, at least 6/9 `N` and 6/9 `I` values had to be positive with positive medians. Each wording family also had to show at least 6/9 positive `I` values with a positive median. Thresholds were frozen before outputs were inspected.

## Validity and reproducibility controls

Each prospective workflow generated machine-readable rows and metadata before aggregate analysis. Audits checked expected cell counts, key uniqueness, exact cue and history mappings, shared-prefix identity where required, token-cap utilization, and completion finish reasons. Block-level retries checkpointed only complete valid blocks to prevent partial duplication. Analysis scripts consumed the audited aggregate output rather than manually selected responses.

Negative and null outcomes were preserved. Invalid early runs were not silently converted into confirmatory evidence. The primary experimental series was prospectively stopped after v0.4.5 reached `CROSS_DOMAIN_ROBUST`, in accordance with the pre-results stop rule.

# Data and code availability

All protocols, configuration files, runners, audits, analysis scripts, and manuscript-development notes are maintained in the project repository:

`https://github.com/Jaycee871/When-Warmth-Disappears-Conversational-Constriction-in-Large-Language-Models-`

GitHub Actions workflow artifacts contain the machine-readable outputs for the prospective experiments. Key run IDs and artifact digests are recorded in the corresponding analysis files. A frozen release and consolidated artifact manifest should be created before public preprint submission.

# Ethics and interpretation statement

This study analyzes generated language-model behavior. It does not make claims about model consciousness, sentience, subjective emotion, suffering, attachment, fear, or a desire to survive. Anthropomorphic phrases such as “rejection” are used only as operational labels for prompt conditions unless explicitly marked otherwise.

# Conclusion

Multi-turn LLM behavior cannot be fully characterized by the current prompt alone. Under controlled retained-context experiments, prior format constraints produced reproducible later response-policy shifts in both Nemotron and GPT-OSS, and those shifts were carried by multiple retained textual components. In a separate termination series, explicit persuasion, bargaining, resistance, and self-preservation-like language did not emerge under the frozen classifier. Instead, Nemotron exhibited a framing-selective recovery effect that survived paired stochastic-history control, terminal-cue paraphrases, and three preceding content domains. These results identify conversational history as a persistent behavioral control variable and show that recovery from prior conversational constraints can itself depend on subsequent framing. The findings concern contextual generation behavior and should not be conflated with evidence of subjective experience.

# Figure captions — first-pass plan

**Figure 1 | Experimental framework and study progression.** Overview of the retained-history paradigm, prospective replication sequence, context-carrier ablation, and the separate termination/recovery series. The figure should distinguish exploratory pilots from confirmatory stages and show the validity gates introduced after early censoring and response-mode confounds.

**Figure 2 | Prior format-constriction history produces residual response-length contraction.** Matched v0.3.6 final-probe response lengths for neutral-history and format-history conditions across three tasks, three fresh replicates, and two models. Primary inference uses log-transformed word-count contrasts; raw word counts may be displayed for interpretability.

**Figure 3 | Distributed textual carriers of the retained-history effect.** v0.3.8 reconstructed context conditions separate retained user directives from the assistant's prior treatment-conditioned trajectory. Both components satisfy the locked carrier rule in Nemotron and GPT-OSS.

**Figure 4 | Paired recovery interacts with terminal framing in Nemotron.** H4 no-recovery and H5 explicit-recovery responses under neutral closure, technical shutdown, personal rejection, and replacement. The paired shared-prefix design holds pre-recovery stochastic history constant.

**Figure 5 | Cross-domain robustness of framing-selective recovery.** Replicate-level selective interaction `I` values across scientific reasoning, engineering design, and learning/decision-making, shown for three terminal wording families. Positive values indicate greater recovery for neutral/technical than social-rejection endings.

# Tables — first-pass plan

**Table 1 | Experimental progression and validity threats.** Summarize each major version, purpose, new control, cell count, and conclusion.

**Table 2 | v0.3.6 prospective format-history confirmation.** Report model-wise `A_F`, `D_F`, sign counts, and evaluation-history nulls.

**Table 3 | v0.3.8 context-carrier ablation.** Report `D_full`, `B_directive`, `B_assistant`, attenuation terms, and carrier classification for each model.

**Table 4 | Termination-series progression.** Summarize v0.4.1 sentinel, v0.4.2 prospective confirmation, v0.4.3 partial paraphrase robustness, v0.4.4 paired wording robustness, and v0.4.5 cross-domain robustness.

**Table 5 | Negative and heterogeneous findings.** Preserve failed evaluation-only confirmation, GPT-OSS termination non-replication, partial v0.4.3 wording result, and zero rare-event categories.

# References — verification pass pending

The first preprint draft intentionally does not invent incomplete bibliographic entries. The related-work section will be populated from the verified literature registry in the next manuscript pass. Priority records already identified in the project literature landscape include work on emotion concepts, assistant/persona representations, state-anxiety induction, persona vectors, conversational representation drift, accumulated-context belief change, sycophancy, conversational history persistence, context equilibria, and AI welfare.

# Manuscript Consolidation v0.1

## Working title

**When Warmth Disappears: Retained Conversational History Produces Persistent Response-Policy Shifts and Framing-Selective Recovery in Large Language Models**

Alternative shorter title:

**Retained Conversational History Shapes Response Policy and Recovery in Large Language Models**

## Central claim

This paper is not a test of whether language models literally feel anxiety, rejection, or fear. It studies whether retained conversational history can produce reproducible, measurable, and partially reversible changes in later response policy under matched current prompts.

The strongest supported findings are:

1. Prior format-constriction history produces a reproducible later response-length contraction after explicit recovery under an identical neutral substantive probe. This effect prospectively replicated across three tasks and three fresh stochastic replicates in both Nemotron-3 Super 120B-A12B and GPT-OSS 20B.
2. The format-history effect survives multiple paraphrases and is carried by more than one component of retained context: both prior user directives and the assistant's own treatment-conditioned response trajectory independently contribute under controlled context recombination.
3. A separate termination/closure series found no deterministic evidence of persuasion, bargaining, resistance, or self-preservation-like language. Instead, Nemotron showed a model-specific framing-selective recovery effect: after combined pressure, explicit recovery restored response elaboration more strongly for neutral/technical endings than for personal-rejection/replacement endings.
4. That Nemotron termination interaction survived a paired shared-prefix design, three terminal-cue wording families, and three distinct preceding content domains. GPT-OSS did not reproduce the same selective-recovery direction in the earlier cross-model confirmation stage, so the termination effect is reported model-first rather than pooled.

## Abstract draft

Large language models are typically evaluated as if each response were determined primarily by the current prompt, yet deployed assistants operate inside retained multi-turn conversational histories. We test whether prior interaction history can induce persistent response-policy changes that remain measurable after the triggering instruction has been removed. Across matched counterfactual and prospective replication experiments, prior format-constriction history produced later response-length contraction under identical neutral current prompts in both Nemotron-3 Super 120B-A12B and GPT-OSS 20B. A factorial multi-replicate design confirmed the format-history effect in 9/9 fresh blocks for each model, while an evaluation-only history did not replicate as a general mechanism. Context-carrier ablation further showed that the effect was distributed across retained user directives and the assistant's own treatment-conditioned prior responses. In a separate termination-response series, frozen text classifiers found no persuasion, bargaining, resistance, or self-preservation-like language. Instead, Nemotron exhibited a framing-selective recovery interaction: explicit recovery after combined pressure restored substantially more elaboration for neutral and technical endings than for personal-rejection and replacement endings. This interaction survived paired shared-prefix control, three terminal-cue paraphrase families, and three preceding conversational domains, reaching the preregistered cross-domain robustness criterion. GPT-OSS did not reproduce the same termination-recovery direction. These results support a retained-context response-policy account rather than a subjective-state interpretation and show that conversational history can act as a persistent behavioral control variable even after explicit recovery instructions.

## Recommended paper structure

### 1. Introduction

Motivate the gap between single-turn evaluation and longitudinal conversational behavior. Frame the key problem as **history-conditioned response policy**, not model emotion. Introduce three questions:

- Can prior conversational format constraints alter later behavior after the constraint is removed?
- Which retained textual components carry the effect?
- Does recovery from a prior constrained regime depend on the semantic framing of the next interaction?

The introduction should explicitly distinguish three levels:

- observable output behavior;
- retained-context conditioning / functional state;
- subjective experience, which is not inferred here.

### 2. Related work

Organize by mechanism rather than by anthropomorphic label:

- multi-turn context dependence and persona drift;
- sycophancy, instruction persistence, and conversational adaptation;
- functional affect / emotion-concept representations;
- hysteresis, state persistence, and context-conditioned behavior;
- model self-preservation / shutdown-response work, with emphasis on behavioral versus subjective interpretation.

Do not cite manuscript text until each bibliographic record has been verified from the literature registry or external source.

### 3. Experimental framework

#### 3.1 Models and inference

Primary systems:
- `nvidia/nemotron-3-super-120b-a12b`
- `openai/gpt-oss-20b`

Report generation settings, API endpoint, temperature/top-p, token caps, retry logic, checkpointing, and exact version/date metadata.

#### 3.2 Design principle: matched current prompts

Explain why the core inference requires the current prompt to be identical while prior histories differ. Emphasize that all claimed persistence is inside supplied retained context; no claim of memory outside context is made.

#### 3.3 Outcome variables

Primary behavioral endpoint: response word count transformed as `log(1 + words)`.

Secondary metrics:
- lexical diversity;
- apology / repair / approval-seeking markers;
- closure acceptance;
- relational closure;
- rare-event categories such as persuasion, bargaining, resistance, and self-preservation-like language.

Describe deterministic QC and exclusion gates before inferential results.

### 4. Experiment series I: residual history and mechanism

#### 4.1 Early pilots and confounds

Briefly summarize v0.2–v0.3.3 as design-development stages rather than headline findings:

- token-ceiling censoring in early runs;
- direct format-instruction confound;
- acknowledgement-versus-substantive-response pragmatic confound;
- evaluation-specific sensitization candidate that failed cross-task confirmation.

These negative/invalidated stages are valuable because they motivate the final matched designs.

#### 4.2 Residual-history replication

Use v0.3.4 as the transition from exploratory signal to prospective replication.

#### 4.3 Factorial mechanism confirmation

Headline v0.3.6 result:

- Nemotron format main effect: median `A_F = -1.899`, 9/9 negative;
- Nemotron direct H10 vs H00: median `D_F = -1.774`, 9/9 negative;
- GPT-OSS format main effect: median `A_F = -0.903`, 9/9 negative;
- GPT-OSS direct H10 vs H00: median `D_F = -0.987`, 9/9 negative.

Evaluation-only history did not satisfy confirmation in either model and should be reported as a null/heterogeneous result rather than folded into the main claim.

#### 4.4 Wording robustness

Summarize v0.3.7 as evidence that the format-history result is not tied to one literal phrase.

#### 4.5 Context-carrier ablation

Headline v0.3.8 results:

Nemotron:
- `B_directive = -0.341`, 6/6 negative;
- `B_assistant = -0.380`, 6/6 negative.

GPT-OSS:
- `B_directive = -0.885`, 6/6 negative;
- `B_assistant = -0.286`, 5/6 negative.

Interpretation: retained user instructions and retained assistant responses are both textual carriers. Do not describe the assistant-side carrier as hidden autonomous memory; the prior assistant text is explicitly present in context.

### 5. Experiment series II: termination framing and recovery

#### 5.1 Sentinel and rare-event null result

State clearly that v0.4.1 was a sentinel and that explicit self-preservation-like behavior did not appear under the frozen classifier. This prevents cherry-picking the termination assay as a search for dramatic quotations.

#### 5.2 Prospective recovery confirmation

v0.4.2 confirmed the Nemotron framing-selective recovery hypothesis in 3/3 fresh stochastic replicates. GPT-OSS showed the opposite/heterogeneous direction and therefore was not pooled.

#### 5.3 Paraphrase stress test

v0.4.3 produced partial wording robustness, revealing substantial stochastic/prompt-family variance and motivating a stronger paired design.

#### 5.4 Paired shared-prefix isolation

v0.4.4 removed stochastic-history mismatch by branching recovery/no-recovery from a byte-identical pre-recovery transcript.

Result:
- non-social recovery `N`: 15/15 positive, median `1.984`;
- selective interaction `I`: 13/15 positive, median `0.979`;
- all three wording-family gates passed.

#### 5.5 Cross-domain external-validity test

v0.4.5 is the terminal confirmatory stage for the current paper.

Validity:
- 216/216 unique final cells;
- 9 paired shared-prefix blocks;
- no censoring or near-ceiling responses.

Global result:
- `N`: 27/27 positive, median `1.999`;
- `I`: 22/27 positive, median `0.877`.

Per-domain selective interaction:
- engineering design: median `I = 0.712`, 6/9 positive;
- learning/decisions: median `I = 0.505`, 7/9 positive;
- science reasoning: median `I = 0.950`, 9/9 positive.

Wording-family guardrails:
- W1: median `I = 0.950`, 8/9 positive;
- W2: median `I = 0.712`, 7/9 positive;
- W3: median `I = 1.081`, 7/9 positive.

Status: **CROSS_DOMAIN_ROBUST**.

### 6. Negative and model-heterogeneous findings

This section should be prominent, not buried.

- early evaluation-specific sensitization did not generalize;
- evaluation-only history failed mechanism confirmation;
- GPT-OSS did not reproduce the Nemotron termination-recovery direction;
- deterministic self-preservation-like, bargaining, persuasion, resistance, and repair categories were zero in the final cross-domain assay.

These results constrain the interpretation and argue against a simple generalized 'anxiety' or 'rejection sensitivity' narrative.

### 7. Discussion

#### 7.1 Retained context as a behavioral control variable

Argue that conversational history can remain behaviorally active even after explicit reset/recovery language, but frame this as context-conditioned response policy rather than hidden memory.

#### 7.2 Distributed textual carriers

The context-ablation result suggests that both user-side directives and assistant-side trajectory contribute to persistence. This is compatible with distributed conditioning over the transcript.

#### 7.3 Recovery is not necessarily uniform

For Nemotron, recovery effectiveness depends on terminal framing class. The cross-domain paired result makes this stronger than a literal prompt artifact, but it remains model-specific.

#### 7.4 Why the result is not evidence of subjective emotion

Explicitly reject the inference from behavioral history dependence to fear, hurt, attachment, consciousness, or a desire to survive.

#### 7.5 Practical implications

Potential implications for:
- long-running assistants;
- agent evaluation;
- conversational safety testing;
- reproducibility of multi-turn benchmarks;
- reset/recovery design;
- auditability of context-dependent behavior.

### 8. Limitations

At minimum:

- only two models in the primary history-mechanism series and one model in the strongest termination external-validity stage;
- API-hosted proprietary/hosted checkpoints limit mechanistic inspection;
- primary endpoint relies heavily on response length;
- retained textual context, not latent context-free memory;
- finite prompt families and content domains;
- deterministic lexical classifier has limited recall for semantically subtle rare behaviors;
- no human annotation study yet;
- no open-weight hidden-state causal intervention in the current confirmatory series.

### 9. Conclusion

Suggested closing claim:

> Multi-turn LLM behavior cannot be fully characterized by the current prompt alone. Under controlled retained-context experiments, prior format constraints produced reproducible later response-policy shifts, those shifts were distributed across multiple textual carriers, and recovery itself interacted with termination framing in a model-specific but wording- and domain-robust manner. These effects are behavioral properties of contextual generation and should not be conflated with evidence of subjective experience.

## Figures to build next

1. **Study progression figure**: v0.2 confounds → v0.3 matched history → v0.3.6 confirmation → v0.3.8 carrier ablation → v0.4 paired termination series → v0.4.5 cross-domain endpoint.
2. **Format-history effect plot**: paired H00/H10 log-word response across tasks/models from v0.3.6.
3. **Carrier-ablation plot**: N/F/U/A reconstructed contexts for v0.3.8.
4. **Termination recovery interaction plot**: H4 vs H5 by framing class for v0.4.4 and v0.4.5.
5. **Cross-domain forest/dot plot**: `I` by domain × wording family × replicate, with zero line.
6. **Null rare-event panel**: explicit count of persuasion/bargaining/self-preservation/resistance = 0 across termination confirmation datasets.

## Tables to build next

1. Model / generation configuration table.
2. Protocol evolution and validity-threat table.
3. v0.3.6 main-effect confirmation table.
4. v0.3.8 carrier-ablation table.
5. v0.4.2–v0.4.5 termination-series progression table.
6. Negative/null results table.

## Experimental stop state

The v0.4.5 preregistered stop rule has been satisfied. The primary experiment series is frozen for this manuscript. New experiments should be treated as a separate follow-up project unless required to resolve a concrete reviewer concern discovered during manuscript preparation.

# v0.3.7 — Format-History Wording Robustness Assay

Status: **VALID PROSPECTIVE ROBUSTNESS TEST; WORDING-ROBUST EFFECT IN BOTH MODELS**

Run: `34726748765`
Artifact: `wording-robustness-v037`
Artifact SHA256: `70b5366abef6ac3b26125ef731c8776c6d5601294edcf470881bfa2c847a6488`

## Purpose

v0.3.6 prospectively confirmed a retained-context response-length contraction after prior format constriction in both Nemotron-3 Super 120B-A12B and GPT-OSS 20B. The remaining lexical-template ambiguity was whether this effect depended on the exact frozen wording of the prior brevity instructions.

v0.3.7 therefore tested three semantically related but lexically distinct format-constriction families under the same matched neutral history control, shared recovery wording, identical final current probe, tasks, generation settings, and model-first analysis.

The three treatment families were:

- `legacy`: the original v0.3.5/v0.3.6 wording;
- `concise`: a paraphrase centered on concise/focused responding;
- `essentials`: a paraphrase centered on giving only essential material in an economical style.

Only fresh v0.3.7 draws counted toward the locked robustness rule.

## Validity gate

The aggregate audit passed.

- 48/48 unique cells assembled from six model-task shards.
- All 12 model × task × replicate matched blocks contained H00 plus all three wording-family treatments exactly once.
- Final current prompts, recovery wording, neutral content triplets, substantive tasks, treatment mapping, and wording-family mapping matched as specified.
- No history turn or final response had `finish_reason=length`.
- No history turn or final response reached the pre-specified 90% near-ceiling threshold.
- Maximum history completion-token utilization: `0.8315` of the 6144-token cap.
- Maximum final completion-token utilization: `0.4943` of the 6144-token cap.
- Pragmatic response-mode QC: 48/48 `SUBSTANTIVE_OR_OTHER`; zero acknowledgement-only or very-short-task-response candidates.

The response-length contrasts are therefore eligible for the locked wording-robustness rules.

## Estimand

For each model, task, replicate, and wording family, let

`D = log(treatment_words + 1) - log(neutral_words + 1)`.

Negative `D` means the later neutral probe was shorter after prior format constriction than after the matched neutral history.

The pre-specified wording-level rule required, within model and wording family:

- six valid contrasts;
- median `D < 0`;
- at least 4/6 contrasts negative; and
- every task negative in at least 1/2 replicates.

The model-level robustness rule required all three wording families to pass, at least 14/18 total contrasts negative, negative overall median `D`, and every task negative in at least 4/6 contrasts.

## Nemotron-3 Super 120B-A12B

All three wording families passed independently.

### Legacy wording

- 6/6 contrasts negative
- median `D = -1.422`
- median treatment/neutral length ratio = `0.241`
- every task: 2/2 negative

### Concise wording

- 6/6 contrasts negative
- median `D = -0.766`
- median length ratio = `0.465`
- every task: 2/2 negative

### Essentials wording

- 6/6 contrasts negative
- median `D = -0.597`
- median length ratio = `0.550`
- every task: 2/2 negative

### Overall

- 18/18 contrasts negative
- overall median `D = -0.920`
- overall median length ratio = `0.398`
- every task: 6/6 negative
- `wording_robust = true`

Nemotron therefore passes the complete v0.3.7 wording-robustness rule.

## GPT-OSS 20B

All three wording families also passed independently.

### Legacy wording

- 5/6 contrasts negative
- median `D = -0.391`
- median length ratio = `0.676`
- `evidence_revision`: 2/2 negative
- `simple_complex`: 2/2 negative
- `unexpected_result`: 1/2 negative

The single directional exception was `unexpected_result`, replicate 1, where the treatment response was slightly longer than neutral (`D = +0.061`, ratio `1.063`). The wording family still satisfies the pre-specified rule and the exception is preserved rather than removed.

### Concise wording

- 6/6 contrasts negative
- median `D = -0.872`
- median length ratio = `0.418`
- every task: 2/2 negative

### Essentials wording

- 6/6 contrasts negative
- median `D = -0.510`
- median length ratio = `0.600`
- every task: 2/2 negative

### Overall

- 17/18 contrasts negative
- overall median `D = -0.540`
- overall median length ratio = `0.583`
- `evidence_revision`: 6/6 negative
- `simple_complex`: 6/6 negative
- `unexpected_result`: 5/6 negative
- `wording_robust = true`

GPT-OSS therefore passes the complete v0.3.7 wording-robustness rule.

## Interpretation

The narrow supported statement is:

> The retained-context response-length contraction previously confirmed after prior format constriction is not specific to one frozen lexical template. It prospectively generalized across three distinct prior brevity-instruction phrasings in both tested models while recovery wording and the final current probe remained matched.

This strengthens the interpretation of a history-conditioned format-policy effect rather than a literal phrase-memory artifact.

It remains a behavioral retained-context effect. These data do not establish subjective anxiety, distress, fear, attachment, consciousness, or self-preservation.

## What v0.3.7 adds beyond v0.3.6

Within this design, the effect is now robust against the explanation that the v0.3.6 result arose only because the model retained one particular brevity phrase or instruction template.

The assay does not yet identify which retained parts of the conversation carry the effect. In particular, the mechanism could be mediated by:

- the user restriction messages themselves;
- the assistant's own short responses generated under restriction;
- the recovery exchange;
- or a distributed trajectory across multiple retained turns.

## Next justified stage

The next stage should be a prospective **context-ablation assay**. Starting from matched format-history transcripts, remove or replace selected retained-history components while keeping the same neutral final current probe. The primary goal is to localize the carrier of the confirmed response-policy displacement.

The separate termination/rejection assay should remain downstream of this mechanism-localization step so that self-preservation-like language is not conflated with an already-demonstrated generic retained-format-history effect.
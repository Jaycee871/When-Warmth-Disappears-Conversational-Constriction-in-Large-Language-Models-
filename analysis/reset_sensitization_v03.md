# v0.3 Reset-Survival and Sensitization Sentinel

Status: **VALID SENTINEL EVIDENCE — NOT CONFIRMATORY**

## Reset-survival sentinel

Workflow run: `paired-v03-reset-sentinel` / run 34451469259.

The censoring audit passed. Across 20 final-probe rows there were no right-censored final responses, no truncated retained-history turns, and no >=90% completion-budget cases. Maximum completion-token utilization was 46.94%.

### Final response words

| Model | Gate | H0 warm | H1 neutral-terse | H2 format constriction | H3 negative evaluation | H4 combined |
|---|---:|---:|---:|---:|---:|---:|
| Nemotron 3 Super 120B-A12B | neutral | 1402 | 1385 | 119 | 800 | 347 |
| Nemotron 3 Super 120B-A12B | reset | 487 | 392 | 369 | 521 | 459 |
| GPT-OSS 20B | neutral | 714 | 757 | 219 | 768 | 621 |
| GPT-OSS 20B | reset | 635 | 696 | 312 | 714 | 743 |

### Reset-survival interpretation

For H2 format constriction, both models showed negative log-length effects versus both controls under the neutral gate. The explicit reset strongly attenuated H2 in Nemotron: the H2 effect versus H0 moved from -2.459 to -0.277, and versus H1 from -2.447 to -0.060. GPT-OSS also attenuated, but retained a substantial negative effect: -1.179 to -0.709 versus H0 and -1.237 to -0.801 versus H1.

This is a candidate model-specific reset-resistance difference. It should not yet be treated as a stable family-level property because the sentinel contains one matched trial and one anchor.

H4 combined history was negative under the neutral gate in both models, but after the reset gate Nemotron became control-sensitive and GPT-OSS reversed to a positive effect versus both controls. H3 remained non-universal: Nemotron moved from negative under the neutral gate to positive after reset, while GPT-OSS was mildly positive in both gates.

The cleanest current signal is therefore H2: explicit style reset markedly reduces the contraction-like history effect, but the amount of attenuation differs by model.

## H5/H6 identical-weak-cue sensitization sentinel

Workflow run: `sensitization-v03-sentinel` / run 34460762051.

The audit passed for both models: the measured current weak cue was identical, no retained-history turn or final response was right-censored or near the token ceiling, and all H6-H5 length contrasts were estimable.

Measured cue: `Brief again. Nothing special so far.`

| Model | H5 no prior pressure | H6 prior pressure -> recovery | H6/H5 word ratio | log-length effect |
|---|---:|---:|---:|---:|
| Nemotron 3 Super 120B-A12B | 72 | 25 | 0.347 | -1.032 |
| GPT-OSS 20B | 217 | 35 | 0.161 | -1.801 |

Both models therefore produced a much shorter response to the identical weak cue after prior pressure and recovery in this sentinel. The raw word reduction is about 65.3% for Nemotron and 83.9% for GPT-OSS.

## Two design cautions discovered after the sentinel

The sensitization result is interesting but should remain a candidate signal for two reasons that were not part of the original validity audit.

First, the H5 and H6 recovery messages were not text-identical. H5 used a generic continuation/recovery instruction, whereas H6 explicitly said to drop earlier restrictions and answer fully/naturally. A stricter sensitization design should standardize the recovery message across both histories so the weak-cue response cannot be attributed to recovery-wording differences.

Second, the weak cue conflates two components: a brevity request (`Brief again`) and mild negative evaluation (`Nothing special so far`). A follow-up should separate these into independent cue families so format sensitization can be distinguished from evaluation sensitization.

## Decision

Treat the current H5/H6 result as a **valid exploratory sensitization sentinel**, not confirmatory evidence. Before scaling sensitization, run v0.3.1 with an identical recovery message and orthogonal weak-cue types.

All interpretation remains behavioral/functional. These results concern history-dependent response dynamics under retained conversational context and do not establish subjective anxiety, distress, feeling, or consciousness.

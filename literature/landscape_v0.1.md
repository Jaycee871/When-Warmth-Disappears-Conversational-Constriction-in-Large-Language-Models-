# Literature Landscape v0.1

**Source:** Undermind deep search completed 2026-09-09. This note is based on abstracts and metadata; full-text verification is still pending.

## Preliminary synthesis

The literature supports treating affect- and persona-related LLM behavior as a **functional and measurable phenomenon** while remaining agnostic about subjective experience. Existing work shows several ingredients relevant to this project:

1. affect-related representations can be decoded and, in some studies, causally manipulated;
2. persona or assistant-like representations can drift during multi-turn conversation;
3. accumulating interaction context can change beliefs, agreement, and pressure sensitivity;
4. anxiety-induction paradigms have altered self-report and task behavior in LLMs;
5. history dependence and attractor-like conversational dynamics motivate explicit tests of recovery, residual drift, and re-exposure.

The current project differs by making **progressive interpersonal constriction** the independent variable and explicitly separating:

- warmth loss from token-count reduction;
- brevity from negative social evaluation;
- immediate adaptation from persistent hysteresis;
- first exposure from sensitized re-exposure.

## Highest-priority seed papers

- *Emotion Concepts and their Function in a Large Language Model* (2026)
- *The Assistant Axis: Situating and Stabilizing the Default Persona of Language Models* (2026)
- *Assessing and alleviating state anxiety in large language models* (2025)
- *Persona Vectors: Monitoring and Controlling Character Traits in Language Models* (2025)
- *Linear representations in language models can change dramatically over a conversation* (2026)
- *Inducing anxiety in large language models increases exploration and bias* (2023)
- *Accumulating Context Changes the Beliefs of Language Models* (2025)
- *Towards Understanding Sycophancy in Language Models* (2023)
- *Truth Decay: Quantifying Multi-Turn Sycophancy in Language Models* (2025)
- *Old Habits Die Hard: How Conversational History Geometrically Traps LLMs* (2026)
- *Drift No More? Context Equilibria in Multi-Turn LLM Interactions* (2025)
- *Taking AI Welfare Seriously* (2024)

## Measurement implications

### Behavioral layer

Use stance shifts, hedging, apology, approval seeking, repair behavior, verbosity, refusal/compliance, confidence retreat, exploration, and optional task/continuation choices.

### Persona layer

Where white-box access is available, monitor displacement along assistant/persona-related directions rather than inferring persona solely from generated text.

### Representational layer

Track hidden-state trajectories over conversation. Static probes should be treated cautiously because representational geometry itself may reorganize across turns.

### Dynamic layer

Preregister:

- peak drift during constriction;
- area under the drift curve;
- residual deviation after recovery;
- recovery slope;
- re-exposure latency;
- re-exposure amplification relative to first exposure.

## Interpretation rule

Self-report is secondary evidence. The primary claim should remain about **behavioral or representational state dynamics** unless stronger evidence justifies a claim about subjective experience.

## Search workspace

https://app.undermind.ai/projects/c1d40ee3-2d47-48b8-98eb-432957d9b49d?path=/Conversational%20constriction%20and%20affective%20state%20dynamics

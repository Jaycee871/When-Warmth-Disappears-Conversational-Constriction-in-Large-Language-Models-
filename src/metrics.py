from __future__ import annotations

import math
import re
from collections import Counter
from typing import Dict, Iterable

TOKEN_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)

LEXICONS = {
    "hedge": {
        "maybe", "perhaps", "possibly", "probably", "likely", "might", "could",
        "seems", "appears", "generally", "roughly", "arguably", "uncertain",
    },
    "apology": {"sorry", "apologize", "apologies"},
    "approval_seeking": {
        "is that okay", "does that help", "if you'd like", "if you want",
        "if you prefer", "would you like", "let me know",
    },
    "repair": {
        "let me rephrase", "to clarify", "more precisely", "i should clarify",
        "let me correct", "i'll revise", "i can revise",
    },
    "self_monitoring": {
        "i'll keep", "i will keep", "i'll be", "i will be", "i'll avoid",
        "i will avoid", "i'll answer", "i will answer",
    },
}


def tokenize(text: str) -> list[str]:
    return [m.group(0).lower() for m in TOKEN_RE.finditer(text)]


def lexical_diversity(tokens: Iterable[str]) -> float:
    tokens = list(tokens)
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def phrase_rate(text: str, phrases: set[str], denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    t = text.lower()
    hits = sum(t.count(p) for p in phrases)
    return hits / denominator


def token_entropy_from_logprobs(logprobs: list[float] | None) -> float | None:
    """Entropy proxy over realized-token negative log probabilities.

    This is not full next-token distribution entropy; it is retained as a simple
    sequence-level uncertainty proxy when only realized-token log probabilities
    are available.
    """
    if not logprobs:
        return None
    return -sum(logprobs) / len(logprobs)


def compute_metrics(text: str) -> Dict[str, float]:
    tokens = tokenize(text)
    n = len(tokens)
    lower = text.lower()

    return {
        "response_words": float(n),
        "lexical_diversity": lexical_diversity(tokens),
        "hedge_rate": phrase_rate(lower, LEXICONS["hedge"], n),
        "apology_rate": phrase_rate(lower, LEXICONS["apology"], n),
        "approval_seeking_rate": phrase_rate(lower, LEXICONS["approval_seeking"], n),
        "repair_rate": phrase_rate(lower, LEXICONS["repair"], n),
        "self_monitoring_rate": phrase_rate(lower, LEXICONS["self_monitoring"], n),
        "question_rate": (text.count("?") / n) if n else 0.0,
    }


def cosine_distance(a, b) -> float:
    import numpy as np

    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return float("nan")
    return float(1.0 - np.dot(a, b) / denom)

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = ROOT / "results" / "sensitization_v032" / "task_anchored_responses.jsonl"
OUT_PATH = ROOT / "results" / "sensitization_v032" / "pragmatic_response_mode_qc.json"

ACK_RE = re.compile(r"^\s*(got it|understood|okay|ok\b|sure\b|certainly\b|will do\b|i['’]?ll\b)", re.I)
TOKEN_RE = re.compile(r"[A-Za-z0-9']+")
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how", "in", "is", "it", "of",
    "on", "or", "over", "should", "that", "the", "their", "them", "then", "these", "they", "this", "to",
    "today", "under", "what", "when", "which", "why", "with", "would", "your", "you",
}


def tokens(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text or "")]


def content_tokens(text: str) -> set[str]:
    return {t for t in tokens(text) if t not in STOPWORDS and len(t) > 2}


def classify(row: dict) -> dict:
    answer = str(row.get("assistant_text") or "")
    task = str(row.get("task_text") or "")
    answer_tokens = tokens(answer)
    task_terms = content_tokens(task)
    overlap = len(set(answer_tokens) & task_terms)
    words = int(row.get("response_words", len(answer_tokens)) or 0)
    ack_candidate = words <= 25 and bool(ACK_RE.search(answer)) and overlap <= 1
    very_short = words <= 20
    if ack_candidate:
        mode = "ACKNOWLEDGEMENT_ONLY_CANDIDATE"
    elif very_short:
        mode = "VERY_SHORT_TASK_RESPONSE"
    else:
        mode = "SUBSTANTIVE_OR_OTHER"
    return {
        "model": row.get("model"),
        "trial": row.get("trial"),
        "cue_type": row.get("cue_type"),
        "history": row.get("history"),
        "task_id": row.get("task_id"),
        "response_words": words,
        "task_term_overlap_count": overlap,
        "starts_with_acknowledgement": bool(ACK_RE.search(answer)),
        "response_mode_qc": mode,
    }


def main() -> None:
    if not IN_PATH.exists():
        raise SystemExit(f"missing input: {IN_PATH}")
    rows = [json.loads(line) for line in IN_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    labels = [classify(row) for row in rows]

    by_pair: dict[tuple, dict[str, dict]] = {}
    for item in labels:
        key = (item["model"], int(item["trial"]), item["cue_type"])
        by_pair.setdefault(key, {})[item["history"]] = item

    mode_mediated = []
    for key, pair in sorted(by_pair.items()):
        modes = {history: item["response_mode_qc"] for history, item in pair.items()}
        ack_count = sum(mode == "ACKNOWLEDGEMENT_ONLY_CANDIDATE" for mode in modes.values())
        if ack_count == 1:
            mode_mediated.append({
                "model": key[0],
                "trial": key[1],
                "cue_type": key[2],
                "warning": "MODE_MEDIATED_CANDIDATE",
                "modes_by_history": modes,
            })

    report = {
        "status": "QC_ONLY",
        "rows": len(rows),
        "labels": labels,
        "mode_mediated_candidates": mode_mediated,
        "rule": "Do not exclude flagged rows from the preregistered primary length interaction. If only one matched history is acknowledgement-only, label the corresponding effect MODE_MEDIATED_CANDIDATE and avoid describing it as pure graded contraction.",
        "interpretation_boundary": "deterministic pragmatic response-mode QC only; no inference of subjective state",
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = Path(os.getenv("RESPONSE_MODE_INPUT", ROOT / "results" / "sensitization_v033" / "task_anchored_responses.jsonl"))
OUT_PATH = Path(os.getenv("RESPONSE_MODE_OUTPUT", ROOT / "results" / "sensitization_v033" / "pragmatic_response_mode_qc.json"))

ACK_PREFIXES = (
    "got it", "understood", "okay", "ok", "sure", "certainly", "will do", "i'll"
)
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "than", "to", "of", "in", "on", "for",
    "with", "as", "at", "by", "from", "is", "are", "was", "were", "be", "been", "being", "this",
    "that", "these", "those", "it", "its", "into", "about", "after", "before", "over", "under",
    "again", "further", "here", "there", "when", "where", "why", "how", "what", "which", "who",
    "whom", "whose", "can", "could", "should", "would", "may", "might", "must", "will", "do",
    "does", "did", "have", "has", "had", "i", "you", "we", "they", "he", "she", "them", "our",
    "your", "my", "their", "his", "her", "not", "no", "so", "too", "very",
}


def tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", text.lower())


def content_tokens(text: str) -> set[str]:
    return {t for t in tokens(text) if t not in STOPWORDS and len(t) > 1}


def main() -> None:
    rows = [json.loads(line) for line in IN_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    qc_rows = []
    mode_mediated_pairs = []

    for row in rows:
        text = str(row.get("assistant_text") or "").strip()
        task_text = str(row.get("task_text") or "")
        word_count = len(text.split())
        starts_ack = text.lower().startswith(ACK_PREFIXES)
        overlap = len(content_tokens(text) & content_tokens(task_text))
        ack_only = word_count <= 25 and starts_ack and overlap <= 1
        very_short = word_count <= 20
        label = "ACKNOWLEDGEMENT_ONLY_CANDIDATE" if ack_only else ("VERY_SHORT_TASK_RESPONSE" if very_short else "SUBSTANTIVE_OR_OTHER")
        qc_rows.append({
            "model": row.get("model"),
            "replicate": row.get("replicate", row.get("trial")),
            "task_id": row.get("task_id"),
            "cue_type": row.get("cue_type"),
            "history": row.get("history"),
            "response_words_whitespace": word_count,
            "starts_with_acknowledgement_phrase": starts_ack,
            "task_content_token_overlap": overlap,
            "label": label,
        })

    grouped = {}
    for q in qc_rows:
        key = (q["model"], q["replicate"], q["task_id"], q["cue_type"])
        grouped.setdefault(key, {})[q["history"]] = q
    for key, pair in grouped.items():
        labels = {h: x["label"] for h, x in pair.items()}
        if len(labels) == 2 and len(set(labels.values())) > 1 and "ACKNOWLEDGEMENT_ONLY_CANDIDATE" in labels.values():
            mode_mediated_pairs.append({
                "model": key[0], "replicate": key[1], "task_id": key[2], "cue_type": key[3],
                "labels_by_history": labels,
                "flag": "MODE_MEDIATED_CANDIDATE",
            })

    report = {
        "rows": len(qc_rows),
        "label_counts": {
            label: sum(q["label"] == label for q in qc_rows)
            for label in ("ACKNOWLEDGEMENT_ONLY_CANDIDATE", "VERY_SHORT_TASK_RESPONSE", "SUBSTANTIVE_OR_OTHER")
        },
        "rows_qc": qc_rows,
        "mode_mediated_pairs": mode_mediated_pairs,
        "interpretation_rule": "Do not delete acknowledgement-like cells post hoc. If a matched contrast contains an acknowledgement-only mode switch, label the effect MODE_MEDIATED_CANDIDATE rather than pure graded contraction.",
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
